#!/usr/bin/env python3
"""
Plan and summarize the run008 Q/lambda2 vortical-structure pass.

This script is intentionally split from the heavy OpenFOAM execution.  It
selects representative full-field checkpoints from the existing Hilbert phase,
writes a small WSL/OpenFOAM runner script, and summarizes any exported VTK files
that the runner produces.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


RUN_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = RUN_DIR.parents[4]
DATA_DIR = RUN_DIR / "data" / "013"
FIG_DIR = RUN_DIR / "figures" / "013"
SCRIPT_DIR = RUN_DIR / "scripts"

CASE_DIR_WSL_STR = "/home/hexmachina/of_runs/V4b_3D_run008"
EXPORT_DIR_WSL_STR = "/home/hexmachina/of_runs/V4b_3D_run008_q_lambda2_013"
CASE_DIR_WSL = Path(CASE_DIR_WSL_STR)
EXPORT_DIR_WSL = Path(EXPORT_DIR_WSL_STR)
CASE_DIR_WIN = Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run008")
EXPORT_DIR_WIN = Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run008_q_lambda2_013")


@dataclass
class PhaseTarget:
    label: str
    phase_deg: float
    reason: str


@dataclass
class SelectedTime:
    label: str
    reason: str
    target_phase_deg: float
    selected_time_s: float
    selected_phase_deg: float
    phase_error_deg: float
    cl_bandpassed: float
    dcl_dt: float


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def circular_error_deg(a: np.ndarray, b_deg: float) -> np.ndarray:
    return ((a - b_deg + 180.0) % 360.0) - 180.0


def read_full_times() -> np.ndarray:
    if not CASE_DIR_WIN.exists():
        raise FileNotFoundError(f"Cannot access case path: {CASE_DIR_WIN}")

    times: list[float] = []
    for child in CASE_DIR_WIN.iterdir():
        if child.is_dir() and re.fullmatch(r"\d+(?:\.\d+)?", child.name):
            t = float(child.name)
            if 2.0 <= t <= 10.0 and abs((t * 100) % 8) < 1e-6:
                # The full-field cadence is 0.08 s.  Other top-level times are
                # reconstructed outlet helper directories.
                if (child / "T").exists():
                    times.append(t)
    if not times:
        raise RuntimeError("No full-field top-level times found")
    return np.array(sorted(set(times)), dtype=float)


def select_times() -> list[SelectedTime]:
    phase = np.load(RUN_DIR / "data" / "002" / "run008_002_hilbert_phase.npz")
    t_phase = phase["time"]
    phase_deg = np.degrees(phase["phase_rad"] % (2.0 * np.pi))
    cl_bp = phase["Cl_bandpassed"]
    dcl_dt = phase["dCl_dt"]

    full_times = read_full_times()
    full_phase = np.interp(full_times, t_phase, phase_deg)
    full_cl = np.interp(full_times, t_phase, cl_bp)
    full_dcl = np.interp(full_times, t_phase, dcl_dt)

    targets = [
        PhaseTarget("cl_zero_down", 11.25, "lift zero-crossing, descending branch"),
        PhaseTarget("cl_zero_up", 78.75, "lift zero-crossing, ascending branch"),
        PhaseTarget("nu_global_max", 123.75, "maximum Nu_tube/Nu_fins/Nu_EB phase"),
        PhaseTarget("cl_min_qtube_max", 236.25, "Cl minimum and Q_tube maximum phase"),
        PhaseTarget("cl_max", 281.25, "Cl maximum phase"),
        PhaseTarget("qfins_qwall_max", 303.75, "Q_fins and Q_wall maximum phase"),
    ]

    selected: list[SelectedTime] = []
    used: set[float] = set()
    for target in targets:
        err = np.abs(circular_error_deg(full_phase, target.phase_deg))
        order = np.argsort(err)
        idx = int(order[0])
        # Avoid duplicate checkpoints for nearby target phases where possible.
        for cand in order:
            if float(full_times[cand]) not in used:
                idx = int(cand)
                break
        used.add(float(full_times[idx]))
        signed_error = float(circular_error_deg(np.array([full_phase[idx]]), target.phase_deg)[0])
        selected.append(
            SelectedTime(
                label=target.label,
                reason=target.reason,
                target_phase_deg=target.phase_deg,
                selected_time_s=float(full_times[idx]),
                selected_phase_deg=float(full_phase[idx]),
                phase_error_deg=signed_error,
                cl_bandpassed=float(full_cl[idx]),
                dcl_dt=float(full_dcl[idx]),
            )
        )
    return selected


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_runner(selected: list[SelectedTime]) -> Path:
    times = ",".join(f"{s.selected_time_s:g}" for s in selected)
    script = SCRIPT_DIR / "run008_q_lambda2_013_wsl.sh"
    script.write_text(
        f"""#!/usr/bin/env bash
