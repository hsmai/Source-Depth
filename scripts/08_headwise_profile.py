#!/usr/bin/env python
"""Gate 2 선행: per-head attention 질량으로 layer ≤14 식별률 80%+ feature 탐색 (탐색적).

600 원본 M-layout 문항에서 layer×head별 (m1, m2)를 저장한 뒤, 2-fold cross-fit으로
feature별·layer별 관련 이미지 top-1 식별률을 평가한다 (과적합 방지: calibration 절반에서
head 선택, 나머지 절반에서 평가 — fold 교차 평균).
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import argparse

import numpy as np
import pandas as pd
import torch

from sourcedepth.config import (COCO_IMG_DIR, PAIRS_CSV, PROMPT_MULTI_SECOND,
                                RESULTS_DIR, SEED)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase, questions_for
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.runlog import append_jsonl, blocked, dump_env, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / "headwise_profile.jsonl"
OUT_SWAP = RESULTS_DIR / "headwise_profile_swapped.jsonl"
SWEEP_OUT = RESULTS_DIR / "controller_feature_sweep.json"
SWEEP_SWAP = RESULTS_DIR / "controller_swap_check.json"
MAX_LAYER_1IDX = 24   # 저장 상한 (관심 구간 1..24)


def profile(model, processor, rows, vs, ve, pad, n_layers, swap=False):
    """swap=True: [distractor, relevant] 순서 + 'second image' 질문. 저장은 항상
    [관련, distractor] 의미 순서 → 같은 head가 '질문이 가리키는 이미지'를 따라가는지 판별."""
    out_path = OUT_SWAP if swap else OUT
    done = {r["question_id"] for r in read_jsonl(out_path)}
    todo = [r for r in rows if r["question_id"] not in done]
    print(f"headwise profiling (swap={swap}): {len(todo)}/{len(rows)} to run")
    for k, row in enumerate(todo):
        im1 = image_path(int(row["image1_id"]), COCO_IMG_DIR)
        im2 = image_path(int(row["image2_id"]), COCO_IMG_DIR)
        if swap:
            q = PROMPT_MULTI_SECOND.format(obj=obj_phrase(row["article"], row["object"]))
            inp = build_inputs(processor, [im2, im1], q, DEV)
            spans = find_vision_spans(inp["input_ids"], vs, ve, pad)
            (s1, e1), (s2, e2) = spans[1], spans[0]     # 관련=두 번째 위치
        else:
            q_multi, _ = questions_for(row)
            inp = build_inputs(processor, [im1, im2], q_multi, DEV)
            (s1, e1), (s2, e2) = find_vision_spans(inp["input_ids"], vs, ve, pad)
        with torch.no_grad():
            out = model(**inp, use_cache=False, output_attentions=True)
        per_layer = []
        for li in range(min(MAX_LAYER_1IDX, n_layers)):
            w = out.attentions[li][0, :, -1, :].float()          # (heads, kv)
            m1 = w[:, s1:e1 + 1].sum(-1)                          # (heads,)
            m2 = w[:, s2:e2 + 1].sum(-1)
            per_layer.append([m1.tolist(), m2.tolist()])
        append_jsonl(out_path, {"question_id": row["question_id"], "cell": int(row["cell"]),
                                "swapped": swap, "heads": per_layer})
        if (k + 1) % 100 == 0:
            print(f"  {k + 1}/{len(todo)}")


def sweep():
    rows = read_jsonl(OUT)
    n = len(rows)
    L = len(rows[0]["heads"])
    H = len(rows[0]["heads"][0][0])
    m1 = np.array([[r["heads"][l][0] for l in range(L)] for r in rows])   # (n, L, H)
    m2 = np.array([[r["heads"][l][1] for l in range(L)] for r in rows])
    diff = m1 - m2
    rng = random.Random(SEED)
    order = list(range(n))
    rng.shuffle(order)
    folds = [order[: n // 2], order[n // 2:]]

    def xfit(score_fn_fit, score_fn_eval):
        accs = []
        for f in (0, 1):
            cal, test = folds[f], folds[1 - f]
            param = score_fn_fit(np.array(cal))
            accs.append(score_fn_eval(np.array(test), param))
        return float(np.mean(accs))

    results = {}
    for l in range(L):
        d = diff[:, l, :]                                   # (n, H)
        feats = {
            "mean_head": lambda test, _p, d=d: (d[test].mean(1) > 0).mean(),
            "best_head": (lambda cal, d=d: int(np.argmax((d[cal] > 0).mean(0))),
                          lambda test, h, d=d: (d[test, h] > 0).mean()),
            "top3_heads": (lambda cal, d=d: np.argsort(-(d[cal] > 0).mean(0))[:3],
                           lambda test, hs, d=d: (d[np.ix_(test, hs)].mean(1) > 0).mean()),
            "max_minus_max": lambda test, _p, l=l: (m1[test, l].max(1) - m2[test, l].max(1) > 0).mean(),
        }
        cum = diff[:, : l + 1, :].mean(axis=(1, 2))
        feats["cumulative_mean"] = lambda test, _p, cum=cum: (cum[test] > 0).mean()
        layer_res = {}
        for name, f in feats.items():
            if isinstance(f, tuple):
                layer_res[name] = xfit(f[0], f[1])
            else:
                layer_res[name] = xfit(lambda cal: None, f)
        results[l + 1] = {k: round(v, 4) for k, v in layer_res.items()}

    best = []
    for l, fr in results.items():
        for fname, acc in fr.items():
            best.append((acc, l, fname))
    best.sort(reverse=True)
    best14 = [b for b in best if b[1] <= 14]
    summary = {
        "n": n, "layers_stored": L, "heads": H,
        "per_layer": results,
        "top5_overall": [{"acc": a, "layer": l, "feature": f} for a, l, f in best[:5]],
        "top5_layer_le14": [{"acc": a, "layer": l, "feature": f} for a, l, f in best14[:5]],
    }
    SWEEP_OUT.write_text(json.dumps(summary, indent=1))
    print("=== controller feature sweep (2-fold cross-fitted) ===")
    print("top5 overall:", summary["top5_overall"])
    print("top5 layer<=14:", summary["top5_layer_le14"])


def swap_check():
    """같은 head가 순서를 뒤집어도 '질문이 가리키는 이미지'를 따라가는가 (position bias 판별)."""
    a, b = read_jsonl(OUT), read_jsonl(OUT_SWAP)
    if not a or not b:
        print("swap_check skip: 데이터 부족"); return
    common = sorted(set(r["question_id"] for r in a) & set(r["question_id"] for r in b))
    ia = {r["question_id"]: r for r in a}
    ib = {r["question_id"]: r for r in b}
    L = len(a[0]["heads"]); H = len(a[0]["heads"][0][0])
    da = np.array([[np.array(ia[q]["heads"][l][0]) - np.array(ia[q]["heads"][l][1])
                    for l in range(L)] for q in common])
    db = np.array([[np.array(ib[q]["heads"][l][0]) - np.array(ib[q]["heads"][l][1])
                    for l in range(L)] for q in common])
    out = {}
    for l in range(L):
        h = int(np.argmax((da[:, l, :] > 0).mean(0)))     # 원본에서 고른 head
        out[l + 1] = {"head": h,
                      "acc_original": round(float((da[:, l, h] > 0).mean()), 4),
                      "acc_swapped": round(float((db[:, l, h] > 0).mean()), 4),
                      "best_head_swapped_acc": round(float((db[:, l, :] > 0).mean(0).max()), 4)}
    SWEEP_SWAP.write_text(json.dumps({"n": len(common), "per_layer": out}, indent=1))
    print("=== position-bias 판별 (원본에서 고른 head를 순서 뒤집기에 그대로 적용) ===")
    for l in sorted(out):
        o = out[l]
        if l in (2, 5, 8, 11, 12, 14, 21):
            print(f"  layer {l:>2} h{o['head']:>2}: 원본 {o['acc_original']:.3f} → "
                  f"뒤집기 {o['acc_swapped']:.3f} (뒤집기 최적head {o['best_head_swapped_acc']:.3f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--swap", action="store_true")
    ap.add_argument("--sweep-only", action="store_true")
    args = ap.parse_args()

    dump_env("08_headwise")
    rows = pd.read_csv(PAIRS_CSV).to_dict("records")
    if not args.sweep_only:
        if not torch.cuda.is_available():
            blocked("08_headwise", "GPU 없음", {})
        torch.manual_seed(SEED)
        with stage("08_headwise_profile"):
            model, processor = load_model_and_processor()
            n_layers = num_layers(model)
            resolve_decoder_layers(model)
            vs, ve, pad = vision_token_ids(processor)
            profile(model, processor, rows, vs, ve, pad, n_layers, swap=args.swap)
    with stage("08_feature_sweep"):
        if not args.swap:
            sweep()
        swap_check()


if __name__ == "__main__":
    main()
