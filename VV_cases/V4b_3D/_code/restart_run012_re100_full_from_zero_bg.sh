#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run012_re100_production}"
NPROCS="${NPROCS:-20}"
TAG="$(date +%Y%m%d_%H%M%S)_run012_re100_full_from_zero"

if [[ "$CASE_DIR" != /home/hexmachina/of_runs/V4b_3D_run012_re100_production ]]; then
  echo "Refusing unexpected CASE_DIR: $CASE_DIR" >&2
  exit 2
fi

cd "$CASE_DIR"
mkdir -p logs

find "$CASE_DIR" -maxdepth 1 -type d -name 'processor*' -exec rm -rf {} +
rm -rf "$CASE_DIR/postProcessing"
find "$CASE_DIR" -maxdepth 1 -type d -regex '.*/[0-9]+(\.[0-9]+)?' ! -name '0' -exec rm -rf {} +

perl -0pi -e 's/startFrom\s+\w+;/startFrom       startTime;/' system/controlDict
perl -0pi -e 's/startTime\s+[0-9.eE+-]+;/startTime       0;/' system/controlDict
perl -0pi -e 's/endTime\s+[0-9.eE+-]+;/endTime         10;/' system/controlDict

decomposePar -force > "logs/log.decomposePar.${TAG}" 2>&1

nohup mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
  > "logs/log.foamRun_parallel.${TAG}.full" 2>&1 </dev/null &

echo "$!" > "logs/pid.${TAG}.full"
echo "$TAG"
echo "PID $(cat "logs/pid.${TAG}.full")"
echo "Log $CASE_DIR/logs/log.foamRun_parallel.${TAG}.full"
