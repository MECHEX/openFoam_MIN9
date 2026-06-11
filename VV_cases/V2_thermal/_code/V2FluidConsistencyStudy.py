from __future__ import annotations

import csv
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import V2AStudy as base


CODE_DIR = Path(__file__).resolve().parent
REPO_CASE = CODE_DIR.parent
RESULTS_DIR = REPO_CASE / "results" / "study_v2a"
RUN_SLUG = "005_data_of13_fluid_consistency_short"
RUN_DIR = RESULTS_DIR / "runs" / RUN_SLUG
SIMS_DIR = RUN_DIR / "simulations"
PLOTS_DIR = RUN_DIR / "plots"

SOURCE_RUN_DIR = RESULTS_DIR / "runs" / "004_data_v2a_ogrid_cylinder_validation" / "simulations"
OLD_SUMMARY = RESULTS_DIR / "runs" / "004_data_v2a_ogrid_cylinder_validation" / "summary.csv"

WORK_ROOT = Path("/home/hexmachina/of_runs/V2_run_of13_fluid_short")
OF_BASHRC = "/opt/openfoam13/etc/bashrc"
NPROCS = 8

CASES = [
    {"name": "Re10_ogrid", "Re": 10, "endTime": 60.0, "writeInterval": 1.0, "forceWriteInterval": 0.10},
    {"name": "Re20_ogrid", "Re": 20, "endTime": 60.0, "writeInterval": 1.0, "forceWriteInterval": 0.10},
    {"name": "Re40_ogrid", "Re": 40, "endTime": 60.0, "writeInterval": 1.0, "forceWriteInterval": 0.10},
    {"name": "Re60_ogrid", "Re": 60, "endTime": 40.0, "writeInterval": 0.20, "forceWriteInterval": 0.02},
    {"name": "Re100_ogrid", "Re": 100, "endTime": 20.0, "writeInterval": 0.10, "forceWriteInterval": 0.01},
]
CASE_MAP = {case["name"]: case for case in CASES}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def selected_cases(names: list[str]) -> list[dict]:
    if not names:
        return CASES
    return [CASE_MAP[name] for name in names]


def case_runtime_dir(case: dict) -> Path:
    return WORK_ROOT / case["name"]


def case_archive_dir(case: dict) -> Path:
    return SIMS_DIR / case["name"]


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", newline="\n")


def decompose_par_dict() -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}}

numberOfSubdomains {NPROCS};
method scotch;
"""


def physical_properties() -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    location    "constant";
    object      physicalProperties;
}}

thermoType
{{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          eConst;
    equationOfState Boussinesq;
    specie          specie;
    energy          sensibleInternalEnergy;
}}

mixture
{{
    specie
    {{
        molWeight       28.9;
    }}
    equationOfState
    {{
        rho0            {base.RHO0:.6f};
        T0              {base.T_IN:.2f};
        beta            {base.BETA_T:.9e};
    }}
    thermodynamics
    {{
        Cv              {base.CP_FLUID:.6f};
        hf              0;
    }}
    transport
    {{
        mu              {base.MU:.9e};
        Pr              {base.PR:.6f};
    }}
}}
"""


def momentum_transport() -> str:
    return """FoamFile
{
    format      ascii;
    class       dictionary;
    location    "constant";
    object      momentumTransport;
}

simulationType  laminar;
"""


def p_file() -> str:
    return """FoamFile
{
    format      ascii;
    class       volScalarField;
    object      p;
}

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet { type calculated; value $internalField; }
    outlet { type calculated; value $internalField; }
    top { type calculated; value $internalField; }
    bottom { type calculated; value $internalField; }
    cylinder { type calculated; value $internalField; }
    front { type symmetryPlane; }
    back { type symmetryPlane; }
}
"""


def p_rgh_file() -> str:
    return """FoamFile
{
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet { type fixedFluxPressure; value uniform 0; }
    outlet { type fixedValue; value uniform 0; }
    top { type fixedFluxPressure; value uniform 0; }
    bottom { type fixedFluxPressure; value uniform 0; }
    cylinder { type fixedFluxPressure; value uniform 0; }
    front { type symmetryPlane; }
    back { type symmetryPlane; }
}
"""


def alphat_file() -> str:
    return """FoamFile
{
    format      ascii;
    class       volScalarField;
    object      alphat;
}

dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet { type calculated; value uniform 0; }
    outlet { type calculated; value uniform 0; }
    top { type calculated; value uniform 0; }
    bottom { type calculated; value uniform 0; }
    cylinder { type calculated; value uniform 0; }
    front { type symmetryPlane; }
    back { type symmetryPlane; }
}
"""


