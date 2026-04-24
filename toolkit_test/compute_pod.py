from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results" / "pod"

DATASETS = [
    {
        "name": "velocity",
        "path": DATA_DIR / "velocity_snapshots_5x5.json",
        "value_prefix": "u",
    },
    {
        "name": "heat_flux",
        "path": DATA_DIR / "heat_flux_wall_snapshots_5x5.json",
        "value_prefix": "q",
    },
]


def format_float(value: float) -> str:
    return f"{value:.10g}"


def matrix_to_rows(matrix: np.ndarray) -> list[list[str]]:
    return [[format_float(float(value)) for value in row] for row in matrix]


def write_matrix_csv(path: Path, matrix: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["y/x", "0", "1", "2", "3", "4"])
        for y, row in enumerate(matrix):
            writer.writerow([y, *[format_float(float(value)) for value in row]])


def write_snapshot_matrix_csv(path: Path, snapshot_ids: list[str], snapshots: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["cell_id", "y", "x", *snapshot_ids])
        for flat_idx in range(snapshots.shape[0]):
            y, x = divmod(flat_idx, 5)
            writer.writerow(
                [
                    f"c{y}{x}",
                    y,
                    x,
                    *[format_float(float(value)) for value in snapshots[flat_idx, :]],
                ]
            )


def write_singular_values_csv(
    path: Path,
    singular_values: np.ndarray,
    energy_fraction: np.ndarray,
    cumulative_energy: np.ndarray,
    active_count: int,
) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["mode", "singular_value", "energy_fraction", "cumulative_energy", "active"])
        for i, singular_value in enumerate(singular_values, start=1):
            writer.writerow(
                [
                    i,
                    format_float(float(singular_value)),
                    format_float(float(energy_fraction[i - 1])),
                    format_float(float(cumulative_energy[i - 1])),
                    "yes" if i <= active_count else "no",
                ]
            )


def write_temporal_coefficients_csv(path: Path, snapshot_ids: list[str], coefficients: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["mode", *snapshot_ids])
        for i in range(coefficients.shape[0]):
            writer.writerow([i + 1, *[format_float(float(value)) for value in coefficients[i, :]]])


def load_dataset(path: Path) -> tuple[dict[str, Any], list[str], list[float], np.ndarray]:
    with path.open("r", encoding="utf-8") as fh:
        dataset = json.load(fh)
    snapshot_ids = [snap["id"] for snap in dataset["snapshots"]]
    times = [float(snap["time"]) for snap in dataset["snapshots"]]
    columns = []
    for snap in dataset["snapshots"]:
        matrix = np.array(snap["matrix"], dtype=float)
        if matrix.shape != (5, 5):
            raise ValueError(f"Unexpected matrix shape for {snap['id']}: {matrix.shape}")
        columns.append(matrix.reshape(-1))
    snapshot_matrix = np.column_stack(columns)
    return dataset, snapshot_ids, times, snapshot_matrix


