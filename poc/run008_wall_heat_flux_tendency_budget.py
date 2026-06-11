from __future__ import annotations

import json
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "poc" / "run008_wall_heat_flux_tendency_budget"
FIG_DIR = OUT_DIR / "figures"

CASE_DIR = Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run008")
CASE_WSL_DIR = "/home/hexmachina/of_runs/V4b_3D_run008"
HILBERT_PHASE_FILE = REPO_ROOT / "VV_cases" / "V4b_3D" / "results" / "run008" / "data" / "002" / "run008_002_hilbert_phase.npz"

D = 0.012
R_TUBE = D / 2.0
FIN_Z_MIN = -0.006
FIN_Z_MAX = 0.006
T_WALL = 343.15
C_AIR = 1005.0
MU_AIR = 1.827e-5
PR_AIR = 0.713
K_AIR = C_AIR * MU_AIR / PR_AIR

T_START = 2.0
T_STOP = 10.0
DT = 0.08
PHASE_BINS = 16
BATCH_SIZE = 25

PLOT_REGIONS = ["tube_separation", "tube_junction", "fin_sweep"]


@dataclass
class PatchInfo:
    name: str
    start_face: int
    n_faces: int


@dataclass
class RegionFaceData:
    proc: int
    patch: str
    region: str
    area: float
    distance_n: float
    owner: int
    x: float
    y: float
    z: float


def time_name(value: float) -> str:
    return f"{value:.8f}".rstrip("0").rstrip(".")


def selected_times() -> np.ndarray:
    n = int(round((T_STOP - T_START) / DT))
    return np.asarray([round(T_START + i * DT, 8) for i in range(n + 1)], dtype=float)


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def run_wsl(command: str) -> None:
    subprocess.run(
        ["wsl", "-d", "Ubuntu-24.04", "bash", "-lc", command],
        check=True,
        cwd=str(REPO_ROOT),
    )


def ensure_cell_centres() -> None:
    probe = CASE_DIR / "processor0" / time_name(T_START) / "C"
    if probe.exists():
        return
    cmd = (
        "source /opt/openfoam13/etc/bashrc >/dev/null 2>&1 && "
        f"cd {CASE_WSL_DIR} && "
        "mpirun --oversubscribe -np 20 foamPostProcess -parallel "
        f"-func writeCellCentres -time {time_name(T_START)}"
    )
    run_wsl(cmd)


def ensure_grad_t(times: np.ndarray) -> None:
    missing = [time_name(t) for t in times if not (CASE_DIR / "processor0" / time_name(t) / "grad(T)").exists()]
    if not missing:
        return
    for i in range(0, len(missing), BATCH_SIZE):
        batch = missing[i : i + BATCH_SIZE]
        time_spec = ",".join(batch)
        cmd = (
            "source /opt/openfoam13/etc/bashrc >/dev/null 2>&1 && "
            f"cd {CASE_WSL_DIR} && "
            "mpirun --oversubscribe -np 20 foamPostProcess -parallel "
            f"-func 'grad(T)' -time '{time_spec}'"
        )
        run_wsl(cmd)


def parse_boundary(path: Path) -> dict[str, PatchInfo]:
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(r"(\w+)\s*\{(.*?)\}", re.S)
    patches: dict[str, PatchInfo] = {}
    for name, body in pattern.findall(text):
        start_match = re.search(r"startFace\s+(\d+)\s*;", body)
        n_match = re.search(r"nFaces\s+(\d+)\s*;", body)
        if start_match and n_match:
            patches[name] = PatchInfo(name=name, start_face=int(start_match.group(1)), n_faces=int(n_match.group(1)))
    return patches


def parse_points(path: Path) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\n(\d+)\n\((.*)\)\n", text, re.S)
    if not match:
        raise ValueError(f"Cannot parse points from {path}")
    n_points = int(match.group(1))
    vals = np.fromstring(match.group(2).replace("(", " ").replace(")", " "), sep=" ")
    pts = vals.reshape(-1, 3)
    if len(pts) != n_points:
        raise ValueError(f"Expected {n_points} points in {path}, got {len(pts)}")
    return pts