def fv_schemes() -> str:
    return """FoamFile
{
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes
{
    default         backward;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default                                 none;
    div(phi,U)                              Gauss linearUpwind grad(U);
    div(phi,e)                              Gauss upwind;
    div(phi,(p|rho))                        Gauss linear;
    div(phi,p)                              Gauss linear;
    div(phi,rho)                            Gauss linear;
    div(phi,K)                              Gauss linear;
    div(phid,p)                             Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U)))))     Gauss linear;
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
"""


def fv_solution() -> str:
    return """FoamFile
{
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

solvers
{
    "rho.*"
    {
        solver          diagonal;
    }

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
    }

    "(U|e)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-7;
        relTol          0.05;
    }

    "(U|e)Final"
    {
        $U;
        relTol          0;
    }
}

PIMPLE
{
    momentumPredictor          yes;
    nOuterCorrectors           2;
    nCorrectors                2;
    nNonOrthogonalCorrectors   1;
    pRefCell                   0;
    pRefValue                  0;
}
"""


def control_dict(case: dict) -> str:
    u_inf = case["Re"] * base.NU / base.D
    aref = base.D * base.L_Z
    return f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    object      controlDict;
}}

solver          fluid;
startFrom       startTime;
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
        libs            ("libforces.so");
        executeControl  timeStep;
        writeControl    runTime;
        writeInterval   {case["forceWriteInterval"]};
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
        type            residuals;
        libs            ("libutilityFunctionObjects.so");
        fields          (U p_rgh e);
        executeControl  timeStep;
        writeControl    runTime;
        writeInterval   {case["forceWriteInterval"]};
    }}

    wallHeatFlux
    {{
        type            wallHeatFlux;
        libs            ("libfieldFunctionObjects.so");
        executeControl  timeStep;
        writeControl    runTime;
        writeInterval   {case["forceWriteInterval"]};
    }}
}}
"""


def allrun_file() -> str:
    return f"""#!/usr/bin/env bash
export ZSH_NAME="${{ZSH_NAME-}}"
source {OF_BASHRC}
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
blockMesh | tee logs/log.blockMesh
checkMesh | tee logs/log.checkMesh
postProcess -func writeCellCentres -time 0 | tee logs/log.writeCellCentres
if [ -f system/setExprFieldsDict ] && command -v setExprFields >/dev/null 2>&1; then
    setExprFields | tee logs/log.setExprFields
