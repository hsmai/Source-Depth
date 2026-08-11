#!/bin/bash
# 자가복구 watchdog — 로그인 노드에서 setsid로 detach 실행 (사용자 SSH 종료와 무관하게 생존).
# 10분마다: (1) 우리 job이 하나라도 살아있으면 대기, (2) 전부 죽었는데 산출물이 미완이면
# 해당 단계를 재제출. 모든 스크립트가 resume-safe이므로 재제출 = 이어서 실행.
# 종료 조건: 전 단계 완료 또는 각 단계 재제출 3회 초과(무한루프 방지).
ROOT=/home/isangmin/sourcedepth
cd $ROOT
LOG=$ROOT/logs/watchdog.log
PY=$ROOT/.venv/bin/python
declare -A RETRY

log() { echo "[$(date '+%F %T')] $*" >> $LOG; }

count() { [ -f "$1" ] && wc -l < "$1" || echo 0; }

stage_incomplete() {
  # 반환: 미완인 첫 단계 이름 (없으면 빈 문자열)
  [ "$(count results/rel_results.jsonl)" -lt 2400 ] && { echo gate; return; }
  [ "$(count results/headwise_profile.jsonl)" -lt 600 ] && { echo gate; return; }
  [ ! -f results/compaction_bench.json ] && { echo gate; return; }
  [ "$(count results/alloc_results.jsonl)" -lt 8400 ] && { echo gate2; return; }
  [ ! -f results/alpha_knob.json ] && { echo gate2; return; }
  [ "$(count results/attn_profile_swapped.jsonl)" -lt 600 ] && { echo ext; return; }
  [ "$(count results/raw_results_7b.jsonl)" -lt 6000 ] && { echo sevenb; return; }
  echo ""
}

submit() {
  case "$1" in
    gate)   qsub pbs/sd_gate_n1.pbs ;;
    gate2)  qsub pbs/sd_gate2_n1.pbs ;;
    ext)    qsub pbs/sd_ext_n1.pbs ;;
    sevenb) J=$(qsub pbs/sd7b_smoke_n1.pbs); J2=$(qsub -W depend=afterok:$J pbs/sd7b_sanity_n1.pbs); qsub -W depend=afterok:$J2 pbs/sd7b_main_n1.pbs ;;
  esac
}

log "watchdog 시작 (pid $$)"
MISS=0
for i in $(seq 1 200); do          # 최대 ~33시간
  # 주의: qstat 기본 출력은 job 이름을 '1_4_isang*'로 절단한다 — 전체 이름으로 grep하면
  # 항상 0이 되어 중복 제출을 유발한다 (실제로 겪은 버그). 절단된 접두사로 매칭할 것.
  ALIVE=$(qstat -u isangmin 2>/dev/null | grep -cE "1_4_isang|1_8_isang" || true)
  STAGE=$(stage_incomplete)
  if [ -z "$STAGE" ]; then
    log "전 단계 완료 — watchdog 종료"
    $PY scripts/10_gate_charts.py >> $LOG 2>&1 || true
    $PY scripts/13_alpha_knob.py >> $LOG 2>&1 || true
    exit 0
  fi
  if [ "$ALIVE" -eq 0 ]; then
    MISS=$((MISS+1))
    if [ "$MISS" -lt 2 ]; then     # 2회 연속 확인 후에만 재제출 (일시적 qstat 오류 방어)
      log "job 미발견 1회차 (STAGE=$STAGE) — 다음 주기 재확인"
    else
      N=${RETRY[$STAGE]:-0}
      if [ "$N" -ge 3 ]; then
        log "STAGE=$STAGE 재시도 3회 초과 — 중단 (사람 확인 필요)"
        exit 1
      fi
      RETRY[$STAGE]=$((N+1))
      OUT=$(submit "$STAGE" 2>&1)
      log "job 없음 + STAGE=$STAGE 미완 → 재제출 (${RETRY[$STAGE]}회차): $OUT"
      MISS=0
    fi
  else
    MISS=0
    log "STAGE=$STAGE 진행 중 (job $ALIVE개 활성)"
  fi
  sleep 600
done
log "watchdog 루프 상한 도달"
