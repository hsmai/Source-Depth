# 향방 결정 문서 (초안) — 적대적 리뷰·베이스라인 위협·수용 기준 역산 종합

> ⚠️ 이 문서는 **검증 전 초안**이다. docs/13_verification_of_12.md의 정정을 반드시 함께 읽을 것.
> 특히 §0의 'method 트랙 사망'과 §2.1의 break-even은 검증에서 **논리 결함(F2)**이 지적됐다.

# SourceDepth 연구 향방 결정 문서
**작성 근거**: 자체 실측 결과 1–7(2026-08-11~12), 적대적 리뷰 9개 반론, FastV 계열 위협 분석, top-tier accept 프로파일 역산
**대상**: 지도교수 미팅 / 석사 진학 전 연구 방향 확정
**작성 원칙**: 낙관 편향 배제. 안 되는 것은 안 된다고 씀.

---

## 0. 한 문단 요약 (먼저 읽을 것)

지금 가진 것은 **"작동하는 방법"이 아니라 "왜 이 축이 작동할 수 없는지에 대한 잘 통제된 증거"**다. 헤드라인 +28.7%p는 oracle 조건이고, 비-oracle 현실 작동점은 3B +3.8%p / 7B −0.2%p다. 더 중요하게, **본인 데이터(결과 3 + 결과 4)만으로 계산하면 relational 질문 비중이 8.4%(3B) / 2.8%(7B)만 넘어도 이 방법은 무개입보다 나쁘다**(§2.1). 실제 multi-image 벤치마크는 relational 비중이 이보다 훨씬 높다. 따라서 **method paper 트랙은 이미 사망했다.** 반면 결과 5(attention 기반 image-relevance가 실은 position bias였고 순서를 뒤집자 99.8%→0.2%)와 결과 4(질문 유형에 따라 최적 depth의 부호가 뒤집힘)는 **최근 pruning 논문들이 공유하는 가정을 falsify하는 성격**이라 analysis paper의 핵심 기여로는 accept 라인에 근접한다. 권고: **Track A(analysis/negative-result)로 전면 전환**, 단 그 전에 §5의 1–2주차 kill test를 먼저 통과할 것.

---

## 1. 현 상태 냉정 판정

### 1.1 지금 결과 그대로 논문을 쓸 경우

| 급 | 확률 | 근거 |
|---|---|---|
| CVPR / ICCV / ICLR / NeurIPS **본회의** | **3%** | efficiency 트랙 accept 라인은 벤치 9–16개·baseline 2–4개·모델 3–4개(2계열 이상)·실측 wall-clock. 현재는 벤치 1.5개(자체 구성)·baseline 2개(자체 재구현)·모델 2개(단일 계열)·실측 9.7%. 세 축 모두 자릿수가 다름 |
| ACL / EMNLP **main** | **5%** | 동일 이유. NLP 계열도 multi-image 주장에 실제 multi-image 벤치를 요구함 |
| **EMNLP / ACL Findings** | **20–25%** | Findings는 "흥미롭지만 불완전"을 수용. 결과 5의 order-swap falsification이 살릴 가능성. 단 "7B에서 현상 소멸 + 이득 0"이 발목 |
| **워크숍** (CVPR/ICCV/NeurIPS workshop) | **70–80%** | 현 상태로 거의 확실히 통과. 다만 석사 진학용 실적으로는 약함 |
| arXiv only | — | 최소 보장선 |

### 1.2 판정 근거 — 지금 상태를 죽이는 것 3가지

**(a) 설계 공간이 공집합에 가깝다.** 논문의 thesis는 "질문 조건부 per-image depth 배분"이다. 그러려면 런타임에 "어느 이미지가 관련되는가"를 판정해야 한다. 결과 5가 보인 것은: 판정 가능한 최초 시점이 **L22**인데 개입이 효과를 갖는 구간은 **L≤16**이다. 이 시간 역전은 하이퍼파라미터 문제가 아니다. 그리고 oracle이 실제로 주어진다면 합리적 정책은 depth 배분이 아니라 **방해 이미지의 layer-0 완전 제거**(절감 최대·정확도 최대)이므로, oracle 하에서 depth 축의 존재 이유가 사라진다. 이 layer-0 상한 baseline이 보고되지 않은 것은 리뷰어가 가장 먼저 찌를 지점이다.

