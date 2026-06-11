#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

# Sequential run queue for the V4b run011 GCI t=3 s campaign.
# Runs coarse first, then fine, because two 20-rank oversubscribed MPI jobs are
# too heavy for the local WSL session.

BASE="${BASE:-/home/hexmachina/of_runs}"
COARSE="${COARSE:-${BASE}/V4b_3D_run011_gci_coarse}"
FINE="${FINE:-${BASE}/V4b_3D_run011_gci_fine}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-3}"
QUEUE_TAG="${QUEUE_TAG:-$(date +%Y%m%d_%H%M%S)_run011_gci_t3_queue}"
QUEUE_LOG="${QUEUE_LOG:-${BASE}/run011_gci_t3_queue.${QUEUE_TAG}.log}"

safe_case_dir() {
    local case_dir="$1"
    [[ "$case_dir" == /home/hexmachina/of_runs/V4b_3D_run011_gci_* ]]
}

clean_partial_outputs() {
    local case_dir="$1"

    safe_case_dir "$case_dir" || {
        echo "Refusing to clean unexpected path: $case_dir" >&2
        exit 3
    }

    rm -rf "${case_dir}/postProcessing"

    # Remove only numeric processor time directories except processor*/0.
    find "$case_dir" -maxdepth 2 -type d -path "${case_dir}/processor*/*" \
        | while read -r path; do
            name="$(basename "$path")"
            parent="$(basename "$(dirname "$path")")"
            if [[ "$parent" == processor* && "$name" != "0" && "$name" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
                rm -rf "$path"
            fi
        done
}

prepare_controls() {
    local case_dir="$1"

    perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" \
        "${case_dir}/system/decomposeParDict"
    perl -0pi -e "s/startFrom\s+\w+;/startFrom       startTime;/" \
        "${case_dir}/system/controlDict"
    perl -0pi -e "s/startTime\s+[0-9.eE+-]+;/startTime       0;/" \
        "${case_dir}/system/controlDict"
    perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         ${END_TIME};/" \
        "${case_dir}/system/controlDict"
}

run_case() {
    local label="$1"
    local case_dir="$2"
    local tag="${QUEUE_TAG}_${label}"

    echo "[$(date --iso-8601=seconds)] START ${label}: ${case_dir}"
    safe_case_dir "$case_dir" || {
        echo "Unexpected case path: $case_dir" >&2
        exit 4
    }

    cd "$case_dir"
    mkdir -p logs

    clean_partial_outputs "$case_dir"
    prepare_controls "$case_dir"

    decomposePar -force > "logs/log.decomposePar.${tag}" 2>&1

    mpirun --oversubscribe -np "${NPROCS}" foamRun -solver fluid -parallel \
        > "logs/log.foamRun_parallel.${tag}" 2>&1

    echo "[$(date --iso-8601=seconds)] END ${label}"
}

{
    echo "[$(date --iso-8601=seconds)] Queue ${QUEUE_TAG}"
    echo "NPROCS=${NPROCS}"
    echo "END_TIME=${END_TIME}"
    echo "COARSE=${COARSE}"
    echo "FINE=${FINE}"
    run_case coarse "$COARSE"
    run_case fine "$FINE"
    echo "[$(date --iso-8601=seconds)] Queue complete"
} >> "$QUEUE_LOG" 2>&1

