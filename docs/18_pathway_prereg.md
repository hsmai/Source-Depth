# 경로 분해 + 고립 파일럿 — 사전 기록

작성 2026-08-14, **결과 관측 전**. 실행 `scripts/22_pathway_pilot.py`. 파일럿(탐색적)이며
확정 주장에는 재현 필요. 그러나 예측은 지금 못박는다.

## 왜

신규 설계의 가설은 "환각 = 이미지 간 정보 섞임, 주로 뒤쪽 layer"다. 그런데 causal LM에서
순서 [img1, img2, text]일 때 정보 경로는 **둘뿐**이다:

- **(a) img2 query → img1 key** — 이미지 간 혼합. 역방향(img1→img2)은 causal상 불가능
- **(b) text query → img key** — 질문 토큰의 읽기

기존 T0(전면 차단)은 (a)+(b)를 함께 끊어서 어느 쪽이 원인인지 말할 수 없었다.
이 실험은 경로를 하나씩 끊는다.

## 예측 (사전 고정)

| # | 예측 | 근거 |
|---|---|---|
| P1 | **READ ≈ T0** (완전 회복), **XIMG ≈ M** (효과 없음) | posbal에서 순서를 뒤집어도(=경로 a의 방향이 바뀌어도) 이득 87% 유지 → 표현 오염이 주범이면 나올 수 없는 결과 |
| P2 | ISO0 ≥ M3 − 0.02 (AUC) — need-all 질문에서도 이미지 간 attention은 불필요 | 통합이 텍스트 토큰에서 일어난다면 이미지끼리 볼 필요 없음 |
| P3 | 관계형(R1·RB)에서도 ISO0 ≈ M | 비교조차 질문 토큰이 수행한다는 가설. **여기가 가장 자신 없는 예측** — 무너지면 그 지점이 이미지 간 attention의 존재 이유 |

P1이 맞으면: 가설 문구를 "정보 섞임" → **"읽기 단계의 출처 오귀속(source misattribution)"**으로
정정해야 한다. 개입 지점도 "표현 분리"가 아니라 "읽기 경로 제어"가 된다.

## 설계

| PART | 데이터 | 질문 | 조건 | n×조건 |
|---|---|---|---|---|
| 1 경로분해 | pairs.csv 셀1·2 (gt 균형) | "first image" | M / XIMG / READ / T0 | 300×4 |
| 2 고립 | md_pairs (leak=yes/ctrl=no 균형) | **"any of these images"** — 모든 이미지 필요 | M3 / ISO0 / ISO16 | 300×3 |
| 3 경계 | rel_pairs (R1·R2·RB) | "both images" | M / ISO0 | 300×2 |

ISO = 이미지 j query → 이미지 i key (i≠j) 차단, 텍스트 query는 모든 이미지를 봄.
구현: `KVBlockController.configure_pathway` — 4D mask의 (query행, key열) 블록 지정.
prefill 단발 forward 전용 (decode 시 좌표 불일치).

## 판정 지표

- PART1: 셀1·2 정확도 + AUC(gt 균형). READ−T0 차이 < 0.02 AUC & XIMG−M < 0.02 AUC → P1 성립
- PART2: AUC(M3) vs AUC(ISO0). ISO0 ≥ M3 − 0.02 → P2 성립. ISO0 > M3 + 0.02 면 "고립이 오히려 이득"
- PART3: R1·RB 정확도. ISO0가 M 대비 −5%p 이상 하락하는 셀이 있으면 → 그 셀이 이미지 간 attention의 필요 지점

## 해석 제약

1. 3B 단독 파일럿. 주장 확정 전 7B 재현 필요.
2. PART2의 need-all 질문에서 앞단 selector는 **정의상 불가능** (모든 이미지가 정답에 관여).
   이 파트가 "왜 VLM 내부 개입이어야 하는가"의 실증 근거다.
3. 파일럿 결과로 P1~P3 예측 문구를 사후 수정하지 않는다. 틀리면 틀린 대로 보고.
