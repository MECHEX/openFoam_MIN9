#!/usr/bin/env bash
set -eo pipefail
set -u

CASE_DIR="${CASE_DIR:-/home/hexmachina/of_runs/V4b_3D_run004}"
RE="${RE:-200}"
UIN="${UIN:-0.25266}"
END_TIME="${END_TIME:-2.0}"
DELTA_T="${DELTA_T:-5e-4}"
NPROCS="${NPROCS:-8}"

mkdir -p "$CASE_DIR/0" "$CASE_DIR/constant" "$CASE_DIR/system" "$CASE_DIR/logs"

cat > "$CASE_DIR/system/controlDict" <<EOF
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}

solver          fluid;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         ${END_TIME};

deltaT          ${DELTA_T};
adjustTimeStep  yes;
maxCo           0.8;

writeControl    adjustableRunTime;
writeInterval   0.5;
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
        libs            ("libforces.so");
        executeControl  timeStep;
        writeControl    timeStep;
        writeInterval   10;
        log             yes;
        patches         (hot_tube);
        rho             rhoInf;
        rhoInf          1.205;
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         ${UIN};
        lRef            0.012;
        Aref            0.000144;
    }

    probes_wake
    {
        type            probes;
        libs            ("libsampling.so");
        executeControl  timeStep;
        writeControl    timeStep;
        writeInterval   10;
        fields          (U p p_rgh T);
        probeLocations
        (
            ( 0.012  0  0.000)
            ( 0.024  0  0.000)
            ( 0.036  0  0.000)
            ( 0.060  0  0.000)
            ( 0.096  0  0.000)
            (-0.006  0  0.000)
        );
    }

    residuals
    {
        type            residuals;
        libs            ("libutilityFunctionObjects.so");
        fields          (U p_rgh e);
        writeControl    timeStep;
        writeInterval   10;
    }
}
EOF

cat > "$CASE_DIR/system/fvSchemes" <<'EOF'
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSchemes;
}

ddtSchemes
{
    default         backward;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default                                 none;
    div(phi,U)                              Gauss linearUpwind grad(U);
    div(phi,e)                              Gauss upwind;
    div(phi,p)                              Gauss linear;
    div(phi,rho)                            Gauss linear;
    div(phi,K)                              Gauss linear;
    div(phid,p)                             Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U)))))     Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}
EOF

cat > "$CASE_DIR/system/fvSolution" <<'EOF'
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSolution;
}

solvers
{
    "rho.*"
    {
        solver          diagonal;
    }

    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-8;
        relTol          0.01;
    }

    p_rghFinal
    {
        $p_rgh;
        relTol          0;
    }

    "(U|e)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-7;
        relTol          0.05;
    }

    "(U|e)Final"
    {
        $U;
        relTol          0;
    }
}

PIMPLE
{
    momentumPredictor          yes;
    nOuterCorrectors           2;
    nCorrectors                2;
    nNonOrthogonalCorrectors   1;
    pRefCell                   0;
    pRefValue                  0;
}
EOF

cat > "$CASE_DIR/system/decomposeParDict" <<EOF
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

cat > "$CASE_DIR/system/blockMeshDict" <<'EOF'
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

cat > "$CASE_DIR/system/snappyHexMeshDict" <<'EOF'
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      snappyHexMeshDict;
}

castellatedMesh true;
snap            true;
addLayers       false;

geometry
{
    hot_tube
    {
        type    searchableCylinder;
        point1  (0 0 -0.006);
        point2  (0 0  0.006);
        radius  0.006;
    }

    nearCylinder
    {
        type searchableBox;
        min (-0.024 -0.012 -0.006);
        max ( 0.036  0.012  0.006);
    }

    wakeBox
    {
        type searchableBox;
        min ( 0.000 -0.014 -0.006);
        max ( 0.084  0.014  0.006);
    }
}

castellatedMeshControls
{
    maxLocalCells           800000;
    maxGlobalCells          3000000;
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
        nearCylinder
        {
            mode    inside;
            levels  ((1e15 2));
        }
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

cat > "$CASE_DIR/constant/g" <<'EOF'
FoamFile
{
    format      ascii;
    class       uniformDimensionedVectorField;
    location    "constant";
    object      g;
}

dimensions      [0 1 -2 0 0 0 0];
value           (0 -9.81 0);
EOF

cat > "$CASE_DIR/constant/physicalProperties" <<'EOF'
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "constant";
    object      physicalProperties;
}

thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          eConst;
    equationOfState Boussinesq;
    specie          specie;
    energy          sensibleInternalEnergy;
}

mixture
{
    specie
    {
        molWeight       28.9;
    }
    equationOfState
    {
        rho0            1.205;
        T0              293.15;
        beta            3.412e-03;
    }
    thermodynamics
    {
        Cv              718;
        hf              0;
    }
    transport
    {
        mu              1.827e-05;
        Pr              0.713;
    }
}
EOF

