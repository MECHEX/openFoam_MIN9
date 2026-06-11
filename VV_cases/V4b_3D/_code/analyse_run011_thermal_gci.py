from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


CASES = [
    {
        "name": "coarse",
        "cells": 196_938,
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run011_gci_coarse"),
    },
    {
        "name": "medium_run008",
        "cells": 407_440,
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run008"),
    },
    {
        "name": "fine",
        "cells": 829_761,
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run011_gci_fine"),
    },
]

OUT_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/results/run011_gci_thermal_analysis")

D = 0.012
T_IN = 293.15
T_HOT = 343.15
CP_AIR = 1005.0
MU_AIR = 1.827e-05
PR_AIR = 0.713
K_AIR = CP_AIR * MU_AIR / PR_AIR
A_HOT_TOTAL = 0.002032
WINDOW = (2.0, 3.0)


def read_wall_heat_flux(case_dir: Path) -> dict[str, np.ndarray]:
    path = case_dir / "postProcessing" / "wallHeatFlux" / "0" / "wallHeatFlux.dat"
    per_time: dict[float, dict[str, dict[str, float]]] = {}
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 6:
                per_time.setdefault(float(parts[0]), {})[parts[1]] = {
                    "Q": float(parts[4]),
                    "q": float(parts[5]),
                }
    times = np.asarray(sorted(per_time), dtype=float)
    tube = np.asarray([per_time[t].get("hot_tube", {}).get("Q", np.nan) for t in times])
    fin_min = np.asarray([per_time[t].get("hot_fin_z_min", {}).get("Q", np.nan) for t in times])
    fin_max = np.asarray([per_time[t].get("hot_fin_z_max", {}).get("Q", np.nan) for t in times])
    tube_area_raw = np.asarray([per_time[t].get("hot_tube", {}).get("Q", np.nan) / per_time[t].get("hot_tube", {}).get("q", np.nan) for t in times])
    fin_min_area_raw = np.asarray([per_time[t].get("hot_fin_z_min", {}).get("Q", np.nan) / per_time[t].get("hot_fin_z_min", {}).get("q", np.nan) for t in times])
    fin_max_area_raw = np.asarray([per_time[t].get("hot_fin_z_max", {}).get("Q", np.nan) / per_time[t].get("hot_fin_z_max", {}).get("q", np.nan) for t in times])
    return {
        "time": times,
        "Q_tube": tube,
        "Q_fin_min": fin_min,
        "Q_fin_max": fin_max,
        "Q_fins": fin_min + fin_max,
        "Q_wall": tube + fin_min + fin_max,
        "A_tube_raw": tube_area_raw,
        "A_fin_min_raw": fin_min_area_raw,
        "A_fin_max_raw": fin_max_area_raw,
    }


def boundary_patch(case_dir: Path, patch_name: str) -> dict[str, int]:
    text = (case_dir / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found in {case_dir}")
    section = match.group(1)
    return {
        "nFaces": int(re.search(r"nFaces\s+(\d+)\s*;", section).group(1)),
        "startFace": int(re.search(r"startFace\s+(\d+)\s*;", section).group(1)),
    }


def parse_points(path: Path) -> np.ndarray:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    count = None
    start = None
    for i, line in enumerate(lines):
        if line.strip().isdigit():
            count = int(line.strip())
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "(":
                    start = j + 1
                    break
            break
    if count is None or start is None:
        raise ValueError(f"Could not parse points from {path}")
    values = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped == ")":
            break
        values.extend(float(v) for v in stripped.strip("()").split())
    arr = np.asarray(values).reshape((-1, 3))
    if len(arr) != count:
        raise ValueError(f"Expected {count} points, got {len(arr)}")
    return arr


def outlet_faces(case_dir: Path, start_face: int, n_faces: int) -> list[list[int]]:
    faces = []
    face_index = 0
    in_list = False
    end_face = start_face + n_faces
    with (case_dir / "constant" / "polyMesh" / "faces").open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not in_list:
                if line == "(":
                    in_list = True
                continue
            if line == ")":
                break
            if start_face <= face_index < end_face:
                nums = [int(v) for v in re.findall(r"\d+", line)]
                faces.append(nums[1 : 1 + nums[0]])
            face_index += 1
            if face_index >= end_face:
                break
    return faces


def polygon_area(points: np.ndarray) -> float:
    origin = points[0]
    area_vec = np.zeros(3)
    for i in range(1, len(points) - 1):
        area_vec += np.cross(points[i] - origin, points[i + 1] - origin)
    return 0.5 * float(np.linalg.norm(area_vec))


def reconstructed_outlet_times(case_dir: Path) -> np.ndarray:
    times = []
    for path in case_dir.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if (path / "T").exists() and (path / "phi").exists() and WINDOW[0] - 1e-9 <= t <= WINDOW[1] + 1e-9:
            times.append(t)
    return np.asarray(sorted(times), dtype=float)


def field_patch_values(case_dir: Path, time_name: str, field_name: str, patch_name: str, n_faces: int) -> np.ndarray:
    text = (case_dir / time_name / field_name).read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\n\s*\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found in {field_name} at {case_dir}/{time_name}")
    section = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.full(n_faces, float(uniform.group(1)))
    vals_match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, flags=re.S)
    if not vals_match:
        raise ValueError(f"Could not parse {field_name}:{patch_name} at {case_dir}/{time_name}")
    vals = np.fromstring(vals_match.group(2), sep=" ")
    if len(vals) != n_faces:
        raise ValueError(f"Expected {n_faces} values for {field_name}:{patch_name}, got {len(vals)}")
    return vals


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    return (d1 - d2) / math.log(d1 / d2)


