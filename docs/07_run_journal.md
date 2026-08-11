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
- analyze는 afterany + **각 GPU job의 EXIT trap이 05_analyze 자체 실행** — 어디서 멈췄든 `results/STATUS.md` 생성 보장
- 전 단계 (question, condition, template) 단위 resume — 강제 종료·양보 후 재제출만으로 복구

### 제출 전 적대적 코드 리뷰 (6-agent workflow, finding 35건)
- **Critical 2건**: ① profiler 질량 합 허용오차 1e-3이 bf16 반올림과 동일 스케일 → 야간 21,600회 체크 중 오탐 BLOCKED 확률 ≈ 1 (→ 2e-2 + 정규화로 수정) ② jsonl 잘린 행 뒤 append 시 레코드 무음 소실 (→ 개행 보정)
- **긍정 확인**: transformers 4.52.3 원본 대조 결과 mask hook 경로 정확 — decoder layer는 attention_mask를 kwargs 4D로 받고, eager에서 None 불가, `model.language_model.layers` 경로 적중, 차단 열 softmax 질량 정확히 0
- person supercategory confound (not-contains pool 부재로 64문항이 셀 1·4 쏠림) → **balanced 배정** 도입: gt-쌍 두 셀의 pool이 모두 존재할 때만 배정, 미달 시에만 unbalanced 2차 (실측: 600문항 전량 balanced 성공)
- 나머지 high/medium 12건 반영 (fired 카운터 per-forward 검증, resume 페어링 일치 검사, stale flag 제거, 커버리지 전수 검사, partial profile 시 ③ 판정 유보 등)

### 데이터 확정 (2026-08-11 13:44)
- `pairs.csv`: 600문항 (셀당 150), **전부 adversarial split** (popular 보충 불필요), **전부 balanced 배정**
- 이미지 1,002장 전수 다운로드·무결성 통과
- POPE gt vs COCO annotation 불일치 36건(6%) — POPE gt 기준 유지, REPORT 한계 기록 예정

### 체인 제출 (2026-08-11 13:47 KST)
```
99106 sd_smoke   (R 즉시 시작)  → 99107 sd_sanity (afterok)
→ 99108 sd_main (afterok, 12h) → 99109 sd_analyze (afterany)
```
- 사용자 별도 프로젝트 job(G1C4, 99059)과 합산 2 GPU = token 2.0 ≤ 2.5 한도 내

### 결과 (2026-08-11 14:16 KST — 체인 제출 후 29분 만에 완주)
- 판정: **① PASS · ② PASS (L*=4) · ②′ PASS · ②″ PASS · ③ FAIL (0.725 < 0.80)**
- sanity: T0vsS 일치 0.983 / grounding 0.90 / S acc 0.855 — 전부 통과, fallback 미사용
- BLOCKED 0건, 실행 GPU: RTX 3090 (pleiades3), 총 GPU 시간 ≈ 30분
- 상세: results/REPORT.md · 그림은 영문 라벨로 재렌더 (서버 한글 폰트 부재)

### 스토리지 사고·이전 (2026-08-11 17:55)
- 확장 실험 도중 **/home이 클러스터 전체 100% 도달** (전일 265GB 여유 → 타 사용자 사용으로 소진). 7B 다운로드가 ENOSPC로 실패, 실행 중이던 결과 쓰기도 위험한 상태였음
- 대응: ext job qhold → `~/sourcedepth` 전체를 **/data3/isangmin/sourcedepth**(726GB 여유, 전 노드 NFS 마운트·쓰기 확인)로 이전 후 symlink → PBS 절대경로·venv 그대로 동작 확인 → qrls
- 7B 다운로드 /data3에서 재개. /home은 8.7GB만 확보된 임계 상태 — **연구실 공지 필요** (사용자 액션 아이템)

### 자체 반증 — "차단이 단일 이미지보다 정확하다" 주장 폐기 (2026-08-11 22:00, 사용자 지적)
- 문제: 슬라이드에서 T4 셀1 92.0% > S 셀1 89.3%을 "얕게 차단이 더 정확"의 근거로 제시했음
- 검증: 조건별 '예' 응답률이 S 0.420 → T4 0.402 → T16 0.367로 단조 감소. 정답이 '아니오'인 셀(1·3)은
  전부 상승, '있다'인 셀(2·4)은 전부 하락 → **정확도 향상이 아니라 판정 기준 이동**.
  전체 정답률 S 0.840 vs T4 0.842 = 사실상 동일
- 브리프 B-2가 이미 "S와 T는 layout이 달라 직접 비교 불가, S는 참조용"이라 사전 경고 — 이를 어긴 것
- 조치: 해당 주장 폐기, 슬라이드에서 제거 + 부록 A3b(자체 반증 점검) 신설
- **핵심 결론은 무영향**: M → T4는 동일 layout 비교이며, 오염 문항군(셀1) +20.0%p vs 오염 없는
  대조군(셀3) −2.0%p로 차등 반응. 기준 이동이면 둘 다 올랐어야 하고, 응답률 이동폭(3.8%p)으로는
  20%p를 설명 불가 → 오염 제거가 실재함이 오히려 강화됨

## 2026-08-11 야간 (D1 밤) — 확장 실험 결과

