#!/usr/bin/env bash
set -euo pipefail

# Prepare a production-geometry Re=100 V4b case with the same sampling contract
# as run008, so POD/EPOD/TE windows can be compared against Re=200.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run008}"
DST="${DST:-/home/hexmachina/of_runs/V4b_3D_run012_re100_production}"
RUN_ID="${RUN_ID:-run012_re100}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-10}"
MAX_CO="${MAX_CO:-0.8}"
U_INF="${U_INF:-0.12633}"

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
perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         ${END_TIME};/" "$DST/system/controlDict"
perl -0pi -e "s/maxCo\s+[0-9.eE+-]+;/maxCo           ${MAX_CO};/" "$DST/system/controlDict"
perl -0pi -e "s/magUInf\s+[0-9.eE+-]+;/magUInf         ${U_INF};/" "$DST/system/controlDict"
perl -0pi -e "s/internalField\s+uniform\s+\([0-9.eE+-]+\s+0\s+0\);/internalField   uniform (${U_INF} 0 0);/" "$DST/0/U"
perl -0pi -e "s/value\s+uniform\s+\([0-9.eE+-]+\s+0\s+0\);/value           uniform (${U_INF} 0 0);/" "$DST/0/U"

cat > "$DST/CASE_VARIANT.md" <<EOF
# V4b_3D ${RUN_ID}

- Parent case: ${SRC}
- Purpose: production-geometry Re=100 reference for before/after-Hopf comparison
- Geometry: accepted production domain, Lin=2D, Lout=8D, Lz=1D
- Mesh: run008 production medium mesh, 407,440 cells
- Physics: constant-property Cp-capacity setup, eConst + Boussinesq
- U_inf: ${U_INF} m/s
- Re: 100, using D=0.012 m and the same viscosity basis as the V4b campaign
- maxCo: ${MAX_CO}
- Target endTime: ${END_TIME} s
- Full field write interval: 0.08 s
- Midspan z=0 surface interval: 0.02 s
- Force/probe/wall-surface interval: 0.005 s
- MPI ranks: ${NPROCS}

Analysis contract:

- Same sampling objects as run008.
- Primary expected role: steady/pre-Hopf contrast against run008 Re=200.
- If the flow remains steady, POD/EPOD/TE should be reported as diagnostic or not applicable rather than over-interpreted.
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