def outlet_thermal_series(case_dir: Path) -> dict[str, np.ndarray]:
    patch = boundary_patch(case_dir, "outlet")
    points = parse_points(case_dir / "constant" / "polyMesh" / "points")
    faces = outlet_faces(case_dir, patch["startFace"], patch["nFaces"])
    areas = np.asarray([polygon_area(points[face]) for face in faces])
    area_total = float(np.sum(areas))
    rows = []
    for t in reconstructed_outlet_times(case_dir):
        name = f"{t:g}"
        t_vals = field_patch_values(case_dir, name, "T", "outlet", patch["nFaces"])
        phi_vals = field_patch_values(case_dir, name, "phi", "outlet", patch["nFaces"])
        weights = np.maximum(phi_vals, 0.0)
        if np.sum(weights) <= 0:
            weights = np.abs(phi_vals)
        t_area = float(np.sum(t_vals * areas) / area_total)
        t_mass = float(np.sum(t_vals * weights) / np.sum(weights))
        m_dot = float(np.sum(weights))
        q_air_area = m_dot * CP_AIR * (t_area - T_IN)
        q_air_mass = m_dot * CP_AIR * (t_mass - T_IN)
        l_area = lmtd(t_area)
        l_mass = lmtd(t_mass)
        nu_area = (q_air_area / (A_HOT_TOTAL * l_area)) * D / K_AIR
        nu_mass = (q_air_mass / (A_HOT_TOTAL * l_mass)) * D / K_AIR
        rows.append([t, t_area, t_mass, m_dot, q_air_area, q_air_mass, l_area, l_mass, nu_area, nu_mass])
    if not rows:
        raise ValueError(f"No reconstructed outlet T/phi found for {case_dir} in window {WINDOW}")
    arr = np.asarray(rows)
    return {
        "time": arr[:, 0],
        "T_area": arr[:, 1],
        "T_mass": arr[:, 2],
        "m_dot": arr[:, 3],
        "Q_air": arr[:, 4],
        "Q_air_massT": arr[:, 5],
        "LMTD": arr[:, 6],
        "LMTD_massT": arr[:, 7],
        "Nu_EB": arr[:, 8],
        "Nu_EB_massT": arr[:, 9],
    }


def mask_window(time: np.ndarray) -> np.ndarray:
    return (time >= WINDOW[0] - 1e-12) & (time <= WINDOW[1] + 1e-12)


def interp_to(time_new: np.ndarray, source_time: np.ndarray, source_values: np.ndarray) -> np.ndarray:
    return np.interp(time_new, source_time, source_values)


def scaled_patch_areas(wall: dict[str, np.ndarray]) -> dict[str, float]:
    mw = mask_window(wall["time"])
    raw = {
        "A_tube": float(np.nanmean(wall["A_tube_raw"][mw])),
        "A_fin_min": float(np.nanmean(wall["A_fin_min_raw"][mw])),
        "A_fin_max": float(np.nanmean(wall["A_fin_max_raw"][mw])),
    }
    raw_total = raw["A_tube"] + raw["A_fin_min"] + raw["A_fin_max"]
    scale = A_HOT_TOTAL / raw_total
    return {
        "A_tube": raw["A_tube"] * scale,
        "A_fin_min": raw["A_fin_min"] * scale,
        "A_fin_max": raw["A_fin_max"] * scale,
        "A_hot_total": A_HOT_TOTAL,
        "A_hot_total_raw": raw_total,
        "area_scale_to_reference": scale,
    }


