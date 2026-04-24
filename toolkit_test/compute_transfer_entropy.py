from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
COHERENCE_DIR = ROOT / "results" / "coherence"
COHERENCE_SIGNALS = COHERENCE_DIR / "signals.csv"
RESULTS_DIR = ROOT / "results" / "transfer_entropy"
FIGURES_DIR = RESULTS_DIR / "figures"

DT = 0.05
MAX_LAG = 48
N_BINS = 5
N_SURROGATES = 60
TRUE_DELAY_SAMPLES = 7
RNG_SEED = 20260415


def format_float(value: float) -> str:
    return f"{value:.10g}"


def ensure_dirs() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def read_signal_csv(path: Path) -> dict[str, np.ndarray]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        names = list(reader.fieldnames or [])
    return {name: np.array([float(row[name]) for row in rows], dtype=float) for name in names}


def write_signal_csv(path: Path, signals: dict[str, np.ndarray]) -> None:
    names = list(signals.keys())
    n = len(next(iter(signals.values())))
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(names)
        for i in range(n):
            writer.writerow([format_float(float(signals[name][i])) for name in names])


def zscore(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    std = float(np.std(values))
    if std == 0.0:
        return values * 0.0
    return (values - float(np.mean(values))) / std


def quantile_discretize(values: np.ndarray, bins: int = N_BINS) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    quantiles = np.linspace(0.0, 100.0, bins + 1)
    edges = np.percentile(values, quantiles)
    edges = np.unique(edges)
    if len(edges) <= 2:
        return np.zeros_like(values, dtype=int)
    return np.searchsorted(edges[1:-1], values, side="right").astype(int)


def lagged_transfer_entropy(
    source: np.ndarray,
    target: np.ndarray,
    lag: int,
    *,
    bins: int = N_BINS,
) -> float:
    """Estimate I(target_t ; source_{t-lag} | target_{t-1}) in bits."""
    if lag < 1:
        raise ValueError("lag must be at least 1")
    if len(source) != len(target):
        raise ValueError("source and target must have equal length")
    if len(source) <= lag + 2:
        raise ValueError("signals are too short for the requested lag")

    xs = quantile_discretize(source, bins=bins)
    yt = quantile_discretize(target, bins=bins)

    joint_yf_yp_xp: Counter[tuple[int, int, int]] = Counter()
    joint_yp_xp: Counter[tuple[int, int]] = Counter()
    joint_yf_yp: Counter[tuple[int, int]] = Counter()
    count_yp: Counter[int] = Counter()

    for t in range(lag, len(source)):
        y_future = int(yt[t])
        y_past = int(yt[t - 1])
        x_past = int(xs[t - lag])
        joint_yf_yp_xp[(y_future, y_past, x_past)] += 1
        joint_yp_xp[(y_past, x_past)] += 1
        joint_yf_yp[(y_future, y_past)] += 1
        count_yp[y_past] += 1

    total = float(sum(joint_yf_yp_xp.values()))
    te = 0.0
    for (y_future, y_past, x_past), count_joint in joint_yf_yp_xp.items():
        denominator = joint_yp_xp[(y_past, x_past)] * joint_yf_yp[(y_future, y_past)]
        numerator = count_joint * count_yp[y_past]
        if denominator > 0 and numerator > 0:
            te += (count_joint / total) * np.log2(numerator / denominator)
    return float(max(te, 0.0))


def surrogate_statistics(
    source: np.ndarray,
    target: np.ndarray,
    lag: int,
    rng: np.random.Generator,
    *,
    bins: int = N_BINS,
    n_surrogates: int = N_SURROGATES,
) -> tuple[float, float]:
    surrogate_values = np.zeros(n_surrogates, dtype=float)
    for i in range(n_surrogates):
        shuffled = np.array(source, copy=True)
        rng.shuffle(shuffled)
        surrogate_values[i] = lagged_transfer_entropy(shuffled, target, lag, bins=bins)
    return float(np.mean(surrogate_values)), float(np.percentile(surrogate_values, 95.0))


def compute_te_curve(
    source: np.ndarray,
    target: np.ndarray,
    *,
    rng: np.random.Generator,
    max_lag: int = MAX_LAG,
    bins: int = N_BINS,
) -> dict[str, np.ndarray]:
    lags = np.arange(1, max_lag + 1, dtype=int)
    raw = np.zeros_like(lags, dtype=float)
    surrogate_mean = np.zeros_like(lags, dtype=float)
    surrogate_p95 = np.zeros_like(lags, dtype=float)

    for i, lag in enumerate(lags):
        raw[i] = lagged_transfer_entropy(source, target, int(lag), bins=bins)
        surrogate_mean[i], surrogate_p95[i] = surrogate_statistics(source, target, int(lag), rng, bins=bins)

    excess = np.maximum(raw - surrogate_mean, 0.0)
    return {
        "lag_samples": lags,
        "lag_time": lags.astype(float) * DT,
        "te_bits": raw,
        "surrogate_mean_bits": surrogate_mean,
        "surrogate_p95_bits": surrogate_p95,
        "excess_te_bits": excess,
    }


def peak_from_curve(curve: dict[str, np.ndarray]) -> dict[str, float]:
    index = int(np.argmax(curve["excess_te_bits"]))
    return {
        "lag_samples": float(curve["lag_samples"][index]),
        "lag_time": float(curve["lag_time"][index]),
        "te_bits": float(curve["te_bits"][index]),
        "surrogate_mean_bits": float(curve["surrogate_mean_bits"][index]),
        "surrogate_p95_bits": float(curve["surrogate_p95_bits"][index]),
        "excess_te_bits": float(curve["excess_te_bits"][index]),
    }


def delayed_causal_signals(base_signals: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(RNG_SEED + 17)
    time = np.asarray(base_signals["time"], dtype=float)
    source = np.zeros(len(time), dtype=float)
    source[0] = rng.normal(0.0, 1.0)
    for t in range(1, len(source)):
        source[t] = 0.22 * source[t - 1] + rng.normal(0.0, 1.0)
    source = zscore(source)

    target = np.zeros_like(source)
    target[:TRUE_DELAY_SAMPLES] = rng.normal(0.0, 0.08, TRUE_DELAY_SAMPLES)
    for t in range(TRUE_DELAY_SAMPLES, len(source)):
        delayed = source[t - TRUE_DELAY_SAMPLES]
        target[t] = (
            0.32 * target[t - 1]
            + 0.95 * np.tanh(1.10 * delayed)
            + 0.10 * delayed**2
            + rng.normal(0.0, 0.18)
        )
    target = zscore(target)

    independent = zscore(np.sin(2.0 * np.pi * 0.37 * time + 0.4) + rng.normal(0.0, 0.55, len(time)))
    return {
        "time": time,
        "u_driver": source,
        "q_response": target,
        "independent_control": independent,
    }


def compute_all_curves(base_signals: dict[str, np.ndarray], delayed_signals: dict[str, np.ndarray]) -> dict[str, dict[str, dict[str, np.ndarray]]]:
    rng = np.random.default_rng(RNG_SEED + 101)
    examples = {
        "current_common_driver": {
            "u_skew_to_q_skew": (base_signals["u_skew"], base_signals["q_skew"]),
            "q_skew_to_u_skew": (base_signals["q_skew"], base_signals["u_skew"]),
            "u_pod_a1_to_q_pod_a1": (base_signals["u_pod_a1"], base_signals["q_pod_a1"]),
            "q_pod_a1_to_u_pod_a1": (base_signals["q_pod_a1"], base_signals["u_pod_a1"]),
        },
        "delayed_causal": {
            "u_driver_to_q_response": (delayed_signals["u_driver"], delayed_signals["q_response"]),
            "q_response_to_u_driver": (delayed_signals["q_response"], delayed_signals["u_driver"]),
            "independent_to_q_response": (delayed_signals["independent_control"], delayed_signals["q_response"]),
        },
    }

    output: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    for example_name, pairs in examples.items():
        output[example_name] = {}
        for pair_name, (source, target) in pairs.items():
            output[example_name][pair_name] = compute_te_curve(source, target, rng=rng)
    return output


def write_curve_csv(path: Path, curves: dict[str, dict[str, np.ndarray]]) -> None:
    pair_names = list(curves.keys())
    lags = curves[pair_names[0]]["lag_samples"]
    lag_time = curves[pair_names[0]]["lag_time"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        header = ["lag_samples", "lag_time"]
        for pair_name in pair_names:
            header.extend(
                [
                    f"{pair_name}_te_bits",
                    f"{pair_name}_surrogate_mean_bits",
                    f"{pair_name}_surrogate_p95_bits",
                    f"{pair_name}_excess_te_bits",
                ]
            )
        writer.writerow(header)
        for i, lag in enumerate(lags):
            row = [int(lag), format_float(float(lag_time[i]))]
            for pair_name in pair_names:
                curve = curves[pair_name]
                row.extend(
                    [
                        format_float(float(curve["te_bits"][i])),
                        format_float(float(curve["surrogate_mean_bits"][i])),
                        format_float(float(curve["surrogate_p95_bits"][i])),
                        format_float(float(curve["excess_te_bits"][i])),
                    ]
                )
            writer.writerow(row)


def write_peak_summary(path: Path, all_curves: dict[str, dict[str, dict[str, np.ndarray]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for example_name, curves in all_curves.items():
        for pair_name, curve in curves.items():
            peak = peak_from_curve(curve)
            rows.append({"example": example_name, "pair": pair_name, **peak})

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: format_float(value) if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )
    return rows


def plot_te_current(curves: dict[str, dict[str, np.ndarray]]) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.5), dpi=180, sharey=True)
    panels = [
        ("u_skew_to_q_skew", "q_skew_to_u_skew", "current data: skew signals"),
        ("u_pod_a1_to_q_pod_a1", "q_pod_a1_to_u_pod_a1", "current data: POD a1 signals"),
    ]
    colors = ["#2563eb", "#dc2626"]
    for ax, (forward_name, reverse_name, title) in zip(axes, panels):
        for pair_name, color in zip([forward_name, reverse_name], colors):
            curve = curves[pair_name]
            label = pair_name.replace("_", " ")
            ax.plot(curve["lag_time"], curve["excess_te_bits"], color=color, lw=1.8, label=label)
            ax.plot(curve["lag_time"], curve["te_bits"], color=color, lw=0.8, alpha=0.32)
        ax.set_title(title)
        ax.set_xlabel("source lead time")
        ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
        ax.legend(frameon=False, fontsize=8)
    axes[0].set_ylabel("transfer entropy above shuffled-source baseline [bits]")
    fig.suptitle("Example 1: TE on current common-driver coherence data")
    fig.tight_layout()
    path = FIGURES_DIR / "te_example1_current_common_driver.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_te_delayed(curves: dict[str, dict[str, np.ndarray]]) -> Path:
    fig, ax = plt.subplots(figsize=(8.8, 4.8), dpi=180)
    colors = {
        "u_driver_to_q_response": "#2563eb",
        "q_response_to_u_driver": "#dc2626",
        "independent_to_q_response": "#78716c",
    }
    for pair_name, curve in curves.items():
        ax.plot(
            curve["lag_time"],
            curve["excess_te_bits"],
            color=colors[pair_name],
            lw=1.9,
            label=pair_name.replace("_", " "),
        )
    true_delay_time = TRUE_DELAY_SAMPLES * DT
    ax.axvline(true_delay_time, color="#111827", lw=1.1, ls="--")
    ax.text(true_delay_time + 0.015, 0.04, f"true delay = {TRUE_DELAY_SAMPLES} samples", rotation=90, va="bottom", fontsize=8)
    ax.set_xlabel("source lead time")
    ax.set_ylabel("transfer entropy above shuffled-source baseline [bits]")
    ax.set_title("Example 2: delayed causal response")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    path = FIGURES_DIR / "te_example2_delayed_causal.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_signal_examples(base_signals: dict[str, np.ndarray], delayed_signals: dict[str, np.ndarray]) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 6.0), dpi=180, sharex=False)
    current_time = base_signals["time"]
    delayed_time = delayed_signals["time"]
    current_mask = current_time <= 4.0
    delayed_mask = delayed_time <= 6.0

    axes[0].plot(current_time[current_mask], zscore(base_signals["u_skew"])[current_mask], color="#2563eb", lw=1.4, label="u_skew")
    axes[0].plot(current_time[current_mask], zscore(base_signals["q_skew"])[current_mask], color="#dc2626", lw=1.4, label="q_skew")
    axes[0].set_title("Example 1 signals: shared oscillator, ambiguous direction")
    axes[0].set_ylabel("normalized value")
    axes[0].legend(frameon=False, fontsize=8)

    axes[1].plot(delayed_time[delayed_mask], delayed_signals["u_driver"][delayed_mask], color="#2563eb", lw=1.4, label="u_driver")
    axes[1].plot(delayed_time[delayed_mask], delayed_signals["q_response"][delayed_mask], color="#dc2626", lw=1.4, label="q_response")
    axes[1].set_title("Example 2 signals: q is delayed response to U")
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("normalized value")
    axes[1].legend(frameon=False, fontsize=8)

    for ax in axes:
        ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
        ax.axhline(0.0, color="#44403c", lw=0.7)
    fig.tight_layout()
    path = FIGURES_DIR / "te_input_signals.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_peak_summary(rows: list[dict[str, Any]]) -> Path:
    selected_names = [
        ("current_common_driver", "u_skew_to_q_skew"),
        ("current_common_driver", "q_skew_to_u_skew"),
        ("delayed_causal", "u_driver_to_q_response"),
        ("delayed_causal", "q_response_to_u_driver"),
        ("delayed_causal", "independent_to_q_response"),
    ]
    row_map = {(row["example"], row["pair"]): row for row in rows}
    labels = [pair.replace("_", "\n") for _, pair in selected_names]
    values = [float(row_map[key]["excess_te_bits"]) for key in selected_names]
    colors = ["#2563eb", "#dc2626", "#2563eb", "#dc2626", "#78716c"]

    fig, ax = plt.subplots(figsize=(9.6, 4.8), dpi=180)
    bars = ax.bar(range(len(values)), values, color=colors, alpha=0.78)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2.0, value + 0.003, f"{value:.3f}", ha="center", fontsize=8)
    ax.set_xticks(range(len(labels)), labels, fontsize=8)
    ax.set_ylabel("max excess TE [bits]")
    ax.set_title("Maximum transfer entropy above shuffled-source baseline")
    ax.grid(True, axis="y", color="#d6d3d1", lw=0.6, alpha=0.85)
    fig.tight_layout()
    path = FIGURES_DIR / "te_peak_summary.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def write_summary_md(rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Transfer Entropy Demonstration",
        "",
        "This folder contains two transfer-entropy examples.",
        "",
        "Transfer entropy is estimated as a lagged conditional mutual information:",
        "",
        "```text",
        "TE_{X->Y}(lag) = I(Y_t ; X_{t-lag} | Y_{t-1})",
        "```",
        "",
        f"The continuous signals are discretized into `{N_BINS}` quantile bins.",
        f"A shuffled-source baseline with `{N_SURROGATES}` surrogates is subtracted to reduce finite-sample bias.",
        "",
        "## Peak Summary",
        "",
        "| example | pair | peak lag samples | peak lag time | TE | surrogate mean | excess TE |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['example']} | {row['pair']} | {float(row['lag_samples']):.0f} | "
            f"{float(row['lag_time']):.3f} | {float(row['te_bits']):.4f} | "
            f"{float(row['surrogate_mean_bits']):.4f} | {float(row['excess_te_bits']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Example 1 uses the existing coherence dataset. Since velocity and heat flux are driven by a shared synthetic oscillator, TE may appear in both directions and should be interpreted as directional predictability, not proof of physical causality.",
            "- Example 2 uses a delayed causal construction, where `q_response(t)` depends on `u_driver(t - tau)` plus its own memory and noise. The expected dominant direction is therefore `u_driver -> q_response` near the imposed delay.",
            "",
            "## Main Figures",
            "",
            "- `figures/te_input_signals.png`",
            "- `figures/te_example1_current_common_driver.png`",
            "- `figures/te_example2_delayed_causal.png`",
            "- `figures/te_peak_summary.png`",
        ]
    )
    (RESULTS_DIR / "transfer_entropy_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figure_readme() -> None:
    lines = [
        "# Transfer Entropy Figures",
        "",
        "- `te_input_signals.png` - representative signals for the common-driver and delayed-causal examples.",
        "- `te_example1_current_common_driver.png` - transfer entropy on the already generated coherence data.",
        "- `te_example2_delayed_causal.png` - transfer entropy for a constructed delayed response.",
        "- `te_peak_summary.png` - maximum excess transfer entropy for the most important directions.",
        "",
    ]
    (FIGURES_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    if not COHERENCE_SIGNALS.exists():
        raise FileNotFoundError(f"Missing {COHERENCE_SIGNALS}. Run compute_spectral_coherence.py first.")

    base_signals = read_signal_csv(COHERENCE_SIGNALS)
    delayed_signals = delayed_causal_signals(base_signals)
    all_curves = compute_all_curves(base_signals, delayed_signals)

    write_signal_csv(RESULTS_DIR / "delayed_causal_signals.csv", delayed_signals)
    write_curve_csv(RESULTS_DIR / "example1_current_common_driver_te.csv", all_curves["current_common_driver"])
    write_curve_csv(RESULTS_DIR / "example2_delayed_causal_te.csv", all_curves["delayed_causal"])
    rows = write_peak_summary(RESULTS_DIR / "transfer_entropy_peak_summary.csv", all_curves)
    write_summary_md(rows)

    figures = [
        plot_signal_examples(base_signals, delayed_signals),
        plot_te_current(all_curves["current_common_driver"]),
        plot_te_delayed(all_curves["delayed_causal"]),
        plot_peak_summary(rows),
    ]
    write_figure_readme()
    for figure in figures:
        print(f"Wrote {figure}")
    print(f"Wrote transfer entropy results to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
