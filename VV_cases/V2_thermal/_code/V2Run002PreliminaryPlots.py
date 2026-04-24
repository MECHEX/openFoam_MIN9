from __future__ import annotations

from pathlib import Path
import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from V2AStudy import BHARTI_NU, D, NU, nu_lange, nu_time_series

REPO_STUDY = Path(__file__).resolve().parent.parent
RUN_DIR = REPO_STUDY / "results" / "study_v2a" / "runs" / "002_data_v2a_boussinesq_validation"
PLOTS_DIR = RUN_DIR / "plots"
COMPARE_MD = RUN_DIR / "literature_comparison.md"
COMPARE_CSV = RUN_DIR / "literature_comparison.csv"

CASE_DIR = Path(r"C:\openfoam-case\VV_cases\V2_thermal_run002\Re10")
COEFFS = CASE_DIR / "postProcessing" / "forceCoeffs" / "0" / "coefficient.dat"

RE = 10.0
U_INF = RE * NU / D


def read_force_coeffs() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    time = []
    cd = []
    cl = []
    for line in COEFFS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split()
        time.append(float(parts[0]))
        cd.append(float(parts[1]))
        cl.append(float(parts[4]))
    return np.asarray(time), np.asarray(cd), np.asarray(cl)


def tail_stats(time: np.ndarray, values: np.ndarray, window_s: float) -> dict[str, float]:
    tmax = float(time[-1])
    mask = time >= (tmax - window_s)
    sel = values[mask]
    return {
        "mean": float(np.mean(sel)),
        "std": float(np.std(sel)),
        "min": float(np.min(sel)),
        "max": float(np.max(sel)),
    }


def spectral_peak_st(time: np.ndarray, cl: np.ndarray, window_s: float) -> tuple[float, float]:
    tmax = float(time[-1])
    mask = time >= (tmax - window_s)
    t = time[mask]
    y = cl[mask] - np.mean(cl[mask])
    dt = float(np.mean(np.diff(t)))

    nfft = 1
    while nfft < len(y) * 8:
        nfft *= 2

    window = np.hanning(len(y))
    freqs = np.fft.rfftfreq(nfft, d=dt)
    amps = np.abs(np.fft.rfft(y * window, n=nfft))
    valid = (freqs > 0) & (freqs < 20.0)
    freqs = freqs[valid]
    amps = amps[valid]
    idx = int(np.argmax(amps))
    freq = float(freqs[idx])
    st = freq * D / U_INF
    return freq, st


def nu_metrics() -> tuple[float | None, int]:
    series = nu_time_series(CASE_DIR)
    if not series:
        return None, 0
    return float(series[-1][1]), len(series)


def write_comparison_csv(
    cd_stats_1s: dict[str, float],
    cl_stats_1s: dict[str, float],
    st_1s: float,
    st_2s: float,
    st_3s: float,
    nu_last: float | None,
    nu_samples: int,
) -> None:
    lange_nu = nu_lange(RE)
    bharti_nu = BHARTI_NU[10]
    nu_value = f"{nu_last:.6f}" if nu_last is not None else "n/a"
    if nu_last is None:
        nu_interp = "Nu extraction not yet available"
    elif nu_samples < 2:
        nu_interp = "single written snapshot only; startup transient, not converged"
    else:
        nu_interp = "transient thermal history; compare only after plateau/time averaging"
    rows = [
        {
            "quantity": "Regime",
            "run002_value": "long transient, solver stable, not yet settled",
            "literature_value": "steady flow at Re=10",
            "interpretation": "qualitatively consistent, not converged in time",
        },
        {
            "quantity": "St provisional (last 1 s)",
            "run002_value": f"{st_1s:.6f}",
            "literature_value": "n/a for steady Re=10 benchmark",
            "interpretation": "transient spectral peak only",
        },
        {
            "quantity": "St provisional (last 2 s)",
            "run002_value": f"{st_2s:.6f}",
            "literature_value": "n/a for steady Re=10 benchmark",
            "interpretation": "transient spectral peak only",
        },
        {
            "quantity": "St provisional (last 3 s)",
            "run002_value": f"{st_3s:.6f}",
            "literature_value": "n/a for steady Re=10 benchmark",
            "interpretation": "transient spectral peak only",
        },
        {
            "quantity": "Nu from wall-normal grad(T) at latest written time",
            "run002_value": nu_value,
            "literature_value": f"Lange={lange_nu:.6f}; Bharti={bharti_nu:.6f}",
            "interpretation": nu_interp,
        },
        {
            "quantity": "Cd mean (last 1 s)",
            "run002_value": f"{cd_stats_1s['mean']:.6f}",
            "literature_value": "n/a in current V2a reference set",
            "interpretation": "transient only",
        },
        {
            "quantity": "Cl mean (last 1 s)",
            "run002_value": f"{cl_stats_1s['mean']:.6f}",
            "literature_value": "0 for settled steady benchmark",
            "interpretation": "still transient, not yet physically settled",
        },
    ]
    with COMPARE_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["quantity", "run002_value", "literature_value", "interpretation"],
        )
        writer.writeheader()
        writer.writerows(rows)