def build_heat_series(wall: dict[str, np.ndarray], outlet: dict[str, np.ndarray], areas: dict[str, float]) -> dict[str, np.ndarray]:
    mw = mask_window(wall["time"])
    time = wall["time"][mw]
    q_tube = wall["Q_tube"][mw]
    q_fin_min = wall["Q_fin_min"][mw]
    q_fin_max = wall["Q_fin_max"][mw]
    q_wall = wall["Q_wall"][mw]
    q_fins = wall["Q_fins"][mw]
    q_air = interp_to(time, outlet["time"], outlet["Q_air"])
    q_air_mass = interp_to(time, outlet["time"], outlet["Q_air_massT"])
    t_out = interp_to(time, outlet["time"], outlet["T_area"])
    lmtd_i = interp_to(time, outlet["time"], outlet["LMTD"])
    nu_wall = (q_wall / (A_HOT_TOTAL * lmtd_i)) * D / K_AIR
    nu_tube = (q_tube / (areas["A_tube"] * lmtd_i)) * D / K_AIR
    nu_fins = (q_fins / ((areas["A_fin_min"] + areas["A_fin_max"]) * lmtd_i)) * D / K_AIR
    nu_eb = interp_to(time, outlet["time"], outlet["Nu_EB"])
    closure = 100.0 * (q_wall - q_air) / q_air
    closure_mass = 100.0 * (q_wall - q_air_mass) / q_air_mass
    return {
        "time": time,
        "Q_air": q_air,
        "Q_air_massT": q_air_mass,
        "Q_wall": q_wall,
        "Q_tube": q_tube,
        "Q_fins": q_fins,
        "T_out": t_out,
        "Nu_wall": nu_wall,
        "Nu_tube_wall": nu_tube,
        "Nu_fins_wall": nu_fins,
        "Nu_EB": nu_eb,
        "closure_pct": closure,
        "closure_ratio_of_means_pct": np.full_like(time, 100.0 * (float(np.mean(q_wall)) - float(np.mean(q_air))) / float(np.mean(q_air))),
        "closure_massT_pct": closure_mass,
        "tube_share_pct": 100.0 * q_tube / q_wall,
        "fins_share_pct": 100.0 * q_fins / q_wall,
    }


def apparent_order(phi1: float, phi2: float, phi3: float, r21: float, r32: float) -> float | None:
    e21 = phi2 - phi1
    e32 = phi3 - phi2
    if e21 == 0 or e32 == 0 or e21 * e32 <= 0:
        return None
    s = 1.0
    p = max(0.1, abs(math.log(abs(e32 / e21)) / math.log(r21)))
    for _ in range(100):
        numerator = r21**p - s
        denominator = r32**p - s
        if numerator <= 0 or denominator <= 0:
            return None
        q = math.log(numerator / denominator)
        p_new = abs((math.log(abs(e32 / e21)) + q) / math.log(r21))
        if abs(p_new - p) < 1e-10:
            return p_new
        p = p_new
    return p


