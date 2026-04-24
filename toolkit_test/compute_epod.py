from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent
POD_DIR = ROOT / "results" / "pod"
EPOD_DIR = ROOT / "results" / "epod"


def format_float(value: float) -> str:
    return f"{value:.10g}"


def read_pod_result(name: str) -> dict[str, Any]:
    path = POD_DIR / name / "pod_result.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_snapshot_matrix(name: str, filename: str) -> tuple[list[str], np.ndarray]:
    path = POD_DIR / name / filename
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        snapshot_ids = fieldnames[3:]
        rows = list(reader)
    matrix = np.array([[float(row[snapshot_id]) for snapshot_id in snapshot_ids] for row in rows], dtype=float)
    return snapshot_ids, matrix


def write_matrix_csv(path: Path, matrix: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["y/x", "0", "1", "2", "3", "4"])
        for y, row in enumerate(matrix.reshape(5, 5)):
            writer.writerow([y, *[format_float(float(value)) for value in row]])


def write_snapshot_matrix_csv(path: Path, snapshot_ids: list[str], matrix: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["cell_id", "y", "x", *snapshot_ids])
        for flat_idx in range(matrix.shape[0]):
            y, x = divmod(flat_idx, 5)
            writer.writerow(
                [
                    f"c{y}{x}",
                    y,
                    x,
                    *[format_float(float(value)) for value in matrix[flat_idx, :]],
                ]
            )


def write_mode_metrics_csv(path: Path, metrics: list[dict[str, float | int]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "mode_count",
                "relative_error_centered_target",
                "captured_target_energy_fraction",
                "captured_target_energy_percent",
            ],
        )
        writer.writeheader()
        for row in metrics:
            writer.writerow(
                {
                    "mode_count": row["mode_count"],
                    "relative_error_centered_target": format_float(float(row["relative_error_centered_target"])),
                    "captured_target_energy_fraction": format_float(float(row["captured_target_energy_fraction"])),
                    "captured_target_energy_percent": format_float(float(row["captured_target_energy_percent"])),
                }
            )


def temporal_coefficients_from_pod(pod: dict[str, Any]) -> np.ndarray:
    rows = pod["temporal_coefficients"]
    return np.array([row["coefficients"] for row in rows], dtype=float)


def compute_epod(source_name: str, target_name: str, out_name: str) -> dict[str, Any]:
    source_pod = read_pod_result(source_name)
    target_pod = read_pod_result(target_name)
    source_snapshot_ids, _ = read_snapshot_matrix(source_name, "centered_snapshot_matrix.csv")
    target_snapshot_ids, target_centered = read_snapshot_matrix(target_name, "centered_snapshot_matrix.csv")

    if len(source_snapshot_ids) != len(target_snapshot_ids):
        raise ValueError("Source and target datasets must have the same number of paired snapshots")

    source_coefficients = temporal_coefficients_from_pod(source_pod)
    active_modes = int(source_pod["active_mode_count"])
    source_coefficients = source_coefficients[:active_modes, :]

    # Least-squares extended modes: target fluctuations ~= Psi * source temporal coefficients.
    gram = source_coefficients @ source_coefficients.T
    extended_modes = target_centered @ source_coefficients.T @ np.linalg.pinv(gram)

    target_norm = float(np.linalg.norm(target_centered))
    metrics: list[dict[str, float | int]] = []
    reconstructions: dict[int, np.ndarray] = {}
    for mode_count in range(1, active_modes + 1):
        coefficients_k = source_coefficients[:mode_count, :]
        modes_k = extended_modes[:, :mode_count]
        reconstruction = modes_k @ coefficients_k
        reconstructions[mode_count] = reconstruction
        error = float(np.linalg.norm(target_centered - reconstruction))
        rel_error = error / target_norm if target_norm > 0.0 else 0.0
        captured = 1.0 - rel_error**2
        metrics.append(
            {
                "mode_count": mode_count,
                "relative_error_centered_target": rel_error,
                "captured_target_energy_fraction": captured,
                "captured_target_energy_percent": 100.0 * captured,
            }
        )

    target_mean = np.array(target_pod["mean_field"], dtype=float).reshape(-1, 1)
    full_centered_reconstruction = reconstructions[active_modes]
    full_reconstruction = target_mean + full_centered_reconstruction

    out_dir = EPOD_DIR / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    for mode_idx in range(active_modes):
        write_matrix_csv(out_dir / f"extended_mode_{mode_idx + 1:02d}.csv", extended_modes[:, mode_idx])
    write_snapshot_matrix_csv(out_dir / "target_centered_reconstruction_all_modes.csv", target_snapshot_ids, full_centered_reconstruction)
    write_snapshot_matrix_csv(out_dir / "target_reconstruction_all_modes.csv", target_snapshot_ids, full_reconstruction)
    write_mode_metrics_csv(out_dir / "reconstruction_metrics.csv", metrics)

    summary = {
        "direction": out_name,
        "source_dataset": source_name,
        "target_dataset": target_name,
        "source_snapshot_ids": source_snapshot_ids,
        "target_snapshot_ids": target_snapshot_ids,
        "active_source_modes": active_modes,
        "formula": "Psi = Y_centered A_source^T (A_source A_source^T)^(-1)",
        "target_reconstruction": "Y_centered_hat = Psi A_source",
        "metrics": metrics,
        "extended_modes": [
            {
                "mode": mode_idx + 1,
                "matrix": extended_modes[:, mode_idx].reshape(5, 5).tolist(),
            }
            for mode_idx in range(active_modes)
        ],
    }
    (out_dir / "epod_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary | {"out_dir": str(out_dir)}


def write_summary(results: list[dict[str, Any]]) -> None:
    lines = [
        "# EPOD Results Summary",
        "",
        "EPOD is computed between the synchronized synthetic velocity and wall heat-flux datasets.",
        "",
        "Here EPOD means: take the temporal coefficients from the POD of one field and use them to reconstruct correlated modes of the other field.",
        "",
        "For source field `X` and target field `Y`:",
        "",
        "```text",
        "X' = U Sigma V^T",
        "A = Sigma V^T",
        "Psi = Y' A^T (A A^T)^(-1)",
        "Y'_hat = Psi A",
        "```",
        "",
        "`Psi` contains the extended spatial modes of the target field associated with the source-field temporal POD coefficients.",
        "",
        "## Reconstruction Metrics",
        "",
        "| direction | source | target | modes used | relative error | captured target energy |",
        "|---|---|---|---:|---:|---:|",
    ]
    for result in results:
        for metric in result["metrics"]:
            lines.append(
                f"| {result['direction']} | {result['source_dataset']} | {result['target_dataset']} | "
                f"{metric['mode_count']} | {float(metric['relative_error_centered_target']):.6g} | "
                f"{float(metric['captured_target_energy_percent']):.3f}% |"
            )
    lines.extend(
        [
            "",
            "## Output Folders",
            "",
            "- `results/epod/velocity_to_heat_flux/`",
            "- `results/epod/heat_flux_to_velocity/`",
        ]
    )
    (EPOD_DIR / "epod_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    EPOD_DIR.mkdir(parents=True, exist_ok=True)
    results = [
        compute_epod("velocity", "heat_flux", "velocity_to_heat_flux"),
        compute_epod("heat_flux", "velocity", "heat_flux_to_velocity"),
    ]
    write_summary(results)
    for result in results:
        last_metric = result["metrics"][-1]
        print(
            f"{result['direction']}: {result['source_dataset']} -> {result['target_dataset']}, "
            f"all-mode relative error={float(last_metric['relative_error_centered_target']):.3e}"
        )


if __name__ == "__main__":
    main()
