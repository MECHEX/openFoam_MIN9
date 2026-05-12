#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run007b: constant-property Cp/enthalpy smoke test.
#
# This reuses the accepted run004b geometry and mesh, but changes the thermal
# model from eConst/sensibleInternalEnergy with Cv=718 to hConst/sensibleEnthalpy
# with Cp=1005. The purpose is to isolate whether the earlier constant-property
# baseline was effectively a Cv-based heat equation rather than the Cp-based
# open-flow heat balance expected for a heat exchanger.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run004b}"
DST="${DST:-/home/hexmachina/of_runs/V4b_3D_run007b}"
RUN_ID="${RUN_ID:-run007b}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-2}"
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
    transport       const;
    thermo          hConst;
    equationOfState Boussinesq;
    specie          specie;
    energy          sensibleEnthalpy;
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
        Cp              1005;
        Hf              0;
    }
    transport
    {
        mu              1.827e-05;
        Pr              0.713;
    }
}
EOF

perl -0pi -e "s/startFrom\s+\S+;/startFrom       startTime;/" "$DST/system/controlDict"
perl -0pi -e "s/startTime\s+[0-9.eE+-]+;/startTime       0;/" "$DST/system/controlDict"
perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         ${END_TIME};/" "$DST/system/controlDict"
perl -0pi -e "s/maxCo\s+[0-9.eE+-]+;/maxCo           ${MAX_CO};/" "$DST/system/controlDict"
perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" "$DST/system/decomposeParDict"

# The enthalpy formulation solves h instead of e.
perl -0pi -e "s/div\(phi,e\)\s+Gauss\s+upwind;/div(phi,e)                              Gauss upwind;\n    div(phi,h)                              Gauss upwind;/" "$DST/system/fvSchemes"
perl -0pi -e 's/"\(U\|e\)"/"(U|e|h)"/g; s/"\(U\|e\)Final"/"(U|e|h)Final"/g' "$DST/system/fvSolution"
perl -0pi -e "s/fields\s+\(\s*U\s+p_rgh\s+e\s*\);/fields          (U p_rgh h);/g" "$DST/system/controlDict"

cat > "$DST/CASE_VARIANT.md" <<EOF
# V4b_3D ${RUN_ID}

- Parent case: ${SRC}
- Purpose: short constant-property Cp/enthalpy smoke test
- Geometry: accepted production candidate, Lin=2D and Lout=8D
- Mesh: copied from accepted run004b corrected BL mesh
- Base model: foamRun fluid / heRhoThermo
- Changed thermal model: eConst + sensibleInternalEnergy + Cv=718 -> hConst + sensibleEnthalpy + Cp=1005
- Equation of state: Boussinesq, same rho0/T0/beta as run004b
- Transport: constant mu=1.827e-05 Pa s, Pr=0.713
- Target thermal conductivity implied by k=mu*Cp/Pr: about 0.02575 W/(m K)
- maxCo: ${MAX_CO}
- Target endTime: ${END_TIME} s
- MPI ranks: ${NPROCS}

Decision use: compare against run004b and run007a over the same early window.
If wallHeatFlux and outlet m_dot*Cp*dT now close cleanly, then the Cp/enthalpy
formulation is the better constant-property baseline for heat-transfer claims.
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