source /opt/openfoam13/etc/bashrc
set -euo pipefail

CASE_DIR=\"{CASE_DIR_WSL.as_posix()}\"
EXPORT_DIR=\"{EXPORT_DIR_WSL.as_posix()}\"
TIMES=\"{times}\"
NPROCS=\"${{NPROCS:-20}}\"

mkdir -p \"$EXPORT_DIR/logs\"
cd \"$CASE_DIR\"

echo \"Computing Q, Lambda2, and vorticity for: $TIMES\"
mpirun --oversubscribe -np \"$NPROCS\" foamPostProcess -parallel -func Q -time \"$TIMES\" \\
    > \"$EXPORT_DIR/logs/log.Q\" 2>&1
mpirun --oversubscribe -np \"$NPROCS\" foamPostProcess -parallel -func Lambda2 -time \"$TIMES\" \\
    > \"$EXPORT_DIR/logs/log.Lambda2\" 2>&1
mpirun --oversubscribe -np \"$NPROCS\" foamPostProcess -parallel -func vorticity -time \"$TIMES\" \\
    > \"$EXPORT_DIR/logs/log.vorticity\" 2>&1

echo \"Exporting decomposed VTK files outside Git: $EXPORT_DIR/vtk_processors\"
rm -rf \"$EXPORT_DIR/vtk\" \"$EXPORT_DIR/vtk_processors\" VTK
find processor* -maxdepth 1 -type d -name VTK -exec rm -rf {{}} +
mpirun --oversubscribe -np \"$NPROCS\" foamToVTK -parallel -useTimeName -time \"$TIMES\" -fields '(Q Lambda2 vorticity T U)' \\
    > \"$EXPORT_DIR/logs/log.foamToVTK\" 2>&1
