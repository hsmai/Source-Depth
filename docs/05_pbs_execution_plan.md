# SourceDepth Phase 0 — PBS 실행 계획서

> 대상 서버: `10.20.23.30` / 계정 `isangmin` / 스케줄러 PBS
> 근거 문서: `01_feasibility_brief.md`(실험 설계 — frozen), `06_gpu_policy.md`(연구실 정책)
> 원칙: 실험 설계는 일절 변경하지 않는다. 이 문서는 **동일한 설계를 PBS job으로 어떻게 배치·실행하느냐**만 다룬다.
> **작성 경위**: 컴퓨트 플래너 agent 초안을 독립 검증 agent가 GPU 정책과 전수 대조 — 명시적 정책 위반 0건 확인, 단 실행 시점 위반으로 전화될 수 있는 허점 1건(노드 미고정 제출)과 기술 정정 9건을 본문에 반영했다.

---

## 1. C-5 단계 → PBS job 분해

브리프 C-5의 5단계 중 GPU가 실제로 필요한 것은 **모델 forward가 일어나는 단계뿐**이다. 데이터 다운로드·페어링·분석은 로그인 노드 CPU 작업으로 처리하고, GPU job은 짧고 명확하게 유지한다 ("최소한의 짧은 사용" 정책 준수).

| C-5 단계 | 내용 | 실행 위치 | 대응 job |
|---|---|---|---|
| 1 | 환경 구축, HF 모델 다운로드, POPE/COCO 다운로드, `pairs.csv` 생성 | **로그인 노드 (CPU only)** | 없음 (GPU 불필요) |
| 2 | mask hook 구현 + sanity 3종 | 코드 작성은 로컬/로그인 노드, 검증 forward는 GPU | **Job 0 (smoke)** → **Job 1 (sanity)** |
| 3 | 본 실험: 10조건 × 600문항 logit 평가 → `results.csv` | GPU | **Job 2A / Job 2B** (문항 shard 분할, §3) |
| 4 | M 조건 attention 로깅 재실행 → 프로파일링 데이터 | GPU | **Job 2A / 2B 내부의 2차 phase** (동일 shard) |
| 5 | shard 병합, 분석, fig1·fig2, McNemar, REPORT.md | **로그인 노드 (CPU only)** | 없음 |

- Job을 잡지 않은 GPU 프로세스는 즉시 강제 종료 대상이므로, **Yes/No 토큰 id 확정용 소량 생성(B-3)과 "first image" grounding 확인(C-4-2)도 전부 Job 0/1 안에서 수행**한다. 로그인 노드에서는 GPU를 절대 만지지 않는다.
- Interactive job 금지 준수: hook 디버깅이 필요해지면 interactive를 잡지 않고 **walltime 30분짜리 batch job(Job 0)을 반복 제출**하는 방식으로 통일한다.

## 2. 노드 선택과 token 계산

| 우선순위 | 구성 | token 계산 | 판단 |
|---|---|---|---|
| **1 (기본)** | **Node 3 (pleiades3) RTX 3090 24GB × 2** (1-GPU job 2개) | 1.0 × 2 = **2.0 ≤ 2.5** | **권장.** 3B BF16(~8GB)에 24GB 충분, job당 ncpus 제한 8로 가장 관대, EPYC 128c로 전처리 여유 최대 |
| 2 (폴백 A) | Node 3 3090 × 1 + Node 1 (pleiades1) 3090 × 1 | 1.0 + 1.0 = 2.0 | Node 3 1장만 가용할 때. 단 Node 1은 마스터 노드 — **`ncpus=4` 이하** (job명 `1_4_...`), CPU 부담 최소화 |
| 3 (폴백 B) | Node 4 (pleiades4) RTX A6000 48GB × 1 (job 2개 순차) | 1.5 × 1 = 1.5 | Node 3 만석 시. **job당 CPU 제한 6 — `ncpus=4` 권장** (job명 `1_4_...`). GPU 1개라 wall-clock 2배 |
| 4 (폴백 C) | Node 3 3090 × 1 + Node 4 A6000 × 1 | 1.0 + 1.5 = **2.5 (한도 정확히 소진)** | 가능하나 여유 0 — 최후 수단. 특이사항 시트에 시작·종료 시간 필수 기재 |
| 금지 | A6000 × 2 | 1.5 × 2 = 3.0 > 2.5 | **한도 초과, 불가** |
| 제외 | Node 2 (A100) | — | 주간 신청제 + 교수님 승인 필요. 24h feasibility에 절차 비용이 실익 초과 → 미사용 |

