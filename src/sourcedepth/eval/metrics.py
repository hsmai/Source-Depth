"""지표·통계·판정 (브리프 B-4, PART D 사전 등록 + 결정 A-1·A-2·A-5).

조작적 정의 (사전 등록 — 결과 확인 후 변경 금지):
- Flip Rate: 분모 = 셀 전체. 셀 1·3: #(pred_S=no ∧ pred_M=yes)/n, 셀 2·4: #(pred_S=yes ∧ pred_M=no)/n
- 판정 ①: Flip1 ≥ 0.10 ∧ Flip3 < Flip1/2 ∧ Flip2 ≥ 0.10 ∧ Flip4 < Flip2/2
- 판정 ②: 셀 1·2의 gap = Acc(T0)−Acc(M). 어느 쪽이든 gap < 0.05면 ② 전체 INDETERMINATE.
  아니면 ∃L: 두 셀 모두 [Acc(TL)−Acc(M) ≥ 0.5·gap ∧ McNemar(TL vs M) p < 0.05]
- L* = 조건 충족 L 중 셀 1·2 평균 Recovery 최대인 L
- 판정 ②′: L*에서 셀 1·2 모두 Recovery > Damage
- 판정 ②″: 600문항 pooled에서 Acc(Trel8) < Acc(M) ∧ pooled McNemar p < 0.05
- 판정 ③: layer 8 (1-indexed) attention top-1 식별률 ≥ 0.80 (layer 4는 측정만)
"""
import pandas as pd
from statsmodels.stats.contingency_tables import mcnemar as _mcnemar

from ..config import (FLIP_THRESH, INDET_GAP, L_GRID, MCNEMAR_ALPHA,
                      RECOVERY_FRAC)

FLIP_DIR = {1: ("no", "yes"), 2: ("yes", "no"), 3: ("no", "yes"), 4: ("yes", "no")}


def to_wide(df: pd.DataFrame):
    """long results → wide (행=question, 열=조건별 pred/correct)."""
    pred = df.pivot_table(index=["question_id", "cell", "gt"], columns="condition",
                          values="pred", aggfunc="first")
    corr = df.pivot_table(index=["question_id", "cell", "gt"], columns="condition",
                          values="correct", aggfunc="first").astype("boolean")
    return pred.reset_index(), corr.reset_index()


def accuracy(corr: pd.DataFrame, cond: str, cell: int | None = None) -> float:
    d = corr if cell is None else corr[corr["cell"] == cell]
    return float(d[cond].mean())


def flip_rate(pred: pd.DataFrame, cell: int, cond: str = "M") -> float:
    d = pred[pred["cell"] == cell]
    s_from, m_to = FLIP_DIR[cell]
    return float(((d["S"] == s_from) & (d[cond] == m_to)).mean())


def flip_counts(pred: pd.DataFrame, cell: int, cond: str = "M") -> dict:
    d = pred[pred["cell"] == cell]
    return {"n": len(d),
            "directional": int(((d["S"] == FLIP_DIR[cell][0]) & (d[cond] == FLIP_DIR[cell][1])).sum()),
            "any_disagree": int((d["S"] != d[cond]).sum())}


def recovery_damage(corr: pd.DataFrame, cell: int, cond: str) -> tuple[float, float]:
    d = corr[corr["cell"] == cell]
    m_wrong = d[~d["M"].fillna(False)]
    m_right = d[d["M"].fillna(False)]
    rec = float(m_wrong[cond].fillna(False).mean()) if len(m_wrong) else float("nan")
    dam = float((~m_right[cond].fillna(False)).mean()) if len(m_right) else float("nan")
    return rec, dam


def mcnemar_p(corr: pd.DataFrame, cond: str, base: str = "M",
              cell: int | None = None) -> dict:
    d = corr if cell is None else corr[corr["cell"] == cell]
    a = d[base].fillna(False).astype(bool)
    b_ = d[cond].fillna(False).astype(bool)
    n11 = int((a & b_).sum()); n10 = int((a & ~b_).sum())
    n01 = int((~a & b_).sum()); n00 = int((~a & ~b_).sum())
    res = _mcnemar([[n11, n10], [n01, n00]], exact=True)
    return {"p": float(res.pvalue), "b_base_only": n10, "c_cond_only": n01}


