from __future__ import annotations

import csv
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


CODE_DIR = Path(__file__).resolve().parent
REPO_CASE = CODE_DIR.parent
COMMON_DIR = REPO_CASE.parent / "_common"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

import production_like_cylinder as plc
import V2AStudy as base


RESULTS_DIR = REPO_CASE / "results" / "study_v2a"
RUN_SLUG = "006_data_v2_production_like_short"
RUN_DIR = RESULTS_DIR / "runs" / RUN_SLUG
SIMS_DIR = RUN_DIR / "simulations"
PLOTS_DIR = RUN_DIR / "plots"
OLD_SUMMARY = RESULTS_DIR / "runs" / "004_data_v2a_ogrid_cylinder_validation" / "summary.csv"

WORK_ROOT = Path("/home/hexmachina/of_runs/V2_production_like_short")
OF_BASHRC = "/opt/openfoam13/etc/bashrc"
NPROCS = 8

CASES = [
    {"name": "Re10_prodLike", "old_key": "Re10_ogrid", "Re": 10, "endTime": 18.0, "writeInterval": 0.50, "forceWriteInterval": 0.05},
    {"name": "Re20_prodLike", "old_key": "Re20_ogrid", "Re": 20, "endTime": 18.0, "writeInterval": 0.50, "forceWriteInterval": 0.05},
    {"name": "Re40_prodLike", "old_key": "Re40_ogrid", "Re": 40, "endTime": 18.0, "writeInterval": 0.50, "forceWriteInterval": 0.05},
    {"name": "Re60_prodLike", "old_key": "Re60_ogrid", "Re": 60, "endTime": 12.0, "writeInterval": 0.20, "forceWriteInterval": 0.02},
    {"name": "Re100_prodLike", "old_key": "Re100_ogrid", "Re": 100, "endTime": 10.0, "writeInterval": 0.10, "forceWriteInterval": 0.01},
]
CASE_MAP = {case["name"]: case for case in CASES}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", newline="\n")


def selected_cases(names: list[str]) -> list[dict]:
    if not names:
        return CASES
    return [CASE_MAP[name] for name in names]


def case_runtime_dir(case: dict) -> Path:
    return WORK_ROOT / case["name"]


def case_archive_dir(case: dict) -> Path:
    return SIMS_DIR / case["name"]


def u_file(case: dict) -> str:
    u_inf = case["Re"] * plc.NU / plc.D
    return f"""FoamFile
{{
    format      ascii;
    class       volVectorField;
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({u_inf:.9f} 0 0);

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform ({u_inf:.9f} 0 0);
    }}
    outlet
    {{
        type            pressureInletOutletVelocity;
        value           uniform ({u_inf:.9f} 0 0);
    }}
    bottom
    {{
        type            symmetryPlane;
    }}
    top
    {{
        type            symmetryPlane;
    }}
    cylinder
    {{
        type            noSlip;
    }}
    front
    {{
        type            symmetryPlane;
    }}
    back
    {{
        type            symmetryPlane;
    }}
}}
"""


def t_file() -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       volScalarField;
    object      T;
}}

dimensions      [0 0 0 1 0 0 0];
internalField   uniform {base.T_IN:.2f};

boundaryField
{{
    inlet {{ type fixedValue; value uniform {base.T_IN:.2f}; }}
    outlet {{ type inletOutlet; inletValue uniform {base.T_IN:.2f}; value uniform {base.T_IN:.2f}; }}
    bottom {{ type symmetryPlane; }}
    top {{ type symmetryPlane; }}
    cylinder {{ type fixedValue; value uniform {base.T_W:.2f}; }}
    front {{ type symmetryPlane; }}
    back {{ type symmetryPlane; }}
}}
"""


def control_dict(case: dict) -> str:
    u_inf = case["Re"] * plc.NU / plc.D
    aref = plc.D * plc.SPAN
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
        rhoInf          {plc.RHO:.4f};
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         {u_inf:.8g};
        lRef            {plc.D};
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
}}
"""


