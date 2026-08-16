#!/usr/bin/env python
"""경로 분해 파일럿 판정 — docs/18_pathway_prereg.md 의 예측 P1·P2·P3 를 기계적으로 적용."""
import collections
import json
import random
import sys
from pathlib import Path

RES = Path(__file__).resolve().parents[1] / "results"
B = 2000
TOL = 0.02          # 사전 등록된 '차이 없음' 허용폭 (AUC)


def auc(pos, neg):
    allv = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    ranks, i = {}, 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    R = sum(ranks[k] for k, (v, l) in enumerate(allv) if l == 1)
    n1, n0 = len(pos), len(neg)
    if n1 == 0 or n0 == 0:
        return float("nan")
    return (R - n1 * (n1 + 1) / 2) / (n1 * n0)


def auc_of(items, cond):
    return auc([d[cond]["margin"] for d in items if d[cond]["gt"] == "yes"],
               [d[cond]["margin"] for d in items if d[cond]["gt"] == "no"])


def boot(items, a, b, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(B):
        s = [rnd.choice(items) for _ in items]
        out.append(auc_of(s, a) - auc_of(s, b))
    out.sort()
    return out[int(.025 * B)], out[int(.975 * B)]


def load(tag):
    f = RES / f"pathway{tag}.jsonl"
    if not f.exists():
        return None
    D = collections.defaultdict(dict)
    meta = {}
    for r in (json.loads(l) for l in open(f) if l.strip()):
        D[r["question_id"]][r["condition"]] = r
        meta[r["question_id"]] = (r["part"], str(r["cell"]))
    return D, meta


def main():
    for tag, label in (("", "3B"), ("_7b", "7B")):
        got = load(tag)
        if not got:
            print(f"\n### {label}: 파일 없음")
            continue
        D, meta = got
        print(f"\n{'='*74}\n{label}")

        # ── PART 1: 경로 분해 ─────────────────────────────
        need = ["M", "XIMG", "READ", "T0"]
        items = [d for q, d in D.items() if meta[q][0] == 1 and all(c in d for c in need)]
        if len(items) >= 50:
            A = {c: auc_of(items, c) for c in need}
            print(f"\n  PART1 경로 분해  n={len(items)}   (M=무개입 / XIMG=img2→img1 / "
                  f"READ=질문→img2 / T0=img2 전면)")
            print("     " + "  ".join(f"{c}={A[c]:.4f}" for c in need))
            lo1, hi1 = boot(items, "READ", "T0", 11)
            lo2, hi2 = boot(items, "XIMG", "M", 12)
            p1a = abs(A["READ"] - A["T0"]) < TOL
            p1b = abs(A["XIMG"] - A["M"]) < TOL
            print(f"     READ − T0 = {A['READ']-A['T0']:+.4f}  CI [{lo1:+.4f}, {hi1:+.4f}]"
                  f"   {'≈ 같음' if p1a else '다름'}")
            print(f"     XIMG − M  = {A['XIMG']-A['M']:+.4f}  CI [{lo2:+.4f}, {hi2:+.4f}]"
                  f"   {'≈ 같음' if p1b else '다름'}")
            print(f"     ── P1 (READ≈T0 & XIMG≈M, 즉 '읽기 오귀속' 가설) : "
                  f"{'★ 성립' if (p1a and p1b) else '✗ 불성립'}")
            recov = (A["T0"] - A["M"]) or 1e-9
            for c in ("XIMG", "READ"):
                print(f"       {c} 회복률 = {(A[c]-A['M'])/recov*100:5.0f}% (T0 대비)")
            for cell in ("1", "2"):
                sub = [d for q, d in D.items()
                       if meta[q] == (1, cell) and all(c in d for c in need)]
                if sub:
                    print(f"       셀{cell} 정확도: " +
                          " ".join(f"{c}={sum(x[c]['correct'] for x in sub)/len(sub):.3f}"
                                   for c in need))

        # ── PART 2: 고립 (need-all 질문) ───────────────────
        need2 = ["M3", "ISO0", "ISO16"]
        items2 = [d for q, d in D.items() if meta[q][0] == 2 and all(c in d for c in need2)]
        if len(items2) >= 50:
            A2 = {c: auc_of(items2, c) for c in need2}
            gt = collections.Counter(d["M3"]["gt"] for d in items2)
            print(f"\n  PART2 고립 (need-all 'any of these images')  n={len(items2)}  gt={dict(gt)}")
            print("     " + "  ".join(f"{c}={A2[c]:.4f}" for c in need2))
            lo, hi = boot(items2, "ISO0", "M3", 21)
            d = A2["ISO0"] - A2["M3"]
            print(f"     ISO0 − M3 = {d:+.4f}  CI [{lo:+.4f}, {hi:+.4f}]")
            verdict = ("★ 고립이 오히려 이득 — 앞단 selector로 불가능한 개입" if lo > 0 else
                       "★ P2 성립 (고립해도 손해 없음)" if d >= -TOL else
                       "✗ 고립이 손해 — 이미지 간 attention이 필요")
            print(f"     ── {verdict}")
            print("     정확도: " + "  ".join(
                f"{c}={sum(x[c]['correct'] for x in items2)/len(items2):.3f}" for c in need2))

        # ── PART 3: 관계형 경계 ───────────────────────────
        items3 = [(q, d) for q, d in D.items()
                  if meta[q][0] == 3 and all(c in d for c in ("M", "ISO0"))]
        if items3:
            print(f"\n  PART3 관계형 경계 ('both images')  n={len(items3)}")
            for cell in ("R1", "R2", "RB"):
                sub = [d for q, d in items3 if meta[q][1] == cell]
                if not sub:
                    continue
                m = sum(x["M"]["correct"] for x in sub) / len(sub)
                i0 = sum(x["ISO0"]["correct"] for x in sub) / len(sub)
                flag = "  ← 이미지 간 attention 필요" if i0 - m < -0.05 else ""
                print(f"     {cell}: M={m:.3f}  ISO0={i0:.3f}  Δ={100*(i0-m):+5.1f}%p{flag}")


if __name__ == "__main__":
    main()
