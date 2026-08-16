#!/usr/bin/env python
"""(A) 더 어려운 need-all 태스크 + (B) 소프트 개입 λ 스윕.

## A. HARD need-all  —  "Do ALL of these images contain X?"
직전 파일럿의 "any of these images"는 AUC 0.99로 천장이었다 (하나만 찾으면 끝).
"ALL"은 **모든 이미지를 확인해야** 답할 수 있다:
  ALLY : X가 3장 전부에 있음        → gt yes
  ALLN : X가 3장 중 2장에만 있음     → gt no  (빠진 한 장을 못 보면 틀림)
→ 앞단 selector가 어떤 이미지도 버릴 수 없는 **진짜** need-all. 조건: M3 / ISO0 / ISO16

## B. 소프트 개입 λ 스윕  (pairs.csv 셀1·2, "first image")
하드 차단(-inf) 대신 **유한한 음수 bias λ** 를 방해 이미지 열에 더한다.
λ=0 무개입 → λ→∞ 하드 차단. 중간에 최적이 있는가? 완만한가?
앞단 selector는 all-or-nothing이라 이 축 자체가 없다 — 우리 개입의 구조적 차별점.
조건: SOFT1 / SOFT2 / SOFT4 / SOFT8  (+ 기존 M·T0와 비교)
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
from sourcedepth.eval.loop import obj_phrase, questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import (append_jsonl, blocked, dump_env, iso_now,
                                read_jsonl, stage)

DEV = "cuda:0"
OUT = RESULTS_DIR / f"hardsoft{TAG}.jsonl"
ALL_ITEMS = RESULTS_DIR / "allof3_items.json"
Q_ALL = "Do all of these images contain {obj}? Answer with Yes or No."
LAMBDAS = [1.0, 2.0, 4.0, 8.0]
N_PER = 150


def build_allof3():
    """ALLY: 3장 전부 객체 보유 / ALLN: 2장만 보유(1장 결여)."""
    idx = build_indices(COCO_INSTANCES)
    have = {i for i in idx.img2cats if image_path(i, COCO_IMG_DIR).exists()}
    rng = random.Random(SEED)
    out = []
    for r in pd.read_csv(PAIRS_CSV).to_dict("records"):
        cat = int(r["category_id"])
        with_o = [i for i in sorted(have) if cat in idx.img2cats.get(i, set())]
        without = [i for i in sorted(have) if cat not in idx.img2cats.get(i, set())]
        if len(with_o) < 3 or not without:
            continue
        grp = "ALLY" if len(out) % 2 == 0 else "ALLN"
        if grp == "ALLY":
            ims = rng.sample(with_o, 3)
        else:
            ims = rng.sample(with_o, 2) + [rng.choice(without)]
            rng.shuffle(ims)                      # 결여 이미지 위치 무작위 — 위치 confound 방지
        out.append({"question_id": f"a3{r['question_id']}", "group": grp,
                    "gt": "yes" if grp == "ALLY" else "no",
                    "article": r["article"], "object": r["object"],
                    "category_id": cat, "images": [int(x) for x in ims]})
    final = []
    for g in ("ALLY", "ALLN"):
        final += [x for x in out if x["group"] == g][:N_PER]
    print(f"all-of-3 문항: " + str({g: sum(x['group'] == g for x in final)
                                    for g in ('ALLY', 'ALLN')}))
    ALL_ITEMS.write_text(json.dumps(final, ensure_ascii=False))
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--parts", default="AB")
    args = ap.parse_args()
    dump_env("25_hard_needall_soft")
    if not torch.cuda.is_available():
        blocked("25_hardsoft", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]

    with stage("25_hard_needall_soft"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0

        def go(qid, part, cell, gt, cond, inputs, seq):
            nonlocal executed
            t0 = time.time()
            try:
                try:
                    out = model(**inputs, use_cache=False)
                except torch.cuda.OutOfMemoryError:
                    torch.cuda.empty_cache()
                    out = model(**inputs, use_cache=False)
            finally:
                ctrl.disable()
            p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
            append_jsonl(OUT, {"question_id": qid, "part": part, "cell": cell, "gt": gt,
                               "condition": cond, **p, "correct": p["pred"] == gt,
                               "n_layers": nlay, "seq_len": seq,
                               "elapsed_ms": int(1000 * (time.time() - t0)),
                               "ts": iso_now()})
            executed += 1

        # ── A. HARD need-all ──────────────────────────────
        if "A" in args.parts:
            rows = (json.loads(ALL_ITEMS.read_text())
                    if ALL_ITEMS.exists() else build_allof3())
            if args.limit:
                rows = rows[: args.limit]
            print(f"PART A: {len(rows)} 문항 × 3조건")
            for row in rows:
                qid = row["question_id"]
                todo = [c for c in ("M3", "ISO0", "ISO16") if (qid, c) not in done]
                if not todo:
                    continue
                q = Q_ALL.format(obj=obj_phrase(row["article"], row["object"]))
                ims = [image_path(i, COCO_IMG_DIR) for i in row["images"]]
                inputs = build_inputs(processor, ims, q, DEV, template)
                sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
                if len(sp) != 3:
                    blocked("25_hardsoft", f"span != 3: {len(sp)}", {"qid": qid})
                seq = int(inputs["input_ids"].shape[1])
                iso = lambda bf: [(bf, sp[j], sp[i])
                                  for j in range(3) for i in range(3) if i < j]
                for cond in todo:
                    if cond == "M3":
                        ctrl.disable()
                    else:
                        ctrl.configure_pathway(iso(0 if cond == "ISO0" else 16))
                    go(qid, "A", row["group"], row["gt"], cond, inputs, seq)
                del inputs
                torch.cuda.empty_cache()

        # ── B. 소프트 λ 스윕 ──────────────────────────────
        if "B" in args.parts:
            rows = [r for r in pd.read_csv(PAIRS_CSV).to_dict("records")
                    if int(r["cell"]) in (1, 2)]
            if args.limit:
                rows = rows[: args.limit]
            print(f"PART B: {len(rows)} 문항 × {len(LAMBDAS)}조건")
            for row in rows:
                qid = f"sf{row['question_id']}"
                todo = [f"SOFT{int(l)}" for l in LAMBDAS
                        if (qid, f"SOFT{int(l)}") not in done]
                if not todo:
                    continue
                q_multi, _ = questions_for(row)
                ims = [image_path(int(row["image1_id"]), COCO_IMG_DIR),
                       image_path(int(row["image2_id"]), COCO_IMG_DIR)]
                inputs = build_inputs(processor, ims, q_multi, DEV, template)
                sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
                seq = int(inputs["input_ids"].shape[1])
                for cond in todo:
                    lam = float(cond[4:])
                    ctrl.configure_soft([(0, sp[1], lam)])
                    go(qid, "B", str(row["cell"]), row["gt"], cond, inputs, seq)
                del inputs
                torch.cuda.empty_cache()

        print(f"executed {executed}")


if __name__ == "__main__":
    main()
