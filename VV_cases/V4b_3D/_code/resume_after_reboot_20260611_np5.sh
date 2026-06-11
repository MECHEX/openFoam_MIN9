#!/usr/bin/env bash

source /opt/openfoam13/etc/bashrc
set -euo pipefail

NPROCS="${NPROCS:-5}"
TAG="$(date +%Y%m%d_%H%M%S)_resume_after_reboot_np5"

declare -A CASES=(
  [re160_dense]="/home/hexmachina/of_runs/V4b_3D_run020_re160_dense_t10_14_np5"
  [re175_dense]="/home/hexmachina/of_runs/V4b_3D_run021_re175_dense_t10_14_np5"
  [re200_dense]="/home/hexmachina/of_runs/V4b_3D_run022_re200_dense_t10_14_np5"
  [re200_airPropsT]="/home/hexmachina/of_runs/V4b_3D_run024_re200_fullAirPropsT_from_t10_np5"
)

for key in re160_dense re175_dense re200_dense re200_airPropsT; do
  case_dir="${CASES[$key]}"
  if [[ ! -d "$case_dir" ]]; then
    echo "Missing case: $case_dir" >&2
    exit 2
  fi

  cd "$case_dir"
  mkdir -p logs

  foamDictionary system/controlDict -entry startFrom -set latestTime >/dev/null
  foamDictionary system/controlDict -entry stopAt -set endTime >/dev/null
  foamDictionary system/controlDict -entry endTime -set 14 >/dev/null
  foamDictionary system/controlDict -entry purgeWrite -set 0 >/dev/null

  perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" system/decomposeParDict

  log_file="logs/log.foamRun_parallel.${TAG}.${key}.full"
  pid_file="logs/pid.${TAG}.${key}.full"

  nohup mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
    > "$log_file" 2>&1 </dev/null &

  echo "$!" > "$pid_file"
  echo "$key PID $(cat "$pid_file")"
  echo "$key LOG $case_dir/$log_file"
done

echo "Resume jobs started with tag $TAG"