**(b) 효율 주장이 성립하지 않는다.** 이론 42.4% vs 실측 9.7%(배치 1 TTFT 510→461ms 단일 수치). 원인이 vision encoder가 여전히 두 이미지를 인코딩하기 때문이라면, 이는 구현 문제가 아니라 "프리필 도중 자른다"는 설계의 내재적 한계다. 비교 대상인 VisionZip은 prefill 7.8×, FastV는 1.58×를 실측으로 보고한다. 자릿수가 다르다.

**(c) 동기 현상이 스케일업으로 소멸한다.** flip rate 3B 21.3% → 7B 0.7%. 30배 감소는 "소형 모델 학습 부족 아티팩트" 가설을 강하게 지지한다. 이를 FOCUS 부록 D.1 / MVH-Bench 인용으로 메운 것은 "우리 세팅이 7B에게 너무 쉽다는 걸 알면서 더 어려운 조건으로 옮기지 않았다"는 자백으로 읽힌다.

### 1.3 그럼에도 죽지 않은 것

결과 5의 order-swap control은 **FOCUS / RSCD / MVH-Bench / FastV 계열이 수행하지 않은 통제**다. 이들은 attention mass를 image relevance의 증거로 사용하는데, 그것이 position prior일 수 있음을 순서 대칭 실험으로 보인 선행 연구를 확인하지 못했다(관련 증거: Feather the Throttle의 raster 위치 편향 80.7%, PoRe의 recency bias — 단 이들은 **image-level**이 아니라 **token-level** 위치 편향이다). **image 단위 position bias의 폭로는 아직 비어 있다.** 이것이 이 연구의 최대 자산이며, 이것 하나로 논문의 프레이밍이 바뀐다.

---

## 2. 본인 데이터로 계산한 두 개의 숫자 (미팅에서 반드시 제시)

### 2.1 ★ Mix break-even: relational 비중 8.4%에서 이득이 0이 된다

무개입 대비 J4x28의 이득을, 결과 3(non-relational)과 결과 4(relational)를 결합해 relational 비중 *p*의 함수로 쓰면:

- **3B**: non-rel `0.837 − 0.790 = +4.7%p`, rel `0.250 − 0.760 = −51.0%p`
  `net(p) = 0.047 − 0.557p` → **break-even p = 8.4%**
- **7B**: non-rel `0.802 − 0.790 = +1.2%p`, rel `0.540 − 0.950 = −41.0%p`
  `net(p) = 0.012 − 0.422p` → **break-even p = 2.8%**

BLINK, MuirBench, Mantis-Eval, NLVR2는 사실상 전부 cross-image relational이다. 즉 **실제 multi-image 벤치 분포에서 이 방법의 기대 이득은 크게 음수**다. (전제: 결과 4의 "4층 차단"이 J4x28의 방해측 정책과 동일하다는 가정 — 1주차에 직접 검증 필요.)

> 이 계산은 리뷰어가 하기 전에 우리가 먼저 해야 한다. 우리가 먼저 하면 "정직한 분석 논문"이고, 리뷰어가 먼저 하면 "숨긴 것"이다.

### 2.2 ★ Oracle이 사실은 상수(=위치)일 가능성

주 세팅은 `[원본][방해]` + "In the first image, is there X?"다. 이 구조에서 **관련 이미지는 항상 position 1**이다. 그렇다면 "oracle 컨트롤러"는 "항상 1번을 고른다"와 동일하고, 결과 5의 layer-8 식별률 99.8%가 순서를 뒤집자 0.2%로 붕괴한 것은 **컨트롤러의 실패가 아니라 데이터셋 설계의 필연**이다. 그리고 결과 3의 +28.7%p 중 얼마가 "배분 전략의 이득"이고 얼마가 "질문이 항상 1번을 가리킨다는 사전정보의 이득"인지 현재 분리되어 있지 않다.

