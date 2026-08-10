# SourceDepth — 연구 개요

> 원 제안서: [SourceDepth_proposal.pdf](reference/SourceDepth_proposal.pdf) (IMML Lab 인턴 한상민, 2027년 상반기 submission 목표)
> 이 문서는 제안서 PDF의 내용을 텍스트로 정리한 것이다. 실험 실행 지시서는 [01_feasibility_brief.md](01_feasibility_brief.md) 참조.

## 1. 한 줄 요약

멀티이미지 LVLM에서 **이미지별로 실행 depth를 다르게 배분**하여, 계산을 줄이면서 동시에 cross-image 정보 오염(source-binding error)을 구조적으로 차단하는 **training-free** 방법.

## 2. 핵심 문제

여러 장의 이미지가 입력으로 들어가면, 모델이 **어느 이미지에서 추출한 정보인지 혼동**한다.

- 현상: 단일 이미지 대비 멀티 이미지에서 성능이 유의하게 하락
- 선행 명명: cross-image information leakage (FOCUS, 2025), multi-view hallucination (MVH-Bench, 2026)
- 예시: [이미지1: 파란 모자] [이미지2: 빨간 모자] + "1번 사람의 모자 색은?" → 모델 답: "빨간색" (2번에서 온 정보)

## 3. 핵심 관찰: Depth = 이미지 간 정보가 섞이는 통로

Transformer에서 서로 다른 이미지의 토큰이 섞이는 **유일한 통로는 layer마다 한 번씩 일어나는 self-attention**이다. 따라서:

- 실행 layer 수 = 이미지 간 정보가 섞일 수 있었던 횟수 (**depth가 곧 혼합량**)
- 이미지 I_j의 토큰을 layer L 이후 KV에서 제거하면, layer L+1~32에서 어떤 토큰도 I_j를 참조할 수 없다
  → 근사적 억제가 아니라 **구조적 차단** (KV cache의 구멍 = leakage 차단)

## 4. Depth의 양날 — 질문 유형에 따라 필요한 깊이가 정반대

| 질문 유형 | 필요한 혼합 | 고정 depth의 결과 |
|---|---|---|
| Unary ("1번 자동차 색은?") | 최소 | 과잉 혼합 → source-binding 오류 |
| Relational ("어느 쪽이 큰가?") | 필수 | 적정 |
| Distractor 이미지 존재 | 0 | 무관 이미지 개입 |

- **Type A (깊어야 맞는 경우)**: 두 이미지를 섞어야 비교 가능 — 깊이가 답을 만든다
- **Type B (얕아야 맞는 경우)**: 얕은 layer에서는 정답이었다가, 깊어지며 다른 이미지 정보가 섞여 오답으로 뒤집힘 — 깊이가 답을 망친다

**형식화**: min E[Σᵢ c(dᵢ)] s.t. P(source-binding error) ≤ α
— Unary 질문에서는 얕게 계산하는 것이 **더 싸면서 동시에 더 정확**할 수 있다.

## 5. 기존 연구 지형 — 전부 'full depth' 전제

