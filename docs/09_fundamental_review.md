# 근본 검토: 외부 리뷰에 대한 평가와 연구 방향 재정립

> 작성: 2026-08-11. 외부 검토문(novelty·타당성 비판)을 받아 수행한 자체 검증 결과.
> 방법: (1) 검토문이 인용한 선행연구 12편의 실존·내용을 웹 검색으로 전수 검증 (§4),
> (2) 검토문의 기술 논점을 Phase 0 실측 데이터로 재검증 (§2·§3), (3) 연구 질문 재정의 (§5~§7).

## 0. 요약 판정

**검토문의 대세 판단에 동의한다** — Phase 0은 "문제 실재 + oracle 개입의 인과 효과"를 입증했을 뿐,
"adaptive per-image depth"의 필요성과 비-oracle 컨트롤러의 실현성은 입증하지 못했다.
넓은 framing("visual token depth 절감 + hallucination 완화")은 선점 밀도가 높아 그대로는 논문이 되지 않는다.

단, 검토문이 놓치거나 과소평가한 지점이 4가지 있다 (§2). 이를 반영한 수정 결론:

- **살아남는 연구 질문** (검토문과 동일): *query-conditioned whole-image exit depth 배분이
  source attribution과 실측 latency의 Pareto frontier를 개선하는가*
- **진행 판단: 조건부 GO** — 2~4주 kill-gate 통과를 조건으로. 게이트별 구체 설계는 §6.
- 미팅 보고 스토리는 "원안 GO"가 아니라 **"현상·인과 입증 완료 → 논문 성립 조건 3개를 kill gate로
  설정하고 단기 검증"**으로 수정해야 한다 (§7).

## 1. 검토문 주장별 평가표

| # | 검토문 주장 | 평가 | 근거 |
|---|---|---|---|
| 1 | Phase 0은 문제 실재·oracle 개입 효과를 지지한다 | **동의** | 판정 ①·②″ 실측 |
| 2 | T0(84.5%) ≥ T4(84.2%)이므로 "중간 depth 필요성" 증거가 아니다 | **부분 동의 — 단 재해석 필요** | §2-A: 순수 distractor에서 T0가 최적인 것은 설계상 당연. 중간 exit의 가치는 정확도 우위가 아니라 **결정 신호의 가용 시점** (§2-A) |
| 3 | 컨트롤러 실패가 핵심 병목 — "빨리 판단하면 부정확, 늦으면 절감 없음" | **동의, 단 창이 비어있지 않음** | §2-B: layer 12–14 신호 75–77% + L=12–16 차단 recovery 83–86% — 간극이 좁은 실측 창 존재 |
| 4 | "depth = 혼합량" 단조 비례는 성립 안 함; 조기 전파 잔존 가능 | **표현 수정 동의, 단 실측은 우리 편** | §2-C: T4 recovery 81% = layer 0–3의 유해 전파가 실측상 무시 가능. "구조적 완전 차단" → "L 이후 직접 접근 차단"으로 수정 |
| 5 | 42.4%는 이론 상한 — 실측 latency·compaction 필요 | **전면 동의** | 브리프도 사전 명시. Gate 3 |
| 6 | 데이터 특화(2장·1번 위치 고정·ordinal 지시·unary·단일 모델) | **동의 — 이미 착수됨** | 순서 뒤집기·7B 재현 job이 hold 상태로 대기 중 (검토 전 제출 완료) |
| 7 | tie 104건 — 근소 margin이 결과를 좌우하는지 분석 필요 | **수행함 — 결과 혼합** | §3: 셀1 강건 / **셀2 역방향은 margin≥0.5에서 소멸** — 검토문 우려가 셀2에서 실증됨 |
| 8 | broad 주장 5개 폐기 필요 | **대체로 동의** | §5: 폐기 목록 확정 + 실제로 우리가 주장했는지 대조 |
| 9 | 선행연구 겹침 (MVPruner·VTW·ShortV 등 12편) | **검증 결과 §4** | 웹 전수 확인 |

## 2. 기술 논점 재검토 (Phase 0 데이터 기준)

### 2-A. "T0 ≥ T4" 논점의 재해석 — 파리티가 곧 실용성 논거다

검토문 지적대로 순수 distractor에서는 d=0(입력 제거)이 최선이며, 우리 데이터도 그렇다 (T0 84.5% ≥ T4 84.2%).
그러나 이 비교의 실용적 의미는 반대 방향이다:

