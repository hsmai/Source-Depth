#!/bin/bash
# 자동 연쇄 제출: smoke → sanity(afterok) → main(afterok) → analyze(afterany)
# - afterok: 선행 job exit 0일 때만 실행. 선행 실패 시 PBS가 후속을 삭제할 수 있으므로
#   각 GPU job이 EXIT trap으로 05_analyze를 자체 실행해 STATUS.md를 보장한다.
# - stale flag 제거: 재제출 시 이전 실행의 SMOKE/SANITY_PASSED로 게이트가 무력화되는 것 방지.
set -e
ROOT=/home/isangmin/sourcedepth
cd $ROOT
mkdir -p logs/pbs
rm -f results/SMOKE_PASSED results/SANITY_PASSED

J0=$(qsub pbs/sd_smoke.pbs)
echo "smoke   : $J0"
J1=$(qsub -W depend=afterok:$J0 pbs/sd_sanity.pbs)
echo "sanity  : $J1 (afterok:$J0)"
J2=$(qsub -W depend=afterok:$J1 pbs/sd_main.pbs)
echo "main    : $J2 (afterok:$J1)"
J3=$(qsub -W depend=afterany:$J2 pbs/sd_analyze.pbs)
echo "analyze : $J3 (afterany:$J2)"
echo
qstat -u isangmin || true
echo
echo "체인 제출 완료. 확인: qstat -u isangmin / 로그: logs/pbs/ / 상태: results/STATUS.md"
