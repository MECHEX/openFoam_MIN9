#!/usr/bin/env bash
# ============================================================
# generate_meshes.sh
# Gmsh → OpenFOAM mesh pipeline for confined cylinder V&V
#
# Usage:
#   bash generate_meshes.sh <level>   # level: coarse | medium | fine
#   bash generate_meshes.sh all       # run all three
#
# Prerequisites:
#   gmsh          (4.x, in PATH)
#   gmshToFoam    (OpenFOAM sourced, or full path)
#   checkMesh     (OpenFOAM sourced)
#   python3       (to generate .geo files)
#
# Output for each level:
#   cases/<level>/constant/polyMesh/   — OpenFOAM mesh
#   cases/<level>/checkMesh.log        — mesh quality report
# ============================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# --------------------------------------------------------
# Configuration
# --------------------------------------------------------
GMSH="${GMSH:-gmsh}"
GMSH_TO_FOAM="${GMSH_TO_FOAM:-gmshToFoam}"
CHECK_MESH="${CHECK_MESH:-checkMesh}"

LEVELS=("coarse" "medium" "fine")

# --------------------------------------------------------
# Helper: process one mesh level
# --------------------------------------------------------
process_level() {
    local LEVEL="$1"
    local GEO_FILE="cylinder_channel_${LEVEL}.geo"
    local MSH_FILE="cylinder_${LEVEL}.msh"
    local CASE_DIR="cases/${LEVEL}"

    echo ""
    echo "========================================================"
    echo "  LEVEL: ${LEVEL}"
    echo "========================================================"

    # 1. Generate .geo if it doesn't exist yet
    if [[ ! -f "${GEO_FILE}" ]]; then
        echo "[1/5] Generating ${GEO_FILE} ..."
        python3 generate_geo.py
    else
        echo "[1/5] ${GEO_FILE} already exists — skipping generation."
    fi

    # 2. Run Gmsh 3-D meshing
    echo "[2/5] Running Gmsh 3-D meshing → ${MSH_FILE} ..."
    ${GMSH} "${GEO_FILE}" \
        -3 \
        -format msh2 \
        -o "${MSH_FILE}" \
        2>&1 | tee "gmsh_${LEVEL}.log"

    # 3. Set up OpenFOAM case directory
    echo "[3/5] Setting up case directory ${CASE_DIR} ..."
    mkdir -p "${CASE_DIR}/constant"
    mkdir -p "${CASE_DIR}/system"

    # Minimal system/controlDict needed by gmshToFoam
    if [[ ! -f "${CASE_DIR}/system/controlDict" ]]; then
        cat > "${CASE_DIR}/system/controlDict" <<'CTRL'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     buoyantPimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1;
deltaT          1;
writeControl    timeStep;
writeInterval   1;
CTRL
    fi

    # 4. Convert to OpenFOAM
    echo "[4/5] Converting mesh with gmshToFoam ..."
    (
        cd "${CASE_DIR}"
        ${GMSH_TO_FOAM} "../../${MSH_FILE}" 2>&1 | tee "gmshToFoam_${LEVEL}.log"
    )

    # 5. Fix defaultFaces patch type and run checkMesh
    echo "[5/5] Fixing defaultFaces, running checkMesh ..."
    (
        cd "${CASE_DIR}"

        # gmshToFoam creates a "defaultFaces" empty patch — keep it or remove.
        # Also change any 'patch' to correct type for symmetry faces if needed.
        # This is case-specific; do a manual check after running.

        ${CHECK_MESH} -allTopology -allGeometry 2>&1 | tee "checkMesh_${LEVEL}.log"
    )

    echo ""
    echo "  ✓  ${LEVEL} mesh complete."
    echo "     Mesh:       ${CASE_DIR}/constant/polyMesh/"
    echo "     checkMesh:  ${CASE_DIR}/checkMesh_${LEVEL}.log"
    echo ""
    echo "  NEXT: review patch names in ${CASE_DIR}/constant/polyMesh/boundary"
    echo "        compare with expected list:"
    echo "           inlet, outlet, topWall, bottomWall, finBottom, finTop, cylinder"
    echo "        If indices are wrong, edit Physical Groups in ${GEO_FILE}"
    echo "        and re-run."
}

# --------------------------------------------------------
# Main dispatch
# --------------------------------------------------------
if [[ $# -lt 1 ]]; then
    echo "Usage: bash generate_meshes.sh <coarse|medium|fine|all>"
    exit 1
fi

TARGET="$1"

if [[ "${TARGET}" == "all" ]]; then
    # Generate .geo files once
    python3 generate_geo.py
    for LVL in "${LEVELS[@]}"; do
        process_level "${LVL}"
    done
else
    # Validate input
    VALID=false
    for LVL in "${LEVELS[@]}"; do
        [[ "${TARGET}" == "${LVL}" ]] && VALID=true && break
    done
    if ! ${VALID}; then
        echo "ERROR: unknown level '${TARGET}'. Choose: coarse | medium | fine | all"
        exit 1
    fi
    # Generate .geo files (all at once — cheap)
    python3 generate_geo.py
    process_level "${TARGET}"
fi

echo "========================================================"
echo "  All done."
echo "========================================================"
