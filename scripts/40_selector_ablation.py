#!/usr/bin/env python
"""selector를 바꿔가며 개입 수단을 고정 — 기여가 '판별'인가 '개입'인가 (docs/36).

anchor 벤치에서 우리 컨트롤러는 CLIP보다 약했다(K=2: 0.557 vs 0.817). 그렇다면
질문은 이것이다: **판별을 남이 해줘도 우리 개입이 이득인가?**

조건 (anchor_items, K∈{2,3}):
  CLIP_READ  : CLIP이 고른 것만 남기고 나머지 '읽기'만 차단
  CLIP_KEEP  : CLIP이 고른 것만 남기고 나머지 전면 차단   ← 앞단 selector + 이미지 제거 = 흔한 방식
  UNION_READ : CLIP과 우리 컨트롤러의 선택 합집합을 남기고 나머지 읽기 차단 (상호보완 검정)

기존 M / ORD_READ / REAL_READ(우리 pick)와 짝지어 분석한다.
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import torch
from sourcedepth.config import COCO_IMG_DIR, RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"selabl{TAG}.jsonl"
ITEMS = RESULTS_DIR / "anchor_items.json"
PROMPT = "In the image that contains {anchor}, is there {obj}? Answer with Yes or No."
CONDS = ["CLIP_READ", "CLIP_KEEP", "UNION_READ"]


def art(n): return "an" if n[0] in "aeiou" else "a"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("40_selector_ablation")
    if not torch.cuda.is_available(): blocked("40_sel", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = json.loads(ITEMS.read_text())
    if args.limit: rows = rows[: args.limit]
    clip = {x["question_id"]: x["clip_pred"] for x in read_jsonl(RESULTS_DIR / "anchor_clip.jsonl")}
    ours = {x["question_id"]: x["pick"] for x in read_jsonl(RESULTS_DIR / f"anchor{TAG}.jsonl")
            if x["condition"] == "REAL_READ" and "pick" in x}
    print(f"{len(rows)} 문항 · CLIP pick {len(clip)} · 우리 pick {len(ours)}")
    if len(clip) < 100: blocked("40_sel", "CLIP pick 부족", {"n": len(clip)})

    with stage("40_selector_ablation"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]; k = row["k"]
            if qid not in clip or qid not in ours: continue
            todo = [c for c in CONDS if (qid, c) not in done]
            if not todo: continue
            q = PROMPT.format(anchor=obj_phrase(art(row["anchor"]), row["anchor"]),
                              obj=obj_phrase(art(row["object"]), row["object"]))
            paths = [image_path(i, COCO_IMG_DIR) for i in row["image_ids"]]
            inputs = build_inputs(processor, paths, q, DEV, template)
            sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
            if len(sp) != k: blocked("40_sel", f"span != {k}", {"qid": qid})
            seq = int(inputs["input_ids"].shape[1]); ts = (sp[-1][1] + 1, seq - 1)
            cp, op = clip[qid], ours[qid]
            for cond in todo:
                t0 = time.time()
                keep = {cp} if cond.startswith("CLIP") else {cp, op}
                others = [i for i in range(k) if i not in keep]
                if not others: ctrl.disable()
                elif cond == "CLIP_KEEP": ctrl.configure_pathway([(0, None, sp[i]) for i in others])
                else: ctrl.configure_pathway([(0, ts, sp[i]) for i in others])
                try:
                    try: out = model(**inputs, use_cache=False)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache(); out = model(**inputs, use_cache=False)
                finally: ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "k": k, "cell": row["cell"],
                                   "gt": row["gt"], "rel_pos": row["rel_pos"], "condition": cond,
                                   "clip_pick": cp, "our_pick": op, **p,
                                   "correct": p["pred"] == row["gt"], "n_layers": nlay,
                                   "seq_len": seq, "elapsed_ms": int(1000*(time.time()-t0)),
                                   "ts": iso_now()})
                executed += 1; del out
            del inputs
            torch.cuda.empty_cache()
        print(f"executed {executed}")


if __name__ == "__main__": main()
