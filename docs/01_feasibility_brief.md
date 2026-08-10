# SourceDepth — 24h Feasibility 실험 실행 브리프

> 이 문서는 Claude Code가 단독으로 실험을 완주할 수 있도록 작성된 실행 지시서다.
> **설계를 임의로 변경하지 말 것.** 막히면 대안을 실행하지 말고 "BLOCKED" 로그를 남기고 보고할 것.
> 모든 수치는 실제 실행 결과만 기록한다. 실패·부정적 결과도 그대로 보고한다. 수치 추정/보간/날조 절대 금지.

---

## PART A. 연구 배경 (이 실험이 무엇을 위한 것인지)

### A-1. 연구 주제: SourceDepth (가칭)

멀티이미지 LVLM에서 **이미지별로 실행 depth를 다르게 배분**하여, 계산을 줄이면서 동시에 cross-image 정보 오염(source-binding error / leakage)을 차단하는 training-free 방법.

**핵심 관찰**: Transformer에서 서로 다른 이미지의 토큰이 섞이는 유일한 통로는 layer마다 한 번씩 일어나는 self-attention이다. 따라서:

- 실행 layer 수 = 이미지 간 정보가 섞일 수 있었던 횟수
- 이미지 I_j의 토큰을 layer L 이후 KV에서 제거하면, layer L+1~32에서 어떤 토큰도 I_j를 참조할 수 없다 (근사 억제가 아니라 구조적 차단)

**가설**: 질문과 무관한 이미지(distractor)의 KV를 후반 layer에서 차단하면,
(a) 답변 토큰의 연산 깊이는 32층 그대로 유지되면서
(b) distractor 유발 오답이 회복되고
(c) distractor 토큰의 후반 layer 연산이 절감된다.

**기존 연구와의 차이**: FOCUS(2508.13744)는 이미지 N장에 N+1회 forward pass로 마스킹 대조를 수행. RSCD, Delimiter Token Scaling 등도 전부 full depth 실행 후 개입. 실행 depth 자체를 이미지별로 배분하는 연구는 2026.08 기준 없음.

### A-2. 이번 미션의 위치

본 연구 6개월 로드맵의 **0단계: feasibility check**. 교수님 보고용 정량 수치 3개를 24시간 안에 산출한다.

| # | 입증할 주장 | 산출할 수치 |
|---|---|---|
| ① | distractor가 답을 오염시킨다 (문제 실재) | 조건별 Flip Rate 격차 |
| ② | 후반 layer KV 차단이 오염을 회복시킨다 (메커니즘 작동) | 정답률–차단깊이 L 곡선 |
| ③ | 얕은 layer attention으로 관련 이미지 식별 가능 (컨트롤러 실현성) | layer 4/8 attention top-1 식별률 |

이번 실험은 **전부 oracle 세팅**이다: 어느 이미지가 관련 있는지 알고 시작한다(질문이 "첫 번째 이미지"를 명시). 컨트롤러 성능과 가설을 분리해 가설만 격리 검증한다.

---

## PART B. 실험 설계 (변경 금지)

### B-1. 데이터: POPE + COCO distractor, 4셀 설계

POPE(COCO 기반, random/popular/adversarial 중 **adversarial split 우선**) 문항을 가져와, 원본 이미지 뒤에 distractor 이미지 1장을 붙인다.

- 입력: `[이미지1=원본][이미지2=distractor] + "In the first image, is there a {object}? Answer with Yes or No."`
- 정답: 이미지1 기준 원래 POPE 정답

**4셀 구성 (셀당 150문항, 총 600):**

| 셀 | 이미지1 정답 | distractor 조건 (COCO annotation으로 판정) | 역할 |
|---|---|---|---|
| 1 | No | 해당 객체 **포함** | 주 leak 측정 (No→Yes 뒤집힘 예상) |
| 2 | Yes | 해당 객체 **미포함** | 역방향 leak 측정 (Yes→No 뒤집힘 예상) |
| 3 | No | 해당 객체 미포함 | 셀 1 대조군 |
| 4 | Yes | 해당 객체 포함 | 셀 2 대조군 |

