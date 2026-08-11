#!/usr/bin/env python
"""A1 (핵심) + A2 baseline: per-image 차등 depth 배분의 직접 실증 (탐색적).

세 블록:
  (a) Rel{L}   — **관련 이미지**를 layer L 이후 차단. "관련 이미지는 몇 층이나 필요한가?"
                 → 어떤 L<36에서 정확도가 유지되면, 관련 이미지도 full depth가 불필요 = 중간 depth
  (b) J{L1}x{L2} — distractor L1 + relevant L2 **동시** 차단. per-image adaptive depth의 실제 구현체.
                 목표: M 수준 정확도를 유지하면서 두 이미지가 서로 다른 depth를 갖는 배분 존재 입증
  (c) VTW{K}   — 두 이미지를 **동일 K**에서 일괄 차단 (VTW/AAAI'25식 uniform withdrawal의 등가 재현).
                 우리 방법과 동일 예산에서 비교할 baseline. VTW 원 논문의 실용 K=16 포함.
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
                                TEMPLATE_CHOICE)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / "alloc_results.jsonl"

REL_LS = [12, 16, 20, 24, 28, 32]          # (a) 관련 이미지 depth 요구량
JOINT = [(4, 32), (4, 28), (4, 24), (8, 28)]   # (b) (distractor L1, relevant L2)
VTW_KS = [8, 16, 24, 28]                   # (c) uniform withdrawal (VTW 실용 K=16 포함)


def conditions():
    return ([f"Rel{L}" for L in REL_LS]
            + [f"J{a}x{b}" for a, b in JOINT]
            + [f"VTW{k}" for k in VTW_KS])


def apply_cond(ctrl, cond, sp_rel, sp_dis):
    if cond.startswith("Rel"):
        ctrl.configure(int(cond[3:]), sp_rel)
    elif cond.startswith("VTW"):
        k = int(cond[3:])
        ctrl.configure_multi([(k, sp_rel), (k, sp_dis)])
    elif cond.startswith("J"):
        a, b = cond[1:].split("x")
        ctrl.configure_multi([(int(a), sp_dis), (int(b), sp_rel)])
    else:
        blocked("11_alloc", f"unknown cond {cond}", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="디버그용 문항 수 제한")
    args = ap.parse_args()

    dump_env("11_allocation")
    if not torch.cuda.is_available():
        blocked("11_alloc", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = pd.read_csv(PAIRS_CSV).to_dict("records")
    if args.limit:
        rows = rows[: args.limit]
    conds = conditions()
    print(f"{len(rows)} items × {len(conds)} conds = {len(rows) * len(conds)} forwards")

    with stage("11_allocation"):
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
            todo = [c for c in conds if (qid, c) not in done]
            if not todo:
                continue
            q_multi, _ = questions_for(row)
            inp = build_inputs(processor,
                               [image_path(int(row["image1_id"]), COCO_IMG_DIR),
                                image_path(int(row["image2_id"]), COCO_IMG_DIR)],
                               q_multi, DEV, template)
            sp_rel, sp_dis = find_vision_spans(inp["input_ids"], vs, ve, pad)
            for cond in todo:
                t0 = time.time()
                apply_cond(ctrl, cond, sp_rel, sp_dis)
                try:
                    out = model(**inp, use_cache=False)
                finally:
                    ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "cell": int(row["cell"]),
                                   "gt": row["gt"], "condition": cond, **p,
                                   "correct": p["pred"] == row["gt"],
                                   "n_layers": n,
                                   "rel_tokens": sp_rel[1] - sp_rel[0] + 1,
                                   "dis_tokens": sp_dis[1] - sp_dis[0] + 1,
                                   "seq_len": int(inp["input_ids"].shape[1]),
                                   "elapsed_ms": int(1000 * (time.time() - t0)),
                                   "ts": iso_now()})
                executed += 1
            if executed and executed % 500 < len(todo):
                print(f"  ~{executed} forwards done")
        print(f"executed {executed}")

    # 요약 (셀별 accuracy) + FLOPs 절감 병기
    res = read_jsonl(OUT)
    base = pd.read_csv(RESULTS_DIR / "results.csv")
    ref = {c: base[base["condition"] == c].groupby("cell")["correct"].mean().to_dict()
           for c in ("M", "T0", "T4")}
    rel_tok = pd.DataFrame(res)["rel_tokens"].median()
    dis_tok = pd.DataFrame(res)["dis_tokens"].median()
    seq = pd.DataFrame(res)["seq_len"].median()

    def saving(cond):
        if cond.startswith("Rel"):
            return rel_tok * (n - int(cond[3:])) / (seq * n)
        if cond.startswith("VTW"):
            k = int(cond[3:])
            return (rel_tok + dis_tok) * (n - k) / (seq * n)
        a, b = (int(x) for x in cond[1:].split("x"))
        return (dis_tok * (n - a) + rel_tok * (n - b)) / (seq * n)

    print(f"\n{'condition':>10} | " + " | ".join(f"c{c}" for c in (1, 2, 3, 4)) +
          " |  all  | FLOPs saved")
    for c in ("M", "T0", "T4"):
        accs = ref[c]
        allacc = base[base["condition"] == c]["correct"].mean()
        print(f"{c:>10} | " + " | ".join(f"{accs.get(i, float('nan')):.3f}" for i in (1, 2, 3, 4))
              + f" | {allacc:.3f} | (reference)")
    for cond in conds:
        sub = [r for r in res if r["condition"] == cond]
        if not sub:
            continue
        line = []
        for cell in (1, 2, 3, 4):
            cc = [r for r in sub if r["cell"] == cell]
            line.append(sum(r["correct"] for r in cc) / max(1, len(cc)))
        allacc = sum(r["correct"] for r in sub) / len(sub)
        print(f"{cond:>10} | " + " | ".join(f"{v:.3f}" for v in line)
              + f" | {allacc:.3f} | {saving(cond):.1%}")


if __name__ == "__main__":
    main()