**→ 관련 이미지 위치를 50/50으로 균형화한 재측정 없이는 결과 3·5의 어떤 숫자도 방어할 수 없다.** 이것이 1주차 최우선 과제다.

한편 결과 5의 layer-22 head 0.882는 selection-on-test지만, null 하 최대값 추정(576 후보, n=600, p=0.5 → 기대 최대 ≈0.57)을 크게 상회하므로 **head 자체의 존재는 실재**한다. 다만 0.882라는 값은 낙관 편향되어 있으므로 held-out 재측정 필요.

---

## 3. 결과별 가치 등급

| # | 결과 | (a) Novel한가 | (b) 리뷰어가 인정할 것인가 | (c) 논문에서의 역할 | 등급 |
|---|---|---|---|---|---|
| **1** | 3B 오염 21.3%, L4 차단으로 오답 81% 회복 (McNemar p=6e-7) | ✗ — MVH-Bench가 7B 오답의 87–94%를 이미 보고. 3B에서의 재현 | △ — 통계는 견고하나 "이미 알려진 것" | **Motivation §1의 1개 그림.** 기여로 주장하면 안 됨 | **C** |
| **2** | 7B에서 오염 소멸 (flip 0.7%) | ✗ (현상), ○ (스케일 대조로서) | ✗ 현재 형태로는 자기 논파. ○ 3스케일 이상으로 확장하면 scaling 발견 | **양날.** 정직하게 "이 현상은 스케일에 취약하다"로 쓰면 논문의 신뢰도 자산, 감추면 치명상 | **C→B** (모델 추가 시) |
| **3** | 동일 예산 배분 대결 +28.7%p / +8.7%p | △ — "예산을 token 수가 아니라 depth로" 치환은 문헌에 비어 있음 | **✗** — VTW16이 무개입(0.790)보다 24%p 낮은 0.550이므로 straw-man. random 배분·layer-0 제거·FastV 동일 FLOPs 대조군 전무. 7B +8.7%p는 CI 미보고 | **Oracle upper bound로만.** "방법의 성능"으로 제시 불가. §2.1과 함께 제시해야 정직 | **D (현재) → B (대조군 4종 추가 시)** |
| **4** | 질문 유형별 최적 depth 부호 역전 (3B −51.0%p, 7B −41.0%p) | **○** — V-Skip 계열은 *task별* depth skip, 여기는 **같은 forward 안에서 이미지별로 상반된 정책이 동시에 필요**함을 보임. 이 형태는 문헌에 없음 | **○** — 통제가 명확하고 효과 크기가 큼. 단 "동일 상대 깊이(44–67% vs 43–71%)"는 n=2·단일 계열이므로 **주장 아닌 관찰**로 써야 함 | **논문의 두 기둥 중 하나.** "왜 단일 depth 정책이 원리적으로 불가능한가"의 증거 | **A−** |
| **5** | 컨트롤러 = position bias (99.8%→0.2%), order-invariant head는 L22 | **○○** — FOCUS/RSCD/FastV 계열이 수행하지 않은 order-swap control. **image 단위** position bias 폭로는 미점유 | **○** — falsification이라 반박이 어려움. 단 §2.2(위치 고정 confound) 해소 + held-out 재측정 필수 | **논문의 중심.** Method의 실패가 아니라 **축의 구조적 제약(controllability gap)**으로 정식화 | **A** |
| **6** | CLIP 베이스라인 식별률 0.505 | △ — 결과지만 사소함 | ○ — 성실성 신호 | **결과 5의 보조 증거.** "이 신호는 시각 유사도로 복원 불가"의 근거 | **C+** |
| **7** | 실측 9.7% vs 이론 42.4%, 마스킹≡삭제 예측 100% 일치 | ✗ | **✗** efficiency 주장으로는 즉사. ○ 구현 동등성 검증으로는 유효 | **부록.** "왜 depth 축이 실측 이득으로 환산되지 않는가"의 정직한 회계. 단 "마스킹≡삭제"가 "차단≡이미지 부재"를 증명하지는 **않음** — 이 혼동은 반드시 철회 | **C (역할 재정의 시)** |

