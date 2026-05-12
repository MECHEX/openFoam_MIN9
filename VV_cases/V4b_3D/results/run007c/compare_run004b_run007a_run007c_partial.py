"""Partial thermal/force comparison for run004b, run007a, run007c.

Uses the common window:

- force coefficients: t = 0.5..2.0 s
- thermal fields/wallHeatFlux: t = 0.5, 1.0, 1.3, 1.5, 1.7, 2.0 s

This is a short smoke-test comparison, not a final production average.
"""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent

RUNS = {
    "run004b": {
        "case": Path("/home/hexmachina/of_runs/V4b_3D_run004b"),
        "model": "baseline eConst/Boussinesq Cv=718",
        "capacity_case": 718.0,
    },
    "run007a": {
        "case": Path("/home/hexmachina/of_runs/V4b_3D_run007a"),
        "model": "variable props: incompressiblePerfectGas + Sutherland",
        "capacity_case": 1005.0,
    },
    "run007c": {
        "case": Path("/home/hexmachina/of_runs/V4b_3D_run007c"),
        "model": "constant props: eConst/Boussinesq capacity=1005",
        "capacity_case": 1005.0,
    },
}

THERMAL_TIMES = ("0.5", "1", "1.3", "1.5", "1.7", "2")
FORCE_START = 0.5
FORCE_END = 2.0
HOT_PATCHES = {"hot_tube", "hot_fin_z_min", "hot_fin_z_max"}

D = 0.012
U_IN = 0.25267
T_IN = 293.15
T_HOT = 343.15
A_HOT_TOTAL = 0.002032
MU_REF = 1.827e-05
CP_REF = 1005.0
PR_REF = 0.713
K_REF = MU_REF * CP_REF / PR_REF


def pct(value: float | None, ref: float | None) -> float | None:
    if value is None or ref in (None, 0):
        return None
    return 100.0 * (value - ref) / ref


def mean_std(values: list[float]) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    return float(np.mean(arr)), float(np.std(arr))


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def parse_force(path: Path) -> dict[str, np.ndarray]:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        rows.append((float(parts[0]), float(parts[2]), float(parts[3])))
    arr = np.asarray(rows, dtype=float)
    return {"time": arr[:, 0], "Cd": arr[:, 1], "Cl": arr[:, 2]}


def frequency_fft(time: np.ndarray, signal: np.ndarray) -> float | None:
    if len(time) < 16:
        return None
    dt = float(np.median(np.diff(time)))
    ti = np.arange(time[0], time[-1], dt)
    yi = np.interp(ti, time, signal) - float(np.mean(signal))
    freqs = np.fft.rfftfreq(len(yi), d=dt)
    power = np.abs(np.fft.rfft(yi)) ** 2
    idx = np.where((freqs >= 2.0) & (freqs <= 5.0))[0]
    if not len(idx):
        return None
    return float(freqs[idx[np.argmax(power[idx])]])