**4셀인 이유**: POPE 모델은 yes-bias가 있어, context 축소가 캘리브레이션만 흔들어도 No 정답률이 변한다. 셀 1(No→Yes)과 셀 2(Yes→No)는 **서로 반대 방향**이므로, T(L)이 양쪽을 모두 회복시키면 단일 편향으로 설명 불가 → leakage 차단의 증거가 된다.

**distractor 선정 규칙**: 같은 COCO supercategory의 다른 이미지에서 무작위 추출하되, 셀 조건(객체 포함/미포함)을 instances_val2014.json으로 검증. 원본과 동일 이미지 금지.

### B-2. 조건 (문항당 총 10회 forward)

| 조건 | 설명 |
|---|---|
| S | 이미지1 단독 (원본 POPE 형식, "In the image, ..." 문구) — 참조 상한 |
| M | 2장, full depth — **baseline** |
| T(L), L ∈ {4, 8, 12, 16, 20, 24} | 2장, **distractor** 토큰의 KV를 layer L 이후 차단 |
| T(0) | 2장, distractor 전 layer 차단 — FOCUS식 완전 마스킹 상한 |
| **T-rel(8)** | 2장, **원본 이미지** 토큰을 layer 8 이후 차단 — **negative control** (정답률 폭락해야 정상) |

주의: S와 T(0)는 position layout이 달라 완전 일치하지 않는다(허용 오차 존재). **핵심 비교군은 M / T(L) / T(0)로, 셋은 동일 layout을 공유한다.** S는 참조용이다. 이 비대칭을 "고치려" 하지 말 것.

### B-3. 평가: 생성 없이 logit 비교

Generation loop를 돌리지 않는다. 프롬프트 마지막 위치의 next-token logits에서 "Yes" 계열 토큰과 "No" 계열 토큰의 logit을 비교해 예측을 정한다.

- 토크나이저 주의: "Yes"/" Yes"/"yes" 등 변형이 있을 수 있음. **실제 모델이 이 프롬프트에서 어떤 토큰을 내는지 소량 생성으로 먼저 확인**하고, Yes/No 각각의 대표 토큰 id 집합을 확정한 뒤 logit 최대값 비교로 통일할 것. 확정한 토큰 id를 REPORT에 기록.

### B-4. 지표

- **Accuracy** (조건별 × 셀별)
- **Flip Rate**: M에서 S 대비 답이 뒤집힌 비율 (셀 1: No→Yes, 셀 2: Yes→No)
- **Recovery Rate**: M 오답 → T(L) 정답 비율 / **Damage Rate**: M 정답 → T(L) 오답 비율
- **통계 검정**: 조건 간 비교는 동일 문항 paired 구조이므로 **McNemar 검정** 사용. p값을 표에 병기.
- **이론 FLOPs 절감**: distractor 토큰 수 × (32−L)/32 를 전체 prefill 연산 대비 비율로 해석적 계산 (실측 latency는 측정하지 않는다 — mask 등가 구현이므로 의미 없음. REPORT에 그 이유 명시)

### B-5. 프로파일링 (M 조건 실행에서 함께 수집)

M 조건을 돌릴 때 각 layer에서, 마지막 프롬프트 토큰(답변 예측 위치)의 attention이 [이미지1 구간 / 이미지2 구간 / 텍스트 구간]에 준 질량 합을 저장한다 (head 평균).

- 산출: layer(x축) vs 이미지1·이미지2 attention 질량(y축) 곡선. **정답 케이스와 뒤집힌 케이스를 분리해** 두 곡선 세트.
- ③ 신호 식별률: layer 4와 layer 8 각각에서, 두 이미지 중 attention 질량이 큰 쪽이 이미지1(관련 이미지)인 비율.