**추가로 반드시 수정할 프레이밍 오류**: "layer L 이후 KV 차단 = 그 이미지가 없는 것과 수학적으로 동일"은 **L=0에서만 참**이다. L>0이면 텍스트·타 이미지 표현이 layer 0..L−1 동안 이미 방해 이미지 정보를 흡수했다. 이 문장은 논문 전체의 인과 귀속("오염 제거")의 토대인데 성립하지 않는다. 표현 철회 + L=0 대조 측정으로 대체.

---

## 4. Oracle 문제 — 세 선택지

### (i) 컨트롤러를 풀어서 정면 돌파

| 항목 | 평가 |
|---|---|
| **성공 확률** | **10–15%** |
| **왜 낮은가** | 결과 5가 보인 시간 역전(판정 L22 > 개입 L≤16)은 구조적이다. CoViPAL도 "guidance layer가 pruning layer보다 깊어야 한다"를 독립 보고했다. 게다가 결과 6이 시사하듯 oracle이 데이터셋 메타정보(셀 1·4는 방해 이미지에도 질의 객체가 실존)에 의존한다면, 어떤 런타임 컨트롤러도 정보이론적으로 복원 불가 |
| **탈출 경로** | 별도 경량 router(prefill 전), L4–8 순서불변 head 조합, cross-image attention entropy, 또는 **판정 시점과 개입 시점을 분리한 2-pass 설계**(단 2-pass는 효율 이득을 대부분 소진) |
| **필요 자원** | 6–12개월, GPU 대량, 실패 시 산출물 0 |
| **타겟** | 성공 시 CVPR/ICCV/NeurIPS 본회의 |
| **판정** | **석사 인턴 단계에서 걸 도박이 아니다.** 단, Track A 논문의 §Future work에 "우리가 시도한 것과 실패 이유"로 남기면 그 자체가 기여 |

### (ii) Oracle을 전제하는 응용으로 재정의 (referring / user-specified 세팅)

| 항목 | 평가 |
|---|---|
| **성공 확률** | **25–30%** (main), 45% (Findings) |
| **논리** | "사용자가 대상 이미지를 지정한다"면 oracle은 정당한 입력이다. 문서 VQA, 멀티턴 이미지 대화, agentic tool-use(스크린샷 N장 중 특정 장 지시) 등에서 실재하는 세팅 |
| **치명적 약점** | **§1.2(a)의 반론이 그대로 살아 있다.** oracle이 진짜 주어지면 합리적 정책은 depth 배분이 아니라 **관련 없는 이미지를 layer 0에서 제거**하는 것이다. 이것이 J4x28을 이기면 depth 축의 기여는 0이다. 이 baseline을 이기지 못하면 (ii)는 성립 자체가 불가 |
| **살아날 조건** | 오직 하나 — **"관련 없는 이미지도 완전 제거하면 안 되고, 얕은 층에서는 필요하다"**를 실증하는 경우. 결과 4의 R1셀이 정확히 그 증거다(양쪽을 봐야 하는 질문에서 조기 차단이 −51%p). 즉 "지정된 이미지 = 깊게, 나머지 = 얕게, 그러나 0은 아니게"가 layer-0 제거를 이길 수 있다면 (ii)는 살아난다 |
| **필요 자원** | 1주차 layer-0 상한 실험이 게이트. 통과 시 8–10주 |
| **타겟** | WACV / BMVC / EMNLP main·Findings. CVPR 본회의는 어려움 |

### (iii) Analysis / negative-result 논문으로 전환, oracle을 upper bound 도구로 사용

