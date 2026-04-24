from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "coherence"
RESULTS_DIR = ROOT / "results" / "coherence"
FIGURES_DIR = RESULTS_DIR / "figures"

GRID_SHAPE = (5, 5)
N_SNAPSHOTS = 1024
DT = 0.05
FS = 1.0 / DT
F0 = 1.25
F2 = 2.0 * F0
PHASE_Q = np.deg2rad(35.0)
RNG_SEED = 20260415


def format_float(value: float) -> str:
    return f"{value:.10g}"


def boundary_mask() -> np.ndarray:
    mask = np.zeros(GRID_SHAPE, dtype=bool)
    mask[0, :] = True
    mask[-1, :] = True
    mask[:, 0] = True
    mask[:, -1] = True
    return mask


BOUNDARY = boundary_mask()
INTERIOR = ~BOUNDARY
LEFT_INTERIOR = np.zeros(GRID_SHAPE, dtype=bool)
LEFT_INTERIOR[1:4, 1] = True
RIGHT_INTERIOR = np.zeros(GRID_SHAPE, dtype=bool)
RIGHT_INTERIOR[1:4, 3] = True
LEFT_WALL = np.zeros(GRID_SHAPE, dtype=bool)
LEFT_WALL[:, 0] = True
RIGHT_WALL = np.zeros(GRID_SHAPE, dtype=bool)
RIGHT_WALL[:, -1] = True


U_BASE = np.array(
    [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 3.0, 5.2, 3.0, 0.0],
        [0.0, 5.2, 10.0, 5.2, 0.0],
        [0.0, 3.0, 5.2, 3.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ],
    dtype=float,
)

U_MODE_SKEW = np.array(
    [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, -0.45, -0.10, 0.55, 0.0],
        [0.0, -1.10, 0.00, 1.20, 0.0],
        [0.0, -0.50, -0.05, 0.45, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ],
    dtype=float,
)

U_MODE_VERTICAL = np.array(
    [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.45, 0.75, 0.35, 0.0],
        [0.0, 0.05, 0.00, -0.05, 0.0],
        [0.0, -0.35, -0.75, -0.45, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ],
    dtype=float,
)

U_MODE_BREATHING = np.array(
    [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.35, 0.50, 0.35, 0.0],
        [0.0, 0.50, 0.85, 0.50, 0.0],
        [0.0, 0.35, 0.50, 0.35, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0],
    ],
    dtype=float,
)

Q_BASE = np.array(
    [
        [2.4, 3.1, 3.8, 3.1, 2.4],
        [3.7, 0.0, 0.0, 0.0, 3.7],
        [5.0, 0.0, 0.0, 0.0, 5.0],
        [3.7, 0.0, 0.0, 0.0, 3.7],
        [2.4, 3.1, 3.8, 3.1, 2.4],
    ],
    dtype=float,
)

Q_MODE_SKEW = np.array(
    [
        [0.25, 0.20, 0.00, -0.20, -0.25],
        [0.80, 0.00, 0.00, 0.00, -0.80],
        [1.35, 0.00, 0.00, 0.00, -1.35],
        [0.80, 0.00, 0.00, 0.00, -0.80],
        [0.25, 0.20, 0.00, -0.20, -0.25],
    ],
    dtype=float,
)

Q_MODE_DIAGONAL = np.array(
    [
        [0.75, 0.40, 0.00, -0.35, -0.65],
        [0.35, 0.00, 0.00, 0.00, -0.20],
        [0.00, 0.00, 0.00, 0.00, 0.00],
        [-0.20, 0.00, 0.00, 0.00, 0.35],
        [-0.65, -0.35, 0.00, 0.40, 0.75],
    ],
    dtype=float,
)

Q_MODE_MEAN = np.array(
    [
        [0.70, 0.90, 1.10, 0.90, 0.70],
        [0.90, 0.00, 0.00, 0.00, 0.90],
        [1.20, 0.00, 0.00, 0.00, 1.20],
        [0.90, 0.00, 0.00, 0.00, 0.90],
        [0.70, 0.90, 1.10, 0.90, 0.70],
    ],
    dtype=float,
)