def setup_case(case: dict, overwrite: bool = False) -> None:
    cdir = case_runtime_dir(case)
    if cdir.exists() and overwrite:
        shutil.rmtree(cdir)
    ensure_dir(cdir / "0")
    ensure_dir(cdir / "constant")
    ensure_dir(cdir / "system")
    write_text(cdir / "system" / "blockMeshDict", plc.block_mesh_dict("symmetryPlane", "symmetryPlane"))
    write_text(cdir / "system" / "snappyHexMeshDict", plc.snappy_hex_mesh_dict())
    write_text(cdir / "system" / "controlDict", control_dict(case))
    write_text(cdir / "system" / "fvSchemes", plc.fv_schemes())
    write_text(cdir / "system" / "fvSolution", plc.fv_solution())
    write_text(cdir / "system" / "decomposeParDict", plc.decompose_par_dict(NPROCS))
    write_text(cdir / "constant" / "g", plc.g_file())
    write_text(cdir / "constant" / "physicalProperties", plc.physical_properties(cv=base.CP_FLUID))
    write_text(cdir / "constant" / "momentumTransport", plc.momentum_transport())
    write_text(cdir / "0" / "U", u_file(case))
    write_text(cdir / "0" / "T", t_file())
    write_text(cdir / "0" / "p", plc.p_file("symmetryPlane", "symmetryPlane"))
    write_text(cdir / "0" / "p_rgh", plc.p_rgh_file("symmetryPlane", "symmetryPlane"))
    write_text(cdir / "0" / "alphat", plc.alphat_file("symmetryPlane", "symmetryPlane"))
    write_text(cdir / "Allrun", plc.allrun_file(OF_BASHRC, NPROCS))
    subprocess.run(["bash", "-lc", f"chmod +x '{cdir / 'Allrun'}'"], check=True)
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
        return {"latest_time_s": None, "T_min_K": None, "T_max_K": None}
    latest = times[-1]
    t_min = math.inf
    t_max = -math.inf
    for pdir in procs:
        matches = [time_dir for time_value, time_dir in base.numeric_time_dirs(pdir) if abs(time_value - latest) < 1e-8 and (time_dir / "T").exists()]
        if not matches:
            continue
        values = base.parse_scalar_internal_field(matches[0] / "T")
        if values:
            t_min = min(t_min, min(values))
            t_max = max(t_max, max(values))
    return {
        "latest_time_s": latest,
        "T_min_K": None if t_min is math.inf else t_min,
        "T_max_K": None if t_max is -math.inf else t_max,
    }


def parallel_nu_time_series(cdir: Path) -> list[tuple[float, float]]:
    procs = processor_dirs(cdir)
    if not procs:
        return []
    faces_by_proc = {}
    centers_by_proc = {}
    for pdir in procs:
        faces_data, cell_centers = base.cylinder_sngrad_setup(pdir)
        faces_by_proc[pdir.name] = faces_data
        centers_by_proc[pdir.name] = cell_centers
    series: list[tuple[float, float]] = []
    for time_value in processor_time_values(cdir):
        area_sum = 0.0
        sngrad_sum = 0.0
        for pdir in procs:
            matches = [time_dir for candidate, time_dir in base.numeric_time_dirs(pdir) if abs(candidate - time_value) < 1e-8 and (time_dir / "T").exists()]
            if not matches:
                continue
            t_values = base.parse_scalar_internal_field(matches[0] / "T")
            for area, normal, f_center, cell_idx in faces_by_proc[pdir.name]:
                if area <= 0.0:
                    continue
                c_p = centers_by_proc[pdir.name][cell_idx]
                delta_perp = (
                    (f_center[0] - c_p[0]) * normal[0]
                    + (f_center[1] - c_p[1]) * normal[1]
                    + (f_center[2] - c_p[2]) * normal[2]
                )
                if abs(delta_perp) < 1e-15:
                    continue
                t_p = t_values[cell_idx]
                sngrad = (base.T_W - t_p) / delta_perp
                area_sum += area
                sngrad_sum += area * sngrad
        if area_sum > 0.0:
            series.append((time_value, plc.D * (sngrad_sum / area_sum) / base.DT))
    return series


def force_coeff_rows(cdir: Path) -> list[tuple[float, float, float]]:
    rows: dict[float, tuple[float, float, float]] = {}
    coeff_root = cdir / "postProcessing" / "forceCoeffs"
    if not coeff_root.exists():
        return []
    for coeff_file in list(coeff_root.glob("*/coefficient.dat")) + list(coeff_root.glob("*/forceCoeffs.dat")):
        for line in coeff_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            rows[float(parts[0])] = (float(parts[0]), float(parts[2]), float(parts[3]))
    return [rows[key] for key in sorted(rows)]


