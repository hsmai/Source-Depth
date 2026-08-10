# Phase 0 실행 계획 종합 (Master Plan)

> 설계 원본: [01_feasibility_brief.md](01_feasibility_brief.md) — **설계 변경 금지, 이 문서는 브리프를 실행 순서·체크리스트로 재배열한 것일 뿐 내용을 바꾸지 않는다.**
> 리스크·주의점: [03_risks_and_watchpoints.md](03_risks_and_watchpoints.md) · 구현 상세: [04_implementation_plan.md](04_implementation_plan.md) · PBS: [05_pbs_execution_plan.md](05_pbs_execution_plan.md)

## 0. 목표 재확인

24h 안에 교수님 보고용 정량 수치 3개 산출:

| # | 주장 | 수치 | 사전 등록 판정 기준 (PART D) |
|---|---|---|---|
| ① | distractor가 답을 오염시킨다 | 조건별 Flip Rate 격차 | 셀 1에서 M의 Flip Rate ≥ S 대비 +10%p, 셀 3에서는 그 절반 미만, 셀 2도 같은 패턴(역방향) |
| ② | 후반 layer KV 차단이 오염 회복 | 정답률–차단깊이 L 곡선 | 어떤 L에서 T(L)이 [M→T(0)] 격차의 50%+ 회복 (셀 1·2 모두, McNemar p<0.05) |
| ②′ | Type-B 실증 | Recovery > Damage | 그 L에서 Recovery Rate > Damage Rate |
| ②″ | 인과 확인 | negative control | T-rel(8) 정답률이 M 대비 유의하게 하락 |
| ③ | 컨트롤러 실현성 | layer 4/8 attention top-1 식별률 | layer 8에서 ≥ 80% |

**판정 기준은 결과를 보고 바꾸지 않는다.** 실패 시 대응도 브리프 PART D에 사전 등록된 순서로만 (각 1회).

## 1. 실행 구조: 로컬 준비 → 서버 실행

외부망에서 서버 SSH 불가이므로 두 트랙으로 분리한다.

### Track A — 로컬 (서버 접속 전, GPU 불필요)
- [x] 레포 생성·문서화 (본 커밋)
- [ ] 전체 코드 작성: 데이터 파이프라인, mask hook, 평가, 프로파일링, 분석·그림
- [ ] 로컬 스모크: 데이터 준비 스크립트는 로컬에서도 실행 가능 (POPE json + COCO annotation + 이미지 다운로드) → `pairs.csv`를 미리 만들어 커밋 가능
- [ ] PBS 스크립트 작성 (queue명 등 placeholder)
- [ ] 코드 리뷰 1회 (mask 구현 로직 중심)

### Track B — 서버 (연구실 네트워크 접속 후, 24h 시계 시작)
브리프 C-5의 시간 상한을 따른다:

| 단계 | 내용 | 상한 | GPU |
|---|---|---|---|
| 1 | 환경 구축(conda, requirements), 모델 선다운로드(HF_HOME), 데이터 준비, pairs.csv 검증 | 3h | 불필요 (로그인 노드) |
| 1.5 | **스모크 테스트 job** (5문항 × 전 조건, walltime 30m) | 단계 2에 포함 | 1 |
| 2 | mask hook 검증 + sanity 3종 (C-4) — **통과 전 본 실험 진입 금지** | 4h | 1 |
| 3 | 본 실험: 10조건 × 600문항 logit 평가 → results.csv | 5h | 1–2 |
| 4 | M 조건 attention 로깅 재실행 → 프로파일링·③ | 3h | 1 (단계 3과 병렬 가능) |
| 5 | 분석·그림·REPORT.md | 3h | 불필요 |
| 버퍼 | 실패 대응 / distractor 2장 확장(여유 시에만) | 6h | — |

단계별 시작·종료 시각을 `logs/`에 기록. 상한 1.5배 초과 시 하위 항목 축소 후 진행 (sanity 미통과 상태로 본 실험 진행은 금지).

## 2. 실험 매트릭스 (브리프 B 요약)

- **데이터**: POPE(COCO) adversarial split → 원본 이미지 + distractor 1장, 4셀 × 150문항 = 600문항
  - 셀 1: GT=No, distractor에 객체 **포함** (주 leak: No→Yes)
  - 셀 2: GT=Yes, distractor에 객체 **미포함** (역방향: Yes→No)
  - 셀 3: GT=No, 미포함 (셀 1 대조군) / 셀 4: GT=Yes, 포함 (셀 2 대조군)
  - distractor: 같은 COCO supercategory의 다른 이미지, instances_val2014.json으로 셀 조건 검증
- **조건 (문항당 10 forward)**: S / M / T(4,8,12,16,20,24) / T(0) / T-rel(8)
  - 핵심 비교군은 M / T(L) / T(0) (동일 layout). S는 참조용 — layout 비대칭을 "고치려" 하지 말 것
- **평가**: 생성 없이 마지막 위치 next-token logits에서 Yes/No 대표 토큰 집합 max-logit 비교 (토큰 id는 소량 생성으로 사전 확정, REPORT에 기록)
- **지표**: Accuracy, Flip Rate, Recovery/Damage Rate, McNemar p, 이론 FLOPs 절감(= distractor 토큰 수 × (32−L)/32, 실측 latency는 측정하지 않음 — mask 등가 구현이므로)
- **프로파일링**: M 조건에서 layer별 마지막 프롬프트 토큰의 attention 질량 [이미지1/이미지2/텍스트] (head 평균), 정답/뒤집힘 케이스 분리. ③ = layer 4/8에서 top-1이 이미지1인 비율

## 3. Sanity 3종 (통과 전 본 실험 금지)

1. **T(0) vs S 일치율**: 셀 3·4 각 30문항에서 ≥ 90% (70% 미만 = mask 버그로 간주, 중단·디버그)
2. **"first image" grounding**: 20문항 소량 생성 육안 확인 → 실패 시 fallback 프롬프트("Picture 1:" 라벨), 그래도 실패면 BLOCKED
3. **S 정답률**: 3B급 POPE 보고치(~80%대)와 대략 일치, 60% 미만이면 파이프라인 버그 의심

## 4. 산출물 (전부 필수, `results/`에 저장 후 커밋)

1. `pairs.csv` — 문항·이미지 페어링 명세
2. `results.csv` — 문항 × 조건별 예측·정오 (raw)
3. `fig1_accuracy_vs_L.png` — 대표 그림 (셀 1·2 분리 패널, M/T(0) 수평선, T-rel(8) 점)
4. `fig2_attention_profile.png` — layer별 attention 질량 (정답 vs 뒤집힘 분리)
5. `REPORT.md` — 고정 구조 (환경 / sanity / 판정표 / 표 1 / FLOPs / 한 줄 결론 / 이상 징후·한계·BLOCKED)

## 5. GPU 사용 (요약)

- Node 3 (3090 24GB), **PBS batch job만** 사용, 1-GPU job 최대 2개 (token 2.0/2.5)
- Job 이름: `1_8_isangmin_sd_<stage>` — 상세는 [05_pbs_execution_plan.md](05_pbs_execution_plan.md)

## 6. 원칙 (브리프 PART F)

- 설계 변경 금지 — 개선 아이디어는 REPORT "제안" 섹션에만
- 수치 추정·보간·날조 금지, 부정적 결과 그대로 보고
- seed 42, 패키지 버전·실행 커맨드 기록
- 검증하지 않는 것(관계 질문 보존, 실측 latency, 비-oracle 컨트롤러)을 REPORT 한계에 명시
- 막히면 BLOCKED 로그 후 보고 (임의 대안 실행 금지)
