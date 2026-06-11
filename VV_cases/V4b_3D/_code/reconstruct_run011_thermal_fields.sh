#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

for case_dir in \
  /home/hexmachina/of_runs/V4b_3D_run011_gci_coarse \
  /home/hexmachina/of_runs/V4b_3D_run011_gci_fine
do
  cd "$case_dir"
  mkdir -p logs
  reconstructPar -time '2:3' -fields '(T phi)' \
    > logs/log.reconstructPar_T_phi_2_3_thermal_gci 2>&1
  tail -n 20 logs/log.reconstructPar_T_phi_2_3_thermal_gci
done
