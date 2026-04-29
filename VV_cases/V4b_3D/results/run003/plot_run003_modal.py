from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "figures"
FIELDS = ("Ux", "Uy", "T")
SHED_F = 3.125


def ensure_fig_dir() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def as_float(rows: list[dict[str, str]], key: str) -> np.ndarray:
    return np.array([float(row[key]) for row in rows], dtype=float)


def temporal_from_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rows = read_csv(path)
    headers = list(rows[0].keys())
    time_headers = headers[1:]
    times = np.array([float(h.split("=", 1)[1]) for h in time_headers], dtype=float)
    coeffs = np.array([[float(row[h]) for h in time_headers] for row in rows], dtype=float)
    return times, coeffs


def plot_pod_energy() -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.0), dpi=180, sharey=True)
    colors = {"Ux": "#2563eb", "Uy": "#0f766e", "T": "#dc2626"}
    for ax, field in zip(axes, FIELDS):
        rows = read_csv(ROOT / "pod" / field / "singular_values.csv")
        modes = as_float(rows, "mode")
        energy = as_float(rows, "energy_pct")
        cumulative = as_float(rows, "cum_energy_pct")
        ax.bar(modes, energy, color=colors[field], alpha=0.75)
        ax.plot(modes, cumulative, color="#111827", marker="o", lw=1.4)
        ax.set_title(field)
        ax.set_xlabel("POD mode")
        ax.set_xticks(modes[:8])
        ax.set_ylim(0, 105)
        ax.grid(True, axis="y", color="#d6d3d1", lw=0.6, alpha=0.85)
        for mode, val in zip(modes[:5], energy[:5]):
            ax.text(mode, val + 2.0, f"{val:.1f}%", ha="center", fontsize=7)
    axes[0].set_ylabel("energy [%]")
    fig.suptitle("run003 POD modal energy")
    fig.tight_layout()
    out = FIG_DIR / "pod_modal_energy.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_pod_temporal() -> Path:
    fig, axes = plt.subplots(3, 1, figsize=(9.4, 8.0), dpi=180, sharex=True)
    for ax, field in zip(axes, FIELDS):
        times, coeffs = temporal_from_csv(ROOT / "pod" / field / "temporal_coefficients.csv")
        for i in range(min(4, coeffs.shape[0])):
            ax.plot(times, coeffs[i], marker="o", lw=1.3, label=f"mode {i + 1}")
        ax.axhline(0, color="#44403c", lw=0.7)
        ax.set_title(f"{field}: temporal coefficients")
        ax.set_ylabel("a_i(t)")
        ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
        ax.legend(frameon=False, fontsize=8, ncol=4, loc="upper right")
    axes[-1].set_xlabel("time [s]")
    fig.suptitle("run003 POD temporal dynamics")
    fig.tight_layout()
    out = FIG_DIR / "pod_temporal_coefficients.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def _scatter_mode_grid(rows: list[dict[str, str]], field: str, columns: list[str], out: Path, *, cmap: str, symmetric: bool) -> Path:
    x = as_float(rows, "x")
    y = as_float(rows, "y")
    values = [as_float(rows, col) for col in columns]
    if symmetric:
        vmax = max(float(np.nanmax(np.abs(v))) for v in values)
        vmin = -vmax
    else:
        vmin = min(float(np.nanmin(v)) for v in values)
        vmax = max(float(np.nanmax(v)) for v in values)

    fig, axes = plt.subplots(1, len(columns), figsize=(3.6 * len(columns), 3.6), dpi=180, sharex=True, sharey=True)
    if len(columns) == 1:
        axes = [axes]
    for ax, col, val in zip(axes, columns, values):
        sc = ax.scatter(x * 1000, y * 1000, c=val, s=3.0, cmap=cmap, vmin=vmin, vmax=vmax, linewidths=0)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(col.replace("_", " "))
        ax.set_xlabel("x [mm]")
        ax.grid(True, color="#e7e5e4", lw=0.4, alpha=0.6)
        fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    axes[0].set_ylabel("y [mm]")
    fig.suptitle(f"{field}: midspan spatial patterns")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_pod_spatial_modes() -> list[Path]:
    written = []
    for field in FIELDS:
        rows = read_csv(ROOT / "pod" / field / "spatial_modes.csv")
        written.append(_scatter_mode_grid(
            rows,
            field,
            ["mean"],
            FIG_DIR / f"pod_{field}_mean_field.png",
            cmap="viridis" if field != "T" else "inferno",
            symmetric=False,
        ))
        columns = [f"mode_{i}" for i in range(1, 5)]
        written.append(_scatter_mode_grid(
            rows,
            field,
            columns,
            FIG_DIR / f"pod_{field}_spatial_modes_1_4.png",
            cmap="RdBu_r",
            symmetric=True,
        ))
    return written


