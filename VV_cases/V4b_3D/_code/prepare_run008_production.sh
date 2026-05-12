#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run008 production case from the accepted run007c setup.
# The production case keeps the run007c constant-property Cp-capacity model and
# adds the sampling required for force/thermal coherence analysis.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run007c}"
DST="${DST:-/home/hexmachina/of_runs/V4b_3D_run008}"
RUN_ID="${RUN_ID:-run008}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-10}"
MAX_CO="${MAX_CO:-0.8}"

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
writeInterval   0.08;

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
        writeInterval   0.005;
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
        writeInterval   0.005;
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
        writeInterval   0.005;
        fields          (U p p_rgh T);
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
        writeInterval   0.005;
    }

    midspan_z0
    {
        type            surfaces;
        libs            ("libsampling.so");
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   0.02;
        surfaceFormat   vtk;
        fields          (U T p_rgh);
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
        writeInterval   0.005;
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
        writeInterval   0.005;
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
- Purpose: production run for force/thermal statistics, spectra, coherence, and transfer entropy
- Geometry: accepted production candidate, Lin=2D and Lout=8D
- Mesh: copied from accepted corrected BL mesh family
- Physics: run007c constant-property Cp-capacity setup
- Thermophysics: eConst + Boussinesq + sensibleInternalEnergy
- Capacity coefficient: 1005
- Transport: constant mu=1.827e-05 Pa s, Pr=0.713
- maxCo: ${MAX_CO}
- Target endTime: ${END_TIME} s
- Full field write interval: 0.08 s
- Midspan z=0 surface interval: 0.02 s
- Force/probe/wall-surface interval: 0.005 s
- MPI ranks: ${NPROCS}

Force output contract:

- forceCoeffs.dat: Time, Cm, Cd, Cl, Cl(f), Cl(r)
- forces.dat: Time, CofR, pressure force vector, viscous force vector,
  pressure moment vector, viscous moment vector
- totals must be computed explicitly as pressure + viscous components
EOF

cat > "$DST/check_mesh.sh" <<'EOF'
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
checkMesh > logs/log.checkMesh.normal 2>&1
EOF

chmod +x "$DST/check_mesh.sh" 2>/dev/null || true

echo "Prepared $DST"
echo "Next: cd $DST && ./check_mesh.sh"