### ★ A1 성공: 이미지별 차등 depth 배분이 동일 예산에서 일괄 차단을 압도
동일 "이미지-레이어 예산"(50.5% 절감)에서 배분 방식만 달리한 통제 비교:
| 배분 | 방식 | 절감 | 셀1 | 전체 |
|---|---|---|---|---|
| 차등 J4x28 | 방해 4층 + 대상 28층 (32+8 image-layers) | 50.5% | 0.927 | **0.837** |
| 일괄 VTW16 | 둘 다 16층 (20+20 image-layers) | 50.5% | 0.840 | **0.550** |
→ **동일 계산량에서 +28.7%p**. 예산이 아니라 **배분**이 결정적임을 입증.
또한 J4x28은 차단 없음(M, 0.790)보다 **정확도 +4.7%p면서 계산 50.5% 절감**.
관련 이미지 depth 요구량: Rel28 0.787 ≈ M 0.790 → 대상 이미지도 36층 전부 불필요(28층이면 충분).

### ★ 7B 반전: POPE 오염이 거의 사라짐 (중대한 한계)
| | 3B | 7B |
|---|---|---|
| 셀1 S→M | 0.893 → 0.720 (−17.3%p) | 0.947 → **0.967 (+2.0%p)** |
| flip rate | 21.3% | **0.7%** |
| negative control | 0.79→0.50 (p=4e-38) | 0.79→0.51 (p=2e-42) ✅ 동일 |
| 컨트롤러(layer8 mean-head) | 72.5% | **92.8%** ✅ 더 강함 |
→ 해석: POPE+distractor 1장은 7B에 너무 쉬움(셀1 S=0.947 천장 근접). 오염 현상은 스케일에 따라
완화되며, **더 어려운 멀티이미지 벤치(MuirBench/MVH-Bench)로 옮겨야 함** — Phase 1 방향 수정 근거.
차단 기구 자체와 컨트롤러 신호는 7B에서도 그대로 작동.
→ 후속: 7B에서 **relational X자 교차**와 **차등 배분 효율**이 성립하는지 즉시 투입 (job 99180).
  둘 다 오염 유무와 무관한 주장이므로, 성립하면 연구의 축을 그쪽으로 옮길 수 있음.

### 실패·복구 (job 99179)
- 08b head 단위 순서뒤집기: PBS 스크립트 편집이 job 제출 이후라 미실행 → 재투입
- 12 CLIP baseline: torch 2.5 + transformers 4.52가 `.bin` 로딩 거부. HF에 safetensors 없어
  `.bin`을 직접 safetensors로 변환해 캐시에 주입 후 재실행
- 13 α-knob: question_id 타입 불일치(int vs str)로 조합 0건 → str 통일로 수정

### ★★ 순서 뒤집기 검증 결과 — 컨트롤러 신호의 정체 판명 (2026-08-11 23:5x)
원본에서 고른 head를 순서 뒤집힌 입력에 그대로 적용:
| layer | 원본 | 뒤집기 | 판정 |
|---|---|---|---|
| 5 (h7) | 0.983 | **0.017** | 위치 편향 |
| 8 (h4) | 0.998 | **0.002** | 위치 편향 |
| 12 (h5) | 1.000 | 0.002 | 위치 편향 |
→ **얕은 층의 99.8%는 "관련도"가 아니라 "첫 번째 이미지"를 보는 head였다. 판정 ③은 버전 B 확정.**

**그러나 더 중요한 후속 분석**: "양쪽 순서 모두에서 맞는 head"(= 질문의 지시대상을 따라가는 head)를
전 층·전 head에서 탐색 → min(원본, 뒤집기) 기준:
| layer | 2~16 | 20 | 21 | **22** | 24 |
|---|---|---|---|---|---|
| 위치 무관 정확도 | 0.31~0.51 (무작위) | 0.617 | 0.843 | **0.882** | 0.785 |
→ **위치 무관 신호는 얕은 층에 없고 layer 20~22에서 발생한다.** 그리고 이 구간은
relational 통합·오염 발생 구간(20~24)과 정확히 일치 — 모델이 "질문↔이미지 결합"을 하는 지점.
→ 외부 리뷰어가 예측한 trade-off("빨리 판단하면 부정확, 늦으면 절감 없음")의 정확한 측정치 확보.
→ 후속 투입: **현실적 작동점 J20x28 / J22x28 / J24x28** (layer 22에서 판단 후 그 지점부터 차단).
  이론 절감은 oracle(50.5%)보다 낮은 ~30% 수준이지만 **비-oracle에서 달성 가능한 수치**.
→ α-knob 결과(정확도 0.788, 절감 21.2%)는 layer-8 위치편향 head 기반이라 사실상 oracle —
  REPORT에 그 한계를 명시하고, layer-22 신호 기반으로 재계산 필요.

### 야간 추가 투입 (GPU 1장 순차 체인, 정책 준수)
- 99180 (R): 7B relational X자 교차 + 7B 차등 배분 — 오염과 무관한 두 핵심 주장의 7B 검증
- 99181 (H): **distractor 2장** (PART D 사전 등록 실패 대응 (b)) 7B→3B — "오염은 스케일보다
  경쟁 출처 수에 민감한가" 검증. 사전 등록 절차이므로 benchmark shopping이 아님
- 99182 (H): J20x28/J22x28/J24x28 현실적 작동점 + CLIP baseline(offline 경로 수정)
