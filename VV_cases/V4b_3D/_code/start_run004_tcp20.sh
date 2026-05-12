#!/usr/bin/env bash
set -euo pipefail

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run004}"
SESSION="${SESSION:-run004_tcp20}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-0.05}"
WRITE_INTERVAL="${WRITE_INTERVAL:-0.01}"
LOG_SUFFIX="${LOG_SUFFIX:-${NPROCS}.tcp}"

cd "$CASE_DIR"

cat > system/decomposeParDict <<EOF
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      decomposeParDict;
}

numberOfSubdomains ${NPROCS};

method          scotch;
EOF

foamDictionary system/controlDict -entry startFrom -set latestTime
foamDictionary system/controlDict -entry endTime -set "$END_TIME"
foamDictionary system/controlDict -entry writeInterval -set "$WRITE_INTERVAL"

rm -rf processor*
decomposePar -force > "logs/log.decomposePar.${LOG_SUFFIX}" 2>&1

tmux kill-session -t "$SESSION" 2>/dev/null || true
tmux new-session -d -s "$SESSION" \
    "cd '$CASE_DIR'; source /opt/openfoam13/etc/bashrc; mpirun --use-hwthread-cpus --mca pml ob1 --mca btl self,tcp -np ${NPROCS} foamRun -solver fluid -parallel > logs/log.foamRun_parallel.${LOG_SUFFIX} 2>&1"

echo "Started tmux session: $SESSION"
echo "Case: $CASE_DIR"
echo "Log: $CASE_DIR/logs/log.foamRun_parallel.${LOG_SUFFIX}"