def parse_faces(path: Path) -> list[np.ndarray]:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\n(\d+)\n\((.*)\)\n", text, re.S)
    if not match:
        raise ValueError(f"Cannot parse faces from {path}")
    n_faces = int(match.group(1))
    body = match.group(2)
    matches = re.findall(r"(\d+)\(([^)]*)\)", body)
    faces = []
    for n_str, inside in matches:
        n = int(n_str)
        ids = np.fromstring(inside, sep=" ", dtype=int)
        if len(ids) != n:
            raise ValueError(f"Face vertex mismatch in {path}")
        faces.append(ids)
    if len(faces) != n_faces:
        raise ValueError(f"Expected {n_faces} faces in {path}, got {len(faces)}")
    return faces


def parse_owner(path: Path) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\n(\d+)\n\((.*)\)\n", text, re.S)
    if not match:
        raise ValueError(f"Cannot parse owner from {path}")
    n = int(match.group(1))
    arr = np.fromstring(match.group(2), sep=" ", dtype=int)
    if len(arr) != n:
        raise ValueError(f"Expected {n} owners in {path}, got {len(arr)}")
    return arr


def parse_internal_field(path: Path, n_comp: int) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    nonuniform = re.search(r"internalField\s+nonuniform\s+List<[^>]+>\s+(\d+)\s*\((.*?)\)\s*;", text, re.S)
    if nonuniform:
        n = int(nonuniform.group(1))
        payload = nonuniform.group(2).replace("(", " ").replace(")", " ")
        arr = np.fromstring(payload, sep=" ")
        if n_comp == 1:
            if len(arr) != n:
                raise ValueError(f"Expected {n} scalar values in {path}, got {len(arr)}")
            return arr
        arr = arr.reshape(-1, n_comp)
        if len(arr) != n:
            raise ValueError(f"Expected {n} vector values in {path}, got {len(arr)}")
        return arr
    uniform = re.search(r"internalField\s+uniform\s+(.+?)\s*;", text, re.S)
    if not uniform:
        raise ValueError(f"Cannot parse internalField from {path}")
    raw = uniform.group(1).strip()
    if n_comp == 1:
        return np.asarray([float(raw)], dtype=float)
    vals = np.fromstring(raw.replace("(", " ").replace(")", " "), sep=" ")
    if len(vals) != n_comp:
        raise ValueError(f"Expected {n_comp} uniform components in {path}, got {len(vals)}")
    return vals.reshape(1, n_comp)


def parse_patch_field(path: Path, patch_name: str) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\n\s*\}}", text, re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found in {path}")
    body = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", body)
    if uniform:
        n_match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)", body)
        if n_match:
            return np.full(int(n_match.group(1)), float(uniform.group(1)))
        raise ValueError(f"Uniform patch value without count in {path}::{patch_name}")
    nonuniform = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", body, re.S)
    if not nonuniform:
        raise ValueError(f"Cannot parse nonuniform patch field in {path}::{patch_name}")
    n = int(nonuniform.group(1))
    arr = np.fromstring(nonuniform.group(2), sep=" ")
    if len(arr) != n:
        raise ValueError(f"Expected {n} patch values in {path}::{patch_name}, got {len(arr)}")
    return arr


def face_center(points: np.ndarray, face: np.ndarray) -> np.ndarray:
    return points[face].mean(axis=0)


def face_area_and_normal(points: np.ndarray, face: np.ndarray) -> tuple[float, np.ndarray]:
    p = points[face]
    ref = p[0]
    area_vec = np.zeros(3)
    for i in range(1, len(p) - 1):
        area_vec += 0.5 * np.cross(p[i] - ref, p[i + 1] - ref)
    area = float(np.linalg.norm(area_vec))
    if area <= 0.0:
        raise ValueError("Degenerate face area")
    return area, area_vec / area


def classify_region(patch: str, center: np.ndarray) -> str | None:
    x, y, z = center
    dist_fin = min(abs(z - FIN_Z_MIN), abs(z - FIN_Z_MAX))
    if patch == "hot_tube":
        if dist_fin < 0.20 * D:
            return "tube_junction"
        if x > 0.25 * D:
            return "tube_rear"
        if 0.35 * D < abs(y) < 1.05 * D:
            return "tube_separation"
        return None
    if patch in {"hot_fin_z_min", "hot_fin_z_max"}:
        if abs(x) < 0.5 * D:
            return "fin_near_tube"
        if x >= 0.5 * D:
            return "fin_sweep"
        if x <= -0.5 * D:
            return "fin_control"
    return None


