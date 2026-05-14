#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run009: run008-style production rerun with variable air
# properties and dense full-field output for vortex/movie post-processing.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run008}"
DST="${DST:-/home/hexmachina/of_runs/V4b_3D_run009_varprops_movie}"
RUN_ID="${RUN_ID:-run009_varprops_movie}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-10}"
MAX_CO="${MAX_CO:-0.8}"
FIELD_WRITE_INTERVAL="${FIELD_WRITE_INTERVAL:-0.02}"
MIDSPAN_WRITE_INTERVAL="${MIDSPAN_WRITE_INTERVAL:-0.01}"
SIGNAL_WRITE_INTERVAL="${SIGNAL_WRITE_INTERVAL:-0.005}"

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
rm -rf "$DST/postProcessing" "$DST/logs"
find "$DST" -maxdepth 1 -type d -name 'processor*' -exec rm -rf {} +
find "$DST" -maxdepth 1 -type d -regex '.*/[0-9]+(\.[0-9]+)?' -exec rm -rf {} +

mkdir -p "$DST/logs"
touch "$DST/${RUN_ID}.foam" "$DST/V4b_${RUN_ID}.foam"

cat > "$DST/constant/physicalProperties" <<'EOF'
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
    transport       sutherland;
    thermo          eConst;
    equationOfState incompressiblePerfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}

mixture
{
    specie
    {
        molWeight       28.97;
    }
    thermodynamics
    {
        Cv              718;
        hf              0;
    }
    equationOfState
    {
        pRef            101325;
    }
    transport
    {
        As              1.458e-06;
        Ts              110.4;
    }
}
EOF

perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" "$DST/system/decomposeParDict"

cat > "$DST/system/controlDict" <<EOF
FoamFile
{
    format      ascii;
    class       dictionary;
    object      controlDict;
}

solver          fluid;

startFrom       startTime;
startTime       0;

stopAt          endTime;
endTime         ${END_TIME};

deltaT          0.0005;

writeControl    adjustableRunTime;
writeInterval   ${FIELD_WRITE_INTERVAL};

purgeWrite      0;

writeFormat     ascii;
writePrecision  8;
writeCompression off;

timeFormat      general;
timePrecision   8;

runTimeModifiable true;

adjustTimeStep  yes;
maxCo           ${MAX_CO};

functions
{
    forceCoeffs
    {
        type            forceCoeffs;
        libs            ("libforces.so");
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   ${SIGNAL_WRITE_INTERVAL};
        log             yes;
        patches         (hot_tube);
        rho             rhoInf;
        rhoInf          1.205;
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         0.25266;
        lRef            0.012;
        Aref            0.000144;
    }

    forces_raw
    {
        type            forces;
        libs            ("libforces.so");
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   ${SIGNAL_WRITE_INTERVAL};
        log             no;
        patches         (hot_tube);
        rho             rhoInf;
        rhoInf          1.205;
        CofR            (0 0 0);
    }

    probes_wake
    {
        type            probes;
        libs            ("libsampling.so");
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   ${SIGNAL_WRITE_INTERVAL};
        fields          (U p p_rgh T rho);
        probeLocations
        (
            (0.010 0 0)
            (0.020 0 0)
            (0.030 0 0)
            (0.040 0 0)
            (0.060 0 0)
            (0.080 0 0)
            (0.100 0 0)
            (0.020 0.006 0)
            (0.040 0.006 0)
            (0.060 0.006 0)
            (0.020 -0.006 0)
            (0.040 -0.006 0)
            (0.060 -0.006 0)
        );
    }

    residuals
    {
        type            residuals;
        libs            ("libutilityFunctionObjects.so");
        fields          (U p_rgh e);
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   0.02;
    }

    wallHeatFlux
    {
        type            wallHeatFlux;
        libs            ("libfieldFunctionObjects.so");
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   ${SIGNAL_WRITE_INTERVAL};
    }

    midspan_z0
    {
        type            surfaces;
        libs            ("libsampling.so");
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   ${MIDSPAN_WRITE_INTERVAL};
        surfaceFormat   vtk;
        fields          (U T p p_rgh rho);
        interpolationScheme cellPoint;
        surfaces
        {
            z0
            {
                type        cutPlane;
                interpolate true;
                planeType   pointAndNormal;
                point       (0 0 0);
                normal      (0 0 1);
            }
        }
    }

    hot_tube_surface
    {
        type            surfaces;
        libs            ("libsampling.so");
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   ${SIGNAL_WRITE_INTERVAL};
        surfaceFormat   vtk;
        fields          (T wallHeatFlux);
        interpolationScheme cellPoint;
        surfaces
        {
            hot_tube
            {
                type        patch;
                interpolate true;
                patches     (hot_tube);
            }
        }
    }

    hot_fin_surface
    {
        type            surfaces;
        libs            ("libsampling.so");
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   ${SIGNAL_WRITE_INTERVAL};
        surfaceFormat   vtk;
        fields          (T wallHeatFlux);
        interpolationScheme cellPoint;
        surfaces
        {
            hot_fin_z_min
            {
                type        patch;
                interpolate true;
                patches     (hot_fin_z_min);
            }
            hot_fin_z_max
            {
                type        patch;
                interpolate true;
                patches     (hot_fin_z_max);
            }
        }
    }
}
EOF

cat > "$DST/CASE_VARIANT.md" <<EOF
# V4b_3D ${RUN_ID}

- Parent case: ${SRC}
- Purpose: run008-style rerun with variable air properties and dense movie-ready output
- Geometry: accepted production domain, Lin=2D and Lout=8D
- Mesh: copied from run008
- Physics change: constant-property eConst+Boussinesq -> incompressiblePerfectGas+Sutherland
- Thermodynamics: eConst, sensibleInternalEnergy, Cv=718 J/(kg K)
- Equation of state: incompressiblePerfectGas with pRef=101325 Pa
- Transport: Sutherland, As=1.458e-06, Ts=110.4 K
- Target endTime: ${END_TIME} s
- maxCo: ${MAX_CO}
- Full-field write interval: ${FIELD_WRITE_INTERVAL} s
- Midspan VTK write interval: ${MIDSPAN_WRITE_INTERVAL} s
- Force/probe/wall-surface interval: ${SIGNAL_WRITE_INTERVAL} s
- MPI ranks: ${NPROCS}

Movie/post-processing intent:

- full fields are written densely enough to compute Q, Lambda2, and vorticity
  after the run for smooth vortex-shedding animations
- expected movie window: after transient, usually t=2..10 s
- estimated storage is several times larger than run008 because field output is
  four times denser than the run008 production field output

Important limitation:

This is a variable-property diagnostic/production candidate, not an accepted
replacement for run008 until wall-air heat balance and force/thermal statistics
are checked.
EOF

cat > "$DST/check_mesh.sh" <<'EOF'
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
checkMesh > logs/log.checkMesh.normal 2>&1
EOF

cat > "$DST/decompose_case.sh" <<'EOF'
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
decomposePar -force > logs/log.decomposePar 2>&1
EOF

chmod +x "$DST/check_mesh.sh" "$DST/decompose_case.sh" 2>/dev/null || true

echo "Prepared $DST"
echo "Next: cd $DST && ./check_mesh.sh && ./decompose_case.sh"