- **d=0 차단은 forward 전에 관련성을 알아야 한다** — 외부 retriever/CLIP 등 추가 모듈·추가 연산 필요
- **중간 exit는 모델 자신의 forward에서 신호를 얻는다** — 추가 forward 없음
- 실측: T4~T16 구간이 T0와 통계적으로 동급 (셀1 acc 0.920~0.933 vs T0 0.933) →
  **"결정을 layer 4~16 사이 어디에서 내려도 정확도 손실이 없다"**는 것이 Phase 0의 실제 발견

즉 Gate 1(§6)은 "중간 depth가 T0를 이겨야 한다"가 아니라 이미지 유형별로 다르게 걸어야 한다:
distractor에는 **파리티**(입증됨), 부분 관련 이미지에는 **중간 최적점 존재**(미입증 — 신규 실험 필요),
relational에는 **full depth 필요**(미입증 — 신규 실험 필요).

### 2-B. 컨트롤러 trade-off — 창이 좁지만 비어있지 않다

검토문의 구조적 trade-off 지적은 정당하다. 실측으로 창의 크기를 재면:

| layer ℓ에서 판정 | naive 신호 식별률 (mean-head attention) | ℓ에서 exit 시 recovery (셀1) | 절감 (전체 prefill) |
|---|---|---|---|
| 4 | 15.5% | 81.0% (T4) | 42.4% |
| 8 | 72.5% | 83.3% (T8) | 37.1% |
| **12–14** | **75.0–77.0%** | **83.3–85.7% (T12–T16)** | **26.5–31.8%** |
| 21 | 99.0% | ~50% 이하 (T20 50%) | ~21% |

- layer 12–14: 신호 75–77%(naive feature 기준)에 recovery 83~86% — **판정 기준 80%에 3~5%p 부족**
- Phase 1의 정량 목표가 명확해짐: **layer ≤14에서 식별률 80%+를 주는 feature를 찾을 수 있는가**
  (mean-head 질량 → max-head, 누적 질량, delimiter hidden state, entropy 등 — 후보군 실험은 저비용)
- 실패 시 검토문 권고대로 축소/폐기 (§6 Gate 2)

### 2-C. "구조적 차단" 표현 수정 — 단, 실측은 조기 전파 미미를 보여줌

검토문: "L 이전에 text token으로 옮겨진 distractor 정보는 남는다" — 이론적으로 옳다. 그래서 실측을 보면:

- T4 recovery 81% → layer 0–3에서 일어난 유해 전파는 오답의 19% 이하
- fig1 플래토(T4~T16) → 유해 전파는 layer 16 이후에 집중
- **VTW의 "초기 층에서 visual→text 이동" 관찰과 우리의 "유해 혼합은 후반부" 실측은 상충하는 것이 아니라,
  '이동'과 '유해한 이동'이 다른 것임을 시사** — 이 대비 자체가 분석 논문 재료다 (§5)

표현은 수정한다: "KV 차단은 layer L 이후의 직접 참조를 제거한다. L 이전 간접 전파는 제거하지 않으며,
그 잔여 효과는 recovery 격차(19%)로 정량화된다."

## 3. 신규 분석: margin 민감도 (검토문 §6 요구 수행)

tie 104건(전 조건 합, 조건당 7~15건)·근소 margin 사례의 영향 (min|margin| of S/M/T4 기준 필터):

| min\|margin\| 필터 | Flip 셀1 (n) | Flip 셀2 (n) | Recovery T4 셀1 (n) |
|---|---|---|---|
| 없음 | 0.213 (150) | 0.127 (150) | 0.810 (42) |
| ≥ 0.25 | 0.214 (131) | 0.086 (128) | 0.829 (35) |
| ≥ 0.5 | 0.189 (111) | **0.010 (103)** | 0.778 (27) |
| ≥ 1.0 | 0.162 (74) | **0.000 (78)** | 0.857 (14) |

- **셀 1 (No→Yes 주 효과): 강건** — 확신도 높은 문항만 남겨도 flip 16~21%, recovery 78~86% 유지
- **셀 2 (Yes→No 역방향): 취약** — margin ≥ 0.5에서 사실상 소멸. 역방향 leak은 대부분
  결정 경계 근처의 calibration 흔들림으로 보인다. **"양방향이므로 yes-bias로 설명 불가"라는
  주장은 약화** — 주 증거는 셀1 단방향 + negative control로 재구성해야 한다

## 4. 선행연구 검증 결과 (웹 전수 확인 — 5 agent 병렬, arXiv/OpenReview/학회 페이지 원문 대조)