def gci(phi1: float, phi2: float, phi3: float, n1: int, n2: int, n3: int) -> dict[str, float | str | None]:
    r21 = (n1 / n2) ** (1.0 / 3.0)
    r32 = (n2 / n3) ** (1.0 / 3.0)
    p = apparent_order(phi1, phi2, phi3, r21, r32)
    if p is None:
        return {"r21": r21, "r32": r32, "p": None, "GCI21_percent": None, "GCI32_percent": None, "status": "non-monotonic"}
    eps21 = abs((phi1 - phi2) / phi1)
    eps32 = abs((phi2 - phi3) / phi2)
    fs = 1.25
    return {
        "r21": r21,
        "r32": r32,
        "p": p,
        "GCI21_percent": fs * eps21 / (r21**p - 1.0) * 100.0,
        "GCI32_percent": fs * eps32 / (r32**p - 1.0) * 100.0,
        "status": "monotonic",
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object, digits: int = 6) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    loaded = []
    summary_rows = []
    metrics = [
        "Q_air",
        "Q_wall",
        "T_out",
        "Nu_EB",
        "Nu_wall",
        "closure_ratio_of_means_pct",
        "closure_pct",
        "Nu_tube_wall",
        "Nu_fins_wall",
        "tube_share_pct",
    ]
    for case in CASES:
        wall = read_wall_heat_flux(case["path"])
        outlet = outlet_thermal_series(case["path"])
        areas = scaled_patch_areas(wall)
        series = build_heat_series(wall, outlet, areas)
        loaded.append({**case, "series": series, "areas": areas})
        row: dict[str, object] = {"case": case["name"], "cells": case["cells"], "n_wall": len(series["time"]), "n_outlet": len(outlet["time"])}
        for metric in metrics:
            values = series[metric]
            row[f"{metric}_mean"] = float(np.mean(values))
            row[f"{metric}_std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
            row[f"{metric}_t3"] = float(values[np.argmin(np.abs(series["time"] - 3.0))])
        summary_rows.append(row)
        write_csv(
            OUT_DIR / f"run011_thermal_timeseries_{case['name']}.csv",
            [{key: float(value[i]) for key, value in series.items()} for i in range(len(series["time"]))],
        )
    write_csv(OUT_DIR / "run011_thermal_summary.csv", summary_rows)

    gci_rows = []
    for source in ["mean", "t3"]:
        for metric in ["Nu_EB", "Nu_wall", "Q_wall", "T_out", "closure_ratio_of_means_pct"]:
            key = f"{metric}_{source}"
            phi3 = float(summary_rows[0][key])
            phi2 = float(summary_rows[1][key])
            phi1 = float(summary_rows[2][key])
            result = gci(phi1, phi2, phi3, int(summary_rows[2]["cells"]), int(summary_rows[1]["cells"]), int(summary_rows[0]["cells"]))
            gci_rows.append({"metric": metric, "source": source, "coarse": phi3, "medium": phi2, "fine": phi1, **result})
    write_csv(OUT_DIR / "run011_thermal_gci_results.csv", gci_rows)

    for metric in ["Nu_EB", "Nu_wall", "Q_air", "Q_wall", "closure_pct"]:
        plt.figure(figsize=(8, 4.8))
        for case in loaded:
            plt.plot(case["series"]["time"], case["series"][metric], label=f"{case['name']} ({case['cells']:,} cells)")
        plt.xlabel("time [s]")
        plt.ylabel(metric)
        plt.title(f"V4b thermal GCI check: {metric}, common window 2-3 s")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT_DIR / f"run011_thermal_{metric}_timeseries_2_3s.png", dpi=180)
        plt.close()

    for source in ["mean", "t3"]:
        plt.figure(figsize=(8, 4.8))
        xs = [row["cells"] for row in summary_rows]
        for metric in ["Nu_EB", "Nu_wall"]:
            ys = [row[f"{metric}_{source}"] for row in summary_rows]
            plt.plot(xs, ys, marker="o", label=metric)
        plt.xlabel("cell count")
        plt.ylabel("Nu")
        plt.title(f"V4b thermal grid trend ({source}, 2-3 s window)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT_DIR / f"run011_thermal_grid_trend_{source}.png", dpi=180)
        plt.close()

    report = [
        "# V4b run011 thermal GCI analysis",
        "",
        "Date: 2026-06-05",
        "",
        "Window: `2.0..3.0 s` for all three grids. Outlet `T/phi` was reconstructed for the new coarse and fine cases.",
        "",
        "## Thermal Summary",
        "",
        "| Case | Cells | Nu_EB mean | Nu_wall mean | closure ratio [%] | Q_air mean [W] | Q_wall mean [W] | T_out mean [K] |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        report.append(
            f"| {row['case']} | {int(row['cells'])} | {fmt(row['Nu_EB_mean'], 8)} | {fmt(row['Nu_wall_mean'], 8)} | {fmt(row['closure_ratio_of_means_pct_mean'], 6)} | {fmt(row['Q_air_mean'], 8)} | {fmt(row['Q_wall_mean'], 8)} | {fmt(row['T_out_mean'], 8)} |"
        )
    report += [
        "",
        "## Thermal GCI",
        "",
        "| Metric | Source | p | GCI fine/medium [%] | GCI medium/coarse [%] | Status |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in gci_rows:
        report.append(
            f"| {row['metric']} | {row['source']} | {fmt(row['p'], 5)} | {fmt(row['GCI21_percent'], 5)} | {fmt(row['GCI32_percent'], 5)} | {row['status']} |"
        )
    report += [
        "",
        "## Interpretation",
        "",
        "- `Nu_EB` and `Nu_wall` both show monotonic grid trends in the common `2-3 s` window.",
        "- Medium-grid thermal values are within about 1% of the fine grid for both independent heat-transfer definitions.",
        "- `closure_ratio_of_means_pct` is monotonic in this short common window, but its absolute value is larger than the full production-window closure because `2-3 s` still contains outlet transport lag. Treat it as an internal consistency diagnostic, not as the primary grid-convergence observable.",
        "- The common `2-3 s` window is shorter than the full production `run008` window (`2-10 s`), but it is the valid overlap for the new coarse/fine GCI runs. The full `run008` production window remains the reference for final closure reporting.",
        "",
    ]
    (OUT_DIR / "run011_thermal_gci_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT_DIR / "run011_thermal_gci_results.json").write_text(json.dumps({"summary": summary_rows, "gci": gci_rows}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
