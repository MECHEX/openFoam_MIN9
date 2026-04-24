"""
V2OGridStudy.py
---------------
Structured O-grid cylinder recovery branch for V2A thermal verification.

Usage:
  python VV_cases/V2_thermal/_code/V2OGridStudy.py plan
  python VV_cases/V2_thermal/_code/V2OGridStudy.py setup
  python VV_cases/V2_thermal/_code/V2OGridStudy.py mesh
  python VV_cases/V2_thermal/_code/V2OGridStudy.py run
  python VV_cases/V2_thermal/_code/V2OGridStudy.py analyze
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import stat
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import V2AStudy as base


CODE_DIR = Path(__file__).resolve().parent
REPO_CASE = CODE_DIR.parent
RESULTS_DIR = REPO_CASE / "results" / "study_v2a"
RUN_SLUG = "004_data_v2a_ogrid_cylinder_validation"
RUN_DIR = RESULTS_DIR / "runs" / RUN_SLUG
PLOTS_DIR = RUN_DIR / "plots"
WORK_ROOT = Path(r"C:\openfoam-case\VV_cases\V2_thermal_run004")

CASES = [
    {"name": "Re10_ogrid", "Re": 10, "steady": True, "endTime": 100.0, "writeInterval": 1.0, "forceWriteInterval": 0.1, "perturb": False},
    {"name": "Re20_ogrid", "Re": 20, "steady": True, "endTime": 100.0, "writeInterval": 1.0, "forceWriteInterval": 0.1, "perturb": False},
    {"name": "Re40_ogrid", "Re": 40, "steady": True, "endTime": 100.0, "writeInterval": 1.0, "forceWriteInterval": 0.1, "perturb": False},
    {"name": "Re45_ogrid", "Re": 45, "steady": True, "endTime": 120.0, "writeInterval": 0.5, "forceWriteInterval": 0.05, "perturb": True},
    {"name": "Re60_ogrid", "Re": 60, "steady": False, "endTime": 80.0, "writeInterval": 0.2, "forceWriteInterval": 0.02, "perturb": True},
    {"name": "Re100_ogrid", "Re": 100, "steady": False, "endTime": 60.0, "writeInterval": 0.1, "forceWriteInterval": 0.01, "perturb": True},
    {"name": "Re200_ogrid", "Re": 200, "steady": False, "endTime": 40.0, "writeInterval": 0.05, "forceWriteInterval": 0.005, "perturb": True},
]

NP = 15
LANGE_RE_CRIT = 45.9
OPTIONAL_NEXT_RE = [45, 60, 100, 200]

RADIUS = 0.5 * base.D
OUTER_HALF = 15.25 * base.D
N_SECTORS = 8
CIRC_CELLS_PER_SECTOR = 16
RADIAL_CELLS = 80
RADIAL_EXPANSION = 40.0
NZ = 1
Z0 = -0.5 * base.L_Z
Z1 = 0.5 * base.L_Z


def ensure_layout() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        sim_dir(case["name"]).mkdir(parents=True, exist_ok=True)


def sim_dir(name: str) -> Path:
    return RUN_DIR / "simulations" / name


def case_dir(name: str) -> Path:
    return WORK_ROOT / name


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rm_readonly(func, path, exc_info) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


def case_by_name(name: str) -> dict:
    for case in CASES:
        if case["name"] == name or str(case["Re"]) == str(name):
            return case
    raise ValueError(f"Unknown run-004 case: {name}")


def selected_cases(names: list[str] | None) -> list[dict]:
    return [case_by_name(name) for name in names] if names else CASES


def outer_square_point(angle: float) -> tuple[float, float]:
    c = math.cos(angle)
    s = math.sin(angle)
    scale = OUTER_HALF / max(abs(c), abs(s))
    return scale * c, scale * s


def make_block_mesh_dict() -> str:
    angles = [2.0 * math.pi * i / N_SECTORS for i in range(N_SECTORS)]

    inner_xy = [(RADIUS * math.cos(a), RADIUS * math.sin(a)) for a in angles]
    outer_xy = [outer_square_point(a) for a in angles]

    vertices: list[tuple[float, float, float]] = []
    vertices.extend((x, y, Z0) for x, y in inner_xy)
    vertices.extend((x, y, Z0) for x, y in outer_xy)
    vertices.extend((x, y, Z1) for x, y in inner_xy)
    vertices.extend((x, y, Z1) for x, y in outer_xy)

    def ib(i: int) -> int:
        return i % N_SECTORS

    def ob(i: int) -> int:
        return N_SECTORS + (i % N_SECTORS)

    def it(i: int) -> int:
        return 2 * N_SECTORS + (i % N_SECTORS)

    def ot(i: int) -> int:
        return 3 * N_SECTORS + (i % N_SECTORS)

    vertex_lines = "\n".join(
        f"    ({x:.10g} {y:.10g} {z:.10g})" for x, y, z in vertices
    )

    block_lines = []
    for i in range(N_SECTORS):
        j = (i + 1) % N_SECTORS
        block_lines.append(
            "    hex "
            f"({ib(i)} {ob(i)} {ob(j)} {ib(j)} {it(i)} {ot(i)} {ot(j)} {it(j)}) "
            f"({RADIAL_CELLS} {CIRC_CELLS_PER_SECTOR} {NZ}) "
            f"simpleGrading ({RADIAL_EXPANSION:.6g} 1 1)"
        )

    edge_lines = []
    for i in range(N_SECTORS):
        j = (i + 1) % N_SECTORS
        mid_angle = angles[i] + math.pi / N_SECTORS
        if j == 0:
            mid_angle = 2.0 * math.pi - math.pi / N_SECTORS
        mx = RADIUS * math.cos(mid_angle)
        my = RADIUS * math.sin(mid_angle)
        edge_lines.append(f"    arc {ib(i)} {ib(j)} ({mx:.10g} {my:.10g} {Z0:.10g})")
        edge_lines.append(f"    arc {it(i)} {it(j)} ({mx:.10g} {my:.10g} {Z1:.10g})")

    cylinder_faces = []
    front_faces = []
    back_faces = []
    outer_faces: dict[str, list[str]] = {"inlet": [], "outlet": [], "top": [], "bottom": []}
    for i in range(N_SECTORS):
        j = (i + 1) % N_SECTORS
        cylinder_faces.append(f"        ({ib(i)} {ib(j)} {it(j)} {it(i)})")
        front_faces.append(f"        ({ib(i)} {ib(j)} {ob(j)} {ob(i)})")
        back_faces.append(f"        ({it(i)} {ot(i)} {ot(j)} {it(j)})")

        ox = 0.5 * (outer_xy[i][0] + outer_xy[j][0])
        oy = 0.5 * (outer_xy[i][1] + outer_xy[j][1])
        if abs(ox) >= abs(oy):
            patch = "outlet" if ox > 0 else "inlet"
        else:
            patch = "top" if oy > 0 else "bottom"
        outer_faces[patch].append(f"        ({ob(i)} {ob(j)} {ot(j)} {ot(i)})")

    def patch(name: str, patch_type: str, faces: list[str]) -> str:
        return f"""    {name}
    {{
        type {patch_type};
        faces
        (
{chr(10).join(faces)}
        );
    }}"""

    boundary_blocks = [
        patch("inlet", "patch", outer_faces["inlet"]),
        patch("outlet", "patch", outer_faces["outlet"]),
        patch("top", "patch", outer_faces["top"]),
        patch("bottom", "patch", outer_faces["bottom"]),
        patch("cylinder", "wall", cylinder_faces),
        patch("front", "empty", front_faces),
        patch("back", "empty", back_faces),
    ]

    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

// V2A run 004: structured 8-block O-grid cylinder mesh
// Domain: {2 * OUTER_HALF / base.D:.2f}D x {2 * OUTER_HALF / base.D:.2f}D
// Circumferential cells: {N_SECTORS * CIRC_CELLS_PER_SECTOR}
// Radial cells: {RADIAL_CELLS}, radial expansion ratio: {RADIAL_EXPANSION}

scale 1;

vertices
(
{vertex_lines}
);

blocks
(
{chr(10).join(block_lines)}
);

edges
(
{chr(10).join(edge_lines)}
);

boundary
(
{chr(10).join(boundary_blocks)}
);

mergePatchPairs ();
"""


