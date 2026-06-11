from __future__ import annotations

import csv
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


CODE_DIR = Path(__file__).resolve().parent
REPO_CASE = CODE_DIR.parent
COMMON_DIR = REPO_CASE.parent / "_common"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

import production_like_cylinder as plc


RESULTS_ROOT = REPO_CASE / "results" / "study_v1"
RUN_SLUG = "005_data_v1_production_like_short"
RUN_DIR = RESULTS_ROOT / "runs" / RUN_SLUG
SIMS_DIR = RUN_DIR / "simulations"
PLOTS_DIR = RUN_DIR / "plots"
OLD_SUMMARY = RESULTS_ROOT / "runs" / "002_data_sahin_owens_poiseuille_verification" / "summary.csv"

WORK_ROOT = Path("/home/hexmachina/of_runs/V1_production_like_short")
OF_BASHRC = "/opt/openfoam13/etc/bashrc"
NPROCS = 6
T_REF = 293.15

SAHIN_OWENS = {
    0.10: {"Re_crit": 50.81, "St_crit": 0.1210},
    0.20: {"Re_crit": 69.43, "St_crit": 0.1566},
    0.30: {"Re_crit": 94.56, "St_crit": 0.2090},
    0.50: {"Re_crit": 124.09, "St_crit": 0.3393},
    0.70: {"Re_crit": 110.29, "St_crit": 0.4752},
    0.80: {"Re_crit": 110.24, "St_crit": 0.5363},
    0.84: {"Re_crit": 113.69, "St_crit": 0.5568},
}


@dataclass(frozen=True)
class StudyCase:
    name: str
    old_key: str
    beta: float
    reynolds: float
    end_time_s: float
    purpose: str

    @property
    def u_max(self) -> float:
        return self.reynolds * plc.NU / plc.D


CASES = [
    StudyCase("b0375_prod_Re105", "b0375_medium_Re105", 0.375, 105.0, 4.0, "near projected onset, production-like domain"),
    StudyCase("b0375_prod_Re120", "b0375_medium_Re120", 0.375, 120.0, 5.0, "above onset, production-like domain"),
    StudyCase("b0375_prod_Re135", "b0375_medium_Re120", 0.375, 135.0, 5.0, "extra-above onset, production-like domain"),
]
CASE_MAP = {case.name: case for case in CASES}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", newline="\n")


def selected_cases(names: list[str]) -> list[StudyCase]:
    if not names:
        return CASES
    return [CASE_MAP[name] for name in names]


def case_runtime_dir(case: StudyCase) -> Path:
    return WORK_ROOT / case.name


def case_archive_dir(case: StudyCase) -> Path:
    return SIMS_DIR / case.name


def so_ref(beta: float) -> dict[str, float | bool]:
    exact = SAHIN_OWENS.get(beta)
    if exact:
        return {"Re_crit": exact["Re_crit"], "St_crit": exact["St_crit"], "interpolated": False}
    betas = sorted(SAHIN_OWENS)
    lo = max(b for b in betas if b <= beta)
    hi = min(b for b in betas if b >= beta)
    t = (beta - lo) / (hi - lo)
    return {
        "Re_crit": SAHIN_OWENS[lo]["Re_crit"] * (1.0 - t) + SAHIN_OWENS[hi]["Re_crit"] * t,
        "St_crit": SAHIN_OWENS[lo]["St_crit"] * (1.0 - t) + SAHIN_OWENS[hi]["St_crit"] * t,
        "interpolated": True,
    }


def u_file(case: StudyCase) -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       volVectorField;
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({case.u_max:.9f} {0.001*case.u_max:.9f} 0);

