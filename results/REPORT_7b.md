# SourceDepth Phase 0 — Feasibility REPORT

생성: 2026-08-11T23:35:06+09:00 · 설계: docs/01_feasibility_brief.md (frozen) · seed 42

## 실행 환경
- GPU: NVIDIA GeForce RTX 3090, 24576 MiB
- 패키지: torch 2.5.1+cu121, transformers 4.52.3, statsmodels 0.14.6 (전체는 logs/pip_freeze.txt)
- 모델: Qwen2.5-VL-3B-Instruct, BF16, eager · **num_hidden_layers = 28** (브리프의 32 전제와 상이 — A-1 규칙에 따라 FLOPs 분모 = 28)
- Yes/No 토큰 id: yes=[7414, 9454, 9693, 9834, 14004] no=[902, 2152, 2308, 2753, 8996]
- 프롬프트 템플릿: primary (fallback_adopted=False)
- forward median 627ms · peak VRAM 18.57GiB
- 단계별 소요: results/STATUS.md 참조

## Sanity 3종 (C-4)
1. T(0) vs S 일치율 = **0.917** (기준 ≥ 0.90)
2. first-image grounding 게이트(셀3·4) = **0.80** (기준 ≥ 0.60, 육안 로그 logs/sanity2_grounding.md)
3. S 정답률(표본 200) = **0.840** (기준 ≥ 0.60, POPE 3B급 보고치 ~0.8x)

## 판정표 (PART D 사전 등록)
| 판정 | 결과 | 근거 |
|---|---|---|
| ① 문제 실재 | **FAIL** | flip 셀1 0.007 / 셀3 0.007 / 셀2 0.087 / 셀4 0.093 |
| ② 메커니즘 | **INDETERMINATE** | gap(cell1)=0.013, gap(cell2)=-0.093 — A-5 규칙: 격차 < 0.05 → 판정 불가 (PASS 격상 금지) |
| ②′ Recovery>Damage | **INDETERMINATE** | {'pass': None, 'status': 'N/A (L* 없음)'} |
| ②″ negative control | **PASS** | acc M 0.790 → Trel8 0.510, pooled p=2.39e-42 |
| ③ 컨트롤러 | **PASS** | layer8 식별률 0.928 (layer4 0.123는 측정만) |

## 표 1 — 조건 × 셀 (전체: results/table1.csv)

```
condition  acc_c1  acc_c2  acc_c3  acc_c4  acc_all  flip_c1  flip_c2  flip_c3  flip_c4  rec_c1  dam_c1     p_c1 bc_c1  rec_c2  dam_c2     p_c2 bc_c2 p_pooled
        S  0.9467  0.6467  0.9800  0.7200   0.8233      NaN      NaN      NaN      NaN     NaN     NaN      NaN   NaN     NaN     NaN      NaN   NaN      NaN
        M  0.9667  0.5667  0.9867  0.6400   0.7900   0.0067   0.0867   0.0067   0.0933     NaN     NaN      NaN   NaN     NaN     NaN      NaN   NaN      NaN
       T4  0.9600  0.5667  1.0000  0.6800   0.8017      NaN      NaN      NaN      NaN     0.0  0.0069 1.00e+00   1/0  0.0615  0.0471 1.00e+00   4/4      NaN
       T8  0.9533  0.6000  1.0000  0.7133   0.8167      NaN      NaN      NaN      NaN     0.0  0.0138 5.00e-01   2/0  0.0769  0.0000 6.25e-02   0/5      NaN
      T12  0.9533  0.5733  0.9933  0.6867   0.8017      NaN      NaN      NaN      NaN     0.0  0.0138 5.00e-01   2/0  0.0308  0.0118 1.00e+00   1/2      NaN
      T16  0.9533  0.5667  0.9933  0.6533   0.7917      NaN      NaN      NaN      NaN     0.0  0.0138 5.00e-01   2/0  0.0154  0.0118 1.00e+00   1/1      NaN
      T20  0.9667  0.5667  0.9867  0.6400   0.7900      NaN      NaN      NaN      NaN     0.0  0.0000 1.00e+00   0/0  0.0154  0.0118 1.00e+00   1/1      NaN
      T24  0.9733  0.5667  0.9867  0.6400   0.7917      NaN      NaN      NaN      NaN     0.2  0.0000 1.00e+00   0/1  0.0154  0.0118 1.00e+00   1/1      NaN
       T0  0.9800  0.4733  1.0000  0.6133   0.7667      NaN      NaN      NaN      NaN     0.4  0.0000 5.00e-01   0/2  0.0154  0.1765 5.19e-04  15/1      NaN
    Trel8  0.9533  0.0000  1.0000  0.0867   0.5100      NaN      NaN      NaN      NaN     1.0  0.0483 7.74e-01   7/5  0.0000  1.0000 5.17e-26  85/0 2.39e-42
```

## 이론 FLOPs 절감 (A-1: (N−L)/N, N=28)
{
 "T4": 0.40893762024398905,
 "T8": 0.3407813502033242,
 "T12": 0.27262508016265935,
 "T16": 0.20446881012199453,
 "T20": 0.13631254008132968,
 "T24": 0.06815627004066484
}
- 최적 L* = None 기준 절감: N/A

## 한 줄 결론
distractor flip 격차가 판정 기준 미달 (셀1 1% vs 셀3 1%, 셀2 9% vs 셀4 9%) · 판정 ②는 A-5 규칙상 INDETERMINATE (M→T(0) 격차 < 5%p) · layer 8 attention top-1 식별률 93%

## 이상 징후
- logit 동률(tie) 발생: 38건 (동률→no 사전 규정)
- stage3 M 예측 vs stage4 재예측 불일치: 0건 (분류 단일 소스 = stage 3)
- fig2 그룹 크기: {'M correct': 474, 'flipped': 14}

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