#!/usr/bin/env python
"""HARD need-all(all-of-3) + 소프트 λ 스윕 판정."""
import collections
import json
import random
from pathlib import Path

RES = Path(__file__).resolve().parents[1] / "results"
B = 2000


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
    return float("nan") if not n1 or not n0 else (R - n1 * (n1 + 1) / 2) / (n1 * n0)


def A(items, c):
    return auc([d[c]["margin"] for d in items if d[c]["gt"] == "yes"],
               [d[c]["margin"] for d in items if d[c]["gt"] == "no"])


def boot(items, a, b, seed):
    rnd = random.Random(seed)
    o = []
    for _ in range(B):
        s = [rnd.choice(items) for _ in items]
        o.append(A(s, a) - A(s, b))
    o.sort()
    return o[int(.025 * B)], o[int(.975 * B)]


def main():
    for tag, label in (("", "3B"), ("_7b", "7B")):
        f = RES / f"hardsoft{tag}.jsonl"
        if not f.exists():
            print(f"\n### {label}: 파일 없음")
            continue
        D = collections.defaultdict(dict)
        part = {}
        for r in (json.loads(l) for l in open(f) if l.strip()):
            D[r["question_id"]][r["condition"]] = r
            part[r["question_id"]] = r["part"]
        print(f"\n{'='*70}\n{label}")

        # ── A. HARD need-all (all-of-3) ────────────────
        need = ["M3", "ISO0", "ISO16"]
        it = [d for q, d in D.items() if part[q] == "A" and all(c in d for c in need)]
        if len(it) >= 50:
            gt = collections.Counter(d["M3"]["gt"] for d in it)
            print(f"\n  A. HARD need-all  \"Do ALL of these images contain X?\"  n={len(it)}  gt={dict(gt)}")
            for c in need:
                acc = sum(d[c]["correct"] for d in it) / len(it)
                print(f"     {c:6} AUC={A(it, c):.4f}  정확도={acc:.4f}")
            lo, hi = boot(it, "ISO0", "M3", 31)
            d = A(it, "ISO0") - A(it, "M3")
            print(f"     ISO0 − M3 = {d:+.4f}  95%CI [{lo:+.4f}, {hi:+.4f}]")
            print("     ── " + ("★ 고립이 이득 — 앞단 selector가 못 하는 개입" if lo > 0 else
                                "★ 고립해도 손해 없음 (통합은 텍스트가 수행)" if d >= -0.02 else
                                "✗ 고립이 손해 — 이 태스크는 이미지 간 attention이 필요"))
            # 직전 'any' 태스크와 난이도 비교
            pf = RES / f"pathway{tag}.jsonl"
            if pf.exists():
                P = collections.defaultdict(dict)
                pt = {}
                for r in (json.loads(l) for l in open(pf) if l.strip()):
                    P[r["question_id"]][r["condition"]] = r
                    pt[r["question_id"]] = r["part"]
                anyit = [d for q, d in P.items() if pt[q] == 2 and "M3" in d]
                if anyit:
                    print(f"     [난이도 비교] any 태스크 AUC={A(anyit,'M3'):.4f} (천장) "
                          f"vs all 태스크 AUC={A(it,'M3'):.4f}")

        # ── B. 소프트 λ 스윕 ──────────────────────────
        soft = [f"SOFT{i}" for i in (1, 2, 4, 8)]
        it2 = [d for q, d in D.items() if part[q] == "B" and all(c in d for c in soft)]
        if len(it2) >= 50:
            sc = collections.defaultdict(dict)
            sf = RES / f"scale_auc{tag}.jsonl"
            if sf.exists():
                for r in (json.loads(l) for l in open(sf) if l.strip()):
                    sc[r["question_id"]][(r["condition"], r["n_dist"])] = r
            print(f"\n  B. 소프트 개입 λ 스윕 (방해 1장)  n={len(it2)}")
            print(f"     {'λ':>5} {'AUC':>9} {'정확도':>9}")
            print(f"     {'0 (무개입)':>5}", end="")
            base = [sc[q.replace('sf', 'sc')] for q in D if part[q] == "B"
                    and q.replace('sf', 'sc') in sc]
            base = [d for d in base if ("M", 1) in d and ("T0", 1) in d]
            if base:
                mm = auc([d[("M", 1)]["margin"] for d in base if d[("M", 1)]["gt"] == "yes"],
                         [d[("M", 1)]["margin"] for d in base if d[("M", 1)]["gt"] == "no"])
                tt = auc([d[("T0", 1)]["margin"] for d in base if d[("T0", 1)]["gt"] == "yes"],
                         [d[("T0", 1)]["margin"] for d in base if d[("T0", 1)]["gt"] == "no"])
                print(f" {mm:9.4f}   (같은 문항 n={len(base)})")
            else:
                mm = tt = float("nan")
                print("  (기준선 매칭 실패)")
            for c in soft:
                print(f"     {c[4:]:>5} {A(it2, c):9.4f} "
                      f"{sum(d[c]['correct'] for d in it2)/len(it2):9.4f}")
            if base:
                print(f"     {'∞ (하드)':>5} {tt:9.4f}")
                best = max(soft, key=lambda c: A(it2, c))
                interior = A(it2, best) > max(mm, tt) + 0.005
                print(f"     ── 최적 λ={best[4:]} (AUC {A(it2,best):.4f}). "
                      + ("★ 내부 최적 존재 — 부분 억제가 하드 차단보다 낫다"
                         if interior else "내부 최적 없음 — 하드 차단이 상한"))


if __name__ == "__main__":
    main()
