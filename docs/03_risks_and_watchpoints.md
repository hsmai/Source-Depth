# Phase 0 리스크·주의점 (Adversarial Design Review)

> 생성 방법: 실험 설계(01 브리프)에 대한 adversarial review agent의 20개 finding을, 독립 검증 agent가 브리프 원문과 전수 대조·정정한 결과를 통합한 것.
> **설계는 동결 상태다.** 여기의 어떤 항목도 설계 변경을 지시하지 않는다 — 각 항목은 다음 셋 중 하나로 분류된다:
> - **[결정 필요]** 브리프가 미규정한 모호성으로, 실행 전 한상민이 조작적 정의를 확정해 사전 등록해야 함
> - **[실행 체크]** 실행 중 반드시 확인·로그할 항목 (설계 불변 범위의 강건화)
> - **[REPORT 기록]** 실행하지 않고 REPORT의 한계·제안 섹션에만 기록

---

## A. 실행 전 확정이 필요한 결정 6건 [결정 필요]

> 아래 6건은 **본 실험 시작 전에** 확정하여 `config.py` 주석 + REPORT에 사전 등록 문구로 고정한다. 결과를 본 후 바꾸면 사전 등록 취지가 무너진다. 각 항목에 권장 기본값을 병기한다.

### A-1. 총 layer 수: 브리프의 "32" 전제 vs 실제 36 (severity: high)

Qwen2.5-VL-3B-Instruct의 text decoder는 **num_hidden_layers = 36**이다 (브리프 A-1·B-4는 32를 전제 — 두 리뷰 agent가 독립적으로 동일 지적, 서버에서 config 실측 확인 필수). 코드가 정상이어도 FLOPs 식을 문자 그대로 (32−L)/32로 쓰면 REPORT 수치가 왜곡된다 (T(24) 절감률: 8/32=25% vs 12/36=33.3%).
- **권장**: 브리프의 32를 '총 layer 수 placeholder'로 해석해 **(N−L)/N, N=실측값(36 예상)** 으로 계산. L grid {4,8,12,16,20,24}는 frozen이므로 불변. REPORT에 실측 N과 채택 해석을 명기.

### A-2. Flip Rate의 조작적 정의 (severity: high)

브리프 B-4 "M에서 S 대비 답이 뒤집힌 비율"은 (a) 분모(셀 전체 150 vs S가 특정 답을 낸 문항만), (b) 방향(셀별 지정 방향만 vs 모든 불일치), (c) PART D ①의 "+10%p" 해석이 갈린다. 정의 선택에 따라 판정 ①이 뒤집힐 수 있다.
- **권장**: 분모=셀 전체 150, 방향=셀별 지정 방향만 (셀 1·3: pred_S=no ∧ pred_M=yes / 셀 2·4: pred_S=yes ∧ pred_M=no). 판정식은 **브리프 D-① 3요건 전부**: FlipRate(셀1) ≥ 0.10 **AND** FlipRate(셀3) < FlipRate(셀1)/2 **AND** 셀 2에서 동형 패턴(역방향, 셀 4 대조 포함). ※ 검증자 지적: 셀 2 요건을 빼먹으면 판정 기준 완화(설계 변경)가 된다. 양방향 raw 카운트를 results.csv에서 재계산 가능하게 저장.

### A-3. 마스킹 대상 토큰 범위: delimiter 포함 여부 (severity: high)

브리프 C-3 "&lt;|vision_start|&gt;/&lt;|vision_end|&gt; (또는 image pad 토큰)"은 (a) `<|image_pad|>`만 vs (b) delimiter 포함 전 구간의 두 해석을 허용한다. Delimiter Token Scaling(브리프가 직접 인용)이 시사하듯 delimiter가 이미지 정보를 응집할 수 있어, (a)를 택하면 leakage 통로가 잔존해 T(L) 회복률이 체계적으로 과소평가될 수 있다 — ② 판정을 조용히 무효화하는 경로.
- **권장**: **`<|vision_start|>`부터 `<|vision_end|>`까지 전 구간 차단**. 채택안을 REPORT에 기록하고, 첫 3개 샘플의 구간 인덱스+실제 token id 디코딩을 로그로 수동 검증 (C-3 요구). ※ 04 구현 계획 초안은 (a)를 기본값으로 썼다 — 이 결정에 따라 `find_vision_spans`의 경계가 달라지므로 코드 작성 전 확정 필요.

### A-4. distractor "같은 supercategory" 규칙의 적용 대상 (severity: medium)

supercategory는 이미지가 아니라 category의 속성이므로 규칙 해석이 갈리고, 해석에 따라 셀 1 vs 셀 3 대비(판정 ①의 핵심)가 distractor 난이도 차이로 오염될 수 있다.
- **권장**: 전 셀 공통 — "질의 객체의 supercategory에 속하는 객체를 1개 이상 포함한 이미지 풀에서 무작위 추출하되, 셀 조건(질의 객체 자체의 포함/미포함)을 instances_val2014.json으로 필터". 셀별 distractor 통계(포함 객체 수, supercategory 분포)를 페어링 로그에 기록.

