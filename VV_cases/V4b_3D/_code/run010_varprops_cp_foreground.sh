#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp}"
NPROCS="${NPROCS:-20}"
TAG="${TAG:-20260514_np20_varprops_cp}"

cd "$CASE_DIR"
mkdir -p logs
{
    echo "runner pid: $$"
    echo "date: $(date)"
    echo "case: $CASE_DIR"
    echo "foamRun: $(command -v foamRun)"
    echo "mpirun: $(command -v mpirun)"
} > "logs/wsl_runner.${TAG}.log"
echo "$$" > "logs/wsl_runner.${TAG}.pid"

exec mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
    > "logs/log.foamRun_parallel.${TAG}" 2>&1