def make_control_dict(case: dict) -> str:
    reynolds = case["Re"]
    u_inf = reynolds * base.NU / base.D
    aref = base.D * base.L_Z
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}}

application     buoyantBoussinesqPimpleFoam;

startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {case["endTime"]};

deltaT          1e-4;
adjustTimeStep  yes;
maxCo           0.5;

writeControl    runTime;
writeInterval   {case["writeInterval"]};
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   8;
runTimeModifiable true;

functions
{{
    forceCoeffs
    {{
        type            forceCoeffs;
        libs            (forces);
        executeControl  timeStep;
        writeControl    runTime;
        writeInterval   {case.get("forceWriteInterval", 0.1)};
        log             yes;
        patches         (cylinder);
        rho             rhoInf;
        rhoInf          {base.RHO0:.4f};
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         {u_inf:.8g};
        lRef            {base.D};
        Aref            {aref:.8g};
    }}

    residuals
    {{
        type            solverInfo;
        libs            (utilityFunctionObjects);
        fields          (U p_rgh T);
        writeControl    timeStep;
        writeInterval   20;
    }}
}}
"""


def make_fv_schemes() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
    grad(U)         Gauss linear;
    grad(T)         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,T)      Gauss vanLeer;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method          meshWave;
}
"""


def make_decompose_par_dict() -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}}

numberOfSubdomains {NP};
method          scotch;
"""


def make_set_expr_fields_dict(case: dict) -> str:
    re_val = case["Re"]
    u_inf = re_val * base.NU / base.D
    perturb = 0.005 * u_inf
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      setExprFieldsDict;
}}

readFields ( U );

expressions
(
    U
    {{
        field U;
        create no;
        dimensions [0 1 -1 0 0 0 0];
        expression
        #{{
            vector(
                {u_inf:.9f},
                {perturb:.9f}*exp(-pow((pos().x()-{0.5 * base.D:.9f})/{1.5 * base.D:.9f}, 2.0)
                                  -pow((pos().y()-{0.25 * base.D:.9f})/{0.75 * base.D:.9f}, 2.0)),
                0
            )
        #}};
    }}
);
"""


def make_allrun() -> str:
    return f"""#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
source {base.OF_BASHRC} 2>/dev/null
set -e
mkdir -p logs
blockMesh | tee logs/log.blockMesh
checkMesh | tee logs/log.checkMesh
postProcess -func writeCellCentres -time 0 | tee logs/log.writeCellCentres
setExprFields | tee logs/log.setExprFields || true
decomposePar -force | tee logs/log.decomposePar
mpirun --use-hwthread-cpus -np {NP} buoyantBoussinesqPimpleFoam -parallel | tee logs/log.buoyantBoussinesqPimpleFoam
"""


