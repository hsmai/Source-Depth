# anchor 벤치 v0 — 질문이 위치를 알려주지 않는 벤치마크. 사전 등록

작성 2026-08-23, **측정 전**. 실행 `scripts/36_anchor_bench.py` (`pbs/sd_anchor_n1.pbs`).

## 왜

기존 벤치의 최대 약점: 질문이 "In the first image"로 **위치를 알려준다.** 텍스트 파싱만으로
관련 이미지를 알 수 있으므로, "개입이 모델 내부여야 한다"는 주장을 이 벤치로는 검증할 수 없다.

## 설계

질문: **"In the image that contains {anchor}, is there {obj}?"** — 관련 이미지는 내용으로만 특정.

- 관련: anchor 포함 / 방해: anchor 전부 미포함 (참조 유일) / 관련 위치 무작위
- 셀1(적대): 관련에 obj 없음·방해에 있음 → gt no / 셀2: 반대 → gt yes
- K∈{2,3}, 셀당 150 → 목표 600문항. COCO instances만 사용, 로컬 보유 이미지로 한정
- (anchor,obj) 쌍당 ≤4문항 — 특정 쌍 집중 방지. seed 42+13

조건: M / B0..B{K-1}(컨트롤러) / ORD_READ(오라클) / REAL_READ(실현, pick은 같은 실행의 B에서
사전 고정 규칙으로 즉석 계산) + 3B에서 CLIP selector(anchor 프롬프트 argmax).

## 판정 (3B, K=3)

**주 종점 1 — 문제가 이 벤치에서도 실재하는가**: AUC(ORD_READ) − AUC(M) CI 하한 > 0.
실패 → 내용 특정 조건에서는 오염이 없다 = 기존 결과가 위치 참조 프롬프트의 산물일 가능성.
**연구 근본 재검토.** 그대로 보고한다.

**주 종점 2 — 실현 성능**: AUC(REAL_READ) − AUC(M) CI 하한 > 0.
실패 → 컨트롤러가 내용 특정 조건에서 무너짐. 방법을 오라클 진단으로 격하.

**부 종점 — selector 비교(공정한 조건에서 처음으로)**: 컨트롤러 판별 정확도 vs CLIP vs 찍기.
이 벤치에서는 CLIP도 anchor를 단서로 쓸 수 있으므로 **CLIP이 이기면 "앞단 selector로 충분"
반론이 성립한다. 그 경우에도 그대로 보고**하고 내부 개입 주장의 범위를 좁힌다.

## 해석 제약

1. v0다: COCO 한정, anchor는 단일 객체, 이항 질문. 일반화 주장 금지.
2. 관련 이미지가 anchor를 "포함"한다는 판정은 COCO annotation 기준(면적 무관) — 기존 규칙 그대로.
3. 셀1의 dis_pool(obj 있음·anchor 없음)과 셀2의 dis_pool(둘 다 없음)은 분포가 다르다.
   셀 간 비교는 하지 않고, 각 셀 내 조건 간 비교만 한다.
