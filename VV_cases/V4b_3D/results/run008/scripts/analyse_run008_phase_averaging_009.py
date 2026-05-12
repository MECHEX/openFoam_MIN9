"""
Run008 phase-averaging layer: shedding phase as the physical story.

Layer 009:
- define shedding phase phi(t) from Cl Hilbert phase,
- phase-average Cl, Cd, Q_tube, Q_fins, Nu(theta,z), Nu_local(x),
- phase-average midspan wake fields U and T,
- identify phases of max/min lift, zero crossings, and heat-transfer maxima,
- produce article-ready grids showing wake-to-local-Nu evolution.
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


RUN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = RUN_DIR / "data" / "009"
FIG_DIR = RUN_DIR / "figures" / "009"

WINDOW = (2.0, 10.0)
N_PHASE = 16
F_SHED = 3.2787
D = 0.012


@dataclass
class PhaseEvent:
    event: str
    phase_bin: int
    phase_deg: float
    value: float
    lag_from_abs_cl_max_deg: float
    lag_from_abs_cl_max_s: float


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def resolve_case_dir() -> Path:
    candidates = [
        Path("/home/hexmachina/of_runs/V4b_3D_run008"),
        Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run008"),
        Path(r"\\wsl$\Ubuntu\home\hexmachina\of_runs\V4b_3D_run008"),
    ]
    for path in candidates:
        if (path / "postProcessing").exists():
            return path
    raise FileNotFoundError("Cannot find V4b_3D_run008 postProcessing via /home or WSL UNC paths")


CASE_DIR = resolve_case_dir()
POST_DIR = CASE_DIR / "postProcessing"
MIDSPAN_DIR = POST_DIR / "midspan_z0"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv_cols(path: Path) -> dict[str, np.ndarray]:
    cols: dict[str, list[float]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key, value in row.items():
                cols.setdefault(key, []).append(float(value))
    return {k: np.asarray(v, dtype=float) for k, v in cols.items()}


def read_force_coeffs() -> dict[str, np.ndarray]:
    rows = []
    with (POST_DIR / "forceCoeffs" / "0" / "forceCoeffs.dat").open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            vals = [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", stripped)]
            if len(vals) >= 5:
                rows.append(vals)
    arr = np.asarray(rows, dtype=float)
    mask = (arr[:, 0] >= WINDOW[0] - 1e-12) & (arr[:, 0] <= WINDOW[1] + 1e-12)
    arr = arr[mask]
    return {"time": arr[:, 0], "Cd": arr[:, 2], "Cl": arr[:, 3], "Cm": arr[:, 4]}


def load_phase(time: np.ndarray) -> np.ndarray:
    data = np.load(RUN_DIR / "data" / "002" / "run008_002_hilbert_phase.npz")
    src_t = np.asarray(data["time"], dtype=float)
    src_phi = np.unwrap(np.asarray(data["phase_rad"], dtype=float))
    return np.mod(np.interp(time, src_t, src_phi), 2 * np.pi)


def phase_bins(phi: np.ndarray, n_phase: int = N_PHASE) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    edges = np.linspace(0.0, 2.0 * np.pi, n_phase + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    idx = np.floor((np.mod(phi, 2.0 * np.pi) / (2.0 * np.pi)) * n_phase).astype(int) % n_phase
    return idx, edges, centers


def phase_average_1d(phi_idx: np.ndarray, values: np.ndarray, n_phase: int = N_PHASE) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    out = np.full(n_phase, np.nan)
    std = np.full(n_phase, np.nan)
    count = np.zeros(n_phase, dtype=int)
    for i in range(n_phase):
        m = (phi_idx == i) & np.isfinite(values)
        count[i] = int(np.sum(m))
        if count[i]:
            out[i] = float(np.mean(values[m]))
            std[i] = float(np.std(values[m], ddof=1)) if count[i] > 1 else 0.0
    return out, std, count


def phase_average_matrix(phi_idx: np.ndarray, matrix: np.ndarray, n_phase: int = N_PHASE) -> tuple[np.ndarray, np.ndarray]:
    out = np.full((n_phase, matrix.shape[1]), np.nan)
    count = np.zeros(n_phase, dtype=int)
    for i in range(n_phase):
        m = phi_idx == i
        count[i] = int(np.sum(m))
        if count[i]:
            out[i] = np.nanmean(matrix[m], axis=0)
    return out, count


def cyclic_delta_deg(a_deg: float, b_deg: float) -> float:
    return ((a_deg - b_deg + 180.0) % 360.0) - 180.0


def phase_lag_s(delta_deg: float) -> float:
    return (delta_deg / 360.0) / F_SHED


def list_midspan_times() -> np.ndarray:
    times = []
    for path in MIDSPAN_DIR.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if WINDOW[0] - 1e-12 <= t <= WINDOW[1] + 1e-12 and (path / "z0.vtk").exists():
            times.append(t)
    return np.asarray(sorted(times), dtype=float)


def read_midspan_vtk(time_value: float, read_points: bool = False) -> tuple[np.ndarray | None, np.ndarray, np.ndarray]:
    text = (MIDSPAN_DIR / f"{time_value:g}" / "z0.vtk").read_text(encoding="utf-8", errors="replace")
    match = re.search(r"POINTS\s+(\d+)\s+\w+\s+(.*?)\nPOLYGONS", text, flags=re.S)
    if not match:
        raise ValueError(f"Could not parse POINTS at {time_value:g}")
    n_points = int(match.group(1))
    points = None
    if read_points:
        points = np.fromstring(match.group(2), sep=" ").reshape((-1, 3))
        if len(points) != n_points:
            raise ValueError(f"Expected {n_points} points, got {len(points)}")
    t_match = re.search(r"\nT\s+1\s+(\d+)\s+float\s+(.*?)\n[A-Za-z_][A-Za-z0-9_]*\s+\d+", text, flags=re.S)
    if not t_match:
        raise ValueError(f"Could not parse T at {time_value:g}")
    temp = np.fromstring(t_match.group(2), sep=" ", count=int(t_match.group(1)))
    u_match = re.search(r"\nU\s+3\s+(\d+)\s+float\s+(.*)", text, flags=re.S)
    if not u_match:
        raise ValueError(f"Could not parse U at {time_value:g}")
    vel = np.fromstring(u_match.group(2), sep=" ", count=3 * int(u_match.group(1))).reshape((-1, 3))
    return points, temp, vel


def load_midspan_phase_averages(force_time: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    times = list_midspan_times()
    points, temp0, vel0 = read_midspan_vtk(float(times[0]), read_points=True)
    assert points is not None
    phi = load_phase(times)
    idx, _, _ = phase_bins(phi)
    n_points = len(points)
    ux_sum = np.zeros((N_PHASE, n_points), dtype=float)
    uy_sum = np.zeros((N_PHASE, n_points), dtype=float)
    t_sum = np.zeros((N_PHASE, n_points), dtype=float)
    counts = np.zeros(N_PHASE, dtype=int)
    for t in times:
        _, temp, vel = read_midspan_vtk(float(t), read_points=False)
        b = int(phase_bins(load_phase(np.asarray([t]))[0:1])[0][0])
        ux_sum[b] += vel[:, 0]
        uy_sum[b] += vel[:, 1]
        t_sum[b] += temp
        counts[b] += 1
    ux = np.divide(ux_sum, counts[:, None], out=np.full_like(ux_sum, np.nan), where=counts[:, None] > 0)
    uy = np.divide(uy_sum, counts[:, None], out=np.full_like(uy_sum, np.nan), where=counts[:, None] > 0)
    temp = np.divide(t_sum, counts[:, None], out=np.full_like(t_sum, np.nan), where=counts[:, None] > 0)
    return times, points, ux, uy, temp


def load_tube_phase_average_16() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    data = np.load(RUN_DIR / "data" / "004" / "run008_004_tube_nu_arrays.npz")
    phase32 = np.asarray(data["phase_average"], dtype=float)
    # Existing layer 004 used 32 bins. Merge pairs to align with this 16-bin story.
    phase16 = np.nanmean(phase32.reshape(N_PHASE, 2, phase32.shape[1], phase32.shape[2]), axis=1)
    return data["theta_centers"], data["z_centers"], data["phase_centers"][::2], phase16


def load_fin_phase_average_16(force_time: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, np.ndarray]]:
    data = np.load(RUN_DIR / "data" / "005" / "run008_005_fin_nu_arrays.npz")
    time = np.asarray(data["times"], dtype=float)
    phi = load_phase(time)
    idx, _, _ = phase_bins(phi)
    min_avg, count_min = phase_average_matrix(idx, np.asarray(data["min_series"], dtype=float))
    max_avg, count_max = phase_average_matrix(idx, np.asarray(data["max_series"], dtype=float))
    return data["x_centers"], {"fin_z_min": min_avg, "fin_z_max": max_avg}, {"fin_z_min": count_min, "fin_z_max": count_max}


def plot_global_cycle(phase_deg: np.ndarray, global_rows: list[dict[str, object]], events: list[PhaseEvent]) -> None:
    cols = {k: np.asarray([float(r[k]) for r in global_rows]) for k in global_rows[0] if k not in {"phase_bin"}}
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    axes[0].plot(phase_deg, cols["Cl"], marker="o", label="Cl")
    axes[0].plot(phase_deg, cols["Cd"], marker="s", label="Cd")
    axes[0].set_ylabel("coefficient")
    axes[0].legend()
    axes[0].set_title("Phase-averaged force and heat-transfer cycle")
    axes[1].plot(phase_deg, cols["Q_tube"], marker="o", label="Q_tube")
    axes[1].plot(phase_deg, cols["Q_fins"], marker="o", label="Q_fins")
    axes[1].plot(phase_deg, cols["Q_wall"], marker="o", label="Q_wall")
    axes[1].set_ylabel("Q [W]")
    axes[1].legend()
    axes[2].plot(phase_deg, cols["Nu_tube_wall"], marker="o", label="Nu_tube_wall")
    axes[2].plot(phase_deg, cols["Nu_fins_wall"], marker="o", label="Nu_fins_wall")
    axes[2].plot(phase_deg, cols["Nu_EB"], marker="o", label="Nu_EB")
    axes[2].set_ylabel("Nu")
    axes[2].set_xlabel("shedding phase from Cl [deg]")
    axes[2].legend()
    for ax in axes:
        ax.grid(True, alpha=0.25)
        for event in events:
            if event.event in {"Cl_max", "Cl_min", "Cl_zero_up", "Cl_zero_down", "Q_wall_max"}:
                ax.axvline(event.phase_deg, color="0.55", lw=0.8, ls="--", alpha=0.6)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_009_phase_global_cycle.png", dpi=180)
    plt.close(fig)


def plot_tube_phase_grid(theta: np.ndarray, z: np.ndarray, phase_deg: np.ndarray, tube_phase: np.ndarray) -> None:
    fig, axes = plt.subplots(4, 4, figsize=(14, 9), sharex=True, sharey=True)
    vmin, vmax = np.nanpercentile(tube_phase, [2, 98])
    theta_deg = np.degrees(theta)
    for i, ax in enumerate(axes.ravel()):
        im = ax.pcolormesh(theta_deg, z * 1000.0, tube_phase[i], shading="auto", cmap="magma", vmin=vmin, vmax=vmax)
        ax.set_title(f"phi={phase_deg[i]:.0f} deg")
        if i % 4 == 0:
            ax.set_ylabel("z [mm]")
        if i >= 12:
            ax.set_xlabel("theta [deg]")
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.84, label="Nu(theta,z)")
    fig.suptitle("Phase-averaged tube Nu(theta,z)")
    fig.savefig(FIG_DIR / "run008_009_tube_nu_phase_grid.png", dpi=180)
    plt.close(fig)


def plot_fin_phase_grid(x: np.ndarray, phase_deg: np.ndarray, fin_phase: dict[str, np.ndarray]) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    x_mm = x * 1000.0
    for ax, side in zip(axes, ["fin_z_min", "fin_z_max"]):
        im = ax.pcolormesh(x_mm, phase_deg, fin_phase[side], shading="auto", cmap="magma")
        ax.set_ylabel("phase [deg]")
        ax.set_title(f"Phase-averaged Nu_local(x): {side}")
        fig.colorbar(im, ax=ax, label="Nu_local")
    axes[-1].set_xlabel("x [mm]")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_009_fin_nu_phase_map.png", dpi=180)
    plt.close(fig)


def plot_wake_phase_grid(points: np.ndarray, ux: np.ndarray, uy: np.ndarray, temp: np.ndarray, phase_deg: np.ndarray) -> None:
    x_mm = points[:, 0] * 1000.0
    y_mm = points[:, 1] * 1000.0
    speed = np.sqrt(ux**2 + uy**2)
    temp_fluc = temp - np.nanmean(temp, axis=0)[None, :]
    fig, axes = plt.subplots(4, 4, figsize=(14, 10), sharex=True, sharey=True)
    vmin, vmax = np.nanpercentile(speed, [2, 98])
    stride = max(1, len(x_mm) // 7000)
    for i, ax in enumerate(axes.ravel()):
        im = ax.scatter(x_mm[::stride], y_mm[::stride], c=speed[i, ::stride], s=1.0, cmap="viridis", vmin=vmin, vmax=vmax, rasterized=True)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(f"phi={phase_deg[i]:.0f} deg")
        if i % 4 == 0:
            ax.set_ylabel("y [mm]")
        if i >= 12:
            ax.set_xlabel("x [mm]")
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.84, label="|U| [m/s]")
    fig.suptitle("Phase-averaged midspan wake speed")
    fig.savefig(FIG_DIR / "run008_009_midspan_wake_speed_phase_grid.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(4, 4, figsize=(14, 10), sharex=True, sharey=True)
    lim = float(np.nanpercentile(np.abs(temp_fluc), 98))
    for i, ax in enumerate(axes.ravel()):
        im = ax.scatter(x_mm[::stride], y_mm[::stride], c=temp_fluc[i, ::stride], s=1.0, cmap="coolwarm", vmin=-lim, vmax=lim, rasterized=True)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(f"phi={phase_deg[i]:.0f} deg")
        if i % 4 == 0:
            ax.set_ylabel("y [mm]")
        if i >= 12:
            ax.set_xlabel("x [mm]")
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.84, label="T phase - mean [K]")
    fig.suptitle("Phase-averaged midspan temperature fluctuation")
    fig.savefig(FIG_DIR / "run008_009_midspan_temperature_phase_grid.png", dpi=180)
    plt.close(fig)


def plot_story_frames(points: np.ndarray, ux: np.ndarray, uy: np.ndarray, temp: np.ndarray, theta: np.ndarray, z: np.ndarray, tube_phase: np.ndarray, phase_deg: np.ndarray, event_bins: list[int]) -> None:
    x_mm = points[:, 0] * 1000.0
    y_mm = points[:, 1] * 1000.0
    speed = np.sqrt(ux**2 + uy**2)
    stride = max(1, len(x_mm) // 7000)
    fig, axes = plt.subplots(len(event_bins), 2, figsize=(11, 3.1 * len(event_bins)))
    if len(event_bins) == 1:
        axes = np.asarray([axes])
    speed_limits = np.nanpercentile(speed, [2, 98])
    nu_limits = np.nanpercentile(tube_phase, [2, 98])
    for row, b in enumerate(event_bins):
        ax = axes[row, 0]
        im0 = ax.scatter(x_mm[::stride], y_mm[::stride], c=speed[b, ::stride], s=1.0, cmap="viridis", vmin=speed_limits[0], vmax=speed_limits[1], rasterized=True)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(f"wake |U|, phi={phase_deg[b]:.0f} deg")
        ax.set_ylabel("y [mm]")
        ax = axes[row, 1]
        im1 = ax.pcolormesh(np.degrees(theta), z * 1000.0, tube_phase[b], shading="auto", cmap="magma", vmin=nu_limits[0], vmax=nu_limits[1])
        ax.set_title(f"tube Nu, phi={phase_deg[b]:.0f} deg")
        ax.set_ylabel("z [mm]")
    axes[-1, 0].set_xlabel("x [mm]")
    axes[-1, 1].set_xlabel("theta [deg]")
    fig.colorbar(im0, ax=axes[:, 0], shrink=0.78, label="|U| [m/s]")
    fig.colorbar(im1, ax=axes[:, 1], shrink=0.78, label="Nu")
    fig.suptitle("Phase story frames: wake mode and local tube Nu")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_009_phase_story_key_frames.png", dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    force = read_force_coeffs()
    time = force["time"]
    phase = load_phase(time)
    idx, _, centers = phase_bins(phase)
    phase_deg = np.degrees(centers)

    heat = read_csv_cols(RUN_DIR / "data" / "003" / "run008_003_heat_balance_timeseries.csv")
    signals = {
        "Cl": force["Cl"],
        "Cd": force["Cd"],
        "Cm": force["Cm"],
        "Q_wall": np.interp(time, heat["time"], heat["Q_wall"]),
        "Q_tube": np.interp(time, heat["time"], heat["Q_tube"]),
        "Q_fins": np.interp(time, heat["time"], heat["Q_fins"]),
        "Nu_tube_wall": np.interp(time, heat["time"], heat["Nu_tube_wall"]),
        "Nu_fins_wall": np.interp(time, heat["time"], heat["Nu_fins_wall"]),
        "Nu_EB": np.interp(time, heat["time"], heat["Nu_EB"]),
    }

    avg: dict[str, np.ndarray] = {}
    std: dict[str, np.ndarray] = {}
    counts = None
    for name, vals in signals.items():
        avg[name], std[name], counts = phase_average_1d(idx, vals)
    assert counts is not None

    global_rows = []
    for i, ph in enumerate(phase_deg):
        row: dict[str, object] = {"phase_bin": i, "phase_deg": float(ph), "count": int(counts[i])}
        for name in signals:
            row[name] = float(avg[name][i])
            row[f"{name}_std"] = float(std[name][i])
        global_rows.append(row)
    write_csv(DATA_DIR / "run008_009_phase_global_cycle.csv", global_rows)

    # Events and answer to heat-vs-lift timing.
    cl = avg["Cl"]
    abs_cl = np.abs(cl - np.nanmean(cl))
    abs_cl_bin = int(np.nanargmax(abs_cl))
    abs_cl_phase = phase_deg[abs_cl_bin]
    events: list[PhaseEvent] = []

    def add_event(name: str, bin_id: int, value: float) -> None:
        delta = cyclic_delta_deg(float(phase_deg[bin_id]), float(abs_cl_phase))
        events.append(PhaseEvent(name, int(bin_id), float(phase_deg[bin_id]), float(value), delta, phase_lag_s(delta)))

    add_event("Cl_max", int(np.nanargmax(cl)), float(np.nanmax(cl)))
    add_event("Cl_min", int(np.nanargmin(cl)), float(np.nanmin(cl)))
    cl_center = float(np.nanmean(cl))
    cl0 = cl - cl_center
    for b in range(N_PHASE):
        nb = (b + 1) % N_PHASE
        if not (np.isfinite(cl0[b]) and np.isfinite(cl0[nb])):
            continue
        if cl0[b] == 0.0 or cl0[b] * cl0[nb] <= 0.0:
            slope = cl0[nb] - cl0[b]
            chosen = b if abs(cl0[b]) <= abs(cl0[nb]) else nb
            if slope >= 0 and not any(e.event == "Cl_zero_up" for e in events):
                add_event("Cl_zero_up", int(chosen), float(cl[chosen]))
            if slope < 0 and not any(e.event == "Cl_zero_down" for e in events):
                add_event("Cl_zero_down", int(chosen), float(cl[chosen]))
    for name in ["Q_wall", "Q_tube", "Q_fins", "Nu_tube_wall", "Nu_fins_wall", "Nu_EB"]:
        b = int(np.nanargmax(avg[name]))
        add_event(f"{name}_max", b, float(avg[name][b]))
    write_csv(DATA_DIR / "run008_009_phase_events.csv", [asdict(e) for e in events])

    theta, z, _, tube_phase = load_tube_phase_average_16()
    x, fin_phase, fin_counts = load_fin_phase_average_16(time)
    write_csv(
        DATA_DIR / "run008_009_fin_phase_profiles.csv",
        [
            {
                "phase_bin": p,
                "phase_deg": float(phase_deg[p]),
                "x_m": float(x[j]),
                "x_mm": float(1000.0 * x[j]),
                "Nu_fin_z_min": float(fin_phase["fin_z_min"][p, j]),
                "Nu_fin_z_max": float(fin_phase["fin_z_max"][p, j]),
            }
            for p in range(N_PHASE)
            for j in range(len(x))
        ],
    )

    mid_times, points, ux, uy, temp = load_midspan_phase_averages(time)
    speed = np.sqrt(ux**2 + uy**2)
    mid_rows = []
    for i, ph in enumerate(phase_deg):
        mid_rows.append(
            {
                "phase_bin": i,
                "phase_deg": float(ph),
                "midspan_speed_mean": float(np.nanmean(speed[i])),
                "midspan_speed_max": float(np.nanmax(speed[i])),
                "midspan_T_mean": float(np.nanmean(temp[i])),
                "midspan_T_max": float(np.nanmax(temp[i])),
            }
        )
    write_csv(DATA_DIR / "run008_009_midspan_phase_summary.csv", mid_rows)

    np.savez_compressed(
        DATA_DIR / "run008_009_phase_arrays.npz",
        phase_centers=centers,
        phase_deg=phase_deg,
        theta_centers=theta,
        z_centers=z,
        tube_nu_phase=tube_phase,
        fin_x=x,
        fin_z_min_phase=fin_phase["fin_z_min"],
        fin_z_max_phase=fin_phase["fin_z_max"],
        midspan_points=points,
        midspan_ux_phase=ux,
        midspan_uy_phase=uy,
        midspan_T_phase=temp,
    )

    plot_global_cycle(phase_deg, global_rows, events)
    plot_tube_phase_grid(theta, z, phase_deg, tube_phase)
    plot_fin_phase_grid(x, phase_deg, fin_phase)
    plot_wake_phase_grid(points, ux, uy, temp, phase_deg)

    key_names = ["Cl_max", "Cl_min", "Cl_zero_up", "Cl_zero_down", "Q_wall_max"]
    event_bins = []
    for name in key_names:
        match = next((e for e in events if e.event == name), None)
        if match is not None and match.phase_bin not in event_bins:
            event_bins.append(match.phase_bin)
    plot_story_frames(points, ux, uy, temp, theta, z, tube_phase, phase_deg, event_bins)

    event_lookup = {e.event: e for e in events}
    q_wall_event = event_lookup["Q_wall_max"]
    q_tube_event = event_lookup["Q_tube_max"]
    q_fins_event = event_lookup["Q_fins_max"]
    cl_max_event = event_lookup["Cl_max"]
    cl_min_event = event_lookup["Cl_min"]
    abs_cl_event_phase = abs_cl_phase
    heat_answer = {
        "abs_cl_reference_phase_deg": float(abs_cl_event_phase),
        "Q_wall_max_phase_deg": q_wall_event.phase_deg,
        "Q_wall_lag_from_abs_cl_max_deg": q_wall_event.lag_from_abs_cl_max_deg,
        "Q_wall_lag_from_abs_cl_max_s": q_wall_event.lag_from_abs_cl_max_s,
        "Q_tube_lag_from_abs_cl_max_s": q_tube_event.lag_from_abs_cl_max_s,
        "Q_fins_lag_from_abs_cl_max_s": q_fins_event.lag_from_abs_cl_max_s,
    }
    summary = {
        "method": {
            "phase_source": "Cl Hilbert phase from layer 002",
            "window_s": WINDOW,
            "n_phase_bins": N_PHASE,
            "midspan_snapshots": int(len(mid_times)),
            "case_dir": str(CASE_DIR),
        },
        "events": [asdict(e) for e in events],
        "heat_timing_answer": heat_answer,
    }
    (DATA_DIR / "run008_009_phase_averaging_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# V4b_3D run008 phase-averaging physical story",
        "",
        "Phase is defined from the Hilbert analytic signal of `Cl` from layer 002. The production window `t=2..10 s` is binned into 16 shedding-phase bins.",
        "",
        "## Key phase events",
        "",
        "| event | phase bin | phase [deg] | value | lag from max abs(Cl) [deg] | lag [s] |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for e in events:
        lines.append(
            f"| {e.event} | {e.phase_bin} | {e.phase_deg:.1f} | {e.value:.6g} | "
            f"{e.lag_from_abs_cl_max_deg:+.1f} | {e.lag_from_abs_cl_max_s:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Heat-transfer timing",
            "",
            f"- Reference phase for maximum `|Cl|`: `{abs_cl_event_phase:.1f} deg`.",
            f"- `Q_wall` maximum phase: `{q_wall_event.phase_deg:.1f} deg`, lag `{q_wall_event.lag_from_abs_cl_max_deg:+.1f} deg` / `{q_wall_event.lag_from_abs_cl_max_s:+.4f} s`.",
            f"- `Q_tube` maximum lag from maximum `|Cl|`: `{q_tube_event.lag_from_abs_cl_max_deg:+.1f} deg` / `{q_tube_event.lag_from_abs_cl_max_s:+.4f} s`.",
            f"- `Q_fins` maximum lag from maximum `|Cl|`: `{q_fins_event.lag_from_abs_cl_max_deg:+.1f} deg` / `{q_fins_event.lag_from_abs_cl_max_s:+.4f} s`.",
            "",
            "Interpretation: maxima of integrated heat uptake are phase-locked to the shedding cycle, but they should be read relative to the local Nu maps because tube and fins redistribute heat-transfer intensity differently around the cycle.",
            "",
            "## Outputs",
            "",
            "- `run008_009_phase_global_cycle.csv`",
            "- `run008_009_phase_events.csv`",
            "- `run008_009_fin_phase_profiles.csv`",
            "- `run008_009_midspan_phase_summary.csv`",
            "- `run008_009_phase_arrays.npz`",
            "",
            "## Figures",
            "",
            "- `../../figures/009/run008_009_phase_global_cycle.png`",
            "- `../../figures/009/run008_009_tube_nu_phase_grid.png`",
            "- `../../figures/009/run008_009_fin_nu_phase_map.png`",
            "- `../../figures/009/run008_009_midspan_wake_speed_phase_grid.png`",
            "- `../../figures/009/run008_009_midspan_temperature_phase_grid.png`",
            "- `../../figures/009/run008_009_phase_story_key_frames.png`",
        ]
    )
    report = DATA_DIR / "run008_009_phase_averaging_analysis.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
