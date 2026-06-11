#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run015_re160_production}"
NPROCS="${NPROCS:-20}"
TAG="$(date +%Y%m%d_%H%M%S)_run015_re160_full"

cd "$CASE_DIR"
mkdir -p logs

checkMesh > "logs/log.checkMesh.${TAG}" 2>&1
decomposePar -force > "logs/log.decomposePar.${TAG}" 2>&1

nohup mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
  > "logs/log.foamRun_parallel.${TAG}.full" 2>&1 </dev/null &

echo "$!" > "logs/pid.${TAG}.full"
echo "$TAG"
echo "PID $(cat "logs/pid.${TAG}.full")"
echo "Log $CASE_DIR/logs/log.foamRun_parallel.${TAG}.full"
