#!/usr/bin/env bash

source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE="/home/hexmachina/of_runs/V4b_3D_run024_re200_fullAirPropsT_from_t10_np5"
NPROCS=5
TAG="$(date +%Y%m%d_%H%M%S)_fullAirPropsT_from_t10_to14_np5"

cd "$CASE"
mkdir -p logs

foamDictionary system/controlDict -entry startFrom -set latestTime >/dev/null
foamDictionary system/controlDict -entry stopAt -set endTime >/dev/null
foamDictionary system/controlDict -entry endTime -set 14 >/dev/null
foamDictionary system/controlDict -entry writeInterval -set 0.08 >/dev/null
foamDictionary system/controlDict -entry purgeWrite -set 0 >/dev/null

log_file="logs/log.foamRun.${TAG}.full"
pid_file="logs/pid.${TAG}.full"

nohup mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
  > "$log_file" 2>&1 </dev/null &

echo "$!" > "$pid_file"
echo "PID $(cat "$pid_file")"
echo "LOG $CASE/$log_file"
