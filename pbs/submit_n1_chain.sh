set -e
cd /home/isangmin/sourcedepth
mkdir -p logs/pbs
rm -f results/SMOKE_PASSED_7b results/SANITY_PASSED_7b
JG=$(qsub pbs/sd_gate_n1.pbs);                         echo "1) gate      : $JG"
JE=$(qsub -W depend=afterany:$JG pbs/sd_ext_n1.pbs);   echo "2) ext       : $JE"
J0=$(qsub -W depend=afterany:$JE pbs/sd7b_smoke_n1.pbs);  echo "3) 7b smoke  : $J0"
J1=$(qsub -W depend=afterok:$J0 pbs/sd7b_sanity_n1.pbs);  echo "4) 7b sanity : $J1"
J2=$(qsub -W depend=afterok:$J1 pbs/sd7b_main_n1.pbs);    echo "5) 7b main   : $J2"
