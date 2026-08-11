#!/bin/bash
# 확장 실험 연쇄 (A6000 1장 순차 — 동시 실행 시 1.5×2=3.0 token으로 한도 초과라 의존성 강제):
#   ext(3B: L 세분화 + swap 프로파일링) → 7b_smoke(afterany) → 7b_sanity(afterok) → 7b_main(afterok)
# 7B는 결과 파일이 *_7b suffix로 분리되어 3B 사전 등록 결과를 건드리지 않는다.
set -e
ROOT=/home/isangmin/sourcedepth
cd $ROOT
mkdir -p logs/pbs
rm -f results/SMOKE_PASSED_7b results/SANITY_PASSED_7b

JE=$(qsub pbs/sd_ext.pbs)
echo "ext       : $JE"
J0=$(qsub -W depend=afterany:$JE pbs/sd7b_smoke.pbs)
echo "7b smoke  : $J0 (afterany:$JE)"
J1=$(qsub -W depend=afterok:$J0 pbs/sd7b_sanity.pbs)
echo "7b sanity : $J1 (afterok:$J0)"
J2=$(qsub -W depend=afterok:$J1 pbs/sd7b_main.pbs)
echo "7b main   : $J2 (afterok:$J1)"
echo
qstat -u isangmin || true
