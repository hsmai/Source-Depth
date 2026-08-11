#!/bin/bash
# GPU 1장(A6000, pleiades4) 순차 체인 — 사용자 지시 2026-08-11.
# 우선순위: 미팅 가치가 높은 순서. afterany로 연결해 앞 job 실패가 뒤를 막지 않게 한다
# (7B 내부 게이트만 afterok — sanity 미통과 시 본실험 진입 금지 원칙 유지).
#   1) gate : 07 relational / 08 head-wise controller / 09 실측 compaction TTFT   [최우선]
#   2) ext  : L 그리드 세분화 + 순서 뒤집기 프로파일링
#   3) 7B   : smoke → sanity(afterok) → main(afterok)   [일반화 검증]
set -e
ROOT=/home/isangmin/sourcedepth
cd $ROOT
mkdir -p logs/pbs
rm -f results/SMOKE_PASSED_7b results/SANITY_PASSED_7b

JG=$(qsub pbs/sd_gate.pbs);                          echo "1) gate      : $JG"
JE=$(qsub -W depend=afterany:$JG pbs/sd_ext.pbs);    echo "2) ext       : $JE"
J0=$(qsub -W depend=afterany:$JE pbs/sd7b_smoke.pbs);  echo "3) 7b smoke  : $J0"
J1=$(qsub -W depend=afterok:$J0 pbs/sd7b_sanity.pbs);  echo "4) 7b sanity : $J1"
J2=$(qsub -W depend=afterok:$J1 pbs/sd7b_main.pbs);    echo "5) 7b main   : $J2"
echo
qstat -u isangmin || true
echo
echo "GPU 동시 사용: 항상 1장 (의존성으로 직렬화). queue=pleiades4 (A6000)"
