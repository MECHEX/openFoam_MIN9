#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run007c: constant-property Cp-as-energy-capacity smoke test.
#
# hConst/sensibleEnthalpy with Boussinesq is not robust in the current OF13
# setup. This fallback keeps the proven run004b eConst/Boussinesq formulation
# and changes only the thermal capacity from 718 to 1005. It is a numerical
# isolation test for the Cv -> Cp effect, not a new production physics model.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run004b}"
DST="${DST:-/home/hexmachina/of_runs/V4b_3D_run007c}"
RUN_ID="${RUN_ID:-run007c}"
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

perl -0pi -e "s/Cv\s+718;/Cv              1005;/" "$DST/constant/physicalProperties"
perl -0pi -e "s/startFrom\s+\S+;/startFrom       startTime;/" "$DST/system/controlDict"
perl -0pi -e "s/startTime\s+[0-9.eE+-]+;/startTime       0;/" "$DST/system/controlDict"
perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         ${END_TIME};/" "$DST/system/controlDict"
perl -0pi -e "s/maxCo\s+[0-9.eE+-]+;/maxCo           ${MAX_CO};/" "$DST/system/controlDict"
perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" "$DST/system/decomposeParDict"

cat > "$DST/CASE_VARIANT.md" <<EOF
# V4b_3D ${RUN_ID}

- Parent case: ${SRC}
- Purpose: short constant-property Cv->Cp isolation smoke test
- Geometry: accepted production candidate, Lin=2D and Lout=8D
- Mesh: copied from accepted run004b corrected BL mesh
- Base model: foamRun fluid / heRhoThermo
- Formulation: eConst + Boussinesq + sensibleInternalEnergy, same as run004b
- Changed coefficient: Cv=718 -> Cv=1005
- Interpretation: Cp-like constant heat capacity in the existing stable energy equation
- Transport: constant mu=1.827e-05 Pa s, Pr=0.713
- maxCo: ${MAX_CO}
- Target endTime: ${END_TIME} s
- MPI ranks: ${NPROCS}

This is a diagnostic fallback after hConst/sensibleEnthalpy+Boussinesq failed
at startup. Use it to isolate the numerical/thermal effect of replacing the
energy capacity 718 with 1005 while preserving all other case mechanics.
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
