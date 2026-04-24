from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results" / "resolvent"
FIGURES_DIR = RESULTS_DIR / "figures"

GRID_SHAPE = (5, 5)
F0 = 1.25
F2 = 2.0 * F0
OMEGA0 = 2.0 * np.pi * F0
OMEGA2 = 2.0 * np.pi * F2


def format_float(value: float) -> str:
    return f"{value:.10g}"


def ensure_dirs() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def normalize(field: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(field.reshape(-1)))
    if norm == 0.0:
        return field.copy()
    return field / norm


def write_matrix_csv(path: Path, matrix: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["y/x", "0", "1", "2", "3", "4"])
        for y, row in enumerate(matrix):
            writer.writerow([y, *[format_float(float(value)) for value in row]])


def build_physical_bases() -> dict[str, np.ndarray]:
    u_skew = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, -0.45, -0.10, 0.55, 0.0],
            [0.0, -1.10, 0.00, 1.20, 0.0],
            [0.0, -0.50, -0.05, 0.45, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    u_vertical = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.45, 0.75, 0.35, 0.0],
            [0.0, 0.05, 0.00, -0.05, 0.0],
            [0.0, -0.35, -0.75, -0.45, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    u_breathing = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.35, 0.50, 0.35, 0.0],
            [0.0, 0.50, 0.85, 0.50, 0.0],
            [0.0, 0.35, 0.50, 0.35, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    u_diagonal = np.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.40, 0.10, -0.30, 0.0],
            [0.0, 0.15, 0.00, 0.15, 0.0],
            [0.0, -0.30, 0.10, 0.40, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    q_skew = np.array(
        [
            [0.25, 0.20, 0.00, -0.20, -0.25],
            [0.80, 0.00, 0.00, 0.00, -0.80],
            [1.35, 0.00, 0.00, 0.00, -1.35],
            [0.80, 0.00, 0.00, 0.00, -0.80],
            [0.25, 0.20, 0.00, -0.20, -0.25],
        ],
        dtype=float,
    )
    q_diagonal = np.array(
        [
            [0.75, 0.40, 0.00, -0.35, -0.65],
            [0.35, 0.00, 0.00, 0.00, -0.20],
            [0.00, 0.00, 0.00, 0.00, 0.00],
            [-0.20, 0.00, 0.00, 0.00, 0.35],
            [-0.65, -0.35, 0.00, 0.40, 0.75],
        ],
        dtype=float,
    )
    q_mean = np.array(
        [
            [0.70, 0.90, 1.10, 0.90, 0.70],
            [0.90, 0.00, 0.00, 0.00, 0.90],
            [1.20, 0.00, 0.00, 0.00, 1.20],
            [0.90, 0.00, 0.00, 0.00, 0.90],
            [0.70, 0.90, 1.10, 0.90, 0.70],
        ],
        dtype=float,
    )
    q_local = np.array(
        [
            [0.00, 0.45, 0.90, 0.45, 0.00],
            [-0.20, 0.00, 0.00, 0.00, -0.20],
            [-0.35, 0.00, 0.00, 0.00, -0.35],
            [-0.20, 0.00, 0.00, 0.00, -0.20],
            [0.00, 0.45, 0.90, 0.45, 0.00],
        ],
        dtype=float,
    )

    return {
        "u_skew": normalize(u_skew),
        "u_vertical": normalize(u_vertical),
        "u_breathing": normalize(u_breathing),
        "u_diagonal": normalize(u_diagonal),
        "q_skew": normalize(q_skew),
        "q_diagonal": normalize(q_diagonal),
        "q_mean": normalize(q_mean),
        "q_local": normalize(q_local),
    }


def build_linear_model() -> dict[str, np.ndarray]:
    """Return a tiny stable linear model for a resolvent demonstration.

    The model is intentionally modal:

        da/dt = A a + B f
        y     = C a

    where y contains a projected velocity field and wall heat-flux field.
    """
    bases = build_physical_bases()

    damping_1 = 0.55
    damping_2 = 1.05
    a_matrix = np.array(
        [
            [-damping_1, -OMEGA0, 0.0, 0.0],
            [OMEGA0, -damping_1, 0.0, 0.0],
            [0.0, 0.0, -damping_2, -OMEGA2],
            [0.0, 0.0, OMEGA2, -damping_2],
        ],
        dtype=float,
    )
    b_matrix = np.diag([1.0, 1.0, 0.75, 0.75])

    # Output vector order: first 25 values are velocity, next 25 are wall heat flux.
    c_matrix = np.zeros((50, 4), dtype=float)
    u_fields = [
        1.00 * bases["u_skew"],
        0.90 * bases["u_vertical"],
        0.65 * bases["u_breathing"],
        0.40 * bases["u_diagonal"],
    ]
    q_fields = [
        0.75 * bases["q_skew"],
        0.55 * bases["q_diagonal"],
        0.95 * bases["q_mean"],
        0.30 * bases["q_local"],
    ]
    for mode in range(4):
        c_matrix[:25, mode] = u_fields[mode].reshape(-1)
        c_matrix[25:, mode] = q_fields[mode].reshape(-1)

    return {"A": a_matrix, "B": b_matrix, "C": c_matrix}


def resolvent(model: dict[str, np.ndarray], frequency_hz: float) -> np.ndarray:
    a_matrix = model["A"]
    b_matrix = model["B"]
    c_matrix = model["C"]
    omega = 2.0 * np.pi * frequency_hz
    identity = np.eye(a_matrix.shape[0], dtype=complex)
    return c_matrix @ np.linalg.solve(1j * omega * identity - a_matrix, b_matrix)


def phase_align(vector: np.ndarray) -> tuple[np.ndarray, complex]:
    pivot = int(np.argmax(np.abs(vector)))
    if np.abs(vector[pivot]) == 0.0:
        return vector, 1.0 + 0.0j
    phase = np.exp(-1j * np.angle(vector[pivot]))
    return vector * phase, phase


def split_physical(vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    velocity = np.asarray(vector[:25]).reshape(GRID_SHAPE)
    heat_flux = np.asarray(vector[25:]).reshape(GRID_SHAPE)
    return velocity, heat_flux


def frequency_sweep(model: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    frequencies = np.linspace(0.05, 5.0, 500)
    singular_values = np.zeros((len(frequencies), 4), dtype=float)
    for i, frequency in enumerate(frequencies):
        _, s_values, _ = np.linalg.svd(resolvent(model, float(frequency)), full_matrices=False)
        singular_values[i, :] = s_values
    return {"frequency_Hz": frequencies, "singular_values": singular_values}


def peak_near(frequencies: np.ndarray, values: np.ndarray, target: float, width: float = 0.35) -> tuple[float, float]:
    mask = (frequencies >= target - width) & (frequencies <= target + width)
    local_indices = np.where(mask)[0]
    if len(local_indices) == 0:
        index = int(np.argmax(values))
    else:
        index = int(local_indices[np.argmax(values[local_indices])])
    return float(frequencies[index]), float(values[index])


def write_gain_csv(path: Path, sweep: dict[str, np.ndarray]) -> None:
    frequencies = sweep["frequency_Hz"]
    singular_values = sweep["singular_values"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["frequency_Hz", "omega_rad_s", "sigma_1", "sigma_2", "sigma_3", "sigma_4"])
        for frequency, s_values in zip(frequencies, singular_values):
            writer.writerow(
                [
                    format_float(float(frequency)),
                    format_float(float(2.0 * np.pi * frequency)),
                    *[format_float(float(value)) for value in s_values],
                ]
            )


def write_peak_summary(path: Path, sweep: dict[str, np.ndarray]) -> list[dict[str, float | str]]:
    frequencies = sweep["frequency_Hz"]
    sigma_1 = sweep["singular_values"][:, 0]
    rows = []
    for label, target in [("base_frequency_f0", F0), ("second_harmonic_2f0", F2)]:
        peak_frequency, peak_gain = peak_near(frequencies, sigma_1, target)
        rows.append(
            {
                "label": label,
                "target_frequency_Hz": target,
                "peak_frequency_Hz": peak_frequency,
                "peak_sigma_1": peak_gain,
            }
        )
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_float(value) if isinstance(value, float) else value for key, value in row.items()})
    return rows


def mode_at_frequency(model: dict[str, np.ndarray], frequency: float) -> dict[str, np.ndarray | float]:
    h_matrix = resolvent(model, frequency)
    response_modes, singular_values, vh = np.linalg.svd(h_matrix, full_matrices=False)
    forcing_modal = vh.conj().T[:, 0]
    response_mode = response_modes[:, 0]
    response_mode, phase = phase_align(response_mode)
    forcing_modal = forcing_modal * phase

    forcing_projected = model["C"] @ (model["B"] @ forcing_modal)
    forcing_projected, _ = phase_align(forcing_projected)

    response_u, response_q = split_physical(response_mode)
    forcing_u, forcing_q = split_physical(forcing_projected)

    return {
        "frequency_Hz": frequency,
        "singular_values": singular_values,
        "forcing_modal": forcing_modal,
        "response_velocity": response_u,
        "response_heat_flux": response_q,
        "forcing_velocity": forcing_u,
        "forcing_heat_flux": forcing_q,
    }


def write_mode_outputs(label: str, mode: dict[str, np.ndarray | float]) -> None:
    for field_name in ["forcing_velocity", "forcing_heat_flux", "response_velocity", "response_heat_flux"]:
        matrix = np.asarray(mode[field_name])
        write_matrix_csv(RESULTS_DIR / f"{label}_{field_name}_real.csv", matrix.real)
        write_matrix_csv(RESULTS_DIR / f"{label}_{field_name}_abs.csv", np.abs(matrix))
        write_matrix_csv(RESULTS_DIR / f"{label}_{field_name}_phase_rad.csv", np.angle(matrix))


def plot_gain_curves(sweep: dict[str, np.ndarray]) -> Path:
    frequencies = sweep["frequency_Hz"]
    singular_values = sweep["singular_values"]
    fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=180)
    colors = ["#2563eb", "#0f766e", "#b45309", "#7c3aed"]
    for mode in range(4):
        ax.plot(frequencies, singular_values[:, mode], color=colors[mode], lw=1.7, label=f"sigma {mode + 1}")
    ax.axvline(F0, color="#111827", ls="--", lw=1.0)
    ax.axvline(F2, color="#111827", ls=":", lw=1.2)
    ax.text(F0 + 0.03, ax.get_ylim()[1] * 0.75, f"f0 = {F0:.2f}", rotation=90, fontsize=8)
    ax.text(F2 + 0.03, ax.get_ylim()[1] * 0.75, f"2f0 = {F2:.2f}", rotation=90, fontsize=8)
    ax.text(
        0.98,
        0.10,
        r"$H(\omega)=C(i\omega I-A)^{-1}B$",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#a8a29e", "alpha": 0.92},
    )
    ax.set_xlabel("frequency")
    ax.set_ylabel("resolvent gain")
    ax.set_title("Resolvent singular values")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    path = FIGURES_DIR / "resolvent_gain_curves.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_mode_shapes(label: str, mode: dict[str, np.ndarray | float]) -> Path:
    panels = [
        ("forcing velocity", np.asarray(mode["forcing_velocity"]).real),
        ("forcing heat flux", np.asarray(mode["forcing_heat_flux"]).real),
        ("response velocity", np.asarray(mode["response_velocity"]).real),
        ("response heat flux", np.asarray(mode["response_heat_flux"]).real),
    ]
    vmax = max(float(np.max(np.abs(matrix))) for _, matrix in panels)
    fig, axes = plt.subplots(1, 4, figsize=(13.0, 3.6), dpi=180)
    for ax, (title, matrix) in zip(axes, panels):
        image = ax.imshow(matrix, origin="upper", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
        ax.set_title(title, fontsize=9)
        ax.set_xticks(range(5))
        ax.set_yticks(range(5))
        ax.tick_params(labelsize=7)
        for y in range(5):
            for x in range(5):
                value = float(matrix[y, x])
                text_color = "white" if abs(value) > 0.55 * vmax else "#111827"
                ax.text(x, y, f"{value:.2g}", ha="center", va="center", fontsize=6.2, color=text_color)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    frequency = float(mode["frequency_Hz"])
    sigma_1 = float(np.asarray(mode["singular_values"])[0])
    fig.suptitle(f"Leading resolvent mode at {frequency:.2f} Hz, sigma1 = {sigma_1:.3f}")
    fig.tight_layout()
    path = FIGURES_DIR / f"resolvent_mode_shapes_{label}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_mode_phase(label: str, mode: dict[str, np.ndarray | float]) -> Path:
    panels = [
        ("response velocity phase", np.angle(np.asarray(mode["response_velocity"]))),
        ("response heat flux phase", np.angle(np.asarray(mode["response_heat_flux"]))),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.7), dpi=180)
    for ax, (title, matrix) in zip(axes, panels):
        image = ax.imshow(matrix, origin="upper", cmap="twilight", vmin=-np.pi, vmax=np.pi)
        ax.set_title(title, fontsize=9)
        ax.set_xticks(range(5))
        ax.set_yticks(range(5))
        ax.tick_params(labelsize=7)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle(f"Response phase at {float(mode['frequency_Hz']):.2f} Hz")
    fig.tight_layout()
    path = FIGURES_DIR / f"resolvent_response_phase_{label}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def write_summary_md(peak_rows: list[dict[str, float | str]], modes: dict[str, dict[str, np.ndarray | float]]) -> None:
    lines = [
        "# Resolvent Analysis Demonstration",
        "",
        "This is a small educational resolvent-analysis example, not a full OpenFOAM linearization.",
        "",
        "The linear model is:",
        "",
        "```text",
        "da/dt = A a + B f",
        "y     = C a",
        "H(w)  = C(i w I - A)^(-1) B",
        "```",
        "",
        "The state `a` contains two damped oscillators:",
        "",
        f"- base oscillator near `f0 = {F0}`",
        f"- second oscillator near `2f0 = {F2}`",
        "",
        "For each frequency, SVD is applied to `H(w)`:",
        "",
        "```text",
        "H(w) = U Sigma V*",
        "```",
        "",
        "- columns of `V` are optimal forcing directions",
        "- columns of `U` are optimal response directions",
        "- singular values `Sigma` are amplification gains",
        "",
        "## Gain Peaks",
        "",
        "| label | target frequency | peak frequency | leading gain |",
        "|---|---:|---:|---:|",
    ]
    for row in peak_rows:
        lines.append(
            f"| {row['label']} | {float(row['target_frequency_Hz']):.3f} | "
            f"{float(row['peak_frequency_Hz']):.3f} | {float(row['peak_sigma_1']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Stored Leading Modes",
            "",
            "| label | frequency | sigma1 |",
            "|---|---:|---:|",
        ]
    )
    for label, mode in modes.items():
        sigma_1 = float(np.asarray(mode["singular_values"])[0])
        lines.append(f"| {label} | {float(mode['frequency_Hz']):.3f} | {sigma_1:.4f} |")
    lines.extend(
        [
            "",
            "## Main Figures",
            "",
            "- `figures/resolvent_gain_curves.png`",
            "- `figures/resolvent_mode_shapes_f0.png`",
            "- `figures/resolvent_mode_shapes_2f0.png`",
            "- `figures/resolvent_response_phase_f0.png`",
            "- `figures/resolvent_response_phase_2f0.png`",
        ]
    )
    (RESULTS_DIR / "resolvent_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figure_readme() -> None:
    lines = [
        "# Resolvent Figures",
        "",
        "- `resolvent_gain_curves.png` - leading singular values of the resolvent operator versus frequency.",
        "- `resolvent_mode_shapes_f0.png` - optimal forcing and response pattern at the base frequency.",
        "- `resolvent_mode_shapes_2f0.png` - optimal forcing and response pattern at the second harmonic.",
        "- `resolvent_response_phase_f0.png` - phase of the leading response mode at the base frequency.",
        "- `resolvent_response_phase_2f0.png` - phase of the leading response mode at the second harmonic.",
        "",
    ]
    (FIGURES_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    model = build_linear_model()
    sweep = frequency_sweep(model)
    write_gain_csv(RESULTS_DIR / "resolvent_gain.csv", sweep)
    peak_rows = write_peak_summary(RESULTS_DIR / "resolvent_peak_summary.csv", sweep)

    modes = {
        "f0": mode_at_frequency(model, F0),
        "2f0": mode_at_frequency(model, F2),
    }
    for label, mode in modes.items():
        write_mode_outputs(label, mode)

    figures = [
        plot_gain_curves(sweep),
        plot_mode_shapes("f0", modes["f0"]),
        plot_mode_shapes("2f0", modes["2f0"]),
        plot_mode_phase("f0", modes["f0"]),
        plot_mode_phase("2f0", modes["2f0"]),
    ]
    write_summary_md(peak_rows, modes)
    write_figure_readme()

    for figure in figures:
        print(f"Wrote {figure}")
    print(f"Wrote resolvent results to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