def plot_force_history(time: np.ndarray, cd: np.ndarray, cl: np.ndarray) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(9, 6), dpi=180, sharex=True)

    axes[0].plot(time, cd, color="#0b5ed7", linewidth=1.0)
    axes[0].set_ylabel("Cd [-]")
    axes[0].grid(True, alpha=0.25)
    axes[0].set_title("V2a run 002, Re10: preliminary force history")

    axes[1].plot(time, cl, color="#c2410c", linewidth=1.0)
    axes[1].set_ylabel("Cl [-]")
    axes[1].set_xlabel("Time [s]")
    axes[1].grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "Re10_Cd_Cl_vs_time.png")
    fig.savefig(PLOTS_DIR / "Re10_Cd_Cl_vs_time.svg")
    plt.close(fig)


def plot_cl_spectrum(time: np.ndarray, cl: np.ndarray) -> tuple[float, float]:
    tmax = float(time[-1])
    mask = time >= (tmax - 3.0)
    t = time[mask]
    y = cl[mask] - np.mean(cl[mask])
    dt = float(np.mean(np.diff(t)))

    nfft = 1
    while nfft < len(y) * 8:
        nfft *= 2

    window = np.hanning(len(y))
    freqs = np.fft.rfftfreq(nfft, d=dt)
    amps = np.abs(np.fft.rfft(y * window, n=nfft))
    valid = (freqs > 0) & (freqs < 20.0)
    freqs = freqs[valid]
    amps = amps[valid]
    idx = int(np.argmax(amps))
    peak_f = float(freqs[idx])
    peak_st = peak_f * D / U_INF

    fig, ax = plt.subplots(figsize=(8, 4), dpi=180)
    ax.plot(freqs, amps, color="#2563eb", linewidth=1.0)
    ax.axvline(peak_f, color="#dc2626", linestyle="--", linewidth=1.0)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Amplitude [-]")
    ax.set_title("Re10 preliminary Cl spectrum from last 3 s")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "Re10_Cl_spectrum.png")
    fig.savefig(PLOTS_DIR / "Re10_Cl_spectrum.svg")
    plt.close(fig)

    return peak_f, peak_st


