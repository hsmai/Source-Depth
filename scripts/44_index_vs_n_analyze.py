#!/usr/bin/env python
"""43_index_vs_n 집계 — 사진 수 N별·조건별 AUC/정확도/예 비율, 문항 단위 paired bootstrap."""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from sourcedepth.config import RESULTS_DIR, SEED, TAG

B = 2000
CONDS = ["ORD", "LBL_ORD", "LBL_PIC", "CON", "LBL_CON"]


def auc(m, y):
    p, n = m[y == 1], m[y == 0]
    if len(p) == 0 or len(n) == 0: return float("nan")
    return float(((p[:, None] > n[None, :]).sum() + 0.5 * (p[:, None] == n[None, :]).sum()) / (len(p) * len(n)))


def main():
    rows = [json.loads(l) for l in open(RESULTS_DIR / f"idxn{TAG}.jsonl")]
    oom = sum(1 for r in rows if r.get("oom"))
    by = collections.defaultdict(dict)
    for r in rows:
        if not r.get("oom"): by[r["question_id"]][(r["n"], r["condition"])] = r
    qs = sorted(by)
    ns = sorted({n for q in qs for n, _ in by[q] if n > 1})
    rng = np.random.default_rng(SEED)
    out = [f"# 사진 수 N 대 지시 방식 (무개입){TAG or ' (3B)'}", "",
           f"문항 {len(qs)} · OOM {oom} · LM attention {rows[0].get('lm_attn')}", ""]

    def vec(n, c, sub=None):
        ks = [q for q in (sub or qs) if (n, c) in by[q]]
        return ks, np.array([by[q][(n, c)]["margin"] for q in ks]), np.array([by[q][(n, c)]["gt"] == "yes" for q in ks]).astype(int)

    _, m, y = vec(1, "S")
    out += [f"단독 입력(S): AUC {auc(m, y):.3f} · 정확도 {((m > 0).astype(int) == y).mean():.3f} · 예 비율 {(m > 0).mean():.3f}", ""]
    for metric in ("AUC", "정확도", "예 비율"):
        out += [f"## {metric}", "", "| 조건 | " + " | ".join(f"N={n}" for n in ns) + " |", "|---|" + "---|" * len(ns)]
        for c in CONDS:
            cells = []
            for n in ns:
                _, m, y = vec(n, c)
                v = auc(m, y) if metric == "AUC" else ((m > 0).astype(int) == y).mean() if metric == "정확도" else (m > 0).mean()
                cells.append(f"{v:.3f}")
            out.append(f"| {c} | " + " | ".join(cells) + " |")
        out.append("")

    def diff(n1, c1, n2, c2):
        ks = [q for q in qs if (n1, c1) in by[q] and (n2, c2) in by[q]]
        a = np.array([by[q][(n1, c1)]["margin"] for q in ks]); b = np.array([by[q][(n2, c2)]["margin"] for q in ks])
        y = np.array([by[q][(n1, c1)]["gt"] == "yes" for q in ks]).astype(int)
        res = []
        for f in (lambda m, yy: auc(m, yy), lambda m, yy: ((m > 0).astype(int) == yy).mean()):
            d = []
            for _ in range(B):
                s = rng.integers(0, len(ks), len(ks)); d.append(f(a[s], y[s]) - f(b[s], y[s]))
            lo, hi = np.nanpercentile(d, [2.5, 97.5])
            res.append(f"{f(a, y) - f(b, y):+.3f} [{lo:+.3f}, {hi:+.3f}]")
        return res

    out += ["## 문항 단위 차이 (95% CI)", "", "| 비교 | ΔAUC | Δ정확도 |", "|---|---|---|"]
    hi_n, lo_n = max(ns), min(ns)
    for c in CONDS:
        a, b = diff(hi_n, c, lo_n, c); out.append(f"| {c}: N={hi_n} − N={lo_n} | {a} | {b} |")
    for n in ns:
        a, b = diff(n, "LBL_ORD", n, "ORD"); out.append(f"| N={n}: LBL_ORD − ORD | {a} | {b} |")
    for n in ns:
        a, b = diff(n, "LBL_CON", n, "CON"); out.append(f"| N={n}: LBL_CON − CON | {a} | {b} |")
    out += ["", f"## 관련 사진 위치별 정확도 (N={hi_n})", "", "| 조건 | 앞 1/3 | 가운데 | 뒤 1/3 |", "|---|---|---|---|"]
    for c in CONDS:
        cells = []
        for lo, hi in ((0, hi_n / 3), (hi_n / 3, 2 * hi_n / 3), (2 * hi_n / 3, hi_n)):
            ks = [q for q in qs if (hi_n, c) in by[q] and lo <= by[q][(hi_n, c)]["rel_pos"] < hi]
            cells.append(f"{np.mean([by[q][(hi_n, c)]['correct'] for q in ks]):.3f} (n={len(ks)})" if ks else "—")
        out.append(f"| {c} | " + " | ".join(cells) + " |")
    text = "\n".join(out)
    (RESULTS_DIR / f"IDXN{TAG}.md").write_text(text)
    print(text)


if __name__ == "__main__": main()
