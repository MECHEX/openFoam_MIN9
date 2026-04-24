"""
V2ChannelCheck.py
-----------------
Diagnostic heated-channel benchmark for V2 thermal verification recovery.

Purpose:
  - decouple thermal-solver / boundedness problems from the cylinder snappy mesh
  - use a pure blockMesh channel before returning to an O-grid cylinder
  - compare a fully developed plane-channel UWT target Nu ~= 7.541

Usage:
  python VV_cases/V2_thermal/_code/V2ChannelCheck.py plan
  python VV_cases/V2_thermal/_code/V2ChannelCheck.py setup
  python VV_cases/V2_thermal/_code/V2ChannelCheck.py analyze
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import V2AStudy as base


CODE_DIR = Path(__file__).resolve().parent
REPO_CASE = CODE_DIR.parent
RESULTS_DIR = REPO_CASE / "results" / "study_v2a"
RUN_SLUG = "003_data_heated_channel_solver_check"
RUN_DIR = RESULTS_DIR / "runs" / RUN_SLUG
SIM_NAME = "plane_channel_Re100_UWT"
SIM_DIR = RUN_DIR / "simulations" / SIM_NAME
PLOTS_DIR = RUN_DIR / "plots"

WORK_ROOT = Path(r"C:\openfoam-case\VV_cases\V2_channel_check")
CASE_DIR = WORK_ROOT / SIM_NAME

RE = 100
GAP = 0.012
HYDRAULIC_DIAMETER = 2.0 * GAP
LENGTH = 60.0 * HYDRAULIC_DIAMETER
SPAN = 0.010
NX = 360
NY = 60
NZ = 1
DX = LENGTH / NX
DY = GAP / NY
U_BULK = RE * base.NU / HYDRAULIC_DIAMETER
END_TIME = 80.0
WRITE_INTERVAL = 5.0
NU_UWT_FULLY_DEVELOPED = 7.541


def ensure_layout() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_block_mesh() -> str:
    x0 = 0.0
    x1 = LENGTH
    y0 = -0.5 * GAP
    y1 = 0.5 * GAP
    z0 = -0.5 * SPAN
    z1 = 0.5 * SPAN
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

scale 1;

vertices
(
    ({x0:.8g} {y0:.8g} {z0:.8g})
    ({x1:.8g} {y0:.8g} {z0:.8g})
    ({x1:.8g} {y1:.8g} {z0:.8g})
    ({x0:.8g} {y1:.8g} {z0:.8g})
    ({x0:.8g} {y0:.8g} {z1:.8g})
    ({x1:.8g} {y0:.8g} {z1:.8g})
    ({x1:.8g} {y1:.8g} {z1:.8g})
    ({x0:.8g} {y1:.8g} {z1:.8g})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({NX} {NY} {NZ}) simpleGrading (1 1 1)
);

edges ();

boundary
(
    inlet
    {{
        type patch;
        faces ( (0 4 7 3) );
    }}
    outlet
    {{
        type patch;
        faces ( (1 2 6 5) );
    }}
    lowerWall
    {{
        type wall;
        faces ( (0 1 5 4) );
    }}
    upperWall
    {{
        type wall;
        faces ( (3 7 6 2) );
    }}
    front
    {{
        type empty;
        faces ( (0 3 2 1) );
    }}
    back
    {{
        type empty;
        faces ( (4 5 6 7) );
    }}
);

mergePatchPairs ();
"""


def make_control_dict() -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}}

application     buoyantBoussinesqPimpleFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {END_TIME};

deltaT          1e-4;
adjustTimeStep  yes;
maxCo           0.5;

writeControl    runTime;
writeInterval   {WRITE_INTERVAL};
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   8;
runTimeModifiable true;