def build_face_catalog() -> tuple[list[RegionFaceData], pd.DataFrame]:
    ensure_cell_centres()
    rows: list[RegionFaceData] = []
    for proc_dir in sorted(CASE_DIR.glob("processor*"), key=lambda p: int(p.name.replace("processor", ""))):
        proc = int(proc_dir.name.replace("processor", ""))
        patches = parse_boundary(proc_dir / "constant" / "polyMesh" / "boundary")
        points = parse_points(proc_dir / "constant" / "polyMesh" / "points")
        faces = parse_faces(proc_dir / "constant" / "polyMesh" / "faces")
        owner = parse_owner(proc_dir / "constant" / "polyMesh" / "owner")
        cell_centres = parse_internal_field(proc_dir / time_name(T_START) / "C", 3)
        for patch_name in ("hot_tube", "hot_fin_z_min", "hot_fin_z_max"):
            patch = patches[patch_name]
            if patch.n_faces == 0:
                continue
            start = patch.start_face
            end = start + patch.n_faces
            for face_index in range(start, end):
                pts = faces[face_index]
                ctr = face_center(points, pts)
                region = classify_region(patch_name, ctr)
                if region is None:
                    continue
                area, normal = face_area_and_normal(points, pts)
                owner_id = int(owner[face_index])
                cell_ctr = cell_centres[owner_id]
                dn = abs(float(np.dot(ctr - cell_ctr, normal)))
                if dn <= 0.0:
                    continue
                rows.append(
                    RegionFaceData(
                        proc=proc,
                        patch=patch_name,
                        region=region,
                        area=area,
                        distance_n=dn,
                        owner=owner_id,
                        x=float(ctr[0]),
                        y=float(ctr[1]),
                        z=float(ctr[2]),
                    )
                )
    face_df = pd.DataFrame([row.__dict__ for row in rows])
    if face_df.empty:
        raise RuntimeError("No hot-wall faces were catalogued for PoC regions")
    return rows, face_df


def interpolate_phase(times: np.ndarray) -> np.ndarray:
    data = np.load(HILBERT_PHASE_FILE)
    phase = np.unwrap(data["phase_rad"])
    return np.interp(times, data["time"], phase)


def compute_time_series(face_rows: list[RegionFaceData], times: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    n_faces = len(face_rows)
    n_times = len(times)
    q = np.zeros((n_times, n_faces))
    t_owner = np.zeros((n_times, n_faces))
    adv = np.zeros((n_times, n_faces))

    by_proc: dict[int, list[tuple[int, RegionFaceData]]] = {}
    for idx, row in enumerate(face_rows):
        by_proc.setdefault(row.proc, []).append((idx, row))

    for time_idx, t in enumerate(times):
        tdir = time_name(t)
        for proc, items in by_proc.items():
            proc_dir = CASE_DIR / f"processor{proc}" / tdir
            wall_flux_text = proc_dir / "wallHeatFlux"
            temperature_text = proc_dir / "T"
            velocity_text = proc_dir / "U"
            grad_text = proc_dir / "grad(T)"

            t_field = parse_internal_field(temperature_text, 1)
            u_field = parse_internal_field(velocity_text, 3)
            grad_field = parse_internal_field(grad_text, 3)

            patch_cache: dict[str, np.ndarray] = {}
            local_patch_order: dict[str, list[tuple[int, RegionFaceData]]] = {}
            for global_idx, item in items:
                local_patch_order.setdefault(item.patch, []).append((global_idx, item))
            for patch_name, patch_items in local_patch_order.items():
                patch_cache[patch_name] = parse_patch_field(wall_flux_text, patch_name)
                for local_face_idx, (global_idx, item) in enumerate(patch_items):
                    owner_id = item.owner
                    q[time_idx, global_idx] = patch_cache[patch_name][local_face_idx]
                    t_owner[time_idx, global_idx] = t_field[owner_id]
                    adv[time_idx, global_idx] = float(np.dot(u_field[owner_id], grad_field[owner_id]))
        if (time_idx + 1) % 25 == 0 or time_idx + 1 == n_times:
            print(f"processed {time_idx + 1}/{n_times} times")

    d_t_dt = np.gradient(t_owner, DT, axis=0)
    p_q_direct = np.gradient(q, DT, axis=0)
    areas = np.asarray([row.area for row in face_rows], dtype=float)
    d_n = np.asarray([row.distance_n for row in face_rows], dtype=float)
    q_model = K_AIR * (T_WALL - t_owner) / d_n[None, :]
    p_q_model = -(K_AIR / d_n[None, :]) * d_t_dt
    p_adv = (K_AIR / d_n[None, :]) * adv
    p_diff = -(K_AIR / d_n[None, :]) * (d_t_dt + adv)
    closure = p_q_direct - (p_adv + p_diff)
    q_mismatch = q - q_model

    arrays = {
        "q_direct": q,
        "q_model": q_model,
        "q_mismatch": q_mismatch,
        "t_owner": t_owner,
        "adv_scalar": adv,
        "dT_dt": d_t_dt,
        "p_q_direct": p_q_direct,
        "p_q_model": p_q_model,
        "p_adv": p_adv,
        "p_diff": p_diff,
        "closure": closure,
        "area": areas,
        "distance_n": d_n,
    }
    return areas, arrays


def area_weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sum(values * weights) / np.sum(weights))


