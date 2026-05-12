"""
Run008 modal analysis: POD, SPOD-like harmonic modes, and DMD.

Layer 006:
- POD for U, T, and scaled joint U+T on midspan_z0,
- modal coefficient phase portraits and correlations with force/thermal signals,
- EPOD/regression fields conditioned on Cl, Q_wall, Nu_tube,
- single-frequency coherent modes at f_shed and 2*f_shed,
- reduced exact DMD sanity check.
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
DATA_DIR = RUN_DIR / "data" / "006"
FIG_DIR = RUN_DIR / "figures" / "006"
CASE_DIR = Path("/home/hexmachina/of_runs/V4b_3D_run008")
POST_DIR = CASE_DIR / "postProcessing"
MIDSPAN_DIR = POST_DIR / "midspan_z0"

WINDOW = (2.0, 10.0)
F_SHED = 3.2787
DMD_RANK = 24
N_PLOT_POINTS = 13524


@dataclass
class ModalSummary:
    metric: str
    value: float


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def list_times() -> np.ndarray:
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


def read_vtk(time_value: float, read_points: bool = False) -> tuple[np.ndarray | None, np.ndarray, np.ndarray]:
    text = (MIDSPAN_DIR / f"{time_value:g}" / "z0.vtk").read_text(encoding="utf-8", errors="replace")
    points = None
    match = re.search(r"POINTS\s+(\d+)\s+\w+\s+(.*?)\nPOLYGONS", text, flags=re.S)
    if not match:
        raise ValueError(f"Could not parse POINTS at {time_value:g}")
    n_points = int(match.group(1))
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


def load_midspan() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    times = list_times()
    points, temp0, vel0 = read_vtk(float(times[0]), read_points=True)
    assert points is not None
    n_points = len(points)
    t_mat = np.empty((n_points, len(times)), dtype=np.float64)
    u_mat = np.empty((2 * n_points, len(times)), dtype=np.float64)
    for j, t in enumerate(times):
        _, temp, vel = read_vtk(float(t), read_points=False)
        t_mat[:, j] = temp
        u_mat[:n_points, j] = vel[:, 0]
        u_mat[n_points:, j] = vel[:, 1]
    return times, points, u_mat, t_mat


def read_force_coeffs(times: np.ndarray) -> dict[str, np.ndarray]:
    rows = []
    with (POST_DIR / "forceCoeffs" / "0" / "forceCoeffs.dat").open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            vals = [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", stripped)]
            if len(vals) >= 4:
                rows.append(vals)
    arr = np.asarray(rows)
    return {
        "Cd": np.interp(times, arr[:, 0], arr[:, 2]),
        "Cl": np.interp(times, arr[:, 0], arr[:, 3]),
    }


def read_heat_signals(times: np.ndarray) -> dict[str, np.ndarray]:
    path = RUN_DIR / "data" / "003" / "run008_003_heat_balance_timeseries.csv"
    cols: dict[str, list[float]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key, value in row.items():
                cols.setdefault(key, []).append(float(value))
    t = np.asarray(cols["time"])
    return {
        "Q_wall": np.interp(times, t, np.asarray(cols["Q_wall"])),
        "Nu_tube": np.interp(times, t, np.asarray(cols["Nu_tube_wall"])),
        "Nu_fins": np.interp(times, t, np.asarray(cols["Nu_fins_wall"])),
    }


def snapshot_pod(x: np.ndarray, n_modes: int = 8) -> dict[str, np.ndarray]:
    mean = np.mean(x, axis=1, keepdims=True)
    xp = x - mean
    u, s, vt = np.linalg.svd(xp, full_matrices=False)
    energy = s**2 / np.sum(s**2)
    coeff = np.diag(s[:n_modes]) @ vt[:n_modes, :]
    return {
        "mean": mean[:, 0],
        "modes": u[:, :n_modes],
        "singular_values": s,
        "energy": energy,
        "coeff": coeff,
        "fluct": xp,
    }


def normalize_joint(u_mat: np.ndarray, t_mat: np.ndarray) -> tuple[np.ndarray, float, float]:
    u_scale = float(np.sqrt(np.mean((u_mat - np.mean(u_mat, axis=1, keepdims=True)) ** 2)))
    t_scale = float(np.sqrt(np.mean((t_mat - np.mean(t_mat, axis=1, keepdims=True)) ** 2)))
    joint = np.vstack([u_mat / u_scale, t_mat / t_scale])
    return joint, u_scale, t_scale


def correlations(coeff: np.ndarray, signals: dict[str, np.ndarray], prefix: str) -> list[dict[str, float | str]]:
    rows = []
    for i in range(min(6, coeff.shape[0])):
        a = coeff[i] - np.mean(coeff[i])
        for name, y in signals.items():
            yy = y - np.mean(y)
            rows.append({"pod_set": prefix, "mode": i + 1, "signal": name, "corr": float(np.corrcoef(a, yy)[0, 1])})
    return rows


def coherent_mode(x: np.ndarray, times: np.ndarray, freq: float) -> np.ndarray:
    xp = x - np.mean(x, axis=1, keepdims=True)
    phase = np.exp(-2j * np.pi * freq * times)
    phase = phase - np.mean(phase)
    return xp @ phase / len(times)


def regression_field(x: np.ndarray, signal: np.ndarray) -> np.ndarray:
    xp = x - np.mean(x, axis=1, keepdims=True)
    sp = signal - np.mean(signal)
    denom = float(np.dot(sp, sp))
    return xp @ sp / denom if denom > 0 else np.full(x.shape[0], np.nan)


def dmd_analysis(x: np.ndarray, times: np.ndarray, rank: int = DMD_RANK) -> dict[str, np.ndarray]:
    xp = x - np.mean(x, axis=1, keepdims=True)
    x1 = xp[:, :-1]
    x2 = xp[:, 1:]
    u, s, vh = np.linalg.svd(x1, full_matrices=False)
    r = min(rank, len(s))
    ur = u[:, :r]
    sr = s[:r]
    vr = vh[:r, :].conj().T
    a_tilde = ur.conj().T @ x2 @ vr @ np.diag(1.0 / sr)
    eigvals, w = np.linalg.eig(a_tilde)
    modes = x2 @ vr @ np.diag(1.0 / sr) @ w
    dt = float(np.median(np.diff(times)))
    omega = np.log(eigvals) / dt
    freq = np.abs(np.imag(omega)) / (2 * np.pi)
    growth = np.real(omega)
    amp = np.linalg.norm(modes, axis=0)
    return {"eigvals": eigvals, "freq": freq, "growth": growth, "amp": amp, "modes": modes}


def scalar_from_u_field(field: np.ndarray, n_points: int) -> np.ndarray:
    return np.sqrt(field[:n_points] ** 2 + field[n_points : 2 * n_points] ** 2)


def scatter_map(ax, points: np.ndarray, values: np.ndarray, title: str, label: str, cmap: str = "viridis"):
    sc = ax.scatter(points[:, 0] * 1000.0, points[:, 1] * 1000.0, c=values, s=3, cmap=cmap, linewidths=0)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title(title)
    plt.colorbar(sc, ax=ax, label=label)


def plot_pod_energy(pods: dict[str, dict[str, np.ndarray]]) -> None:
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    for name, pod in pods.items():
        energy = pod["energy"][:12]
        ax.plot(np.arange(1, len(energy) + 1), 100 * energy, marker="o", label=name)
    ax.set_xlabel("POD mode")
    ax.set_ylabel("energy [%]")
    ax.set_title("POD modal energy")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.savefig(FIG_DIR / "run008_006_pod_energy.png", dpi=180)
    plt.close(fig)


def plot_phase_portraits(pods: dict[str, dict[str, np.ndarray]], signals: dict[str, np.ndarray]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    for ax, name in zip(axes, ["U", "T", "U+T"]):
        c = pods[name]["coeff"]
        sc = ax.scatter(c[0], c[1], c=signals["Cl"], s=10, cmap="coolwarm")
        ax.set_xlabel("a1")
        ax.set_ylabel("a2")
        ax.set_title(f"{name} POD a1-a2, colored by Cl")
        ax.grid(alpha=0.25)
        plt.colorbar(sc, ax=ax, label="Cl")
    fig.savefig(FIG_DIR / "run008_006_pod_phase_portraits.png", dpi=180)
    plt.close(fig)


def plot_pod_modes(points: np.ndarray, pods: dict[str, dict[str, np.ndarray]], n_points: int) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
    for j, mode_idx in enumerate([0, 1]):
        scatter_map(axes[mode_idx, 0], points, scalar_from_u_field(pods["U"]["modes"][:, mode_idx], n_points), f"U POD mode {mode_idx+1}", "|U mode|")
        scatter_map(axes[mode_idx, 1], points, pods["T"]["modes"][:, mode_idx], f"T POD mode {mode_idx+1}", "T mode", cmap="coolwarm")
        joint_mode_t = pods["U+T"]["modes"][2 * n_points :, mode_idx]
        scatter_map(axes[mode_idx, 2], points, joint_mode_t, f"joint POD T-part mode {mode_idx+1}", "scaled T mode", cmap="coolwarm")
    fig.savefig(FIG_DIR / "run008_006_pod_mode_maps.png", dpi=180)
    plt.close(fig)


def plot_correlation_heatmap(rows: list[dict[str, float | str]]) -> None:
    pod_sets = ["U", "T", "U+T"]
    signals = ["Cl", "Cd", "Q_wall", "Nu_tube", "Nu_fins"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    for ax, pod_set in zip(axes, pod_sets):
        mat = np.full((6, len(signals)), np.nan)
        for row in rows:
            if row["pod_set"] == pod_set:
                mat[int(row["mode"]) - 1, signals.index(str(row["signal"]))] = float(row["corr"])
        im = ax.imshow(mat, vmin=-1, vmax=1, cmap="coolwarm", aspect="auto")
        ax.set_title(pod_set)
        ax.set_xticks(np.arange(len(signals)))
        ax.set_xticklabels(signals, rotation=35, ha="right")
        ax.set_yticks(np.arange(6))
        ax.set_yticklabels([f"m{i}" for i in range(1, 7)])
        for i in range(6):
            for j in range(len(signals)):
                ax.text(j, i, f"{mat[i,j]:+.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=axes, label="correlation")
    fig.savefig(FIG_DIR / "run008_006_pod_signal_correlations.png", dpi=180)
    plt.close(fig)


def plot_epod_spod(points: np.ndarray, fields: dict[str, np.ndarray]) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), constrained_layout=True)
    scatter_map(axes[0, 0], points, fields["epod_Cl_T"], "EPOD T | Cl", "dT/dCl", cmap="coolwarm")
    scatter_map(axes[0, 1], points, fields["epod_Q_wall_T"], "EPOD T | Q_wall", "dT/dQ", cmap="coolwarm")
    scatter_map(axes[0, 2], points, fields["epod_Nu_tube_T"], "EPOD T | Nu_tube", "dT/dNu", cmap="coolwarm")
    scatter_map(axes[1, 0], points, fields["spod_T_f1_amp"], "T coherent amplitude f_shed", "amp")
    scatter_map(axes[1, 1], points, fields["spod_U_f1_amp"], "U coherent amplitude f_shed", "amp")
    scatter_map(axes[1, 2], points, fields["spod_T_f2_amp"], "T coherent amplitude 2*f_shed", "amp")
    fig.savefig(FIG_DIR / "run008_006_epod_spod_maps.png", dpi=180)
    plt.close(fig)


def plot_dmd(points: np.ndarray, dmd: dict[str, np.ndarray], n_points: int) -> tuple[int, int]:
    freq = dmd["freq"]
    amp = dmd["amp"]
    valid = (freq > 0.2) & (freq < 20.0)
    idx_f1 = int(np.where(valid)[0][np.argmin(np.abs(freq[valid] - F_SHED))])
    idx_f2 = int(np.where(valid)[0][np.argmin(np.abs(freq[valid] - 2 * F_SHED))])
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    axes[0].scatter(freq[valid], dmd["growth"][valid], s=40 * amp[valid] / np.nanmax(amp[valid]), color="#263238")
    axes[0].axvline(F_SHED, color="#a33", ls="--")
    axes[0].axvline(2 * F_SHED, color="#2a6", ls="--")
    axes[0].set_xlabel("frequency [Hz]")
    axes[0].set_ylabel("growth [1/s]")
    axes[0].set_title("DMD eigenvalues")
    axes[0].grid(alpha=0.25)
    scatter_map(axes[1], points, np.abs(dmd["modes"][2 * n_points :, idx_f1]), f"DMD T amplitude near f={freq[idx_f1]:.2f} Hz", "amp")
    scatter_map(axes[2], points, np.abs(dmd["modes"][2 * n_points :, idx_f2]), f"DMD T amplitude near f={freq[idx_f2]:.2f} Hz", "amp")
    fig.savefig(FIG_DIR / "run008_006_dmd_sanity_modes.png", dpi=180)
    plt.close(fig)
    return idx_f1, idx_f2


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ensure_dirs()
    times, points, u_mat, t_mat = load_midspan()
    n_points = len(points)
    signals = {}
    signals.update(read_force_coeffs(times))
    signals.update(read_heat_signals(times))

    joint, u_scale, t_scale = normalize_joint(u_mat, t_mat)
    pods = {
        "U": snapshot_pod(u_mat),
        "T": snapshot_pod(t_mat),
        "U+T": snapshot_pod(joint),
    }
    corr_rows = []
    for name, pod in pods.items():
        corr_rows.extend(correlations(pod["coeff"], signals, name))

    sp_t_f1 = coherent_mode(t_mat, times, F_SHED)
    sp_t_f2 = coherent_mode(t_mat, times, 2 * F_SHED)
    sp_u_f1 = coherent_mode(u_mat, times, F_SHED)
    epod_fields = {
        "epod_Cl_T": regression_field(t_mat, signals["Cl"]),
        "epod_Q_wall_T": regression_field(t_mat, signals["Q_wall"]),
        "epod_Nu_tube_T": regression_field(t_mat, signals["Nu_tube"]),
        "spod_T_f1_amp": np.abs(sp_t_f1),
        "spod_U_f1_amp": np.abs(scalar_from_u_field(sp_u_f1, n_points)),
        "spod_T_f2_amp": np.abs(sp_t_f2),
    }

    dmd = dmd_analysis(joint, times)
    dmd_i1, dmd_i2 = plot_dmd(points, dmd, n_points)

    plot_pod_energy(pods)
    plot_phase_portraits(pods, signals)
    plot_pod_modes(points, pods, n_points)
    plot_correlation_heatmap(corr_rows)
    plot_epod_spod(points, epod_fields)

    energy_rows = []
    for name, pod in pods.items():
        for i, e in enumerate(pod["energy"][:20], start=1):
            energy_rows.append({"pod_set": name, "mode": i, "energy_fraction": float(e), "cumulative_energy": float(np.sum(pod["energy"][:i]))})
    write_csv(DATA_DIR / "run008_006_pod_energy.csv", energy_rows)
    write_csv(DATA_DIR / "run008_006_pod_signal_correlations.csv", corr_rows)
    dmd_rows = [
        {
            "mode": i,
            "frequency_hz": float(dmd["freq"][i]),
            "growth_1_s": float(dmd["growth"][i]),
            "amplitude_norm": float(dmd["amp"][i]),
        }
        for i in range(len(dmd["freq"]))
    ]
    write_csv(DATA_DIR / "run008_006_dmd_eigenvalues.csv", dmd_rows)
    np.savez_compressed(
        DATA_DIR / "run008_006_modal_arrays.npz",
        times=times,
        points=points,
        pod_u_energy=pods["U"]["energy"],
        pod_t_energy=pods["T"]["energy"],
        pod_joint_energy=pods["U+T"]["energy"],
        pod_u_coeff=pods["U"]["coeff"],
        pod_t_coeff=pods["T"]["coeff"],
        pod_joint_coeff=pods["U+T"]["coeff"],
        sp_t_f1=sp_t_f1,
        sp_t_f2=sp_t_f2,
        dmd_freq=dmd["freq"],
        dmd_growth=dmd["growth"],
    )

    pair_metric_u = float((pods["U"]["energy"][0] + pods["U"]["energy"][1]) / np.sum(pods["U"]["energy"][:8]))
    pair_metric_t = float((pods["T"]["energy"][0] + pods["T"]["energy"][1]) / np.sum(pods["T"]["energy"][:8]))
    best_corrs = sorted(corr_rows, key=lambda r: abs(float(r["corr"])), reverse=True)[:8]
    summary = [
        ModalSummary("n_snapshots", float(len(times))),
        ModalSummary("n_points", float(n_points)),
        ModalSummary("U_mode1_energy_pct", float(100 * pods["U"]["energy"][0])),
        ModalSummary("U_mode2_energy_pct", float(100 * pods["U"]["energy"][1])),
        ModalSummary("T_mode1_energy_pct", float(100 * pods["T"]["energy"][0])),
        ModalSummary("T_mode2_energy_pct", float(100 * pods["T"]["energy"][1])),
        ModalSummary("joint_mode1_energy_pct", float(100 * pods["U+T"]["energy"][0])),
        ModalSummary("joint_mode2_energy_pct", float(100 * pods["U+T"]["energy"][1])),
        ModalSummary("U_pair12_share_of_first8", pair_metric_u),
        ModalSummary("T_pair12_share_of_first8", pair_metric_t),
        ModalSummary("DMD_near_f_shed_hz", float(dmd["freq"][dmd_i1])),
        ModalSummary("DMD_near_2f_shed_hz", float(dmd["freq"][dmd_i2])),
        ModalSummary("joint_scale_U_rms", u_scale),
        ModalSummary("joint_scale_T_rms", t_scale),
    ]
    write_csv(DATA_DIR / "run008_006_modal_summary.csv", [asdict(s) for s in summary])
    (DATA_DIR / "run008_006_modal_summary.json").write_text(
        json.dumps({"summary": [asdict(s) for s in summary], "top_correlations": best_corrs}, indent=2),
        encoding="utf-8",
    )

    lookup = {s.metric: s.value for s in summary}
    lines = [
        "# V4b_3D run008 POD/SPOD/DMD",
        "",
        f"Primary window: `{WINDOW[0]:.1f}..{WINDOW[1]:.1f} s`, snapshots `{len(times)}`, midspan points `{n_points}`.",
        "POD sets: `U`, `T`, and RMS-scaled joint `U+T`.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for s in summary:
        lines.append(f"| {s.metric} | {s.value:.6f} |")
    lines.extend(["", "## Strongest POD-signal correlations", "", "| POD set | mode | signal | corr |", "|---|---:|---|---:|"])
    for row in best_corrs:
        lines.append(f"| {row['pod_set']} | {row['mode']} | {row['signal']} | {float(row['corr']):+.4f} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- U POD mode 1/2 carry `{lookup['U_mode1_energy_pct']:.2f}%` and `{lookup['U_mode2_energy_pct']:.2f}%`; their paired phase portrait should be inspected as the shedding-pair candidate.",
            f"- T POD is more concentrated: mode 1/2 carry `{lookup['T_mode1_energy_pct']:.2f}%` and `{lookup['T_mode2_energy_pct']:.2f}%`.",
            f"- DMD finds sanity-check frequencies near `{lookup['DMD_near_f_shed_hz']:.3f} Hz` and `{lookup['DMD_near_2f_shed_hz']:.3f} Hz`.",
            "- EPOD maps are regression fields conditioned on Cl, Q_wall, and Nu_tube; SPOD-like maps are single-frequency coherent amplitudes at f_shed and 2*f_shed.",
            "",
            "## Figures",
            "",
            "- `../../figures/006/run008_006_pod_energy.png`",
            "- `../../figures/006/run008_006_pod_phase_portraits.png`",
            "- `../../figures/006/run008_006_pod_mode_maps.png`",
            "- `../../figures/006/run008_006_pod_signal_correlations.png`",
            "- `../../figures/006/run008_006_epod_spod_maps.png`",
            "- `../../figures/006/run008_006_dmd_sanity_modes.png`",
        ]
    )
    (DATA_DIR / "run008_006_modal_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((DATA_DIR / "run008_006_modal_analysis.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