**결론: 검토문이 인용한 12편 전부 실존하며, 내용 요약도 10편 정확·2편 부분 정확.**
검토문은 신뢰할 수 있는 문서다. 상세 (원문 URL은 scratchpad/priorart.json):

| 논문 | 실존·venue | 검토문 정확도 | 실제 겹침 | 결정적 차이 (방어 논리) |
|---|---|---|---|---|
| **MVPruner** | ✅ arXiv:2606.27660, **ECCV 2026** | 정확 (세부 4주장 전부 사실) | **최대 위협.** layer별 task-relevant view 식별률 측정(Fig.2a — shallow 낮고 중간층 peak: 우리 layer-21 발견과 동일 패턴), instruction 기반 view별 예산 배분 | 예산 축이 **token 수** (모든 view가 전 layer 통과, depth 요소 전무 — HTML 전문 확인) vs 우리는 **실행 depth**. source-binding 목표 부재. 자율주행 동일-장면 6-view vs 일반 독립 multi-image. **인용 없이 layer별 식별 분석을 제시하면 치명적 — 반드시 인용·비교** |
| **VTW** | ✅ arXiv:2405.05803, AAAI 2025 | 정확 | layer-wise visual 조기 제거 (training-free) | 단일 고정 layer K에서 **전량 일괄** 제거, 이미지별 차등·멀티이미지·binding 전무. **주목: 실용 K=16 (32층 중)** — "초기 층 이동" rhetoric과 달리 실측 K는 우리의 "유해 혼합은 layer 16 이후" 경계와 정합 (상충 아님 — 방어 재료) |
| **ShortV** | ✅ arXiv:2504.00502, ICCV 2025 | 정확 (speedup 1.39~1.64× 사실) | layer별 visual 동결 + text 계속 처리 | 입력 무관 **정적·전역** 결정, 단일 이미지 efficiency. 구현 방식은 우리 저-depth 실행과 유사할 수 있어 인용 필요 |
| Do VLMs Need to Process Image Tokens? | ✅ arXiv:2604.09425, CVPR26 **워크숍** | 정확 | depth-wise truncation 분석, task-dependent 깊이 | 진단 논문, 단일 이미지·배분 방법 없음 |
| Late-Layer Fusion is Enough | ✅ arXiv:2606.09131, 저널 심사 중 | 정확 | 중간층 이후 visual 제외 | **trainable** (training-free 아님), 이미지 구분 없음 |
| Look Less Reason More (V-Skip) | ✅ arXiv:2606.08511, preprint | 정확 | training-free + task-dependent depth — 2026 4편 중 최근접 | 배분 단위가 task 전역, 이미지별 아님. baseline 비교 권장 |
| Attend, Transform, or Silence | ✅ arXiv:2606.31903, preprint | 정확 | operator 수준 layer skip | 이미지 구분 없음 |
| **PruneHal** | ✅ arXiv:2510.19183, ICLR26 **철회** | 정확 | KV pruning + hallucination 완화 조합 선례 | 단일 이미지·token-level·decoding-step 축, source-binding 무관 |
| **Attention Remasking** (Multiple Images Distract...) | ✅ OpenReview KFzVh70GhN, ICLR26 **철회** | **부분 정확** | 멀티이미지 + attention masking 골격, 이미지 간 오배분 진단 | 마스킹 단위가 **sink token(배경 patch)**, same-cost 재배분 (절감 없음), **depth 축 부재** (abstract 수준 확인 — 원문은 CAPTCHA로 미열람, 최종 확인 권장). "image-column masking과 가깝다"는 검토문 표현은 축·단위를 뭉뚱그린 과장 |
| FOCUS | ✅ arXiv:2508.13744 | 정확 | leakage 정의·완화 (제안서 기인용) | N+1 forward (계산 증가), depth 축 부재 |
| Delimiter Token Scaling | ✅ arXiv:2602.01984, **ICLR 2026 게재** | 정확 | delimiter attention 분석 + leakage 완화 | full depth, hidden-state scaling — depth 배분 아님 |
| **RSCD/MVH-Bench** | ✅ arXiv:2603.23934, **미게재 preprint** | **부분 정확** | **layer 범위(12/13–20) 선택적 masking + layer sweep 실재** — "depth 분석 최초" 무제한 주장은 유지 불가 (검토문 옳음) | 단 sweep 대상이 **text-to-text attention** (이미지 토큰 아님, 'leakage' 용어 미사용), 개입은 전 이미지 균일 + negative pass로 **계산 +10% 증가**. "**per-image 실행 depth 관점의 leakage 측정 + 계산 절감 배분**"으로 좁히면 novelty 문장 성립 |

