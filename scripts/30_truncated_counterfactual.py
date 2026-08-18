#!/usr/bin/env python
"""층 절단 반사실 — 컨트롤러를 싸게 만들 수 있는가 (FOCUS 대비 비용 우위의 생사).

현재 컨트롤러(0.730)는 각 이미지를 **0층부터** 마스킹한 반사실을 쓴다 → forward N+1회 전액.
만약 **L층부터만** 마스킹해도 신호가 유지된다면, 앞쪽 L층은 캐시 재사용이 가능해
반사실 하나당 (1 − L/n_layers) 비용으로 줄어든다.

조건 (3B, N=3, 4장): M + B{i}@L  for i in 0..3, L in {8, 16, 24}
(L=0은 results/loo.jsonl 에 이미 있음)

판정: L별 컨트롤러 정확도 = argmax_i |margin(B_i@L) − margin(M)| == 0 인 비율.
      L=16에서 0.70 이상 유지되면 → 비용 우위 주장 성립.
      크게 떨어지면 → 비용 우위를 버리고 경로 선택성만으로 간다.
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import torch
from sourcedepth.config import COCO_IMG_DIR, RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"trunc_cf{TAG}.jsonl"
ITEMS = RESULTS_DIR / "scale_auc_items.json"
N_DIST = 3
LS = [8, 16, 24]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("30_truncated_counterfactual")
    if not torch.cuda.is_available(): blocked("30_trunc", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = json.loads(ITEMS.read_text())
    if args.limit: rows = rows[: args.limit]
    CONDS = ["M"] + [f"B{i}@{l}" for l in LS for i in range(N_DIST + 1)]
    print(f"{len(rows)} 문항 × {len(CONDS)} 조건 = {len(rows)*len(CONDS)}회")
    with stage("30_truncated_counterfactual"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]
            todo = [c for c in CONDS if (qid, c) not in done]
            if not todo: continue
            q_multi, _ = questions_for(row)
            ims = [image_path(row["image1_id"], COCO_IMG_DIR)] + \
                  [image_path(d, COCO_IMG_DIR) for d in row["distractors"][:N_DIST]]
            inputs = build_inputs(processor, ims, q_multi, DEV, template)
            sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
            if len(sp) != N_DIST + 1:
                blocked("30_trunc", f"span != {N_DIST+1}: {len(sp)}", {"qid": qid})
            seq = int(inputs["input_ids"].shape[1])
            for cond in todo:
                t0 = time.time()
                if cond == "M": ctrl.disable()
                else:
                    i, l = cond[1:].split("@")
                    ctrl.configure_multi([(int(l), sp[int(i)])])
                try:
                    try: out = model(**inputs, use_cache=False)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache(); out = model(**inputs, use_cache=False)
                finally: ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "cell": row["cell"], "gt": row["gt"],
                                   "condition": cond, "n_dist": N_DIST, **p,
                                   "correct": p["pred"] == row["gt"], "n_layers": nlay,
                                   "seq_len": seq, "elapsed_ms": int(1000*(time.time()-t0)),
                                   "ts": iso_now()})
                executed += 1; del out
            del inputs; torch.cuda.empty_cache()
        print(f"executed {executed}")

if __name__ == "__main__": main()
