#!/usr/bin/env python
"""밤새 결과 요약 v2 — endtoend / routing / anchor / trunc_cf_7b. 없는 파일은 건너뜀."""
import collections, json, random, sys
from pathlib import Path
RES = Path(__file__).resolve().parents[1] / "results"
OUT = RES / "OVERNIGHT2.md"
B = 2000

def auc(p, n):
    a = sorted([(v, 1) for v in p] + [(v, 0) for v in n]); r = {}; i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[j+1][0] == a[i][0]: j += 1
        m = (i + j) / 2 + 1
        for k in range(i, j + 1): r[k] = m
        i = j + 1
    R = sum(r[k] for k, (v, l) in enumerate(a) if l == 1)
    n1, n0 = len(p), len(n)
    return float("nan") if not n1 or not n0 else (R - n1*(n1+1)/2) / (n1*n0)

def A(items, c):
    return auc([d[c]["margin"] for d in items if d[c]["gt"] == "yes"],
               [d[c]["margin"] for d in items if d[c]["gt"] == "no"])

def ci(items, ca, cb, seed):
    rnd = random.Random(seed); o = []
    for _ in range(B):
        s = [rnd.choice(items) for _ in items]
        o.append(A(s, ca) - A(s, cb))
    o.sort(); return o[int(.025*B)], o[int(.975*B)]

L = ["# 밤새 실행 결과 v2\n"]

def rd(name):
    f = RES / name
    if not f.exists(): return []
    return [json.loads(l) for l in open(f) if l.strip()]

# 1. endtoend — loo의 M과 짝지어 실현/오라클 표
for tag, lab in (("", "3B"), ("_7b", "7B")):
    e = rd(f"endtoend{tag}.jsonl")
    if not e: continue
    loo = {(x["question_id"], x["n_dist"]): x for x in rd(f"loo{tag}.jsonl") if x["condition"] == "M"}
    L.append(f"\n## 종단 성능 {lab} (docs/33)\n")
    L.append("| N | M | REAL_READ | ORD_READ | REAL−M CI | 판정 |\n|---|---|---|---|---|---|")
    for n in (1, 2, 3):
        D = collections.defaultdict(dict)
        for x in e:
            if x["n_dist"] == n: D[x["question_id"]][x["condition"]] = x
        it = []
        for q, v in D.items():
            if (q, n) in loo and all(c in v for c in ("REAL_READ", "ORD_READ")):
                v = dict(v); v["M"] = loo[(q, n)]; it.append(v)
        if len(it) < 50: continue
        lo, hi = ci(it, "REAL_READ", "M", 40 + n)
        verdict = "★통과" if lo > 0 else ("부분" if A(it, "REAL_READ") >= A(it, "M") else "✗실패")
        L.append(f"| {n} | {A(it,'M'):.4f} | {A(it,'REAL_READ'):.4f} | {A(it,'ORD_READ'):.4f} "
                 f"| [{lo:+.4f},{hi:+.4f}] | {verdict} |")
        keep = [v for v in it if "REAL_KEEP" in v]
        if len(keep) > 50:
            L.append(f"|  |  | KEEP비교: READ {A(keep,'REAL_READ'):.4f} vs KEEP {A(keep,'REAL_KEEP'):.4f} | | | |")

# 2. routing contrast (docs/30) — 적대셀 주종점 + 대조셀 부종점
for tag, lab in (("", "3B"), ("_7b", "7B")):
    r = rd(f"routing{tag}.jsonl")
    if not r: continue
    L.append(f"\n## 경로 대비 재현 {lab} (docs/30, β=1 고정)\n")
    for cells, nm in ((("c1", "c2"), "적대셀(주종점)"), (("c3", "c4"), "대조셀(부종점2)")):
        D = collections.defaultdict(dict)
        for x in r:
            if x["kind"] in cells: D[x["question_id"]][x["condition"]] = x
        it = [v for v in D.values() if all(c in v for c in ("M", "READ2", "XIMG", "NOISE2"))]
        if len(it) < 50: continue
        for v in it:
            v["COMBO"] = {"margin": 2*v["READ2"]["margin"] - v["XIMG"]["margin"], "gt": v["READ2"]["gt"]}
            v["FSTYLE"] = {"margin": 2*v["NOISE2"]["margin"] - v["M"]["margin"], "gt": v["M"]["gt"]}
        lo, hi = ci(it, "COMBO", "READ2", 60)
        L.append(f"**{nm}** n={len(it)}: M {A(it,'M'):.4f} · READ2 {A(it,'READ2'):.4f} · "
                 f"조합 {A(it,'COMBO'):.4f} (Δ vs READ2 [{lo:+.4f},{hi:+.4f}]) · "
                 f"FOCUS식 {A(it,'FSTYLE'):.4f}\n")

# 3. anchor 벤치 (docs/32)
for tag, lab in (("", "3B"), ("_7b", "7B")):
    a = rd(f"anchor{tag}.jsonl")
    if not a: continue
    L.append(f"\n## anchor 벤치 {lab} (docs/32)\n")
    L.append("| K | M | REAL_READ | ORD_READ | ORD−M CI | REAL−M CI | 판별정확도 |\n|---|---|---|---|---|---|---|")
    for k in (2, 3):
        D = collections.defaultdict(dict)
        for x in a:
            if x["k"] == k: D[x["question_id"]][x["condition"]] = x
        it = [v for v in D.values() if all(c in v for c in ("M", "ORD_READ", "REAL_READ"))]
        if len(it) < 50: continue
        lo1, hi1 = ci(it, "ORD_READ", "M", 70 + k)
        lo2, hi2 = ci(it, "REAL_READ", "M", 80 + k)
        pc = [v["REAL_READ"].get("pick_correct") for v in it]
        pca = sum(1 for x in pc if x) / len(pc)
        L.append(f"| {k} | {A(it,'M'):.4f} | {A(it,'REAL_READ'):.4f} | {A(it,'ORD_READ'):.4f} "
                 f"| [{lo1:+.4f},{hi1:+.4f}] | [{lo2:+.4f},{hi2:+.4f}] | {pca:.3f} |")
clip = rd("anchor_clip.jsonl")
if clip:
    for k in (2, 3):
        s = [x for x in clip if x["k"] == k]
        if s: L.append(f"\nCLIP selector K={k}: {sum(x['clip_correct'] for x in s)/len(s):.3f} (n={len(s)}, 찍기 {1/k:.2f})")

# 4. 7B 절단 반사실
t = rd("trunc_cf_7b.jsonl")
if t:
    L.append("\n## 절단 반사실 7B\n")
    D = collections.defaultdict(dict)
    for x in t: D[x["question_id"]][x["condition"]] = x
    conds = sorted({x["condition"] for x in t})
    L.append(f"조건: {conds} — 판별 정확도는 손계산 필요(23_pathway_analyze 참고), row 수 {len(t)}")

OUT.write_text("\n".join(L))
print(f"wrote {OUT} ({len(L)} lines)")
