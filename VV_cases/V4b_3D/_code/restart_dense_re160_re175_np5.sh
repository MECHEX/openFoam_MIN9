#!/usr/bin/env bash

source /opt/openfoam13/etc/bashrc
set -euo pipefail

NPROCS=5
TAG="$(date +%Y%m%d_%H%M%S)_dense_restart_np5"

declare -A CASES=(
  [re160]="/home/hexmachina/of_runs/V4b_3D_run020_re160_dense_t10_14_np5"
  [re175]="/home/hexmachina/of_runs/V4b_3D_run021_re175_dense_t10_14_np5"
)

for key in re160 re175; do
  case_dir="${CASES[$key]}"
  cd "$case_dir"
  mkdir -p logs
  log_file="logs/log.foamRun_parallel.${TAG}.${key}.full"
  pid_file="logs/pid.${TAG}.${key}.full"

  nohup mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
    > "$log_file" 2>&1 </dev/null &

  echo "$!" > "$pid_file"
  echo "$key PID $(cat "$pid_file")"
  echo "$key LOG $case_dir/$log_file"
done
