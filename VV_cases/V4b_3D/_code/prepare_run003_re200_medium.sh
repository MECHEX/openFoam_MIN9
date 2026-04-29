#!/usr/bin/env bash
set -euo pipefail

# Prepare V4b_3D run003: Re=200 on the medium/lvl-2 mesh from run001.

SRC="${SRC:-/home/kik/of_runs/V4b_3D_run001}"
DST="${DST:-/home/kik/of_runs/V4b_3D_run003}"
WIN_DST="${WIN_DST:-/mnt/c/openfoam-case/VV_cases/V4b_3D_run003}"

RE="200"
UIN="0.25266"

if [[ ! -d "$SRC" ]]; then
    echo "Missing source case: $SRC" >&2
    exit 1
fi

if [[ -e "$DST" ]]; then
    echo "Destination already exists: $DST" >&2
    exit 2
fi

mkdir -p "$DST/0" "$DST/logs"
cp -a "$SRC/constant" "$SRC/system" "$SRC/mesh.sh" "$SRC/run_solver.sh" "$DST/"
cp -a "$SRC/0/U" "$SRC/0/T" "$SRC/0/p_rgh" "$SRC/0/alphat" "$DST/0/"
touch "$DST/run003.foam" "$DST/V4b_run003.foam"

perl -0pi -e "s/0\\.12633/$UIN/g" "$DST/0/U" "$DST/system/controlDict"
perl -0pi -e "s/Re=100/Re=$RE/g; s/V4b_3D_run001/V4b_3D_run003/g; s/t=0\\.\\.20s/t=0..5s/g" "$DST/run_solver.sh"
perl -0pi -e "s/deltaT\\s+1e-3;/deltaT          5e-4;\\nadjustTimeStep  yes;\\nmaxCo           0.8;\\nmaxDeltaT       1e-3;/" "$DST/system/controlDict"
perl -0pi -e "s/writeControl\\s+timeStep;\\nwriteInterval\\s+500;\\s+\\/\\/ every 0\\.5 s/writeControl    adjustableRunTime;\\nwriteInterval   0.5;      \\/\\/ every 0.5 s simulation time/" "$DST/system/controlDict"
perl -0pi -e "s/timeStart\\s+10;/timeStart       2;/" "$DST/system/controlDict"

cat > "$DST/run_solver_parallel.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs

source /usr/share/openfoam/etc/bashrc

if compgen -G "processor*" > /dev/null; then
    echo "Processor directories already exist. Remove them intentionally before a fresh decompose." >&2
    exit 2
fi

echo "=== decomposePar: V4b_3D_run003, Re=200, medium/lvl-2 mesh ==="
decomposePar > logs/decomposePar.log 2>&1

echo "=== launching buoyantBoussinesqPimpleFoam -parallel on 8 ranks ==="
nohup nice -n 10 mpirun -np 8 buoyantBoussinesqPimpleFoam -parallel > logs/solver.log 2>&1 &
echo "$!" > logs/solver.pid
echo "PID $(cat logs/solver.pid)"
EOF
chmod +x "$DST/run_solver.sh" "$DST/run_solver_parallel.sh"

if [[ ! -e "$WIN_DST" ]]; then
    mkdir -p "$WIN_DST"
    cp -a "$DST/0" "$DST/constant" "$DST/system" "$DST/mesh.sh" "$DST/run_solver.sh" "$DST/run_solver_parallel.sh" "$WIN_DST/"
    touch "$WIN_DST/run003.foam" "$WIN_DST/V4b_run003.foam"
fi

echo "Prepared $DST"
echo "Mirrored lightweight runnable case to $WIN_DST"
echo "Re=$RE, Uin=$UIN m/s, mesh copied from run001 medium/lvl-2"
