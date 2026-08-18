#!/usr/bin/env python
"""밤새 나온 결과를 한 파일로 요약 — results/OVERNIGHT_SUMMARY.md

존재하는 결과 파일만 읽고, 없는 것은 '미완료'로 적는다. 어떤 실험이 실패했는지도 그대로 남긴다.
"""
import collections, json, random, sys
from pathlib import Path

RES = Path(__file__).resolve().parents[1] / "results"
OUT = RES / "OVERNIGHT_SUMMARY.md"
L = []
def w(s=""): L.append(s)

def auc(pos, neg):
    a = sorted([(v,1) for v in pos] + [(v,0) for v in neg]); r={}; i=0
    while i < len(a):
        j=i
        while j+1 < len(a) and a[j+1][0]==a[i][0]: j+=1
        m=(i+j)/2+1
        for k in range(i,j+1): r[k]=m
        i=j+1
    R=sum(r[k] for k,(v,l) in enumerate(a) if l==1); n1,n0=len(pos),len(neg)
    return float("nan") if not n1 or not n0 else (R-n1*(n1+1)/2)/(n1*n0)

def load(name):
    f = RES / name
    if not f.exists(): return None
    return [json.loads(x) for x in open(f) if x.strip()]

def A(items, c, key="condition"):
    d=[x for x in items if x[key]==c]
    return auc([x["margin"] for x in d if x["gt"]=="yes"],
               [x["margin"] for x in d if x["gt"]=="no"])

def boot(items, ca, cb, key="condition", B=2000, seed=1):
    by=collections.defaultdict(dict)
    for x in items: by[x["question_id"]][x[key]]=x
    it=[v for v in by.values() if ca in v and cb in v]
    if len(it) < 30: return None
    rnd=random.Random(seed); o=[]
    for _ in range(B):
        s=[rnd.choice(it) for _ in it]
        f=lambda c: auc([d[c]["margin"] for d in s if d[c]["gt"]=="yes"],
                        [d[c]["margin"] for d in s if d[c]["gt"]=="no"])
        o.append(f(ca)-f(cb))
    o.sort(); return o[int(.025*B)], o[int(.975*B)]

w("# 밤새 실행 결과 요약\n")
w("생성: 33_overnight_summary.py · 존재하는 파일만 읽음\n")

# ── 1. 비용 실측 ──
w("\n## 1. 비용 실측 (FOCUS 방식 대비)\n")
f = RES / "cost_bench.json"
if f.exists():
    d = json.load(open(f))
    w(f"| 항목 | ms |\n|---|---|")
    for k in ("t_full","t_vision","t_llm","t_kvmask","t_pixel"):
        w(f"| {k} | {d.get(k,'-')} |")
    w(f"\nvision encoder 비중: **{d.get('vision_share_pct','-')}%**\n")
    w("| 절단 층 | FOCUS | 우리 | 절감 |\n|---|---|---|---|")
    for Lv in (0,8,16,24):
        p=d.get(f"pipeline_L{Lv}")
        if p: w(f"| L={Lv} | {p['FOCUS_ms']}ms | {p['ours_ms']}ms | **{p['saving_pct']}%** |")
else:
    w("**미완료 또는 실패** — cost_bench.json 없음\n")

# ── 2. 층 절단 반사실 ──
w("\n## 2. 층 절단 반사실 — 판별기를 싸게 만들 수 있는가\n")
r = load("trunc_cf.jsonl")
if r:
    by=collections.defaultdict(dict)
    for x in r: by[x["question_id"]][x["condition"]]=x
    w("| 절단 층 | 판별 정확도 | (참고) L=0 기준 0.730 |\n|---|---|---|")
    for Lv in (8,16,24):
        need=["M"]+[f"B{i}@{Lv}" for i in range(4)]
        it=[v for v in by.values() if all(c in v for c in need)]
        if not it: continue
        acc=sum(max(range(4), key=lambda i: abs(v[f"B{i}@{Lv}"]["margin"]-v["M"]["margin"]))==0
                for v in it)/len(it)
        w(f"| {Lv}층부터 | **{acc:.4f}** | n={len(it)} |")
    w("\n판정: 16층에서 0.70 이상 유지되면 비용 우위 주장 성립\n")
else:
    w("**미완료** — trunc_cf.jsonl 없음\n")

# ── 3. 읽기 깊이 ──
w("\n## 3. 읽기 차단을 몇 층부터 걸어야 하는가\n")
for tag,label in (("","3B"),("_7b","7B")):
    r = load(f"readdepth{tag}.jsonl")
    if not r: w(f"**{label} 미완료**\n"); continue
    w(f"\n### {label}  (n={len({x['question_id'] for x in r})})\n")
    w("| 조건 | 판별력 점수 |\n|---|---|")
    for c in ["M","READ0","READ8","READ16","READ24","T0"]:
        v=A(r,c)
        if v==v: w(f"| {c} | {v:.4f} |")
    ci=boot(r,"READ16","READ0")
    if ci: w(f"\nREAD16 − READ0 의 95%CI: [{ci[0]:+.4f}, {ci[1]:+.4f}]"
             + ("  → 뒤쪽만 막아도 충분" if ci[0] > -0.02 else "  → 앞쪽부터 막아야 함") + "\n")

# ── 4. 부분 관련 ──
w("\n## 4. 부분 관련 — selection이 잘못된 추상인가\n")
for tag,label in (("","3B"),("_7b","7B")):
    r = load(f"partial{tag}.jsonl")
    if not r: w(f"**{label} 미완료**\n"); continue
    for grp in ("PART-hit","PART-miss"):
        sub=[x for x in r if x["group"]==grp]
        if not sub: continue
        w(f"\n### {label} · {grp}  (n={len({x['question_id'] for x in sub})})\n")
        w("| 조건 | 판별력 점수 |\n|---|---|")
        vals={}
        for c in ["M","DROP2","READ2","DROP3","READ3"]:
            v=A(sub,c); vals[c]=v
            if v==v: w(f"| {c} | {v:.4f} |")
        if all(k in vals and vals[k]==vals[k] for k in ("M","DROP2","READ2")):
            base=max(vals["M"], vals["DROP2"])
            ci=boot(sub,"READ2","DROP2" if vals["DROP2"]>=vals["M"] else "M")
            w(f"\nREAD2 − max(M, DROP2) = **{vals['READ2']-base:+.4f}**"
              + (f"  95%CI [{ci[0]:+.4f}, {ci[1]:+.4f}]" if ci else ""))
            if grp=="PART-hit" and ci:
                w(f"\n**판정: {'통과 — selection이 표현 못 하는 우월 지점 존재' if ci[0]>0 else '불성립 — 주장 철회'}**\n")

OUT.write_text("\n".join(L))
print(f"작성 완료: {OUT}")
print("\n".join(L[:40]))