def force_stats(case: Path) -> dict[str, float | None]:
    data = parse_force(case / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat")
    mask = (data["time"] >= FORCE_START) & (data["time"] <= FORCE_END)
    t = data["time"][mask]
    cd = data["Cd"][mask]
    cl = data["Cl"][mask]
    cl_mean = float(np.mean(cl))
    f = frequency_fft(t, cl)
    return {
        "n_force": int(len(cd)),
        "Cd_mean": float(np.mean(cd)),
        "Cl_mean": cl_mean,
        "Cl_rms": float(np.sqrt(np.mean((cl - cl_mean) ** 2))),
        "f_fft_Hz": f,
        "St_fft": f * D / U_IN if f is not None else None,
    }


def boundary_patch(case: Path, patch_name: str) -> dict[str, int]:
    text = (case / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found in {case}")
    section = match.group(1)
    return {
        "nFaces": int(re.search(r"nFaces\s+(\d+)\s*;", section).group(1)),
        "startFace": int(re.search(r"startFace\s+(\d+)\s*;", section).group(1)),
    }


def field_patch_values(case: Path, time_name: str, field: str, patch_name: str, n_faces: int) -> np.ndarray:
    text = (case / time_name / field).read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\n\s*\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found in {field}")
    section = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.full(n_faces, float(uniform.group(1)))
    vals_match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, flags=re.S)
    if not vals_match:
        raise ValueError(f"No scalar patch values in {field}:{patch_name}")
    vals = np.fromstring(vals_match.group(2), sep=" ", dtype=float)
    if len(vals) != n_faces:
        raise ValueError(f"Expected {n_faces} {field} values, got {len(vals)}")
    return vals


def parse_points(path: Path) -> np.ndarray:
    text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
    match = re.search(r"\n\s*(\d+)\s*\(\s*(.*?)\s*\)\s*$", text, flags=re.S)
    vals = np.fromstring(match.group(2).replace("(", " ").replace(")", " "), sep=" ", dtype=float)
    return vals.reshape((-1, 3))


def outlet_faces(path: Path, start_face: int, n_faces: int) -> list[list[int]]:
    faces = []
    in_list = False
    face_index = 0
    end_face = start_face + n_faces
    with path.open("r", encoding="utf-8", errors="replace") as handle:
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


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    return (d1 - d2) / math.log(d1 / d2)


def wall_heat_flux_by_time(case: Path) -> dict[str, float]:
    # foamPostProcess writes multiple requested times into the first requested
    # time directory, so scan all wallHeatFlux.dat files and key by actual time.
    by_time: dict[str, float] = {}
    for path in sorted((case / "postProcessing" / "wallHeatFlux").glob("*/wallHeatFlux.dat")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            time_name = f"{float(parts[0]):g}"
            patch = parts[1]
            if patch in HOT_PATCHES:
                by_time[time_name] = by_time.get(time_name, 0.0) + float(parts[4])
    return by_time


def thermal_stats(case: Path, capacity_case: float) -> dict[str, float]:
    patch = boundary_patch(case, "outlet")
    n_faces = patch["nFaces"]
    points = parse_points(case / "constant" / "polyMesh" / "points")
    faces = outlet_faces(case / "constant" / "polyMesh" / "faces", patch["startFace"], n_faces)
    areas = np.asarray([polygon_area(points[f]) for f in faces], dtype=float)
    wall_by_time = wall_heat_flux_by_time(case)

    t_mass_values = []
    q_air_case_values = []
    q_air_cp_values = []
    q_wall_values = []
    nu_wall_case_values = []
    nu_wall_ref_values = []
    nu_air_case_values = []
    nu_air_ref_values = []

    k_case = MU_REF * capacity_case / PR_REF
    for time_name in THERMAL_TIMES:
        t_vals = field_patch_values(case, time_name, "T", "outlet", n_faces)
        phi_vals = field_patch_values(case, time_name, "phi", "outlet", n_faces)
        weights = np.maximum(phi_vals, 0.0)
        if float(np.sum(weights)) <= 0:
            weights = np.abs(phi_vals)
        t_mass = float(np.sum(t_vals * weights) / np.sum(weights))
        m_dot = float(np.sum(weights))
        q_air_case = m_dot * capacity_case * (t_mass - T_IN)
        q_air_cp = m_dot * CP_REF * (t_mass - T_IN)
        q_wall = wall_by_time[time_name]
        lmtd_value = lmtd(t_mass)
        h_wall = q_wall / (A_HOT_TOTAL * lmtd_value)
        h_air_case = q_air_case / (A_HOT_TOTAL * lmtd_value)
        h_air_ref = q_air_cp / (A_HOT_TOTAL * lmtd_value)

        t_mass_values.append(t_mass)
        q_air_case_values.append(q_air_case)
        q_air_cp_values.append(q_air_cp)
        q_wall_values.append(q_wall)
        nu_wall_case_values.append(h_wall * D / k_case)
        nu_wall_ref_values.append(h_wall * D / K_REF)
        nu_air_case_values.append(h_air_case * D / k_case)
        nu_air_ref_values.append(h_air_ref * D / K_REF)

    result: dict[str, float] = {
        "n_thermal_times": float(len(THERMAL_TIMES)),
        "capacity_case": capacity_case,
        "k_case": k_case,
    }
    for name, values in {
        "T_out_mass_K": t_mass_values,
        "Q_air_case_W": q_air_case_values,
        "Q_air_Cp1005_W": q_air_cp_values,
        "Q_wall_hot_W": q_wall_values,
        "Nu_wall_case_k": nu_wall_case_values,
        "Nu_wall_ref_k": nu_wall_ref_values,
        "Nu_air_case_k": nu_air_case_values,
        "Nu_air_ref_k": nu_air_ref_values,
    }.items():
        avg, std = mean_std(values)
        result[name] = avg
        result[f"{name}_std"] = std
    result["wall_vs_air_case_pct"] = pct(result["Q_wall_hot_W"], result["Q_air_case_W"])
    result["wall_vs_air_Cp1005_pct"] = pct(result["Q_wall_hot_W"], result["Q_air_Cp1005_W"])
    return result


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None or not math.isfinite(value):
        return "N/A"
    return f"{value:.{digits}f}"


def main() -> None:
    rows = []
    for run, meta in RUNS.items():
        row: dict[str, float | str | None] = {
            "run": run,
            "model": meta["model"],
            "force_window": f"{FORCE_START}..{FORCE_END}",
            "thermal_times": ",".join(THERMAL_TIMES),
        }
        row.update(force_stats(meta["case"]))
        row.update(thermal_stats(meta["case"], meta["capacity_case"]))
        rows.append(row)

    refs = {row["run"]: row for row in rows}
    for row in rows:
        for ref_name in ("run004b", "run007a"):
            ref = refs[ref_name]
            for key in (
                "Cd_mean",
                "Cl_rms",
                "Q_wall_hot_W",
                "Q_air_case_W",
                "Q_air_Cp1005_W",
                "Nu_wall_case_k",
                "Nu_wall_ref_k",
                "Nu_air_case_k",
                "Nu_air_ref_k",
                "T_out_mass_K",
            ):
                row[f"{key}_diff_pct_vs_{ref_name}"] = pct(row[key], ref[key])

    csv_path = SCRIPT_DIR / "run004b_run007a_run007c_final_0p5_2_compare.csv"
    json_path = SCRIPT_DIR / "run004b_run007a_run007c_final_0p5_2_compare.json"
    md_path = SCRIPT_DIR / "run004b_run007a_run007c_final_0p5_2_compare.md"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    md = [
        "# run004b vs run007a vs run007c final 0.5..2.0 smoke comparison",
        "",
        "This is the completed short `run007c` smoke-test comparison, not a long production average.",
        "",
        f"- force window: `{FORCE_START}..{FORCE_END} s`",
        f"- thermal checkpoints: `{', '.join(THERMAL_TIMES)} s`",
        f"- reference conductivity for `Nu_wall_ref_k`: `k_ref = {K_REF:.8f} W/(m K)`",
        "",
        "| Run | model | Cd | Cl_rms | Q_wall W | Q_air case W | Nu_wall case-k | Nu_wall ref-k | wall-air case diff |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        md.append(
            f"| {row['run']} | {row['model']} | {fmt(row['Cd_mean'], 4)} | "
            f"{fmt(row['Cl_rms'], 4)} | {fmt(row['Q_wall_hot_W'], 4)} | "
            f"{fmt(row['Q_air_case_W'], 4)} | {fmt(row['Nu_wall_case_k'], 4)} | "
            f"{fmt(row['Nu_wall_ref_k'], 4)} | {fmt(row['wall_vs_air_case_pct'], 1)}% |"
        )

    r7a = refs["run007a"]
    r7c = refs["run007c"]
    md.extend(
        [
            "",
            "## Key Comparisons",
            "",
            f"- `run007a` vs `run004b`: Q_wall {r7a['Q_wall_hot_W_diff_pct_vs_run004b']:+.2f}%, "
            f"Nu_wall_ref_k {r7a['Nu_wall_ref_k_diff_pct_vs_run004b']:+.2f}%, "
            f"Cd {r7a['Cd_mean_diff_pct_vs_run004b']:+.2f}%.",
            f"- `run007c` vs `run004b`: Q_wall {r7c['Q_wall_hot_W_diff_pct_vs_run004b']:+.2f}%, "
            f"Nu_wall_ref_k {r7c['Nu_wall_ref_k_diff_pct_vs_run004b']:+.2f}%, "
            f"Nu_wall_case_k {r7c['Nu_wall_case_k_diff_pct_vs_run004b']:+.2f}%.",
            f"- `run007c` vs `run007a`: Q_wall {r7c['Q_wall_hot_W_diff_pct_vs_run007a']:+.2f}%, "
            f"Nu_wall_ref_k {r7c['Nu_wall_ref_k_diff_pct_vs_run007a']:+.2f}%.",
            "",
            "## Interpretation",
            "",
            "Using the common reference conductivity, both `run007a` and `run007c` show higher wall heat flux/Nu than the old `run004b` baseline.",
            "However, `run007c` is higher than `run007a` in this completed smoke-test window, so the increase is not primarily caused by variable properties.",
            "When `run007c` is normalized with its matching case conductivity (`k = mu*1005/Pr`), its wall-side Nu is almost the same as the old baseline normalized with `k = mu*718/Pr`.",
            "For `run004b` and `run007c`, the wall-side and air-side heat rates close to about 1.4%, while `run007a` remains energetically inconsistent over this short window.",
        ]
    )
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(md_path.read_text(encoding="utf-8"))
    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
