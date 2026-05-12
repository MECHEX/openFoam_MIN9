#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

# Continue run007a from the latest decomposed checkpoint. This intentionally
# does not call decomposePar, so existing processor*/time directories are kept.

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run007a}"
NPROCS="${NPROCS:-20}"
TAG="${TAG:-20260508_np20_varProps_to6}"
END_TIME="${END_TIME:-6}"

cd "$CASE_DIR"
mkdir -p logs

perl -0pi -e "s/startFrom\s+\S+;/startFrom       latestTime;/" system/controlDict
perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         ${END_TIME};/" system/controlDict
perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" system/decomposeParDict

setsid mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel \
    > "logs/log.foamRun_parallel.${TAG}" 2>&1 < /dev/null &

echo "$!" > "logs/solver.${TAG}.pid"
echo "PID $(cat "logs/solver.${TAG}.pid")"
echo "LOG logs/log.foamRun_parallel.${TAG}"
