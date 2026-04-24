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
POD_DIR = ROOT / "results" / "pod"
EPOD_DIR = ROOT / "results" / "epod"
FIGURES_DIR = ROOT / "results" / "figures"

POD_DATASETS = ["velocity", "heat_flux"]
EPOD_DIRECTIONS = ["velocity_to_heat_flux", "heat_flux_to_velocity"]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_snapshot_matrix(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        snapshot_ids = fieldnames[3:]
        rows = list(reader)
    matrix = np.array([[float(row[sid]) for sid in snapshot_ids] for row in rows], dtype=float)
    return snapshot_ids, matrix


def active_modes(pod: dict[str, Any]) -> int:
    return int(pod["active_mode_count"])


def pod_temporal_coefficients(pod: dict[str, Any]) -> np.ndarray:
    return np.array([row["coefficients"] for row in pod["temporal_coefficients"]], dtype=float)


def save_matrix_grid(
    matrices: list[np.ndarray],
    titles: list[str],
    path: Path,
    *,
    cmap: str,
    symmetric: bool,
    suptitle: str,
) -> None:
    n = len(matrices)
    fig, axes = plt.subplots(1, n, figsize=(3.0 * n, 3.4), dpi=180)
    if n == 1:
        axes = [axes]

    if symmetric:
        vmax = max(float(np.max(np.abs(matrix))) for matrix in matrices)
        vmin = -vmax
    else:
        vmin = min(float(np.min(matrix)) for matrix in matrices)
        vmax = max(float(np.max(matrix)) for matrix in matrices)

    for ax, matrix, title in zip(axes, matrices, titles):
        image = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax, origin="upper")
        ax.set_title(title, fontsize=9)
        ax.set_xticks(range(5))
        ax.set_yticks(range(5))
        ax.tick_params(labelsize=7)
        for y in range(matrix.shape[0]):
            for x in range(matrix.shape[1]):
                value = float(matrix[y, x])
                text_color = "white" if abs(value) > 0.55 * max(abs(vmin), abs(vmax), 1.0e-12) else "#111827"
                ax.text(x, y, f"{value:.2g}", ha="center", va="center", fontsize=6.5, color=text_color)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle(suptitle, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_pod_energy(pods: dict[str, dict[str, Any]]) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), dpi=180, sharey=True)
    colors = {"velocity": "#2563eb", "heat_flux": "#dc2626"}

    for ax, dataset in zip(axes, POD_DATASETS):
        pod = pods[dataset]
        n_active = active_modes(pod)
        energy = np.array(pod["energy_fraction"], dtype=float)[:n_active] * 100.0
        cumulative = np.array(pod["cumulative_energy"], dtype=float)[:n_active] * 100.0
        modes = np.arange(1, n_active + 1)
        ax.bar(modes, energy, color=colors[dataset], alpha=0.72, label="mode energy")
        ax.plot(modes, cumulative, color="#111827", marker="o", lw=1.5, label="cumulative")
        ax.set_title(dataset)
        ax.set_xlabel("mode")
        ax.set_xticks(modes)
        ax.set_ylim(0, 105)
        ax.grid(True, axis="y", color="#d6d3d1", lw=0.6, alpha=0.85)
        for mode, value in zip(modes, energy):
            ax.text(mode, value + 2.0, f"{value:.1f}%", ha="center", fontsize=8)
        ax.legend(frameon=False, fontsize=8, loc="upper right")

    axes[0].set_ylabel("energy [%]")
    fig.suptitle("POD modal energy")
    fig.tight_layout()
    out = FIGURES_DIR / "pod_modal_energy.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_pod_modes(dataset: str, pod: dict[str, Any]) -> Path:
    mean = np.array(pod["mean_field"], dtype=float)
    n_active = active_modes(pod)
    modes = [np.array(item["matrix"], dtype=float) for item in pod["spatial_modes"][:n_active]]

    out_mean = FIGURES_DIR / f"pod_{dataset}_mean_field.png"
    save_matrix_grid([mean], ["mean field"], out_mean, cmap="viridis" if dataset == "velocity" else "inferno", symmetric=False, suptitle=f"{dataset}: temporal mean")

    out_modes = FIGURES_DIR / f"pod_{dataset}_spatial_modes.png"
    save_matrix_grid(
        modes,
        [f"mode {i}" for i in range(1, n_active + 1)],
        out_modes,
        cmap="RdBu_r",
        symmetric=True,
        suptitle=f"{dataset}: POD spatial modes",
    )
    return out_modes


