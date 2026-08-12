#!/usr/bin/env python
"""★ 1순위 게이트: 위치 confound 제거 — 관련 이미지를 2번 자리에 놓고 전부 재측정.

문제: 지금까지 모든 실험에서 관련 이미지가 항상 1번 자리였다. 따라서
  - "oracle 컨트롤러" ≡ "무조건 1번 고르기"
  - +28.7%p 중 얼마가 '배분 전략의 이득'이고 얼마가 '항상 1번이라는 사전정보'인지 분리 불가
  - 컨트롤러 식별률 99.8%도 위치 선호로 설명 가능

이 실험: 입력을 [방해][원본]으로 뒤집고 질문을 "In the second image, ..."로 바꿔
동일 조건을 재측정한다. 두 순서의 평균이 위치 무관한 진짜 효과다.

판정:
  - 뒤집기에서도 J4x28 > VTW16 격차가 유지 → 배분 이득은 실재
  - 격차가 절반 이하로 붕괴 → +28.7%p의 상당 부분이 위치 사전정보였음
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
OUT = RESULTS_DIR / f"posbal_results{TAG}.jsonl"
# 원 실험과 동일 조건 집합 (비교 가능해야 함)
CONDS = ["M", "T4", "T8", "T16", "T0", "J4x28", "VTW16"]


def apply_cond(ctrl, cond, sp_rel, sp_dis, n):
    """sp_rel/sp_dis는 '의미' 기준 — 위치와 무관하게 관련/방해 구간을 받는다."""
    if cond == "M":
        ctrl.disable()
    elif cond == "T0":
        ctrl.configure(0, sp_dis)
    elif cond.startswith("VTW"):
        k = int(cond[3:])
        ctrl.configure_multi([(k, sp_rel), (k, sp_dis)])
    elif cond.startswith("J"):
        a, b = (int(x) for x in cond[1:].split("x"))
        ctrl.configure_multi([(a, sp_dis), (b, sp_rel)])
    elif cond.startswith("T"):
        ctrl.configure(int(cond[1:]), sp_dis)
    else:
        blocked("16_posbal", f"unknown cond {cond}", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("16_position_balanced")
    if not torch.cuda.is_available():
        blocked("16_posbal", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = pd.read_csv(PAIRS_CSV).to_dict("records")
    if args.limit:
        rows = rows[: args.limit]
    print(f"{len(rows)} items × {len(CONDS)} conds (관련 이미지를 2번 자리로)")

    with stage("16_position_balanced"):
        model, processor = load_model_and_processor()
        n = num_layers(model)
        layers = resolve_decoder_layers(model)
        ctrl = KVBlockController(model, layers)
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()

        done = {(r["question_id"], r["condition"]) for r in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]
            todo = [c for c in CONDS if (qid, c) not in done]
            if not todo:
                continue
            # 뒤집힌 입력: [방해, 원본] + "In the second image, ..."
            q = PROMPT_MULTI_SECOND.format(obj=obj_phrase(row["article"], row["object"]))
            im_rel = image_path(int(row["image1_id"]), COCO_IMG_DIR)
            im_dis = image_path(int(row["image2_id"]), COCO_IMG_DIR)
            inp = build_inputs(processor, [im_dis, im_rel], q, DEV, template)
            spans = find_vision_spans(inp["input_ids"], vs, ve, pad)
            if len(spans) != 2:
                blocked("16_posbal", f"span != 2: {spans}", {"qid": qid})
            sp_dis, sp_rel = spans[0], spans[1]      # 방해가 1번, 관련이 2번
            for cond in todo:
                t0 = time.time()
                apply_cond(ctrl, cond, sp_rel, sp_dis, n)
                try:
                    out = model(**inp, use_cache=False)
                finally:
                    ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "cell": int(row["cell"]),
                                   "gt": row["gt"], "condition": cond, **p,
                                   "correct": p["pred"] == row["gt"], "n_layers": n,
                                   "order": "swapped",
                                   "rel_tokens": sp_rel[1] - sp_rel[0] + 1,
                                   "dis_tokens": sp_dis[1] - sp_dis[0] + 1,
                                   "seq_len": int(inp["input_ids"].shape[1]),
                                   "elapsed_ms": int(1000 * (time.time() - t0)),
                                   "ts": iso_now()})
                executed += 1
            if executed and executed % 700 < len(todo):
                print(f"  ~{executed} forwards")
        print(f"executed {executed}")

    # ---- 원 순서와 대조 ----
    res = read_jsonl(OUT)
    sw = {}
    for r in res:
        sw.setdefault(r["condition"], []).append(r["correct"])
    SW = {c: sum(v) / len(v) for c, v in sw.items()}

    orig = {}
    base = pd.read_csv(RESULTS_DIR / f"results{TAG}.csv")
    for c in ("M", "T4", "T8", "T16", "T0"):
        d = base[base["condition"] == c]
        if len(d):
            orig[c] = d["correct"].mean()
    ar = RESULTS_DIR / f"alloc_results{TAG}.jsonl"
    if ar.exists():
        agg = {}
        for r in read_jsonl(ar):
            agg.setdefault(r["condition"], []).append(r["correct"])
        for c in ("J4x28", "VTW16"):
            if c in agg:
                orig[c] = sum(agg[c]) / len(agg[c])

    print(f"\n{'조건':>8} | {'원 순서(관련=1번)':>16} | {'뒤집기(관련=2번)':>16} | {'차이':>7}")
    print("=" * 60)
    for c in CONDS:
        if c in orig and c in SW:
            print(f"{c:>8} | {orig[c]:>16.3f} | {SW[c]:>16.3f} | {SW[c]-orig[c]:>+7.3f}")
    if all(k in orig and k in SW for k in ("J4x28", "VTW16")):
        g0 = orig["J4x28"] - orig["VTW16"]
        g1 = SW["J4x28"] - SW["VTW16"]
        print(f"\n★ 배분 이득(J4x28 − VTW16)")
        print(f"   원 순서 : {g0*100:+.1f}%p")
        print(f"   뒤집기  : {g1*100:+.1f}%p")
        print(f"   양방향 평균: {(g0+g1)/2*100:+.1f}%p   ← 위치 무관한 진짜 효과")
        keep = g1 / g0 if g0 else float("nan")
        print(f"   유지율  : {keep:.0%}  " +
              ("→ 배분 이득 실재" if keep > 0.5 else "→ 상당 부분이 위치 사전정보였음"))


if __name__ == "__main__":
    main()