boundaryField
{{
    inlet
    {{
        type            codedFixedValue;
        name            poiseuilleInlet;
        value           uniform (0 0 0);
        code
        #{{
            vectorField v(this->patch().size(), vector::zero);
            const vectorField& cf = this->patch().Cf();
            forAll(v, i)
            {{
                const scalar y = cf[i].y();
                v[i].x() = {case.u_max:.9f}*(1.0 - sqr(y/{plc.Y_HALF:.9f}));
            }}
            operator==(v);
        #}};
    }}
    outlet
    {{
        type            pressureInletOutletVelocity;
        value           uniform ({case.u_max:.9f} 0 0);
    }}
    bottom
    {{
        type            noSlip;
    }}
    top
    {{
        type            noSlip;
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
internalField   uniform {T_REF:.2f};

boundaryField
{{
    inlet {{ type fixedValue; value uniform {T_REF:.2f}; }}
    outlet {{ type inletOutlet; inletValue uniform {T_REF:.2f}; value uniform {T_REF:.2f}; }}
    bottom {{ type zeroGradient; }}
    top {{ type zeroGradient; }}
    cylinder {{ type zeroGradient; }}
    front {{ type symmetryPlane; }}
    back {{ type symmetryPlane; }}
}}
"""


def control_dict(case: StudyCase) -> str:
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
endTime         {case.end_time_s:.3f};
deltaT          0.001;
adjustTimeStep  yes;
maxCo           0.8;
writeControl    adjustableRunTime;
writeInterval   0.10;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
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
        writeControl    adjustableRunTime;
        writeInterval   0.01;
        log             yes;
        patches         (cylinder);
        rho             rhoInf;
        rhoInf          {plc.RHO:.6f};
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         {case.u_max:.9f};
        lRef            {plc.D:.6f};
        Aref            {plc.D*plc.SPAN:.9f};
    }}

    residuals
    {{
        type            residuals;
        libs            ("libutilityFunctionObjects.so");
        fields          (U p_rgh e);
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   0.05;
    }}
}}
"""


def setup_case(case: StudyCase, overwrite: bool = False) -> None:
    cdir = case_runtime_dir(case)
    if cdir.exists() and overwrite:
        shutil.rmtree(cdir)
    ensure_dir(cdir / "0")
    ensure_dir(cdir / "constant")
    ensure_dir(cdir / "system")
    write_text(cdir / "system" / "blockMeshDict", plc.block_mesh_dict("wall", "wall"))
    write_text(cdir / "system" / "snappyHexMeshDict", plc.snappy_hex_mesh_dict())
    write_text(cdir / "system" / "controlDict", control_dict(case))
    write_text(cdir / "system" / "fvSchemes", plc.fv_schemes())
    write_text(cdir / "system" / "fvSolution", plc.fv_solution())
    write_text(cdir / "system" / "decomposeParDict", plc.decompose_par_dict(NPROCS))
    write_text(cdir / "constant" / "g", plc.g_file())
    write_text(cdir / "constant" / "physicalProperties", plc.physical_properties())
    write_text(cdir / "constant" / "momentumTransport", plc.momentum_transport())
    write_text(cdir / "0" / "U", u_file(case))
    write_text(cdir / "0" / "T", t_file())
    write_text(cdir / "0" / "p", plc.p_file("wall", "wall"))
    write_text(cdir / "0" / "p_rgh", plc.p_rgh_file("wall", "wall"))
    write_text(cdir / "0" / "alphat", plc.alphat_file("wall", "wall"))
    write_text(cdir / "Allrun", plc.allrun_file(OF_BASHRC, NPROCS))
    subprocess.run(["bash", "-lc", f"chmod +x '{cdir / 'Allrun'}'"], check=True)
    archive_setup(case)


def archive_setup(case: StudyCase) -> None:
    target = case_archive_dir(case) / "openfoam_setup"
    if target.exists():
        shutil.rmtree(target)
    ensure_dir(target.parent)
    shutil.copytree(case_runtime_dir(case), target)


def run_case(case: StudyCase) -> None:
    subprocess.run(["bash", "Allrun"], cwd=case_runtime_dir(case), check=True)


def parse_check_mesh(path: Path) -> dict[str, float | int | str | None]:
    result: dict[str, float | int | str | None] = {
        "status": "missing",
        "cells": None,
        "points": None,
        "faces": None,
        "max_non_ortho": None,
    }
    if not path.exists():
        return result
    text = path.read_text(encoding="utf-8", errors="ignore")
    result["status"] = "ok" if "Mesh OK" in text else "warn"
    import re

    for key, pattern in {
        "points": r"points:\s+(\d+)",
        "faces": r"faces:\s+(\d+)",
        "cells": r"cells:\s+(\d+)",
        "max_non_ortho": r"Mesh non-orthogonality Max:\s+([0-9.eE+-]+)",
    }.items():
        match = re.search(pattern, text)
        if match:
            result[key] = int(match.group(1)) if key in {"points", "faces", "cells"} else float(match.group(1))
    return result


def coeff_paths(case: StudyCase) -> list[Path]:
    root = case_runtime_dir(case) / "postProcessing" / "forceCoeffs"
    if not root.exists():
        return []
    pairs: list[tuple[float, Path]] = []
    for child in root.iterdir():
        if not child.is_dir():
            continue
        for filename in ("coefficient.dat", "forceCoeffs.dat"):
            coeff = child / filename
            if coeff.exists():
                try:
                    start = float(child.name)
                except ValueError:
                    start = math.inf
                pairs.append((start, coeff))
                break
    return [path for _, path in sorted(pairs, key=lambda item: item[0])]


def load_coeffs(paths: list[Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    merged: dict[float, tuple[float, float]] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 4:
                merged[float(parts[0])] = (float(parts[2]), float(parts[3]))
    ordered = sorted(merged.items())
    return (
        np.asarray([item[0] for item in ordered], dtype=float),
        np.asarray([item[1][0] for item in ordered], dtype=float),
        np.asarray([item[1][1] for item in ordered], dtype=float),
    )


def compute_metrics(case: StudyCase, time: np.ndarray, cd: np.ndarray, cl: np.ndarray) -> dict[str, object]:
    if time.size < 32:
        return {"status": "insufficient-data", "regime": "undetermined", "Cd_mean": None, "Cl_rms": None, "frequency_hz": None, "St": None}
    start = max(0.4 * float(time.max()), float(time.max()) - 2.5)
    mask = time >= start
    t_sel = time[mask]
    cd_sel = cd[mask]
    cl_sel = cl[mask]
    cd_mean = float(np.mean(cd_sel))
    cl_centered = cl_sel - np.mean(cl_sel)
    cl_rms = float(np.sqrt(np.mean(cl_centered**2)))
    if t_sel.size < 32 or cl_rms < 1e-3:
        return {"status": "ok", "regime": "steady-or-weakly-unsteady", "Cd_mean": cd_mean, "Cl_rms": cl_rms, "frequency_hz": None, "St": None}
    dt = float(np.mean(np.diff(t_sel)))
    nfft = 1
    while nfft < cl_centered.size * 8:
        nfft *= 2
    freqs = np.fft.rfftfreq(nfft, d=dt)
    amps = np.abs(np.fft.rfft(cl_centered * np.hanning(cl_centered.size), n=nfft))
    valid = (freqs > 0.0) & (freqs < 30.0)
    freqs = freqs[valid]
    amps = amps[valid]
    idx = int(np.argmax(amps))
    freq = float(freqs[idx])
    return {
        "status": "ok",
        "regime": "periodic",
        "Cd_mean": cd_mean,
        "Cl_rms": cl_rms,
        "frequency_hz": freq,
        "St": float(freq * plc.D / case.u_max),
    }


def plot_cl(case: StudyCase, time: np.ndarray, cl: np.ndarray) -> None:
    out = case_archive_dir(case) / "plots"
    ensure_dir(out)
    fig, ax = plt.subplots(figsize=(9, 4), dpi=160)
    ax.plot(time, cl, lw=0.9, color="#0b5ed7")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Cl [-]")
    ax.set_title(f"{case.name}: Cl(t) on production-like mesh")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "Cl_vs_time.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def load_old_summary() -> dict[str, dict[str, str]]:
    with OLD_SUMMARY.open(encoding="utf-8") as handle:
        return {row["case"]: row for row in csv.DictReader(handle)}


def analyze_cases(cases: list[StudyCase]) -> list[dict[str, object]]:
    old = load_old_summary()
    rows: list[dict[str, object]] = []
    for case in cases:
        mesh_info = parse_check_mesh(case_runtime_dir(case) / "logs" / "checkMesh.log")
        paths = coeff_paths(case)
        if not paths:
            continue
        time, cd, cl = load_coeffs(paths)
        metrics = compute_metrics(case, time, cd, cl)
        plot_cl(case, time, cl)
        ref = so_ref(case.beta)
        old_row = old.get(case.old_key, {})
        old_st = float(old_row["St_sim"]) if old_row.get("St_sim") not in {"", "None", None} else None
        old_cd = float(old_row["Cd_mean"]) if old_row.get("Cd_mean") not in {"", "None", None} else None
        delta_vs_old = None
        if metrics["St"] is not None and old_st not in (None, 0.0):
            delta_vs_old = 100.0 * (float(metrics["St"]) - old_st) / old_st
        row = {
            "case": case.name,
            "old_key": case.old_key,
            "beta": case.beta,
            "Re": case.reynolds,
            "cells": mesh_info["cells"],
            "regime_new": metrics["regime"],
            "Cd_old": old_cd,
            "Cd_new": metrics["Cd_mean"],
            "Cl_rms_old": float(old_row["Cl_rms"]) if old_row.get("Cl_rms") not in {"", "None", None} else None,
            "Cl_rms_new": metrics["Cl_rms"],
            "St_old": old_st,
            "St_new": metrics["St"],
            "St_ref": ref["St_crit"],
            "dSt_new_vs_old_pct": delta_vs_old,
            "status": metrics["status"],
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
        "| case | old key | Re | Cd old | Cd new | St old | St new | dSt new vs old [%] |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['old_key']} | {row['Re']} | {row['Cd_old']} | {row['Cd_new']} | "
            f"{row['St_old']} | {row['St_new']} | {row['dSt_new_vs_old_pct']} |"
        )
    write_text(RUN_DIR / "summary.md", "\n".join(lines) + "\n")


def plot_comparison(rows: list[dict[str, object]]) -> None:
    periodic = [row for row in rows if row["St_old"] is not None and row["St_new"] is not None]
    if periodic:
        fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=180)
        xs = [float(row["St_old"]) for row in periodic]
        ys = [float(row["St_new"]) for row in periodic]
        ax.scatter(xs, ys, s=42, color="#0f766e")
        lo = min(xs + ys) * 0.98
        hi = max(xs + ys) * 1.02
        ax.plot([lo, hi], [lo, hi], "--", color="#9ca3af", lw=1.0)
        for row in periodic:
            ax.text(float(row["St_old"]), float(row["St_new"]), row["case"].split("_")[-1], fontsize=7)
        ax.set_xlabel("St old benchmark")
        ax.set_ylabel("St new production-like")
        ax.set_title("V1 production-like bridge")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "V1_prodlike_old_vs_new_st.png", dpi=180, bbox_inches="tight")
        plt.close(fig)

    with_old_cd = [row for row in rows if row["Cd_old"] is not None and row["Cd_new"] is not None]
    if with_old_cd:
        labels = [row["case"] for row in with_old_cd]
        x = np.arange(len(labels))
        width = 0.35
        fig, ax = plt.subplots(figsize=(8.0, 4.5), dpi=180)
        ax.bar(x - width / 2, [float(row["Cd_old"]) for row in with_old_cd], width, label="old")
        ax.bar(x + width / 2, [float(row["Cd_new"]) for row in with_old_cd], width, label="prod-like")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=15, ha="right")
        ax.set_ylabel("Cd")
        ax.set_title("V1 drag: benchmark vs production-like")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "V1_prodlike_old_vs_new_cd.png", dpi=180, bbox_inches="tight")
        plt.close(fig)


def write_run_doc() -> None:
    ensure_dir(RUN_DIR)
    ensure_dir(SIMS_DIR)
    ensure_dir(PLOTS_DIR)
    lines = [
        f"# {RUN_SLUG}",
        "",
        "Production-like V1 rerun on the compact V4b-style domain and mesh family.",
        "",
        f"- runtime root: `{WORK_ROOT}`",
        f"- solver chain: `foamRun -solver fluid`",
        f"- geometry family: compact V4b-like domain, beta = {plc.D / (2.0 * plc.Y_HALF):.3f}",
        "",
        "| case | old key | beta | Re | endTime [s] | role |",
        "|---|---|---:|---:|---:|---|",
    ]
    for case in CASES:
        lines.append(f"| {case.name} | {case.old_key} | {case.beta:.3f} | {case.reynolds:.0f} | {case.end_time_s:.1f} | {case.purpose} |")
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
        raise SystemExit("No analyzable V1 production-like cases found.")
    write_summary(rows)
    plot_comparison(rows)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 V1ProductionLikeStudy.py setup|run|analyze|all [case names...]")
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
