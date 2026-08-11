#!/usr/bin/env python
"""A4: 보증 있는 계산 배분 — risk-calibrated α-knob의 Pareto 곡선 (GPU 불필요, post-hoc).

정책: 결정 layer ℓ에서 컨트롤러 점수 s = (relevant mass − distractor mass).
  s >  τ  → image2가 무관하다고 판단 → image2를 layer ℓ 이후 차단   (결과 = 측정된 T{ℓ} 정오)
  s < −τ  → image1이 무관하다고 판단 → image1을 차단 (오판이면 손해)  (결과 = 측정된 Rel{ℓ}/Trel{ℓ} 정오)
  |s| ≤ τ → 확신 부족 → 차단하지 않음 (안전)                          (결과 = 측정된 M 정오)

τ를 키우면 안전하지만 절감이 줄고, 낮추면 절감이 크지만 위험. 전부 **실측된 per-item 정오**로
시뮬레이션하므로 추정치가 아니다. 휴리스틱 threshold를 쓰는 기존 pruning과 달리
"오류율을 정해두고 계산을 최소화"하는 knob을 제시하는 것이 본 연구의 차별점(제안서 기여 4).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from sourcedepth.config import RESULTS_DIR
from sourcedepth.runlog import read_jsonl

HEADWISE = RESULTS_DIR / "headwise_profile.jsonl"
SWEEP = RESULTS_DIR / "controller_feature_sweep.json"
ALLOC = RESULTS_DIR / "alloc_results.jsonl"
OUT = RESULTS_DIR / "alpha_knob.json"


def scores_at(layer_1idx, feature, sweep):
    """headwise_profile에서 결정 layer의 per-item 점수 s = m1 - m2 (feature별)."""
    rows = read_jsonl(HEADWISE)
    out = {}
    li = layer_1idx - 1
    best_head = None
    if feature == "best_head":
        # sweep에서 고른 head를 쓰지 않고, 여기서는 전체 데이터 기준 최적 head를 사용한다
        # (Pareto 곡선은 상한 성격 — REPORT에 그대로 명시)
        d = np.array([np.array(r["heads"][li][0]) - np.array(r["heads"][li][1]) for r in rows])
        best_head = int(np.argmax((d > 0).mean(0)))
    for r in rows:
        m1 = np.array(r["heads"][li][0])
        m2 = np.array(r["heads"][li][1])
        if feature == "mean_head":
            s = float((m1 - m2).mean())
        elif feature == "best_head":
            s = float(m1[best_head] - m2[best_head])
        elif feature == "max_minus_max":
            s = float(m1.max() - m2.max())
        else:
            s = float((m1 - m2).mean())
        out[r["question_id"]] = s
    return out, best_head


def main():
    if not HEADWISE.exists():
        print("headwise_profile 없음 — 08 미실행"); return
    base = pd.read_csv(RESULTS_DIR / "results.csv")
    base["question_id"] = base["question_id"].astype(str)
    alloc = pd.DataFrame(read_jsonl(ALLOC)) if ALLOC.exists() else pd.DataFrame()
    if len(alloc):
        alloc["question_id"] = alloc["question_id"].astype(str)

    def outcome_map(cond):
        d = base[base["condition"] == cond]
        if len(d) == 0 and len(alloc):
            d = alloc[alloc["condition"] == cond]
        return dict(zip(d["question_id"].astype(str), d["correct"].astype(bool))) if len(d) else None

    m_out = outcome_map("M")
    tokens = base[base["condition"] == "M"].drop_duplicates("question_id")
    n_layers = int(json.loads((RESULTS_DIR / "SMOKE_PASSED").read_text())["num_hidden_layers"])
    dis_tok = tokens["img2_span"].apply(lambda s: eval(s)[1] - eval(s)[0] + 1).median()
    rel_tok = tokens["img1_span"].apply(lambda s: eval(s)[1] - eval(s)[0] + 1).median()
    seq = tokens["seq_len"].median()

    sweep = json.loads(SWEEP.read_text()) if SWEEP.exists() else {}
    # (결정 layer, 차단 L) 쌍 — 측정 데이터가 있는 조합만
    pairs = [(8, "T8", "Trel8")]
    for L in (12, 16, 20, 24):
        if outcome_map(f"T{L}") and outcome_map(f"Rel{L}"):
            pairs.append((L, f"T{L}", f"Rel{L}"))

    results = {}
    for feature in ("mean_head", "best_head", "max_minus_max"):
        for ell, cond_block2, cond_block1 in pairs:
            s_map, bh = scores_at(ell, feature, sweep)
            o2, o1 = outcome_map(cond_block2), outcome_map(cond_block1)
            if not (o2 and o1 and m_map_ok(s_map, m_out)):
                continue
            qids = [q for q in s_map if q in o2 and q in o1 and q in m_out]
            s = np.array([s_map[q] for q in qids])
            curve = []
            for tau in np.quantile(np.abs(s), np.linspace(0, 1, 21)):
                acc, saved = [], []
                for i, q in enumerate(qids):
                    if s[i] > tau:
                        acc.append(o2[q]); saved.append(dis_tok * (n_layers - ell))
                    elif s[i] < -tau:
                        acc.append(o1[q]); saved.append(rel_tok * (n_layers - ell))
                    else:
                        acc.append(m_out[q]); saved.append(0.0)
                curve.append({"tau": round(float(tau), 5),
                              "accuracy": round(float(np.mean(acc)), 4),
                              "flops_saved": round(float(np.mean(saved) / (seq * n_layers)), 4),
                              "blocked_frac": round(float(np.mean(np.abs(s) > tau)), 4)})
            key = f"{feature}@L{ell}"
            results[key] = {"curve": curve, "best_head": bh,
                            "baseline_M_acc": round(float(np.mean([m_out[q] for q in qids])), 4)}

    if not results:
        print("사용 가능한 (결정 layer, 차단 L) 조합 없음"); return
    # 요약: M 정확도를 유지(≥ M − 0.5%p)하면서 최대 절감을 주는 점
    summary = {}
    for k, v in results.items():
        base_acc = v["baseline_M_acc"]
        ok = [p for p in v["curve"] if p["accuracy"] >= base_acc - 0.005]
        best = max(ok, key=lambda p: p["flops_saved"]) if ok else None
        top = max(v["curve"], key=lambda p: p["accuracy"])
        summary[k] = {"M_acc": base_acc, "no_loss_point": best, "max_acc_point": top}
    OUT.write_text(json.dumps({"summary": summary, "curves": results}, indent=1))
    print("=== α-knob Pareto (실측 per-item 정오 기반 시뮬레이션) ===")
    print(json.dumps(summary, indent=1))


def m_map_ok(s_map, m_out):
    return bool(m_out) and len(set(s_map) & set(m_out)) > 0


if __name__ == "__main__":
    main()
