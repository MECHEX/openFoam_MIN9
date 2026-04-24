#!/usr/bin/env bash
set -euo pipefail

CASE_NAME="${1:?Usage: run_ogrid_case_tmux.sh <case_name> [session_name] [np]}"
SESSION_NAME="${2:-v2_${CASE_NAME}}"
NP="${3:-15}"

OF_BASHRC="${OF_BASHRC:-/home/kik/openfoam/OpenFOAM-v2512/etc/bashrc}"
CASE_DIR="/mnt/c/openfoam-case/VV_cases/V2_thermal_run004/${CASE_NAME}"
LOG_FILE="${CASE_DIR}/logs/log.buoyantBoussinesqPimpleFoam"

if [[ ! -f "${OF_BASHRC}" ]]; then
    echo "Missing OpenFOAM bashrc: ${OF_BASHRC}" >&2
    exit 2
fi

if [[ ! -d "${CASE_DIR}" ]]; then
    echo "Missing case directory: ${CASE_DIR}" >&2
    exit 2
fi

mkdir -p "${CASE_DIR}/logs"

if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
    echo "session_exists ${SESSION_NAME}"
    tmux list-sessions
    exit 0
fi

cmd="source \"${OF_BASHRC}\" 2>/dev/null; cd \"${CASE_DIR}\"; foamDictionary system/controlDict -entry stopAt -set endTime >/dev/null 2>&1 || true; echo --- resume \$(date -Is) --- >> \"${LOG_FILE}\"; if [[ ! -d processor0 ]]; then if [[ -f system/setExprFieldsDict ]]; then setExprFields >> \"${CASE_DIR}/logs/log.setExprFields\" 2>&1; fi; decomposePar -force >> \"${CASE_DIR}/logs/log.decomposePar\" 2>&1; fi; mpirun --use-hwthread-cpus -np \"${NP}\" buoyantBoussinesqPimpleFoam -parallel >> \"${LOG_FILE}\" 2>&1; status=\$?; echo --- finished \$(date -Is) exit=\$status --- >> \"${LOG_FILE}\"; exit \$status"

tmux new-session -d -s "${SESSION_NAME}" "${cmd}"
tmux list-sessions