| 항목 | 평가 |
|---|---|
| **성공 확률** | **30–35%** (CVPR/ICCV/ICLR 본회의), **45–55%** (ACL/EMNLP main), **75%+** (Findings) |
| **논리** | analysis 트랙에서 oracle을 **명시적 upper bound**로 쓰는 것은 정상 관행이다. accept된 프로파일 실례: *What's in the Image?*(CVPR'25 — 모델 2개, 벤치 3개, baseline 0개, 응용 1개), *Cross-modal Information Flow*(CVPR'25 — 자체 데이터셋, 방법 제안 없음), *Towards Interpreting Visual Info Processing*(ICLR'25 — 인과 ablation 중심) |
| **우리가 이미 가진 것** | 인과 개입 도구(KV 차단 + 역방향 대조 + McNemar) ✓ / falsification(order-swap 붕괴, CLIP 0.505) ✓ / 부호 역전이라는 강한 효과 크기 ✓ / 비대칭 페널티 정량화(오분류 시 0.79→0.50) ✓ |
| **부족한 것** | 모델 계열 1개 → 3개 필요, 벤치 1.5개 → 3개(MVH-Bench 필수) 필요, baseline 공식 재현 3개, downstream 데모 1개 |
| **필요 자원** | **12주, 추론 전용, PBS로 충분** (학습 없음). 가장 현실적 |
| **타겟** | 1지망 CVPR/ICCV, 2지망 ACL/EMNLP main, 안전망 Findings |
| **부수 효과** | 실패해도 "왜 안 되는지"가 산출물이라 **손실이 0인 유일한 트랙** |

---

## 5. 프레이밍 최종 권고

### 권고: **(iii) Analysis / negative-result 트랙.** (ii)는 1주차 결과에 따라 §7의 하위 섹션으로 흡수.

**이유 4가지**
1. §2.1의 break-even 8.4%가 method 트랙을 이미 죽였다. 이를 알고도 method로 밀면 리뷰어가 계산해서 desk-reject한다.
2. 이 연구의 최고 자산(결과 5의 order-swap, 결과 4의 부호 역전)은 **method의 실패이자 analysis의 성공**이다. 자산과 프레이밍이 정반대로 놓여 있었다.
3. Track A는 필요 작업이 유한하고(모델 2개 + 벤치 2개 + baseline 재현) 전부 추론 전용이라 12주에 실제로 끝난다.
4. 실패 시에도 워크숍/Findings가 확보되고, 그 과정에서 (i)에 필요한 신호 탐색이 자연히 진행된다.

### 제목 후보

1. **"Which Image, and How Deep? The Controllability Gap in Multi-Image LVLM Compute Allocation"** — controllability gap을 전면에. 가장 정직하고 기여가 명확.
2. **"Attention Mass Is Position, Not Relevance: Falsifying Image-Level Relevance Signals in Multi-Image LVLMs"** — falsification을 전면에. 임팩트 최대, 선행 연구와 대립각이 커서 리뷰 리스크도 최대.
3. **"No Single Depth Works: Question-Conditional Depth Requirements Are Sign-Reversed Across Images"** — 결과 4 중심. 안전하지만 임팩트 중간.
4. **"An Oracle You Cannot Build: Upper Bounds and Structural Limits of Per-Image Depth Allocation"** — negative result임을 제목이 선언. 리뷰어의 "왜 작동 안 하나" 공격을 무력화.

**권장: 1번을 주 제목, 2번의 부제 결합.**
> *Which Image, and How Deep? Attention Mass Encodes Position, Not Relevance — and the Controllability Gap It Creates in Multi-Image LVLMs*

### Abstract 초안 (1문단)

