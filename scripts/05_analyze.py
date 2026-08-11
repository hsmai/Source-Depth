#!/usr/bin/env python
"""C-5 단계 5: 병합·지표·그림·REPORT.md (CPU 전용).

afterany로 실행되므로 파이프라인이 어디서 멈췄든 STATUS.md는 반드시 생성한다.
결과가 완전할 때만 REPORT.md 판정을 확정한다. 수치는 전부 실측값 (PART F).
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from sourcedepth.config import (ATTN_PROFILE, CONDITIONS, IDENT_THRESH, L_GRID,
                                LOGS_DIR, N_PER_CELL, PAIRS_CSV,
                                PROFILE_LAYERS_1IDX, RAW_RESULTS, RESULTS_DIR,
                                SMOKE_FLAG, TAG, TEMPLATE_CHOICE)
from sourcedepth.eval.metrics import (FLIP_DIR, accuracy, flip_counts,
                                      flip_rate, flops_savings, judge,
                                      mcnemar_p, recovery_damage, to_wide)
from sourcedepth.runlog import dump_env, iso_now, read_jsonl, stage

EXPECTED = 4 * N_PER_CELL * len(CONDITIONS)   # 6000


def _table_md(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)      # tabulate 필요
    except ImportError:
        return "```\n" + df.to_string(index=False) + "\n```"


def pipeline_status(template, n_rows, n_profile):
    stages = read_jsonl(LOGS_DIR / "stage_times.jsonl")
    lines = [f"# STATUS — {iso_now()}", "",
             f"- template: {template}",
             f"- raw_results rows (현 template): {n_rows} / {EXPECTED}",
             f"- attn_profile rows: {n_profile} / {4 * N_PER_CELL}",
             "", "## 단계 이벤트 로그 (stage_times.jsonl)", ""]
    for s in stages[-40:]:
        lines.append(f"- {s['ts']} [{s.get('event')}] {s.get('stage')} "
                     f"({s.get('elapsed_s', '')}s) {s.get('reason', '')}")
    blocked_md = LOGS_DIR / "BLOCKED.md"
    lines += ["", "## BLOCKED", "", blocked_md.read_text() if blocked_md.exists() else "없음"]
    (RESULTS_DIR / f"STATUS{TAG}.md").write_text("\n".join(lines))
    print(f"STATUS{TAG}.md written ({n_rows}/{EXPECTED} rows)")


def fig1(pred, corr, path, l_grid=None):
    l_grid = l_grid or L_GRID
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, cell in zip(axes, (1, 2)):
        accs = [accuracy(corr, f"T{L}", cell) for L in l_grid]
        m = accuracy(corr, "M", cell)
        t0 = accuracy(corr, "T0", cell)
        rel = accuracy(corr, "Trel8", cell)
        ax.plot(l_grid, accs, "o-", label="T(L)")
        ax.axhline(m, color="tab:red", ls="--", label="M (baseline)")
        ax.axhline(t0, color="tab:green", ls=":", label="T(0)")
        ax.plot([8], [rel], "x", color="tab:purple", ms=10, label="T-rel(8) neg. ctrl")
        ax.set_title(f"Cell {cell} ({'No->Yes leak' if cell == 1 else 'Yes->No leak'})")
        ax.set_xlabel("KV-block depth L (0-based, mask at layer idx >= L)")
        ax.set_ylabel("Accuracy")
        ax.grid(alpha=0.3)
    axes[0].legend(loc="lower right", fontsize=8)
    fig.suptitle("Accuracy vs KV-block depth L (POPE+COCO distractor, Qwen2.5-VL-3B)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig2(profile_rows, pred, path, n_layers):
    by_q = {r["question_id"]: r for r in profile_rows}
    groups = {"M correct": [], "flipped": []}
    for r in pred.itertuples():
        pr = by_q.get(r.question_id)
        if pr is None:
            continue
        s_from, m_to = FLIP_DIR[r.cell]
        if getattr(r, "M") == r.gt:
            groups["M correct"].append(pr["masses"])
        elif r.cell in (1, 2) and getattr(r, "S") == s_from and getattr(r, "M") == m_to:
            groups["flipped"].append(pr["masses"])   # leak 측정 셀(1·2)의 방향성 flip만 (리뷰 지적)
    fig, ax = plt.subplots(figsize=(9, 5))
    xs = list(range(1, n_layers + 1))
    styles = {"M correct": "-", "flipped": "--"}
    import numpy as np
    counts = {}
    for gname, rows_ in groups.items():
        if not rows_:
            continue
        counts[gname] = len(rows_)
        arr = np.array(rows_)                     # (n, layers, 3)
        ax.plot(xs, arr[:, :, 0].mean(0), styles[gname], color="tab:blue",
                label=f"img1 (relevant) — {gname} (n={len(rows_)})")
        ax.plot(xs, arr[:, :, 1].mean(0), styles[gname], color="tab:orange",
                label=f"img2 (distractor) — {gname}")
    ax.set_xlabel("layer (1-indexed)")
    ax.set_ylabel("attention mass (head mean, last prompt token)")
    ax.set_title("Per-layer image attention mass — condition M (correct vs flipped)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return counts


def _clean_nan(o):
    if isinstance(o, dict):
        return {k: _clean_nan(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean_nan(v) for v in o]
    if isinstance(o, float) and o != o:
        return None
    return o


def main():
    dump_env("05_analyze")
    template = "primary"
    if TEMPLATE_CHOICE.exists():
        try:                       # torn write여도 STATUS 생성은 보장 (리뷰 지적)
            template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"WARN: template_choice.json 손상 ({e}) — primary 가정")
    raw = [r for r in read_jsonl(RAW_RESULTS) if r.get("template") == template]
    seen, rows = set(), []
    for r in raw:                                  # 중복 방지 (resume 경계)
        k = (r["question_id"], r["condition"])
        if k not in seen:
            seen.add(k)
            rows.append(r)
    profile_rows = [r for r in read_jsonl(ATTN_PROFILE) if r.get("template") == template]
    pipeline_status(template, len(rows), len(profile_rows))
    # 완료성 = 행 수가 아니라 (question, 기본 조건) 전수 커버리지 (리뷰 지적: --extra-l 행이
    # 수를 부풀려 미완료 데이터로 REPORT를 확정할 수 있음)
    if not PAIRS_CSV.exists():
        print("pairs.csv 부재 — REPORT 확정 불가")
        return
    pair_qids = list(pd.read_csv(PAIRS_CSV)["question_id"].astype(str))
    have = {(str(r["question_id"]), r["condition"]) for r in rows}
    missing = [(q, c) for q in pair_qids for c in CONDITIONS if (q, c) not in have]
    if missing:
        print(f"결과 불완전 (미비 {len(missing)}/{len(pair_qids) * len(CONDITIONS)} — "
              f"예: {missing[:3]}) — REPORT 확정 불가, STATUS만 갱신")
        return

    with stage("05_analyze"):
        df = pd.DataFrame(rows)
        df.to_csv(RESULTS_DIR / f"results{TAG}.csv", index=False)
        pred, corr = to_wide(df)
        n_layers = json.loads(SMOKE_FLAG.read_text())["num_hidden_layers"]

        # 곡선(fig1)·FLOPs는 데이터에 실재하는 모든 T(L)로 — 세분화 실행분 포함.
        # 단 **판정 ②는 사전 등록 L_GRID로만** (세분화 L을 판정에 넣으면 탐색 공간이
        # 넓어져 사전 등록 위반 — 세분화는 곡선 해상도용 탐색적 분석)
        det_ls = sorted({int(c[1:]) for c in df["condition"].unique()
                         if c.startswith("T") and c[1:].isdigit() and int(c[1:]) > 0})
        judge_ls = [l for l in det_ls if l in L_GRID] or det_ls
        j = judge(pred, corr, l_grid=judge_ls)
        flops = flops_savings(df, n_layers, l_grid=det_ls)

        # 표 1
        t1 = []
        for cond in CONDITIONS:
            row = {"condition": cond}
            for c in (1, 2, 3, 4):
                row[f"acc_c{c}"] = round(accuracy(corr, cond, c), 4)
            row["acc_all"] = round(accuracy(corr, cond), 4)
            if cond == "M":
                for c in (1, 2, 3, 4):
                    row[f"flip_c{c}"] = round(flip_rate(pred, c), 4)
            if cond.startswith("T"):
                for c in (1, 2):
                    rec, dam = recovery_damage(corr, c, cond)
                    mc = mcnemar_p(corr, cond, cell=c)
                    row[f"rec_c{c}"] = round(rec, 4)
                    row[f"dam_c{c}"] = round(dam, 4)
                    row[f"p_c{c}"] = f"{mc['p']:.2e}"
                    row[f"bc_c{c}"] = f"{mc['b_base_only']}/{mc['c_cond_only']}"
            if cond == "Trel8":
                mc = mcnemar_p(corr, cond)
                row["p_pooled"] = f"{mc['p']:.2e}"
            t1.append(row)
        table1 = pd.DataFrame(t1)
        table1.to_csv(RESULTS_DIR / f"table1{TAG}.csv", index=False)

        fig1(pred, corr, RESULTS_DIR / f"fig1_accuracy_vs_L{TAG}.png", l_grid=det_ls)

        ident, fig2_counts, mismatch = {}, {}, None
        profile_complete = {str(r["question_id"]) for r in profile_rows} >= set(pair_qids)
        if profile_rows:
            import numpy as np
            arr = np.array([r["masses"] for r in profile_rows])
            for l1 in PROFILE_LAYERS_1IDX:
                ident[l1] = float((arr[:, l1 - 1, 0] > arr[:, l1 - 1, 1]).mean())
            fig2_counts = fig2(profile_rows, pred,
                               RESULTS_DIR / f"fig2_attention_profile{TAG}.png", n_layers)
            m_pred = dict(zip(pred["question_id"], pred["M"]))
            mismatch = sum(1 for r in profile_rows
                           if m_pred.get(r["question_id"]) not in (None, r["pred_reprofile"]))
        # ③ 판정은 프로파일 전수(600) 완료 시에만 확정 (리뷰 지적: partial로 PASS/FAIL 금지)
        d3_pass = (ident.get(8, 0.0) >= IDENT_THRESH) if (ident and profile_complete) else None

        # ---- REPORT.md ----
        smoke = json.loads(SMOKE_FLAG.read_text())
        sanity = json.loads((LOGS_DIR / "sanity_summary.json").read_text())
        ties = int(df["tie"].sum()) if "tie" in df else 0
        ls = j.get("L_star")
        envs = {p.name: json.loads(p.read_text()) for p in LOGS_DIR.glob("env_*.json")}
        any_env = {}
        for name in ("env_03_main.json", "env_00_smoke.json", "env_02_sanity.json"):
            if name in envs and "unavailable" not in str(envs[name].get("nvidia_smi", "")):
                any_env = envs[name]      # GPU 노드에서 기록된 env 우선 (리뷰 지적)
                break
        if not any_env and envs:
            any_env = next(iter(envs.values()))

        def pf(x):
            return "PASS" if x is True else ("FAIL" if x is False else "INDETERMINATE")

        if j["D2"].get("status") == "INDETERMINATE":
            d2_evidence = j["D2"]["reason"]
        else:
            d2_evidence = (f"qualifying L={j['D2'].get('qualifying_L')}, L*={ls}, "
                           f"gap 셀1 {j['gaps'][1]:.3f} / 셀2 {j['gaps'][2]:.3f}")

        concl = []
        if j["D1"]["pass"]:
            concl.append(f"distractor로 셀1 flip {j['flip'][1]:.0%}·셀2 flip {j['flip'][2]:.0%} 발생 (대조군 셀3 {j['flip'][3]:.0%}·셀4 {j['flip'][4]:.0%})")
        else:
            concl.append(f"distractor flip 격차가 판정 기준 미달 (셀1 {j['flip'][1]:.0%} vs 셀3 {j['flip'][3]:.0%}, 셀2 {j['flip'][2]:.0%} vs 셀4 {j['flip'][4]:.0%})")
        if ls is not None:
            e = j["per_L"][ls]
            concl.append(f"L*={ls} 차단으로 셀1 recovery {e[1]['recovery']:.0%}·셀2 {e[2]['recovery']:.0%}, distractor 토큰 이론 FLOPs 절감 {flops[f'T{ls}']:.1%}")
        elif j["D2"].get("status") == "INDETERMINATE":
            concl.append("판정 ②는 A-5 규칙상 INDETERMINATE (M→T(0) 격차 < 5%p)")
        else:
            concl.append("어떤 L에서도 사전 등록 회복 기준(50%+, p<0.05) 미충족")
        if ident:
            concl.append(f"layer 8 attention top-1 식별률 {ident[8]:.0%}")

        rpt = [f"# SourceDepth Phase 0 — Feasibility REPORT", "",
               f"생성: {iso_now()} · 설계: docs/01_feasibility_brief.md (frozen) · seed 42", "",
               "## 실행 환경",
               f"- GPU: {any_env.get('nvidia_smi', '?')}",
               f"- 패키지: torch {any_env.get('torch')}, transformers {any_env.get('transformers')}, "
               f"statsmodels {any_env.get('statsmodels')} (전체는 logs/pip_freeze.txt)",
               f"- 모델: Qwen2.5-VL-3B-Instruct, BF16, eager · **num_hidden_layers = {n_layers}** "
               f"(브리프의 32 전제와 상이 — A-1 규칙에 따라 FLOPs 분모 = {n_layers})",
               f"- Yes/No 토큰 id: yes={smoke['yes_ids']} no={smoke['no_ids']}",
               f"- 프롬프트 템플릿: {template} (fallback_adopted={sanity['fallback_adopted']})",
               f"- forward median {smoke['forward_median_ms']:.0f}ms · peak VRAM {smoke['peak_vram_gib']}GiB",
               f"- 단계별 소요: results/STATUS.md 참조", "",
               "## Sanity 3종 (C-4)",
               f"1. T(0) vs S 일치율 = **{sanity['sanity1_agree']:.3f}** (기준 ≥ 0.90)",
               f"2. first-image grounding 게이트(셀3·4) = **{sanity['sanity2_gate_acc']:.2f}** "
               f"(기준 ≥ 0.60, 육안 로그 logs/sanity2_grounding.md)",
               f"3. S 정답률(표본 200) = **{sanity['sanity3_s_acc']:.3f}** (기준 ≥ 0.60, POPE 3B급 보고치 ~0.8x)", "",
               "## 판정표 (PART D 사전 등록)",
               "| 판정 | 결과 | 근거 |", "|---|---|---|",
               f"| ① 문제 실재 | **{pf(j['D1']['pass'])}** | flip 셀1 {j['flip'][1]:.3f} / 셀3 {j['flip'][3]:.3f} / 셀2 {j['flip'][2]:.3f} / 셀4 {j['flip'][4]:.3f} |",
               f"| ② 메커니즘 | **{pf(j['D2']['pass'])}** | {d2_evidence} |",
               f"| ②′ Recovery>Damage | **{pf(j['D2p']['pass'])}** | {j['D2p']} |",
               f"| ②″ negative control | **{pf(j['D2pp']['pass'])}** | acc M {j['D2pp']['acc_M']:.3f} → Trel8 {j['D2pp']['acc_Trel8']:.3f}, pooled p={j['D2pp']['p']:.2e} |",
               f"| ③ 컨트롤러 | **{pf(d3_pass)}** | layer8 식별률 {ident.get(8, float('nan')):.3f} (layer4 {ident.get(4, float('nan')):.3f}는 측정만) |", "",
               "## 표 1 — 조건 × 셀 (전체: results/table1.csv)", "",
               _table_md(table1), "",
               "## 이론 FLOPs 절감 (A-1: (N−L)/N, N=%d)" % n_layers,
               json.dumps(flops, indent=1),
               f"- 최적 L* = {ls} 기준 절감: {flops.get(f'T{ls}', 'N/A') if ls else 'N/A'}", "",
               "## 한 줄 결론", " · ".join(concl), "",
               "## 이상 징후",
               f"- logit 동률(tie) 발생: {ties}건 (동률→no 사전 규정)",
               f"- stage3 M 예측 vs stage4 재예측 불일치: {mismatch}건 (분류 단일 소스 = stage 3)",
               f"- fig2 그룹 크기: {fig2_counts}", "",
               "## 한계 (PART F 요구 — 이 실험이 검증하지 않는 것)",
               "- 관계(relational) 질문의 성능 보존 — 본 실험은 unary 질문만 다룸",
               "- 실측 latency — mask 등가 구현이므로 측정하지 않음 (연산 절감은 해석적 계산)",
               "- 비-oracle 컨트롤러 — 전 문항 oracle 세팅 (관련 이미지 = 항상 이미지1)",
               "- ③의 position bias confound: 관련 이미지가 전 문항 첫 위치 → 식별률이 관련도 신호가 아닌 primacy bias일 수 있음 (03 §C-1)",
               "- attention 질량 '합' 비교는 토큰 수 많은 이미지에 구조적으로 유리 (03 §C-2)",
               "- COCO annotation 불완전성으로 셀 2·3 '미포함' 판정에 노이즈 가능 (03 §B-8)",
               "- McNemar 다중 검정: L 그리드 6 × 셀 2 = 12회 (판정 ②는 conjunctive라 우연 통과 상한 ≈1.5%)",
               "- batch 1 사용 (C-1의 '배치 4~8' 지침에서 이탈 — 시간 상한 내 단순성 우선)", "",
               "## BLOCKED 목록",
               (LOGS_DIR / "BLOCKED.md").read_text() if (LOGS_DIR / "BLOCKED.md").exists() else "없음", "",
               "## 제안 (실행하지 않음 — PART F)",
               "- 이미지 순서 뒤집기(distractor 먼저) 대조 실행으로 ③ position bias 분리 (Phase 1)",
               "- per-token 평균 질량 기준 식별률 병기",
               "- Bonferroni 조정 p 참고치 병기",
               "- distractor 2장 확장 및 시각 유사 distractor (PART D 실패 대응 경로 — 이번 실행에서 미사용 시)"]
        (RESULTS_DIR / f"REPORT{TAG}.md").write_text("\n".join(rpt))
        (RESULTS_DIR / f"judgments{TAG}.json").write_text(
            json.dumps(_clean_nan(j), indent=1, ensure_ascii=False, default=str))
        print("REPORT.md written")
        print("\n".join(concl))


if __name__ == "__main__":
    main()