mkdir -p \"$EXPORT_DIR/vtk_processors\"
for proc in processor*; do
    if [[ -d \"$proc/VTK\" ]]; then
        mkdir -p \"$EXPORT_DIR/vtk_processors/$proc\"
        mv \"$proc/VTK\" \"$EXPORT_DIR/vtk_processors/$proc/VTK\"
    fi
done
if [[ -d VTK ]]; then
    mv VTK \"$EXPORT_DIR/vtk_links\"
fi

echo \"Done\"
""",
        encoding="utf-8",
    )
    return script


def plot_selected(selected: list[SelectedTime]) -> None:
    phase = np.load(RUN_DIR / "data" / "002" / "run008_002_hilbert_phase.npz")
    time = phase["time"]
    phase_deg = np.degrees(phase["phase_rad"] % (2.0 * np.pi))
    cl = phase["Cl_bandpassed"]

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), constrained_layout=True)
    axes[0].plot(time, cl, lw=1.0, color="0.2")
    for row in selected:
        axes[0].axvline(row.selected_time_s, color="tab:red", lw=0.9, alpha=0.75)
        axes[0].text(row.selected_time_s, np.nanmax(cl) * 0.92, row.label, rotation=90, fontsize=7)
    axes[0].set_xlabel("t [s]")
    axes[0].set_ylabel("bandpassed Cl")
    axes[0].set_title("Selected full-field checkpoints for Q/lambda2 pass")

    axes[1].scatter(phase_deg, cl, s=4, color="0.65", label="0.005 s samples")
    for row in selected:
        axes[1].scatter(row.selected_phase_deg, row.cl_bandpassed, s=52, label=row.label)
    axes[1].set_xlabel("Hilbert phase of Cl [deg]")
    axes[1].set_ylabel("bandpassed Cl")
    axes[1].set_xlim(0, 360)
    axes[1].legend(ncols=2, fontsize=7)
    fig.savefig(FIG_DIR / "run008_013_selected_q_lambda2_phases.png", dpi=180)


def summarize_vtk(selected: list[SelectedTime]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in selected:
        t = f"{row.selected_time_s:g}"
        candidates = (
            list((EXPORT_DIR_WIN / "vtk_processors").glob(f"**/*_{t}.vtk"))
            if (EXPORT_DIR_WIN / "vtk_processors").exists()
            else []
        )
        total_bytes = sum(p.stat().st_size for p in candidates if p.is_file())
        rows.append(
            {
                "label": row.label,
                "time_s": row.selected_time_s,
                "vtk_file_count": len(candidates),
                "vtk_size_MB": round(total_bytes / (1024 * 1024), 3),
                "export_dir": str(EXPORT_DIR_WIN),
            }
        )
    return rows


def parse_scalar_internal(path: Path) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s+(\d+)\s*\(\s*(.*?)\s*\)\s*;", text, re.S)
    if not m:
        raise ValueError(f"Cannot parse scalar internalField: {path}")
    vals = np.fromstring(m.group(2), sep=" ")
    expected = int(m.group(1))
    if vals.size != expected:
        raise ValueError(f"Parsed {vals.size}, expected {expected}: {path}")
    return vals


def parse_vector_mag_internal(path: Path) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s+(\d+)\s*\(\s*(.*?)\s*\)\s*;", text, re.S)
    if not m:
        raise ValueError(f"Cannot parse vector internalField: {path}")
    raw = m.group(2).replace("(", " ").replace(")", " ")
    vals = np.fromstring(raw, sep=" ")
    expected = int(m.group(1))
    if vals.size != expected * 3:
        raise ValueError(f"Parsed {vals.size}, expected {expected * 3}: {path}")
    vec = vals.reshape((-1, 3))
    return np.linalg.norm(vec, axis=1)


def structure_metrics(selected: list[SelectedTime]) -> list[dict[str, object]]:
    if not CASE_DIR_WIN.exists():
        return []
    rows: list[dict[str, object]] = []
    processors = sorted(CASE_DIR_WIN.glob("processor*"), key=lambda p: int(p.name.replace("processor", "")))
    for row in selected:
        t = f"{row.selected_time_s:g}"
        q_parts: list[np.ndarray] = []
        l2_parts: list[np.ndarray] = []
        w_parts: list[np.ndarray] = []
        missing: list[str] = []
        for proc in processors:
            try:
                q_parts.append(parse_scalar_internal(proc / t / "Q"))
                l2_parts.append(parse_scalar_internal(proc / t / "Lambda2"))
                w_parts.append(parse_vector_mag_internal(proc / t / "vorticity"))
            except FileNotFoundError:
                missing.append(proc.name)
        if not q_parts:
            rows.append({"label": row.label, "time_s": row.selected_time_s, "status": "missing_fields"})
            continue
        q = np.concatenate(q_parts)
        l2 = np.concatenate(l2_parts)
        w = np.concatenate(w_parts)
        q_pos = q[q > 0.0]
        l2_neg = l2[l2 < 0.0]
        rows.append(
            {
                "label": row.label,
                "time_s": row.selected_time_s,
                "n_cells": int(q.size),
                "missing_processors": ";".join(missing),
                "Q_min": float(np.min(q)),
                "Q_p50": float(np.percentile(q, 50)),
                "Q_p95": float(np.percentile(q, 95)),
                "Q_p99": float(np.percentile(q, 99)),
                "Q_max": float(np.max(q)),
                "Q_positive_fraction": float(q_pos.size / q.size),
                "Q_positive_mean": float(np.mean(q_pos)) if q_pos.size else 0.0,
                "Lambda2_min": float(np.min(l2)),
                "Lambda2_p01": float(np.percentile(l2, 1)),
                "Lambda2_negative_fraction": float(l2_neg.size / l2.size),
                "Lambda2_negative_mean": float(np.mean(l2_neg)) if l2_neg.size else 0.0,
                "vorticity_mag_p95": float(np.percentile(w, 95)),
                "vorticity_mag_p99": float(np.percentile(w, 99)),
                "vorticity_mag_max": float(np.max(w)),
                "status": "ok",
            }
        )
    return rows


def plot_metrics(metrics: list[dict[str, object]]) -> None:
    ok = [m for m in metrics if m.get("status") == "ok"]
    if not ok:
        return
    labels = [str(m["label"]) for m in ok]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), constrained_layout=True)
    axes[0].bar(x, [float(m["Q_positive_fraction"]) for m in ok], color="#3b7ea1")
    axes[0].set_ylabel("cell fraction")
    axes[0].set_title("Q > 0 rotation-dominated cell-count proxy")
    axes[1].bar(x, [float(m["Lambda2_negative_fraction"]) for m in ok], color="#8f5f9f")
    axes[1].set_ylabel("cell fraction")
    axes[1].set_title("Lambda2 < 0 vortex-core cell-count proxy")
    axes[2].plot(x, [float(m["vorticity_mag_p99"]) for m in ok], marker="o", label="p99")
    axes[2].plot(x, [float(m["vorticity_mag_max"]) for m in ok], marker="o", label="max")
    axes[2].set_ylabel("|omega| [1/s]")
    axes[2].set_title("Vorticity magnitude")
    axes[2].legend()
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=25, ha="right")
        ax.grid(True, axis="y", alpha=0.25)
    fig.savefig(FIG_DIR / "run008_013_q_lambda2_structure_metrics.png", dpi=180)


def write_report(
    selected: list[SelectedTime],
    vtk_rows: list[dict[str, object]],
    metrics: list[dict[str, object]],
) -> None:
    lines = [
        "# V4b_3D run008 Q/lambda2 structure pass",
        "",
        "## Status",
        "",
        "This layer selects representative full-field checkpoints and prepares the",
        "OpenFOAM execution path for `Q`, `Lambda2`, and `vorticity` fields. Heavy",
        "VTK exports are intentionally written outside Git.",
        "",
        "## Selected checkpoints",
        "",
        "| label | reason | target phase [deg] | selected t [s] | selected phase [deg] | error [deg] |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in selected:
        lines.append(
            f"| `{row.label}` | {row.reason} | {row.target_phase_deg:.2f} | "
            f"{row.selected_time_s:.3f} | {row.selected_phase_deg:.2f} | {row.phase_error_deg:+.2f} |"
        )
    lines += [
        "",
        "## OpenFOAM runner",
        "",
        "- script: `scripts/run008_q_lambda2_013_wsl.sh`",
        f"- case: `{CASE_DIR_WSL_STR}`",
        f"- heavy export directory: `{EXPORT_DIR_WSL_STR}`",
        "",
        "Run from WSL or PowerShell/WSL:",
        "",
        "```bash",
        "bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/results/run008/scripts/run008_q_lambda2_013_wsl.sh",
        "```",
        "",
        "## Export check",
        "",
        "| label | time [s] | VTK files | VTK size [MB] |",
        "|---|---:|---:|---:|",
    ]
    for row in vtk_rows:
        lines.append(
            f"| `{row['label']}` | {float(row['time_s']):.3f} | "
            f"{row['vtk_file_count']} | {row['vtk_size_MB']} |"
        )
    ok_metrics = [m for m in metrics if m.get("status") == "ok"]
    lines += [
        "",
        "## Cell-count structure metrics",
        "",
        "These are first-pass proxies, not volume-integrated vortex measures. They",
        "use all decomposed cells with equal weight.",
        "",
        "| label | time [s] | Q>0 frac | Lambda2<0 frac | Q p99 | |omega| p99 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in ok_metrics:
        lines.append(
            f"| `{row['label']}` | {float(row['time_s']):.3f} | "
            f"{float(row['Q_positive_fraction']):.4f} | "
            f"{float(row['Lambda2_negative_fraction']):.4f} | "
            f"{float(row['Q_p99']):.3g} | "
            f"{float(row['vorticity_mag_p99']):.3g} |"
        )
    lines += [
        "",
        "## Interpretation guide",
        "",
        "- `Q > 0` isolates rotation-dominated regions and should directly expose the",
        "  shedding vortices behind the POD mode pair.",
        "- `Lambda2 < 0` is the companion check for coherent vortex cores.",
        "- The selected `qfins_qwall_max` and `nu_global_max` checkpoints are the key",
        "  tests for whether the heat-transfer response is tied to wake sweeping or",
        "  delayed fin-surface organization.",
        "- The first pass should be inspected in ParaView before promoting this into a",
        "  formal quantitative layer.",
        "",
    ]
    (DATA_DIR / "run008_013_q_lambda2_structure_pass.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    selected = select_times()
    rows = [asdict(s) for s in selected]
    write_csv(DATA_DIR / "run008_013_selected_q_lambda2_times.csv", rows)
    (DATA_DIR / "run008_013_selected_q_lambda2_times.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )
    script = write_runner(selected)
    plot_selected(selected)
    vtk_rows = summarize_vtk(selected)
    metrics = structure_metrics(selected)
    write_csv(DATA_DIR / "run008_013_q_lambda2_structure_metrics.csv", metrics)
    (DATA_DIR / "run008_013_q_lambda2_structure_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    plot_metrics(metrics)
    write_csv(DATA_DIR / "run008_013_vtk_export_check.csv", vtk_rows)
    write_report(selected, vtk_rows, metrics)
    print(f"Wrote {script}")
    print((DATA_DIR / "run008_013_q_lambda2_structure_pass.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