---

## PART C. 구현 지침

### C-1. 모델·환경

- 모델: `Qwen/Qwen2.5-VL-3B-Instruct`, BF16, `attn_implementation="eager"` (custom mask + attention 추출에 필수. SDPA/flash는 4D mask나 attn 출력이 제한될 수 있음)
- transformers 최신 + qwen-vl-utils. 이미지 해상도는 기본 프로세서 설정 사용(임의 축소 금지, 단 OOM 시 `max_pixels` 제한은 허용하되 REPORT에 기록)
- GPU 사전 점검: `nvidia-smi`로 카드·VRAM 확인 후 배치 크기 결정 (3B BF16 ≈ 8GB + activation. 24GB 카드면 배치 4~8, OOM 시 배치 1까지 낮춤)
- GPU가 없으면 즉시 BLOCKED 보고 (CPU 실행 시도 금지 — 시간 초과 확정)

### C-2. 데이터 준비

- POPE: 공식 repo(github.com/RUCAIBox/POPE)의 `coco_pope_adversarial.json` (부족 시 popular로 보충)
- COCO: `instances_val2014.json` annotation + **필요한 이미지 파일만 개별 다운로드** (`http://images.cocodataset.org/val2014/COCO_val2014_{id:012d}.jpg`). val2014 전체 zip(~6GB) 다운로드 금지 — 필요 이미지는 600문항 × 2장 ≈ 최대 1,200장 미만
- 4셀 페어링 스크립트: 셀 조건 충족 여부를 annotation으로 검증하고, (question_id, image1_id, image2_id, cell, gt) 목록을 `pairs.csv`로 저장

### C-3. KV 차단의 등가 구현: layer별 attention mask

실제로 KV 계산을 생략하지 않는다. **layer > L에서 모든 query가 distractor 토큰 위치(key 열)에 attention하지 못하도록 additive mask에 −inf를 넣는다.** 아무도 참조하지 않는 KV는 존재하지 않는 것과 수학적으로 동일하다(softmax 분모에서도 제외됨). 품질 효과는 정확히 같고, 연산 절감은 B-4의 해석적 계산으로 대체한다.

- 각 이미지의 토큰 구간은 `<|vision_start|>`/`<|vision_end|>` (또는 image pad 토큰) 위치를 input_ids에서 찾아 특정. **구간 인덱스를 로그로 남기고 첫 3개 샘플은 수동 확인 가능한 형태로 출력**
- 구현 방식: 각 decoder layer forward에 hook을 걸어, layer index ≥ 임계값일 때 attention_mask(4D additive)에 해당 열 −inf 추가. 또는 attention forward monkey-patch. 어느 쪽이든 **layer index를 정확히 세는 것**이 관건
- M-RoPE/position id는 건드리지 않는다 (토큰은 자리 유지, 참조만 차단)

### C-4. Sanity check 3종 — 통과 전 본 실험 진입 금지

1. **T(0) vs S**: 셀 3·4 각 30문항에서 예측 일치율 ≥ 90% (position layout 차이로 100%는 아님. 70% 미만이면 mask 구현 버그로 간주하고 중단·디버그)
2. **"first image" grounding**: 20문항 소량 생성으로 모델이 실제로 이미지1에 대해 답하는지 육안 확인용 로그 저장. 실패 시 fallback 프롬프트("Picture 1: <image>\nPicture 2: <image>\n..." 텍스트 라벨 명시) 시도, 그래도 실패면 BLOCKED 보고
3. **S 정답률**: 원본 POPE 보고치(3B급 모델 ~80%대)와 크게 다르지 않은지 확인. 60% 미만이면 평가 파이프라인 버그 의심

### C-5. 실행 순서·시간 상한

