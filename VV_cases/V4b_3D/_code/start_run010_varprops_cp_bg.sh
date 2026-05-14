#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp}"
NPROCS="${NPROCS:-20}"
TAG="${TAG:-$(date +%Y%m%d_%H%M%S)_np${NPROCS}_varprops_cp}"

cd "$CASE_DIR"
mkdir -p logs

setsid mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
    > "logs/log.foamRun_parallel.${TAG}" 2>&1 < /dev/null &

pid=$!
echo "$pid" > "logs/mpirun.${TAG}.pid"
echo "PID $pid"
echo "LOG $CASE_DIR/logs/log.foamRun_parallel.${TAG}"