def plot_epod_quality() -> Path:
    fig, ax = plt.subplots(figsize=(8.4, 4.8), dpi=180)
    colors = {"Ux_to_T": "#2563eb", "T_to_Ux": "#dc2626", "Uy_to_T": "#0f766e"}
    for name, color in colors.items():
        rows = read_csv(ROOT / "epod" / name / "reconstruction_metrics.csv")
        modes = as_float(rows, "n_modes")
        captured = as_float(rows, "captured_target_energy_pct")
        ax.plot(modes, captured, marker="o", lw=1.5, color=color, label=name.replace("_", " "))
    ax.set_xlabel("source POD modes used")
    ax.set_ylabel("captured target energy [%]")
    ax.set_ylim(0, 105)
    ax.set_title("EPOD reconstruction quality")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    out = FIG_DIR / "epod_reconstruction_quality.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_epod_modes() -> list[Path]:
    written = []
    for name in ("Ux_to_T", "T_to_Ux", "Uy_to_T"):
        rows = read_csv(ROOT / "epod" / name / "extended_modes.csv")
        columns = [f"emode_{i}" for i in range(1, 5)]
        written.append(_scatter_mode_grid(
            rows,
            f"EPOD {name}",
            columns,
            FIG_DIR / f"epod_{name}_extended_modes_1_4.png",
            cmap="RdBu_r",
            symmetric=True,
        ))
    return written


