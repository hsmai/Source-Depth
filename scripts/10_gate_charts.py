#!/usr/bin/env python
"""미팅용 gate 차트: fig3(반대 곡선 대조 — Gate 1 핵심), fig4(컨트롤러 feature 스윕 — Gate 2).

fig3이 이 연구의 승부처: 같은 모델·같은 개입(L 이후 img2 차단)인데
  - distractor 질문(unary): L이 얕을수록 **정확도 상승** (차단이 이득)
  - relational 질문(both):  L이 얕을수록 **정확도 붕괴** (혼합이 필수)
→ 단일 depth 정책으로는 양쪽을 동시에 만족할 수 없음 = per-image adaptive depth의 필요조건.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sourcedepth.config import IDENT_THRESH, RESULTS_DIR
from sourcedepth.runlog import read_jsonl

REL = RESULTS_DIR / "rel_results.jsonl"
SWEEP = RESULTS_DIR / "controller_feature_sweep.json"
L_ORDER = [0, 4, 8, 12, 16, 20, 24]


def acc_by_L(rows, cell=None):
    out = {}
    for L in L_ORDER:
        cond = f"T{L}"
        sub = [r for r in rows if r["condition"] == cond and (cell is None or r["cell"] == cell)]
        if sub:
            out[L] = sum(r["correct"] for r in sub) / len(sub)
    m = [r for r in rows if r["condition"] == "M" and (cell is None or r["cell"] == cell)]
    m_acc = sum(r["correct"] for r in m) / len(m) if m else None
    return out, m_acc


def fig3():
    rel = read_jsonl(REL)
    if not rel:
        print("fig3 skip: rel_results 없음")
        return None
    df = pd.read_csv(RESULTS_DIR / "results.csv")
    dis = df[df["cell"] == 1].to_dict("records")
    dis_acc, dis_m = acc_by_L(dis)
    # R1 = 질의 객체가 image1에만 존재, 질문 "in both images?", 정답 no.
    # 정답하려면 image2를 반드시 확인해야 하므로 relational 의존성의 clean probe.
    # (RB는 image1만 보고도 'yes'로 맞출 수 있어 교란됨 — 실측으로 확인)
    rb_acc, rb_m = acc_by_L(rel, cell="R1")

    fig, ax = plt.subplots(figsize=(8.5, 5))
    xs_d = sorted(dis_acc)
    ax.plot(xs_d, [dis_acc[x] for x in xs_d], "o-", color="tab:blue", lw=2.2, ms=7,
            label="Unary + distractor: blocking HELPS  (+21%p at L=4)")
    xs_r = sorted(rb_acc)
    ax.plot(xs_r, [rb_acc[x] for x in xs_r], "s--", color="tab:red", lw=2.2, ms=7,
            label="Relational 'in both?': blocking HURTS  (−51%p at L=4)")
    ax.axvspan(19, 25, color="tab:orange", alpha=0.12)
    ax.annotate("both effects switch on\nin the same band (L≈20–24)", (22, 0.45),
                ha="center", fontsize=8.5, color="darkorange")
    if dis_m is not None:
        ax.axhline(dis_m, color="tab:blue", ls=":", alpha=0.55, lw=1.3)
        ax.annotate(f"M (no blocking) {dis_m:.2f}", (24.4, dis_m), fontsize=8,
                    color="tab:blue", va="center")
    if rb_m is not None:
        ax.axhline(rb_m, color="tab:red", ls=":", alpha=0.55, lw=1.3)
        ax.annotate(f"M (no blocking) {rb_m:.2f}", (24.4, rb_m), fontsize=8,
                    color="tab:red", va="center")
    ax.set_xlabel("blocking depth L  (block distractor/second image at layers ≥ L; L=0 → fully blocked)")
    ax.set_ylabel("accuracy")
    ax.set_title("Same model, same intervention — opposite optimal depth per question type")
    ax.set_xticks(L_ORDER)
    ax.set_xlim(-1.5, 31)
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    ax.legend(loc="center left", fontsize=9)
    fig.tight_layout()
    p = RESULTS_DIR / "fig3_opposite_depth_policies.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    # 수치 요약
    summary = {"distractor_cell1": {f"T{k}": round(v, 4) for k, v in dis_acc.items()},
               "distractor_cell1_M": round(dis_m, 4) if dis_m else None,
               "relational_RB": {f"T{k}": round(v, 4) for k, v in rb_acc.items()},
               "relational_RB_M": round(rb_m, 4) if rb_m else None}
    for cell in ("R1", "R2"):
        a, m = acc_by_L(rel, cell=cell)
        summary[f"relational_{cell}"] = {f"T{k}": round(v, 4) for k, v in a.items()}
        summary[f"relational_{cell}_M"] = round(m, 4) if m else None
    (RESULTS_DIR / "gate1_summary.json").write_text(json.dumps(summary, indent=1))
    print("fig3 done:", json.dumps(summary, indent=1))
    return summary


def fig4():
    if not SWEEP.exists():
        print("fig4 skip: sweep 없음")
        return None
    s = json.loads(SWEEP.read_text())
    per = s["per_layer"]
    layers = sorted(int(k) for k in per)
    feats = ["mean_head", "best_head", "top3_heads", "max_minus_max", "cumulative_mean"]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    styles = {"mean_head": ("o-", "tab:gray"), "best_head": ("s-", "tab:green"),
              "top3_heads": ("^-", "tab:olive"), "max_minus_max": ("v-", "tab:cyan"),
              "cumulative_mean": ("d-", "tab:purple")}
    for f in feats:
        ys = [per[str(l)].get(f) for l in layers]
        if any(y is None for y in ys):
            continue
        st, c = styles[f]
        ax.plot(layers, ys, st, color=c, ms=4, lw=1.6,
                label=f + (" (Phase 0 baseline)" if f == "mean_head" else ""))
    ax.axhline(IDENT_THRESH, color="black", ls="--", lw=1.2, label=f"target {IDENT_THRESH:.0%}")
    ax.axvspan(0.5, 14.5, color="tab:green", alpha=0.07)
    ax.annotate("useful controller window\n(blocking here still recovers 80%+)",
                (7.5, 0.12), ha="center", fontsize=8, color="tab:green")
    ax.set_xlabel("layer (1-indexed) at which the controller decides")
    ax.set_ylabel("relevant-image identification rate\n(2-fold cross-fitted)")
    ax.set_title("Controller signal by layer and feature (n=600, exploratory)")
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, ncol=2, loc="lower right")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "fig4_controller_feature_sweep.png", dpi=150)
    plt.close(fig)
    print("fig4 done. top5 layer<=14:", s.get("top5_layer_le14"))
    return s


if __name__ == "__main__":
    fig3()
    fig4()
