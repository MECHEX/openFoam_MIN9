#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run004b: controlled Lout=8D outlet-sensitivity case.
#
# run004 used level-2 volume refinement over a large nearCylinder box, producing
# ~1.78M cells. This variant keeps the longer outlet, keeps tube surface
# level-2, restores boundary-layer extrusion similar to run001/run003, and
# limits volume refinement to a short level-1 wake box.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run004}"
DST="${DST:-/home/hexmachina/of_runs/V4b_3D_run004b}"
RUN_ID="${RUN_ID:-run004b}"
NPROCS="${NPROCS:-8}"
END_TIME="${END_TIME:-6}"

if [[ ! -d "$SRC" ]]; then
    echo "Missing source case: $SRC" >&2
    exit 1
fi

if [[ -e "$DST" ]]; then
    echo "Destination already exists: $DST" >&2
    exit 2
fi

mkdir -p "$DST"
cp -a "$SRC/0" "$SRC/constant" "$SRC/system" "$DST/"
cp -a "$SRC/mesh.sh" "$SRC/run_smoke.sh" "$SRC/run_parallel.sh" "$DST/" 2>/dev/null || true

rm -rf "$DST/constant/polyMesh" "$DST/postProcessing" "$DST/logs"
find "$DST" -maxdepth 1 -type d -name 'processor*' -exec rm -rf {} +
find "$DST" -maxdepth 1 -type d -regex '.*/[0-9]+(\.[0-9]+)?' -exec rm -rf {} +

mkdir -p "$DST/logs"
touch "$DST/${RUN_ID}.foam" "$DST/V4b_${RUN_ID}.foam"

cat > "$DST/system/controlDict" <<EOF
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}

solver          fluid;

startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         ${END_TIME};

deltaT          0.0005;
adjustTimeStep  yes;
maxCo           0.8;

writeControl    adjustableRunTime;
writeInterval   0.1;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   8;
runTimeModifiable true;

functions
{
    forceCoeffs
    {
        type            forceCoeffs;
        libs            ( "libforces.so" );
        executeControl  timeStep;
        writeControl    timeStep;
        writeInterval   10;
        log             yes;
        patches         ( hot_tube );
        rho             rhoInf;
        rhoInf          1.205;
        CofR            ( 0 0 0 );
        liftDir         ( 0 1 0 );
        dragDir         ( 1 0 0 );
        pitchAxis       ( 0 0 1 );
        magUInf         0.25266;
        lRef            0.012;
        Aref            0.000144;
    }

    probes_wake
    {
        type            probes;
        libs            ( "libsampling.so" );
        executeControl  timeStep;
        writeControl    timeStep;
        writeInterval   10;
        fields          ( U p p_rgh T );
        probeLocations
        (
            ( 0.012  0  0.000 )
            ( 0.024  0  0.000 )
            ( 0.036  0  0.000 )
            ( 0.060  0  0.000 )
            ( 0.096  0  0.000 )
            (-0.006  0  0.000 )
        );
    }

    residuals
    {
        type            residuals;
        libs            ( "libutilityFunctionObjects.so" );
        fields          ( U p_rgh e );
        writeControl    timeStep;
        writeInterval   10;
    }
}
EOF

cat > "$DST/system/decomposeParDict" <<EOF
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

cat > "$DST/system/blockMeshDict" <<'EOF'
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      blockMeshDict;
}

scale 1;

vertices
(
    (-0.037855 -0.016 -0.006)
    (-0.013855 -0.016 -0.006)
    ( 0.013855 -0.016 -0.006)
    ( 0.109855 -0.016 -0.006)
    (-0.037855  0.016 -0.006)
    (-0.013855  0.016 -0.006)
    ( 0.013855  0.016 -0.006)
    ( 0.109855  0.016 -0.006)

    (-0.037855 -0.016  0.006)
    (-0.013855 -0.016  0.006)
    ( 0.013855 -0.016  0.006)
    ( 0.109855 -0.016  0.006)
    (-0.037855  0.016  0.006)
    (-0.013855  0.016  0.006)
    ( 0.013855  0.016  0.006)
    ( 0.109855  0.016  0.006)
);