def plot_coherence_curves() -> Path:
    rows = read_csv(ROOT / "spectral_coherence" / "coherence_curves.csv")
    pairs = sorted(set(row["pair"] for row in rows))
    fig, ax = plt.subplots(figsize=(9.4, 5.2), dpi=180)
    colors = ["#2563eb", "#dc2626", "#0f766e", "#b45309"]
    for color, pair in zip(colors, pairs):
        subset = [row for row in rows if row["pair"] == pair]
        freq = as_float(subset, "freq_Hz")
        coh = as_float(subset, "coherence")
        mask = freq <= 12
        ax.plot(freq[mask], coh[mask], lw=1.6, color=color, label=pair)
    ax.axvline(SHED_F, color="#111827", ls="--", lw=1.0, label=f"f_shed={SHED_F:.3f} Hz")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("magnitude-squared coherence")
    ax.set_title("Wake U/T coherence")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    out = FIG_DIR / "coherence_curves.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_power_spectra() -> Path:
    rows = read_csv(ROOT / "spectral_coherence" / "power_spectra.csv")
    signals = sorted(set(row["signal"] for row in rows))
    fig, ax = plt.subplots(figsize=(8.8, 4.9), dpi=180)
    colors = ["#2563eb", "#0f766e", "#dc2626"]
    for color, signal in zip(colors, signals):
        subset = [row for row in rows if row["signal"] == signal]
        freq = as_float(subset, "freq_Hz")
        psd = as_float(subset, "psd")
        mask = freq <= 12
        ax.semilogy(freq[mask], psd[mask], lw=1.5, color=color, label=signal)
    ax.axvline(SHED_F, color="#111827", ls="--", lw=1.0, label=f"f_shed={SHED_F:.3f} Hz")
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("Welch PSD")
    ax.set_title("Representative probe spectra")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    out = FIG_DIR / "probe_power_spectra.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_te_curves() -> Path:
    rows = read_csv(ROOT / "transfer_entropy" / "te_curves.csv")
    pairs = sorted(set(row["pair"] for row in rows))
    fig, axes = plt.subplots(2, 1, figsize=(9.4, 7.2), dpi=180, sharex=True)
    colors = ["#2563eb", "#dc2626", "#0f766e", "#b45309", "#7c3aed"]
    for color, pair in zip(colors, pairs):
        subset = [row for row in rows if row["pair"] == pair]
        lag = as_float(subset, "lag_s")
        te = as_float(subset, "te_bits")
        excess = as_float(subset, "excess_te_bits")
        axes[0].plot(lag, te, lw=1.4, color=color, label=pair)
        axes[1].plot(lag, excess, lw=1.4, color=color, label=pair)
    axes[0].set_ylabel("TE [bits]")
    axes[0].set_title("Transfer entropy by lag")
    axes[1].set_ylabel("excess TE [bits]")
    axes[1].set_xlabel("lag [s]")
    for ax in axes:
        ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
        ax.legend(frameon=False, fontsize=7, ncol=2)
    fig.tight_layout()
    out = FIG_DIR / "transfer_entropy_curves.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_te_peaks() -> Path:
    rows = read_csv(ROOT / "transfer_entropy" / "te_peak_summary.csv")
    labels = [row["pair"].replace("_", " ") for row in rows]
    vals = as_float(rows, "excess_te_bits")
    lags = as_float(rows, "peak_lag_s")
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.8, 4.8), dpi=180)
    bars = ax.barh(y, vals, color="#2563eb", alpha=0.78)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("excess TE [bits]")
    ax.set_title("Peak transfer entropy directions")
    ax.grid(True, axis="x", color="#d6d3d1", lw=0.6, alpha=0.85)
    for bar, lag in zip(bars, lags):
        ax.text(bar.get_width() + 0.006, bar.get_y() + bar.get_height() / 2, f"lag {lag:.3f}s", va="center", fontsize=8)
    fig.tight_layout()
    out = FIG_DIR / "transfer_entropy_peak_summary.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_force_spectra() -> Path:
    path = ROOT / "force_spectra" / "force_power_spectra.csv"
    if not path.exists():
        return Path()
    rows = read_csv(path)
    signals = sorted(set(row["signal"] for row in rows))
    fig, ax = plt.subplots(figsize=(9.0, 5.0), dpi=180)
    for signal in signals[:6]:
        subset = [row for row in rows if row["signal"] == signal]
        freq = as_float(subset, "freq_Hz")
        psd = as_float(subset, "psd")
        mask = freq <= 12
        ax.semilogy(freq[mask], psd[mask], lw=1.2, label=signal)
    ax.axvline(SHED_F, color="#111827", ls="--", lw=1.0, label=f"f_shed={SHED_F:.3f} Hz")
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("Welch PSD")
    ax.set_title("Raw force.dat column spectra")
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    out = FIG_DIR / "force_power_spectra.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def write_readme(paths: list[Path]) -> None:
    summary = read_json(ROOT / "analysis_summary.json")
    lines = [
        "# run003 Figures",
        "",
        "Figures generated from the repo-local run003 modal analysis outputs.",
        "",
        "## Quick Reading",
        "",
        f"- POD uses {summary['n_snapshots']} midspan snapshots; read its mode maps as exploratory.",
        f"- Probe spectra/coherence use {summary['n_probe_samples']} samples at dt={summary['probe_dt_s']:.6g} s.",
        "- The vertical dashed line in spectral plots marks f_shed = 3.125 Hz.",
        "",
        "## Files",
        "",
    ]
    for path in sorted(p for p in paths if p and p.name):
        lines.append(f"- `{path.name}`")
    lines.append("")
    (FIG_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_fig_dir()
    written = [
        plot_pod_energy(),
        plot_pod_temporal(),
        *plot_pod_spatial_modes(),
        plot_epod_quality(),
        *plot_epod_modes(),
        plot_coherence_curves(),
        plot_power_spectra(),
        plot_te_curves(),
        plot_te_peaks(),
        plot_force_spectra(),
    ]
    write_readme(written)
    for path in written:
        if path and path.name:
            print(f"Wrote {path}")
    print(f"Wrote {FIG_DIR / 'README.md'}")


if __name__ == "__main__":
    main()
