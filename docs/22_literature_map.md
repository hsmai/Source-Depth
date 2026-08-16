# 선행연구 지도 — 무엇이 죽었고 무엇이 남았나

2026-08-14. 4축 병렬 조사(멀티이미지 환각 / negative attention / pruning·layer skipping /
layer 역할) + 고위협 논문 5편 적대적 검증.

## 위협 등급 상위 — 반드시 Related Work에서 정면으로 다뤄야 할 5편

| 논문 | 무엇을 하나 | layer 개입 | training-free | 우리와의 관계 |
|---|---|---|---|---|
| **FOCUS** (2508.13744) | "cross-image information **leakage**" 명명. 타깃 외 이미지를 **픽셀 노이즈**로 가리고 N+1회 forward → logit 대조 | **없음** (입력·출력 레벨) | **예** | **Qwen2.5-VL 3B/7B 동일 모델.** 우리 문제를 이름 붙여 선점. 단 attention/KV 레벨 아님, layer 분석 전무, 진짜 무관 distractor 세팅 미실험, 개선폭 +3.22%p |
| **MIMIC** (2601.07812) | layer 12–23에 block-diagonal mask (이미지 내부로만 attend). Finding 6: inter-image attention은 깊은 층에서 감소 | **예** (12–23) | **아니오** (LoRA 중 적용) | layer 선택이 attention 관찰 + 성능 ablation. **인과 국소화 아님**. 모든 inter-image를 **균일** 차단 |
| **CAPL** (2603.07048) | 이미지별 상위 에너지 토큰만 **양방향** cross-image attention 허용 + cross-image DPO | **예** (홀수 층 교대) | **아니오** (DPO 필수) | *"추론시 attention 수정만으로는 일시적 개선"*이라고 **선점 반론**. 방향이 **정반대**(열기 vs 막기) |
| **RSCD** (2603.23934) | 중간 층(Qwen 12–20)에서 **text→text** attention 상위 ρ% 차단 → contrastive decoding | **예** (12–20) | **예** | **layer sweep + 개입으로 critical layer 국소화**를 이미 함 → 우리 "인과 검증 방법론"은 새롭지 않음. 단 대상이 text→text |
| **SoFA** (CVPR 2025) | causal ↔ bidirectional mask를 σ로 보간, 2개 층마다 삽입 | **예** (2층 간격) | **예** | 추론시 inter-image attention을 layer 단위로 조절한 **직접 선행**. 방향은 역시 **열기** |

## 사망한 novelty 주장 — 덱에 쓰면 안 됨

| 주장 | 사망 이유 |
|---|---|
| ~~"training-free 추론시 개입"~~ | FOCUS·RSCD·SoFA 전부 training-free |
| ~~"layer 단위 개입"~~ | MIMIC·CAPL·RSCD·SoFA 전부 layer 단위 |
| ~~"인과 검증 방법론"~~ | RSCD가 이미 layer sweep + 개입 + 지표변화로 critical layer 국소화 |

## 살아남은 것 — 그리고 오늘 실험이 정확히 여기를 때렸다

**① image_i → image_j edge의 layer-resolved knockout이 문헌에 없다.**
기존 knockout 연구는 전부 **모달리티 간** edge(image→question, image→last, question→last)만
끊었다. "무관 이미지의 KV만 특정 층부터 차단 → 회복률" 곡선은 존재하지 않는다.
→ **우리 PART1(XIMG vs READ 분해)이 정확히 이것이다.**

**② 무관 이미지 **하나만** 골라 차단한 연구가 0편.**
존재하는 것: 균일 차단(MIMIC) / 개방(CAPL·SoFA) / 재분배(DAB) / text-to-text(RSCD) /
픽셀 노이즈(FOCUS). pruning 25편 중 interleaved 멀티이미지에서 **per-image 선택 게이팅**은 0편.

**③ 원인 진단의 부호가 반대다 — 이것이 새 novelty의 중심축.**
CAPL·SoFA = "cross-image 정보가 **부족**하다(position bias)" → attention을 **연다**.
우리 = "무관 이미지의 정보가 **오염**시킨다" → 선택적으로 **막는다**.
그리고 **CAPL은 무관 이미지 시나리오를 한 번도 실험하지 않았다.** 그 레짐이 비어 있다.

**④ training-free negative attention은 비어 있으나 이유가 있을 수 있다.**
GPAM = Generalized Probabilistic Attention Mechanism (arXiv 2410.15578) — softmax의 convex
결합을 affine으로 일반화해 음수 attention 허용, 합은 1 고정. **NLP 전용, 아키텍처 변경 + 학습 필요.**
Cog Attention·Diff Transformer도 동일. 학습 없이 softmax **이후** 분포에 음수를 넣으면 정규화가
깨진다(저자들이 불안정성·overflow 명시). → 우리가 할 수 있는 건 attention **logit**에 큰 음수를
주는 것이고, **그건 이미 우리 4D mask의 연속판(λ 스윕)이다.** 별도 novelty로 팔 수 없다.

## 오늘 실험과의 정합성 — 중요

우리 PART1 결과(이미지 간 attention 차단 시 3B −0.294 / 7B −0.422, **크게 나빠짐**)는
CAPL·SoFA가 attention을 **여는** 방향으로 간 것과 **일치**한다. 서로 모순이 아니다.

**새 주장**: 기존 연구는 두 경로를 구분하지 않았다.
- **image → image 혼합**: 도움이 된다 (막으면 −0.29 ~ −0.42)
- **text → image 읽기**: 해악이 **전부** 여기 있다 (막으면 +0.21, 전면 차단과 **완전 동일**)

**이 둘을 layer-resolved 인과 개입으로 분리한 연구는 없다.** 그것이 우리 기여다.
MIMIC이 "균일 차단"으로 얻은 개선도, CAPL이 "개방"으로 얻은 개선도, 이 분해로 설명된다.
