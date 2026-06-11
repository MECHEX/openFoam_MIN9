from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/007_strong_indicators/02_frequency_coherence_phase"
NU_FILE = REPO_DIR / "VV_cases/presentation_data/007_strong_indicators/00_fullNu3D_xt/fullNu3D_xt_time_resolved.csv"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CASES = [
    {"Re": 100.0, "case": "run012_re100", "path": Path("/home/hexmachina/of_runs/V4b_3D_run012_re100_production"), "regime": "steady"},
    {"Re": 150.0, "case": "run013_re150", "path": Path("/home/hexmachina/of_runs/V4b_3D_run013_re150_production"), "regime": "steady"},
    {"Re": 160.0, "case": "run015_re160", "path": Path("/home/hexmachina/of_runs/V4b_3D_run015_re160_production"), "regime": "shedding"},
    {"Re": 175.0, "case": "run014_re175", "path": Path("/home/hexmachina/of_runs/V4b_3D_run014_re175_production"), "regime": "shedding"},
    {"Re": 200.0, "case": "run008_re200", "path": Path("/home/hexmachina/of_runs/V4b_3D_run008"), "regime": "production shedding"},
]

D_REF_M = 0.012
SELECTED_X_MM = [-11.5, -5.5, 0.5, 5.5, 10.5, 13.5]
ANALYSIS_WINDOW = (8.0, 10.0)
CL_STD_SHEDDING_THRESHOLD = 1.0e-3


