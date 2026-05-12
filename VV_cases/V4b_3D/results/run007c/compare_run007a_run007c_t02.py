"""Very early t=0.2 comparison for run007a vs run007c.

run007a: variable-property incompressiblePerfectGas + Sutherland.
run007c: stable constant-property eConst/Boussinesq diagnostic with capacity 1005.

This is a startup sanity check, not a production averaging window.
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
    "run007a": {
        "case": Path("/home/hexmachina/of_runs/V4b_3D_run007a"),
        "model": "variable props: incompressiblePerfectGas + Sutherland",
    },
    "run007c": {
        "case": Path("/home/hexmachina/of_runs/V4b_3D_run007c"),
        "model": "constant props: eConst/Boussinesq capacity=1005",
    },
}

D = 0.012
T_IN = 293.15
T_HOT = 343.15
A_HOT_TOTAL = 0.002032
MU_REF = 1.827e-05
CP_REF = 1005.0
PR_REF = 0.713
K_REF = MU_REF * CP_REF / PR_REF
TIME_NAME = "0.2"
FORCE_START = 0.1
FORCE_END = 0.2
HOT_PATCHES = {"hot_tube", "hot_fin_z_min", "hot_fin_z_max"}


def pct(value: float, ref: float) -> float:
    return 100.0 * (value - ref) / ref


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


def force_stats(case: Path) -> dict[str, float]:
    data = parse_force(case / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat")
    mask = (data["time"] >= FORCE_START) & (data["time"] <= FORCE_END)
    cd = data["Cd"][mask]
    cl = data["Cl"][mask]
    cl_mean = float(np.mean(cl))
    return {
        "n_force": int(len(cd)),
        "Cd_mean_0p1_0p2": float(np.mean(cd)),
        "Cl_mean_0p1_0p2": cl_mean,
        "Cl_rms_0p1_0p2": float(np.sqrt(np.mean((cl - cl_mean) ** 2))),
    }


def boundary_patch(case: Path, patch_name: str) -> dict[str, int]:
    text = (case / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found")
    section = match.group(1)
    return {
        "nFaces": int(re.search(r"nFaces\s+(\d+)\s*;", section).group(1)),
        "startFace": int(re.search(r"startFace\s+(\d+)\s*;", section).group(1)),
    }


def field_patch_values(case: Path, field: str, patch_name: str, n_faces: int) -> np.ndarray:
    text = (case / TIME_NAME / field).read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\n\s*\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found in {field}")
    section = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.full(n_faces, float(uniform.group(1)))
    vals_match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, flags=re.S)
    if not vals_match:
        raise ValueError(f"No scalar values for {field}:{patch_name}")
    vals = np.fromstring(vals_match.group(2), sep=" ", dtype=float)
    if len(vals) != n_faces:
        raise ValueError(f"Expected {n_faces} values for {field}:{patch_name}, got {len(vals)}")
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


def outlet_stats(case: Path) -> dict[str, float]:
    patch = boundary_patch(case, "outlet")
    n_faces = patch["nFaces"]
    points = parse_points(case / "constant" / "polyMesh" / "points")
    faces = outlet_faces(case / "constant" / "polyMesh" / "faces", patch["startFace"], n_faces)
    areas = np.asarray([polygon_area(points[f]) for f in faces], dtype=float)
    t_vals = field_patch_values(case, "T", "outlet", n_faces)
    phi_vals = field_patch_values(case, "phi", "outlet", n_faces)
    t_area = float(np.sum(t_vals * areas) / np.sum(areas))
    weights = np.maximum(phi_vals, 0.0)
    if float(np.sum(weights)) <= 0:
        weights = np.abs(phi_vals)
    t_mass = float(np.sum(t_vals * weights) / np.sum(weights))
    m_dot = float(np.sum(weights))
    return {
        "T_out_area_K": t_area,
        "T_out_mass_K": t_mass,
        "m_dot_proxy": m_dot,
        "Q_air_Cp1005_W": m_dot * CP_REF * (t_mass - T_IN),
    }


def wall_heat_flux(case: Path) -> dict[str, float]:
    path = case / "postProcessing" / "wallHeatFlux" / TIME_NAME / "wallHeatFlux.dat"
    rows: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        patch = parts[1]
        if patch in HOT_PATCHES:
            rows[f"Q_wall_{patch}_W"] = float(parts[4])
    rows["Q_wall_hot_total_W"] = sum(rows.values())
    return rows


def add_nu(row: dict[str, float]) -> None:
    h_wall = row["Q_wall_hot_total_W"] / (A_HOT_TOTAL * lmtd(row["T_out_mass_K"]))
    row["k_ref_W_mK"] = K_REF
    row["Nu_wall_ref_k"] = h_wall * D / K_REF


def main() -> None:
    rows = []
    for run, meta in RUNS.items():
        row = {
            "run": run,
            "model": meta["model"],
            "time_for_thermal": float(TIME_NAME),
            "force_window": f"{FORCE_START}..{FORCE_END}",
        }
        row.update(force_stats(meta["case"]))
        row.update(outlet_stats(meta["case"]))
        row.update(wall_heat_flux(meta["case"]))
        add_nu(row)
        rows.append(row)

    baseline = rows[0]
    for row in rows:
        for key in (
            "Cd_mean_0p1_0p2",
            "Cl_rms_0p1_0p2",
            "T_out_mass_K",
            "Q_wall_hot_total_W",
            "Q_air_Cp1005_W",
            "Nu_wall_ref_k",
        ):
            row[f"{key}_diff_pct_vs_run007a"] = pct(row[key], baseline[key])

    csv_path = SCRIPT_DIR / "run007a_vs_run007c_t02_quick_compare.csv"
    json_path = SCRIPT_DIR / "run007a_vs_run007c_t02_quick_compare.json"
    md_path = SCRIPT_DIR / "run007a_vs_run007c_t02_quick_compare.md"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    def f(v: float, n: int = 4) -> str:
        return f"{v:.{n}f}"

    md = [
        "# run007a vs run007c t=0.2 quick comparison",
        "",
        "This is a very early startup sanity check, not a production averaging window.",
        "Nu is normalized with the same reference conductivity `k_ref = mu_ref*Cp_ref/Pr_ref = "
        f"{K_REF:.8f} W/(m K)` for both cases.",
        "",
        "| Run | model | Cd 0.1..0.2 | Cl_rms 0.1..0.2 | T_out mass K | Q_wall W | Q_air Cp1005 W | Nu_wall/k_ref |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        md.append(
            f"| {row['run']} | {row['model']} | {f(row['Cd_mean_0p1_0p2'])} | "
            f"{f(row['Cl_rms_0p1_0p2'])} | {f(row['T_out_mass_K'])} | "
            f"{f(row['Q_wall_hot_total_W'])} | {f(row['Q_air_Cp1005_W'], 8)} | "
            f"{f(row['Nu_wall_ref_k'])} |"
        )
    r = rows[1]
    md.extend(
        [
            "",
            "## Early interpretation",
            "",
            f"- `run007c` wall heat input is {r['Q_wall_hot_total_W_diff_pct_vs_run007a']:+.2f}% versus `run007a` at `t=0.2 s`.",
            f"- `run007c` wall-side Nu using common `k_ref` is {r['Nu_wall_ref_k_diff_pct_vs_run007a']:+.2f}% versus `run007a`.",
            f"- Force coefficients are almost unchanged at this early time: Cd difference {r['Cd_mean_0p1_0p2_diff_pct_vs_run007a']:+.2f}%.",
            "",
            "At this very early checkpoint, the variable-property case is not producing a larger wall-side Nu than the Cp-scale constant-property fallback. "
            "The constant `1005` fallback is actually about 11% higher in wall heat flux/Nu than `run007a` when both are normalized with the same reference k.",
        ]
    )
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(md_path.read_text(encoding="utf-8"))
    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
