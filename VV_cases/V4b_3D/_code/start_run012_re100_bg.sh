#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run012_re100_production}"
NPROCS="${NPROCS:-20}"
TAG="$(date +%Y%m%d_%H%M%S)_run012_re100"

cd "$CASE_DIR"
mkdir -p logs

checkMesh > "logs/log.checkMesh.${TAG}" 2>&1
decomposePar -force > "logs/log.decomposePar.${TAG}" 2>&1

cp system/controlDict "system/controlDict.full.${TAG}"
perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         0.1;/" system/controlDict
mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
  > "logs/log.foamRun_parallel.${TAG}.smoke" 2>&1
cp "system/controlDict.full.${TAG}" system/controlDict

perl -0pi -e "s/startFrom\s+\w+;/startFrom       latestTime;/" system/controlDict

nohup mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
  > "logs/log.foamRun_parallel.${TAG}.full" 2>&1 </dev/null &

echo "$!" > "logs/pid.${TAG}.full"
echo "Started full run PID $(cat "logs/pid.${TAG}.full")"
echo "Full log: $CASE_DIR/logs/log.foamRun_parallel.${TAG}.full"
