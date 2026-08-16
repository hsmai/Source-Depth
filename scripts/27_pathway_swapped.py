#!/usr/bin/env python
"""순서를 뒤집은 경로 분해 — "읽기 경로뿐"이 자명한 결과인지 조건부 사실인지 가른다.

원순서 [관련, 방해, 질문]에서는 관련 이미지가 방해를 볼 수 없으므로(causal),
방해의 영향 경로가 '질문 → 방해' 하나로 **구조상 강제**된다. 즉 READ ≡ T0 는 발견이 아니다.

뒤집은 순서 [방해, 관련, 질문]에서는 **관련 이미지가 방해를 볼 수 있다.**
→ 표현 오염 경로(방해 → 관련)가 실제로 존재한다. 이제 질문이 성립한다:

  방해의 해악 중 얼마가 '표현 오염'이고 얼마가 '읽기 오귀속'인가?

조건 (질문은 "In the second image, ..."):
  M      : 무개입
  XIMG   : 관련(2번) → 방해(1번) 경로 차단   ← 표현 오염 경로. 원순서에는 없던 것
  READ   : 질문 → 방해(1번) 경로 차단        ← 읽기 경로
  T0     : 방해(1번) 키 전면 차단
  BOTH   : XIMG + READ 동시 차단

예측(사전 기록):
  P1. 원순서와 달리 READ < T0 이 된다 (읽기만 막아서는 부족 — 표현 경로가 남음)
  P2. XIMG 단독은 M보다 개선된다 (원순서에서는 −0.29로 악화됐던 것과 반대)
  P3. BOTH ≈ T0
  P1이 성립하면 "해악의 경로 구성은 입력 순서가 정한다"가 되고,
  원순서 결과는 자명한 게 아니라 **경계 조건이 특정된 사실**이 된다.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch

from sourcedepth.config import (COCO_IMG_DIR, PAIRS_CSV, PROMPT_MULTI_SECOND,
                                RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import (append_jsonl, blocked, dump_env, iso_now,
                                read_jsonl, stage)

DEV = "cuda:0"
OUT = RESULTS_DIR / f"pathway_swap{TAG}.jsonl"
CONDS = ["M", "XIMG", "READ", "T0", "BOTH"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("27_pathway_swapped")
    if not torch.cuda.is_available():
        blocked("27_swap", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = [r for r in pd.read_csv(PAIRS_CSV).to_dict("records")
            if int(r["cell"]) in (1, 2)]
    if args.limit:
        rows = rows[: args.limit]
    print(f"{len(rows)} 문항 × {len(CONDS)} 조건 (뒤집은 순서: [방해, 관련, 질문])")

    with stage("27_pathway_swapped"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = f"sw{row['question_id']}"
            todo = [c for c in CONDS if (qid, c) not in done]
            if not todo:
                continue
            q = PROMPT_MULTI_SECOND.format(obj=obj_phrase(row["article"], row["object"]))
            # 뒤집기: 방해(image2)를 먼저, 관련(image1)을 두 번째로
            ims = [image_path(int(row["image2_id"]), COCO_IMG_DIR),
                   image_path(int(row["image1_id"]), COCO_IMG_DIR)]
            inputs = build_inputs(processor, ims, q, DEV, template)
            sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
            if len(sp) != 2:
                blocked("27_swap", f"span != 2: {len(sp)}", {"qid": qid})
            dis, rel = sp[0], sp[1]                     # 방해=1번 자리, 관련=2번 자리
            seq = int(inputs["input_ids"].shape[1])
            ts = (sp[-1][1] + 1, seq - 1)
            for cond in todo:
                t0 = time.time()
                if cond == "M":
                    ctrl.disable()
                elif cond == "XIMG":
                    ctrl.configure_pathway([(0, rel, dis)])          # 관련 → 방해
                elif cond == "READ":
                    ctrl.configure_pathway([(0, ts, dis)])           # 질문 → 방해
                elif cond == "BOTH":
                    ctrl.configure_pathway([(0, rel, dis), (0, ts, dis)])
                else:
                    ctrl.configure_pathway([(0, None, dis)])         # 전면
                try:
                    try:
                        out = model(**inputs, use_cache=False)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache()
                        out = model(**inputs, use_cache=False)
                finally:
                    ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "cell": int(row["cell"]),
                                   "gt": row["gt"], "condition": cond, **p,
                                   "correct": p["pred"] == row["gt"],
                                   "n_layers": nlay, "seq_len": seq,
                                   "elapsed_ms": int(1000 * (time.time() - t0)),
                                   "ts": iso_now()})
                executed += 1
                del out
            del inputs
            torch.cuda.empty_cache()
        print(f"executed {executed}")

    res = read_jsonl(OUT)
    print(f"\n{'cond':>6} {'정확도':>8}  n")
    for c in CONDS:
        sub = [r for r in res if r["condition"] == c]
        if sub:
            print(f"{c:>6} {sum(x['correct'] for x in sub)/len(sub):8.4f}  {len(sub)}")


if __name__ == "__main__":
    main()
