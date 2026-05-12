#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE_DIR="/home/hexmachina/of_runs/V4b_3D_run008"
EXPORT_DIR="/home/hexmachina/of_runs/V4b_3D_run008_q_lambda2_013"
TIMES="2.72,7.44,6.88,3.84,2.16,5.04"
NPROCS="${NPROCS:-20}"

mkdir -p "$EXPORT_DIR/logs"
cd "$CASE_DIR"

echo "Computing Q, Lambda2, and vorticity for: $TIMES"
mpirun --oversubscribe -np "$NPROCS" foamPostProcess -parallel -func Q -time "$TIMES" \
    > "$EXPORT_DIR/logs/log.Q" 2>&1
mpirun --oversubscribe -np "$NPROCS" foamPostProcess -parallel -func Lambda2 -time "$TIMES" \
    > "$EXPORT_DIR/logs/log.Lambda2" 2>&1
mpirun --oversubscribe -np "$NPROCS" foamPostProcess -parallel -func vorticity -time "$TIMES" \
    > "$EXPORT_DIR/logs/log.vorticity" 2>&1

echo "Exporting decomposed VTK files outside Git: $EXPORT_DIR/vtk_processors"
rm -rf "$EXPORT_DIR/vtk" "$EXPORT_DIR/vtk_processors" VTK
find processor* -maxdepth 1 -type d -name VTK -exec rm -rf {} +
mpirun --oversubscribe -np "$NPROCS" foamToVTK -parallel -useTimeName -time "$TIMES" -fields '(Q Lambda2 vorticity T U)' \
    > "$EXPORT_DIR/logs/log.foamToVTK" 2>&1
mkdir -p "$EXPORT_DIR/vtk_processors"
for proc in processor*; do
    if [[ -d "$proc/VTK" ]]; then
        mkdir -p "$EXPORT_DIR/vtk_processors/$proc"
        mv "$proc/VTK" "$EXPORT_DIR/vtk_processors/$proc/VTK"
    fi
done
if [[ -d VTK ]]; then
    mv VTK "$EXPORT_DIR/vtk_links"
fi

echo "Done"
