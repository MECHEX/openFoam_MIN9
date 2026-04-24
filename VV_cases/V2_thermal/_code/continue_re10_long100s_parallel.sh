#!/usr/bin/env bash

# Source OpenFOAM before enabling nounset because the vendor bashrc touches
# variables that are not always pre-defined in non-interactive shells.
source /home/kik/openfoam/OpenFOAM-v2512/etc/bashrc 2>/dev/null
set -euo pipefail

CASE_DIR="/mnt/c/openfoam-case/VV_cases/V2_thermal_run002/Re10_long100s"

cd "$CASE_DIR"
mkdir -p logs

checkMesh > logs/log.checkMesh 2>&1
decomposePar -force > logs/log.decomposePar 2>&1
mpirun -np 10 buoyantBoussinesqPimpleFoam -parallel > logs/log.buoyantBoussinesqPimpleFoam 2>&1