> Multi-image LVLMs waste compute on images irrelevant to the question, and prior work assumes that attention mass identifies which image matters. We test that assumption directly. Using KV-column blocking as a causal intervention on Qwen2.5-VL (3B/7B) over a controlled four-cell POPE-multi construction, MVH-Bench, and BLINK, we establish three results. **First**, per-image execution depth — not token budget — is a real and consequential axis: under an oracle that reveals which image the question concerns, reallocating an identical image-layer budget changes accuracy by up to 28.7 points, an effect no token-count pruning method can express. **Second**, the required depth is *sign-reversed* across question types within the same forward pass: an intervention worth +21 points on single-image queries costs 51 points on cross-image relational queries, so no single depth policy is safe; re-weighting to realistic benchmark mixtures drives the net gain negative beyond a relational fraction of only 8.4%. **Third**, and most consequentially, the oracle cannot be built from the signals the field currently uses. An attention-mass controller identifies the relevant image with 99.8% accuracy at layer 8 — but collapses to 0.2% when the two images are swapped, revealing that it has learned image position, not image relevance. Exhaustive search over all layers and heads finds an order-invariant signal only at layer 22, whereas interventions are effective only at layers ≤16. This *controllability gap* — the earliest layer at which relevance is decodable lies strictly after the last layer at which intervention helps — is a structural property of the attention-based dynamic-pruning family, not a failure of one implementation, and it is compounded by an asymmetric penalty: misidentifying the relevant image drops accuracy from 0.79 to 0.50. We report the oracle upper bound and the realized non-oracle operating point side by side (3B: +3.8 points; 7B: −0.2 points), and argue that order-swap controls should be a required diagnostic for any attention-based cross-image attribution claim.

**한국어 요지**: (1) per-image depth는 실재하는 축이고 oracle 상한이 크다 → (2) 그러나 질문 유형에 따라 최적 정책의 부호가 뒤집혀 단일 정책이 원리적으로 불가하며 실제 벤치 분포에서 이득은 음수 → (3) 그리고 그 oracle은 현재 분야가 쓰는 신호로는 만들 수 없다(position bias 폭로 + controllability gap). 상한과 실현치를 나란히 보고하고, order-swap control을 분야 표준 진단으로 제안.

---

## 6. 12주 실행 계획

> **원칙**: 프로젝트를 죽일 수 있는 실험을 가장 먼저 한다. 1–2주차 kill test를 통과하지 못하면 §7로 간다.

### Phase 0 — Kill test (1–2주차). **여기서 프로젝트의 생사가 갈린다.**

| 주 | 작업 | 막는 반론 |
|---|---|---|
| **W1** | **① 위치 균형화 재측정**: 관련 이미지를 position 1/2에 50:50 배치하고 결과 1·3·5 전부 재실행. **② layer-0 완전 제거 상한 baseline**을 모든 셀에서 측정. **③ random per-image depth 배분** 대조군(seed ≥5, bootstrap CI) | oracle=위치 confound(§2.2) / "oracle이 있으면 layer-0 제거가 최적" / "질문 조건부가 아니라 무작위여도 되는 것 아닌가" — **가장 치명적인 3개를 한 주에 처리** |
| **W2** | **④ Mix sensitivity 곡선**: relational 비중 0→100% 스윕, break-even 지점 명시(예상 3B 8.4%). **⑤ L=0 vs L>0 차단 곡선 비교** → "이미 흡수된 오염"의 크기 정량화. **⑥ "수학적 동일" 표현 철회** 및 인과 주장 재작성. **⑦ 모든 headline 수치에 bootstrap CI + McNemar** 부착 | mix gerrymandering / "차단=부재" 프레이밍 오류 / "7B +8.7%p는 노이즈" |

> **W2 종료 시점 게이트**: ③에서 random 배분이 J4x28과 CI 내에서 구분되지 않으면 → "질문 조건부"라는 주장이 소멸 → §7 발동. ②에서 layer-0 제거가 J4x28을 모든 셀에서 이기면 → depth 축 기여 0 → 프레이밍을 "controllability gap"만으로 축소.

### Phase 1 — 일반성 확보 (3–7주차)

