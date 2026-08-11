# 실행 저널 (Phase 0)

## 2026-08-10 (D0) — 밑작업
- 레포 생성, 문서 00~06 작성 (설계 리뷰·구현 계획·PBS 계획 + 검증 반영)
- 사전 등록 결정 A-1~A-6 권장값으로 확정 (docs/03 §A → src/sourcedepth/config.py)
- 서버 접속 확보: `~/.ssh/config`의 `prm-server` (10.20.23.30:**3022**, 키 인증 — 표준 22 포트는 닫혀 있음)
- 서버 환경 셋업 시작 (venv, 모델 다운로드) — 세션 종료로 중단됨

## 2026-08-11 (D1) — 구현·배포·제출

### 서버 환경 실측 (docs/05의 미검증 가정 4건 해소)
| 가정 | 실측 결과 |
|---|---|
| 스케줄러 | **PBS Pro** (`/usr/pbs`), `select=1:ncpus=8:ngpus=1` 문법 — 실행 중 타 job에서 확인 |
| 노드 지정 | **노드별 queue 방식**: `workq/A100/pleiades1/pleiades2/pleiades3/pleiades4/single` → `-q pleiades3`로 고정 (host= 불필요) |
| 로그인 노드 | **pleiades1 (마스터 노드와 동일)** — stage 1/5 CPU 작업은 경량 유지 |
| 아웃바운드 인터넷 | **가능** (HF·GitHub·COCO 모두 200) — 서버에서 직접 다운로드 |

- 홈: `/home/isangmin` (정책 문서의 /home1 아님), `/home` 97% 사용 중 (여유 265GB, 본 프로젝트 소요 ~14GB)
- 환경: 기존 `qwen-omni` conda env(torch 2.5.1+cu121, transformers 4.52.3) 위에 venv overlay
  (`--system-site-packages` + statsmodels/pandas/scipy/qwen-vl-utils) — 신규 대용량 설치 회피
- 모델 다운로드 이슈: HF snapshot_download가 2.78GB 지점 `.incomplete`에서 resume 정체 반복
  → curl 직접 이어받기 + sha256 검증으로 우회 (`setup/curl_shard.sh`)
- 교훈: `ssh 'pkill -f <패턴>'`은 원격 쉘 자신의 cmdline과 매칭되면 self-kill → `[d]` 브래킷 트릭 필수

### GPU 사용 확정 (사용자 지시 2026-08-11)
- **1 GPU만, Node 1 또는 3** → `pleiades3` queue 1-GPU job으로 확정 (2-GPU 분할 계획 폐기)
- 사용자 언급 "A6000"은 정책 문서상 Node 4 소속 — Node 3은 3090. 스모크 job의 nvidia-smi로 실제 카드 확인·기록
- job 이름: `1_8_isangmin_sd_*` (analyze는 CPU-only `0_4_...`)

### 무인 자동 실행 설계 (사용자 퇴근 후 개입 불가 전제)
```
submit_chain.sh:
  smoke(1h) → sanity(3h, afterok) → main(12h, afterok: 03_run_main + 04_profile) → analyze(1h, afterany)
```
- 게이트: SMOKE_PASSED/SANITY_PASSED flag + BLOCKED(exit 86) → afterok가 후속 job 자동 취소
- analyze는 afterany — 어디서 멈췄든 `results/STATUS.md` 생성 보장
- 전 단계 (question, condition, template) 단위 resume — 강제 종료·양보 후 재제출만으로 복구
