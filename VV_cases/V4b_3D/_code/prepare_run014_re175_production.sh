#!/usr/bin/env bash
set -euo pipefail

# Prepare a production-geometry Re=175 V4b case with the same sampling contract
# as run008/run012/run013, for Hopf-onset bracketing.

SRC="${SRC:-/home/hexmachina/of_runs/V4b_3D_run008}"
DST="${DST:-/home/hexmachina/of_runs/V4b_3D_run014_re175_production}"
RUN_ID="${RUN_ID:-run014_re175}"
NPROCS="${NPROCS:-20}"
END_TIME="${END_TIME:-10}"
MAX_CO="${MAX_CO:-0.8}"
U_INF="${U_INF:-0.2210775}"

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
perl -0pi -e "s/startFrom\s+\w+;/startFrom       startTime;/" "$DST/system/controlDict"
perl -0pi -e "s/startTime\s+[0-9.eE+-]+;/startTime       0;/" "$DST/system/controlDict"
perl -0pi -e "s/endTime\s+[0-9.eE+-]+;/endTime         ${END_TIME};/" "$DST/system/controlDict"
perl -0pi -e "s/maxCo\s+[0-9.eE+-]+;/maxCo           ${MAX_CO};/" "$DST/system/controlDict"
perl -0pi -e "s/magUInf\s+[0-9.eE+-]+;/magUInf         ${U_INF};/" "$DST/system/controlDict"
perl -0pi -e "s/internalField\s+uniform\s+\([0-9.eE+-]+\s+0\s+0\);/internalField   uniform (${U_INF} 0 0);/" "$DST/0/U"
perl -0pi -e "s/value\s+uniform\s+\([0-9.eE+-]+\s+0\s+0\);/value           uniform (${U_INF} 0 0);/" "$DST/0/U"

cat > "$DST/CASE_VARIANT.md" <<EOF
# V4b_3D ${RUN_ID}

- Parent case: ${SRC}
- Purpose: production-geometry Re=175 point for Hopf-onset bracketing
- Geometry: accepted production domain, Lin=2D, Lout=8D, Lz=1D
- Mesh: run008 production medium mesh, 407,440 cells
- Physics: constant-property Cp-capacity setup, eConst + Boussinesq
- U_inf: ${U_INF} m/s
- Re: 175, using D=0.012 m and the same viscosity basis as the V4b campaign
- maxCo: ${MAX_CO}
- Target endTime: ${END_TIME} s
- Full field write interval: 0.08 s
- Midspan z=0 surface interval: 0.02 s
- Force/probe/wall-surface interval: 0.005 s
- MPI ranks: ${NPROCS}

Interpretation contract:

- Re=100 and Re=150 decayed to a steady late-time state in this production geometry.
- Re=200 is the expected periodic/reference production point.
- If late-window Cl_std remains finite with a robust spectral peak, Re=175 is post-Hopf/periodic.
- If late-window Cl_std decays toward numerical noise, Re=175 is pre-Hopf/steady.
- If the signal is weakly growing or weakly decaying, run a narrower bracket such as Re=185 or Re=165.
EOF

echo "Prepared $DST"