def build_region_outputs(face_df: pd.DataFrame, times: np.ndarray, phases: np.ndarray, arrays: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    phase_centres = np.linspace(0.0, 2.0 * math.pi, PHASE_BINS, endpoint=False)
    phase_idx = np.floor(((phases % (2.0 * math.pi)) / (2.0 * math.pi)) * PHASE_BINS).astype(int)
    time_rows = []
    summary_rows = []
    phase_rows = []

    for region in sorted(face_df["region"].unique()):
        mask = face_df["region"].to_numpy() == region
        weights = arrays["area"][mask]
        reg = {"region": region, "n_faces": int(mask.sum()), "area_m2": float(np.sum(weights))}

        q_direct_series = np.asarray([area_weighted_mean(arrays["q_direct"][i, mask], weights) for i in range(len(times))])
        q_model_series = np.asarray([area_weighted_mean(arrays["q_model"][i, mask], weights) for i in range(len(times))])
        p_q_series = np.asarray([area_weighted_mean(arrays["p_q_direct"][i, mask], weights) for i in range(len(times))])
        p_adv_series = np.asarray([area_weighted_mean(arrays["p_adv"][i, mask], weights) for i in range(len(times))])
        p_diff_series = np.asarray([area_weighted_mean(arrays["p_diff"][i, mask], weights) for i in range(len(times))])
        closure_series = np.asarray([area_weighted_mean(arrays["closure"][i, mask], weights) for i in range(len(times))])

        for i, t in enumerate(times):
            time_rows.append(
                {
                    "time_s": t,
                    "phase_rad": phases[i],
                    "phase_deg": float(np.degrees(phases[i] % (2.0 * math.pi))),
                    "region": region,
                    "q_direct_wm2": q_direct_series[i],
                    "q_model_wm2": q_model_series[i],
                    "p_q_direct_wm2s": p_q_series[i],
                    "p_adv_wm2s": p_adv_series[i],
                    "p_diff_wm2s": p_diff_series[i],
                    "closure_wm2s": closure_series[i],
                }
            )

        q_rms = float(np.std(q_direct_series))
        p_q_rms = float(np.std(p_q_series))
        p_adv_rms = float(np.std(p_adv_series))
        p_diff_rms = float(np.std(p_diff_series))
        closure_rms = float(np.std(closure_series))
        dominant = "advective" if p_adv_rms > p_diff_rms else "diffusive"
        corr_adv = float(np.corrcoef(p_q_series, p_adv_series)[0, 1])
        corr_diff = float(np.corrcoef(p_q_series, p_diff_series)[0, 1])
        q_mae_pct = float(100.0 * np.mean(np.abs(q_direct_series - q_model_series)) / np.mean(np.abs(q_direct_series)))
        reg.update(
            {
                "q_mean_wm2": float(np.mean(q_direct_series)),
                "q_rms_wm2": q_rms,
                "p_q_rms_wm2s": p_q_rms,
                "p_adv_rms_wm2s": p_adv_rms,
                "p_diff_rms_wm2s": p_diff_rms,
                "closure_rms_wm2s": closure_rms,
                "corr_pq_padv": corr_adv,
                "corr_pq_pdiff": corr_diff,
                "q_model_mae_pct_of_q": q_mae_pct,
                "dominant_rms_term": dominant,
                "tube_or_fin": "tube" if region.startswith("tube_") else "fin",
            }
        )
        summary_rows.append(reg)

        for bin_id, centre in enumerate(phase_centres):
            select = phase_idx == bin_id
            phase_rows.append(
                {
                    "region": region,
                    "phase_bin": bin_id,
                    "phase_center_deg": float(np.degrees(centre)),
                    "q_direct_wm2": float(np.mean(q_direct_series[select])),
                    "p_q_direct_wm2s": float(np.mean(p_q_series[select])),
                    "p_adv_wm2s": float(np.mean(p_adv_series[select])),
                    "p_diff_wm2s": float(np.mean(p_diff_series[select])),
                    "closure_wm2s": float(np.mean(closure_series[select])),
                }
            )

    return pd.DataFrame(time_rows), pd.DataFrame(summary_rows), pd.DataFrame(phase_rows)


def save_plots(summary_df: pd.DataFrame, phase_df: pd.DataFrame) -> None:
    plot_df = phase_df[phase_df["region"].isin(PLOT_REGIONS)]
    fig, axes = plt.subplots(len(PLOT_REGIONS), 1, figsize=(8.6, 9.2), sharex=True)
    if len(PLOT_REGIONS) == 1:
        axes = [axes]
    for ax, region in zip(axes, PLOT_REGIONS):
        sub = plot_df[plot_df["region"] == region].sort_values("phase_center_deg")
        ax.plot(sub["phase_center_deg"], sub["p_q_direct_wm2s"], label="P_q direct", color="#222222", lw=2.0)
        ax.plot(sub["phase_center_deg"], sub["p_adv_wm2s"], label="P_adv est", color="#1f77b4", lw=1.8)
        ax.plot(sub["phase_center_deg"], sub["p_diff_wm2s"], label="P_diff est", color="#d62728", lw=1.8)
        ax.plot(sub["phase_center_deg"], sub["closure_wm2s"], label="closure", color="#7f7f7f", lw=1.2, ls="--")
        ax.axhline(0.0, color="0.4", lw=0.8)
        ax.set_ylabel("W m$^{-2}$ s$^{-1}$")
        ax.set_title(region.replace("_", " "))
    axes[-1].set_xlabel("Cl phase [deg]")
    axes[0].legend(loc="upper right", ncol=4, frameon=False)
    fig.suptitle("Local wall-heat-flux tendency budget PoC: phase-averaged region terms", y=0.995)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_budget_phase_regions.png", dpi=220)
    plt.close(fig)

    summary_order = summary_df.sort_values(["tube_or_fin", "region"]).reset_index(drop=True)
    x = np.arange(len(summary_order))
    width = 0.24
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.bar(x - width, summary_order["p_q_rms_wm2s"], width=width, label="P_q direct RMS", color="#222222")
    ax.bar(x, summary_order["p_adv_rms_wm2s"], width=width, label="P_adv RMS", color="#1f77b4")
    ax.bar(x + width, summary_order["p_diff_rms_wm2s"], width=width, label="P_diff RMS", color="#d62728")
    ax.set_xticks(x)
    ax.set_xticklabels([name.replace("_", "\n") for name in summary_order["region"]], fontsize=9)
    ax.set_ylabel("RMS [W m$^{-2}$ s$^{-1}$]")
    ax.set_title("run008 PoC budget term strength by wall region")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_budget_rms_summary.png", dpi=220)
    plt.close(fig)


def write_report(face_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    top = summary_df.sort_values("p_q_rms_wm2s", ascending=False)
    lines = [
        "# Wall-Heat-Flux Tendency Budget PoC",
        "",
        "Case: `V4b_3D run008`",
        "",
        "## What this PoC computes",
        "",
        "This is a near-wall first-cell estimate, not the final publication-grade",
        "normal-derivative budget. For each selected hot-wall face we use:",
        "",
        "- direct local `q''(t)` from the OpenFOAM `wallHeatFlux` boundary field,",
        "- owner-cell `T`, `U`, and `grad(T)`,",
        "- face-to-owner normal distance `d_n`,",
        "- the constant-property `run008` conductivity `k = Cp * mu / Pr`.",
        "",
        "The local first-cell closure used here is:",
        "",
        "- `q''_model ~= k (T_wall - T_P) / d_n`",
        "- `P_q_model = d q''_model / dt ~= -(k/d_n) dT_P/dt`",
        "- `P_adv_est ~= (k/d_n) (u . grad T)_P`",
        "- `P_diff_est ~= -(k/d_n) (dT_P/dt + (u . grad T)_P)`",
        "",
        "The most honest comparison quantity is therefore the direct boundary-field tendency",
        "`P_q_direct = d q''/dt` together with the residual closure",
        "`P_q_direct - (P_adv_est + P_diff_est)`.",
        "",
        "## Region inventory",
        "",
        f"- analysed faces: `{len(face_df)}`",
        f"- analysed regions: `{', '.join(sorted(summary_df['region'].unique()))}`",
        "",
        "## RMS summary",
        "",
        "| region | n_faces | q_mean [W/m2] | RMS(P_q) | RMS(P_adv) | RMS(P_diff) | RMS(closure) | corr(P_q,P_adv) | corr(P_q,P_diff) | dominant | q_model MAE [%q] |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for _, row in summary_df.sort_values(["tube_or_fin", "region"]).iterrows():
        lines.append(
            f"| `{row['region']}` | {int(row['n_faces'])} | {row['q_mean_wm2']:.2f} | "
            f"{row['p_q_rms_wm2s']:.2f} | {row['p_adv_rms_wm2s']:.2f} | {row['p_diff_rms_wm2s']:.2f} | "
            f"{row['closure_rms_wm2s']:.2f} | {row['corr_pq_padv']:.3f} | {row['corr_pq_pdiff']:.3f} | "
            f"{row['dominant_rms_term']} | {row['q_model_mae_pct_of_q']:.2f} |"
        )
    lines += [
        "",
        "## First reading",
        "",
        f"- strongest direct tendency RMS region: `{top.iloc[0]['region']}`",
        f"- weakest direct tendency RMS region: `{top.iloc[-1]['region']}`",
        "- `tube_*` regions indicate tube-wall production zones.",
        "- `fin_*` regions indicate fin-wall production zones aggregated over both fin sides.",
        "",
        "## Limits",
        "",
        "- This is not yet the exact wall-normal derivative form `k d_n(u.gradT) - k alpha d_n(laplacianT)`.",
        "- `P_diff_est` is obtained from the first-cell energy balance, not from an independently differentiated wall-normal Laplacian.",
        "- The closure column tells us how far the first-cell estimate is from the direct `wallHeatFlux` tendency.",
        "- A publication-grade extension should repeat this with explicit near-wall gradient reconstruction and grid/time sensitivity of the budget itself.",
        "",
        "## Figures",
        "",
        "- `figures/run008_budget_phase_regions.png`",
        "- `figures/run008_budget_rms_summary.png`",
        "",
        "Figure title candidate:",
        "",
        "`Local wall-heat-flux tendency budget: where the wall gradient is produced, not where vortices are visible.`",
    ]
    (OUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    times = selected_times()
    ensure_grad_t(times)
    face_rows, face_df = build_face_catalog()
    areas, arrays = compute_time_series(face_rows, times)
    phases = interpolate_phase(times)
    time_df, summary_df, phase_df = build_region_outputs(face_df, times, phases, arrays)

    face_df.to_csv(OUT_DIR / "run008_budget_face_catalog.csv", index=False, float_format="%.10g")
    time_df.to_csv(OUT_DIR / "run008_budget_region_timeseries.csv", index=False, float_format="%.10g")
    summary_df.to_csv(OUT_DIR / "run008_budget_region_summary.csv", index=False, float_format="%.10g")
    phase_df.to_csv(OUT_DIR / "run008_budget_region_phase_average.csv", index=False, float_format="%.10g")
    np.savez_compressed(
        OUT_DIR / "run008_budget_raw_arrays.npz",
        time_s=times,
        phase_rad=phases,
        **arrays,
    )
    metadata = {
        "case_dir": str(CASE_DIR),
        "t_start_s": T_START,
        "t_stop_s": T_STOP,
        "dt_s": DT,
        "n_times": int(len(times)),
        "conductivity_wmk": K_AIR,
        "wall_temperature_k": T_WALL,
        "phase_bins": PHASE_BINS,
        "method": "near-wall first-cell estimate with direct wallHeatFlux comparison",
    }
    (OUT_DIR / "run008_budget_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    save_plots(summary_df, phase_df)
    write_report(face_df, summary_df)
    print((OUT_DIR / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