| 연구 | 개입 지점 | 비용 | depth |
|---|---|---|---|
| FOCUS (2025, arXiv 2508.13744) | 입력 마스킹 | N+1 forward | full |
| Delimiter Token Scaling (ICLR'26) | 토큰 hidden state | 1 pass | full |
| RSCD / MVH-Bench (2026) | attention 마스킹 | 1 pass + α | full |
| Looking Back and Forth (2026) | attention + DPO | 학습 필요 | full |
| STEAR (2026, 비디오) | layer-aware evidence 주입 | 계산 추가 | full |
| AdaSkip / FlexiDepth / Reroute / DARE | depth·토큰 생략 | 절감 | (단일 이미지, 효율 목적) |

**실행 depth 자체를 이미지별로 배분하는 연구는 2026.08 기준 없음.**

## 6. 차별점 (3가지)

1. **관측**: leakage가 어느 depth에서 생기는지 측정한 연구가 없음 (전부 full depth 전제)
2. **메커니즘**: 이미지 I_j를 layer l에서 생략하면 그 layer에서 아무도 I_j를 참조할 수 없음 → KV cache의 구멍이 곧 잘못된 이미지 정보의 leakage 차단
3. **비용 방향**: FOCUS는 N+1 forward, Ours는 **1 forward pass 미만** 목표

## 7. 후보 Method: Per-image depth

1. 초기 layer 4개만 실행하여 (추가 forward 없이) 이미지별 **질문 관련도** 추정 (예: 0.7 / 0.1 / 0.2)
2. 관련도에 따라 이미지별 실행 깊이 배분 (예: L32 / L8 / L14)
3. 최종 답변은 관련 이미지 기준 full depth로 생성 — 막대 높이 = 해당 이미지 토큰이 통과하는 layer 수

## 8. 핵심 기여 (논문 기준)

1. **Depth as leakage channel**: leakage 발생 depth 구간의 최초 측정 + activation patching 인과 검증
2. **Source-attribution risk 신호**: 추가 연산 없이 오류를 예측
3. **Per-image adaptive depth**: 이미지별 실행 깊이 배분
4. **보증 있는 계산 배분**: 휴리스틱 threshold 기반 기존 skipping과의 구분점

신규 지표: Source-Binding Error Rate / Relation Preservation / Unsafe Skip Rate / Recovery Rate

## 9. 본 연구 로드맵 (6개월)

| 목적 | 데이터셋 |
|---|---|
| 멀티이미지 종합 | MuirBench, MIRB, Mantis-Eval |
| Source-binding 직접 평가 | MVH-Bench |
| 통제 실험 | MuirBench 파생 4종 split (순서 / minimal-pair / distractor / relation) |
| 일반 능력 보존 | MMBench, MMMU 서브셋 |

- 모델: Qwen2.5-VL-3B/7B (주) + LLaVA-OneVision-7B (교차 검증), 최소 2개 계열
- 컴퓨트: **학습 없음**, 총 400–1,000 GPU-hour, 2–4 GPU

## 10. Risk / 중단 기준

| 리스크 | 완화책 |
|---|---|
| Unary 질문에서 '얕을수록 정확한 구간' 없음 | **2개월차 go/no-go.** 없으면 "FOCUS와 동일 성능을 1/N 비용으로" 시스템 논문으로 pivot (MLSys·EMNLP) |
| 실측 latency가 안 줄어듦 | 1개월차 확인. prefill 단계/이미지 단위로만 제한 구현 |
| Baseline 재현 비용 | 재현 일정 선반영 |

분기: **Type-B 사례(얕게 멈출 때 오히려 더 정확한 구간)가 존재하는가?** → 있음: 원안 진행 (신뢰성 제약형 depth 배분, CVPR·ICLR) / 없음: 효율 논문 pivot

## 11. 현 단계 (Phase 0): 24h Feasibility Check

교수님 보고용 정량 수치 3개를 24시간 안에 산출한다. 상세 설계는 [01_feasibility_brief.md](01_feasibility_brief.md) — **설계 변경 금지**.

| # | 입증할 주장 | 산출할 수치 |
|---|---|---|
| ① | distractor가 답을 오염시킨다 (문제 실재) | 조건별 Flip Rate 격차 |
| ② | 후반 layer KV 차단이 오염을 회복시킨다 (메커니즘 작동) | 정답률–차단깊이 L 곡선 |
| ③ | 얕은 layer attention으로 관련 이미지 식별 가능 (컨트롤러 실현성) | layer 4/8 attention top-1 식별률 |

전부 **oracle 세팅** (어느 이미지가 관련 있는지 알고 시작) — 컨트롤러 성능과 가설을 분리해 가설만 격리 검증.
