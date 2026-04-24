#!/bin/bash
# run002_pilot_continue.sh
# Continues the pilot subset from where it stopped.
# - b030_medium_Re100: restart pimpleFoam from latestTime (mesh already built)
# - remaining 4 pilot cases: full Allrun
#
# Run from WSL (OpenFOAM already sourced in environment, or source manually once):
#   source /home/kik/openfoam/OpenFOAM-v2512/etc/bashrc
#   bash /mnt/c/Users/kik/My\ Drive/.../V1_solver/run002_pilot_continue.sh

set -eo pipefail

BASE="/mnt/c/openfoam-case/VV_cases/V1_solver_run002"

# ── 1. Restart b030_medium_Re100 from latestTime ──────────────────────────────
echo "=== RESTART b030_medium_Re100 (from latestTime) ==="
cd "${BASE}/b030_medium_Re100"
# patch controlDict: startFrom latestTime
sed -i 's/startFrom\s\+startTime/startFrom latestTime/' system/controlDict
pimpleFoam | tee -a logs/pimpleFoam.log
# restore original controlDict setting
sed -i 's/startFrom\s\+latestTime/startFrom startTime/' system/controlDict

# ── 2. Fresh runs for the remaining pilot cases ───────────────────────────────
REMAINING=(
  "b0375_medium_Re110"
  "b0375_medium_Re120"
  "b050_medium_Re120"
  "b050_medium_Re130"
)

for c in "${REMAINING[@]}"; do
  echo "=== RUN ${c} ==="
  cd "${BASE}/${c}"
  bash Allrun
done

echo ""
echo "Pilot subset done. Run _code/V1Run2Study.py analyze to collect results."