blocks
(
    hex (0 1 5 4 8 9 13 12)   (24 32 18) simpleGrading (1 1 1)
    hex (1 2 6 5 9 10 14 13)  (28 32 18) simpleGrading (1 1 1)
    hex (2 3 7 6 10 11 15 14) (96 32 18) simpleGrading (1 1 1)
);

edges ();

boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 8 12 4)
        );
    }

    outlet
    {
        type patch;
        faces
        (
            (3 7 15 11)
        );
    }

    symmetry_y_min
    {
        type symmetryPlane;
        faces
        (
            (0 1 9 8)
            (1 2 10 9)
            (2 3 11 10)
        );
    }

    symmetry_y_max
    {
        type symmetryPlane;
        faces
        (
            (4 12 13 5)
            (5 13 14 6)
            (6 14 15 7)
        );
    }

    symmetry_z_min_inlet
    {
        type symmetryPlane;
        faces
        (
            (0 4 5 1)
        );
    }

    hot_fin_z_min
    {
        type wall;
        faces
        (
            (1 5 6 2)
        );
    }

    symmetry_z_min_outlet
    {
        type symmetryPlane;
        faces
        (
            (2 6 7 3)
        );
    }

    symmetry_z_max_inlet
    {
        type symmetryPlane;
        faces
        (
            (8 9 13 12)
        );
    }

    hot_fin_z_max
    {
        type wall;
        faces
        (
            (9 10 14 13)
        );
    }

    symmetry_z_max_outlet
    {
        type symmetryPlane;
        faces
        (
            (10 11 15 14)
        );
    }
);

mergePatchPairs ();
EOF

cat > "$DST/system/snappyHexMeshDict" <<'EOF'
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
    maxLocalCells           600000;
    maxGlobalCells          1000000;
    minRefinementCells      0;
    maxLoadUnbalance        0.10;
    nCellsBetweenLevels     3;
    resolveFeatureAngle     30;

    features ();

    refinementSurfaces
    {
        hot_tube
        {
            level   (2 2);
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
            levels  ((1e15 1));
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
            nSurfaceLayers 8;
        }
        hot_fin_z_min
        {
            nSurfaceLayers 6;
        }
        hot_fin_z_max
        {
            nSurfaceLayers 6;
        }
    }

    expansionRatio        1.20;
    firstLayerThickness   3e-05;
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

cat > "$DST/CASE_VARIANT.md" <<EOF
# V4b_3D ${RUN_ID}

- Parent diagnostic case: ${SRC}
- Purpose: controlled outlet-sensitivity replacement for over-refined run004
- Re: 200
- Lin: 2D
- Lout: 8D
- Lx: 147.71 mm
- Mesh intent: comparable-cost lvl-2 surface mesh, not run004's large level-2 volume mesh
- Tube surface refinement: level (2 2)
- Boundary layers: hot_tube 8, hot_fin_z_min/z_max 6, first layer 30 um
- Wake refinement: short level-1 box, x = 0..72 mm, y = +/-12 mm
- Deliberately removed: large nearCylinder level-2 volume box from run004
EOF

cat > "$DST/mesh.sh" <<'EOF'
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
blockMesh > logs/log.blockMesh 2>&1
snappyHexMesh -overwrite > logs/log.snappyHexMesh 2>&1
checkMesh -allTopology -allGeometry > logs/log.checkMesh 2>&1
EOF

cat > "$DST/run_smoke.sh" <<'EOF'
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
foamRun -solver fluid > logs/log.foamRun_smoke 2>&1
EOF

cat > "$DST/run_parallel.sh" <<EOF
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "\$(dirname "\$0")"
mkdir -p logs
decomposePar -force > logs/log.decomposePar 2>&1
nohup mpirun -np ${NPROCS} foamRun -solver fluid -parallel > logs/log.foamRun_parallel 2>&1 &
echo \$! > logs/solver.pid
echo "PID \$(cat logs/solver.pid)"
EOF

chmod +x "$DST/mesh.sh" "$DST/run_smoke.sh" "$DST/run_parallel.sh" 2>/dev/null || true

echo "Prepared $DST"
echo "Next: cd $DST && ./mesh.sh"
