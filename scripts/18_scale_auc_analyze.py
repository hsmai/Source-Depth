#!/usr/bin/env python
"""scale-AUC 판정 — docs/16_scale_auc_prereg.md 의 사전 등록 기준을 그대로 적용."""
import collections
import json
import random
import sys
from pathlib import Path

RES = Path(__file__).resolve().parents[1] / "results"
NS = [1, 2, 3]
B = 2000

# 사전 등록된 임계값
PASS, PARTIAL = -0.020, -0.010


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
    return (R - n1 * (n1 + 1) / 2) / (n1 * n0)


def auc_of(items, key):
    return auc([d[key]["margin"] for d in items if d[key]["gt"] == "yes"],
               [d[key]["margin"] for d in items if d[key]["gt"] == "no"])


def boot_diff(items, key_a, key_b, seed):
    """대응 부트스트랩: AUC(a) − AUC(b)"""
    rnd = random.Random(seed)
    out = []
    for _ in range(B):
        s = [rnd.choice(items) for _ in items]
        out.append(auc_of(s, key_a) - auc_of(s, key_b))
    out.sort()
    return out[int(.025 * B)], out[int(.975 * B)]


def main():
    for tag, label in (("_7b", "7B  (주 종점)"), ("", "3B  (부 종점)")):
        f = RES / f"scale_auc{tag}.jsonl"
        if not f.exists():
            print(f"\n### {label}: 파일 없음 — 건너뜀")
            continue
        rows = [json.loads(l) for l in open(f) if l.strip()]
        D = collections.defaultdict(dict)
        for r in rows:
            D[r["question_id"]][(r["condition"], r["n_dist"])] = r
        need = [("S", 0)] + [(c, n) for n in NS for c in ("M", "T0", "T4")]
        items = [d for d in D.values() if all(k in d for k in need)]
        print(f"\n{'='*68}\n{label}   완결 문항 n={len(items)}  (전체 {len(D)})")
        if len(items) < 100:
            print("  문항 부족 — 판정 보류")
            continue
        gt = collections.Counter(d[("S", 0)]["gt"] for d in items)
        print(f"  gt 균형: {dict(gt)}")

        A = {k: auc_of(items, k) for k in need}
        print(f"\n  {'N':>2} {'M(무개입)':>11} {'T0(차단)':>11} {'T4':>9} {'ΔAUC(T0−M)':>13} {'회복률':>8}")
        base = A[("S", 0)]
        print(f"  {'0':>2} {base:11.4f}   ← S(1장 단독, 상한)")
        for n in NS:
            m, t0, t4 = A[("M", n)], A[("T0", n)], A[("T4", n)]
            dmg = base - m
            rec = (t0 - m) / dmg * 100 if dmg > 1e-9 else float("nan")
            print(f"  {n:>2} {m:11.4f} {t0:11.4f} {t4:9.4f} {t0-m:+13.4f} {rec:7.0f}%")

        # ── 주 종점 ──────────────────────────────────────
        d = A[("M", 3)] - A[("M", 1)]
        lo, hi = boot_diff(items, ("M", 3), ("M", 1), 101)
        excl = (hi < 0) or (lo > 0)
        verdict = ("통과" if (d <= PASS and excl) else
                   "부분 통과" if (d <= PARTIAL and excl) else "실패")
        print(f"\n  ── 주 종점: AUC(M,N=3) − AUC(M,N=1) ──")
        print(f"     {d:+.4f}   95%CI [{lo:+.4f}, {hi:+.4f}]   "
              f"{'0 배제' if excl else '0 포함'}")
        print(f"     ★ {verdict} ★   (통과 ≤{PASS} & CI 0배제 / 부분 ≤{PARTIAL} & CI 0배제)")

        # ── 부 종점: 각 N에서 회복이 유의한가 ────────────
        print(f"\n  ── 부 종점: ΔAUC(T0 − M) 가 각 N에서 유의한 양수인가 ──")
        for n in NS:
            lo2, hi2 = boot_diff(items, ("T0", n), ("M", n), 200 + n)
            print(f"     N={n}: {A[('T0',n)]-A[('M',n)]:+.4f}  95%CI [{lo2:+.4f}, {hi2:+.4f}]"
                  + ("   ★ 유의" if lo2 > 0 else ""))

        # 참고: 고정 임계값 정확도 (판정 근거 아님)
        print(f"\n  [참고, 판정 근거 아님] 고정 임계값 정확도")
        acc = lambda k: sum(d[k]["correct"] for d in items) / len(items)
        print(f"     S={acc(('S',0)):.4f}  " +
              "  ".join(f"M{n}={acc(('M',n)):.4f}/T0{n}={acc(('T0',n)):.4f}" for n in NS))


if __name__ == "__main__":
    main()