def plot_pod_temporal(dataset: str, pod: dict[str, Any]) -> Path:
    n_active = active_modes(pod)
    coeffs = pod_temporal_coefficients(pod)[:n_active, :]
    times = np.array(pod["times"], dtype=float)
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=180)
    for mode_idx in range(n_active):
        ax.plot(times, coeffs[mode_idx, :], marker="o", lw=1.5, label=f"mode {mode_idx + 1}")
    ax.axhline(0.0, color="#44403c", lw=0.8)
    ax.set_xlabel("time")
    ax.set_ylabel("temporal coefficient")
    ax.set_title(f"{dataset}: POD temporal coefficients")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    out = FIGURES_DIR / f"pod_{dataset}_temporal_coefficients.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_epod_quality(epods: dict[str, dict[str, Any]]) -> Path:
    fig, ax = plt.subplots(figsize=(7.4, 4.4), dpi=180)
    colors = {"velocity_to_heat_flux": "#0f766e", "heat_flux_to_velocity": "#b45309"}
    for direction in EPOD_DIRECTIONS:
        metrics = epods[direction]["metrics"]
        modes = [int(row["mode_count"]) for row in metrics]
        captured = [float(row["captured_target_energy_percent"]) for row in metrics]
        ax.plot(modes, captured, marker="o", lw=1.8, color=colors[direction], label=direction.replace("_", " "))
        for mode, value in zip(modes, captured):
            ax.text(mode, value + 1.5, f"{value:.1f}%", ha="center", fontsize=8)
    ax.set_xlabel("source POD modes used")
    ax.set_ylabel("captured target fluctuation energy [%]")
    ax.set_ylim(0, 105)
    ax.set_xticks([1, 2, 3, 4])
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title("EPOD target reconstruction quality")
    fig.tight_layout()
    out = FIGURES_DIR / "epod_reconstruction_quality.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_epod_extended_modes(direction: str, epod: dict[str, Any]) -> Path:
    modes = [np.array(item["matrix"], dtype=float) for item in epod["extended_modes"]]
    out = FIGURES_DIR / f"epod_{direction}_extended_modes.png"
    save_matrix_grid(
        modes,
        [f"mode {i}" for i in range(1, len(modes) + 1)],
        out,
        cmap="RdBu_r",
        symmetric=True,
        suptitle=f"EPOD extended modes: {direction.replace('_', ' ')}",
    )
    return out


def reconstruct_epod_snapshot(direction: str, epod: dict[str, Any], mode_count: int, snapshot_index: int = -1) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    source = str(epod["source_dataset"])
    target = str(epod["target_dataset"])
    source_pod = read_json(POD_DIR / source / "pod_result.json")
    target_pod = read_json(POD_DIR / target / "pod_result.json")
    target_snapshot_ids, target_matrix = read_snapshot_matrix(POD_DIR / target / "snapshot_matrix.csv")

    source_coeffs = pod_temporal_coefficients(source_pod)[:mode_count, :]
    modes = np.column_stack([np.array(item["matrix"], dtype=float).reshape(-1) for item in epod["extended_modes"][:mode_count]])
    target_mean = np.array(target_pod["mean_field"], dtype=float).reshape(-1, 1)
    reconstruction = target_mean + modes @ source_coeffs

    idx = snapshot_index if snapshot_index >= 0 else len(target_snapshot_ids) + snapshot_index
    original = target_matrix[:, idx].reshape(5, 5)
    reconstructed = reconstruction[:, idx].reshape(5, 5)
    residual = original - reconstructed
    return original, reconstructed, residual, target_snapshot_ids[idx]


def plot_epod_reconstruction(direction: str, epod: dict[str, Any], mode_count: int = 3) -> Path:
    original, reconstructed, residual, snapshot_id = reconstruct_epod_snapshot(direction, epod, mode_count)
    vmax = max(float(np.max(original)), float(np.max(reconstructed)))
    residual_abs = max(float(np.max(np.abs(residual))), 1.0e-12)

    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.5), dpi=180)
    panels = [
        (original, "target original", "viridis", 0.0, vmax),
        (reconstructed, f"EPOD recon ({mode_count} modes)", "viridis", 0.0, vmax),
        (residual, "residual", "RdBu_r", -residual_abs, residual_abs),
    ]
    for ax, (matrix, title, cmap, vmin, vmax_local) in zip(axes, panels):
        image = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax_local, origin="upper")
        ax.set_title(title, fontsize=9)
        ax.set_xticks(range(5))
        ax.set_yticks(range(5))
        ax.tick_params(labelsize=7)
        for y in range(5):
            for x in range(5):
                value = float(matrix[y, x])
                ax.text(x, y, f"{value:.2g}", ha="center", va="center", fontsize=6.5, color="#111827")
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle(f"{direction.replace('_', ' ')} | snapshot {snapshot_id}")
    fig.tight_layout()
    out = FIGURES_DIR / f"epod_{direction}_snapshot_reconstruction_mode{mode_count}.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    pods = {dataset: read_json(POD_DIR / dataset / "pod_result.json") for dataset in POD_DATASETS}
    epods = {direction: read_json(EPOD_DIR / direction / "epod_result.json") for direction in EPOD_DIRECTIONS}

    written = [
        plot_pod_energy(pods),
        plot_epod_quality(epods),
    ]

    for dataset, pod in pods.items():
        written.append(plot_pod_modes(dataset, pod))
        written.append(plot_pod_temporal(dataset, pod))

    for direction, epod in epods.items():
        written.append(plot_epod_extended_modes(direction, epod))
        written.append(plot_epod_reconstruction(direction, epod, mode_count=3))

    for path in written:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
