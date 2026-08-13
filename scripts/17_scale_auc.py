#!/usr/bin/env python
"""판별력 손상이 출처 수 N에 비례하는가 — AUC를 주 종점으로.

docs/16_scale_auc_prereg.md 참조.

설계: 셀1(gt=no, 방해에 질의 객체 O) 150 + 셀2(gt=yes, 방해에 질의 객체 X) 150 = 300문항.
양쪽 모두 방해 이미지가 **오답 방향으로** 압력을 준다. gt가 균형이므로 AUC 계산 가능.

방해 이미지를 N=1,2,3으로 늘리되 **중첩**시킨다(N=1의 방해가 N=2·3에도 포함) → N만 달라짐.
조건: S(1장, N무관 1회) / 각 N에 대해 M(무개입) · T0(전층 차단) · T4(4층부터 차단)

주 종점: AUC(M) 이 N에 따라 단조 감소하는가 (모델별)
부 종점: ΔAUC(T0 − M) 이 각 N에서 유의하게 양수인가 (회복)
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch

from sourcedepth.config import (COCO_IMG_DIR, COCO_INSTANCES, PAIRS_CSV,
                                RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE)
from sourcedepth.data.coco_index import build_indices
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
OUT = RESULTS_DIR / f"scale_auc{TAG}.jsonl"
ITEMS = RESULTS_DIR / "scale_auc_items.json"
NS = [1, 2, 3]
CONDS_N = ["M", "T0", "T4"]
MAX_D = max(NS)


def build_items():
    """셀1·셀2에 방해 이미지를 MAX_D장까지 중첩 구성. 셀1은 객체 포함, 셀2는 미포함."""
    idx = build_indices(COCO_INSTANCES)
    have = {i for i in idx.img2cats if image_path(i, COCO_IMG_DIR).exists()}
    rng = random.Random(SEED)
    out = []
    for r in pd.read_csv(PAIRS_CSV).to_dict("records"):
        cell = int(r["cell"])
        if cell not in (1, 2):
            continue
        cat = int(r["category_id"])
        contains = (cell == 1)          # 셀1: 방해에 객체 O / 셀2: 방해에 객체 X
        used = {int(r["image1_id"]), int(r["image2_id"])}
        pool = [i for i in sorted(have)
                if i not in used and ((cat in idx.img2cats.get(i, set())) == contains)]
        if len(pool) < MAX_D - 1:
            continue
        extra = rng.sample(pool, MAX_D - 1)
        out.append({"question_id": f"sc{r['question_id']}", "cell": cell,
                    "gt": r["gt"], "article": r["article"], "object": r["object"],
                    "category_id": cat, "image1_id": int(r["image1_id"]),
                    "distractors": [int(r["image2_id"])] + [int(x) for x in extra]})
    n1 = sum(x["cell"] == 1 for x in out)
    n2 = sum(x["cell"] == 2 for x in out)
    print(f"items: cell1(gt=no)={n1}  cell2(gt=yes)={n2}")
    if min(n1, n2) < 100:
        blocked("17_scale_auc", f"문항 부족 cell1={n1} cell2={n2}", {})
    ITEMS.write_text(json.dumps(out, ensure_ascii=False))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("17_scale_auc")
    if not torch.cuda.is_available():
        blocked("17_scale_auc", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]

    rows = json.loads(ITEMS.read_text()) if ITEMS.exists() else build_items()
    if args.limit:
        rows = rows[: args.limit]

    todo_all = [("S", 0)] + [(c, n) for n in NS for c in CONDS_N]
    print(f"{len(rows)} 문항 × {len(todo_all)} 조건 = {len(rows) * len(todo_all)}회")

    with stage("17_scale_auc"):
        model, processor = load_model_and_processor()
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()

        done = {(x["question_id"], x["condition"], x["n_dist"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]
            todo = [(c, n) for (c, n) in todo_all if (qid, c, n) not in done]
            if not todo:
                continue
            q_multi, q_single = questions_for(row)
            im1 = image_path(row["image1_id"], COCO_IMG_DIR)
            dis = [image_path(d, COCO_IMG_DIR) for d in row["distractors"]]

            cache = {}   # n -> (inputs, spans)
            for cond, n in todo:
                t0 = time.time()
                if cond == "S":
                    ctrl.disable()
                    inputs = build_inputs(processor, [im1], q_single, DEV, template)
                else:
                    if n not in cache:
                        inp = build_inputs(processor, [im1] + dis[:n], q_multi, DEV, template)
                        sp = find_vision_spans(inp["input_ids"], vs, ve, pad)
                        if len(sp) != n + 1:
                            blocked("17_scale_auc",
                                    f"span 수 불일치: N={n} 기대 {n+1}, 실제 {len(sp)}", {"qid": qid})
                        cache[n] = (inp, sp)
                    inputs, sp = cache[n]
                    if cond == "M":
                        ctrl.disable()
                    else:
                        bf = 0 if cond == "T0" else int(cond[1:])
                        ctrl.configure_multi([(bf, s) for s in sp[1:]])
                try:
                    out = model(**inputs, use_cache=False)
                finally:
                    ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "cell": row["cell"],
                                   "gt": row["gt"], "condition": cond, "n_dist": n,
                                   **p, "correct": p["pred"] == row["gt"],
                                   "n_layers": nlay,
                                   "seq_len": int(inputs["input_ids"].shape[1]),
                                   "elapsed_ms": int(1000 * (time.time() - t0)),
                                   "ts": iso_now()})
                executed += 1
            if executed and executed % 400 == 0:
                print(f"  {executed}회 완료")
        print(f"executed {executed}")

    res = read_jsonl(OUT)
    print(f"\n{'cond':>5} {'N':>2} {'정확도':>8}  n")
    for cond, n in todo_all:
        sub = [r for r in res if r["condition"] == cond and r["n_dist"] == n]
        if sub:
            print(f"{cond:>5} {n:>2} {sum(x['correct'] for x in sub)/len(sub):8.4f}  {len(sub)}")


if __name__ == "__main__":
    main()