ncpus는 4의 배수 권장 정책에 따라 Node 3에서 `ncpus=8`(제한치), Node 1/4에서 `ncpus=4`.

> ⚠️ **필수 게이트 (검증자 지적)**: `select=1:ncpus=8:ngpus=1`만으로는 노드가 고정되지 않는다. 미고정 상태로 두 job을 제출했다가 스케줄러가 Node 4에 2개를 배치하면 **A6000×2 = 3.0 > 2.5 한도 초과**, Node 2 배치 시 무승인 A100 사용이 된다. **queue/host 고정 문법을 확정하기 전에는 GPU job을 제출하지 않는다** (§10 체크리스트 #1의 통과 조건).

## 3. GPU 2개 활용 전략

실험은 문항 간 의존이 전혀 없는 embarrassingly parallel 구조이고, 정책 7("알고리즘상 병렬화 불가 코드는 GPU 1개만")에 따라 **multi-GPU job 1개가 아니라 독립 1-GPU job 2개**로 제출한다. 분할 축 두 안 비교:

| | 안 1: 문항 분할 (권고) | 안 2: 기능 분할 |
|---|---|---|
| 구성 | Job 2A = 문항 shard 0 (300문항) × 10조건 + 해당 shard의 M-attention 프로파일링, Job 2B = shard 1 동일 | Job A = 본실험 전체, Job B = 프로파일링 전체 |
| 부하 균형 | **거의 완전 균등** — wall-clock 절반 | 심한 불균형 (A가 B의 ~5–8배) |
| 코드 | 단일 스크립트 + `--shard i --num-shards 2` 인자 | 스크립트 실행 경로 2종 분리 |
| 결과 병합 | shard 파일 concat — McNemar는 문항 단위 paired라 분할해도 통계 무영향 | 병합 불필요 |
| 양보 대응 | 어느 job을 내려도 남은 job 종료 후 resume 재제출로 복구 용이 | A를 내리면 본실험 전체 중단 |

**권고: 안 1 (문항 분할).** 안 2의 장점(프로파일링 격리)은 각 job 내부의 phase 순차 분리(본실험 → 프로파일링)로 동일하게 확보된다. 각 job 내부는 **문항-major 루프**(문항 1개 전처리 → 10조건 연속)로 이미지 전처리를 조건 간 재사용 — 실행 순서 최적화일 뿐 설계 변경이 아니다.

## 4. PBS job 설계와 스크립트 템플릿

### 4.1 Job 목록

| Job | 이름 (`GPU수_CPU수_isangmin_작업명`) | 내용 | walltime |
|---|---|---|---|
| 0 | `1_8_isangmin_sd_smoke` | 5문항 × 10조건 + Yes/No 토큰 id 확정 + span 수동확인 로그 + **문항당 시간 실측** | 00:30:00 |
| 1 | `1_8_isangmin_sd_sanity` | sanity 3종 (04 문서 §8) | 02:00:00 |
| 2A | `1_8_isangmin_sd_mainA` | shard 0: 본실험 300문항 × 10조건 → M-attention 프로파일링 shard 0 | 06:00:00 |
| 2B | `1_8_isangmin_sd_mainB` | shard 1: 동일 | 06:00:00 |

제출 흐름: 로그인 노드 stage 1 완료 → Job 0 → 로그 검토 → Job 1 → **sanity 3종 통과를 사람이 확인한 후에만** Job 2A·2B 동시 제출 (브리프 C-4). `qsub -W depend=afterok:` 자동 체이닝은 sanity 수치를 사람이 봐야 하므로 쓰지 않는다.

### 4.2 서버 접속 후 확인할 것 (제출 전 필수)

```bash
qstat -Q                      # queue 목록 (노드별 queue인지 default queue인지)
qstat -q                      # queue별 리소스 제한
pbsnodes -a                   # 노드명(pleiades3 등)과 GPU 리소스 키워드 (ngpus? gpus?)
qmgr -c "print server" 2>/dev/null   # default queue·기본값 (권한 없으면 skip)
qstat -f <실행중인 타인 jobid>        # 통용되는 Resource_List 형식 참고 (privacy 설정으로 차단될 수 있음)
/home1/s20225367/resmonitor/monitor.sh   # 현재 점유 현황
# 연구실 선배들의 기존 제출 스크립트(#PBS 헤더)를 구해 select 문법·queue 이름을 그대로 따를 것
# job 내에서 echo $CUDA_VISIBLE_DEVICES / nvidia-smi 로 GPU 격리 방식 검증
```

**미검증 가정 4건 (검증자 지적 — 접속 직후 확인, 어긋나면 계획 수정 후 진행):**
1. **스케줄러 계열**: PBS Pro가 아니라 Torque 계열이면 `select=1:ncpus=8:ngpus=1` 문법 전체가 무효 (`-l nodes=1:ppn=8:gpus=1` 형식) — 기존 스크립트 확인이 가장 확실.
2. **로그인 노드 = Node 1(마스터)인지**: 동일하면 stage 1/5의 CPU 작업(이미지 1,200장 다운로드·병합·분석) 강도를 낮추고 (다운로드는 네트워크 I/O 위주라 대체로 무방), 무거운 연산은 Node 3 CPU-only batch job으로 이관.
3. **로그인 노드의 아웃바운드 인터넷** (HF·GitHub·COCO): 06 문서는 인바운드 SSH 불가만 확인했다. 불가 시 폴백 — 연구실 내부 PC에서 받아 `scp`로 반입.
4. **GPU 리소스 키워드·노드 고정 문법**: `host=pleiades3` vs 노드별 queue — 확정 전 GPU job 제출 금지 (§2 게이트).

### 4.3 스크립트 템플릿 (Job 2A 예시 — 나머지는 이름·인자만 변경)

```bash
#!/bin/bash
#PBS -N 1_8_isangmin_sd_mainA
#PBS -q [QUEUE_NAME]                     # ← 확인 후 기입. 노드 고정이 queue 방식이면 여기서,
#PBS -l select=1:ncpus=8:ngpus=1         # ← host 방식이면 select에 :host=pleiades3 추가.
                                         #    [확정 전 제출 금지 — §2 게이트]
#PBS -l walltime=06:00:00
#PBS -j oe
#PBS -o /home1/isangmin/sourcedepth/logs/
# ↑ logs/ 디렉토리는 제출 전에 mkdir -p로 생성해 둘 것 (없으면 output 전달 실패 가능,
#   디렉토리 지정 동작 자체도 PBS 버전 의존 — Job 0에서 확인)

cd /home1/isangmin/sourcedepth           # $PBS_O_WORKDIR 사용 가능하나 절대경로가 안전

# conda activate는 set -u와 충돌하는 사례가 흔함 — activate 후에 엄격 모드 적용 (검증자 지적)
source /home1/isangmin/miniconda3/etc/profile.d/conda.sh
conda activate sourcedepth
set -euo pipefail

# compute node 인터넷 접근 미확인 → 완전 offline 강제 (§6 선다운로드 완료 전제)
export HF_HOME=/home1/isangmin/.cache/huggingface
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONHASHSEED=42

date; nvidia-smi; echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"

# Phase 1: 본실험 shard (checkpoint/resume 내장 — §8)
python scripts/03_run_main.py --pairs results/pairs.csv --shard 0 --num-shards 2 --resume --seed 42

# Phase 2: M 조건 attention 프로파일링 shard (eager + output_attentions, batch 1)
python scripts/04_run_attention_profile.py --pairs results/pairs.csv --shard 0 --num-shards 2 --resume --seed 42

date
```

- walltime 초과 시 보호는 **행 단위 append+flush(resume)가 실질 수단**이다. `trap ... TERM`은 bash가 foreground python 종료 전까지 trap을 실행하지 않아 대부분 로그를 남기지 못한다 (검증자 지적) — 필요 시 python 쪽 SIGTERM 핸들러로 구현.
- Job 0/1은 같은 골격에 이름·walltime·실행부만 교체. 폴백 노드 사용 시 **ncpus와 job명의 CPU수를 함께 수정** (`1_4_isangmin_sd_mainA`).

## 5. Walltime 추정 근거

**단가 추정 (3090, BF16, eager, batch 1):**
- 시퀀스: COCO 원본(~640×480) 기준 이미지당 대략 300–500 vision tokens. 2이미지 prefill ≈ 700–1,100 tokens.
- LLM prefill (3B, N=36 layers): 1k tokens ≈ 6 TFLOPs. **+ vision encoder (~0.67B)가 매 forward 재실행** — pixel_values 재사용은 전처리 재사용일 뿐 ViT 연산은 조건마다 반복되므로 최대 ~2배 추가 (검증자 지적: 초안은 LLM만 계산해 과소). 합산 forward당 **0.5–1.2초**로 잡는다.

| 항목 | 규모 | 추정 |
|---|---|---|
| 모델 로드 (공유 FS 콜드 캐시) | 1회 | 수 분 (NFS 콜드 캐시면 1–2분보다 느릴 수 있음) |
| 본실험 전체 | 6,000 forwards | 순수 50–120분 → I/O·hook 오버헤드 ×1.5 ⇒ **1.5–3h (1 GPU)** |
| 본실험 shard (job당) | 3,000 forwards | **0.8–1.5h** |
| 프로파일링 shard | 300 forwards (M만) | 단가 1.5–2× ⇒ **10–30분**, batch 1 고정 |
| **job 2A/2B walltime** | 합 ~2h | **여유 계수 ~3× → 06:00:00** |

**Job 0의 문항당 시간 실측으로 이 추정을 보정한 뒤 Job 2A/2B walltime을 확정하는 것은 선택이 아니라 필수다** (검증자 지적 — ViT 단가 불확실성 때문). Job 0의 30분은 50 forwards + 모델 로드 + 토큰 probe에 충분하며, 크게 초과하면 환경 이상 신호로 본다 (단, 최초 실행의 콜드 캐시 지연은 감안).

## 6. 모델·데이터 스테이징 (compute node 인터넷 미확인 대비)

확인 여부와 무관하게 성립하는 **로그인 노드 선다운로드 + job 완전 offline** 전략을 기본으로 한다.

```bash
# 전부 로그인 노드에서 (CPU 작업, GPU 무관)
export HF_HOME=/home1/isangmin/.cache/huggingface
# conda env는 /home1 (공유 FS)에 생성, 설치 후 pip freeze로 exact pin 확정
huggingface-cli download Qwen/Qwen2.5-VL-3B-Instruct    # ~8GB, 1회

# POPE: coco_pope_adversarial.json (+popular 보충분)
# COCO: instances_val2014.json + pairs.csv 확정 후 필요한 이미지만 개별 다운로드 (≤1,300장 ≈ 200–300MB)
#       val2014 전체 zip(~6GB) 금지 — 브리프 C-2 명시
```

- job 스크립트에서 `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` 강제 — compute node에 인터넷이 있어도 네트워크를 시도하지 않게 (offline 재현성 + 실패 모드 단순화). Job 0가 offline 캐시 로드의 최초 검증을 겸한다.
- 스토리지 ≈ 모델 8GB + conda env ~5GB + 이미지 0.3GB → 접속 직후 `quota -s` / `df -h /home1` 확인.
- 코드 반입: 로컬 → GitHub → 서버 clone (06 문서 §5). 데이터는 로컬 선준비 시 `rsync`로 반입 가능.
- 아웃바운드 인터넷 불가로 확인되면: BLOCKED 상당 로그를 남기고, **사전 승인된 폴백**(연구실 내부 PC에서 다운로드 후 scp)으로만 전환 (03 §B-10 — 임의 대안 실행 금지 원칙 준수).

## 7. 모니터링·에티켓

- **제출 전**: `monitor.sh`로 Node 3 가용 GPU 확인 후 제출. 만석이면 §2 폴백 순서대로.
- **GPU 특이사항 시트**: 본 계획은 token 2.0으로 한도 내이지만, 권장에 따라 **실험 시작·예상 종료 시각**(Job 2A/2B: 제출 + 6h 이내)을 기재. 폴백 C(2.5 정확 소진) 시 필수 기재.
- **양보 요청 대응**: 09–22시 기준 6시간 내 응답 (무응답 시 LIFO 강제 종료). 요청 시 **1-GPU job 단위로 내린다** — Job 2B를 `qdel`하고, 여유가 생기면 2B를 `--shard 1 --resume`으로 재제출. GPU가 계속 부족하면 Job 2A 종료 후 같은 GPU에서 `--shard 1 --resume`을 이어 돌린다 (§8과 동일 경로 — 실행 중인 2A가 shard를 동적으로 이어받는 것이 아님).
- **Interactive 금지**: 디버깅 포함 전 과정을 batch job으로 통일 (Job 0 반복 제출).
- 실행 중 점검: `qstat -u isangmin`, job 로그 tail, `monitor.sh`. 로그인 노드에서 무거운 CPU 연산을 장시간 돌리지 않는다.

## 8. 실패·재제출 전략

- **Checkpoint 단위 = (question_id, condition) 1행.** jsonl에 문항 완료 즉시 append + flush + fsync. `--resume`은 완료 조합 skip — walltime 초과·강제 종료·양보 후 **동일 스크립트 재제출만으로 이어서 실행**된다.
- **프로파일링 checkpoint**: `np.savez`는 append 불가 (검증자 지적) — 원본은 문항 단위 `attn_profile.jsonl` append로 저장하고 npz는 완료 후 최종 변환본으로만 생성 (04 문서 §6과 일치).
- **Walltime 초과**: 같은 job 재제출 (resume 보장). 2회 연속 초과 시 문항당 처리 시간 로그 근거로 walltime 재산정.
- **한쪽 job 소실**: 남은 job 종료 후 `--shard <소실쪽> --resume` 재제출.
- **OOM**: 브리프 C-1 지침 그대로 — batch 1 유지, 그래도 OOM이면 `max_pixels` 제한 (REPORT 기록). 코드 수정 후 Job 0부터 재검증.
- **BLOCKED**: 브리프 원칙대로 대안 실행 없이 로그 후 보고.

## 9. 스모크 테스트 선행 계획 (Job 0)

본실험 GPU 시간을 태우기 전에 **5문항 × 10조건, walltime 00:30:00**의 `1_8_isangmin_sd_smoke`로 검증: ① PBS 스크립트 자체 (queue·GPU 키워드·conda·CUDA_VISIBLE_DEVICES), ② offline 캐시 로드, ③ Yes/No 토큰 id 확정, ④ vision span 수동 확인 로그, ⑤ mask hook layer counting (`N=36` 실측 포함), ⑥ **문항당 처리 시간 실측 → §5 walltime 확정** (필수).

## 10. 실행 체크리스트 (시간순)

| # | 작업 | 위치 | 게이트 |
|---|---|---|---|
| 1 | `qstat -Q`, `pbsnodes -a`, 기존 스크립트 확보 → **§4.2 미검증 가정 4건 해소, 노드 고정 문법 확정** | 로그인 노드 | **미확정 시 GPU job 제출 금지** |
| 2 | conda env + HF 모델·POPE·COCO annotation 다운로드 (`HF_HOME` 고정), `mkdir -p logs`, `quota -s` 확인 | 로그인 노드 | |
| 3 | 페어링 → `pairs.csv` → 필요 이미지 개별 다운로드 | 로그인 노드 | |
| 4 | `monitor.sh` 확인 → Job 0 제출 → 로그 검토 + 문항당 시간 실측 → walltime 확정 | PBS | Job 0 전 항목 통과 |
| 5 | Job 1 제출 → sanity 3종 판정 | PBS | **sanity 미통과 시 본실험 진입 금지** |
| 6 | GPU 특이사항 시트 기재 → Job 2A·2B 동시 제출 | PBS | |
| 7 | 완료 확인 → shard 병합, fig1·fig2, McNemar, REPORT.md | 로그인 노드 | |