cat > "$CASE_DIR/constant/momentumTransport" <<'EOF'
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "constant";
    object      momentumTransport;
}

simulationType  laminar;
EOF

cat > "$CASE_DIR/0/U" <<EOF
FoamFile
{
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (${UIN} 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (${UIN} 0 0);
    }
    outlet
    {
        type            zeroGradient;
    }
    symmetry_y_min
    {
        type            symmetryPlane;
    }
    symmetry_y_max
    {
        type            symmetryPlane;
    }
    symmetry_z_min_inlet
    {
        type            symmetryPlane;
    }
    symmetry_z_min_outlet
    {
        type            symmetryPlane;
    }
    symmetry_z_max_inlet
    {
        type            symmetryPlane;
    }
    symmetry_z_max_outlet
    {
        type            symmetryPlane;
    }
    hot_fin_z_min
    {
        type            noSlip;
    }
    hot_fin_z_max
    {
        type            noSlip;
    }
    hot_tube
    {
        type            noSlip;
    }
}
EOF

cat > "$CASE_DIR/0/T" <<'EOF'
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      T;
}

dimensions      [0 0 0 1 0 0 0];
internalField   uniform 293.15;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 293.15;
    }
    outlet
    {
        type            inletOutlet;
        inletValue      uniform 293.15;
        value           uniform 293.15;
    }
    symmetry_y_min
    {
        type            symmetryPlane;
    }
    symmetry_y_max
    {
        type            symmetryPlane;
    }
    symmetry_z_min_inlet
    {
        type            symmetryPlane;
    }
    symmetry_z_min_outlet
    {
        type            symmetryPlane;
    }
    symmetry_z_max_inlet
    {
        type            symmetryPlane;
    }
    symmetry_z_max_outlet
    {
        type            symmetryPlane;
    }
    hot_fin_z_min
    {
        type            fixedValue;
        value           uniform 343.15;
    }
    hot_fin_z_max
    {
        type            fixedValue;
        value           uniform 343.15;
    }
    hot_tube
    {
        type            fixedValue;
        value           uniform 343.15;
    }
}
EOF

cat > "$CASE_DIR/0/p_rgh" <<'EOF'
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }
    outlet
    {
        type            fixedValue;
        value           uniform 0;
    }
    symmetry_y_min
    {
        type            symmetryPlane;
    }
    symmetry_y_max
    {
        type            symmetryPlane;
    }
    symmetry_z_min_inlet
    {
        type            symmetryPlane;
    }
    symmetry_z_min_outlet
    {
        type            symmetryPlane;
    }
    symmetry_z_max_inlet
    {
        type            symmetryPlane;
    }
    symmetry_z_max_outlet
    {
        type            symmetryPlane;
    }
    hot_fin_z_min
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }
    hot_fin_z_max
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }
    hot_tube
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }
}
EOF

cat > "$CASE_DIR/0/p" <<'EOF'
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      p;
}

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            calculated;
        value           $internalField;
    }
    outlet
    {
        type            calculated;
        value           $internalField;
    }
    symmetry_y_min
    {
        type            symmetryPlane;
    }
    symmetry_y_max
    {
        type            symmetryPlane;
    }
    symmetry_z_min_inlet
    {
        type            symmetryPlane;
    }
    symmetry_z_min_outlet
    {
        type            symmetryPlane;
    }
    symmetry_z_max_inlet
    {
        type            symmetryPlane;
    }
    symmetry_z_max_outlet
    {
        type            symmetryPlane;
    }
    hot_fin_z_min
    {
        type            calculated;
        value           $internalField;
    }
    hot_fin_z_max
    {
        type            calculated;
        value           $internalField;
    }
    hot_tube
    {
        type            calculated;
        value           $internalField;
    }
}
EOF

cat > "$CASE_DIR/mesh.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
blockMesh > logs/log.blockMesh 2>&1
snappyHexMesh -overwrite > logs/log.snappyHexMesh 2>&1
checkMesh -allTopology -allGeometry > logs/log.checkMesh 2>&1
EOF

cat > "$CASE_DIR/run_smoke.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
foamRun -solver fluid > logs/log.foamRun_smoke 2>&1
EOF

cat > "$CASE_DIR/run_parallel.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "\$(dirname "\$0")"
mkdir -p logs
decomposePar -force > logs/log.decomposePar 2>&1
nohup mpirun -np ${NPROCS} foamRun -solver fluid -parallel > logs/log.foamRun_parallel 2>&1 &
echo \$! > logs/solver.pid
echo "PID \$(cat logs/solver.pid)"
EOF

chmod +x "$CASE_DIR/mesh.sh" "$CASE_DIR/run_smoke.sh" "$CASE_DIR/run_parallel.sh"

touch "$CASE_DIR/run004.foam" "$CASE_DIR/V4b_run004.foam"

echo "Prepared $CASE_DIR"