### A-5. ② 판정식의 분모 [M→T(0)] 격차가 작거나 음수일 때 (severity: medium)

회복률 = (Acc(T(L))−Acc(M))/(Acc(T(0))−Acc(M))에서 셀 2는 격차가 수 %p 이하이거나 음수일 수 있다. 분모 0 근처에서 수치 폭주, 음수면 부호 해석 역전.
- **권장**: "셀별 [M→T(0)] 격차 < 5%p면 해당 셀은 판정 불가(indeterminate)로 기록하고, **이 경우 ② 전체를 indeterminate로 보고한다 (판정 가능한 셀만으로 PASS 격상 금지)**". ※ 검증자 지적: 남은 셀만으로 PASS 처리하면 '셀 1·2 모두' 요건의 완화다.

### A-6. 프롬프트 관사: "a {object}" 고정 vs POPE 원문 관사 보존 (severity: low)

브리프 B-1 문구는 "a {object}"지만 POPE 원문은 모음 앞 "an"을 쓴다 ("an orange"). "a orange" 같은 비문은 sanity 3에서 S 정답률을 POPE 보고치와 비교할 때 격차 요인이 될 수 있다.
- **권장**: POPE 원문 질문에서 관사까지 포함해 객체구를 추출·보존 ("an orange" → "is there an orange"). 채택안을 REPORT에 명기.

---

## B. 실행 중 반드시 확인할 항목 [실행 체크]

| # | 항목 | 요지 | 대응 (04 구현 계획에 반영됨) |
|---|---|---|---|
| B-1 | **mask 무음 실패(no-op) 탐지** (high) | 셀 3·4는 M vs S 일치율이 원래 높아, hook이 전혀 발화 안 해도 sanity 1을 통과할 수 있음 → 전 T(L)=M인 채 "회복 없음" false negative | ① probe 샘플에서 layer≥L의 distractor 열 attention 질량 == 0 assert, ② 셀 1에서 T(0) vs M 불일치 > 0 확인, ③ T(N)≡M bitwise 동등성, ④ hook 발화 카운터(layer×문항 기대치 일치) |
| B-2 | **"first image" grounding + fallback 후속 처리** | Qwen2.5-VL 기본 chat template에는 "Picture N" 라벨이 없음(버전 의존 — 렌더링 문자열로 실측 확인). fallback 채택 시 기존 결과 무효화 | fallback 채택 시 **sanity 1·3 재실행 + Yes/No 토큰 probe 재확인 + pairs.csv 프롬프트 컬럼 재생성**. 최종 템플릿 전문을 REPORT에 기록. 라벨 토큰이 마스킹 구간에 미포함임을 인덱스로 확인 |
| B-3 | **logit 추출 위치** | add_generation_prompt 누락 / batch padding 시 잘못된 위치의 logit을 읽는 무음 버그 | 위치 결정을 단일 함수로 통일(평가·프로파일링 공유), batch 1 기본, 소량 샘플 argmax 디코딩 육안 로그 |
| B-4 | **transformers 버전 고정** | ≥4.49 floating이면 hook 경로·전처리가 버전에 따라 무음으로 달라짐. config 접근(`num_hidden_layers`)도 버전에 따라 text_config 하위로 이동 | 서버 설치 시점에 exact pin + pip freeze 기록, 로컬·서버 버전 일치, `getattr(config, "num_hidden_layers", config.text_config.num_hidden_layers)` fallback |
| B-5 | **mask 구현 디테일** | literal −inf 대신 `torch.finfo(dtype).min`(관례 일관성 — 본 설계에서 전행 마스킹은 없어 NaN 실위험은 낮음). model.forward에 4D mask 직접 주입 금지(get_rope_index가 2D 기대 → M-RoPE 파손) | layer-level hook로만 주입, NaN/inf assert, M vs T(L) position_ids 동일성 1샘플 비교 |
| B-6 | **T(L) 경계 off-by-one** | 브리프 내 서술은 일관되나(0-based `idx ≥ L` 차단 = 앞 L개 layer만 혼합), 구현자가 `>` 사용·1-based로 오독 가능 | 'T(L) = 0-based idx ≥ L 마스킹' 상수 명문화, T(0) hook 발화 카운터로 anchor 검증 |
| B-7 | **McNemar 세부** | exact vs chi-square 선택으로 경계 p값이 달라짐. 다중 검정 주의 (단, 판정 ②는 동일 L에서 셀 1·2 conjunctive라 우연 통과 상한 ≈ 6×0.05² ≈ 1.5% — 초안의 "5%를 훨씬 넘는다"는 검증자가 정정) | `statsmodels mcnemar(exact=True)` 고정, discordant pair (b,c)를 표 1에 병기, 검정 총 횟수를 REPORT에 명시 |
| B-8 | **COCO annotation 불완전성** | 셀 3 '미포함' 판정은 annotation 부재 기반 — 소형 객체·iscrowd 경계 사례로 대비 희석 가능 | iscrowd 처리 규칙을 상수로 고정·기록, 셀 1 distractor 10장 육안 스팟체크, 한계 섹션 명시. ※ bbox 면적 하한 필터는 **채택 금지**(B-1 셀 구성 규칙에 없는 추가 필터 = 설계 변경) — 제안 섹션에만 기록 |
| B-9 | **POPE 포맷 함정** | JSONL(단일 배열 아님), label 소문자 "yes"/"no", 다단어 객체(dining table 등) 매칭 | line-by-line 파싱, 80 category exact-match 사전, 매칭 실패 수 집계(≠0이면 원인 확인) |
| B-10 | **네트워크 스테이징** | compute node 외부 인터넷 미확인 — stage 1이 통째로 막힐 수 있음 | **사전 확정된 스테이징 경로**(로그인 노드 선다운로드 + job offline 강제)를 기본으로 하고, 경로 전환이 필요해지면 BLOCKED 상당 로그 후 사전 승인된 계획 내에서만 전환 (임의 대안 실행 금지 원칙과의 충돌 방지) |
| B-11 | **선점·강제종료 대비 resume** | 양보 무응답 LIFO kill 환경에서 stage 3 (5h)가 통째로 소실 가능. 2-job 병렬 시 동일 파일 동시 쓰기 race | (question_id, condition) 단위 append-only + idempotent resume, job별 별도 shard 파일 → stage 5 병합·중복 검사 |
| B-12 | **stage 3·4 간 M 예측 불일치** | BF16 비결정성·batch 차이로 근소 문항의 예측이 재실행 간 뒤집힘 → fig2 케이스 분류 오염 | 케이스 분류의 단일 소스 = stage 3 results.csv 사전 지정, stage 4 재예측과의 일치율 로그, margin 저장으로 near-tie 식별 |
| B-13 | **attention 프로파일링 OOM** | full attention 유지 시 36 layers × 16 heads × seq² — 샘플당 대용량 (fp32 기준 수 GB 자릿수) | hook에서 마지막 토큰 행만 즉시 축약 후 폐기 (샘플당 수 MB), 행 합 ≈ 1.0 검증(softmax 후 텐서인지 확인) |