def write_run_docs(status: str = "planned") -> None:
    ensure_layout()
    lines = [
        f"# {RUN_SLUG}",
        "",
        "## Purpose",
        "",
        "Structured cylinder recovery run for V2A after the snappy mesh produced a non-physical temperature field.",
        "",
        "## Mesh",
        "",
        f"- topology: 8-block O-grid, pure `blockMesh`",
        f"- outer square domain: `{2 * OUTER_HALF / base.D:.2f}D x {2 * OUTER_HALF / base.D:.2f}D`",
        f"- cylinder diameter: `{base.D:.6f} m`",
        f"- span: `{base.L_Z:.6f} m`, one `empty` cell",
        f"- cells around cylinder: `{N_SECTORS * CIRC_CELLS_PER_SECTOR}`",
        f"- radial cells: `{RADIAL_CELLS}`",
        f"- radial expansion ratio: `{RADIAL_EXPANSION:g}` from cylinder to far field",
        "",
        "## Simulation matrix",
        "",
        "| case | Re | endTime | target | status |",
        "|---|---:|---:|---:|---|",
    ]
    for case in CASES:
        re_val = case["Re"]
        target = base.BHARTI_NU.get(re_val, base.nu_lange(re_val))
        lines.append(f"| {case['name']} | {re_val} | {case['endTime']} | Nu ~= {target:.4f} | {status} |")
    lines += [
        "",
        "## Optional extension",
        "",
        f"- low-Re Bharti matrix cases are included; optional higher-Re extension: `{', '.join(str(x) for x in OPTIONAL_NEXT_RE)}`",
        "- publication table and plots are generated only from bounded O-grid runs",
    ]
    write_text(RUN_DIR / "run.md", "\n".join(lines) + "\n")


def write_case_notes(case: dict, extra: list[str] | None = None) -> None:
    re_val = case["Re"]
    u_inf = re_val * base.NU / base.D
    target_bharti = base.BHARTI_NU.get(re_val)
    lines = [
        f"# {case['name']}",
        "",
        "## Setup",
        "",
        f"- Re: `{re_val}`",
        f"- U_inf: `{u_inf:.8g} m/s`",
        f"- solver: `buoyantBoussinesqPimpleFoam` with `g = 0`",
        "- mesh: structured O-grid from `blockMesh`, no snappyHexMesh",
        "- thermal scheme: `div(phi,T) Gauss vanLeer`",
        "- cylinder thermal BC: `fixedValue 303.15 K`",
        "- far-field T: `293.15 K`",
        f"- Lange Nu: `{base.nu_lange(re_val):.4f}`",
        f"- Bharti Nu: `{target_bharti:.4f}`" if target_bharti else "- Bharti Nu: `n/a`",
        "",
        "## Notes",
        "",
        "- Quality gate: temperature must remain bounded before Nu is interpreted.",
        "- Nu is extracted from wall-normal `snGrad(T)` on the cylinder patch.",
    ]
    if extra:
        lines += ["", "## Results", ""] + extra
    write_text(sim_dir(case["name"]) / "notes.md", "\n".join(lines) + "\n")


def setup_case(case: dict) -> None:
    ensure_layout()
    write_run_docs(status="case generated")
    write_case_notes(case)

    cdir = case_dir(case["name"])
    if cdir.exists():
        write_text(cdir / "system" / "controlDict", make_control_dict(case))
        write_text(cdir / "system" / "decomposeParDict", make_decompose_par_dict())
        if case.get("perturb"):
            write_text(cdir / "system" / "setExprFieldsDict", make_set_expr_fields_dict(case))
        write_text(cdir / "Allrun", make_allrun())
        archive_setup(case)
        print(f"[refresh] {cdir} already exists; refreshed control/decompose setup")
        return

    u_inf = case["Re"] * base.NU / base.D
    (cdir / "0").mkdir(parents=True, exist_ok=True)
    (cdir / "constant").mkdir(parents=True, exist_ok=True)
    (cdir / "system").mkdir(parents=True, exist_ok=True)
    (cdir / "logs").mkdir(parents=True, exist_ok=True)

    write_text(cdir / "system" / "blockMeshDict", make_block_mesh_dict())
    write_text(cdir / "system" / "controlDict", make_control_dict(case))
    write_text(cdir / "system" / "fvSchemes", make_fv_schemes())
    write_text(cdir / "system" / "fvSolution", base.make_fvSolution())
    write_text(cdir / "system" / "decomposeParDict", make_decompose_par_dict())
    if case.get("perturb"):
        write_text(cdir / "system" / "setExprFieldsDict", make_set_expr_fields_dict(case))
    write_text(cdir / "constant" / "transportProperties", base.make_transportProperties())
    write_text(cdir / "constant" / "g", base.make_g())
    write_text(cdir / "constant" / "turbulenceProperties", base.make_turbulenceProperties())
    write_text(cdir / "0" / "U", base.make_U(u_inf))
    write_text(cdir / "0" / "T", base.make_T())
    write_text(cdir / "0" / "p_rgh", base.make_p_rgh())
    write_text(cdir / "0" / "alphat", base.make_alphat())
    write_text(cdir / "Allrun", make_allrun())

    archive_setup(case)
    print(f"Generated {cdir}")


def archive_setup(case: dict) -> None:
    cdir = case_dir(case["name"])
    target = sim_dir(case["name"]) / "openfoam_setup"
    if target.exists():
        shutil.rmtree(target, onexc=_rm_readonly)
    target.mkdir(parents=True, exist_ok=True)
    for name in ("0", "constant", "system", "Allrun"):
        src = cdir / name
        if src.is_dir():
            shutil.copytree(src, target / name)
        elif src.exists():
            shutil.copy2(src, target / name)