def read_force_coeffs(case_dir: Path) -> tuple[pd.DataFrame, float]:
    path = case_dir / "postProcessing/forceCoeffs/0/forceCoeffs.dat"
    if not path.exists():
        raise FileNotFoundError(path)
    u_ref = math.nan
    rows: list[list[float]] = []
    with path.open(errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                if "magUInf" in line:
                    try:
                        u_ref = float(line.split(":")[-1])
                    except ValueError:
                        pass
                continue
            vals = [float(x) for x in line.split()]
            if len(vals) >= 4:
                rows.append(vals[:6])
    df = pd.DataFrame(rows, columns=["time_s", "Cm", "Cd", "Cl", "Cl_f", "Cl_r"])
    return df, u_ref


def dominant_frequency(time: np.ndarray, values: np.ndarray) -> tuple[float, float]:
    dt = float(np.median(np.diff(time)))
    fs = 1.0 / dt
    x = values - np.mean(values)
    nperseg = min(256, len(x))
    freq, psd = signal.welch(x, fs=fs, nperseg=nperseg, detrend="constant")
    valid = freq > 0.15
    if not np.any(valid):
        return math.nan, math.nan
    idx_valid = np.where(valid)[0]
    idx = idx_valid[int(np.argmax(psd[valid]))]
    return float(freq[idx]), float(psd[idx])


def interp_to_times(src_t: np.ndarray, src_y: np.ndarray, dst_t: np.ndarray) -> np.ndarray:
    return np.interp(dst_t, src_t, src_y)


def spectral_metrics(time: np.ndarray, driver: np.ndarray, response: np.ndarray, target_f: float) -> dict[str, float]:
    dt = float(np.median(np.diff(time)))
    fs = 1.0 / dt
    x = driver - np.mean(driver)
    y = response - np.mean(response)
    n = len(time)
    if np.std(x) <= 1.0e-14 or np.std(y) <= 1.0e-14:
        return {
            "fs_sampling_Hz": fs,
            "n_samples": n,
            "nperseg": min(16, n),
            "n_welch_segments_approx": 0,
            "target_frequency_Hz": target_f,
            "frequency_bin_at_target_Hz": math.nan,
            "coherence_at_target": math.nan,
            "phase_at_target_rad": math.nan,
            "delay_at_target_s": math.nan,
            "max_coherence": math.nan,
            "frequency_at_max_coherence_Hz": math.nan,
            "phase_at_max_coherence_rad": math.nan,
            "zero_lag_pearson": math.nan,
            "best_abs_xcorr_lag_s": math.nan,
            "best_abs_xcorr_value_raw": math.nan,
            "note": "driver_or_response_has_near_zero_variance",
        }
    nperseg = min(16, n)
    noverlap = nperseg // 2
    freq, coh = signal.coherence(x, y, fs=fs, nperseg=nperseg, noverlap=noverlap, detrend="constant")
    freq_csd, csd = signal.csd(x, y, fs=fs, nperseg=nperseg, noverlap=noverlap, detrend="constant")
    if len(freq) == 0:
        return {}
    idx_target = int(np.argmin(np.abs(freq - target_f))) if np.isfinite(target_f) else int(np.nanargmax(coh[1:]) + 1)
    if len(coh) > 1 and np.any(np.isfinite(coh[1:])):
        idx_max = int(np.nanargmax(coh[1:]) + 1)
    else:
        idx_max = 0
    phase_target = float(np.angle(csd[idx_target]))
    f_target_used = float(freq[idx_target])
    delay_target = -phase_target / (2.0 * math.pi * f_target_used) if f_target_used > 0 else math.nan
    corr = signal.correlate(y, x, mode="full")
    lags = signal.correlation_lags(len(y), len(x), mode="full") * dt
    lag_idx = int(np.argmax(np.abs(corr)))
    pearson0 = float(np.corrcoef(x, y)[0, 1]) if np.std(x) > 0 and np.std(y) > 0 else math.nan
    return {
        "fs_sampling_Hz": fs,
        "n_samples": n,
        "nperseg": nperseg,
        "n_welch_segments_approx": 1 + max(0, (n - nperseg) // max(1, nperseg - noverlap)),
        "target_frequency_Hz": target_f,
        "frequency_bin_at_target_Hz": f_target_used,
        "coherence_at_target": float(coh[idx_target]),
        "phase_at_target_rad": phase_target,
        "delay_at_target_s": delay_target,
        "max_coherence": float(coh[idx_max]),
        "frequency_at_max_coherence_Hz": float(freq[idx_max]),
        "phase_at_max_coherence_rad": float(np.angle(csd[idx_max])),
        "zero_lag_pearson": pearson0,
        "best_abs_xcorr_lag_s": float(lags[lag_idx]),
        "best_abs_xcorr_value_raw": float(corr[lag_idx]),
        "note": "ok_low_sample_count",
    }


def build_timeseries_and_metrics() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    nu = pd.read_csv(NU_FILE)
    ts_rows: list[pd.DataFrame] = []
    metric_rows: list[dict] = []
    cl_summary_rows: list[dict] = []

    for case in CASES:
        fc, u_ref = read_force_coeffs(case["path"])
        t0, t1 = ANALYSIS_WINDOW
        fc_win = fc[(fc["time_s"] >= t0) & (fc["time_s"] <= t1)].copy()
        f_cl, psd_peak = dominant_frequency(fc_win["time_s"].to_numpy(), fc_win["Cl"].to_numpy())
        cl_std = float(fc_win["Cl"].std())
        valid_shedding_signal = cl_std > CL_STD_SHEDDING_THRESHOLD
        if not valid_shedding_signal:
            f_cl = math.nan
            psd_peak = math.nan
        st_cl = f_cl * D_REF_M / u_ref if np.isfinite(f_cl) and np.isfinite(u_ref) and u_ref > 0 else math.nan
        cl_summary_rows.append(
            {
                "Re": case["Re"],
                "case": case["case"],
                "regime": case["regime"],
                "U_ref_m_s": u_ref,
                "dominant_Cl_frequency_Hz": f_cl,
                "dominant_Cl_St": st_cl,
                "Cl_psd_peak": psd_peak,
                "Cl_std_window": cl_std,
                "valid_shedding_signal": valid_shedding_signal,
                "Cd_mean_window": float(fc_win["Cd"].mean()),
                "Cl_n_samples_high_res": int(len(fc_win)),
            }
        )
        nu_case = nu[np.isclose(nu["Re"], case["Re"])].copy()
        times = np.asarray(sorted(nu_case["time_s"].unique()), dtype=float)
        cl_on_nu = interp_to_times(fc_win["time_s"].to_numpy(), fc_win["Cl"].to_numpy(), times)
        cd_on_nu = interp_to_times(fc_win["time_s"].to_numpy(), fc_win["Cd"].to_numpy(), times)
        for x_mm in SELECTED_X_MM:
            sub = nu_case[np.isclose(nu_case["x_center_mm"], x_mm)].sort_values("time_s")
            if sub.empty:
                continue
            local = pd.DataFrame(
                {
                    "Re": case["Re"],
                    "case": case["case"],
                    "regime": case["regime"],
                    "time_s": times,
                    "x_center_mm": x_mm,
                    "Cl_interp": cl_on_nu,
                    "Cd_interp": cd_on_nu,
                    "Nu_3D_xt": sub["Nu_3D_xt"].to_numpy(),
                    "Q_total_strip_W": sub["Q_total_strip_W"].to_numpy(),
                    "DeltaT_lm_yz_K": sub["DeltaT_lm_yz_K"].to_numpy(),
                }
            )
            ts_rows.append(local)
            for response_name in ["Nu_3D_xt", "Q_total_strip_W"]:
                metrics = spectral_metrics(times, cl_on_nu, local[response_name].to_numpy(), f_cl)
                metrics.update(
                    {
                        "Re": case["Re"],
                        "case": case["case"],
                        "regime": case["regime"],
                        "x_center_mm": x_mm,
                        "driver": "Cl",
                        "response": response_name,
                        "U_ref_m_s": u_ref,
                        "St_at_target": metrics.get("frequency_bin_at_target_Hz", math.nan) * D_REF_M / u_ref
                        if np.isfinite(u_ref) and u_ref > 0
                        else math.nan,
                    }
                )
                metric_rows.append(metrics)
    return pd.concat(ts_rows, ignore_index=True), pd.DataFrame(metric_rows), pd.DataFrame(cl_summary_rows)


def plot_outputs(ts: pd.DataFrame, metrics: pd.DataFrame, cl_summary: pd.DataFrame) -> None:
    shedding_res = [160.0, 175.0, 200.0]
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 8.2), sharex=True)
    for ax, re in zip(axes, shedding_res):
        sub = ts[(np.isclose(ts["Re"], re)) & (np.isclose(ts["x_center_mm"], 5.5))]
        if sub.empty:
            continue
        ax2 = ax.twinx()
        ax.plot(sub["time_s"], sub["Cl_interp"] - sub["Cl_interp"].mean(), color="0.2", lw=1.5, label="Cl fluct.")
        ax2.plot(sub["time_s"], sub["Nu_3D_xt"] - sub["Nu_3D_xt"].mean(), color="#d55e00", lw=1.5, label="Nu fluct., x=5.5 mm")
        ax.set_ylabel(f"Re {re:g}\nCl'")
        ax2.set_ylabel("Nu'")
        ax.grid(True, alpha=0.25)
    axes[-1].set_xlabel("time [s]")
    fig.suptitle("Time-domain comparison: Cl fluctuations vs local Nu_3D fluctuations")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig01_time_traces_Cl_vs_Nu_x5p5.png", dpi=240)
    fig.savefig(OUT_DIR / "fig01_time_traces_Cl_vs_Nu_x5p5.pdf")
    plt.close(fig)

    for response in ["Nu_3D_xt", "Q_total_strip_W"]:
        fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), sharey=False)
        sub = metrics[(metrics["response"] == response) & (metrics["Re"].isin(shedding_res))]
        for re in shedding_res:
            sr = sub[np.isclose(sub["Re"], re)].sort_values("x_center_mm")
            axes[0].plot(sr["x_center_mm"], sr["coherence_at_target"], marker="o", lw=1.8, label=f"Re {re:g}")
            axes[1].plot(sr["x_center_mm"], sr["delay_at_target_s"], marker="o", lw=1.8, label=f"Re {re:g}")
        for ax in axes:
            ax.axvline(-6, color="0.35", ls="--", lw=0.8)
            ax.axvline(6, color="0.35", ls="--", lw=0.8)
            ax.grid(True, alpha=0.25)
            ax.set_xlabel("x position [mm]")
        axes[0].set_ylabel("coherence at dominant Cl frequency")
        axes[1].set_ylabel("phase delay [s]")
        axes[0].set_title(f"Cl -> {response}: coherence")
        axes[1].set_title(f"Cl -> {response}: phase-derived delay")
        axes[0].legend(frameon=False)
        fig.tight_layout()
        stem = response.replace("_", "")
        fig.savefig(OUT_DIR / f"fig02_{stem}_coherence_delay_by_x.png", dpi=240)
        fig.savefig(OUT_DIR / f"fig02_{stem}_coherence_delay_by_x.pdf")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    valid = cl_summary[cl_summary["valid_shedding_signal"]].copy()
    invalid = cl_summary[~cl_summary["valid_shedding_signal"]].copy()
    ax.plot(valid["Re"], valid["dominant_Cl_St"], marker="o", lw=2.0, label="valid shedding signal")
    if not invalid.empty:
        ax.scatter(invalid["Re"], np.zeros(len(invalid)), marker="x", s=70, color="0.35", label="steady / below Cl threshold")
    ax.set_xlabel("Re")
    ax.set_ylabel("dominant Cl Strouhal number")
    ax.set_title("Dominant shedding frequency from high-resolution Cl(t)")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig03_dominant_Cl_St_by_Re.png", dpi=240)
    fig.savefig(OUT_DIR / "fig03_dominant_Cl_St_by_Re.pdf")
    plt.close(fig)


