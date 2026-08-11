# SourceDepth Phase 0 — Feasibility REPORT

생성: 2026-08-11T14:18:41+09:00 · 설계: docs/01_feasibility_brief.md (frozen) · seed 42

## 실행 환경
- GPU: NVIDIA GeForce RTX 3090, 24576 MiB
- 패키지: torch 2.5.1+cu121, transformers 4.52.3, statsmodels 0.14.6 (전체는 logs/pip_freeze.txt)
- 모델: Qwen2.5-VL-3B-Instruct, BF16, eager · **num_hidden_layers = 36** (브리프의 32 전제와 상이 — A-1 규칙에 따라 FLOPs 분모 = 36)
- Yes/No 토큰 id: yes=[7414, 9454, 9693, 9834, 14004] no=[902, 2152, 2308, 2753, 8996]
- 프롬프트 템플릿: primary (fallback_adopted=False)
- forward median 516ms · peak VRAM 9.85GiB
- 단계별 소요: results/STATUS.md 참조

## Sanity 3종 (C-4)
1. T(0) vs S 일치율 = **0.983** (기준 ≥ 0.90)
2. first-image grounding 게이트(셀3·4) = **0.90** (기준 ≥ 0.60, 육안 로그 logs/sanity2_grounding.md)
3. S 정답률(표본 200) = **0.855** (기준 ≥ 0.60, POPE 3B급 보고치 ~0.8x)

## 판정표 (PART D 사전 등록)
| 판정 | 결과 | 근거 |
|---|---|---|
| ① 문제 실재 | **PASS** | flip 셀1 0.213 / 셀3 0.000 / 셀2 0.127 / 셀4 0.047 |
| ② 메커니즘 | **PASS** | qualifying L=[4], L*=4, gap 셀1 0.213 / 셀2 0.087 |
| ②′ Recovery>Damage | **PASS** | {'pass': True, 'at_L': 4, 'detail': {1: {'recovery': 0.8095238095238095, 'damage': 0.037037037037037035}, 2: {'recovery': 0.2545454545454545, 'damage': 0.010526315789473684}}} |
| ②″ negative control | **PASS** | acc M 0.790 → Trel8 0.502, pooled p=3.59e-38 |
| ③ 컨트롤러 | **FAIL** | layer8 식별률 0.725 (layer4 0.155는 측정만) |

## 표 1 — 조건 × 셀 (전체: results/table1.csv)

```
condition  acc_c1  acc_c2  acc_c3  acc_c4  acc_all  flip_c1  flip_c2  flip_c3  flip_c4  rec_c1  dam_c1     p_c1 bc_c1  rec_c2  dam_c2     p_c2 bc_c2 p_pooled
        S  0.8933  0.7400  0.9467  0.7800   0.8400      NaN      NaN      NaN      NaN     NaN     NaN      NaN   NaN     NaN     NaN      NaN   NaN      NaN
        M  0.7200  0.6333  0.9800  0.8267   0.7900   0.2133   0.1267      0.0   0.0467     NaN     NaN      NaN   NaN     NaN     NaN      NaN   NaN      NaN
       T4  0.9200  0.7200  0.9600  0.7667   0.8417      NaN      NaN      NaN      NaN  0.8095  0.0370 6.04e-07  4/34  0.2545  0.0105 9.77e-04  1/14      NaN
       T8  0.9333  0.6667  0.9600  0.7600   0.8300      NaN      NaN      NaN      NaN  0.8333  0.0278 6.68e-08  3/35  0.1636  0.0421 2.67e-01   4/9      NaN
      T12  0.9267  0.6667  0.9667  0.7600   0.8300      NaN      NaN      NaN      NaN  0.8333  0.0370 3.35e-07  4/35  0.1455  0.0316 2.27e-01   3/8      NaN
      T16  0.9333  0.6267  0.9667  0.7400   0.8167      NaN      NaN      NaN      NaN  0.8571  0.0370 1.86e-07  4/36  0.0909  0.0632 1.00e+00   6/5      NaN
      T20  0.8133  0.6400  0.9667  0.8267   0.8117      NaN      NaN      NaN      NaN  0.5000  0.0648 1.25e-02  7/21  0.0545  0.0211 1.00e+00   2/3      NaN
      T24  0.7333  0.6333  0.9867  0.8200   0.7933      NaN      NaN      NaN      NaN  0.0714  0.0093 6.25e-01   1/3  0.0000  0.0000 1.00e+00   0/0      NaN
       T0  0.9333  0.7200  0.9533  0.7733   0.8450      NaN      NaN      NaN      NaN  0.8333  0.0278 6.68e-08  3/35  0.2909  0.0316 4.43e-03  3/16      NaN
    Trel8  0.2400  0.0267  0.9800  0.7600   0.5017      NaN      NaN      NaN      NaN  0.0238  0.6759 7.94e-21  73/1  0.0000  0.9579 8.08e-28  91/0 3.59e-38
```

## 이론 FLOPs 절감 (A-1: (N−L)/N, N=36)
{
 "T4": 0.42408345803080344,
 "T8": 0.371073025776953,
 "T12": 0.31806259352310257,
 "T16": 0.26505216126925213,
 "T20": 0.21204172901540172,
 "T24": 0.15903129676155128
}
- 최적 L* = 4 기준 절감: 0.42408345803080344

## 한 줄 결론
distractor로 셀1 flip 21%·셀2 flip 13% 발생 (대조군 셀3 0%·셀4 5%) · L*=4 차단으로 셀1 recovery 81%·셀2 25%, distractor 토큰 이론 FLOPs 절감 42.4% · layer 8 attention top-1 식별률 72%

## 이상 징후
- logit 동률(tie) 발생: 104건 (동률→no 사전 규정)
- stage3 M 예측 vs stage4 재예측 불일치: 0건 (분류 단일 소스 = stage 3)
- fig2 그룹 크기: {'M correct': 474, 'flipped': 51}

## 한계 (PART F 요구 — 이 실험이 검증하지 않는 것)
- 관계(relational) 질문의 성능 보존 — 본 실험은 unary 질문만 다룸
- 실측 latency — mask 등가 구현이므로 측정하지 않음 (연산 절감은 해석적 계산)
- 비-oracle 컨트롤러 — 전 문항 oracle 세팅 (관련 이미지 = 항상 이미지1)
- ③의 position bias confound: 관련 이미지가 전 문항 첫 위치 → 식별률이 관련도 신호가 아닌 primacy bias일 수 있음 (03 §C-1)
- attention 질량 '합' 비교는 토큰 수 많은 이미지에 구조적으로 유리 (03 §C-2)
- COCO annotation 불완전성으로 셀 2·3 '미포함' 판정에 노이즈 가능 (03 §B-8)
- McNemar 다중 검정: L 그리드 6 × 셀 2 = 12회 (판정 ②는 conjunctive라 우연 통과 상한 ≈1.5%)
- batch 1 사용 (C-1의 '배치 4~8' 지침에서 이탈 — 시간 상한 내 단순성 우선)

## BLOCKED 목록
없음

## 제안 (실행하지 않음 — PART F)
- 이미지 순서 뒤집기(distractor 먼저) 대조 실행으로 ③ position bias 분리 (Phase 1)
- per-token 평균 질량 기준 식별률 병기
- Bonferroni 조정 p 참고치 병기
- distractor 2장 확장 및 시각 유사 distractor (PART D 실패 대응 경로 — 이번 실행에서 미사용 시)