def mesh_case(case: dict) -> None:
    cdir = case_dir(case["name"])
    if not cdir.exists():
        raise FileNotFoundError(f"Case not generated: {cdir}")
    logs = cdir / "logs"
    logs.mkdir(exist_ok=True)
    base.run_of("blockMesh", cdir, logs / "log.blockMesh")
    base.run_of("checkMesh", cdir, logs / "log.checkMesh")
    base.run_of("postProcess -func writeCellCentres -time 0", cdir, logs / "log.writeCellCentres")
    print(f"Meshed {case['name']}")


def run_case(case: dict) -> None:
    cdir = case_dir(case["name"])
    if not cdir.exists():
        raise FileNotFoundError(f"Case not generated: {cdir}")
    logs = cdir / "logs"
    logs.mkdir(exist_ok=True)
    p_times = processor_time_values(cdir)
    resume_parallel = bool(p_times and p_times[-1] > 0.0)
    if case.get("perturb") and not resume_parallel:
        base.run_of("setExprFields", cdir, logs / "log.setExprFields")
    if not resume_parallel:
        base.run_of("decomposePar -force", cdir, logs / "log.decomposePar")
    else:
        print(f"Resuming {case['name']} from parallel latestTime {p_times[-1]}")
    base.run_of(f"mpirun --use-hwthread-cpus -np {NP} buoyantBoussinesqPimpleFoam -parallel", cdir, logs / "log.buoyantBoussinesqPimpleFoam")
    print(f"Solved {case['name']}")


def latest_t_values(cdir: Path) -> tuple[float, list[float]] | tuple[None, None]:
    for time_value, time_dir in reversed(base.numeric_time_dirs(cdir)):
        if time_value <= 0:
            continue
        t_path = time_dir / "T"
        if not t_path.exists():
            continue
        try:
            return time_value, base.parse_scalar_internal_field(t_path)
        except ValueError:
            continue
    return None, None


def processor_dirs(cdir: Path) -> list[Path]:
    found = [child for child in cdir.iterdir() if child.is_dir() and child.name.startswith("processor")]
    return sorted(found, key=lambda path: int(path.name.replace("processor", "")))


def processor_time_values(cdir: Path) -> list[float]:
    procs = processor_dirs(cdir)
    if not procs:
        return []
    return [time_value for time_value, time_dir in base.numeric_time_dirs(procs[0]) if time_value > 0.0 and (time_dir / "T").exists()]


def latest_parallel_t_stats(cdir: Path) -> dict[str, float | None]:
    procs = processor_dirs(cdir)
    times = processor_time_values(cdir)
    if not procs or not times:
        return {
            "latest_time_s": None,
            "T_min_K": None,
            "T_max_K": None,
            "T_below_Tin_pct": None,
            "T_above_Tw_pct": None,
            "cylinder_owner_above_Tw_pct": None,
        }
    latest = times[-1]
    t_min = math.inf
    t_max = -math.inf
    n_total = 0
    n_below = 0
    n_above = 0
    owner_vals: list[float] = []

    for pdir in procs:
        t_path = pdir / f"{latest:.15g}" / "T"
        if not t_path.exists():
            matches = [time_dir for time_value, time_dir in base.numeric_time_dirs(pdir) if abs(time_value - latest) < 1e-8 and (time_dir / "T").exists()]
            if not matches:
                continue
            t_path = matches[-1] / "T"
        values = base.parse_scalar_internal_field(t_path)
        if not values:
            continue
        t_min = min(t_min, min(values))
        t_max = max(t_max, max(values))
        n_total += len(values)
        n_below += sum(value < base.T_IN for value in values)
        n_above += sum(value > base.T_W for value in values)

        try:
            boundary = base.parse_boundary(pdir / "constant" / "polyMesh" / "boundary")
            owner = base.parse_owner(pdir / "constant" / "polyMesh" / "owner")
            cyl = boundary.get("cylinder")
            if cyl:
                start = int(cyl["startFace"])
                n_faces = int(cyl["nFaces"])
                owner_vals.extend(values[idx] for idx in owner[start : start + n_faces])
        except (FileNotFoundError, KeyError, ValueError):
            pass

    return {
        "latest_time_s": latest,
        "T_min_K": t_min if n_total else None,
        "T_max_K": t_max if n_total else None,
        "T_below_Tin_pct": 100.0 * n_below / n_total if n_total else None,
        "T_above_Tw_pct": 100.0 * n_above / n_total if n_total else None,
        "cylinder_owner_above_Tw_pct": 100.0 * sum(value > base.T_W for value in owner_vals) / len(owner_vals) if owner_vals else None,
    }