| 단계 | 내용 | 상한 |
|---|---|---|
| 1 | 환경·모델·데이터 준비, pairs.csv | 3h |
| 2 | mask hook 구현 + sanity 3종 | 4h |
| 3 | 본 실험: 10조건 × 600문항 logit 평가 → `results.csv` | 5h |
| 4 | M 조건 attention 로깅 재실행 → 프로파일링·③ | 3h |
| 5 | 분석·그림·REPORT.md | 3h |
| 버퍼 | 실패 대응 / distractor 2장 확장(여유 시에만) | 6h |

각 단계 시작·종료 시각을 로그에 남길 것. 단계가 상한 1.5배를 넘으면 하위 항목을 줄여서라도 다음 단계로 진행 (단, sanity 미통과 상태로 본 실험 진행은 금지).

---

## PART D. 판정 기준 (사전 등록 — 결과 보고 바꾸지 않는다)

| 판정 | 기준 |
|---|---|
| ① 문제 실재 | 셀 1에서 M의 Flip Rate ≥ S 대비 +10%p, 그리고 셀 3에서는 그 절반 미만. 셀 2에서도 같은 패턴(역방향) |
| ② 메커니즘 작동 | 어떤 L에서 T(L)이 [M → T(0)] 격차의 50% 이상 회복 (셀 1·2 모두에서, McNemar p<0.05) |
| ②′ Type-B 실증 | 그 L에서 Recovery Rate > Damage Rate |
| ②″ 인과 확인 | T-rel(8)에서 정답률이 M 대비 유의하게 **하락** (negative control 성립) |
| ③ 컨트롤러 가능성 | layer 8 attention top-1 식별률 ≥ 80% |

**실패 시 대응 (이 순서로만, 각 1회):**
- ①이 안 나오면: (a) distractor를 동일 supercategory + 시각 유사 이미지로 교체, (b) distractor 2장으로 증가. 그래도 안 나오면 "3B에서 leakage 미미"를 결과로 보고 (이것도 유효한 발견이다)
- ②가 안 나오면: L 그리드를 {2,4,6,8,10,12}로 세분화해 1회 재탐색. 그래도 없으면 그대로 보고 (연구는 효율 방향으로 pivot — 그 판단은 사람이 한다)

---

## PART E. 산출물 (전부 필수)

1. `pairs.csv` — 문항·이미지 페어링 명세
2. `results.csv` — 문항 × 조건별 예측·정오 (raw)
3. `fig1_accuracy_vs_L.png` — x=차단깊이 L, y=정답률. M 수평선·T(0) 수평선·T-rel(8) 점 포함. 셀 1·2 분리 패널. **대표 그림**
4. `fig2_attention_profile.png` — layer별 이미지1/이미지2 attention 질량. 정답 vs 뒤집힘 케이스 분리
5. `REPORT.md` — 다음 구조 고정:
   - 실행 환경 (GPU, 소요 시간, 확정한 Yes/No 토큰 id)
   - Sanity 결과 3종
   - 판정표 (PART D의 5개 기준 각각 PASS/FAIL + 근거 수치)
   - 표 1: 조건별 × 셀별 Accuracy / Flip / Recovery / Damage / McNemar p
   - 이론 FLOPs 절감률 (최적 L 기준)
   - 한 줄 결론 (예: "distractor 유발 오류의 X%가 layer L* 이후 차단만으로 회복, distractor 토큰 연산 Y% 절감")
   - 이상 징후·한계·BLOCKED 목록 (없으면 "없음"이라고 쓸 것)

## PART F. 원칙

- 설계 변경 금지. 개선 아이디어가 있으면 REPORT의 "제안" 섹션에 적고 실행은 하지 말 것
- 부정적 결과, 애매한 결과 전부 그대로 기록. 판정 기준을 결과에 맞춰 재해석하지 말 것
- 재현성: seed 고정(42), 사용 패키지 버전 기록, 실행 커맨드 기록
- 이 실험이 검증하지 않는 것(관계 질문 보존, 실측 latency, 비-oracle 컨트롤러)을 REPORT 한계 섹션에 명시할 것