functions
{{
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


def make_fv_solution() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-8;
        relTol          0.01;
    }
    p_rghFinal
    {
        $p_rgh;
        relTol          0;
        tolerance       1e-9;
    }

    "(U|T)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-8;
        relTol          0.05;
    }
    "(U|T)Final"
    {
        $U;
        relTol          0;
        tolerance       1e-9;
    }
}

PIMPLE
{
    momentumPredictor no;
    nOuterCorrectors        1;
    nCorrectors             2;
    nNonOrthogonalCorrectors 1;
    pRefCell        0;
    pRefValue       0;
}

relaxationFactors
{
    equations
    {
        U       0.9;
        UFinal  1.0;
        T       0.9;
        TFinal  1.0;
    }
}
"""


def make_u() -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({U_BULK:.8g} 0 0);

boundaryField
{{
    inlet
    {{
        type        fixedValue;
        value       uniform ({U_BULK:.8g} 0 0);
    }}
    outlet
    {{
        type        zeroGradient;
    }}
    lowerWall
    {{
        type        noSlip;
    }}
    upperWall
    {{
        type        noSlip;
    }}
    front
    {{
        type        empty;
    }}
    back
    {{
        type        empty;
    }}
}}
"""


def make_t() -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}}

dimensions      [0 0 0 1 0 0 0];
internalField   uniform {base.T_IN:.2f};

boundaryField
{{
    inlet
    {{
        type        fixedValue;
        value       uniform {base.T_IN:.2f};
    }}
    outlet
    {{
        type        inletOutlet;
        inletValue  uniform {base.T_IN:.2f};
        value       uniform {base.T_IN:.2f};
    }}
    lowerWall
    {{
        type        fixedValue;
        value       uniform {base.T_W:.2f};
    }}
    upperWall
    {{
        type        fixedValue;
        value       uniform {base.T_W:.2f};
    }}
    front
    {{
        type        empty;
    }}
    back
    {{
        type        empty;
    }}
}}
"""


def make_p_rgh() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}

dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet     { type fixedFluxPressure; rho rhok; value uniform 0; }
    outlet    { type fixedValue; value uniform 0; }
    lowerWall { type fixedFluxPressure; rho rhok; value uniform 0; }
    upperWall { type fixedFluxPressure; rho rhok; value uniform 0; }
    front     { type empty; }
    back      { type empty; }
}
"""


def make_alphat() -> str:
    return """FoamFile { version 2.0; format ascii; class volScalarField; object alphat; }
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;
boundaryField { ".*" { type calculated; value uniform 0; } }
"""


def make_allrun() -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

source {base.OF_BASHRC}
mkdir -p logs

