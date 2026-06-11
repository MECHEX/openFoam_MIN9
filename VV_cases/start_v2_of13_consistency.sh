#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9"
LOG_DIR="$ROOT/VV_cases/_batch_logs"

mkdir -p "$LOG_DIR"
cd "$ROOT/VV_cases/V2_thermal/_code"
nohup python3 ./V2FluidConsistencyStudy.py all > "$LOG_DIR/V2_of13_all.log" 2>&1 < /dev/null &
echo $! > "$LOG_DIR/V2_of13_all.wslpid"
