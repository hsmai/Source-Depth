"""미팅 최종 그림: (5) 동일 예산 배분 대결, (6) X자 교차 3B vs 7B."""
import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = str(Path(__file__).resolve().parents[1] / "results") + "/"


def load_alloc(tag=""):
    rows = [json.loads(l) for l in open(f"{R}alloc_results{tag}.jsonl") if l.strip()]
    acc = defaultdict(list)
    for r in rows:
        acc[r["condition"]].append(r["correct"])
    for r in csv.DictReader(open(f"{R}results{tag}.csv")):
        if r["condition"] in ("M", "T4", "T0"):
            acc[r["condition"]].append(r["correct"] == "True")
    n = rows[0]["n_layers"]
    rel = statistics.median([r["rel_tokens"] for r in rows])
    dis = statistics.median([r["dis_tokens"] for r in rows])
    seq = statistics.median([r["seq_len"] for r in rows])

    def save(c):
        if c.startswith("VTW"):
            k = int(c[3:]); return max(0, (rel + dis) * (n - k) / (seq * n))
        if c.startswith("J"):
            a, b = (int(x) for x in c[1:].split("x"))
            return max(0, (dis * (n - a) + rel * max(0, n - b)) / (seq * n))
        return 0.0
    A = {c: sum(v) / len(v) for c, v in acc.items()}
    return A, save, n


def fig5():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
    for ax, (tag, lbl) in zip(axes, (("", "Qwen2.5-VL-3B"), ("_7b", "Qwen2.5-VL-7B"))):
        A, save, n = load_alloc(tag)
        js = sorted([c for c in A if c.startswith("J")], key=save)
        vs = sorted([c for c in A if c.startswith("VTW")], key=save)
        ax.plot([save(c) * 100 for c in vs], [A[c] for c in vs], "s--", color="tab:red",
                lw=2.4, ms=10, label="Uniform: block BOTH images at the same layer\n(prior approach, e.g. VTW)")
        ax.plot([save(c) * 100 for c in js], [A[c] for c in js], "o-", color="tab:blue",
                lw=2.6, ms=10, label="Per-image: distractor early, relevant late\n(OURS)")
        ax.axhline(A["M"], color="gray", ls=":", lw=2)
        ax.annotate(f"no blocking  {A['M']:.3f}", (1, A["M"]), fontsize=10.5,
                    color="gray", va="bottom", weight="bold")
        # 동일 예산 대결 강조
        best = None
        for j in js:
            for v in vs:
                if abs(save(j) - save(v)) < 0.015 and save(j) > 0.2:
                    gap = A[j] - A[v]
                    if best is None or gap > best[0]:
                        best = (gap, j, v)
        if best:
            g, j, v = best
            x = save(j) * 100
            ax.annotate("", xy=(x, A[j]), xytext=(x, A[v]),
                        arrowprops=dict(arrowstyle="<->", color="black", lw=2.2))
            ax.annotate(f"SAME compute\n{g*100:+.1f}%p", (x + 1.5, (A[j] + A[v]) / 2),
                        fontsize=13, weight="bold", va="center")
        ax.set_title(f"{lbl}  ({n} layers)", fontsize=14, weight="bold")
        ax.set_xlabel("Compute saved on image tokens (%)", fontsize=12)
        ax.set_ylabel("Accuracy" if tag == "" else "", fontsize=12)
        ax.set_ylim(0.40, 0.92)
        ax.grid(alpha=0.25)
        ax.legend(loc="lower left", fontsize=9.5)
    fig.suptitle("Same compute budget, different allocation — allocation is what matters",
                 fontsize=15.5, weight="bold")
    fig.tight_layout()
    fig.savefig(R + "fig5_allocation_vs_uniform.png", dpi=155)
    plt.close(fig)
    print("fig5 done")


def fig6():
    Ls = [0, 4, 8, 12, 16, 20, 24]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    for ax, (tag, lbl, nl) in zip(axes, (("", "Qwen2.5-VL-3B", 36), ("_7b", "Qwen2.5-VL-7B", 28))):
        rows = [json.loads(l) for l in open(f"{R}rel_results{tag}.jsonl") if l.strip()]
        rel = defaultdict(list)
        for r in rows:
            if r["cell"] == "R1":
                rel[r["condition"]].append(r["correct"])
        RL = {c: sum(v) / len(v) for c, v in rel.items()}
        d1 = defaultdict(list)
        for r in csv.DictReader(open(f"{R}results{tag}.csv")):
            if int(r["cell"]) == 1:
                d1[r["condition"]].append(r["correct"] == "True")
        D1 = {c: sum(v) / len(v) for c, v in d1.items()}
        ax.plot(Ls, [D1[f"T{L}"] for L in Ls], "o-", color="tab:blue", lw=2.6, ms=9,
                label="Single-image question + distractor\n→ blocking is FREE (or helps)")
        ax.plot(Ls, [RL[f"T{L}"] for L in Ls], "s--", color="tab:red", lw=2.6, ms=9,
                label="Two-image comparison question\n→ blocking DESTROYS it")
        ax.axhline(D1["M"], color="tab:blue", ls=":", alpha=0.6)
        ax.axhline(RL["M"], color="tab:red", ls=":", alpha=0.6)
        lo, hi = (16, 24) if tag == "" else (12, 20)
        ax.axvspan(lo, hi, color="tab:orange", alpha=0.12)
        ax.annotate(f"transition\nL{lo}–{hi}\n({lo/nl:.0%}–{hi/nl:.0%} depth)",
                    ((lo + hi) / 2, 0.13), ha="center", fontsize=10, color="darkorange", weight="bold")
        ax.set_title(f"{lbl}  ({nl} layers)", fontsize=14, weight="bold")
        ax.set_xlabel("Blocking start layer", fontsize=12)
        ax.set_ylabel("Accuracy" if tag == "" else "", fontsize=12)
        ax.set_xticks(Ls); ax.set_ylim(0, 1.03); ax.grid(alpha=0.25)
        ax.legend(loc="center left", fontsize=9.5)
    fig.suptitle("Opposite optimal depth by question type — replicates at both scales",
                 fontsize=15.5, weight="bold")
    fig.tight_layout()
    fig.savefig(R + "fig6_xcross_both_scales.png", dpi=155)
    plt.close(fig)
    print("fig6 done")


if __name__ == "__main__":
    fig5(); fig6()