fi
decomposePar -force | tee logs/log.decomposePar
mpirun --use-hwthread-cpus -np {NPROCS} foamRun -solver fluid -parallel | tee logs/log.foamRun
"""


def prepare_case(case: dict, overwrite: bool = False) -> None:
    src = SOURCE_RUN_DIR / case["name"] / "openfoam_setup"
    if not src.exists():
        raise FileNotFoundError(f"Missing source setup for {case['name']}: {src}")
    dst = case_runtime_dir(case)
    if dst.exists() and overwrite:
        shutil.rmtree(dst)
    if not dst.exists():
        shutil.copytree(src, dst)

    for rel in ("system/blockMeshDict", "0/U", "0/T", "0/p_rgh"):
        path = dst / rel
        if path.exists():
            text = path.read_text(encoding="utf-8")
            text = re.sub(r"type\s+empty\s*;", "type symmetryPlane;", text)
            write_text(path, text)

    write_text(dst / "constant" / "physicalProperties", physical_properties())
    write_text(dst / "constant" / "momentumTransport", momentum_transport())
    if (dst / "constant" / "transportProperties").exists():
        (dst / "constant" / "transportProperties").unlink()
    if (dst / "constant" / "turbulenceProperties").exists():
        (dst / "constant" / "turbulenceProperties").unlink()
    write_text(dst / "0" / "alphat", alphat_file())
    write_text(dst / "0" / "p", p_file())
    write_text(dst / "0" / "p_rgh", p_rgh_file())
    write_text(dst / "system" / "controlDict", control_dict(case))
    write_text(dst / "system" / "fvSchemes", fv_schemes())
    write_text(dst / "system" / "fvSolution", fv_solution())
    write_text(dst / "system" / "decomposeParDict", decompose_par_dict())
    write_text(dst / "Allrun", allrun_file())
    subprocess.run(["bash", "-lc", f"chmod +x '{dst / 'Allrun'}'"], check=True)
    archive_setup(case)


def archive_setup(case: dict) -> None:
    target = case_archive_dir(case) / "openfoam_setup"
    if target.exists():
        shutil.rmtree(target)
    ensure_dir(target.parent)
    shutil.copytree(case_runtime_dir(case), target)


def run_case(case: dict) -> None:
    subprocess.run(["bash", "Allrun"], cwd=case_runtime_dir(case), check=True)


def processor_dirs(cdir: Path) -> list[Path]:
    return sorted([child for child in cdir.iterdir() if child.is_dir() and child.name.startswith("processor")], key=lambda path: int(path.name.replace("processor", "")))


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
        matches = [time_dir for time_value, time_dir in base.numeric_time_dirs(pdir) if abs(time_value - latest) < 1e-8 and (time_dir / "T").exists()]
        if not matches:
            continue
        t_path = matches[-1] / "T"
        values = base.parse_scalar_internal_field(t_path)
        t_min = min(t_min, min(values))
        t_max = max(t_max, max(values))
        n_total += len(values)
        n_below += sum(value < base.T_IN for value in values)
        n_above += sum(value > base.T_W for value in values)
        boundary = base.parse_boundary(pdir / "constant" / "polyMesh" / "boundary")
        owner = base.parse_owner(pdir / "constant" / "polyMesh" / "owner")
        cyl = boundary.get("cylinder")
        if cyl:
            start = int(cyl["startFace"])
            n_faces = int(cyl["nFaces"])
            owner_vals.extend(values[idx] for idx in owner[start : start + n_faces])
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
        except Exception:
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
            matches = [time_dir for candidate, time_dir in base.numeric_time_dirs(pdir) if abs(candidate - time_value) < 1e-8 and (time_dir / "T").exists()]
            if not matches:
                continue
            t_cell = base.parse_scalar_internal_field(matches[-1] / "T")
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


def force_coeff_rows(cdir: Path) -> list[tuple[float, float, float]]:
    rows: dict[float, tuple[float, float, float]] = {}
    coeff_root = cdir / "postProcessing" / "forceCoeffs"
    if not coeff_root.exists():
        return []
    for coeff_file in coeff_root.glob("*/coefficient.dat"):
        for line in coeff_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            rows[float(parts[0])] = (float(parts[0]), float(parts[1]), float(parts[4]))
    return [rows[key] for key in sorted(rows)]


def force_stats(case: dict, cdir: Path) -> dict[str, float | bool | None]:
    rows = force_coeff_rows(cdir)
    result = {
        "Cd_tail_mean": None,
        "Cl_tail_rms": None,
        "St_present": None,
    }
    if not rows:
        return result
    tail = rows[-max(20, len(rows) // 2) :]
    times = [row[0] for row in tail]
    cds = [row[1] for row in tail]
    cls = [row[2] for row in tail]
    cl_mean = sum(cls) / len(cls)
    centered = [value - cl_mean for value in cls]
    cl_rms = math.sqrt(sum(value * value for value in centered) / len(centered))
    result["Cd_tail_mean"] = sum(cds) / len(cds)
    result["Cl_tail_rms"] = cl_rms
    if case["Re"] < 45.9 or cl_rms < 1e-8 or len(times) < 20:
        return result
    dt = sum(b - a for a, b in zip(times[:-1], times[1:]) if b > a) / max(1, len(times) - 1)
    spectrum = base._fft(centered)
    best_idx = None
    best_amp = -1.0
    for idx in range(1, len(spectrum) // 2):
        amp = abs(spectrum[idx])
        if amp > best_amp:
            best_amp = amp
            best_idx = idx
    if best_idx is not None and dt > 0.0:
        freq_hz = best_idx / (len(spectrum) * dt)
        u_inf = case["Re"] * base.NU / base.D
        result["St_present"] = freq_hz * base.D / u_inf
    return result


def mesh_cell_count(cdir: Path) -> int | None:
    c_path = cdir / "0" / "C"
    if not c_path.exists():
        return None
    try:
        return len(base.parse_vector_internal_field(c_path))
    except Exception:
        return None


def load_old_summary() -> dict[str, dict[str, str]]:
    with OLD_SUMMARY.open(encoding="utf-8") as handle:
        return {row["case"]: row for row in csv.DictReader(handle)}


def plot_nu_series(case: dict, series: list[tuple[float, float]]) -> None:
    if not series:
        return
    out = case_archive_dir(case) / "plots"
    ensure_dir(out)
    fig, ax = plt.subplots(figsize=(8.0, 4.5), dpi=180)
    ax.plot([item[0] for item in series], [item[1] for item in series], color="#0f766e", lw=1.4, label="OF13 fluid")
    ax.axhline(base.nu_lange(case["Re"]), color="#b45309", lw=1.2, ls="--", label=f"Lange {base.nu_lange(case['Re']):.4f}")
    if case["Re"] in base.BHARTI_NU:
        ax.axhline(base.BHARTI_NU[case["Re"]], color="#1d4ed8", lw=1.2, ls=":", label=f"Bharti {base.BHARTI_NU[case['Re']]:.4f}")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("mean cylinder Nu")
    ax.set_title(f"{case['name']}: Nu(t) on OF13 fluid")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "Nu_vs_time.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def analyze_cases(cases: list[dict]) -> list[dict[str, object]]:
    old = load_old_summary()
    rows: list[dict[str, object]] = []
    for case in cases:
        cdir = case_runtime_dir(case)
        nu_series = parallel_nu_time_series(cdir)
        plot_nu_series(case, nu_series)
        force = force_stats(case, cdir)
        tstats = latest_parallel_t_stats(cdir)
        old_row = old.get(case["name"], {})
        nu_old = float(old_row["Nu_tail_mean"]) if old_row.get("Nu_tail_mean") not in {"", "None", None} else None
        nu_new = sum(v for _, v in nu_series[-max(5, len(nu_series) // 5) :]) / max(1, len(nu_series[-max(5, len(nu_series) // 5) :])) if nu_series else None
        st_old = float(old_row["St_present"]) if old_row.get("St_present") not in {"", "None", None} else None
        st_new = force["St_present"]
        row = {
            "case": case["name"],
            "Re": case["Re"],
            "cells": mesh_cell_count(cdir),
            "latest_time_s": tstats["latest_time_s"],
            "Nu_old": nu_old,
            "Nu_new": nu_new,
            "Nu_ref": base.BHARTI_NU.get(case["Re"], base.nu_lange(case["Re"])),
            "Nu_new_vs_old_pct": (100.0 * (float(nu_new) - nu_old) / nu_old) if nu_new is not None and nu_old not in (None, 0.0) else None,
            "Nu_new_vs_ref_pct": (100.0 * (float(nu_new) - float(base.BHARTI_NU.get(case['Re'], base.nu_lange(case['Re'])))) / float(base.BHARTI_NU.get(case['Re'], base.nu_lange(case['Re'])))) if nu_new is not None else None,
            "Cd_old": float(old_row["Cd_tail_mean"]) if old_row.get("Cd_tail_mean") not in {"", "None", None} else None,
            "Cd_new": force["Cd_tail_mean"],
            "St_old": st_old,
            "St_new": st_new,
            "T_min_K": tstats["T_min_K"],
            "T_max_K": tstats["T_max_K"],
            "cylinder_owner_above_Tw_pct": tstats["cylinder_owner_above_Tw_pct"],
        }
        rows.append(row)
        write_text(case_archive_dir(case) / "summary.json", json.dumps(row, indent=2) + "\n")
    return rows


def write_summary(rows: list[dict[str, object]]) -> None:
    ensure_dir(RUN_DIR)
    ensure_dir(PLOTS_DIR)
    with (RUN_DIR / "summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        f"# {RUN_SLUG}",
        "",
        "| case | Re | Nu old | Nu new | Nu ref | dNu new vs old [%] | dNu new vs ref [%] | Cd old | Cd new | St old | St new |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['Re']} | {row['Nu_old']} | {row['Nu_new']} | {row['Nu_ref']} | "
            f"{row['Nu_new_vs_old_pct']} | {row['Nu_new_vs_ref_pct']} | {row['Cd_old']} | {row['Cd_new']} | {row['St_old']} | {row['St_new']} |"
        )
    write_text(RUN_DIR / "summary.md", "\n".join(lines) + "\n")


def plot_comparison(rows: list[dict[str, object]]) -> None:
    valid_nu = [row for row in rows if row["Nu_old"] is not None and row["Nu_new"] is not None]
    if valid_nu:
        fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=180)
        xs = [float(row["Nu_old"]) for row in valid_nu]
        ys = [float(row["Nu_new"]) for row in valid_nu]
        ax.scatter(xs, ys, s=46, color="#0f766e")
        lo = min(xs + ys) * 0.98
        hi = max(xs + ys) * 1.02
        ax.plot([lo, hi], [lo, hi], "--", color="#9ca3af", lw=1.0)
        for row in valid_nu:
            ax.text(float(row["Nu_old"]), float(row["Nu_new"]), str(row["Re"]), fontsize=8)
        ax.set_xlabel("Nu old")
        ax.set_ylabel("Nu new (OF13 fluid)")
        ax.set_title("V2 consistency: old vs new Nu")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "V2_of13_old_vs_new_nu.png", dpi=180, bbox_inches="tight")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.4, 4.8), dpi=180)
    re_vals = [row["Re"] for row in rows]
    ax.plot(re_vals, [row["Nu_old"] for row in rows], "o--", color="#64748b", lw=1.0, label="old run004")
    ax.plot(re_vals, [row["Nu_new"] for row in rows], "s-", color="#0f766e", lw=1.2, label="new OF13 fluid")
    ax.plot(re_vals, [base.BHARTI_NU.get(row["Re"], base.nu_lange(row["Re"])) for row in rows], "x:", color="#b45309", lw=1.0, label="reference")
    ax.set_xlabel("Re")
    ax.set_ylabel("mean cylinder Nu")
    ax.set_title("V2 consistency: Nu(Re) old vs new vs reference")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "V2_of13_nu_reference_overlay.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    valid_st = [row for row in rows if row["St_old"] is not None and row["St_new"] is not None]
    if valid_st:
        fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=180)
        xs = [float(row["St_old"]) for row in valid_st]
        ys = [float(row["St_new"]) for row in valid_st]
        ax.scatter(xs, ys, s=46, color="#1d4ed8")
        lo = min(xs + ys) * 0.98
        hi = max(xs + ys) * 1.02
        ax.plot([lo, hi], [lo, hi], "--", color="#9ca3af", lw=1.0)
        for row in valid_st:
            ax.text(float(row["St_old"]), float(row["St_new"]), str(row["Re"]), fontsize=8)
        ax.set_xlabel("St old")
        ax.set_ylabel("St new (OF13 fluid)")
        ax.set_title("V2 consistency: old vs new St")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "V2_of13_old_vs_new_st.png", dpi=180, bbox_inches="tight")
        plt.close(fig)


def write_run_doc() -> None:
    ensure_dir(RUN_DIR)
    ensure_dir(SIMS_DIR)
    ensure_dir(PLOTS_DIR)
    lines = [
        f"# {RUN_SLUG}",
        "",
        "Short solver-consistency rerun of V2 O-grid validation cases on the OF13 `foamRun -solver fluid` chain used by V4b.",
        "",
        f"- runtime root: `{WORK_ROOT}`",
        f"- source setups: `{SOURCE_RUN_DIR}`",
        f"- solver chain: `foamRun -solver fluid`",
        f"- thermophysical model: `heRhoThermo + eConst + Boussinesq + sensibleInternalEnergy`",
        "",
        "## Case matrix",
        "",
        "| case | Re | endTime [s] | role |",
        "|---|---:|---:|---|",
    ]
    for case in CASES:
        lines.append(f"| {case['name']} | {case['Re']} | {case['endTime']:.1f} | OF13 fluid consistency check |")
    write_text(RUN_DIR / "run.md", "\n".join(lines) + "\n")


def setup(names: list[str], overwrite: bool = False) -> None:
    write_run_doc()
    ensure_dir(WORK_ROOT)
    for case in selected_cases(names):
        prepare_case(case, overwrite=overwrite)


def run(names: list[str]) -> None:
    for case in selected_cases(names):
        run_case(case)


def analyze(names: list[str]) -> None:
    rows = analyze_cases(selected_cases(names))
    if not rows:
        raise SystemExit("No analyzable V2 OF13 cases found.")
    write_summary(rows)
    plot_comparison(rows)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 V2FluidConsistencyStudy.py setup|run|analyze|all [case names...]")
    cmd = sys.argv[1]
    names = sys.argv[2:]
    if cmd == "setup":
        setup(names, overwrite=True)
    elif cmd == "run":
        run(names)
    elif cmd == "analyze":
        analyze(names)
    elif cmd == "all":
        setup(names, overwrite=True)
        run(names)
        analyze(names)
    else:
        raise SystemExit(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
