#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run018_re159_production}"
NPROCS="${NPROCS:-20}"
TAG="$(date +%Y%m%d_%H%M%S)_run018_re159_continue_full"

cd "$CASE_DIR"
mkdir -p logs

perl -0pi -e "s/startFrom\s+\w+;/startFrom       latestTime;/" system/controlDict

nohup mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
  > "logs/log.foamRun_parallel.${TAG}.full" 2>&1 </dev/null &

echo "$!" > "logs/pid.${TAG}.full"
echo "$TAG"
echo "PID $(cat "logs/pid.${TAG}.full")"
echo "Log $CASE_DIR/logs/log.foamRun_parallel.${TAG}.full"