| 주 | 작업 | 막는 반론 |
|---|---|---|
| **W3–4** | **모델 계열 확장**: LLaVA-OneVision-7B + InternVL3-8B 추가(총 4모델/3계열). 결과 4의 전환 구간(상대 깊이 44–67%)과 결과 5의 order-swap 붕괴를 전 모델에서 재현 | "n=2·단일 계열로 scaling law 주장" / "특정 모델 우연" — **여기서 상대 깊이가 재현되면 논문의 최고 문장이 되고, 재현 안 되면 관찰로 강등** |
| **W5** | **MVH-Bench 이식**(필수 — 우리가 인용하는 근거 벤치). RSCD와 직접 수치 비교 | "자기 motivation 벤치를 피했다" — 이 반론은 인용만으로 절대 막히지 않음 |
| **W6** | **BLINK + Mantis-Eval** 이식(non-binary 포맷, 자연 multi-image). 실제 question-type 분포 하 기대 이득 재계산 | "POPE yes/no 단일 포맷" / "합성 concat은 실제 multi-image 태스크가 아님" |
| **W7** | **스케일 확장**: 가능하면 32B급 1개에서 flip rate 재측정. 불가하면 "7B에서 소멸"을 명시적 scaling 발견으로 서술 + 더 어려운 조건(FOCUS D.1 재현)에서 7B 오염 재유도 | "동기 현상이 스케일업으로 소멸" / "인용으로 메웠다" |

### Phase 2 — 비교 및 진단 (8–10주차)

| 주 | 작업 | 막는 반론 |
|---|---|---|
| **W8** | **FastV 공식 코드 재현 + ★ 진단 측정**: FastV 적용 시 **layer별·이미지별 잔존 토큰 비율**을 직접 측정. **예측: 방해 이미지가 아니라 뒤쪽 이미지가 더 살아남는다.** 순서 스왑 양방향 실행 | "왜 FastV와 비교 안 했나" — 그리고 이 그림 한 장이 **논문의 motivation figure**가 됨(FastV의 기준은 relevance가 아니라 position임을 실증) |
| **W9** | **동일 실측 축에서 Pareto frontier**: prefill FLOPs / TTFT / peak KV memory 3축 모두에서 FastV·PyramidDrop·PLPHP·random pruning·원저자 VTW·우리 배분 비교. 예산 sweep 전 구간 | "image-layer는 자작 proxy" / "단일 작동점은 cherry-picking" / "random 80%도 +5% 오른다"(2503.20540) |
| **W10** | **직교성 실험**: FastV(token 축) + 우리 depth 배분 결합. 결합 이득이 각각을 초과하면 "직교 축"이 실증됨. **"FastV를 대체한다"가 아니라 "FastV가 볼 수 없는 축"으로 프레이밍**. 컨트롤러 held-out split 재평가 + permutation null 하 기대 최대값 보고 | "기존 축의 데카르트 곱" / "selection on test(576 후보에서 0.882 선택)" |

### Phase 3 — 집필 및 방어 (11–12주차)

| 주 | 작업 | 막는 반론 |
|---|---|---|
| **W11** | 실측 latency 전 작동점 재측정(하드웨어 명시, n≥20, CI, 배치 1/8/32, encoder/prefill/decode 분해). **encoder가 지배적이면 efficiency 주장 자체를 철회하고 부록으로 강등** | "이론 42.4% vs 실측 9.7%" / "배치 1 단일 수치" |
| **W12** | 집필. 모든 oracle 표에 "Oracle upper bound" 라벨. Limitation 섹션에 컨트롤러 실패를 **숨기지 않고 §4(핵심 결과)로 배치**. downstream 데모 1개(현실 작동점, 3B J20x28: −30.3% 비용 +3.8%p)를 숫자와 함께 | "abstract에 +28.7%p, §5에 −0.2%p" misleading claim |

---

## 7. 중단 기준 (이 중 하나라도 성립하면 방향을 접거나 축소한다)

