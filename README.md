# SourceDepth

**이미지별 적응적 깊이 배분을 통한 멀티이미지 환각 완화** (training-free, per-image execution depth allocation for multi-image LVLMs)

> IMML Lab 인턴 한상민 개인연구 · 2027년 상반기 submission 목표
> 현 단계: **Phase 0 — 24h Feasibility Check** (교수님 보고용 정량 수치 3개 산출)

## 핵심 아이디어

Transformer에서 서로 다른 이미지의 토큰이 섞이는 유일한 통로는 layer별 self-attention이다. 즉 **depth = 이미지 간 혼합량**. 질문과 무관한 이미지(distractor)의 KV를 후반 layer에서 차단하면:

- (a) 답변 토큰의 연산 깊이는 그대로 유지되면서
- (b) distractor 유발 오답이 회복되고 (source-binding error의 구조적 차단)
- (c) distractor 토큰의 후반 layer 연산이 절감된다

## Phase 0에서 입증할 것

| # | 주장 | 수치 |
|---|---|---|
| ① | distractor가 답을 오염시킨다 | 조건별 Flip Rate 격차 (POPE+COCO 4셀 설계) |
| ② | 후반 layer KV 차단이 오염을 회복시킨다 | 정답률–차단깊이 L 곡선 |
| ③ | 얕은 layer attention으로 관련 이미지 식별 가능 | layer 4/8 attention top-1 식별률 |

모델: `Qwen/Qwen2.5-VL-3B-Instruct` (BF16, eager attention) · 평가: 생성 없이 next-token logit 비교 · 통계: McNemar paired test

## 저장소 구조

```
docs/
  00_research_overview.md     # 연구 개요 (제안서 PDF 정리)
  01_feasibility_brief.md     # 24h 실험 실행 지시서 (설계 변경 금지)
  02_experiment_plan.md       # 실행 계획 종합 (단계별 체크리스트)
  03_risks_and_watchpoints.md # 설계 리스크·주의점 (adversarial review 결과)
  04_implementation_plan.md   # 구현 상세 계획
  05_pbs_execution_plan.md    # PBS job 설계·제출 계획
  06_gpu_policy.md            # 연구실 GPU 정책 요약 + 본 프로젝트 적용
  reference/                  # 원 제안서 PDF
src/sourcedepth/              # 실험 코드 (Phase 0)
scripts/                      # 실행 엔트리포인트
pbs/                          # PBS job 스크립트
data/                         # POPE·COCO 데이터 (gitignore, 서버에서 다운로드)
results/                      # pairs.csv, results.csv, 그림, REPORT.md
logs/                         # 실행 로그 (단계별 시작·종료 시각 포함)
```

## 실행 환경

- 연구실 GPU 서버 `10.20.23.30` (PBS, 계정 isangmin) — **반드시 PBS batch job으로 제출** ([docs/06_gpu_policy.md](docs/06_gpu_policy.md))
- 대상: Node 3 (RTX 3090 24GB), 1-GPU job × 최대 2개 (token 2.0/2.5)
- 외부망에서 서버 SSH 불가 — 연구실 네트워크에서 clone 후 실행

## 원칙 (feasibility brief에서 발췌)

- 설계 변경 금지. 개선 아이디어는 REPORT "제안" 섹션에만 기록
- 모든 수치는 실제 실행 결과만. 추정·보간·날조 금지. 부정적 결과도 그대로 보고
- 재현성: seed 42 고정, 패키지 버전·실행 커맨드 기록
- 막히면 대안 실행 대신 "BLOCKED" 로그 후 보고
