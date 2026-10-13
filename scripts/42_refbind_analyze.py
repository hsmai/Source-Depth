#!/usr/bin/env python
"""41_reference_binding 결과 집계 — 지시 방식 × 차단 조건별 ΔAUC (문항 단위 paired bootstrap)."""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from sourcedepth.config import RESULTS_DIR, SEED, TAG

B = 2000


def auc(m, y):
    p, n = m[y == 1], m[y == 0]
    if len(p) == 0 or len(n) == 0: return float("nan")
    return float(((p[:, None] > n[None, :]).sum() + 0.5 * (p[:, None] == n[None, :]).sum()) / (len(p) * len(n)))


def main():
    rows = [json.loads(l) for l in open(RESULTS_DIR / f"refbind{TAG}.jsonl")]
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["part"], r["k"], r["question_id"])][r["condition"]] = r
    rng = np.random.default_rng(SEED)
    out = [f"# 참조 결속 프로브 결과{TAG or ' (3B)'}", ""]
    groups = sorted({(p, k) for p, k, _ in by if p != "S"})
    for part, k in groups:
        items = [v for (p, kk, _), v in by.items() if p == part and kk == k and "M" in v]
        conds = [c for c in dict.fromkeys(c for v in items for c in v) if c not in ("M",)]
        y = np.array([1 if v["M"]["gt"] == "yes" else 0 for v in items])
        out += [f"## {part} · 사진 {k}장 (n={len(items)})", "",
                "| 조건 | AUC | 기준 대비 ΔAUC [95% CI] | 정확도 | 예 비율 |", "|---|---|---|---|---|"]
        def col(c, base="M"):
            ok = [i for i, v in enumerate(items) if c in v and base in v]
            m = np.array([items[i][c]["margin"] for i in ok]); b = np.array([items[i][base]["margin"] for i in ok])
            yy = y[ok]
            d = []
            for _ in range(B):
                s = rng.integers(0, len(ok), len(ok))
                d.append(auc(m[s], yy[s]) - auc(b[s], yy[s]))
            lo, hi = np.nanpercentile(d, [2.5, 97.5])
            return (f"| {c} | {auc(m, yy):.3f} | {auc(m, yy) - auc(b, yy):+.3f} [{lo:+.3f}, {hi:+.3f}] (vs {base}) | "
                    f"{((m > 0).astype(int) == yy).mean():.3f} | {(m > 0).mean():.3f} |")
        m0 = np.array([v["M"]["margin"] for v in items])
        out.append(f"| M | {auc(m0, y):.3f} | — | {((m0 > 0).astype(int) == y).mean():.3f} | {(m0 > 0).mean():.3f} |")
        for c in conds:
            out.append(col(c, "LBL_M" if c == "LBL_X_ALL" else "M"))
        out.append("")
    # 어느 사진을 읽는가: margin(조건) ~ a·S_REL + b·S_DIST + c  (PART A)
    S = {q: v for (p, _, q), v in by.items() if p == "S"}
    out += ["## 어느 사진의 답을 따르는가 (PART A, 최소제곱: margin = a·단독(관련) + b·단독(방해) + c)", "",
            "| 배치 | 조건 | a (관련) | b (방해) | a/(|a|+|b|) |", "|---|---|---|---|---|"]
    for part in ("A_orig", "A_swap"):
        its = {q: v for (p, _, q), v in by.items() if p == part}
        qs = [q for q in its if q in S and "S_REL" in S[q] and "S_DIST" in S[q]]
        if not qs: continue
        X = np.array([[S[q]["S_REL"]["margin"], S[q]["S_DIST"]["margin"], 1.0] for q in qs])
        for c in ["M", "X_ALL", "X_COLD", "X_COLP", "X_ROWD", "X_ROWP", "LBL_M", "LBL_X_ALL"]:
            ok = [i for i, q in enumerate(qs) if c in its[q]]
            if not ok: continue
            t = np.array([its[qs[i]][c]["margin"] for i in ok])
            a, b, _ = np.linalg.lstsq(X[ok], t, rcond=None)[0]
            out.append(f"| {part} | {c} | {a:+.3f} | {b:+.3f} | {a / (abs(a) + abs(b) + 1e-9):+.2f} |")
    text = "\n".join(out)
    (RESULTS_DIR / f"REFBIND{TAG}.md").write_text(text)
    print(text)


if __name__ == "__main__": main()