blockMesh | tee logs/log.blockMesh
buoyantBoussinesqPimpleFoam | tee logs/log.buoyantBoussinesqPimpleFoam
postProcess -func writeCellCentres -latestTime | tee logs/log.writeCellCentres
"""


def write_run_docs(status: str = "planned") -> None:
    ensure_layout()
    run_lines = [
        f"# {RUN_SLUG}",
        "",
        "## Purpose",
        "",
        "Diagnostic recovery run for V2 thermal verification after the cylinder case produced a non-physical temperature field.",
        "",
        "This run deliberately removes the snappy cylinder mesh from the problem:",
        "",
        "- geometry: 2D plane channel from `blockMesh`",
        "- thermal problem: uniform wall temperature on both walls",
        "- solver architecture: `buoyantBoussinesqPimpleFoam` with `g = 0`",
        "- scalar convection check: `div(phi,T) Gauss vanLeer`",
        "- reference target: fully developed plane-channel UWT `Nu ~= 7.541`",
        "- default diagnostic Re is `Re_Dh = 100` to keep a finite outlet wall-bulk temperature difference",
        "",
        "## Critique driving this run",
        "",
        "- The current `Re10_long100s` cylinder result has a non-physical `T` field and must not be used as a validation result.",
        "- The cylinder result mixes at least three issues: scalar boundedness, `Nu` extraction, and snappy wall-normal mesh quality.",
        "- This channel check isolates the solver/scheme/extraction path before investing in a structured O-grid cylinder mesh.",
        "",
        "## Simulation matrix",
        "",
        "| simulation | Re_Dh | target | status |",
        "|---|---:|---:|---|",
        f"| {SIM_NAME} | {RE} | Nu ~= {NU_UWT_FULLY_DEVELOPED:.3f} | {status} |",
        "",
        "## Planned interpretation",
        "",
        "- If `T` stays bounded and local same-station `Nu` approaches the analytic value, the solver/scheme path is likely acceptable and the cylinder problem should move to O-grid meshing.",
        "- If `T` overshoots here too, the scalar transport setup is still wrong independently of the cylinder mesh.",
        "- A preliminary `Re_Dh = 10` channel sanity run stayed bounded but saturated the outlet to `T_wall`, making outlet-local Nu ill-conditioned; the Nu diagnostic therefore uses `Re_Dh = 100`.",
    ]
    write_text(RUN_DIR / "run.md", "\n".join(run_lines) + "\n")

    sim_lines = [
        f"# {SIM_NAME}",
        "",
        "## Setup",
        "",
        f"- Re_Dh: `{RE}`",
        f"- channel gap: `{GAP:.6f} m`",
        f"- hydraulic diameter: `{HYDRAULIC_DIAMETER:.6f} m`",
        f"- length: `{LENGTH:.6f} m` (`{LENGTH / HYDRAULIC_DIAMETER:.1f} D_h`)",
        f"- mesh: `{NX} x {NY} x {NZ}`",
        f"- bulk inlet velocity: `{U_BULK:.8g} m/s`",
        f"- inlet temperature: `{base.T_IN:.2f} K`",
        f"- wall temperature: `{base.T_W:.2f} K`",
        "- thermal BC: uniform wall temperature on both channel walls",
        "- benchmark: fully developed plane-channel UWT `Nu ~= 7.541`",
        "",
        "## Notes",
        "",
        "- This is a diagnostic solver/scheme benchmark, not a cylinder validation case.",
        "- Nu must be computed locally from the same x-station wall gradient and bulk temperature; outlet-only Nu is unsafe if the outlet saturates.",
    ]
    write_text(SIM_DIR / "notes.md", "\n".join(sim_lines) + "\n")

    with (RUN_DIR / "summary.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["simulation", "Re_Dh", "Nu_target", "status"])
        writer.writeheader()
        writer.writerow(
            {
                "simulation": SIM_NAME,
                "Re_Dh": RE,
                "Nu_target": NU_UWT_FULLY_DEVELOPED,
                "status": status,
            }
        )
    write_text(
        RUN_DIR / "summary.md",
        "\n".join(
            [
                f"# {RUN_SLUG} summary",
                "",
                "| simulation | Re_Dh | Nu target | status |",
                "|---|---:|---:|---|",
                f"| {SIM_NAME} | {RE} | {NU_UWT_FULLY_DEVELOPED:.3f} | {status} |",
            ]
        )
        + "\n",
    )


def setup_case() -> None:
    ensure_layout()
    write_run_docs(status="case generated")
    if CASE_DIR.exists():
        print(f"Case already exists, not overwriting: {CASE_DIR}")
        return

    for subdir in ("0", "constant", "system"):
        (CASE_DIR / subdir).mkdir(parents=True, exist_ok=True)

    write_text(CASE_DIR / "system" / "blockMeshDict", make_block_mesh())
    write_text(CASE_DIR / "system" / "controlDict", make_control_dict())
    write_text(CASE_DIR / "system" / "fvSchemes", make_fv_schemes())
    write_text(CASE_DIR / "system" / "fvSolution", make_fv_solution())

    write_text(CASE_DIR / "constant" / "transportProperties", base.make_transportProperties())
    write_text(CASE_DIR / "constant" / "g", base.make_g())
    write_text(CASE_DIR / "constant" / "turbulenceProperties", base.make_turbulenceProperties())

    write_text(CASE_DIR / "0" / "U", make_u())
    write_text(CASE_DIR / "0" / "T", make_t())
    write_text(CASE_DIR / "0" / "p_rgh", make_p_rgh())
    write_text(CASE_DIR / "0" / "alphat", make_alphat())
    write_text(CASE_DIR / "Allrun", make_allrun())
    write_text(
        CASE_DIR / "caseMeta.json",
        json.dumps(
            {
                "study": "V2 thermal recovery",
                "run_slug": RUN_SLUG,
                "simulation": SIM_NAME,
                "case_type": "plane_channel_UWT",
                "solver": "buoyantBoussinesqPimpleFoam",
                "Re_Dh": RE,
                "Dh": HYDRAULIC_DIAMETER,
                "U_bulk": U_BULK,
                "T_in": base.T_IN,
                "T_wall": base.T_W,
                "Nu_target_UWT_fully_developed": NU_UWT_FULLY_DEVELOPED,
            },
            indent=2,
        )
        + "\n",
    )
    print(f"Generated channel check case: {CASE_DIR}")


def latest_time_dir(case_dir: Path) -> tuple[float, Path] | None:
    times = base.numeric_time_dirs(case_dir)
    return times[-1] if times else None


def plot_nu_profile(profile_rows: list[dict[str, float]], selected: dict[str, float]) -> tuple[Path, Path]:
    ensure_layout()
    xs = [row["x_over_Dh"] for row in profile_rows]
    nus = [row["Nu_local"] if math.isfinite(row["Nu_local"]) else None for row in profile_rows]
    margins = [max(row["Tw_minus_Tbulk_K"], 1.0e-12) for row in profile_rows]

    finite_nu = sorted(row["Nu_local"] for row in profile_rows if math.isfinite(row["Nu_local"]))
    if finite_nu:
        p95 = finite_nu[int(0.95 * (len(finite_nu) - 1))]
        y_upper = min(max(12.0, 1.15 * p95), 80.0)
    else:
        y_upper = 12.0

    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.0), dpi=180, sharex=True)

    axes[0].plot(xs, nus, color="#164e63", lw=1.4, label="local channel Nu")
    axes[0].axhline(NU_UWT_FULLY_DEVELOPED, color="#b45309", lw=1.2, ls="--", label="UWT target 7.541")
    axes[0].plot(
        selected["x_over_Dh"],
        selected["Nu_local"],
        marker="o",
        color="#dc2626",
        ms=5.5,
        label="selected comparison station",
    )
    axes[0].set_ylabel(r"$Nu_{D_h}$")
    axes[0].set_ylim(0.0, y_upper)
    axes[0].grid(True, color="#d6d3d1", lw=0.6, alpha=0.8)
    axes[0].legend(frameon=False, fontsize=8, loc="upper right")

    axes[1].semilogy(xs, margins, color="#475569", lw=1.3)
    axes[1].axvline(selected["x_over_Dh"], color="#dc2626", lw=1.0, ls=":")
    axes[1].axhline(0.05, color="#78716c", lw=1.0, ls="--")
    axes[1].set_xlabel(r"$x/D_h$")
    axes[1].set_ylabel(r"$T_w - T_b$ [K]")
    axes[1].grid(True, which="both", color="#d6d3d1", lw=0.6, alpha=0.8)

    fig.suptitle("Heated channel diagnostic: local Nu and thermal margin", fontsize=11)
    fig.tight_layout()
    out_png = PLOTS_DIR / "V2_channel_Re100_Nu_profile.png"
    out_svg = PLOTS_DIR / "V2_channel_Re100_Nu_profile.svg"
    fig.savefig(out_png, dpi=180, bbox_inches="tight")
    fig.savefig(out_svg, bbox_inches="tight")
    plt.close(fig)
    return out_png, out_svg


def analyze_case() -> None:
    if not CASE_DIR.exists():
        raise FileNotFoundError(f"Case does not exist: {CASE_DIR}")
    latest = latest_time_dir(CASE_DIR)
    if latest is None:
        raise FileNotFoundError(f"No numeric time directories found in {CASE_DIR}")

    time_value, time_dir = latest
    t_values = base.parse_scalar_internal_field(time_dir / "T")
    u_values = base.parse_vector_internal_field(time_dir / "U")
    c_path = time_dir / "C"
    if not c_path.exists():
        raise FileNotFoundError(
            f"Cell-centre field missing: {c_path}. Run `postProcess -func writeCellCentres -latestTime` first."
        )
    c_values = base.parse_vector_internal_field(c_path)

    boundary = base.parse_boundary(CASE_DIR / "constant" / "polyMesh" / "boundary")
    owner = base.parse_owner(CASE_DIR / "constant" / "polyMesh" / "owner")

    wall_owners: list[tuple[str, int]] = []
    for patch_name in ("lowerWall", "upperWall"):
        patch = boundary[patch_name]
        start_face = int(patch["startFace"])
        n_faces = int(patch["nFaces"])
        wall_owners.extend((patch_name, idx) for idx in owner[start_face : start_face + n_faces])

    def x_bin(x_value: float) -> int:
        return max(0, min(NX - 1, int(x_value / DX)))

    # Orthogonal blockMesh: wall distance from owner-cell centre to wall is dy/2.
    wall_grad_sum = [0.0 for _ in range(NX)]
    wall_grad_count = [0 for _ in range(NX)]
    for _patch_name, cell_idx in wall_owners:
        i = x_bin(c_values[cell_idx][0])
        wall_grad_sum[i] += (base.T_W - t_values[cell_idx]) / (0.5 * DY)
        wall_grad_count[i] += 1

    # Local Nu must use the wall gradient and bulk temperature from the same x-station.
    bulk_t_sum = [0.0 for _ in range(NX)]
    bulk_u_sum = [0.0 for _ in range(NX)]
    for center, t_val, u_val in zip(c_values, t_values, u_values):
        if u_val[0] > 0.0:
            i = x_bin(center[0])
            bulk_t_sum[i] += u_val[0] * t_val
            bulk_u_sum[i] += u_val[0]

    profile_rows = []
    for i in range(NX):
        if wall_grad_count[i] == 0 or bulk_u_sum[i] <= 0.0:
            continue
        t_bulk = bulk_t_sum[i] / bulk_u_sum[i]
        denom = base.T_W - t_bulk
        wall_sngrad = wall_grad_sum[i] / wall_grad_count[i]
        nu_local = HYDRAULIC_DIAMETER * wall_sngrad / denom if abs(denom) > 1.0e-12 else float("nan")
        profile_rows.append(
            {
                "x_m": (i + 0.5) * DX,
                "x_over_Dh": (i + 0.5) * DX / HYDRAULIC_DIAMETER,
                "T_bulk_K": t_bulk,
                "Tw_minus_Tbulk_K": denom,
                "wall_sngrad_K_per_m": wall_sngrad,
                "wall_face_samples": wall_grad_count[i],
                "Nu_local": nu_local,
            }
        )

    if not profile_rows:
        raise ValueError("Could not compute any local channel Nu profile rows")

    stable_rows = [
        row
        for row in profile_rows
        if row["x_over_Dh"] >= 10.0 and row["Tw_minus_Tbulk_K"] >= 0.05
    ]
    if not stable_rows:
        stable_rows = [
            row
            for row in profile_rows
            if row["x_over_Dh"] >= 5.0 and row["Tw_minus_Tbulk_K"] >= 0.01
        ]
    if not stable_rows:
        stable_rows = [row for row in profile_rows if row["Tw_minus_Tbulk_K"] > 1.0e-9]
    selected = stable_rows[-1]
    outlet = profile_rows[-1]
    err_pct = 100.0 * (selected["Nu_local"] - NU_UWT_FULLY_DEVELOPED) / NU_UWT_FULLY_DEVELOPED

    with (RUN_DIR / "Nu_profile.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(profile_rows[0].keys()))
        writer.writeheader()
        writer.writerows(profile_rows)
    plot_png, plot_svg = plot_nu_profile(profile_rows, selected)

    result = {
        "simulation": SIM_NAME,
        "latest_time_s": time_value,
        "T_min_K": min(t_values),
        "T_max_K": max(t_values),
        "T_below_inlet_pct": 100.0 * sum(v < base.T_IN for v in t_values) / len(t_values),
        "T_above_wall_pct": 100.0 * sum(v > base.T_W for v in t_values) / len(t_values),
        "selected_x_over_Dh": selected["x_over_Dh"],
        "selected_T_bulk_K": selected["T_bulk_K"],
        "selected_Tw_minus_Tbulk_K": selected["Tw_minus_Tbulk_K"],
        "selected_Nu_local": selected["Nu_local"],
        "outlet_T_bulk_K": outlet["T_bulk_K"],
        "outlet_Tw_minus_Tbulk_K": outlet["Tw_minus_Tbulk_K"],
        "outlet_Nu_local": outlet["Nu_local"],
        "Nu_target_UWT_fully_developed": NU_UWT_FULLY_DEVELOPED,
        "selected_Nu_error_pct": err_pct,
        "nu_profile_png": str(plot_png),
        "nu_profile_svg": str(plot_svg),
    }

    with (RUN_DIR / "summary.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(result.keys()))
        writer.writeheader()
        writer.writerow(result)

    lines = [
        f"# {RUN_SLUG} summary",
        "",
        "| quantity | value |",
        "|---|---:|",
        f"| latest time | {time_value:.6g} s |",
        f"| T min | {result['T_min_K']:.4f} K |",
        f"| T max | {result['T_max_K']:.4f} K |",
        f"| cells below inlet T | {result['T_below_inlet_pct']:.2f}% |",
        f"| cells above wall T | {result['T_above_wall_pct']:.2f}% |",
        f"| selected x/Dh | {selected['x_over_Dh']:.3f} |",
        f"| selected bulk T | {selected['T_bulk_K']:.4f} K |",
        f"| selected Tw - Tbulk | {selected['Tw_minus_Tbulk_K']:.4g} K |",
        f"| selected local Nu | {selected['Nu_local']:.4f} |",
        f"| outlet bulk T | {outlet['T_bulk_K']:.4f} K |",
        f"| outlet Tw - Tbulk | {outlet['Tw_minus_Tbulk_K']:.4g} K |",
        f"| outlet-local Nu | {outlet['Nu_local']:.4f} |",
        f"| target Nu | {NU_UWT_FULLY_DEVELOPED:.4f} |",
        f"| Nu error | {err_pct:+.2f}% |",
        f"| Nu profile plot | `plots/{plot_png.name}` |",
        "",
        f"![Local Nu profile](plots/{plot_png.name})",
        "",
        "## Reading",
        "",
        "- The selected Nu uses the furthest x-station that is both downstream and still numerically well conditioned.",
        "- The outlet Nu is reported separately because a saturated outlet makes Tw - Tbulk too small for a stable denominator.",
        "- The first pass/fail check is boundedness of T in the known physical interval.",
    ]
    write_text(RUN_DIR / "summary.md", "\n".join(lines) + "\n")
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="V2 diagnostic heated-channel benchmark")
    parser.add_argument("action", choices=["plan", "setup", "analyze"], help="Action to perform")
    args = parser.parse_args()

    if args.action == "plan":
        write_run_docs(status="planned")
        print(f"Wrote plan docs: {RUN_DIR}")
    elif args.action == "setup":
        setup_case()
    elif args.action == "analyze":
        analyze_case()


if __name__ == "__main__":
    main()
