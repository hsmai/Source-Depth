# 연구실 GPU 서버 사용 정책 (요약 + 본 프로젝트 적용)

> 서버: `10.20.23.30` / 계정: `isangmin` / 스케줄러: **PBS**
> 이 문서는 연구실 공지 정책을 본 프로젝트 관점에서 정리한 것. 위반 시 경고 누적(1시간마다) → 3차 경고 시 job 강제 종료.

## 0. 본 프로젝트에 적용되는 핵심 제약 (요약)

- **사용 가능 GPU: 총 2개** (Node 1, 3, 4 중에서)
- **반드시 PBS job 제출 방식** — interactive 사용 금지 (디버깅 목적 단시간만 예외적 허용이나, 본 프로젝트는 batch로 통일)
- 개인 GPU 활용 한도(token): **2.5**
  - RTX 3090 = 1.0 / RTX A6000 = 1.5 per device
  - → 3090 × 2 = 2.0 (OK) / A6000 × 1 = 1.5 (OK) / **A6000 × 2 = 3.0 (한도 초과, 불가)**
- Node 2 (A100)는 교수님 승인 + 주간 신청 필요 → **본 feasibility에서는 사용하지 않음**
- Job을 잡지 않고 GPU 프로세스 실행 시 **발견 즉시 강제 종료**
- Job 이름 규칙: `GPU수_CPU수_isangmin_작업명` (예: `1_8_isangmin_sd_main`)

## 1. 서버 리소스

| 노드 | CPU | GPU | Job당 CPU 제한 | 권장 CPU/GPU |
|---|---|---|---|---|
| Node 1 (pleiades1) | Xeon Gold 6342 ×2 (48c) | RTX 3090 24GB ×10 | 4 | max 4 |
| Node 2 (pleiades2) | Xeon Platinum 8358 ×2 (64c) | A100 80GB ×10 | 6 | max 8 (4 권장) — **별도 신청제** |
| Node 3 (pleiades3) | EPYC 7763 ×2 (128c) | RTX 3090 24GB ×8 | 8 | max 16 |
| Node 4 (pleiades4) | Xeon Platinum 8358 ×2 (64c) | RTX A6000 48GB ×8 | 6 | max 8 (4 권장) |

- Node 1은 마스터 노드 — CPU를 많이 쓰는 작업 금지, CPU-only interactive job 금지
- CPU 코어를 많이 쓸 예정이면 Node 3 사용
- CPU는 4의 배수가 효율적

## 2. 정책 요점

1. **기본 job 제한**: 교수님 지도 프로젝트만 허용. 수업 과제 사용 금지. 최소한의 짧은 사용. A100은 교수님 승인 필요 (CC: seonghee@unist.ac.kr, GPU Resource Manager 방진식에게 이메일).
2. **GPU 특이사항 시트**: 활용 한도 초과 사용 시 반드시 기재. AIGS/슈퍼컴퓨팅센터 대여 시에도 기재 (이 경우 한도 2.5 고정). 실험 시작·예상 종료 시간 기재 권장.
3. **GPU 활용 한도**: token_project = 2 + 0.5n, token_person = **2.5**. 한도 내에서도 GPU 부족 시 다른 프로젝트에 양보할 수 있어야 함. 소통 무응답 기준: 09–22시 사이 6시간 (22–09시는 카운트 제외). LIFO로 강제 종료.
4. **Node 2**: 매주 금요일 23:59까지 주간 신청, 최소 1 ~ 최대 4개, 4개 초과는 교수님 허락. 미신청 시 권한 소멸.
5. **Interactive job**: GPU 잡고 4시간 미활용 시 강제 종료. 짧은 디버깅 용도만.
6. **Deadline 근처**: 교수님 지정 학생 우선순위. 미제출 시 전 프로젝트 한도 2.5 고정.
7. **GPU 병렬화 확인**: 알고리즘상 병렬화 불가 코드는 GPU 1개만 사용할 것 (사용량 모니터링 필수).

## 3. 모니터링 도구

```
/home1/s20225367/resmonitor/res.py        # Node 1,3,4
/home1/s20225367/resmonitor/resnode2.py   # Node 2
/home1/s20225367/resmonitor/monitor.sh    # 통합
```

## 4. 본 프로젝트(SourceDepth Phase 0)의 GPU 사용 계획

- **대상 노드: Node 3 (pleiades3, RTX 3090 24GB)** — Qwen2.5-VL-3B BF16는 24GB에 충분(모델 ~8GB + activation). CPU 여유가 가장 크고 job당 CPU 제한(8)도 가장 관대.
- **3090 × 2 = token 2.0 ≤ 2.5** 한도 내. 단, 실험은 GPU 간 통신이 필요 없는 embarrassingly parallel 구조이므로 **1-GPU job 2개로 분리 제출** (정책 7 "병렬화 불가 시 1 GPU" 준수 + 양보 요청 시 job 단위로 내리기 쉬움).
- Job 이름: `1_8_isangmin_sd_<stage>` 형식.
- 폴백: Node 3 만석 시 Node 4 (A6000 ×1, token 1.5) 또는 Node 1 (3090 ×1, ncpus≤4).
- 상세 job 설계는 [05_pbs_execution_plan.md](05_pbs_execution_plan.md) 참조.

## 5. 접속 관련 메모

- 외부망(집)에서 SSH 불가 — **연구실 네트워크에서만 접속 가능** (2026-08-10 확인: 외부에서 port 22 timeout).
- 따라서 실험 실행은 연구실 접속 상태에서 수행하고, 코드·데이터 준비는 로컬 → GitHub → 서버 clone 경로로 관리한다.
