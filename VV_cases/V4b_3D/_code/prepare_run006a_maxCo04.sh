#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run006a: timestep/Courant sensitivity check.
#
# The mesh and domain are copied from the accepted run004b case:
# Lin=2D, Lout=8D, corrected BL mesh. Only the adaptive timestep limit is
# changed from maxCo=0.8 to maxCo=0.4.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run004b}"
DST="${DST:-/home/hexmachina/of_runs/V4b_3D_run006a}"
RUN_ID="${RUN_ID:-run006a}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-6}"
MAX_CO="${MAX_CO:-0.4}"

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

perl -0pi -e "s/startFrom\s+\S+;/startFrom       startTime;/" "$DST/system/controlDict"
perl -0pi -e "s/startTime\s+[0-9.eE+-]+;/startTime       0;/" "$DST/system/controlDict"
perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         ${END_TIME};/" "$DST/system/controlDict"
perl -0pi -e "s/maxCo\s+[0-9.eE+-]+;/maxCo           ${MAX_CO};/" "$DST/system/controlDict"
perl -0pi -e "s/numberOfSubdomains\s+\d+;/numberOfSubdomains ${NPROCS};/" "$DST/system/decomposeParDict"

cat > "$DST/CASE_VARIANT.md" <<EOF
# V4b_3D ${RUN_ID}

- Parent case: ${SRC}
- Purpose: timestep / adaptive Courant sensitivity check
- Re: 200
- Lin: 2D
- Lout: 8D
- Mesh: copied from accepted run004b corrected BL mesh
- Changed control: maxCo ${MAX_CO} instead of run004b maxCo 0.8
- Target endTime: ${END_TIME} s
- MPI ranks: ${NPROCS}
EOF

cat > "$DST/check_mesh.sh" <<'EOF'
#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
checkMesh > logs/log.checkMesh.normal 2>&1
checkMesh -allTopology -allGeometry > logs/log.checkMesh 2>&1 || true
EOF

chmod +x "$DST/check_mesh.sh" 2>/dev/null || true

echo "Prepared $DST"
echo "Next: cd $DST && ./check_mesh.sh"
