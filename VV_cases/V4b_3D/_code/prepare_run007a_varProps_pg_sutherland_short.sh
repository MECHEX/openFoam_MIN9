#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run007a: variable-temperature air-property smoke test.
#
# This copies the accepted run004b geometry/mesh/control family and changes the
# thermophysical model from Boussinesq + constant transport to
# incompressiblePerfectGas + Sutherland transport. It is intentionally a short
# run first, because this is a physics-model change, not just a numerical
# parameter change.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run004b}"
DST="${DST:-/home/hexmachina/of_runs/V4b_3D_run007a}"
RUN_ID="${RUN_ID:-run007a}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-2}"
MAX_CO="${MAX_CO:-0.8}"
P_ABS="${P_ABS:-101325}"

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

perl -0pi -e "s/startFrom\s+\S+;/startFrom       startTime;/" "$DST/system/controlDict"
perl -0pi -e "s/startTime\s+[0-9.eE+-]+;/startTime       0;/" "$DST/system/controlDict"
perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         ${END_TIME};/" "$DST/system/controlDict"
perl -0pi -e "s/maxCo\s+[0-9.eE+-]+;/maxCo           ${MAX_CO};/" "$DST/system/controlDict"
perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" "$DST/system/decomposeParDict"

# incompressiblePerfectGas uses pRef/(R*T) for density, so the pressure field can
# remain the same gauge-style field used by the Boussinesq baseline.
perl -0pi -e "s/internalField\s+uniform\s+[0-9.eE+-]+;/internalField   uniform 0;/" "$DST/0/p"

cat > "$DST/CASE_VARIANT.md" <<EOF
# V4b_3D ${RUN_ID}

- Parent case: ${SRC}
- Purpose: short variable-temperature-property physics smoke test
- Re target: 200 at inlet/reference air state
- Geometry: accepted production candidate, Lin=2D and Lout=8D
- Mesh: copied from accepted run004b corrected BL mesh
- Base model: foamRun fluid / heRhoThermo
- Changed physics: Boussinesq + constant transport -> incompressiblePerfectGas + Sutherland transport
- Pressure initialisation: p and p_rgh remain gauge-style; density uses pRef=${P_ABS} Pa
- Sutherland constants: As=1.458e-06, Ts=110.4 K
- Cv: 718 J/(kg K), molWeight: 28.97 g/mol
- maxCo: ${MAX_CO}
- Target endTime: ${END_TIME} s
- MPI ranks: ${NPROCS}

Important limitation: this is no longer a strict Boussinesq model. It is a
low-Mach variable-density/variable-transport sensitivity check with density
depending on temperature through pRef/(R*T), not on dynamic pressure.
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
