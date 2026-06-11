#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run011 GCI mesh cases.
# The medium mesh is the accepted production run008 mesh. This script prepares
# only the coarse and fine siblings on the same Lin=2D, Lout=8D, Lz=1D domain.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run008}"
BASE="${BASE:-/home/hexmachina/of_runs}"
RUN_PREFIX="${RUN_PREFIX:-V4b_3D_run011_gci}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-3}"
MAX_CO="${MAX_CO:-0.8}"

if [[ ! -d "$SRC" ]]; then
    echo "Missing source case: $SRC" >&2
    exit 1
fi

prepare_variant() {
    local variant="$1"
    local dst="${BASE}/${RUN_PREFIX}_${variant}"

    local b1 b2 b3 surf_level wake_level tube_layers fin_layers first_layer expansion max_local max_global target_cells note

    case "$variant" in
        coarse)
            # Linear coarsening relative to run008 is about 1/1.28.
            b1="19 25 14"
            b2="22 25 14"
            b3="75 25 14"
            surf_level="(2 2)"
            wake_level="1"
            tube_layers="6"
            fin_layers="4"
            first_layer="3.8e-05"
            expansion="1.20"
            max_local="400000"
            max_global="700000"
            target_cells="~185k-210k"
            note="coarse GCI sibling, target about half of run008 cells"
            ;;
        fine)
            # Linear refinement relative to run008 is about 1.28.
            b1="31 41 23"
            b2="36 41 23"
            b3="123 41 23"
            surf_level="(2 2)"
            wake_level="1"
            tube_layers="10"
            fin_layers="8"
            first_layer="2.35e-05"
            expansion="1.17"
            max_local="1200000"
            max_global="2500000"
            target_cells="~800k-900k"
            note="fine GCI sibling, target about twice run008 cells"
            ;;
        *)
            echo "Unknown GCI variant: $variant" >&2
            exit 2
            ;;
    esac

    if [[ -e "$dst" ]]; then
        echo "Destination already exists: $dst" >&2
        exit 3
    fi

    mkdir -p "$dst"
    cp -a "$SRC/0" "$SRC/constant" "$SRC/system" "$dst/"
    rm -rf "$dst/postProcessing" "$dst/logs"
    find "$dst" -maxdepth 1 -type d -name 'processor*' -exec rm -rf {} +
    find "$dst" -maxdepth 1 -type d -regex '.*/[0-9]+(\.[0-9]+)?' -exec rm -rf {} +
    rm -rf "$dst/constant/polyMesh"
    rm -rf "$dst/0/wallHeatFlux"

    mkdir -p "$dst/logs"
    touch "$dst/${RUN_PREFIX}_${variant}.foam" "$dst/V4b_${RUN_PREFIX}_${variant}.foam"

    perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" "$dst/system/decomposeParDict"

    perl -0pi -e "s/hex \(0 1 5 4 8 9 13 12\)\s+\([0-9 ]+\)/hex (0 1 5 4 8 9 13 12)   (${b1})/" "$dst/system/blockMeshDict"
    perl -0pi -e "s/hex \(1 2 6 5 9 10 14 13\)\s+\([0-9 ]+\)/hex (1 2 6 5 9 10 14 13)  (${b2})/" "$dst/system/blockMeshDict"
    perl -0pi -e "s/hex \(2 3 7 6 10 11 15 14\)\s+\([0-9 ]+\)/hex (2 3 7 6 10 11 15 14) (${b3})/" "$dst/system/blockMeshDict"

    cat > "$dst/system/snappyHexMeshDict" <<EOF
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      snappyHexMeshDict;
}

castellatedMesh true;
snap            true;
addLayers       true;

geometry
{
    hot_tube
    {
        type    searchableCylinder;
        point1  (0 0 -0.006);
        point2  (0 0  0.006);
        radius  0.006;
    }

    wakeBox
    {
        type searchableBox;
        min ( 0.000 -0.012 -0.006);
        max ( 0.072  0.012  0.006);
    }
}

castellatedMeshControls
{
    maxLocalCells           ${max_local};
    maxGlobalCells          ${max_global};
    minRefinementCells      0;
    maxLoadUnbalance        0.10;
    nCellsBetweenLevels     3;
    resolveFeatureAngle     30;

    features ();

    refinementSurfaces
    {
        hot_tube
        {
            level   ${surf_level};
            patchInfo
            {
                type wall;
            }
        }
    }

    refinementRegions
    {
        wakeBox
        {
            mode    inside;
            levels  ((1e15 ${wake_level}));
        }
    }

    locationInMesh (-0.030 0 0);
    allowFreeStandingZoneFaces true;
}