Q_MODE_LOCAL = np.array(
    [
        [0.00, 0.45, 0.90, 0.45, 0.00],
        [-0.20, 0.00, 0.00, 0.00, -0.20],
        [-0.35, 0.00, 0.00, 0.00, -0.35],
        [-0.20, 0.00, 0.00, 0.00, -0.20],
        [0.00, 0.45, 0.90, 0.45, 0.00],
    ],
    dtype=float,
)


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def zscore(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    std = float(np.std(values))
    if std == 0.0:
        return values * 0.0
    return (values - float(np.mean(values))) / std


def deterministic_signs(
    modes: np.ndarray,
    coefficients: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    modes = modes.copy()
    coefficients = coefficients.copy()
    for i in range(modes.shape[1]):
        pivot = int(np.argmax(np.abs(modes[:, i])))
        if modes[pivot, i] < 0.0:
            modes[:, i] *= -1.0
            coefficients[i, :] *= -1.0
    return modes, coefficients


def compute_pod(snapshot_matrix: np.ndarray) -> dict[str, np.ndarray]:
    mean = snapshot_matrix.mean(axis=1, keepdims=True)
    centered = snapshot_matrix - mean
    modes, singular_values, vt = np.linalg.svd(centered, full_matrices=False)
    coefficients = np.diag(singular_values) @ vt
    modes, coefficients = deterministic_signs(modes, coefficients)
    energy = singular_values**2
    energy_fraction = energy / float(np.sum(energy))
    return {
        "mean": mean[:, 0],
        "centered": centered,
        "modes": modes,
        "singular_values": singular_values,
        "coefficients": coefficients,
        "energy_fraction": energy_fraction,
        "cumulative_energy": np.cumsum(energy_fraction),
    }


def generate_datasets() -> dict[str, Any]:
    rng = np.random.default_rng(RNG_SEED)
    times = np.arange(N_SNAPSHOTS, dtype=float) * DT
    velocity = np.zeros((N_SNAPSHOTS, *GRID_SHAPE), dtype=float)
    heat_flux = np.zeros((N_SNAPSHOTS, *GRID_SHAPE), dtype=float)

    for i, time in enumerate(times):
        omega = 2.0 * np.pi * F0 * time
        omega2 = 2.0 * np.pi * F2 * time

        u_noise = rng.normal(0.0, 0.025, GRID_SHAPE)
        u_noise[BOUNDARY] = 0.0
        q_noise = rng.normal(0.0, 0.045, GRID_SHAPE)
        q_noise[INTERIOR] = 0.0

        velocity[i] = (
            U_BASE
            + 1.20 * np.sin(omega) * U_MODE_SKEW
            + 0.90 * np.cos(omega + 0.22) * U_MODE_VERTICAL
            + 0.55 * np.sin(omega2 + 0.15) * U_MODE_BREATHING
            + u_noise
        )

        heat_flux[i] = (
            Q_BASE
            + 1.05 * np.sin(omega + PHASE_Q) * Q_MODE_SKEW
            + 0.65 * np.cos(omega + PHASE_Q + 0.40) * Q_MODE_DIAGONAL
            + 0.85 * np.sin(omega2 + 0.50) * Q_MODE_MEAN
            + 0.22 * np.sin(2.0 * np.pi * 3.75 * time + 0.10) * Q_MODE_LOCAL
            + q_noise
        )

        heat_flux[i, INTERIOR] = 0.0

    velocity = np.maximum(velocity, 0.0)
    return {"times": times, "velocity": velocity, "heat_flux": heat_flux}


def write_dataset_json(path: Path, name: str, times: np.ndarray, fields: np.ndarray) -> None:
    snapshots = [
        {
            "id": f"t{i:04d}",
            "time": format_float(float(time)),
            "matrix": fields[i].round(10).tolist(),
        }
        for i, time in enumerate(times)
    ]
    payload = {
        "dataset": name,
        "description": "Long synthetic 5x5 time series for spectral coherence demonstration.",
        "grid_shape": list(GRID_SHAPE),
        "n_snapshots": int(len(times)),
        "dt": DT,
        "sampling_frequency": FS,
        "base_frequency": F0,
        "second_harmonic_frequency": F2,
        "snapshots": snapshots,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_snapshot_long_csv(path: Path, times: np.ndarray, fields: np.ndarray, value_name: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["snapshot_id", "time", "y", "x", value_name])
        for i, time in enumerate(times):
            for y in range(GRID_SHAPE[0]):
                for x in range(GRID_SHAPE[1]):
                    writer.writerow([f"t{i:04d}", format_float(float(time)), y, x, format_float(float(fields[i, y, x]))])


def write_matrix_csv(path: Path, matrix: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["y/x", "0", "1", "2", "3", "4"])
        for y, row in enumerate(matrix):
            writer.writerow([y, *[format_float(float(value)) for value in row]])


def write_modal_energy_csv(path: Path, pod_results: dict[str, dict[str, np.ndarray]], mode_count: int = 8) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["dataset", "mode", "singular_value", "energy_fraction", "cumulative_energy"])
        for dataset, pod in pod_results.items():
            for i in range(min(mode_count, len(pod["singular_values"]))):
                writer.writerow(
                    [
                        dataset,
                        i + 1,
                        format_float(float(pod["singular_values"][i])),
                        format_float(float(pod["energy_fraction"][i])),
                        format_float(float(pod["cumulative_energy"][i])),
                    ]
                )


def write_signals_csv(path: Path, signals: dict[str, np.ndarray]) -> None:
    names = list(signals.keys())
    n = len(next(iter(signals.values())))
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(names)
        for i in range(n):
            writer.writerow([format_float(float(signals[name][i])) for name in names])


def flatten_snapshots(fields: np.ndarray) -> np.ndarray:
    return np.column_stack([field.reshape(-1) for field in fields])


def extract_signals(times: np.ndarray, velocity: np.ndarray, heat_flux: np.ndarray, pod_u: dict[str, np.ndarray], pod_q: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    u_skew = velocity[:, RIGHT_INTERIOR].mean(axis=1) - velocity[:, LEFT_INTERIOR].mean(axis=1)
    q_skew = heat_flux[:, RIGHT_WALL].mean(axis=1) - heat_flux[:, LEFT_WALL].mean(axis=1)
    u_core_mean = velocity[:, INTERIOR].mean(axis=1)
    q_wall_mean = heat_flux[:, BOUNDARY].mean(axis=1)

    signals = {
        "time": times,
        "u_skew": u_skew,
        "q_skew": q_skew,
        "u_core_mean": u_core_mean,
        "q_wall_mean": q_wall_mean,
    }

    for mode in range(3):
        signals[f"u_pod_a{mode + 1}"] = pod_u["coefficients"][mode, :]
        signals[f"q_pod_a{mode + 1}"] = pod_q["coefficients"][mode, :]
    return signals


def welch_cross_spectrum(
    x: np.ndarray,
    y: np.ndarray,
    fs: float,
    *,
    nperseg: int = 256,
    noverlap: int = 128,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape:
        raise ValueError("Signals must have the same shape.")
    if len(x) < nperseg:
        raise ValueError("Signal is shorter than nperseg.")

    step = nperseg - noverlap
    starts = range(0, len(x) - nperseg + 1, step)
    window = np.hanning(nperseg)
    scale = fs * float(np.sum(window**2))
    sxx = None
    syy = None
    sxy = None
    count = 0

    for start in starts:
        sx = x[start : start + nperseg].copy()
        sy = y[start : start + nperseg].copy()
        sx -= float(np.mean(sx))
        sy -= float(np.mean(sy))
        fx = np.fft.rfft(sx * window)
        fy = np.fft.rfft(sy * window)
        if sxx is None:
            sxx = np.zeros_like(fx, dtype=np.complex128)
            syy = np.zeros_like(fy, dtype=np.complex128)
            sxy = np.zeros_like(fx, dtype=np.complex128)
        sxx += fx * np.conjugate(fx)
        syy += fy * np.conjugate(fy)
        sxy += fx * np.conjugate(fy)
        count += 1

    if count == 0 or sxx is None or syy is None or sxy is None:
        raise RuntimeError("No Welch segments were produced.")

    freqs = np.fft.rfftfreq(nperseg, d=1.0 / fs)
    sxx = sxx / (count * scale)
    syy = syy / (count * scale)
    sxy = sxy / (count * scale)
    return freqs, sxx.real, syy.real, sxy


def coherence_from_spectra(sxx: np.ndarray, syy: np.ndarray, sxy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    denominator = np.maximum(sxx * syy, 1.0e-30)
    coherence = np.abs(sxy) ** 2 / denominator
    return np.clip(coherence.real, 0.0, 1.0), np.angle(sxy)


def compute_pair_spectra(signals: dict[str, np.ndarray]) -> dict[str, dict[str, np.ndarray]]:
    pairs = {
        "u_skew_vs_q_skew": ("u_skew", "q_skew", F0),
        "u_core_mean_vs_q_wall_mean": ("u_core_mean", "q_wall_mean", F2),
        "u_pod_a1_vs_q_pod_a1": ("u_pod_a1", "q_pod_a1", F0),
        "u_pod_a2_vs_q_pod_a2": ("u_pod_a2", "q_pod_a2", F2),
    }
    output: dict[str, dict[str, np.ndarray]] = {}
    for name, (x_name, y_name, expected_frequency) in pairs.items():
        freqs, sxx, syy, sxy = welch_cross_spectrum(signals[x_name], signals[y_name], FS)
        coherence, phase = coherence_from_spectra(sxx, syy, sxy)
        output[name] = {
            "frequency": freqs,
            "sxx": sxx,
            "syy": syy,
            "sxy_abs": np.abs(sxy),
            "coherence": coherence,
            "phase": phase,
            "expected_frequency": np.full_like(freqs, expected_frequency, dtype=float),
        }
    return output


def compute_pod_coherence_matrices(
    signals: dict[str, np.ndarray],
    *,
    mode_count: int = 3,
) -> dict[str, dict[str, np.ndarray]]:
    matrices: dict[str, dict[str, np.ndarray]] = {}
    for label, target_frequency in [("f0", F0), ("2f0", F2)]:
        coherence_matrix = np.zeros((mode_count, mode_count), dtype=float)
        phase_matrix = np.zeros((mode_count, mode_count), dtype=float)
        frequency_matrix = np.zeros((mode_count, mode_count), dtype=float)
        for i in range(mode_count):
            for j in range(mode_count):
                x_name = f"u_pod_a{i + 1}"
                y_name = f"q_pod_a{j + 1}"
                freqs, sxx, syy, sxy = welch_cross_spectrum(signals[x_name], signals[y_name], FS)
                coherence, phase = coherence_from_spectra(sxx, syy, sxy)
                peak_frequency, peak_coherence, index = peak_near(freqs, coherence, target_frequency, width=0.12)
                coherence_matrix[i, j] = peak_coherence
                phase_matrix[i, j] = phase[index]
                frequency_matrix[i, j] = peak_frequency
        matrices[label] = {
            "coherence": coherence_matrix,
            "phase": phase_matrix,
            "frequency": frequency_matrix,
        }
    return matrices


def peak_near(freqs: np.ndarray, values: np.ndarray, target: float, width: float = 0.24) -> tuple[float, float, int]:
    mask = (freqs >= target - width) & (freqs <= target + width)
    if not np.any(mask):
        index = int(np.argmin(np.abs(freqs - target)))
        return float(freqs[index]), float(values[index]), index
    local_indices = np.where(mask)[0]
    local_best = int(local_indices[np.argmax(values[local_indices])])
    return float(freqs[local_best]), float(values[local_best]), local_best


def write_frequency_response_csv(path: Path, spectra: dict[str, dict[str, np.ndarray]]) -> None:
    names = list(spectra.keys())
    freqs = spectra[names[0]]["frequency"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        header = ["frequency_Hz"]
        for name in names:
            header.extend([f"{name}_coherence", f"{name}_phase_rad", f"{name}_sxx", f"{name}_syy"])
        writer.writerow(header)
        for i, freq in enumerate(freqs):
            row = [format_float(float(freq))]
            for name in names:
                row.extend(
                    [
                        format_float(float(spectra[name]["coherence"][i])),
                        format_float(float(spectra[name]["phase"][i])),
                        format_float(float(spectra[name]["sxx"][i])),
                        format_float(float(spectra[name]["syy"][i])),
                    ]
                )
            writer.writerow(row)


def write_peak_summary_csv(path: Path, spectra: dict[str, dict[str, np.ndarray]]) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for name, data in spectra.items():
        target = float(data["expected_frequency"][0])
        peak_frequency, peak_coherence, index = peak_near(data["frequency"], data["coherence"], target)
        rows.append(
            {
                "pair": name,
                "expected_frequency_Hz": target,
                "peak_frequency_Hz": peak_frequency,
                "peak_coherence": peak_coherence,
                "phase_at_peak_rad": float(data["phase"][index]),
                "phase_at_peak_deg": float(np.rad2deg(data["phase"][index])),
            }
        )

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_float(value) if isinstance(value, float) else value for key, value in row.items()})
    return rows


def write_pod_pair_coherence_csv(path: Path, matrices: dict[str, dict[str, np.ndarray]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "frequency_label",
                "velocity_mode",
                "heat_flux_mode",
                "peak_frequency_Hz",
                "coherence",
                "phase_rad",
                "phase_deg",
            ]
        )
        for label, data in matrices.items():
            coherence = data["coherence"]
            phase = data["phase"]
            frequency = data["frequency"]
            for i in range(coherence.shape[0]):
                for j in range(coherence.shape[1]):
                    writer.writerow(
                        [
                            label,
                            i + 1,
                            j + 1,
                            format_float(float(frequency[i, j])),
                            format_float(float(coherence[i, j])),
                            format_float(float(phase[i, j])),
                            format_float(float(np.rad2deg(phase[i, j]))),
                        ]
                    )


def write_summary_md(path: Path, peak_rows: list[dict[str, float | str]], pod_u: dict[str, np.ndarray], pod_q: dict[str, np.ndarray]) -> None:
    lines = [
        "# Spectral Coherence Demonstration",
        "",
        "This folder contains a long synthetic `5x5` velocity and wall heat-flux time series.",
        "",
        f"- snapshots: `{N_SNAPSHOTS}`",
        f"- time step: `{DT}`",
        f"- sampling frequency: `{FS}`",
        f"- imposed base frequency: `{F0}`",
        f"- imposed second harmonic: `{F2}`",
        "",
        "The magnitude-squared coherence is computed as:",
        "",
        "```text",
        "C_xy(f) = |S_xy(f)|^2 / (S_xx(f) S_yy(f))",
        "```",
        "",
        "where `S_xy` is the Welch cross-spectrum and `S_xx`, `S_yy` are the Welch auto-spectra.",
        "",
        "## POD Energy of the Long Series",
        "",
        "| dataset | mode 1 | mode 2 | mode 3 | cumulative 3 modes |",
        "|---|---:|---:|---:|---:|",
        (
            f"| velocity | {100.0 * pod_u['energy_fraction'][0]:.2f}% | "
            f"{100.0 * pod_u['energy_fraction'][1]:.2f}% | "
            f"{100.0 * pod_u['energy_fraction'][2]:.2f}% | "
            f"{100.0 * pod_u['cumulative_energy'][2]:.2f}% |"
        ),
        (
            f"| heat_flux | {100.0 * pod_q['energy_fraction'][0]:.2f}% | "
            f"{100.0 * pod_q['energy_fraction'][1]:.2f}% | "
            f"{100.0 * pod_q['energy_fraction'][2]:.2f}% | "
            f"{100.0 * pod_q['cumulative_energy'][2]:.2f}% |"
        ),
        "",
        "## Coherence Peaks",
        "",
        "| pair | expected frequency | peak frequency | peak coherence | phase at peak |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in peak_rows:
        lines.append(
            f"| {row['pair']} | {float(row['expected_frequency_Hz']):.3f} | "
            f"{float(row['peak_frequency_Hz']):.3f} | {float(row['peak_coherence']):.3f} | "
            f"{float(row['phase_at_peak_deg']):.1f} deg |"
        )
    lines.extend(
        [
            "",
            "## Main Figures",
            "",
            "- `figures/coherence_snapshot_gallery.png`",
            "- `figures/coherence_input_signals.png`",
            "- `figures/coherence_power_spectra.png`",
            "- `figures/coherence_curves.png`",
            "- `figures/coherence_pod_modal_energy.png`",
            "- `figures/coherence_pod_mode_pair_heatmaps.png`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def selected_snapshot_indices() -> list[int]:
    period = 1.0 / F0
    targets = [0.0, 0.25 * period, 0.50 * period, 0.75 * period]
    return [int(round(target / DT)) for target in targets]


def plot_snapshot_gallery(times: np.ndarray, velocity: np.ndarray, heat_flux: np.ndarray) -> Path:
    indices = selected_snapshot_indices()
    fig, axes = plt.subplots(2, len(indices), figsize=(12.5, 6.1), dpi=180)
    vmin_u = float(np.min(velocity[indices]))
    vmax_u = float(np.max(velocity[indices]))
    vmin_q = float(np.min(heat_flux[indices]))
    vmax_q = float(np.max(heat_flux[indices]))

    for col, index in enumerate(indices):
        for row, (fields, label, cmap, vmin, vmax) in enumerate(
            [
                (velocity, "velocity U", "viridis", vmin_u, vmax_u),
                (heat_flux, "wall heat flux q", "inferno", vmin_q, vmax_q),
            ]
        ):
            ax = axes[row, col]
            image = ax.imshow(fields[index], origin="upper", cmap=cmap, vmin=vmin, vmax=vmax)
            ax.set_title(f"{label}\nt = {times[index]:.2f}", fontsize=9)
            ax.set_xticks(range(5))
            ax.set_yticks(range(5))
            ax.tick_params(labelsize=7)
            for y in range(5):
                for x in range(5):
                    ax.text(x, y, f"{fields[index, y, x]:.1f}", ha="center", va="center", fontsize=6.3, color="white")
            fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle("Synthetic snapshots over one base-frequency cycle")
    fig.tight_layout()
    path = FIGURES_DIR / "coherence_snapshot_gallery.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_input_signals(signals: dict[str, np.ndarray]) -> Path:
    time = signals["time"]
    mask = time <= 4.0 / F0
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 6.0), dpi=180, sharex=True)

    axes[0].plot(time[mask], zscore(signals["u_skew"])[mask], color="#2563eb", lw=1.5, label="U skew")
    axes[0].plot(time[mask], zscore(signals["q_skew"])[mask], color="#dc2626", lw=1.5, label="q skew")
    axes[0].set_title(f"Base-frequency pair, f0 = {F0:.2f}")
    axes[0].set_ylabel("normalized signal")
    axes[0].legend(frameon=False, fontsize=8)

    axes[1].plot(time[mask], zscore(signals["u_core_mean"])[mask], color="#0f766e", lw=1.5, label="U core mean")
    axes[1].plot(time[mask], zscore(signals["q_wall_mean"])[mask], color="#b45309", lw=1.5, label="q wall mean")
    axes[1].set_title(f"Second-harmonic pair, 2f0 = {F2:.2f}")
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("normalized signal")
    axes[1].legend(frameon=False, fontsize=8)

    for ax in axes:
        ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
        ax.axhline(0.0, color="#44403c", lw=0.7)
    fig.tight_layout()
    path = FIGURES_DIR / "coherence_input_signals.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_power_spectra(spectra: dict[str, dict[str, np.ndarray]]) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=180, sharey=False)
    configs = [
        ("u_skew_vs_q_skew", "Skew signals", F0),
        ("u_core_mean_vs_q_wall_mean", "Mean signals", F2),
    ]
    for ax, (name, title, expected) in zip(axes, configs):
        freq = spectra[name]["frequency"]
        mask = (freq >= 0.0) & (freq <= 5.0)
        ax.semilogy(freq[mask], spectra[name]["sxx"][mask], color="#2563eb", lw=1.5, label="source PSD")
        ax.semilogy(freq[mask], spectra[name]["syy"][mask], color="#dc2626", lw=1.5, label="target PSD")
        ax.axvline(expected, color="#111827", ls="--", lw=1.0, label=f"expected {expected:.2f}")
        ax.set_title(title)
        ax.set_xlabel("frequency")
        ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
        ax.legend(frameon=False, fontsize=8)
    axes[0].set_ylabel("Welch PSD")
    fig.suptitle("Power spectra of representative signals")
    fig.tight_layout()
    path = FIGURES_DIR / "coherence_power_spectra.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_coherence_curves(spectra: dict[str, dict[str, np.ndarray]]) -> Path:
    fig, ax = plt.subplots(figsize=(9.4, 5.1), dpi=180)
    colors = {
        "u_skew_vs_q_skew": "#2563eb",
        "u_core_mean_vs_q_wall_mean": "#dc2626",
        "u_pod_a1_vs_q_pod_a1": "#0f766e",
        "u_pod_a2_vs_q_pod_a2": "#b45309",
    }
    for name, data in spectra.items():
        freq = data["frequency"]
        mask = (freq >= 0.0) & (freq <= 5.0)
        label = name.replace("_", " ")
        ax.plot(freq[mask], data["coherence"][mask], lw=1.7, color=colors[name], label=label)

    ax.axvline(F0, color="#111827", ls="--", lw=1.0)
    ax.axvline(F2, color="#111827", ls=":", lw=1.2)
    ax.text(F0 + 0.04, 0.08, f"f0 = {F0:.2f}", rotation=90, va="bottom", fontsize=8)
    ax.text(F2 + 0.04, 0.08, f"2f0 = {F2:.2f}", rotation=90, va="bottom", fontsize=8)
    ax.text(
        0.98,
        0.12,
        r"$C_{xy}(f)=|S_{xy}(f)|^2/(S_{xx}(f)S_{yy}(f))$",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#a8a29e", "alpha": 0.92},
    )
    ax.set_xlim(0.0, 5.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel("frequency")
    ax.set_ylabel("magnitude-squared coherence")
    ax.set_title("Spectral coherence between velocity and heat-flux signals")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    path = FIGURES_DIR / "coherence_curves.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_pod_modal_energy(pod_u: dict[str, np.ndarray], pod_q: dict[str, np.ndarray]) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.2), dpi=180, sharey=True)
    for ax, name, pod, color in [
        (axes[0], "velocity", pod_u, "#2563eb"),
        (axes[1], "heat flux", pod_q, "#dc2626"),
    ]:
        modes = np.arange(1, 7)
        energy = 100.0 * pod["energy_fraction"][:6]
        cumulative = 100.0 * pod["cumulative_energy"][:6]
        ax.bar(modes, energy, color=color, alpha=0.72, label="mode energy")
        ax.plot(modes, cumulative, color="#111827", marker="o", lw=1.5, label="cumulative")
        ax.set_title(name)
        ax.set_xlabel("POD mode")
        ax.set_xticks(modes)
        ax.set_ylim(0.0, 105.0)
        ax.grid(True, axis="y", color="#d6d3d1", lw=0.6, alpha=0.85)
        ax.legend(frameon=False, fontsize=8, loc="lower right")
    axes[0].set_ylabel("energy [%]")
    fig.suptitle("POD modal energy for long coherence dataset")
    fig.tight_layout()
    path = FIGURES_DIR / "coherence_pod_modal_energy.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_pod_pair_coherence_heatmaps(matrices: dict[str, dict[str, np.ndarray]]) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.0), dpi=180)
    configs = [("f0", F0, "base frequency"), ("2f0", F2, "second harmonic")]
    for ax, (label, frequency, title) in zip(axes, configs):
        matrix = matrices[label]["coherence"]
        image = ax.imshow(matrix, origin="upper", cmap="magma", vmin=0.0, vmax=1.0)
        ax.set_title(f"{title}\nf = {frequency:.2f}")
        ax.set_xlabel("heat-flux POD mode")
        ax.set_ylabel("velocity POD mode")
        ax.set_xticks(range(matrix.shape[1]), [str(i) for i in range(1, matrix.shape[1] + 1)])
        ax.set_yticks(range(matrix.shape[0]), [str(i) for i in range(1, matrix.shape[0] + 1)])
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = float(matrix[i, j])
                ax.text(j, i, f"{value:.2f}", ha="center", va="center", color="white" if value > 0.55 else "#111827", fontsize=9)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Spectral coherence between POD temporal coefficients")
    fig.tight_layout()
    path = FIGURES_DIR / "coherence_pod_mode_pair_heatmaps.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def write_outputs(
    data: dict[str, Any],
    pod_u: dict[str, np.ndarray],
    pod_q: dict[str, np.ndarray],
    signals: dict[str, np.ndarray],
    spectra: dict[str, dict[str, np.ndarray]],
    pod_pair_matrices: dict[str, dict[str, np.ndarray]],
) -> None:
    times = data["times"]
    velocity = data["velocity"]
    heat_flux = data["heat_flux"]

    write_dataset_json(DATA_DIR / "velocity_time_snapshots_5x5.json", "velocity", times, velocity)
    write_dataset_json(DATA_DIR / "heat_flux_time_snapshots_5x5.json", "heat_flux", times, heat_flux)
    write_snapshot_long_csv(DATA_DIR / "velocity_time_snapshots_5x5_long.csv", times, velocity, "u")
    write_snapshot_long_csv(DATA_DIR / "heat_flux_time_snapshots_5x5_long.csv", times, heat_flux, "q")

    write_signals_csv(RESULTS_DIR / "signals.csv", signals)
    write_modal_energy_csv(RESULTS_DIR / "pod_modal_energy.csv", {"velocity": pod_u, "heat_flux": pod_q})
    write_frequency_response_csv(RESULTS_DIR / "frequency_response.csv", spectra)
    write_pod_pair_coherence_csv(RESULTS_DIR / "pod_pair_coherence.csv", pod_pair_matrices)
    peak_rows = write_peak_summary_csv(RESULTS_DIR / "coherence_peak_summary.csv", spectra)
    write_summary_md(RESULTS_DIR / "coherence_summary.md", peak_rows, pod_u, pod_q)

    for name, mode in [("velocity_pod_mode_01.csv", pod_u["modes"][:, 0]), ("heat_flux_pod_mode_01.csv", pod_q["modes"][:, 0])]:
        write_matrix_csv(RESULTS_DIR / name, mode.reshape(GRID_SHAPE))

    figures = [
        plot_snapshot_gallery(times, velocity, heat_flux),
        plot_input_signals(signals),
        plot_power_spectra(spectra),
        plot_coherence_curves(spectra),
        plot_pod_modal_energy(pod_u, pod_q),
        plot_pod_pair_coherence_heatmaps(pod_pair_matrices),
    ]
    (FIGURES_DIR / "README.md").write_text(
        "\n".join(
            [
                "# Spectral Coherence Figures",
                "",
                "- `coherence_snapshot_gallery.png` - selected velocity and heat-flux snapshots over one imposed cycle.",
                "- `coherence_input_signals.png` - normalized representative input signals.",
                "- `coherence_power_spectra.png` - Welch power spectra for representative pairs.",
                "- `coherence_curves.png` - magnitude-squared coherence curves with the imposed frequencies marked.",
                "- `coherence_pod_modal_energy.png` - POD energy split for the long coherence dataset.",
                "- `coherence_pod_mode_pair_heatmaps.png` - coherence between the first POD temporal coefficients.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for figure in figures:
        print(f"Wrote {figure}")


def main() -> None:
    ensure_dirs()
    data = generate_datasets()
    x_u = flatten_snapshots(data["velocity"])
    x_q = flatten_snapshots(data["heat_flux"])
    pod_u = compute_pod(x_u)
    pod_q = compute_pod(x_q)
    signals = extract_signals(data["times"], data["velocity"], data["heat_flux"], pod_u, pod_q)
    spectra = compute_pair_spectra(signals)
    pod_pair_matrices = compute_pod_coherence_matrices(signals)
    write_outputs(data, pod_u, pod_q, signals, spectra, pod_pair_matrices)
    print(f"Wrote coherence results to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
