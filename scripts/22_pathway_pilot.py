#!/usr/bin/env python
"""경로 분해 + 고립(isolation) 파일럿 — 신규 설계의 검증 항목 1·2를 인과 개입으로 가른다.

docs/18_pathway_prereg.md 참조. 세 파트:

PART 1 — 경로 분해 (2-image, pairs.csv 셀1·셀2, "first image" 질문)
  causal 순서 [img1, img2, text]에서 정보가 흐르는 경로는 둘뿐:
    (a) img2 query → img1 key   (이미지 간 혼합; 역방향은 causal상 불가)
    (b) text query → img 키     (질문 토큰의 읽기)
  조건:  M / XIMG(경로 a만 차단) / READ(text→img2만 차단) / T0(img2 키 전면 차단)
  예측(사전 기록): READ ≈ T0 (완전 회복), XIMG ≈ M (효과 없음)
    → 성립하면 "환각 = 표현의 섞임"이 아니라 "읽기 단계의 출처 오귀속(misattribution)"

PART 2 — 고립 (3-image, md_pairs, "any of these images" 질문 — 모든 이미지가 필요한 유형)
  gt: leak(방해가 객체 보유)=yes / ctrl=no → 균형, AUC 가능
  조건:  M3 / ISO0(이미지끼리 서로 차단, text는 전부 봄) / ISO16(16층부터 고립)
  질문: 이미지 간 attention 없이 질문 토큰만으로 통합이 되는가?

PART 3 — 관계형 경계 (2-image, rel_pairs, "both images" 질문)
  조건:  M / ISO0
  질문: 비교 질문에서도 이미지 간 attention이 불필요한가? (여기서 무너지면 경계 확정)
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch

from sourcedepth.config import (COCO_IMG_DIR, PAIRS_CSV, RESULTS_DIR, SEED,
                                TAG, TEMPLATE_CHOICE)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase, questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import (append_jsonl, blocked, dump_env, iso_now,
                                read_jsonl, stage)

DEV = "cuda:0"
OUT = RESULTS_DIR / f"pathway{TAG}.jsonl"
MD_PAIRS = RESULTS_DIR / "md_pairs.json"
REL_PAIRS = RESULTS_DIR / "rel_pairs.json"
Q_ANY = "Is there {obj} in any of these images? Answer with Yes or No."
Q_BOTH = "Is there {obj} in both images? Answer with Yes or No."


def run_one(model, ctrl, inputs, yes_ids, no_ids):
    try:
        try:
            out = model(**inputs, use_cache=False)
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            out = model(**inputs, use_cache=False)
    finally:
        ctrl.disable()
    return predict(out.logits[0, -1].float(), yes_ids, no_ids)


def text_span(spans, seq_len):
    """마지막 이미지 span 이후 전부를 text query 구간으로 본다."""
    return (spans[-1][1] + 1, seq_len - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--parts", default="123")
    args = ap.parse_args()
    dump_env("22_pathway_pilot")
    if not torch.cuda.is_available():
        blocked("22_pathway", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]

    with stage("22_pathway_pilot"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0

        def emit(qid, part, cell, gt, cond, p, seq_len, t0):
            nonlocal executed
            append_jsonl(OUT, {"question_id": qid, "part": part, "cell": cell,
                               "gt": gt, "condition": cond, **p,
                               "correct": p["pred"] == gt, "n_layers": nlay,
                               "seq_len": seq_len,
                               "elapsed_ms": int(1000 * (time.time() - t0)),
                               "ts": iso_now()})
            executed += 1

        # ── PART 1: 경로 분해 ─────────────────────────────
        if "1" in args.parts:
            rows = [r for r in pd.read_csv(PAIRS_CSV).to_dict("records")
                    if int(r["cell"]) in (1, 2)]
            if args.limit:
                rows = rows[: args.limit]
            print(f"PART1: {len(rows)} 문항 × 4조건")
            for row in rows:
                qid = f"pw{row['question_id']}"
                todo = [c for c in ("M", "XIMG", "READ", "T0")
                        if (qid, c) not in done]
                if not todo:
                    continue
                q_multi, _ = questions_for(row)
                ims = [image_path(int(row["image1_id"]), COCO_IMG_DIR),
                       image_path(int(row["image2_id"]), COCO_IMG_DIR)]
                inputs = build_inputs(processor, ims, q_multi, DEV, template)
                sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
                if len(sp) != 2:
                    blocked("22_pathway", f"span != 2: {len(sp)}", {"qid": qid})
                seq = int(inputs["input_ids"].shape[1])
                ts = text_span(sp, seq)
                for cond in todo:
                    t0 = time.time()
                    if cond == "M":
                        ctrl.disable()
                    elif cond == "XIMG":            # img2가 img1을 보는 경로만
                        ctrl.configure_pathway([(0, sp[1], sp[0])])
                    elif cond == "READ":            # 질문 토큰이 img2를 읽는 경로만
                        ctrl.configure_pathway([(0, ts, sp[1])])
                    else:                           # T0: img2 키 전면 차단
                        ctrl.configure_pathway([(0, None, sp[1])])
                    p = run_one(model, ctrl, inputs, yes_ids, no_ids)
                    emit(qid, 1, int(row["cell"]), row["gt"], cond, p, seq, t0)
                del inputs
                torch.cuda.empty_cache()

        # ── PART 2: 고립 (3-image, need-all 질문) ─────────
        if "2" in args.parts:
            rows = json.loads(MD_PAIRS.read_text())
            if args.limit:
                rows = rows[: args.limit]
            print(f"PART2: {len(rows)} 문항 × 3조건")
            for row in rows:
                qid = f"any{row['question_id']}"
                todo = [c for c in ("M3", "ISO0", "ISO16") if (qid, c) not in done]
                if not todo:
                    continue
                gt = "yes" if row["group"] == "leak" else "no"
                q = Q_ANY.format(obj=obj_phrase(row["article"], row["object"]))
                ims = [image_path(row[f"image{i}_id"], COCO_IMG_DIR) for i in (1, 2, 3)]
                inputs = build_inputs(processor, ims, q, DEV, template)
                sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
                if len(sp) != 3:
                    blocked("22_pathway", f"span != 3: {len(sp)}", {"qid": qid})
                seq = int(inputs["input_ids"].shape[1])
                iso_rules = lambda bf: [(bf, sp[j], sp[i])
                                        for j in range(3) for i in range(3) if i < j]
                for cond in todo:
                    t0 = time.time()
                    if cond == "M3":
                        ctrl.disable()
                    elif cond == "ISO0":
                        ctrl.configure_pathway(iso_rules(0))
                    else:
                        ctrl.configure_pathway(iso_rules(16))
                    p = run_one(model, ctrl, inputs, yes_ids, no_ids)
                    emit(qid, 2, row["group"], gt, cond, p, seq, t0)
                del inputs
                torch.cuda.empty_cache()

        # ── PART 3: 관계형 경계 ───────────────────────────
        if "3" in args.parts:
            rows = json.loads(REL_PAIRS.read_text())
            if args.limit:
                rows = rows[: args.limit]
            print(f"PART3: {len(rows)} 문항 × 2조건")
            for row in rows:
                qid = f"iso{row['question_id']}"
                todo = [c for c in ("M", "ISO0") if (qid, c) not in done]
                if not todo:
                    continue
                q = Q_BOTH.format(obj=obj_phrase(row["article"], row["object"]))
                ims = [image_path(int(row["image1_id"]), COCO_IMG_DIR),
                       image_path(int(row["image2_id"]), COCO_IMG_DIR)]
                inputs = build_inputs(processor, ims, q, DEV, template)
                sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
                seq = int(inputs["input_ids"].shape[1])
                for cond in todo:
                    t0 = time.time()
                    if cond == "M":
                        ctrl.disable()
                    else:
                        ctrl.configure_pathway([(0, sp[1], sp[0])])
                    p = run_one(model, ctrl, inputs, yes_ids, no_ids)
                    emit(qid, 3, row["cell"], row["gt"], cond, p, seq, t0)
                del inputs
                torch.cuda.empty_cache()

        print(f"executed {executed}")

    # 요약 출력
    res = read_jsonl(OUT)
    for part in (1, 2, 3):
        sub = [r for r in res if r["part"] == part]
        if not sub:
            continue
        conds = sorted({r["condition"] for r in sub})
        cells = sorted({str(r["cell"]) for r in sub})
        print(f"\nPART{part}  ({len(sub)}건)")
        print("  " + " ".join(f"{c:>6}" for c in ["cell"] + conds))
        for cell in cells:
            accs = []
            for c in conds:
                v = [r["correct"] for r in sub
                     if str(r["cell"]) == cell and r["condition"] == c]
                accs.append(f"{sum(v)/len(v):6.3f}" if v else "     -")
            print(f"  {cell:>6} " + " ".join(accs))


if __name__ == "__main__":
    main()