def force_stats(case: dict, cdir: Path) -> dict[str, float | None]:
    rows = force_coeff_rows(cdir)
    result = {"Cd_tail_mean": None, "Cl_tail_rms": None, "St_present": None}
    if not rows:
        return result
    tail = rows[-max(20, len(rows) // 2):]
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
        u_inf = case["Re"] * plc.NU / plc.D
        result["St_present"] = freq_hz * plc.D / u_inf
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
    ax.plot([item[0] for item in series], [item[1] for item in series], color="#0f766e", lw=1.4, label="production-like")
    ax.axhline(base.nu_lange(case["Re"]), color="#b45309", lw=1.2, ls="--", label=f"Lange {base.nu_lange(case['Re']):.4f}")
    if case["Re"] in base.BHARTI_NU:
        ax.axhline(base.BHARTI_NU[case["Re"]], color="#1d4ed8", lw=1.2, ls=":", label=f"Bharti {base.BHARTI_NU[case['Re']]:.4f}")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("mean cylinder Nu")
    ax.set_title(f"{case['name']}: Nu(t) on production-like mesh")
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
        old_row = old.get(case["old_key"], {})
        nu_old = float(old_row["Nu_tail_mean"]) if old_row.get("Nu_tail_mean") not in {"", "None", None} else None
        nu_new = sum(v for _, v in nu_series[-max(5, len(nu_series) // 5):]) / max(1, len(nu_series[-max(5, len(nu_series) // 5):])) if nu_series else None
        st_old = float(old_row["St_present"]) if old_row.get("St_present") not in {"", "None", None} else None
        st_new = force["St_present"]
        row = {
            "case": case["name"],
            "old_key": case["old_key"],
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
        "| case | old key | Re | Nu old | Nu new | Nu ref | dNu new vs old [%] | dNu new vs ref [%] | Cd old | Cd new | St old | St new |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['old_key']} | {row['Re']} | {row['Nu_old']} | {row['Nu_new']} | {row['Nu_ref']} | "
            f"{row['Nu_new_vs_old_pct']} | {row['Nu_new_vs_ref_pct']} | {row['Cd_old']} | {row['Cd_new']} | {row['St_old']} | {row['St_new']} |"
        )
    write_text(RUN_DIR / "summary.md", "\n".join(lines) + "\n")


def plot_comparison(rows: list[dict[str, object]]) -> None:
    with_old = [row for row in rows if row["Nu_old"] is not None and row["Nu_new"] is not None]
    if with_old:
        fig, ax = plt.subplots(figsize=(5.4, 5.4), dpi=180)
        xs = [float(row["Nu_old"]) for row in with_old]
        ys = [float(row["Nu_new"]) for row in with_old]
        ax.scatter(xs, ys, s=44, color="#0f766e")
        lo = min(xs + ys) * 0.95
        hi = max(xs + ys) * 1.05
        ax.plot([lo, hi], [lo, hi], "--", color="#9ca3af", lw=1.0)
        for row in with_old:
            ax.text(float(row["Nu_old"]), float(row["Nu_new"]), f"Re{row['Re']}", fontsize=7)
        ax.set_xlabel("Nu old O-grid")
        ax.set_ylabel("Nu new production-like")
        ax.set_title("V2 production-like bridge")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "V2_prodlike_old_vs_new_nu.png", dpi=180, bbox_inches="tight")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=180)
    ordered = sorted(rows, key=lambda row: float(row["Re"]))
    ax.plot([float(row["Re"]) for row in ordered], [float(row["Nu_ref"]) for row in ordered], "o--", color="#1d4ed8", label="reference")
    ax.plot([float(row["Re"]) for row in ordered if row["Nu_new"] is not None], [float(row["Nu_new"]) for row in ordered if row["Nu_new"] is not None], "s-", color="#0f766e", label="production-like")
    ax.set_xlabel("Re")
    ax.set_ylabel("Nu")
    ax.set_title("V2 production-like vs reference")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "V2_prodlike_nu_reference_overlay.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_run_doc() -> None:
    ensure_dir(RUN_DIR)
    ensure_dir(SIMS_DIR)
    ensure_dir(PLOTS_DIR)
    lines = [
        f"# {RUN_SLUG}",
        "",
        "Production-like V2 rerun on the compact V4b-style domain and mesh family.",
        "",
        f"- runtime root: `{WORK_ROOT}`",
        f"- solver chain: `foamRun -solver fluid`",
        f"- geometry family: compact V4b-like domain, heated cylinder only",
        "",
        "| case | old key | Re | endTime [s] | writeInterval [s] |",
        "|---|---|---:|---:|---:|",
    ]
    for case in CASES:
        lines.append(f"| {case['name']} | {case['old_key']} | {case['Re']} | {case['endTime']} | {case['writeInterval']} |")
    write_text(RUN_DIR / "run.md", "\n".join(lines) + "\n")


def setup(names: list[str], overwrite: bool = False) -> None:
    write_run_doc()
    ensure_dir(WORK_ROOT)
    for case in selected_cases(names):
        setup_case(case, overwrite=overwrite)


def run(names: list[str]) -> None:
    for case in selected_cases(names):
        run_case(case)


def analyze(names: list[str]) -> None:
    rows = analyze_cases(selected_cases(names))
    if not rows:
        raise SystemExit("No analyzable V2 production-like cases found.")
    write_summary(rows)
    plot_comparison(rows)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 V2ProductionLikeStudy.py setup|run|analyze|all [case names...]")
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
