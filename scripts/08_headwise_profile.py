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

import numpy as np
import pandas as pd
import torch

from sourcedepth.config import (COCO_IMG_DIR, PAIRS_CSV, RESULTS_DIR, SEED)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.runlog import append_jsonl, blocked, dump_env, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / "headwise_profile.jsonl"
SWEEP_OUT = RESULTS_DIR / "controller_feature_sweep.json"
MAX_LAYER_1IDX = 24   # 저장 상한 (관심 구간 1..24)


def profile(model, processor, rows, vs, ve, pad, n_layers):
    done = {r["question_id"] for r in read_jsonl(OUT)}
    todo = [r for r in rows if r["question_id"] not in done]
    print(f"headwise profiling: {len(todo)}/{len(rows)} to run")
    for k, row in enumerate(todo):
        q_multi, _ = questions_for(row)
        inp = build_inputs(processor, [image_path(int(row["image1_id"]), COCO_IMG_DIR),
                                       image_path(int(row["image2_id"]), COCO_IMG_DIR)],
                           q_multi, DEV)
        (s1, e1), (s2, e2) = find_vision_spans(inp["input_ids"], vs, ve, pad)
        with torch.no_grad():
            out = model(**inp, use_cache=False, output_attentions=True)
        per_layer = []
        for li in range(min(MAX_LAYER_1IDX, n_layers)):
            w = out.attentions[li][0, :, -1, :].float()          # (heads, kv)
            m1 = w[:, s1:e1 + 1].sum(-1)                          # (heads,)
            m2 = w[:, s2:e2 + 1].sum(-1)
            per_layer.append([m1.tolist(), m2.tolist()])
        append_jsonl(OUT, {"question_id": row["question_id"], "cell": int(row["cell"]),
                           "heads": per_layer})
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


def main():
    dump_env("08_headwise")
    if not torch.cuda.is_available():
        blocked("08_headwise", "GPU 없음", {})
    torch.manual_seed(SEED)
    rows = pd.read_csv(PAIRS_CSV).to_dict("records")
    with stage("08_headwise_profile"):
        model, processor = load_model_and_processor()
        n_layers = num_layers(model)
        resolve_decoder_layers(model)
        vs, ve, pad = vision_token_ids(processor)
        profile(model, processor, rows, vs, ve, pad, n_layers)
    with stage("08_feature_sweep"):
        sweep()


if __name__ == "__main__":
    main()
