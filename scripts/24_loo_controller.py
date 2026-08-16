#!/usr/bin/env python
"""이미지별 leave-one-out — 오라클 없는 인과 컨트롤러의 정직한 성능.

앞선 오프라인 계산은 N≥2에서 T0(방해 '전부' 차단)를 썼기 때문에 leave-one-out이 아니었다.
여기서는 **이미지 하나씩만** 차단해 N+1개의 반사실(counterfactual)을 만든다.

조건 (scale_auc_items.json 재사용, N ∈ {1,2,3}):
  M          : 무개입
  B{i}       : i번째 이미지만 0층부터 차단  (i = 0..N, 0번이 관련 이미지)

컨트롤러 규칙(사전 고정): 제거했을 때 |Δmargin| 이 가장 큰 이미지를 '관련'으로 판정하고,
그 이미지를 제외한 나머지를 차단한 조건을 최종 출력으로 쓴다.
→ 위치를 참조하지 않으므로 위치 편향이 구조적으로 불가능.

비용: forward N+1회. 효율 트랙이 아니라 **정확도 트랙**임을 명시할 것.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import torch

from sourcedepth.config import (COCO_IMG_DIR, RESULTS_DIR, SEED, TAG,
                                TEMPLATE_CHOICE)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import (append_jsonl, blocked, dump_env, iso_now,
                                read_jsonl, stage)

DEV = "cuda:0"
OUT = RESULTS_DIR / f"loo{TAG}.jsonl"
ITEMS = RESULTS_DIR / "scale_auc_items.json"
NS = [1, 2, 3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("24_loo_controller")
    if not torch.cuda.is_available():
        blocked("24_loo", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = json.loads(ITEMS.read_text())
    if args.limit:
        rows = rows[: args.limit]
    total = sum(len(rows) * (n + 2) for n in NS)      # M + B0..BN
    print(f"{len(rows)} 문항, N∈{NS} → 약 {total}회")

    with stage("24_loo_controller"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"], x["n_dist"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]
            q_multi, _ = questions_for(row)
            im1 = image_path(row["image1_id"], COCO_IMG_DIR)
            dis = [image_path(d, COCO_IMG_DIR) for d in row["distractors"]]
            for n in NS:
                conds = ["M"] + [f"B{i}" for i in range(n + 1)]
                todo = [c for c in conds if (qid, c, n) not in done]
                if not todo:
                    continue
                inputs = build_inputs(processor, [im1] + dis[:n], q_multi, DEV, template)
                sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
                if len(sp) != n + 1:
                    blocked("24_loo", f"span != {n+1}: {len(sp)}", {"qid": qid})
                seq = int(inputs["input_ids"].shape[1])
                for cond in todo:
                    t0 = time.time()
                    if cond == "M":
                        ctrl.disable()
                    else:
                        ctrl.configure_multi([(0, sp[int(cond[1:])])])
                    try:
                        try:
                            out = model(**inputs, use_cache=False)
                        except torch.cuda.OutOfMemoryError:
                            torch.cuda.empty_cache()
                            out = model(**inputs, use_cache=False)
                    finally:
                        ctrl.disable()
                    p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                    append_jsonl(OUT, {"question_id": qid, "cell": row["cell"],
                                       "gt": row["gt"], "condition": cond, "n_dist": n,
                                       **p, "correct": p["pred"] == row["gt"],
                                       "n_layers": nlay, "seq_len": seq,
                                       "elapsed_ms": int(1000 * (time.time() - t0)),
                                       "ts": iso_now()})
                    executed += 1
                    del out
                del inputs, sp
                torch.cuda.empty_cache()
        print(f"executed {executed}")


if __name__ == "__main__":
    main()
