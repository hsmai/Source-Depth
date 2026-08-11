"""체크포인트 가능한 평가 루프 (03 §B-11: (question_id, condition, template) 단위 resume).

문항-major 루프: 문항 1개의 M layout 입력을 9개 조건(M/T×6/T0/Trel8)이 공유.
"""
import time

import torch

from ..config import COCO_IMG_DIR, PROMPT_MULTI, PROMPT_SINGLE
from ..data.download import image_path
from ..model.inputs import build_inputs, find_vision_spans
from ..model.masking import condition_to_block
from ..runlog import append_jsonl, blocked, iso_now, read_jsonl
from .yesno import predict


def obj_phrase(article: str, obj: str) -> str:
    return f"{article} {obj}"    # A-6: POPE 원문 관사 보존


def questions_for(row) -> tuple[str, str]:
    phrase = obj_phrase(row["article"], row["object"])
    return PROMPT_MULTI.format(obj=phrase), PROMPT_SINGLE.format(obj=phrase)


def done_keys(out_path) -> set:
    return {(r["question_id"], r["condition"], r.get("template", "primary"))
            for r in read_jsonl(out_path) if "condition" in r}


@torch.no_grad()
def run_eval(pairs_rows, conds, model, processor, ctrl, vs_ve_pad, out_path,
             template: str, yes_ids, no_ids, device="cuda:0") -> int:
    """pairs_rows: dict-like 목록. 반환: 이번 호출에서 실제 실행한 forward 수."""
    vs_id, ve_id, pad_id = vs_ve_pad
    done = done_keys(out_path)
    executed = 0
    for row in pairs_rows:
        qid = row["question_id"]
        todo = [c for c in conds if (qid, c, template) not in done]
        if not todo:
            continue
        q_multi, q_single = questions_for(row)
        img1 = image_path(int(row["image1_id"]), COCO_IMG_DIR)
        img2 = image_path(int(row["image2_id"]), COCO_IMG_DIR)
        in_s = in_m = sp = None
        if "S" in todo:
            in_s = build_inputs(processor, [img1], q_single, device, template)
        if any(c != "S" for c in todo):
            in_m = build_inputs(processor, [img1, img2], q_multi, device, template)
            sp = find_vision_spans(in_m["input_ids"], vs_id, ve_id, pad_id)
            if len(sp) != 2:
                blocked("loop", f"M layout span 수 != 2: {sp}", {"question_id": qid})
        n_layers = len(ctrl.layers)
        for cond in todo:
            t0 = time.time()
            if cond == "S":
                ctrl.disable()
                inputs = in_s
                expected_fires = 0
            else:
                bf, cols = condition_to_block(cond, sp[0], sp[1])
                if bf is None:
                    ctrl.disable()
                    expected_fires = 0
                else:
                    ctrl.configure(bf, cols)
                    expected_fires = max(0, n_layers - bf)
                inputs = in_m
            fired_before = sum(ctrl.fired.values())
            try:
                out = model(**inputs, use_cache=False)
            finally:
                ctrl.disable()   # 예외 시에도 hook armed 잔류 금지 (리뷰 지적)
            fired_delta = sum(ctrl.fired.values()) - fired_before
            if fired_delta != expected_fires:
                blocked("loop", "hook 발화 카운터 불일치 — 마스킹 무음 no-op 의심",
                        {"question_id": qid, "condition": cond,
                         "fired": fired_delta, "expected": expected_fires})
            p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
            rec = {"question_id": qid, "cell": int(row["cell"]), "gt": row["gt"],
                   "condition": cond, "template": template, **p,
                   "correct": p["pred"] == row["gt"],
                   "image1_id": int(row["image1_id"]), "image2_id": int(row["image2_id"]),
                   "seq_len": int(inputs["input_ids"].shape[1]),
                   "img1_span": list(sp[0]) if cond != "S" else None,
                   "img2_span": list(sp[1]) if cond != "S" else None,
                   "elapsed_ms": int(1000 * (time.time() - t0)), "ts": iso_now()}
            append_jsonl(out_path, rec)
            done.add((qid, cond, template))
            executed += 1
    return executed
