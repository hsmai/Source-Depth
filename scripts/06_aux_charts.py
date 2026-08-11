#!/usr/bin/env python
"""미팅용 보조 차트 (docs/08 키트의 보조차트 A·B·C) — 존재하는 데이터만 렌더."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sourcedepth.config import (ATTN_PROFILE, ATTN_PROFILE_SWAPPED,
                                IDENT_THRESH, RESULTS_DIR, TAG)
from sourcedepth.runlog import read_jsonl


def ident_rates(rows):
    arr = np.array([r["masses"] for r in rows])       # (n, layers, 3) [relevant, distractor, text]
    return (arr[:, :, 0] > arr[:, :, 1]).mean(axis=0)


def chart_a(rows):
    r = ident_rates(rows)
    n = len(r)
    xs = np.arange(1, n + 1)
    colors = ["tab:red" if x in (4, 8) else ("tab:green" if r[x - 1] == r.max() else "tab:blue")
              for x in xs]
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(xs, r, color=colors)
    ax.axhline(IDENT_THRESH, color="black", ls="--", lw=1,
               label=f"pre-registered threshold {IDENT_THRESH:.0%} (layer 8)")
    for x in (4, 8):
        ax.annotate(f"L{x}: {r[x-1]:.1%}", (x, r[x - 1]), textcoords="offset points",
                    xytext=(0, 6), ha="center", fontsize=8, color="tab:red")
    b = int(r.argmax()) + 1
    ax.annotate(f"L{b}: {r[b-1]:.1%}", (b, r[b - 1]), textcoords="offset points",
                xytext=(0, 6), ha="center", fontsize=8, color="tab:green")
    ax.set_xlabel("layer (1-indexed)")
    ax.set_ylabel("top-1 identification rate (img1 = relevant)")
    ax.set_title("Per-layer attention identification of the relevant image (n=600, exploratory)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f"aux_chartA_ident_by_layer{TAG}.png", dpi=150)
    plt.close(fig)
    print("chartA done; layer4/8/best:",
          {4: round(float(r[3]), 3), 8: round(float(r[7]), 3), b: round(float(r[b - 1]), 3)})


def chart_b(rows, rows_sw):
    ra, rb = ident_rates(rows), ident_rates(rows_sw)
    xs = np.arange(1, len(ra) + 1)
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(xs, ra, "o-", ms=3, label="original order (relevant first)")
    ax.plot(xs, rb, "s-", ms=3, label="swapped order (relevant second)")
    ax.axhline(IDENT_THRESH, color="black", ls="--", lw=1)
    ax.set_xlabel("layer (1-indexed)")
    ax.set_ylabel("top-1 identification rate (relevant image)")
    ax.set_title("Position-bias control: identification with image order swapped (exploratory)")
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f"aux_chartB_swap_control{TAG}.png", dpi=150)
    plt.close(fig)
    top = [(int(i) + 1, round(float(ra[i]), 3), round(float(rb[i]), 3))
           for i in np.argsort(-ra)[:5]]
    print("chartB done; (layer, orig, swapped) top5 by orig:", top)


def chart_c():
    df = pd.read_csv(RESULTS_DIR / f"results{TAG}.csv")
    cells = [1, 2, 3, 4]
    acc = {c: {cell: df[(df["condition"] == c) & (df["cell"] == cell)]["correct"].mean()
               for cell in cells} for c in ("M", "Trel8")}
    x = np.arange(len(cells))
    w = 0.35
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x - w / 2, [acc["M"][c] for c in cells], w, label="M (both images visible)")
    ax.bar(x + w / 2, [acc["Trel8"][c] for c in cells], w, color="tab:purple",
           label="T-rel(8): relevant image blocked")
    for i, c in enumerate(cells):
        ax.annotate(f"{acc['Trel8'][c]:.2f}", (i + w / 2, acc["Trel8"][c]),
                    textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8)
    ax.set_xticks(x, [f"cell {c}" for c in cells])
    ax.set_ylabel("accuracy")
    ax.set_title("Negative control: predictions follow whichever image is visible")
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f"aux_chartC_negative_control{TAG}.png", dpi=150)
    plt.close(fig)
    print("chartC done:", {k: {c: round(float(v[c]), 3) for c in cells} for k, v in acc.items()})


def main():
    rows = [r for r in read_jsonl(ATTN_PROFILE)]
    if rows:
        chart_a(rows)
    rows_sw = [r for r in read_jsonl(ATTN_PROFILE_SWAPPED)]
    if rows and rows_sw:
        chart_b(rows, rows_sw)
    if (RESULTS_DIR / f"results{TAG}.csv").exists():
        chart_c()


if __name__ == "__main__":
    main()
