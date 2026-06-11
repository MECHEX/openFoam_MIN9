#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9"
LOG_DIR="$ROOT/VV_cases/_batch_logs"

mkdir -p "$LOG_DIR"
cd "$ROOT/VV_cases/V1_solver/_code"
nohup python3 ./V1ProductionLikeStudy.py all > "$LOG_DIR/V1_prodlike_all.log" 2>&1 < /dev/null &
echo $! > "$LOG_DIR/V1_prodlike_all.wslpid"