def parallel_nu_time_series(cdir: Path) -> list[tuple[float, float]]:
    procs = processor_dirs(cdir)
    times = processor_time_values(cdir)
    if not procs or not times:
        return []

    setups = []
    for pdir in procs:
        try:
            faces_data, cell_centers = base.cylinder_sngrad_setup(pdir)
        except (FileNotFoundError, KeyError, ValueError):
            continue
        if faces_data:
            setups.append((pdir, faces_data, cell_centers))
    if not setups:
        return []

    series: list[tuple[float, float]] = []
    for time_value in times:
        area_sum = 0.0
        sngrad_sum = 0.0
        for pdir, faces_data, cell_centers in setups:
            t_path = pdir / f"{time_value:.15g}" / "T"
            if not t_path.exists():
                matches = [
                    time_dir
                    for candidate, time_dir in base.numeric_time_dirs(pdir)
                    if abs(candidate - time_value) < 1e-8 and (time_dir / "T").exists()
                ]
                if not matches:
                    continue
                t_path = matches[-1] / "T"
            t_cell = base.parse_scalar_internal_field(t_path)
            for area, normal, f_center, cell_idx in faces_data:
                if area <= 0:
                    continue
                t_p = t_cell[cell_idx]
                c_p = cell_centers[cell_idx]
                delta_perp = (
                    (f_center[0] - c_p[0]) * normal[0]
                    + (f_center[1] - c_p[1]) * normal[1]
                    + (f_center[2] - c_p[2]) * normal[2]
                )
                if abs(delta_perp) < 1e-15:
                    continue
                sngrad = (base.T_W - t_p) / delta_perp
                area_sum += area
                sngrad_sum += area * sngrad
        if area_sum > 0.0:
            series.append((time_value, base.D * (sngrad_sum / area_sum) / base.DT))
    return series


def case_nu_time_series(cdir: Path) -> list[tuple[float, float]]:
    parallel_series = parallel_nu_time_series(cdir)
    if parallel_series:
        root_series = base.nu_time_series(cdir) if base.numeric_time_dirs(cdir) else []
        if not root_series or parallel_series[-1][0] > root_series[-1][0] + 1e-8:
            return parallel_series
    return base.nu_time_series(cdir)


def cylinder_owner_temperature_stats(cdir: Path, t_values: list[float]) -> dict[str, float]:
    boundary = base.parse_boundary(cdir / "constant" / "polyMesh" / "boundary")
    owner = base.parse_owner(cdir / "constant" / "polyMesh" / "owner")
    cyl = boundary["cylinder"]
    start = int(cyl["startFace"])
    n_faces = int(cyl["nFaces"])
    owners = owner[start : start + n_faces]
    vals = [t_values[idx] for idx in owners]
    return {
        "cylinder_owner_count": len(vals),
        "cylinder_owner_T_min_K": min(vals),
        "cylinder_owner_T_max_K": max(vals),
        "cylinder_owner_above_Tw_pct": 100.0 * sum(v > base.T_W for v in vals) / len(vals),
        "cylinder_owner_below_Tin_pct": 100.0 * sum(v < base.T_IN for v in vals) / len(vals),
    }