| # | 조건 | 확인 시점 | 조치 |
|---|---|---|---|
| **S1** | **random per-image depth 배분**이 J4x28과 CI 내에서 구분되지 않는다 | **W1** | "질문 조건부 배분"이라는 주장 소멸. 논문을 **결과 5(position bias falsification) 단독**으로 축소 → 짧은 analysis paper 또는 workshop |
| **S2** | **layer-0 완전 제거**가 모든 셀에서 J4x28 이상 | **W1** | depth 축의 기여 0 확정. Track (ii) 폐기, "controllability gap" 논문만 유지 |
| **S3** | **위치 균형화 후** 결과 3의 이득이 절반 이하로 축소되거나 CI에 0 포함 | **W1** | 결과 3을 논문에서 제거하고 upper-bound 언급만. 논문의 축을 결과 4+5로 완전 이동 |
| **S4** | **MVH-Bench / BLINK에서 결과 4의 부호 역전이 재현되지 않는다** | **W5–6** | 결과 4는 자체 구성 데이터의 아티팩트. **논문 전체 중단**, workshop 제출로 마무리 |
| **S5** | **LLaVA-OneVision / InternVL3에서 order-swap 붕괴가 재현되지 않는다** | **W3–4** | position bias가 Qwen 고유 → falsification의 일반성 상실. 기여가 "Qwen 계열 관찰"로 축소 → Findings 이하 |
| **S6** | 누군가 6개월 내 동일 wedge("multi-image per-image depth")를 선점 발표 | 상시(월 1회 arXiv 서베이) | 즉시 arXiv 선공개. 이미 선점당했으면 order-swap control **하나만** 떼어 short paper |
| **S7** | W7까지 32B 또는 더 어려운 조건에서 7B 오염을 재유도하지 못함 | **W7** | "이 현상은 소형 모델 아티팩트"를 논문이 스스로 인정하고, 기여를 **efficiency가 아니라 interpretability/diagnostics**로 완전 이전 |

**추가 원칙**: S1–S3(1주차 kill test) 중 **2개 이상**이 동시 성립하면 12주 계획을 중단하고, 4주짜리 workshop paper(결과 4+5)로 축소한 뒤 다른 주제로 이동한다. 석사 진학 전 시간을 여기에 6개월 이상 태우지 않는다.

---

## 8. 교수님 미팅에서 받아야 할 결정 3가지

1. **트랙 승인**: analysis/negative-result 트랙(Track A) 전환에 동의하는가? 아니면 method 트랙을 유지하고 컨트롤러 정면 돌파(성공률 10–15%, 6–12개월)에 자원을 걸 것인가?
2. **자원 확보**: LLaVA-OneVision-7B / InternVL3-8B / 가능하면 32B급 1개에 대한 GPU 예산(PBS 큐, 추론 전용, 대략 200–400 A100-h 추정). 32B가 불가하면 S7 조치를 미리 합의.
3. **타겟 마감 확정**: CVPR(11월경) / ICCV / ACL·EMNLP 중 어느 데드라인을 12주 종점으로 잡을 것인가. 이것이 정해져야 W11–12의 압축 정도가 결정된다.

---

## 부록 — 반드시 고쳐야 할 문장 3개

| 현재 | 문제 | 수정 |
|---|---|---|
| "layer L 이후 KV 차단 = 그 이미지가 없는 것과 수학적으로 동일" | L=0에서만 참. 인과 귀속의 토대가 무너짐 | "L 이후 차단은 L 이전에 이미 흡수된 정보를 되돌리지 않는다. L=0 대조와의 차이가 그 흡수량이다" |
| "실제 토큰 삭제와 마스킹 예측 100% 일치" (프레이밍 검증으로 제시) | 구현 동등성만 검증. 프레이밍은 검증 안 됨 | 구현 동등성 검증으로만 서술, 부록 이동 |
| "동일 상대 깊이(3B 44–67% vs 7B 43–71%)" | n=2, 단일 계열, 동일 학습 레시피 | "두 스케일에서 유사한 상대 깊이가 관찰되었다. 일반 법칙 주장을 위해서는 다계열·다스케일 재현이 필요하다" (W3–4에서 해소되면 승격) |