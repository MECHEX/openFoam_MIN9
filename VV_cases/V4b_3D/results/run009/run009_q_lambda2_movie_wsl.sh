#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

# Post-process run009 dense fields into Q/Lambda2/vorticity VTK files for
# animation. Run this after the solver has completed, or set a shorter TIMES
# range for a partial movie test.

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run009_varprops_movie}"
EXPORT_DIR="${EXPORT_DIR:-/home/hexmachina/of_runs/V4b_3D_run009_varprops_movie_q_lambda2_movie}"
DEFAULT_TIMES_FILE="/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/results/run009/data/001/run009_001_48_phase_times.txt"
TIMES_FILE="${TIMES_FILE:-$DEFAULT_TIMES_FILE}"
if [[ -z "${TIMES:-}" && -f "$TIMES_FILE" ]]; then
    TIMES="$(<"$TIMES_FILE")"
fi
TIMES="${TIMES:-2:10}"
NPROCS="${NPROCS:-20}"

mkdir -p "$EXPORT_DIR/logs"
cd "$CASE_DIR"

echo "Computing Q, Lambda2, and vorticity for time selection: $TIMES"
mpirun --oversubscribe -np "$NPROCS" foamPostProcess -parallel -func Q -time "$TIMES" \
    > "$EXPORT_DIR/logs/log.Q" 2>&1
mpirun --oversubscribe -np "$NPROCS" foamPostProcess -parallel -func Lambda2 -time "$TIMES" \
    > "$EXPORT_DIR/logs/log.Lambda2" 2>&1
mpirun --oversubscribe -np "$NPROCS" foamPostProcess -parallel -func vorticity -time "$TIMES" \
    > "$EXPORT_DIR/logs/log.vorticity" 2>&1

echo "Exporting decomposed VTK files outside Git: $EXPORT_DIR/vtk_processors"
rm -rf "$EXPORT_DIR/vtk_processors" "$EXPORT_DIR/vtk_links" VTK
find processor* -maxdepth 1 -type d -name VTK -exec rm -rf {} +
mpirun --oversubscribe -np "$NPROCS" foamToVTK -parallel -useTimeName -time "$TIMES" -fields '(Q Lambda2 vorticity T U rho)' \
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