def flops_savings(df: pd.DataFrame, n_layers: int, l_grid=None) -> dict:
    """이론 FLOPs 절감 (A-1: 분모 = 실측 N). M layout 행에서 span·seq 사용."""
    l_grid = l_grid or L_GRID
    m = df[df["condition"] == "M"].drop_duplicates("question_id")
    masked = m["img2_span"].apply(lambda s: s[1] - s[0] + 1)
    total = (m["seq_len"] * n_layers).sum()
    return {f"T{L}": float((masked * (n_layers - L)).sum() / total) for L in l_grid}


def judge(pred: pd.DataFrame, corr: pd.DataFrame, l_grid=None) -> dict:
    l_grid = l_grid or L_GRID
    out = {}
    # ① 문제 실재
    f = {c: flip_rate(pred, c) for c in (1, 2, 3, 4)}
    out["flip"] = f
    out["D1"] = {"pass": bool(f[1] >= FLIP_THRESH and f[3] < f[1] / 2
                              and f[2] >= FLIP_THRESH and f[4] < f[2] / 2),
                 "detail": f}
    # ② 메커니즘
    acc_m = {c: accuracy(corr, "M", c) for c in (1, 2)}
    acc_t0 = {c: accuracy(corr, "T0", c) for c in (1, 2)}
    gaps = {c: acc_t0[c] - acc_m[c] for c in (1, 2)}
    out["gaps"] = gaps
    per_l = {}
    for L in l_grid:
        cond = f"T{L}"
        entry = {}
        for c in (1, 2):
            acc_tl = accuracy(corr, cond, c)
            mc = mcnemar_p(corr, cond, cell=c)
            rec, dam = recovery_damage(corr, c, cond)
            entry[c] = {"acc": acc_tl, "delta": acc_tl - acc_m[c],
                        "needed": RECOVERY_FRAC * gaps[c], "p": mc["p"],
                        "b": mc["b_base_only"], "c_": mc["c_cond_only"],
                        "recovery": rec, "damage": dam}
        entry["qualifies"] = all(
            gaps[c] >= INDET_GAP and entry[c]["delta"] >= RECOVERY_FRAC * gaps[c]
            and entry[c]["p"] < MCNEMAR_ALPHA for c in (1, 2))
        per_l[L] = entry
    out["per_L"] = per_l
    if any(gaps[c] < INDET_GAP for c in (1, 2)):
        out["D2"] = {"pass": None, "status": "INDETERMINATE",
                     "reason": f"gap(cell1)={gaps[1]:.3f}, gap(cell2)={gaps[2]:.3f} — "
                               f"A-5 규칙: 격차 < {INDET_GAP} → 판정 불가 (PASS 격상 금지)"}
        out["L_star"] = None
    else:
        qual = [L for L in l_grid if per_l[L]["qualifies"]]
        l_star = max(qual, key=lambda L: (per_l[L][1]["recovery"] + per_l[L][2]["recovery"]) / 2) if qual else None
        out["D2"] = {"pass": bool(qual), "qualifying_L": qual, "L_star": l_star}
        out["L_star"] = l_star
    # ②′
    ls = out.get("L_star")
    if ls is not None:
        e = per_l[ls]
        out["D2p"] = {"pass": bool(e[1]["recovery"] > e[1]["damage"]
                                   and e[2]["recovery"] > e[2]["damage"]),
                      "at_L": ls,
                      "detail": {c: {"recovery": e[c]["recovery"], "damage": e[c]["damage"]}
                                 for c in (1, 2)}}
    else:
        out["D2p"] = {"pass": None, "status": "N/A (L* 없음)"}
    # ②″ negative control (pooled 600)
    acc_m_all = accuracy(corr, "M")
    acc_rel = accuracy(corr, "Trel8")
    mc_rel = mcnemar_p(corr, "Trel8")
    out["D2pp"] = {"pass": bool(acc_rel < acc_m_all and mc_rel["p"] < MCNEMAR_ALPHA),
                   "acc_M": acc_m_all, "acc_Trel8": acc_rel, **mc_rel}
    return out
