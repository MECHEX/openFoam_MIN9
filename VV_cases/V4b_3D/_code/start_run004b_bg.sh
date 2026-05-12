#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run004b}"
NPROCS="${NPROCS:-8}"
TAG="${TAG:-20260505}"

cd "$CASE_DIR"
mkdir -p logs

perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" system/decomposeParDict

decomposePar -force > "logs/log.decomposePar.${TAG}" 2>&1

setsid mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
    > "logs/log.foamRun_parallel.${TAG}" 2>&1 < /dev/null &

echo "$!" > "logs/solver.${TAG}.pid"
echo "PID $(cat "logs/solver.${TAG}.pid")"
echo "LOG logs/log.foamRun_parallel.${TAG}"
