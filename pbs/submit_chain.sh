#!/bin/bash
# 자동 연쇄 제출: smoke → sanity(afterok) → main(afterok) → analyze(afterany)
# afterok = 선행 job이 exit 0일 때만 실행 (sanity/BLOCKED 게이트가 코드 안에 있음)
# afterany = 선행 job 종료 시 무조건 실행 (STATUS.md 생성 보장)
set -e
ROOT=/home/isangmin/sourcedepth
cd $ROOT
mkdir -p logs/pbs

J0=$(qsub pbs/sd_smoke.pbs)
echo "smoke   : $J0"
J1=$(qsub -W depend=afterok:$J0 pbs/sd_sanity.pbs)
echo "sanity  : $J1 (afterok:$J0)"
J2=$(qsub -W depend=afterok:$J1 pbs/sd_main.pbs)
echo "main    : $J2 (afterok:$J1)"
J3=$(qsub -W depend=afterany:$J2 pbs/sd_analyze.pbs)
echo "analyze : $J3 (afterany:$J2)"
echo
qstat -u isangmin
echo
echo "체인 제출 완료. 확인: qstat -u isangmin / 로그: logs/pbs/"
