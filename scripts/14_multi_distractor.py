#!/usr/bin/env python
"""PART D 사전 등록 실패 대응 (b): distractor를 2장으로 증가.

브리프 PART D "실패 시 대응": "①이 안 나오면 (a) 시각 유사 distractor 교체, (b) distractor 2장으로 증가."
7B에서 ①(문제 실재)이 FAIL(flip 0.7%)했으므로 (b)를 사전 등록된 절차대로 실행한다.
— 이것은 결과를 보고 벤치를 갈아타는 것이 아니라, 실험 전 문서화된 대응 경로다.

가설: 오염은 모델 크기보다 **경쟁하는 출처의 수**에 더 민감하다. 3장(원본+방해 2장)이면
7B에서도 오염이 나타날 수 있다.

구성 (기존 pairs.csv 재사용, 신규 다운로드 없음):
  M3-leak : [원본(정답 no), 방해1(객체 O), 방해2(객체 O)]  ← 오염 압력 최대
  M3-ctrl : [원본(정답 no), 방해1(객체 X), 방해2(객체 X)]  ← 대조군
조건: S(1장) / M(3장 차단없음) / T4·T8·T16 / T0(방해 2장 모두 전층 차단)
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

from sourcedepth.config import (COCO_IMG_DIR, COCO_INSTANCES, LOGS_DIR,
                                PAIRS_CSV, RESULTS_DIR, SEED, TAG,
                                TEMPLATE_CHOICE)
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
OUT = RESULTS_DIR / f"md_results{TAG}.jsonl"
PAIRS3 = RESULTS_DIR / "md_pairs.json"
CONDS = ["S", "M", "T4", "T8", "T16", "T0"]
N_PER = 150


def build_triples():
    """기존 pairs.csv의 셀1(방해에 객체 O)·셀3(방해에 객체 X)에 두 번째 방해 이미지를 추가."""
    idx = build_indices(COCO_INSTANCES)
    have = {i for i in idx.img2cats if image_path(i, COCO_IMG_DIR).exists()}
    rng = random.Random(SEED)
    pairs = pd.read_csv(PAIRS_CSV).to_dict("records")
    out = []
    for r in pairs:
        if int(r["cell"]) not in (1, 3):
            continue
        cat = int(r["category_id"])
        contains = int(r["cell"]) == 1        # 셀1은 방해에 객체 존재
        used = {int(r["image1_id"]), int(r["image2_id"])}
        pool = [i for i in have
                if i not in used and ((cat in idx.img2cats.get(i, set())) == contains)]
        if not pool:
            continue
        d2 = rng.choice(pool)
        out.append({"question_id": f"md{r['question_id']}",
                    "group": "leak" if contains else "ctrl",
                    "gt": r["gt"], "article": r["article"], "object": r["object"],
                    "category_id": cat,
                    "image1_id": int(r["image1_id"]),
                    "image2_id": int(r["image2_id"]),
                    "image3_id": int(d2)})
    # 그룹별 상위 N_PER
    final = []
    for g in ("leak", "ctrl"):
        sub = [x for x in out if x["group"] == g][:N_PER]
        if len(sub) < N_PER:
            print(f"WARN: {g} 그룹 {len(sub)}개 (목표 {N_PER}) — 가용 풀 한계, 그대로 진행")
        final += sub
    PAIRS3.write_text(json.dumps(final, ensure_ascii=False))
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("14_multi_distractor")
    if not torch.cuda.is_available():
        blocked("14_md", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]

    rows = json.loads(PAIRS3.read_text()) if PAIRS3.exists() else build_triples()
    if args.limit:
        rows = rows[: args.limit]
    print(f"triples: leak={sum(r['group']=='leak' for r in rows)} "
          f"ctrl={sum(r['group']=='ctrl' for r in rows)} × {len(CONDS)} conds")

    with stage("14_multi_distractor"):
        model, processor = load_model_and_processor()
        n = num_layers(model)
        layers = resolve_decoder_layers(model)
        ctrl = KVBlockController(model, layers)
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        tok = processor.tokenizer

        # grounding 확인 (3장에서도 'first image'가 먹히는지 — 육안 로그)
        glog = [f"# 3-image grounding check {iso_now()}"]
        for r in rows[:4] + rows[N_PER:N_PER + 2]:
            q, _ = questions_for(r)
            ims = [image_path(r[f"image{i}_id"], COCO_IMG_DIR) for i in (1, 2, 3)]
            inp = build_inputs(processor, ims, q, DEV, template)
            gen = model.generate(**inp, max_new_tokens=8, do_sample=False)
            glog.append(f"- [{r['group']}] {r['object']} gt={r['gt']} → "
                        f"{tok.decode(gen[0, inp['input_ids'].shape[1]:], skip_special_tokens=True)!r}")
        (LOGS_DIR / f"md_grounding{TAG}.md").write_text("\n".join(glog))
        print("\n".join(glog))

        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]
            todo = [c for c in CONDS if (qid, c) not in done]
            if not todo:
                continue
            q_multi, q_single = questions_for(row)
            ims = [image_path(row[f"image{i}_id"], COCO_IMG_DIR) for i in (1, 2, 3)]
            in_s = in_m = sp = None
            if "S" in todo:
                in_s = build_inputs(processor, [ims[0]], q_single, DEV, template)
            if any(c != "S" for c in todo):
                in_m = build_inputs(processor, ims, q_multi, DEV, template)
                sp = find_vision_spans(in_m["input_ids"], vs, ve, pad)
                if len(sp) != 3:
                    blocked("14_md", f"3장 layout span 수 != 3: {sp}", {"qid": qid})
            for cond in todo:
                t0 = time.time()
                if cond == "S":
                    ctrl.disable()
                    inputs = in_s
                elif cond == "M":
                    ctrl.disable()          # 3장 전부 보이는 기준선
                    inputs = in_m
                else:
                    bf = 0 if cond == "T0" else int(cond[1:])
                    ctrl.configure_multi([(bf, sp[1]), (bf, sp[2])])  # 방해 2장 동시 차단
                    inputs = in_m
                try:
                    out = model(**inputs, use_cache=False)
                finally:
                    ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "group": row["group"],
                                   "gt": row["gt"], "condition": cond, **p,
                                   "correct": p["pred"] == row["gt"], "n_layers": n,
                                   "n_images": 1 if cond == "S" else 3,
                                   "seq_len": int(inputs["input_ids"].shape[1]),
                                   "elapsed_ms": int(1000 * (time.time() - t0)),
                                   "ts": iso_now()})
                executed += 1
        print(f"executed {executed}")

    res = read_jsonl(OUT)
    print(f"\n{'cond':>6} | {'leak군':>8} | {'ctrl군':>8} | {'전체':>7}")
    for c in CONDS:
        sub = [r for r in res if r["condition"] == c]
        if not sub:
            continue
        f = lambda g: (lambda v: sum(x["correct"] for x in v) / max(1, len(v)))(
            [x for x in sub if x["group"] == g])
        allv = sum(x["correct"] for x in sub) / len(sub)
        print(f"{c:>6} | {f('leak'):>8.3f} | {f('ctrl'):>8.3f} | {allv:>7.3f}")
    # 핵심 지표: 3장에서의 flip (S=no → M=yes)
    by = {}
    for r in res:
        by.setdefault(r["question_id"], {})[r["condition"]] = r
    for g in ("leak", "ctrl"):
        qs = [q for q, d in by.items() if "S" in d and "M" in d and d["M"]["group"] == g]
        if not qs:
            continue
        flip = sum(by[q]["S"]["pred"] == "no" and by[q]["M"]["pred"] == "yes" for q in qs) / len(qs)
        print(f"\n[{g}] 이미지 3장에서의 flip rate = {flip:.3f}  (n={len(qs)})")


if __name__ == "__main__":
    main()