**교차 발견**: MVPruner Fig.2(a)의 "관련 view 식별은 shallow에서 낮고 중간층에서 peak" — 우리의 layer별 식별률 실측(layer 4 15.5% → layer 21 99%)과 독립적으로 동일한 패턴. 우리 발견의 신빙성은 높이지만 해당 분석의 novelty는 낮춘다 (Gate 2 설계 시 인용 필수).

## 5. 살아남는 기여 재정의 / 폐기할 주장

**폐기 (검토문 동의):**
- "visual token 실행 depth 절감 최초" — VTW/ShortV 등 선점
- "KV pruning으로 hallucination·비용 동시 개선 최초"
- "layer별 cross-image leakage 최초 분석" — RSCD 등과의 관계 §4 확인 후 표현 확정
- "depth = 혼합량" (단조 비례 함의) → 인과 실측 표현으로 교체
- "구조적으로 완전 차단" → §2-C 표현으로 교체

**살아남는/재정의된 기여 후보:**
1. **Blocking-depth sweep에 의한 유해 혼합의 depth 국재화** — "distractor 오염은 후반 layer(≥16)에서
   발생하며 앞 16층 혼합은 무해"의 인과적 실측 (mask 개입 + negative control). '이동'(VTW)과
   '유해한 이동'(우리)의 구분.
2. **Query-conditioned whole-image exit** — 이미지 단위 routing + 이미지별 상이한 exit depth +
   source-binding 목표의 조합 (검토문도 "정확한 조합의 직접 중복은 미확인"). 단 조합 novelty이므로
   §6 게이트의 실증 강도가 필수.
3. Pareto frontier 실증 (accuracy × 실측 TTFT/latency) — Gate 3 통과 시.

## 6. Kill Gates (2~4주, 각 게이트 실패 시 대응 사전 등록)

**Gate 1 — 중간 depth의 필요성** (1주)
- 신규 데이터: (a) 부분 관련 이미지(질문 객체와 같은 장면 유형이지만 대상 아님), (b) relational 질문
  (MuirBench 파생 또는 2이미지 비교 구성), 각 150문항 내외
- 통과 기준: 이미지 유형 × 최적 depth가 {0, 중간, full}로 실제 갈림 (relational에서 T0/T4가 full 대비 유의 하락 확인 포함)
- 실패 시: per-image depth 폐기 → "image selection + 후반부 유해성 분석" 논문으로 축소

**Gate 2 — 비-oracle 컨트롤러** (1~2주, Gate 1과 병렬 가능)
- 순서 counterbalance된 2~6장 세팅에서 layer ≤14 feature로 식별률 80%+ (§2-B 후보 feature 스윕)
- 비교선: CLIP relevance, instruction-aware attention score 계열
- 지표: 식별률, unsafe skip rate, controller overhead
- 실패 시: oracle causal-analysis 논문으로 대폭 축소 또는 중단

**Gate 3 — 실측 속도** (1주, Gate 1·2 통과 시에만)
- mask 등가가 아닌 실제 sequence compaction 구현 → TTFT·end-to-end latency·peak VRAM·throughput
- 비교선: VTW, ShortV (동일 accuracy 또는 동일 FLOPs 조건)
- 실패 시(절감 미미): 방법 재설계 또는 중단

**공통**: 지금 hold 중인 확장 실험(순서 뒤집기 = Gate 2의 선행 체크, 7B = 일반화)은 게이트 착수 전
저비용으로 완료해 두는 것이 유리 (이미 제출된 상태, A6000 수 시간).

## 7. 미팅 스토리 수정 제안

기존 "GO — 원안 진행" 슬라이드 9·10을 다음으로 교체:

- 슬라이드 9: "Phase 0이 입증한 것 / 입증하지 못한 것"의 정직한 2단 구분
  (입증: 문제 실재·인과·depth 국재화·회복-절감 동시 달성 가능성 / 미입증: adaptive depth 필요성·비-oracle 컨트롤러·실측 속도)
- 슬라이드 10: 선행연구 지형 요약 (§4 표) + **kill gate 3개와 2~4주 일정** + 게이트별 실패 시 대응
- 메시지: "6개월을 걸기 전에 성립 조건 3개를 단기에 검증하는 계획" — 교수님 관점에서 더 신뢰 가능한 구성