## C. REPORT에만 기록할 것 [REPORT 기록]

1. **③의 구조적 confound (high)**: 전 600문항에서 관련 이미지가 항상 첫 번째 위치 → positional/primacy bias만으로도 식별률 80%+가 나올 수 있어, ③ PASS가 컨트롤러 신호를 입증하지 못한 채 통과 가능. **한계 섹션에 "position bias와 관련도 신호를 분리하지 못함" 명시**, 제안 섹션에 "이미지 순서 뒤집은 소량 대조 실행" (Phase 1 과제). ※ 검증자 정정: 80% 임계는 **layer 8에만** 적용 (layer 4는 측정만, 판정 임계 없음).
2. **③ attention 질량 합의 토큰 수 confound (low)**: 질량 '합' 비교는 토큰 수 많은 이미지에 구조적으로 유리. 이미지별 토큰 수를 저장해 식별 실패 문항과의 상관을 REPORT에 기술, per-token 평균 기준 식별률을 제안 섹션에 병기.
3. **McNemar 다중성**: 검정 총 횟수와 선택 효과 주의 명시, Bonferroni 조정 p 참고치 병기 (제안 섹션).
4. **batch 1 채택**: 브리프 C-1의 "배치 4~8" 지침에서 이탈 (결과 불변·시간 상한 내 근거) — 이탈 사유를 REPORT에 명기.

## D. 검증자가 정정·기각한 초안 주장 (기록용)

- ③ 임계 "layer 4·8 각각 80%" → **layer 8만 80%** (layer 4는 판정 없음)
- off-by-one이 "브리프 내 모순"이라는 프레임 → 브리프는 내적으로 일관 (0-based ≥L = 1-based 'L 이후'), 리스크는 구현자 오독뿐
- "12회 검정 중 1회 p<0.05 우연 확률이 5%를 훨씬 넘는다" → 판정 ②는 conjunctive 기준이라 우연 통과 상한 ≈ 1.5% (다중성 명시 권고 자체는 유지)
- literal −inf의 NaN "위험" → 본 설계에선 전행 마스킹이 없어 실위험 낮음 (finfo.min 사용은 관례상 유지)
- "로그인 노드 다운로드가 마스터 노드 CPU 정책과 충돌" → 과장 (다운로드는 네트워크 I/O 위주, 06 문서가 이미 스테이징 경로 명시)
- 불확실로 표시된 기술 주장 (서버에서 실측 확인 필요): Qwen2.5-VL 토큰 id 3종(151652/151653/151655) 및 36층, 기본 chat template의 'Picture N' 라벨 부재(버전 의존), transformers 리팩토링의 정확한 버전 경계, 이미지당 vision token 수(COCO 기본 해상도에서 ~300–400개가 전형)
