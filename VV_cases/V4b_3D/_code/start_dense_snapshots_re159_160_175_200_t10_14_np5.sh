#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

NPROCS="${NPROCS:-5}"
START_TIME="${START_TIME:-10}"
END_TIME="${END_TIME:-14}"
WRITE_INTERVAL="${WRITE_INTERVAL:-0.005}"
TAG="$(date +%Y%m%d_%H%M%S)_dense_t10_14_np5"

declare -A SRC=(
  [re159]="/home/hexmachina/of_runs/V4b_3D_run018_re159_production"
  [re160]="/home/hexmachina/of_runs/V4b_3D_run015_re160_production"
  [re175]="/home/hexmachina/of_runs/V4b_3D_run014_re175_production"
  [re200]="/home/hexmachina/of_runs/V4b_3D_run008"
)

declare -A DST=(
  [re159]="/home/hexmachina/of_runs/V4b_3D_run019_re159_dense_t10_14_np5"
  [re160]="/home/hexmachina/of_runs/V4b_3D_run020_re160_dense_t10_14_np5"
  [re175]="/home/hexmachina/of_runs/V4b_3D_run021_re175_dense_t10_14_np5"
  [re200]="/home/hexmachina/of_runs/V4b_3D_run022_re200_dense_t10_14_np5"
)

prepare_case() {
  local key="$1"
  local src="${SRC[$key]}"
  local dst="${DST[$key]}"

  if [[ ! -d "$src" ]]; then
    echo "Missing source case: $src" >&2
    exit 2
  fi
  if [[ -e "$dst" ]]; then
    echo "Destination already exists, leaving it untouched: $dst" >&2
    return
  fi

  echo "==> Reconstructing $key at t=$START_TIME from $src"
  (cd "$src" && reconstructPar -time "$START_TIME" > "logs/log.reconstructPar.${TAG}.${key}" 2>&1)

  if [[ ! -d "$src/$START_TIME" ]]; then
    echo "Reconstruction did not create $src/$START_TIME" >&2
    exit 3
  fi

  echo "==> Creating dense continuation case $dst"
  mkdir -p "$dst/logs"
  cp -a "$src/0" "$src/constant" "$src/system" "$src/$START_TIME" "$dst/"
  touch "$dst/${key}_dense.foam" "$dst/V4b_${key}_dense.foam"

  python3 - "$dst/system/controlDict" "$START_TIME" "$END_TIME" "$WRITE_INTERVAL" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
start = sys.argv[2]
end = sys.argv[3]
write = sys.argv[4]
text = path.read_text()
text = re.sub(r"startFrom\s+\w+;", "startFrom       startTime;", text)
text = re.sub(r"startTime\s+[0-9.eE+-]+;", f"startTime       {start};", text)
text = re.sub(r"endTime\s+[0-9.eE+-]+;", f"endTime         {end};", text)
text = re.sub(r"writeInterval\s+[0-9.eE+-]+;", f"writeInterval   {write};", text)
text = re.sub(r"purgeWrite\s+\d+;", "purgeWrite      0;", text)
path.write_text(text)
PY

  perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" "$dst/system/decomposeParDict"

  cat > "$dst/DENSE_SNAPSHOT_RUN.md" <<EOF
# Dense snapshot continuation

- Source case: $src
- Start time: $START_TIME s
- End time: $END_TIME s
- Full-field and functionObject writeInterval: $WRITE_INTERVAL s
- MPI ranks: $NPROCS
- Purpose: high-snapshot dataset for coherence/phase/EPOD/SPOD-ready post-processing.
- Created tag: $TAG
EOF

  echo "==> Decomposing $dst to $NPROCS processors"
  (cd "$dst" && decomposePar -force > "logs/log.decomposePar.${TAG}.${key}" 2>&1)
}

start_case() {
  local key="$1"
  local dst="${DST[$key]}"
  echo "==> Starting $key dense run in $dst"
  (
    cd "$dst"
    nohup mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
      > "logs/log.foamRun_parallel.${TAG}.${key}.full" 2>&1 </dev/null &
    echo "$!" > "logs/pid.${TAG}.${key}.full"
    echo "$key PID $(cat "logs/pid.${TAG}.${key}.full")"
    echo "$key LOG $dst/logs/log.foamRun_parallel.${TAG}.${key}.full"
  )
}

for key in re159 re160 re175 re200; do
  prepare_case "$key"
done

for key in re159 re160 re175 re200; do
  start_case "$key"
done

echo "Started dense snapshot runs with tag $TAG"
