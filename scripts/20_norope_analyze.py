#!/usr/bin/env python
"""RoPE 제거 컨트롤러 판정 — 기존(RoPE 적용) 결과와 층별 직접 비교.

지표: 위치무관 판정 정확도 = (원순서 정확도 + 뒤집기 정확도) / 2
head 선택은 원순서 절반(calibration)에서, 평가는 나머지 절반 + 뒤집기 전체에서.
"""
import json
import random
import sys
from pathlib import Path

import numpy as np

RES = Path(__file__).resolve().parents[1] / "results"
SEED = 42
TAG = sys.argv[1] if len(sys.argv) > 1 else ""


def load(p):
    rows = [json.loads(l) for l in open(p) if l.strip()]
    rows.sort(key=lambda r: r["question_id"])
    m1 = np.array([[l[0] for l in r["heads"]] for r in rows])   # (n, L, H)
    m2 = np.array([[l[1] for l in r["heads"]] for r in rows])
    return m1 - m2, [r["question_id"] for r in rows]


def main():
    fo, fs = RES / f"norope_profile{TAG}.jsonl", RES / f"norope_profile_swapped{TAG}.jsonl"
    if not (fo.exists() and fs.exists()):
        print("결과 파일 없음 — 실행 대기")
        return
    do, qo = load(fo)
    ds, qs = load(fs)
    common = sorted(set(qo) & set(qs))
    io = [qo.index(q) for q in common]
    isw = [qs.index(q) for q in common]
    do, ds = do[io], ds[isw]
    n, L, H = do.shape
    print(f"RoPE 제거 컨트롤러  n={n} 문항, {L}층 × {H} head")

    rng = random.Random(SEED)
    order = list(range(n))
    rng.shuffle(order)
    cal, test = order[: n // 2], order[n // 2:]

    # 기존(RoPE 적용) 결과 — 비교용
    old = {}
    f_old = RES / "controller_swap_check.json"
    if f_old.exists():
        for k, v in json.load(open(f_old))["per_layer"].items():
            old[int(k)] = (v["acc_original"] + v["acc_swapped"]) / 2

    print(f"\n  {'층':>3} {'원순서':>9} {'뒤집기':>9} {'위치무관':>10}   {'기존(RoPE)':>11}  {'변화':>8}")
    best = (None, -1)
    for l in range(L):
        # calibration 절반의 원순서에서 head 선택 (관련 이미지 질량이 더 큰 비율 최대)
        h = int(np.argmax((do[cal, l, :] > 0).mean(0)))
        ao = float((do[test, l, h] > 0).mean())
        asw = float((ds[test, l, h] > 0).mean())
        bal = (ao + asw) / 2
        o = old.get(l + 1)
        mark = ""
        if bal > best[1]:
            best = (l + 1, bal)
        if o is not None and bal - o > 0.15:
            mark = "  ★ 개선"
        print(f"  {l+1:>3} {ao:9.3f} {asw:9.3f} {bal:10.3f}   "
              + (f"{o:11.3f}  {bal-o:+8.3f}" if o is not None else " " * 21) + mark)

    print(f"\n  최고 위치무관 층 = {best[0]}층 ({best[1]:.3f})")
    shallow = [(l + 1, ((do[test, l, int(np.argmax((do[cal, l, :] > 0).mean(0)))] > 0).mean()
                        + (ds[test, l, int(np.argmax((do[cal, l, :] > 0).mean(0)))] > 0).mean()) / 2)
               for l in range(min(16, L))]
    bs = max(shallow, key=lambda x: x[1])
    print(f"  16층 이하 최고 = {bs[0]}층 ({bs[1]:.3f})")
    print("\n  판정 기준: 16층 이하에서 위치무관 ≥ 0.80 이면 '차단이 이득인 구간에서 판정 가능'")
    print(f"  → {'★ 통과 — 두 곡선이 겹친다' if bs[1] >= 0.80 else '✗ 실패 — 기존 결론 유지'}")


if __name__ == "__main__":
    main()
