#!/bin/bash
set -eo pipefail

BASE="/mnt/c/openfoam-case/VV_cases/V1_solver_run002"
CASES=(
  "b030_medium_Re095"
  "b030_medium_Re100"
  "b0375_medium_Re110"
  "b0375_medium_Re120"
  "b050_medium_Re120"
  "b050_medium_Re130"
)

for c in "${CASES[@]}"; do
  echo "=== RUN ${c} ==="
  cd "${BASE}/${c}"
  bash Allrun
done
