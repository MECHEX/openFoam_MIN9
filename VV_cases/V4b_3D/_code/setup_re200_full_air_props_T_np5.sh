#!/usr/bin/env bash

source /opt/openfoam13/etc/bashrc
set -euo pipefail

SRC="/home/hexmachina/of_runs/V4b_3D_run008"
DST="/home/hexmachina/of_runs/V4b_3D_run023_re200_fullAirPropsT_np5"
NPROCS=5

if [[ -e "$DST" ]]; then
    echo "Destination already exists: $DST"
    exit 2
fi

mkdir -p "$DST"
cp -a "$SRC/0" "$DST/0"
cp -a "$SRC/constant" "$DST/constant"
cp -a "$SRC/system" "$DST/system"
mkdir -p "$DST/logs"

cat > "$DST/constant/physicalProperties" <<'EOF_PHYS'
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
    thermo          janaf;
    equationOfState incompressiblePerfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}

pRef            100000;

mixture
{
    specie
    {
        molWeight       28.9;
    }
    equationOfState
    {
        pRef            100000;
    }
    thermodynamics
    {
        Tlow            100;
        Thigh           10000;
        Tcommon         1000;

        lowCpCoeffs
        (
            3.5309628
            -0.0001236595
            -5.0299339e-07
            2.4352768e-09
            -1.4087954e-12
            -1046.9637
            2.9674391
        );

        highCpCoeffs
        (
            2.9525407
            0.0013968838
            -4.9262577e-07
            7.8600091e-11
            -4.6074978e-15
            -923.93753
            5.8718221
        );
    }
    transport
    {
        As              1.458e-06;
        Ts              110.4;
    }
}
EOF_PHYS

# Incompressible-perfect-gas uses pRef for rho(T), while p remains the dynamic pressure.
python3 - <<'PY' "$DST/0/p"
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
text = text.replace("internalField   uniform 100000;", "internalField   uniform 0;", 1)
p.write_text(text)
PY

# Keep both h and e schemes available; the selected energy variable is e here.
python3 - <<'PY' "$DST/system/fvSolution"
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
text = text.replace('"(U|e)"', '"(U|h|e)"')
text = text.replace('"(U|e)Final"', '"(U|h|e)Final"')
p.write_text(text)
PY

python3 - <<'PY' "$DST/system/fvSchemes"
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
if "div(phi,h)" not in text:
    text = text.replace("    div(phi,e)                              Gauss upwind;\n", "    div(phi,e)                              Gauss upwind;\n    div(phi,h)                              Gauss upwind;\n")
p.write_text(text)
PY

foamDictionary "$DST/system/decomposeParDict" -entry numberOfSubdomains -set "$NPROCS" >/dev/null
foamDictionary "$DST/system/controlDict" -entry startFrom -set startTime >/dev/null
foamDictionary "$DST/system/controlDict" -entry startTime -set 0 >/dev/null
foamDictionary "$DST/system/controlDict" -entry stopAt -set endTime >/dev/null
foamDictionary "$DST/system/controlDict" -entry endTime -set 0.02 >/dev/null
foamDictionary "$DST/system/controlDict" -entry deltaT -set 0.0005 >/dev/null
foamDictionary "$DST/system/controlDict" -entry writeInterval -set 0.01 >/dev/null
foamDictionary "$DST/system/controlDict" -entry purgeWrite -set 0 >/dev/null

cd "$DST"
checkMesh > logs/log.checkMesh.smoke 2>&1
decomposePar -force > logs/log.decomposePar.smoke_np5 2>&1
mpirun --oversubscribe -np "$NPROCS" foamRun -solver fluid -parallel > logs/log.foamRun.smoke_np5 2>&1

echo "$DST"