snapControls
{
    nSmoothPatch        5;
    tolerance           2.0;
    nSolveIter          100;
    nRelaxIter          5;
    nFeatureSnapIter    10;
    implicitFeatureSnap true;
    explicitFeatureSnap false;
    multiRegionFeatureSnap false;
}

addLayersControls
{
    relativeSizes        false;

    layers
    {
        hot_tube
        {
            nSurfaceLayers ${tube_layers};
        }
        hot_fin_z_min
        {
            nSurfaceLayers ${fin_layers};
        }
        hot_fin_z_max
        {
            nSurfaceLayers ${fin_layers};
        }
    }

    expansionRatio        ${expansion};
    firstLayerThickness   ${first_layer};
    minThickness          1e-06;
    nGrow                 0;
    featureAngle          130;
    slipFeatureAngle      30;
    nRelaxIter            5;
    nSmoothSurfaceNormals 3;
    nSmoothNormals        3;
    nSmoothThickness      10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedianAxisAngle    90;
    nBufferCellsNoExtrude 0;
    nLayerIter            50;
    nRelaxedIter          20;
}

meshQualityControls
{
    maxNonOrtho         65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave          80;
    minVol              1e-13;
    minTetQuality       1e-30;
    minArea             -1;
    minTwist            0.02;
    minDeterminant      0.001;
    minFaceWeight       0.02;
    minVolRatio         0.01;
    minTriangleTwist    -1;
    nSmoothScale        4;
    errorReduction      0.75;

    relaxed
    {
        maxNonOrtho     75;
    }
}

writeFlags ( scalarLevels );
mergeTolerance 1e-6;
EOF

    perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         ${END_TIME};/" "$dst/system/controlDict"
    perl -0pi -e "s/maxCo\s+[0-9.eE+-]+;/maxCo           ${MAX_CO};/" "$dst/system/controlDict"

    cat > "$dst/CASE_VARIANT.md" <<EOF
# V4b_3D run011 GCI ${variant}

- Parent case: ${SRC}
- Purpose: ${note}
- Geometry: accepted production domain, Lin=2D, Lout=8D, Lz=1D
- Physics: same accepted run008 constant-property Cp-consistent setup
- Solver: foamRun -solver fluid
- Re: 200
- Target cell count: ${target_cells}
- Medium reference: run008, 407,440 cells
- blockMesh cells:
  - inlet block: ${b1}
  - fin/tube block: ${b2}
  - outlet block: ${b3}
- hot tube surface refinement: level ${surf_level}
- wake refinement: level ${wake_level}
- layers: hot_tube ${tube_layers}, hot_fin_z_min/z_max ${fin_layers}
- firstLayerThickness: ${first_layer} m
- expansionRatio: ${expansion}
- maxCo: ${MAX_CO}
- smoke endTime: ${END_TIME} s
- MPI ranks: ${NPROCS}

GCI metrics to extract after the run:

- Cd_mean
- Cl_rms
- St
- Nu_EB
- Nu_wall
- wall-air closure
- Q_tube / Q_fins heat split

Use the measured final cell count to compute actual refinement ratios:

- r_21 = (N_medium / N_coarse)^(1/3)
- r_32 = (N_fine / N_medium)^(1/3)

EOF

    cat > "$dst/mesh.sh" <<'EOF'
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
blockMesh > logs/log.blockMesh 2>&1
snappyHexMesh -overwrite > logs/log.snappyHexMesh 2>&1
checkMesh > logs/log.checkMesh.normal 2>&1
checkMesh -allTopology -allGeometry > logs/log.checkMesh.strict 2>&1 || true
EOF

    cat > "$dst/decompose_case.sh" <<'EOF'
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
decomposePar -force > logs/log.decomposePar 2>&1
EOF

    cat > "$dst/run_parallel.sh" <<'EOF'
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
NPROCS="${NPROCS:-20}"
TAG="${TAG:-$(date +%Y%m%d_%H%M%S)_gci_smoke}"
mpirun --oversubscribe -np "${NPROCS}" foamRun -solver fluid -parallel > "logs/log.foamRun_parallel.${TAG}" 2>&1
EOF

    chmod +x "$dst/mesh.sh" "$dst/decompose_case.sh" "$dst/run_parallel.sh" 2>/dev/null || true

    echo "Prepared ${dst}"
}

prepare_variant coarse
prepare_variant fine

cat <<EOF
Prepared GCI sibling cases:

- ${BASE}/${RUN_PREFIX}_coarse
- ${BASE}/${RUN_PREFIX}_fine

Next smoke-test sequence for each case:

cd <case>
./mesh.sh
./decompose_case.sh
NPROCS=${NPROCS} TAG=run011_gci_smoke ./run_parallel.sh

Medium reference remains:

- ${SRC}
EOF