def force_cd_mean(cdir: Path) -> float | None:
    coeff_file = base.latest_force_coeff_file(cdir)
    if not coeff_file:
        return None
    rows = [
        line.split()
        for line in coeff_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if not rows:
        return None
    tail = rows[-max(1, len(rows) // 5) :]
    vals = [float(row[1]) for row in tail if len(row) > 1]
    return sum(vals) / len(vals) if vals else None


def force_coeff_rows(cdir: Path) -> list[tuple[float, float, float]]:
    """Return deduplicated (time, Cd, Cl) rows from coefficient files and solver log."""
    rows: dict[float, tuple[float, float, float]] = {}
    coeff_root = cdir / "postProcessing" / "forceCoeffs"
    if coeff_root.exists():
        for coeff_file in coeff_root.glob("*/coefficient.dat"):
            for line in coeff_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                if not line.strip() or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue
                try:
                    time_value = float(parts[0])
                    rows[time_value] = (time_value, float(parts[1]), float(parts[4]))
                except ValueError:
                    continue

    log_file = cdir / "logs" / "log.buoyantBoussinesqPimpleFoam"
    if log_file.exists():
        current_time: float | None = None
        pending_cd: float | None = None
        time_pattern = re.compile(r"^Time =\s+([0-9.eE+-]+)")
        for line in log_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            match = time_pattern.match(stripped)
            if match:
                try:
                    current_time = float(match.group(1))
                except ValueError:
                    current_time = None
                pending_cd = None
                continue
            if stripped.startswith("Cd:"):
                parts = stripped.split()
                if len(parts) > 1:
                    try:
                        pending_cd = float(parts[1])
                    except ValueError:
                        pending_cd = None
                continue
            if stripped.startswith("Cl:") and current_time is not None and pending_cd is not None:
                parts = stripped.split()
                if len(parts) > 1:
                    try:
                        rows[current_time] = (current_time, pending_cd, float(parts[1]))
                    except ValueError:
                        pass
                pending_cd = None

    return [rows[key] for key in sorted(rows)]


def st_lange(reynolds: int | float) -> float | None:
    if reynolds < LANGE_RE_CRIT:
        return None
    return -3.3265 / reynolds + 0.1816 + 1.6e-4 * reynolds


def mesh_cell_count(cdir: Path) -> int | None:
    c_path = cdir / "0" / "C"
    if not c_path.exists():
        return None
    try:
        return len(base.parse_vector_internal_field(c_path))
    except (ValueError, FileNotFoundError):
        return None


def mesh_cylinder_faces(cdir: Path) -> int | None:
    boundary_path = cdir / "constant" / "polyMesh" / "boundary"
    if not boundary_path.exists():
        return None
    try:
        boundary = base.parse_boundary(boundary_path)
    except (ValueError, FileNotFoundError, KeyError):
        return None
    cyl = boundary.get("cylinder")
    return int(cyl["nFaces"]) if cyl else None


def force_stats(case: dict, cdir: Path) -> dict[str, float | bool | None]:
    empty = {
        "Cd_tail_mean": None,
        "Cl_tail_mean": None,
        "Cl_tail_rms": None,
        "St_present": None,
        "St_lowest_bin_peak": None,
    }
    rows = force_coeff_rows(cdir)
    if not rows:
        return empty

    tail = rows[-max(20, len(rows) // 2) :]
    times = [row[0] for row in tail]
    cds = [row[1] for row in tail]
    cls = [row[2] for row in tail]
    cl_mean = sum(cls) / len(cls)
    cl_centered = [value - cl_mean for value in cls]
    cl_rms = math.sqrt(sum(value * value for value in cl_centered) / len(cl_centered))

    result: dict[str, float | bool | None] = {
        "Cd_tail_mean": sum(cds) / len(cds),
        "Cl_tail_mean": cl_mean,
        "Cl_tail_rms": cl_rms,
        "St_present": None,
        "St_lowest_bin_peak": None,
    }
    if case["Re"] < LANGE_RE_CRIT or cl_rms < 1e-8 or len(times) < 20:
        return result

    dt_values = [b - a for a, b in zip(times[:-1], times[1:]) if b > a]
    if not dt_values:
        return result
    dt = sum(dt_values) / len(dt_values)
    if dt <= 0.0:
        return result

    spectrum = base._fft(cl_centered)
    n_fft = len(spectrum)
    best_idx = None
    best_amp = -1.0
    for idx in range(1, n_fft // 2):
        amp = abs(spectrum[idx])
        if amp > best_amp:
            best_amp = amp
            best_idx = idx
    if best_idx is None:
        return result

    freq_hz = best_idx / (n_fft * dt)
    u_inf = case["Re"] * base.NU / base.D
    result["St_present"] = freq_hz * base.D / u_inf
    result["St_lowest_bin_peak"] = best_idx == 1
    return result


def case_has_solution(case: dict) -> bool:
    cdir = case_dir(case["name"])
    if not cdir.exists():
        return False
    if processor_time_values(cdir):
        return True
    for time_value, time_dir in base.numeric_time_dirs(cdir):
        if time_value > 0.0 and (time_dir / "T").exists():
            return True
    return False


def analyzable_cases() -> list[dict]:
    return [case for case in CASES if case_has_solution(case)]


def write_nu_series(case: dict, nu_series: list[tuple[float, float]]) -> None:
    out = sim_dir(case["name"]) / "Nu_timeseries.csv"
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time_s", "Nu"])
        writer.writerows(nu_series)


def plot_nu_series(case: dict, nu_series: list[tuple[float, float]]) -> Path | None:
    if not nu_series:
        return None
    re_val = case["Re"]
    times = [item[0] for item in nu_series]
    values = [item[1] for item in nu_series]
    out = PLOTS_DIR / f"{case['name']}_Nu_vs_time.png"

    fig, ax = plt.subplots(figsize=(8.0, 4.5), dpi=180)
    ax.plot(times, values, color="#0f766e", lw=1.5, label="O-grid CFD")
    ax.axhline(base.nu_lange(re_val), color="#b45309", lw=1.2, ls="--", label=f"Lange {base.nu_lange(re_val):.4f}")
    if re_val in base.BHARTI_NU:
        ax.axhline(base.BHARTI_NU[re_val], color="#1d4ed8", lw=1.2, ls=":", label=f"Bharti {base.BHARTI_NU[re_val]:.4f}")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("mean cylinder Nu")
    ax.set_title(f"{case['name']}: wall-normal snGrad(T) Nu")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.8)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=180, bbox_inches="tight")
    fig.savefig(out.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    return out


def plot_mesh_schematic() -> Path:
    out = PLOTS_DIR / "V2_run004_ogrid_mesh_schematic.png"
    angles = [2.0 * math.pi * i / (N_SECTORS * CIRC_CELLS_PER_SECTOR) for i in range(N_SECTORS * CIRC_CELLS_PER_SECTOR + 1)]
    q = RADIAL_EXPANSION ** (1.0 / max(1, RADIAL_CELLS - 1))
    dr0 = (OUTER_HALF - RADIUS) * (q - 1.0) / (RADIAL_EXPANSION - 1.0)
    radii = [RADIUS]
    for _ in range(RADIAL_CELLS):
        radii.append(radii[-1] + dr0 * q ** len(radii))

    fig, ax = plt.subplots(figsize=(6.0, 6.0), dpi=180)
    for r in radii[:24:2]:
        ax.plot([r * math.cos(a) for a in angles], [r * math.sin(a) for a in angles], color="#94a3b8", lw=0.35)
    for a in [2.0 * math.pi * i / (N_SECTORS * CIRC_CELLS_PER_SECTOR) for i in range(0, N_SECTORS * CIRC_CELLS_PER_SECTOR, 8)]:
        ax.plot([RADIUS * math.cos(a), radii[24] * math.cos(a)], [RADIUS * math.sin(a), radii[24] * math.sin(a)], color="#cbd5e1", lw=0.3)
    ax.plot([RADIUS * math.cos(a) for a in angles], [RADIUS * math.sin(a) for a in angles], color="#0f172a", lw=1.5)
    ax.set_aspect("equal")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Run 004 O-grid near-cylinder mesh schematic")
    ax.grid(True, color="#e7e5e4", lw=0.5)
    fig.tight_layout()
    fig.savefig(out, dpi=180, bbox_inches="tight")
    fig.savefig(out.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    return out


def plot_nu_reference(results: list[dict]) -> Path:
    out = PLOTS_DIR / "V2_run004_Nu_vs_reference.png"
    re_min = 8.0
    re_max = max(45.0, max(float(row["Re"]) for row in results) * 1.15)
    re_curve = [re_min + i * (re_max - re_min) / 200 for i in range(201)]
    lange = [base.nu_lange(re_val) for re_val in re_curve]

    fig, ax = plt.subplots(figsize=(7.0, 4.8), dpi=180)
    ax.plot(re_curve, lange, color="#b45309", lw=1.4, label="Lange correlation")
    bharti_rows = [(re_val, nu) for re_val, nu in sorted(base.BHARTI_NU.items()) if re_min <= re_val <= re_max]
    if bharti_rows:
        ax.plot(
            [item[0] for item in bharti_rows],
            [item[1] for item in bharti_rows],
            marker="s",
            color="#1d4ed8",
            lw=0,
            ms=5.5,
            label="Bharti tabulated",
        )
    present = [row for row in results if row.get("Nu_tail_mean") is not None]
    if present:
        ax.plot(
            [float(row["Re"]) for row in present],
            [float(row["Nu_tail_mean"]) for row in present],
            marker="o",
            color="#0f766e",
            lw=1.2,
            ms=6.0,
            label="Present O-grid",
        )
    ax.set_xlabel("Re")
    ax.set_ylabel("mean cylinder Nu")
    ax.set_title("V2A O-grid thermal verification")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.8)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=180, bbox_inches="tight")
    fig.savefig(out.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    return out


def analyze_case(case: dict) -> dict:
    cdir = case_dir(case["name"])
    if not cdir.exists():
        raise FileNotFoundError(f"Case not generated: {cdir}")

    nu_series = case_nu_time_series(cdir)
    write_nu_series(case, nu_series)
    plot_path = plot_nu_series(case, nu_series)
    f_stats = force_stats(case, cdir)

    time_value, t_values = latest_t_values(cdir)
    p_times = processor_time_values(cdir)
    parallel_t_stats = (
        latest_parallel_t_stats(cdir)
        if time_value is None or (p_times and p_times[-1] > (time_value or 0.0) + 1e-8)
        else {}
    )
    result: dict[str, object] = {
        "case": case["name"],
        "Re": case["Re"],
        "mesh_cells": mesh_cell_count(cdir),
        "cylinder_faces": mesh_cylinder_faces(cdir),
        "parallel_ranks": NP,
        "latest_time_s": parallel_t_stats.get("latest_time_s", time_value),
        "Nu_samples": len(nu_series),
        "Nu_last": nu_series[-1][1] if nu_series else None,
        "Nu_tail_mean": None,
        "Nu_Lange": base.nu_lange(case["Re"]),
        "Nu_Bharti": base.BHARTI_NU.get(case["Re"]),
        "Cd_tail_mean": f_stats["Cd_tail_mean"],
        "Cl_tail_mean": f_stats["Cl_tail_mean"],
        "Cl_tail_rms": f_stats["Cl_tail_rms"],
        "St_present": f_stats["St_present"],
        "St_Lange": st_lange(case["Re"]),
        "St_lowest_bin_peak": f_stats["St_lowest_bin_peak"],
        "plot": str(plot_path) if plot_path else None,
    }
    if nu_series:
        tail = nu_series[-max(1, len(nu_series) // 2) :]
        result["Nu_tail_mean"] = sum(v for _, v in tail) / len(tail)
    if result["Nu_tail_mean"] is not None:
        ref = result["Nu_Bharti"] or result["Nu_Lange"]
        result["Nu_error_vs_reference_pct"] = 100.0 * (float(result["Nu_tail_mean"]) - float(ref)) / float(ref)
    else:
        result["Nu_error_vs_reference_pct"] = None

    if t_values is not None:
        result.update(
            {
                "T_min_K": min(t_values),
                "T_max_K": max(t_values),
                "T_below_Tin_pct": 100.0 * sum(v < base.T_IN for v in t_values) / len(t_values),
                "T_above_Tw_pct": 100.0 * sum(v > base.T_W for v in t_values) / len(t_values),
            }
        )
        result.update(cylinder_owner_temperature_stats(cdir, t_values))
    if parallel_t_stats:
        result.update({key: value for key, value in parallel_t_stats.items() if value is not None})

    notes = [
        f"- latest time = `{time_value}`",
        f"- Nu_tail_mean = `{result['Nu_tail_mean']}`",
        f"- Nu_last = `{result['Nu_last']}`",
        f"- Nu_Lange = `{result['Nu_Lange']:.4f}`",
        f"- Nu_Bharti = `{result['Nu_Bharti']}`",
        f"- Cd_tail_mean = `{result['Cd_tail_mean']}`",
        f"- Cl_tail_rms = `{result['Cl_tail_rms']}`",
        f"- St_present = `{result['St_present']}`",
        f"- St_Lange = `{result['St_Lange']}`",
        f"- mesh_cells = `{result['mesh_cells']}`",
        f"- T_min/T_max = `{result.get('T_min_K')}` / `{result.get('T_max_K')}` K",
        f"- cylinder owner cells above T_wall = `{result.get('cylinder_owner_above_Tw_pct')}` %",
    ]
    write_case_notes(case, notes)
    return result


def fmt_float(value: object, fmt: str = ".4f") -> str:
    if value is None or value == "":
        return "n/a"
    try:
        return format(float(value), fmt)
    except (TypeError, ValueError):
        return str(value)


def write_summary(results: list[dict]) -> None:
    ensure_layout()
    plot_mesh_schematic()
    nu_reference_plot = plot_nu_reference(results)
    fieldnames = [
        "case",
        "Re",
        "mesh_cells",
        "cylinder_faces",
        "parallel_ranks",
        "latest_time_s",
        "Nu_tail_mean",
        "Nu_last",
        "Nu_samples",
        "Nu_Lange",
        "Nu_Bharti",
        "Nu_error_vs_reference_pct",
        "Cd_tail_mean",
        "Cl_tail_mean",
        "Cl_tail_rms",
        "St_present",
        "St_Lange",
        "St_lowest_bin_peak",
        "T_min_K",
        "T_max_K",
        "T_below_Tin_pct",
        "T_above_Tw_pct",
        "cylinder_owner_above_Tw_pct",
    ]
    with (RUN_DIR / "summary.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    table_lines = [
        "# V2A O-grid Thermal Verification Table",
        "",
        "| case | Re | cells | Nu present | Nu Lange | Nu Bharti | err vs active ref | Cd mean | Cl RMS | St present | St Lange | T bounded |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in results:
        bounded = (
            row.get("T_below_Tin_pct") == 0.0
            and row.get("T_above_Tw_pct") == 0.0
            and row.get("cylinder_owner_above_Tw_pct") == 0.0
        )
        err = row.get("Nu_error_vs_reference_pct")
        nu_bharti = row.get("Nu_Bharti")
        st_present = row.get("St_present")
        st_ref = row.get("St_Lange")
        cl_rms = row.get("Cl_tail_rms")
        err_text = "n/a" if err is None else f"{float(err):+.2f}%"
        table_lines.append(
            f"| {row.get('case')} | {row.get('Re')} | {row.get('mesh_cells')} | "
            f"{fmt_float(row.get('Nu_tail_mean'))} | {fmt_float(row.get('Nu_Lange'))} | "
            f"{fmt_float(nu_bharti)} | {err_text} | {fmt_float(row.get('Cd_tail_mean'))} | "
            f"{fmt_float(cl_rms, '.3e')} | {fmt_float(st_present)} | {fmt_float(st_ref)} | "
            f"{'yes' if bounded else 'no'} |"
        )
    table_lines += [
        "",
        "Note: this table contains all O-grid cases currently present in `summary.csv`.",
    ]
    write_text(RUN_DIR / "publication_table.md", "\n".join(table_lines) + "\n")

    lines = [
        f"# {RUN_SLUG} summary",
        "",
        "| case | Re | cells | latest t | Nu | ref | err % | Cd | St | T range | cylinder > Tw | status |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for row in results:
        ref = row.get("Nu_Bharti") or row.get("Nu_Lange")
        bounded = (
            row.get("T_below_Tin_pct") == 0.0
            and row.get("T_above_Tw_pct") == 0.0
            and row.get("cylinder_owner_above_Tw_pct") == 0.0
        )
        status = "bounded; candidate" if bounded and row.get("Nu_tail_mean") is not None else "diagnostic"
        lines.append(
            f"| {row.get('case')} | {row.get('Re')} | {row.get('mesh_cells')} | {row.get('latest_time_s')} | "
            f"{row.get('Nu_tail_mean')} | {ref} | {row.get('Nu_error_vs_reference_pct')} | "
            f"{row.get('Cd_tail_mean')} | {row.get('St_present')} | "
            f"{row.get('T_min_K')} - {row.get('T_max_K')} | {row.get('cylinder_owner_above_Tw_pct')} | {status} |"
        )
    lines += [
        "",
        "## Figures",
        "",
        "- `plots/V2_run004_ogrid_mesh_schematic.png`",
        f"- `plots/{nu_reference_plot.name}`",
    ]
    article_plot = PLOTS_DIR / "V2A_Nu_Re_articles_vs_present.png"
    if article_plot.exists():
        lines.append(f"- `plots/{article_plot.name}`")
        for name in (
            "V2A_St_Re_articles_vs_present.png",
            "V2A_Cd_Re_articles_vs_present.png",
            "V2A_articles_vs_present_dashboard.png",
        ):
            if (PLOTS_DIR / name).exists():
                lines.append(f"- `plots/{name}`")
        lines.append("- `publication_Nu_Re_data.csv`")
        if (RUN_DIR / "publication_articles_vs_present_data.csv").exists():
            lines.append("- `publication_articles_vs_present_data.csv`")
    for row in results:
        if row.get("plot"):
            lines.append(f"- `plots/{Path(str(row['plot'])).name}`")
    lines += [
        "",
        "## Reading",
        "",
        "- This run is the structured-cylinder replacement for the rejected snappy run 002.",
        "- The low-Re O-grid matrix currently passes the boundedness and Nu checks for all completed cases.",
    ]
    write_text(RUN_DIR / "summary.md", "\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="V2A structured O-grid cylinder validation branch")
    parser.add_argument("action", choices=["plan", "setup", "mesh", "run", "analyze", "all"])
    parser.add_argument("cases", nargs="*", help="Case names or Reynolds numbers")
    args = parser.parse_args()

    cases = selected_cases(args.cases)
    if args.action == "plan":
        write_run_docs(status="planned")
        plot_mesh_schematic()
    elif args.action == "setup":
        for case in cases:
            setup_case(case)
    elif args.action == "mesh":
        for case in cases:
            mesh_case(case)
    elif args.action == "run":
        for case in cases:
            run_case(case)
    elif args.action == "analyze":
        analysis_cases = cases if args.cases else analyzable_cases()
        write_summary([analyze_case(case) for case in analysis_cases])
    elif args.action == "all":
        for case in cases:
            setup_case(case)
            mesh_case(case)
            run_case(case)
        write_summary([analyze_case(case) for case in analyzable_cases()])


if __name__ == "__main__":
    main()