def enforce_deterministic_signs(
    modes: np.ndarray,
    temporal_coefficients: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    modes = modes.copy()
    temporal_coefficients = temporal_coefficients.copy()
    for mode_idx in range(modes.shape[1]):
        col = modes[:, mode_idx]
        pivot = int(np.argmax(np.abs(col)))
        if col[pivot] < 0.0:
            modes[:, mode_idx] *= -1.0
            temporal_coefficients[mode_idx, :] *= -1.0
    return modes, temporal_coefficients


def compute_pod(snapshot_matrix: np.ndarray) -> dict[str, np.ndarray | int]:
    mean_vector = snapshot_matrix.mean(axis=1, keepdims=True)
    centered = snapshot_matrix - mean_vector
    modes, singular_values, vt = np.linalg.svd(centered, full_matrices=False)
    temporal_coefficients = np.diag(singular_values) @ vt
    modes, temporal_coefficients = enforce_deterministic_signs(modes, temporal_coefficients)

    energy = singular_values**2
    energy_sum = float(energy.sum())
    if energy_sum > 0.0:
        energy_fraction = energy / energy_sum
        cumulative_energy = np.cumsum(energy_fraction)
    else:
        energy_fraction = np.zeros_like(singular_values)
        cumulative_energy = np.zeros_like(singular_values)

    tolerance = max(1.0e-12, float(singular_values[0]) * 1.0e-10) if singular_values.size else 1.0e-12
    active_count = int(np.sum(singular_values > tolerance))

    return {
        "mean_vector": mean_vector[:, 0],
        "centered_matrix": centered,
        "spatial_modes": modes,
        "singular_values": singular_values,
        "temporal_coefficients": temporal_coefficients,
        "energy_fraction": energy_fraction,
        "cumulative_energy": cumulative_energy,
        "active_count": active_count,
    }


def write_json_result(
    path: Path,
    dataset_name: str,
    snapshot_ids: list[str],
    times: list[float],
    pod: dict[str, np.ndarray | int],
) -> None:
    active_count = int(pod["active_count"])
    modes = np.asarray(pod["spatial_modes"])[:, :active_count]
    temporal_coefficients = np.asarray(pod["temporal_coefficients"])[:active_count, :]
    result = {
        "dataset": dataset_name,
        "snapshot_ids": snapshot_ids,
        "times": times,
        "matrix_convention": "columns are flattened row-major 5x5 snapshots",
        "mean_field": np.asarray(pod["mean_vector"]).reshape(5, 5).tolist(),
        "singular_values": np.asarray(pod["singular_values"]).tolist(),
        "energy_fraction": np.asarray(pod["energy_fraction"]).tolist(),
        "cumulative_energy": np.asarray(pod["cumulative_energy"]).tolist(),
        "active_mode_count": active_count,
        "spatial_modes": [
            {
                "mode": i + 1,
                "matrix": modes[:, i].reshape(5, 5).tolist(),
            }
            for i in range(active_count)
        ],
        "temporal_coefficients": [
            {
                "mode": i + 1,
                "coefficients": temporal_coefficients[i, :].tolist(),
            }
            for i in range(active_count)
        ],
    }
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")


def run_dataset(config: dict[str, Any]) -> dict[str, Any]:
    dataset, snapshot_ids, times, snapshot_matrix = load_dataset(Path(config["path"]))
    pod = compute_pod(snapshot_matrix)
    name = str(config["name"])
    out_dir = RESULTS_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    write_snapshot_matrix_csv(out_dir / "snapshot_matrix.csv", snapshot_ids, snapshot_matrix)
    write_snapshot_matrix_csv(out_dir / "centered_snapshot_matrix.csv", snapshot_ids, np.asarray(pod["centered_matrix"]))
    write_matrix_csv(out_dir / "mean_field.csv", np.asarray(pod["mean_vector"]).reshape(5, 5))
    write_singular_values_csv(
        out_dir / "singular_values.csv",
        np.asarray(pod["singular_values"]),
        np.asarray(pod["energy_fraction"]),
        np.asarray(pod["cumulative_energy"]),
        int(pod["active_count"]),
    )
    write_temporal_coefficients_csv(
        out_dir / "temporal_coefficients.csv",
        snapshot_ids,
        np.asarray(pod["temporal_coefficients"])[: int(pod["active_count"]), :],
    )

    modes = np.asarray(pod["spatial_modes"])
    for mode_idx in range(int(pod["active_count"])):
        write_matrix_csv(out_dir / f"spatial_mode_{mode_idx + 1:02d}.csv", modes[:, mode_idx].reshape(5, 5))

    write_json_result(out_dir / "pod_result.json", name, snapshot_ids, times, pod)

    return {
        "name": name,
        "path": out_dir,
        "active_count": int(pod["active_count"]),
        "singular_values": np.asarray(pod["singular_values"]),
        "energy_fraction": np.asarray(pod["energy_fraction"]),
        "cumulative_energy": np.asarray(pod["cumulative_energy"]),
    }


def write_summary(results: list[dict[str, Any]]) -> None:
    lines = [
        "# POD Results Summary",
        "",
        "POD is computed independently for the synthetic velocity field and the synthetic wall heat-flux field.",
        "",
        "For each dataset, the snapshot matrix uses row-major flattened `5x5` fields as columns:",
        "",
        "```text",
        "X = [x_1, x_2, x_3, x_4, x_5]",
        "```",
        "",
        "The temporal mean is subtracted before SVD:",
        "",
        "```text",
        "X' = X - mean(X)",
        "X' = U Sigma V^T",
        "```",
        "",
        "Interpretation:",
        "",
        "- `mean_field.csv` is the temporal mean field reshaped back to `5x5`.",
        "- `spatial_mode_XX.csv` is one normalized spatial POD mode reshaped to `5x5`.",
        "- `temporal_coefficients.csv` contains `Sigma V^T`, i.e. the amplitude of each mode in each snapshot.",
        "- `singular_values.csv` contains modal energy fractions, computed from `sigma_i^2 / sum(sigma^2)`.",
        "",
        "## Modal Energy",
        "",
        "| dataset | active modes | mode | singular value | energy fraction | cumulative energy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        singular_values = result["singular_values"]
        energy_fraction = result["energy_fraction"]
        cumulative_energy = result["cumulative_energy"]
        for i in range(result["active_count"]):
            lines.append(
                f"| {result['name']} | {result['active_count']} | {i + 1} | "
                f"{float(singular_values[i]):.6g} | {100.0 * float(energy_fraction[i]):.3f}% | "
                f"{100.0 * float(cumulative_energy[i]):.3f}% |"
            )
    lines.extend(
        [
            "",
            "## Output Folders",
            "",
            "- `results/pod/velocity/`",
            "- `results/pod/heat_flux/`",
        ]
    )
    (RESULTS_DIR / "pod_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = [run_dataset(config) for config in DATASETS]
    write_summary(results)
    for result in results:
        print(f"{result['name']}: active_modes={result['active_count']} -> {result['path']}")


if __name__ == "__main__":
    main()
