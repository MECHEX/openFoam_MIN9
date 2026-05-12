#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run004: Re=200 outlet-sensitivity variant with a longer outlet.
# Default choice is Lout = 8D, but LOUT_D can be overridden, e.g. LOUT_D=10.

RUN_ID="${RUN_ID:-run004}"
SRC="${SRC:-/mnt/c/openfoam-case/VV_cases/V4b_3D_run003}"
DST="${DST:-/mnt/c/openfoam-case/VV_cases/V4b_3D_run004}"
WIN_DST="${WIN_DST:-C:/openfoam-case/VV_cases/V4b_3D_run004}"

RE="${RE:-200}"
UIN="${UIN:-0.25266}"

D_MM="12.0"
LIN_MM="24.0"
LF_MM="27.71"
LOUT_D="${LOUT_D:-8}"

if [[ ! "$LOUT_D" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    echo "LOUT_D must be numeric, got: $LOUT_D" >&2
    exit 2
fi

LOUT_MM=$(awk "BEGIN { printf \"%.2f\", $LOUT_D * $D_MM }")
LX_MM=$(awk "BEGIN { printf \"%.2f\", $LIN_MM + $LF_MM + $LOUT_MM }")
LOUT_M=$(awk "BEGIN { printf \"%.5f\", $LOUT_MM / 1000.0 }")
LX_M=$(awk "BEGIN { printf \"%.5f\", $LX_MM / 1000.0 }")

if [[ ! -d "$SRC" ]]; then
    echo "Missing source case: $SRC" >&2
    exit 1
fi

if [[ -e "$DST" ]]; then
    echo "Destination already exists: $DST" >&2
    exit 2
fi

mkdir -p "$DST/0" "$DST/logs"

cp -a "$SRC/constant" "$SRC/system" "$DST/"
cp -a "$SRC/0/U" "$SRC/0/T" "$SRC/0/p_rgh" "$SRC/0/alphat" "$DST/0/"

if [[ -f "$SRC/mesh.sh" ]]; then
    cp -a "$SRC/mesh.sh" "$DST/"
fi

if [[ -f "$SRC/run_solver.sh" ]]; then
    cp -a "$SRC/run_solver.sh" "$DST/"
fi

# Geometry changes require a clean remesh. Keep fields and dictionaries, drop old mesh/results.
rm -rf "$DST/constant/polyMesh" "$DST/postProcessing"
find "$DST" -maxdepth 1 -type d -name 'processor*' -exec rm -rf {} +
find "$DST" -maxdepth 1 -type d -regex '.*/[0-9]+(\.[0-9]+)?' -exec rm -rf {} +

touch "$DST/${RUN_ID}.foam" "$DST/V4b_${RUN_ID}.foam"

replace_if_present() {
    local pattern="$1"
    local replacement="$2"
    local file="$3"
    if [[ -f "$file" ]]; then
        perl -0pi -e "s/$pattern/$replacement/g" "$file"
    fi
}

replace_line_if_present() {
    local pattern="$1"
    local replacement="$2"
    local file="$3"
    if [[ -f "$file" ]]; then
        perl -0pi -e "s/$pattern/$replacement/gm" "$file"
    fi
}

replace_if_present 'V4b_3D_run003' 'V4b_3D_run004' "$DST/run_solver.sh"
replace_if_present 'run003' 'run004' "$DST/run_solver.sh"
replace_if_present 'Re=100' "Re=$RE" "$DST/run_solver.sh"
replace_if_present 'Re=200' "Re=$RE" "$DST/run_solver.sh"
replace_if_present '0\.12633' "$UIN" "$DST/0/U"
replace_if_present '0\.25266' "$UIN" "$DST/0/U"
replace_if_present '0\.12633' "$UIN" "$DST/system/controlDict"
replace_if_present '0\.25266' "$UIN" "$DST/system/controlDict"
replace_if_present '0\.1263' "$UIN" "$DST/system/controlDict"

# Try to patch common geometry parameter names in mesh scripts/dictionaries.
for geom_file in "$DST/mesh.sh" "$DST/system/blockMeshDict" "$DST/system/snappyHexMeshDict"; do
    replace_line_if_present '^(\s*LOUT_D\s*=\s*).*$' "\${1}$LOUT_D" "$geom_file"
    replace_line_if_present '^(\s*LOUT_MM\s*=\s*).*$' "\${1}$LOUT_MM" "$geom_file"
    replace_line_if_present '^(\s*LoutD\s*=\s*).*$' "\${1}$LOUT_D" "$geom_file"
    replace_line_if_present '^(\s*Lout_mm\s*=\s*).*$' "\${1}$LOUT_MM" "$geom_file"
    replace_line_if_present '^(\s*LX_MM\s*=\s*).*$' "\${1}$LX_MM" "$geom_file"
    replace_line_if_present '^(\s*Lx_mm\s*=\s*).*$' "\${1}$LX_MM" "$geom_file"
    replace_if_present 'Lout=5D' "Lout=${LOUT_D}D" "$geom_file"
    replace_if_present 'Lout=60mm' "Lout=${LOUT_MM}mm" "$geom_file"
    replace_if_present '111\.71' "$LX_MM" "$geom_file"
    replace_if_present '0\.11171' "$LX_M" "$geom_file"
done

cat > "$DST/CASE_VARIANT.md" <<EOF
# ${RUN_ID} Case Variant

- Parent case: \`$SRC\`
- Target study: \`V4b_3D\`
- Purpose: outlet sensitivity for the periodic \`Re=$RE\` configuration
- Mesh family: inherited from run003 / run001 medium lvl-2 setup, but requires fresh meshing
- Lin: 2D = 24.00 mm
- Lf: 2.309D = 27.71 mm
- Lout: ${LOUT_D}D = ${LOUT_MM} mm
- Lx: ${LX_MM} mm
- Uin: ${UIN} m/s

Expected workflow:

1. Inspect \`mesh.sh\` or the active mesh dictionary and confirm the new outlet extent.
2. Rebuild the mesh for the new \`Lout\`.
3. Run \`checkMesh\`.
4. Launch the solver and compare \`St\`, \`Cd\`, \`dp\`, and \`T_out\` against run003.
EOF

cat > "$DST/run_solver_parallel.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs

source /usr/share/openfoam/etc/bashrc

if [[ ! -d constant/polyMesh ]]; then
    echo "No mesh found. Build the run004 mesh first." >&2
    exit 2
fi

if compgen -G "processor*" > /dev/null; then
    echo "Processor directories already exist. Remove them intentionally before a fresh decompose." >&2
    exit 2
fi

echo "=== decomposePar: V4b_3D_run004, outlet sensitivity ==="
decomposePar > logs/decomposePar.log 2>&1

echo "=== launching buoyantBoussinesqPimpleFoam -parallel on 8 ranks ==="
nohup nice -n 10 mpirun -np 8 buoyantBoussinesqPimpleFoam -parallel > logs/solver.log 2>&1 &
echo "$!" > logs/solver.pid
echo "PID $(cat logs/solver.pid)"
EOF
chmod +x "$DST/run_solver.sh" "$DST/run_solver_parallel.sh" 2>/dev/null || true

echo "Prepared $DST"
echo "Lout=${LOUT_D}D (${LOUT_MM} mm), Lx=${LX_MM} mm, Re=$RE, Uin=$UIN m/s"
echo "Fresh mesh required before solver launch."
