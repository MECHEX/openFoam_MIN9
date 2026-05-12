"""
Run008 aerodynamics analysis.

Layer 002 after the data audit:
- pressure/viscous decomposition of raw forces and moments,
- RMS and phase of pressure/viscous components,
- PSD and harmonic checks,
- phase portraits and Hilbert shedding phase.
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
from scipy import signal


RUN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = RUN_DIR / "data" / "002"
FIG_DIR = RUN_DIR / "figures" / "002"
CASE_DIR = Path("/home/hexmachina/of_runs/V4b_3D_run008")
POST_DIR = CASE_DIR / "postProcessing"

D = 0.012
U_INF = 0.25266
A_REF = 1.44e-4
RHO_INF = 1.205
Q_REF = 0.5 * RHO_INF * U_INF**2
F_REF = Q_REF * A_REF
M_REF = F_REF * D

WINDOW = (2.0, 10.0)
PSD_NPERSEG = 1024


@dataclass
class ComponentStat:
    component: str
    mean: float
    rms: float
    rms_fraction_total_pct: float
    phase_vs_total_deg: float
    corr_vs_total: float


@dataclass
class HarmonicStat:
    signal_name: str
    target: str
    target_hz: float
    peak_hz: float
    strouhal: float
    relative_power_db: float


@dataclass
class PeakStat:
    signal_name: str
    rank: int
    peak_hz: float
    strouhal: float
    relative_power_db: float


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def read_numeric_table(path: Path) -> np.ndarray:
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            values = [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", stripped)]
            if values:
                rows.append(values)
    if not rows:
        raise RuntimeError(f"No numeric rows found in {path}")
    width = max(len(row) for row in rows)
    good = [row for row in rows if len(row) == width]
    return np.asarray(good, dtype=float)


def read_force_coeffs() -> dict[str, np.ndarray]:
    arr = read_numeric_table(POST_DIR / "forceCoeffs" / "0" / "forceCoeffs.dat")
    return {
        "time": arr[:, 0],
        "Cm": arr[:, 1],
        "Cd": arr[:, 2],
        "Cl": arr[:, 3],
        "Cl_f": arr[:, 4],
        "Cl_r": arr[:, 5],
    }


def read_forces_raw() -> dict[str, np.ndarray]:
    arr = read_numeric_table(POST_DIR / "forces_raw" / "0" / "forces.dat")
    names = [
        "time",
        "Fx_p",
        "Fy_p",
        "Fz_p",
        "Fx_v",
        "Fy_v",
        "Fz_v",
        "Mx_p",
        "My_p",
        "Mz_p",
        "Mx_v",
        "My_v",
        "Mz_v",
    ]
    raw = {name: arr[:, i] for i, name in enumerate(names)}
    raw["Fx"] = raw["Fx_p"] + raw["Fx_v"]
    raw["Fy"] = raw["Fy_p"] + raw["Fy_v"]
    raw["Fz"] = raw["Fz_p"] + raw["Fz_v"]
    raw["Mx"] = raw["Mx_p"] + raw["Mx_v"]
    raw["My"] = raw["My_p"] + raw["My_v"]
    raw["Mz"] = raw["Mz_p"] + raw["Mz_v"]

    for suffix in ("p", "v", ""):
        key_suffix = f"_{suffix}" if suffix else ""
        raw[f"Cd{key_suffix}"] = raw[f"Fx{key_suffix}"] / F_REF
        raw[f"Cl{key_suffix}"] = raw[f"Fy{key_suffix}"] / F_REF
        raw[f"Cm{key_suffix}"] = raw[f"Mz{key_suffix}"] / M_REF
    return raw


def window_mask(time: np.ndarray, window: tuple[float, float] = WINDOW) -> np.ndarray:
    return (time >= window[0]) & (time <= window[1])


def demean(x: np.ndarray) -> np.ndarray:
    return x - float(np.mean(x))


def sampling_frequency(time: np.ndarray) -> float:
    return 1.0 / float(np.median(np.diff(time)))


def welch_psd(time: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    fs = sampling_frequency(time)
    nperseg = min(PSD_NPERSEG, len(x))
    freqs, psd = signal.welch(demean(x), fs=fs, window="hann", nperseg=nperseg, noverlap=nperseg // 2)
    return freqs, psd


def peak_frequency(time: np.ndarray, x: np.ndarray, band: tuple[float, float]) -> float:
    freqs, psd = welch_psd(time, x)
    mask = (freqs >= band[0]) & (freqs <= band[1])
    if not np.any(mask):
        return float("nan")
    local_freqs = freqs[mask]
    local_psd = psd[mask]
    return float(local_freqs[int(np.argmax(local_psd))])


def shedding_frequency_from_alternate_peaks(time: np.ndarray, cl: np.ndarray) -> tuple[float, float, int]:
    """Return fundamental shedding frequency from every-second lift peak.

    In this case adjacent Cl peaks carry a strong ~2*f_shed component, so the
    physical period is better estimated from alternating peaks.
    """
    y = demean(cl)
    fs = sampling_frequency(time)
    min_distance = max(1, int(0.10 * fs))
    prominence = 0.25 * float(np.std(y))
    peaks, _ = signal.find_peaks(y, distance=min_distance, prominence=prominence)
    if len(peaks) < 5:
        return peak_frequency(time, cl, (2.0, 4.5)), float("nan"), int(len(peaks))
    adjacent_frequency = 1.0 / float(np.median(np.diff(time[peaks])))
    alternate_periods = []
    for offset in (0, 1):
        selected = peaks[offset::2]
        if len(selected) >= 3:
            alternate_periods.extend(np.diff(time[selected]).tolist())
    fundamental_frequency = 1.0 / float(np.median(alternate_periods))
    return fundamental_frequency, adjacent_frequency, int(len(peaks))


def bandpass_analytic(time: np.ndarray, x: np.ndarray, center_hz: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fs = sampling_frequency(time)
    low = max(0.2, center_hz * 0.65)
    high = min(fs * 0.45, center_hz * 1.35)
    sos = signal.butter(4, [low, high], btype="bandpass", fs=fs, output="sos")
    xf = signal.sosfiltfilt(sos, demean(x))
    analytic = signal.hilbert(xf)
    phase = np.unwrap(np.angle(analytic))
    return xf, phase, np.abs(analytic)


def circular_mean_deg(delta_phase: np.ndarray) -> float:
    z = np.exp(1j * delta_phase)
    return float(np.degrees(np.angle(np.mean(z))))


def component_stats(raw: dict[str, np.ndarray], time: np.ndarray, f0: float) -> list[ComponentStat]:
    mask = window_mask(time)
    t = time[mask]
    stats: list[ComponentStat] = []
    groups = [
        ("Cd_p", "Cd", 2.0 * f0),
        ("Cd_v", "Cd", 2.0 * f0),
        ("Cl_p", "Cl", f0),
        ("Cl_v", "Cl", f0),
        ("Cm_p", "Cm", f0),
        ("Cm_v", "Cm", f0),
    ]
    phase_cache: dict[tuple[str, float], np.ndarray] = {}
    for component, total, center in groups:
        x = raw[component][mask]
        y = raw[total][mask]
        x_rms = float(np.std(demean(x), ddof=1))
        y_rms = float(np.std(demean(y), ddof=1))
        if (component, center) not in phase_cache:
            _, phase_cache[(component, center)], _ = bandpass_analytic(t, x, center)
        if (total, center) not in phase_cache:
            _, phase_cache[(total, center)], _ = bandpass_analytic(t, y, center)
        phase = circular_mean_deg(phase_cache[(component, center)] - phase_cache[(total, center)])
        corr = float(np.corrcoef(demean(x), demean(y))[0, 1])
        stats.append(
            ComponentStat(
                component=component,
                mean=float(np.mean(x)),
                rms=x_rms,
                rms_fraction_total_pct=100.0 * x_rms / y_rms if y_rms else float("nan"),
                phase_vs_total_deg=phase,
                corr_vs_total=corr,
            )
        )
    return stats


def harmonic_stats(signals: dict[str, np.ndarray], time: np.ndarray, f0: float) -> list[HarmonicStat]:
    rows: list[HarmonicStat] = []
    targets = [("f0", f0), ("2f0", 2.0 * f0), ("3f0", 3.0 * f0)]
    for name, x in signals.items():
        freqs, psd = welch_psd(time, x)
        positive = (freqs >= 0.5) & (freqs <= 15.0)
        ref = float(np.max(psd[positive])) if np.any(positive) else float(np.max(psd))
        for label, target in targets:
            band = (max(0.2, target - 0.55), target + 0.55)
            mask = (freqs >= band[0]) & (freqs <= band[1])
            if not np.any(mask):
                continue
            local_freqs = freqs[mask]
            local_psd = psd[mask]
            idx = int(np.argmax(local_psd))
            rel_db = 10.0 * math.log10(float(local_psd[idx]) / ref) if ref > 0 and local_psd[idx] > 0 else float("nan")
            rows.append(
                HarmonicStat(
                    signal_name=name,
                    target=label,
                    target_hz=float(target),
                    peak_hz=float(local_freqs[idx]),
                    strouhal=float(local_freqs[idx] * D / U_INF),
                    relative_power_db=rel_db,
                )
            )
    return rows


def side_peak_stats(signals: dict[str, np.ndarray], time: np.ndarray, max_peaks: int = 5) -> list[PeakStat]:
    rows: list[PeakStat] = []
    for name, x in signals.items():
        freqs, psd = welch_psd(time, x)
        band = (freqs >= 0.5) & (freqs <= 15.0)
        f = freqs[band]
        p = psd[band]
        if len(f) < 3:
            continue
        peaks, _ = signal.find_peaks(p)
        if len(peaks) == 0:
            peaks = np.array([int(np.argmax(p))])
        ordered = peaks[np.argsort(p[peaks])[::-1]][:max_peaks]
        ref = float(p[ordered[0]]) if len(ordered) else float(np.max(p))
        for rank, idx in enumerate(ordered, start=1):
            rel_db = 10.0 * math.log10(float(p[idx]) / ref) if ref > 0 and p[idx] > 0 else float("nan")
            rows.append(
                PeakStat(
                    signal_name=name,
                    rank=rank,
                    peak_hz=float(f[idx]),
                    strouhal=float(f[idx] * D / U_INF),
                    relative_power_db=rel_db,
                )
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_decomposition(time: np.ndarray, raw: dict[str, np.ndarray], stats: list[ComponentStat]) -> None:
    mask = window_mask(time)
    t = time[mask]
    fig, axes = plt.subplots(3, 2, figsize=(12, 9), constrained_layout=True)
    pairs = [("Cd", "Cd_p", "Cd_v"), ("Cl", "Cl_p", "Cl_v"), ("Cm", "Cm_p", "Cm_v")]
    for ax, (total, pressure, viscous) in zip(axes[:, 0], pairs):
        ax.plot(t, raw[total][mask], color="black", lw=1.2, label="total")
        ax.plot(t, raw[pressure][mask], color="#2f6f9f", lw=0.9, label="pressure")
        ax.plot(t, raw[viscous][mask], color="#c77700", lw=0.9, label="viscous")
        ax.set_ylabel(total)
        ax.grid(alpha=0.25)
    axes[0, 0].legend(ncol=3, fontsize=8)
    axes[-1, 0].set_xlabel("t [s]")

    labels = [s.component for s in stats]
    means = [s.mean for s in stats]
    rms = [s.rms for s in stats]
    phases = [s.phase_vs_total_deg for s in stats]
    x = np.arange(len(labels))
    axes[0, 1].bar(x, means, color="#597a4a")
    axes[0, 1].set_title("Mean component coefficient")
    axes[1, 1].bar(x, rms, color="#985f41")
    axes[1, 1].set_title("RMS of fluctuating component")
    axes[2, 1].bar(x, phases, color="#536c9f")
    axes[2, 1].set_title("Phase vs matching total signal")
    for ax in axes[:, 1]:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right")
        ax.grid(axis="y", alpha=0.25)
    axes[2, 1].set_ylabel("deg")
    fig.suptitle("run008 force/moment pressure-viscous decomposition, t=2..10 s")
    fig.savefig(FIG_DIR / "run008_002_force_pressure_viscous_decomposition.png", dpi=180)
    plt.close(fig)


def plot_psd(time: np.ndarray, signals: dict[str, np.ndarray], f0: float) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
    axes = axes.ravel()
    for ax, (name, x) in zip(axes, signals.items()):
        freqs, psd = welch_psd(time, x)
        ax.semilogy(freqs, psd, color="#263238", lw=1.2)
        for mult, color in [(1, "#a33"), (2, "#2a6"), (3, "#36c")]:
            ax.axvline(mult * f0, color=color, ls="--", lw=0.9, alpha=0.75)
        ax.set_xlim(0, 15)
        ax.set_title(name)
        ax.set_xlabel("f [Hz]")
        ax.set_ylabel("PSD")
        ax.grid(alpha=0.25)
    fig.suptitle("run008 aerodynamic PSD and harmonics, t=2..10 s")
    fig.savefig(FIG_DIR / "run008_002_force_psd_harmonics.png", dpi=180)
    plt.close(fig)


def plot_phase_portraits(time: np.ndarray, raw: dict[str, np.ndarray], coeffs: dict[str, np.ndarray], f0: float) -> dict[str, np.ndarray]:
    mask = window_mask(time)
    t = time[mask]
    cl = coeffs["Cl"][mask]
    cd = coeffs["Cd"][mask]
    cm = coeffs["Cm"][mask]
    cl_filt, phase, amp = bandpass_analytic(t, cl, f0)
    phase_wrapped = np.mod(phase, 2.0 * np.pi)
    dcl_dt = np.gradient(cl_filt, t)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
    sc0 = axes[0, 0].scatter(cl, cd, c=phase_wrapped, s=8, cmap="twilight", alpha=0.85)
    axes[0, 0].set_xlabel("Cl")
    axes[0, 0].set_ylabel("Cd")
    axes[0, 0].set_title("Cd(t) vs Cl(t)")
    sc1 = axes[0, 1].scatter(cl_filt, dcl_dt, c=phase_wrapped, s=8, cmap="twilight", alpha=0.85)
    axes[0, 1].set_xlabel("bandpassed Cl")
    axes[0, 1].set_ylabel("dCl/dt [1/s]")
    axes[0, 1].set_title("Cl phase portrait")
    axes[1, 0].plot(t, np.mod(phase, 2.0 * np.pi), color="#314f77", lw=0.8)
    axes[1, 0].set_xlabel("t [s]")
    axes[1, 0].set_ylabel("Hilbert phase [rad]")
    axes[1, 0].set_title("Shedding phase from analytic signal")
    axes[1, 1].scatter(cl, cm, c=phase_wrapped, s=8, cmap="twilight", alpha=0.85)
    axes[1, 1].set_xlabel("Cl")
    axes[1, 1].set_ylabel("Cm")
    axes[1, 1].set_title("Cm(t) vs Cl(t)")
    for ax in axes.ravel():
        ax.grid(alpha=0.25)
    fig.colorbar(sc0, ax=axes[:, :], shrink=0.82, label="phase [rad]")
    fig.suptitle("run008 phase portraits, Hilbert phase based on Cl")
    fig.savefig(FIG_DIR / "run008_002_phase_portraits_hilbert.png", dpi=180)
    plt.close(fig)
    return {"time": t, "phase_rad": phase_wrapped, "Cl_bandpassed": cl_filt, "Cl_envelope": amp, "dCl_dt": dcl_dt}


def plot_cycle_average(phase_data: dict[str, np.ndarray], raw: dict[str, np.ndarray], coeffs: dict[str, np.ndarray]) -> None:
    t = phase_data["time"]
    mask_raw = window_mask(raw["time"])
    mask_coeff = window_mask(coeffs["time"])
    phase = phase_data["phase_rad"]
    bins = np.linspace(0, 2 * np.pi, 49)
    centers = 0.5 * (bins[:-1] + bins[1:])

    series = {
        "Cd": coeffs["Cd"][mask_coeff],
        "Cl": coeffs["Cl"][mask_coeff],
        "Cm": coeffs["Cm"][mask_coeff],
        "Cl_p": raw["Cl_p"][mask_raw],
        "Cl_v": raw["Cl_v"][mask_raw],
    }
    rows = []
    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    for name, values in series.items():
        means = []
        for lo, hi in zip(bins[:-1], bins[1:]):
            m = (phase >= lo) & (phase < hi)
            means.append(float(np.mean(values[m])) if np.any(m) else float("nan"))
        means_arr = np.asarray(means)
        if np.nanstd(means_arr) > 0:
            plot_values = (means_arr - np.nanmean(means_arr)) / np.nanstd(means_arr)
        else:
            plot_values = means_arr
        ax.plot(centers, plot_values, lw=1.3, label=name)
        for c, val, scaled in zip(centers, means_arr, plot_values):
            rows.append({"signal": name, "phase_rad": c, "phase_deg": math.degrees(c), "mean_value": val, "scaled_value": scaled})
    ax.set_xlabel("Hilbert shedding phase [rad]")
    ax.set_ylabel("cycle mean, standardized")
    ax.set_title("Phase-conditioned aerodynamic cycle")
    ax.grid(alpha=0.25)
    ax.legend(ncol=5, fontsize=8)
    fig.savefig(FIG_DIR / "run008_002_phase_conditioned_cycle.png", dpi=180)
    plt.close(fig)
    write_csv(DATA_DIR / "run008_002_phase_conditioned_cycle.csv", rows)


def write_report(
    f0: float,
    adjacent_peak_frequency: float,
    n_peaks: int,
    coeffs: dict[str, np.ndarray],
    raw: dict[str, np.ndarray],
    comp_stats: list[ComponentStat],
    harmonics: list[HarmonicStat],
    side_peaks: list[PeakStat],
) -> None:
    mask_c = window_mask(coeffs["time"])
    mask_r = window_mask(raw["time"])
    total_match = {
        "Cd_raw_minus_forceCoeffs_mean": float(np.mean(raw["Cd"][mask_r] - coeffs["Cd"][mask_c])),
        "Cl_raw_minus_forceCoeffs_mean": float(np.mean(raw["Cl"][mask_r] - coeffs["Cl"][mask_c])),
        "Cm_raw_minus_forceCoeffs_mean": float(np.mean(raw["Cm"][mask_r] - coeffs["Cm"][mask_c])),
    }

    lines = [
        "# V4b_3D run008 aerodynamic analysis",
        "",
        "Scope: `forceCoeffs` and `forces_raw` both use patch `hot_tube`; pressure/viscous decomposition is therefore cylinder-only and directly comparable to Cd/Cl/Cm.",
        "",
        f"Primary window: `{WINDOW[0]:.1f}..{WINDOW[1]:.1f} s`.",
        f"Shedding frequency from every-second Cl peak: `{f0:.4f} Hz`, `St = {f0 * D / U_INF:.5f}`.",
        f"Adjacent Cl-peak component: `{adjacent_peak_frequency:.4f} Hz` from `{n_peaks}` detected peaks.",
        "The PSD is dominated by the adjacent-peak component near `2*f_shed`; the lower `f_shed` component is present but much weaker in Cl.",
        "",
        "## Consistency check",
        "",
        "| Quantity | raw total - forceCoeffs mean |",
        "|---|---:|",
        f"| Cd | {total_match['Cd_raw_minus_forceCoeffs_mean']:.6e} |",
        f"| Cl | {total_match['Cl_raw_minus_forceCoeffs_mean']:.6e} |",
        f"| Cm | {total_match['Cm_raw_minus_forceCoeffs_mean']:.6e} |",
        "",
        "## Pressure/viscous component statistics",
        "",
        "| Component | mean | RMS | RMS / total RMS | phase vs total | corr vs total |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for s in comp_stats:
        lines.append(
            f"| {s.component} | {s.mean:.6f} | {s.rms:.6f} | {s.rms_fraction_total_pct:.2f}% | {s.phase_vs_total_deg:+.2f} deg | {s.corr_vs_total:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Harmonics",
            "",
            "| Signal | target | target Hz | peak Hz | St | relative power |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for h in harmonics:
        lines.append(
            f"| {h.signal_name} | {h.target} | {h.target_hz:.4f} | {h.peak_hz:.4f} | {h.strouhal:.5f} | {h.relative_power_db:+.2f} dB |"
        )
    lines.extend(
        [
            "",
            "## Dominant peaks / side peaks",
            "",
            "| Signal | rank | peak Hz | St | relative power |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for p in side_peaks:
        lines.append(
            f"| {p.signal_name} | {p.rank} | {p.peak_hz:.4f} | {p.strouhal:.5f} | {p.relative_power_db:+.2f} dB |"
        )
    lines.extend(
        [
            "",
            "## Figures",
            "",
            "- `../../figures/002/run008_002_force_pressure_viscous_decomposition.png`",
            "- `../../figures/002/run008_002_force_psd_harmonics.png`",
            "- `../../figures/002/run008_002_phase_portraits_hilbert.png`",
            "- `../../figures/002/run008_002_phase_conditioned_cycle.png`",
        ]
    )
    (DATA_DIR / "run008_002_aerodynamics.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    coeffs_all = read_force_coeffs()
    raw_all = read_forces_raw()

    mask_c = window_mask(coeffs_all["time"])
    mask_r = window_mask(raw_all["time"])
    coeffs = {k: v[mask_c] for k, v in coeffs_all.items()}
    raw = {k: v[mask_r] for k, v in raw_all.items()}
    time = coeffs["time"]

    f0, adjacent_peak_frequency, n_peaks = shedding_frequency_from_alternate_peaks(time, coeffs["Cl"])
    comp_stats = component_stats(raw, raw["time"], f0)
    psd_signals = {
        "Cd": coeffs["Cd"],
        "Cl": coeffs["Cl"],
        "Cm": coeffs["Cm"],
        "Cl_pressure": raw["Cl_p"],
        "Cl_viscous": raw["Cl_v"],
        "Cm_pressure": raw["Cm_p"],
    }
    harmonics = harmonic_stats(psd_signals, time, f0)
    side_peaks = side_peak_stats(psd_signals, time)

    plot_decomposition(raw["time"], raw, comp_stats)
    plot_psd(time, psd_signals, f0)
    phase_data = plot_phase_portraits(time, raw, coeffs, f0)
    plot_cycle_average(phase_data, raw, coeffs)

    write_csv(DATA_DIR / "run008_002_pressure_viscous_stats.csv", [asdict(s) for s in comp_stats])
    write_csv(DATA_DIR / "run008_002_harmonic_peaks.csv", [asdict(h) for h in harmonics])
    write_csv(DATA_DIR / "run008_002_side_peaks.csv", [asdict(p) for p in side_peaks])
    np.savez_compressed(
        DATA_DIR / "run008_002_hilbert_phase.npz",
        time=phase_data["time"],
        phase_rad=phase_data["phase_rad"],
        Cl_bandpassed=phase_data["Cl_bandpassed"],
        Cl_envelope=phase_data["Cl_envelope"],
        dCl_dt=phase_data["dCl_dt"],
    )
    (DATA_DIR / "run008_002_aerodynamics.json").write_text(
        json.dumps(
            {
                "window": WINDOW,
                "f0_hz": f0,
                "adjacent_peak_frequency_hz": adjacent_peak_frequency,
                "n_detected_cl_peaks": n_peaks,
                "St": f0 * D / U_INF,
                "pressure_viscous_stats": [asdict(s) for s in comp_stats],
                "harmonics": [asdict(h) for h in harmonics],
                "side_peaks": [asdict(p) for p in side_peaks],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_report(f0, adjacent_peak_frequency, n_peaks, coeffs, raw, comp_stats, harmonics, side_peaks)
    print((DATA_DIR / "run008_002_aerodynamics.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