def write_readme(metrics: pd.DataFrame, cl_summary: pd.DataFrame) -> None:
    max_segments = int(metrics["n_welch_segments_approx"].max())
    min_samples = int(metrics["n_samples"].min())
    text = f"""# 02_frequency_coherence_phase

This stage tests whether the unsteady aerodynamic/shedding signal `Cl(t)` is phase-related to local heat-transfer response.

Inputs:

- `Nu_3D(x,t)` from `00_fullNu3D_xt`, computed from full hot-surface heat flux and full y-z-plane `T_bulk`.
- high-resolution `forceCoeffs.dat` for `Cl(t)` and `Cd(t)`.

Method:

- Dominant shedding frequency is estimated from high-resolution `Cl(t)` in the 8-10 s window.
- `Cl(t)` is interpolated to the available full-3D Nu snapshots.
- Coherence, cross spectral phase, phase-derived delay, zero-lag Pearson, and cross-correlation lag are computed for selected 1 mm strips.

Important limitation:

The full-3D Nu signal has only `{min_samples}` snapshots per Re in the 8-10 s window, because this is how often full volume fields are available. Welch coherence therefore uses only about `{max_segments}` segments. Treat these frequency-domain results as exploratory support, not final standalone statistical proof.

Steady/no-shedding cases are flagged with `valid_shedding_signal = false` when `std(Cl) <= {CL_STD_SHEDDING_THRESHOLD:g}`; their dominant frequency is intentionally reported as `NaN` because a PSD peak would only represent numerical noise.

Outputs:

- `stage02_timeseries_Cl_Nu_Q_selected_strips.csv`
- `stage02_coherence_phase_metrics.csv`
- `stage02_dominant_Cl_frequency_summary.csv`
- `fig01_time_traces_Cl_vs_Nu_x5p5`
- `fig02_Nu3Dxt_coherence_delay_by_x`
- `fig02_QtotalstripW_coherence_delay_by_x`
- `fig03_dominant_Cl_St_by_Re`

Recommended interpretation:

Use this stage to identify candidate strips and delays. For publication-grade spectral claims, increase full-field write frequency or compute exact `Nu_3D(x,t)` online during simulation/postProcess so that `Nu` has the same temporal resolution as `forceCoeffs`.
"""
    (OUT_DIR / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    ts, metrics, cl_summary = build_timeseries_and_metrics()
    ts.to_csv(OUT_DIR / "stage02_timeseries_Cl_Nu_Q_selected_strips.csv", index=False)
    metrics.to_csv(OUT_DIR / "stage02_coherence_phase_metrics.csv", index=False)
    cl_summary.to_csv(OUT_DIR / "stage02_dominant_Cl_frequency_summary.csv", index=False)
    plot_outputs(ts, metrics, cl_summary)
    write_readme(metrics, cl_summary)
    print(f"Wrote stage 02 outputs to {OUT_DIR}")
    print(cl_summary.to_string(index=False))


if __name__ == "__main__":
    main()
