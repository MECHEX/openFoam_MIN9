#!/usr/bin/env bash

# Launch a prepared run011 GCI case in the background.

CASE_DIR="${CASE_DIR:-}"
NPROCS="${NPROCS:-20}"
TAG="${TAG:-$(date +%Y%m%d_%H%M%S)_run011_gci}"

if [[ -z "$CASE_DIR" ]]; then
    echo "Set CASE_DIR to a prepared run011 GCI case." >&2
    exit 1
fi

if [[ ! -d "$CASE_DIR" ]]; then
    echo "Missing case directory: $CASE_DIR" >&2
    exit 2
fi

source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$CASE_DIR"
mkdir -p logs

if [[ ! -d processor0 ]]; then
    decomposePar -force > "logs/log.decomposePar.${TAG}" 2>&1
fi

setsid mpirun --oversubscribe -np "${NPROCS}" foamRun -solver fluid -parallel \
    > "logs/log.foamRun_parallel.${TAG}" 2>&1 < /dev/null &

pid=$!
echo "$pid" > "logs/solver.${TAG}.pid"

echo "Launched ${CASE_DIR}"
echo "TAG=${TAG}"
echo "PID=${pid}"
echo "Log=${CASE_DIR}/logs/log.foamRun_parallel.${TAG}"