def write_comparison_md(
    cd_stats_1s: dict[str, float],
    cl_stats_1s: dict[str, float],
    st_1s: float,
    st_2s: float,
    st_3s: float,
    nu_last: float | None,
    nu_samples: int,
) -> None:
    lange_nu = nu_lange(RE)
    bharti_nu = BHARTI_NU[10]
    nu_value = f"{nu_last:.4f}" if nu_last is not None else "n/a"
    if nu_last is None:
        nu_reading = "Nu extraction not yet available"
    elif nu_samples < 2:
        nu_reading = "single written snapshot only; startup transient, not converged"
    else:
        nu_reading = "transient thermal history; compare only after plateau/time averaging"
    lines = [
        "# Re10 Preliminary Comparison With Literature",
        "",
        "## Comparison Table",
        "",
        "| Quantity | Current run-002 result | Literature expectation | Reading |",
        "|---|---:|---:|---|",
        "| Regime | long transient, solver stable, not yet fully settled | steady flow at Re=10 | qualitatively consistent with a low-Re steady benchmark, but not yet converged in time |",
        f"| Provisional spectral peak St (last 1 s) | {st_1s:.3f} | not defined for a steady Re=10 benchmark | not physically acceptable as shedding St |",
        f"| Provisional spectral peak St (last 2 s) | {st_2s:.3f} | not defined for a steady Re=10 benchmark | still a transient spectral peak only |",
        f"| Provisional spectral peak St (last 3 s) | {st_3s:.3f} | not defined for a steady Re=10 benchmark | still a transient spectral peak only |",
        f"| Nu from wall-normal grad(T) at latest written time | {nu_value} | Lange = {lange_nu:.4f}; Bharti = {bharti_nu:.4f} | {nu_reading} |",
        f"| Cd mean (last 1 s) | {cd_stats_1s['mean']:.4f} | not available in current V2a reference set | transient only |",
        f"| Cl mean (last 1 s) | {cl_stats_1s['mean']:.4f} | 0 for a settled steady Re=10 benchmark | still transient, not yet physically settled |",
        "",
        "## Force-tail statistics",
        "",
        f"- last 1 s: `Cd_mean = {cd_stats_1s['mean']:.4f}`, `Cd_std = {cd_stats_1s['std']:.4f}`",
        f"- last 1 s: `Cl_mean = {cl_stats_1s['mean']:.4f}`, `Cl_std = {cl_stats_1s['std']:.4f}`",
        "",
        "## Nu note",
        "",
        "- `Nu` is now extracted from the area-averaged wall-normal temperature gradient on the cylinder patch",
        "- this replaces the earlier rejected `mag(grad(T))` shortcut",
        f"- current latest written-time value is `Nu = {nu_value}` from `Nu_samples = {nu_samples}` thermal snapshot(s)",
        f"- literature steady references remain `Nu_Lange = {lange_nu:.4f}` and `Nu_Bharti = {bharti_nu:.4f}`",
        "- `Nu vs time` is still not meaningful for this run because only one non-zero written thermal snapshot is currently available",
        "",
        "## Practical conclusion",
        "",
        "- the present run is already a good solver-stability smoke-test",
        "- the present `Nu` extraction path is now physically correct",
        "- this particular `Re10` run is still not a valid steady heat-transfer comparison case because the thermal transient is not finished",
        "- the cleanest figures to show now are the force history and the transient spectrum, explicitly labeled as preliminary",
    ]
    COMPARE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    time, cd, cl = read_force_coeffs()
    cd_stats_1s = tail_stats(time, cd, 1.0)
    cl_stats_1s = tail_stats(time, cl, 1.0)
    nu_last, nu_samples = nu_metrics()

    _, st_1s = spectral_peak_st(time, cl, 1.0)
    _, st_2s = spectral_peak_st(time, cl, 2.0)
    _, st_3s = spectral_peak_st(time, cl, 3.0)

    plot_force_history(time, cd, cl)
    plot_cl_spectrum(time, cl)
    write_comparison_md(cd_stats_1s, cl_stats_1s, st_1s, st_2s, st_3s, nu_last, nu_samples)
    write_comparison_csv(cd_stats_1s, cl_stats_1s, st_1s, st_2s, st_3s, nu_last, nu_samples)

    print("Wrote preliminary V2a run-002 assets:")
    print(PLOTS_DIR / "Re10_Cd_Cl_vs_time.png")
    print(PLOTS_DIR / "Re10_Cl_spectrum.png")
    print(COMPARE_MD)
    print(COMPARE_CSV)


if __name__ == "__main__":
    main()
