#!/usr/bin/env python3
"""Layer 018: decycling/envelope/phase-consistency tests for run010 layer 017.

This layer addresses the main weakness of direct cross-correlation in a
periodic shedding signal. It reuses the uniformly sampled layer-017 time series
and applies:

1. least-squares removal of f_shed and 2*f_shed from both signals,
2. Hilbert-envelope lag correlation,
3. cross-phase consistency between f_shed and 2*f_shed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RUN_DIR = Path(__file__).resolve().parents[1]
IN_DIR = RUN_DIR / "data" / "017_available_uniform_lag_surrogates"
DATA_DIR = RUN_DIR / "data" / "018_available_signal_decycling"
FIG_DIR = RUN_DIR / "figures" / "018_available_signal_decycling"

VORTEX_CSV = IN_DIR / "run010_017_available_uniform_region_q_lambda2_timeseries.csv"
HEAT_CSV = IN_DIR / "run010_017_available_uniform_heat_timeseries.csv"

F_SHED_HZ = 3.24675
DT = 0.02
T_SHED = 1.0 / F_SHED_HZ
N_SUR = 1000
RNG_SEED = 20260514

PAIRS = [
    ("R_sep", "Nu_tube_wall", "Q_tube", 0.009),
    ("R_near_wake", "Nu_tube_wall", "Q_tube", 0.018),
    ("R_fin_junction", "Nu_wall", "Q_wall", 0.006),
    ("R_fin_sweep", "Nu_fins_wall", "Q_fins", 0.020),
    ("R_far_wake", "Nu_fins_wall", "Q_fins", 0.040),
]


def zscore(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    a = a - np.nanmean(a)
    s = np.nanstd(a)
    return a / s if np.isfinite(s) and s > 0 else np.zeros_like(a)


def detrend_linear(y: np.ndarray) -> np.ndarray:
    x = np.arange(len(y), dtype=float)
    ok = np.isfinite(y)
    if ok.sum() < 3:
        return y - np.nanmean(y)
    p = np.polyfit(x[ok], y[ok], 1)
    return y - np.polyval(p, x)


def remove_harmonics(t: np.ndarray, y: np.ndarray, freqs: list[float]) -> tuple[np.ndarray, np.ndarray]:
    cols = [np.ones_like(t), t - np.mean(t)]
    for f in freqs:
        w = 2 * np.pi * f
        cols.append(np.sin(w * t))
        cols.append(np.cos(w * t))
    X = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    fit = X @ beta
    return y - fit, fit


def analytic_envelope(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    n = len(y)
    Y = np.fft.fft(y)
    h = np.zeros(n)
    if n % 2 == 0:
        h[0] = 1
        h[n // 2] = 1
        h[1 : n // 2] = 2
    else:
        h[0] = 1
        h[1 : (n + 1) // 2] = 2
    return np.abs(np.fft.ifft(Y * h))


def xcorr_lag(x: np.ndarray, y: np.ndarray, dt: float, max_lag_s: float) -> tuple[np.ndarray, np.ndarray]:
    max_k = int(round(max_lag_s / dt))
    lags = np.arange(-max_k, max_k + 1)
    vals = []
    for k in lags:
        if k > 0:
            xs, ys = x[:-k], y[k:]
        elif k < 0:
            xs, ys = x[-k:], y[:k]
        else:
            xs, ys = x, y
        ok = np.isfinite(xs) & np.isfinite(ys)
        vals.append(float(np.mean(zscore(xs[ok]) * zscore(ys[ok]))) if ok.sum() >= 5 else np.nan)
    return lags * dt, np.asarray(vals)


def best_abs_and_pos(lags: np.ndarray, corr: np.ndarray) -> dict[str, float]:
    idx_abs = int(np.nanargmax(np.abs(corr)))
    positive = corr.copy()
    positive[positive < 0] = np.nan
    if np.all(~np.isfinite(positive)):
        idx_pos = idx_abs
    else:
        idx_pos = int(np.nanargmax(positive))
    return {
        "rho_abs_star": float(corr[idx_abs]),
        "abs_rho_abs_star": float(abs(corr[idx_abs])),
        "tau_abs_star_s": float(lags[idx_abs]),
        "rho_pos_star": float(corr[idx_pos]),
        "tau_pos_star_s": float(lags[idx_pos]),
    }


def surrogate_thresholds(x: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> dict[str, float]:
    lo = int(round(0.2 * len(x)))
    hi = int(round(0.8 * len(x)))
    max_abs = []
    max_pos = []
    for _ in range(N_SUR):
        xs = np.roll(x, int(rng.integers(lo, hi)))
        _, c = xcorr_lag(xs, y, DT, T_SHED)
        max_abs.append(float(np.nanmax(np.abs(c))))
        max_pos.append(float(np.nanmax(c)))
    return {
        "sur_abs_p95": float(np.nanpercentile(max_abs, 95)),
        "sur_abs_p99": float(np.nanpercentile(max_abs, 99)),
        "sur_pos_p95": float(np.nanpercentile(max_pos, 95)),
        "sur_pos_p99": float(np.nanpercentile(max_pos, 99)),
    }


def cross_phase_delay(t: np.ndarray, x: np.ndarray, y: np.ndarray, f: float) -> tuple[float, float, float]:
    # Least-squares complex coefficient at exactly f, avoiding FFT-bin mismatch.
    e = np.exp(-1j * 2 * np.pi * f * t)
    X = np.vdot(e, x)
    Y = np.vdot(e, y)
    phase = float(np.angle(np.conj(X) * Y))
    # Positive tau means x leads y. For y(t)=x(t-tau), phase(conj(X)Y)=-w*tau.
    tau = -phase / (2 * np.pi * f)
    period = 1.0 / f
    while tau > 0.5 * period:
        tau -= period
    while tau < -0.5 * period:
        tau += period
    coh_like = float((abs(np.conj(X) * Y) ** 2) / ((abs(X) ** 2) * (abs(Y) ** 2) + 1e-30))
    return phase, tau, coh_like


def wrap_pi(a: float) -> float:
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def classify(row: dict[str, float], tau_conv: float) -> str:
    if row["rho_pos_star"] > row["sur_pos_p95"] and row["tau_pos_star_s"] > 0 and row["tau_pos_star_s"] <= 0.5 * T_SHED:
        if abs(row["tau_pos_star_s"] - tau_conv) <= 0.5 * T_SHED:
            return "positive coupling survives"
    if row["abs_rho_abs_star"] > row["sur_abs_p95"]:
        return "only signed/periodic coupling"
    return "not significant after test"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    vortex = pd.read_csv(VORTEX_CSV)
    heat = pd.read_csv(HEAT_CSV)
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    curves = []

    for region, nu_col, q_col, dist in PAIRS:
        sub = vortex[vortex["region"] == region].sort_values("time_s")
        base = sub.merge(heat, on="time_s", how="inner")
        t = base["time_s"].to_numpy(float)
        tau_conv = dist / 0.253
        for structure_col, structure_label in [("I_Lambda2_star", "I_Lambda2*"), ("I_Q_star", "I_Q*")]:
            x0 = zscore(detrend_linear(base[structure_col].to_numpy(float)))
            x_res, x_fit = remove_harmonics(t, x0, [F_SHED_HZ, 2 * F_SHED_HZ])
            x_env = zscore(detrend_linear(analytic_envelope(x0)))
            for response_label, response_col in [("Nu", nu_col)]:
                y0 = zscore(detrend_linear(base[response_col].to_numpy(float)))
                y_res, y_fit = remove_harmonics(t, y0, [F_SHED_HZ, 2 * F_SHED_HZ])
                y_env = zscore(detrend_linear(analytic_envelope(y0)))

                for method, x, y in [
                    ("raw", x0, y0),
                    ("decycled_residual", zscore(x_res), zscore(y_res)),
                    ("envelope", x_env, y_env),
                ]:
                    lags, corr = xcorr_lag(x, y, DT, T_SHED)
                    rec = best_abs_and_pos(lags, corr)
                    sur = surrogate_thresholds(x, y, rng)
                    phase1, tau1, coh1 = cross_phase_delay(t, x, y, F_SHED_HZ)
                    phase2, tau2, coh2 = cross_phase_delay(t, x, y, 2 * F_SHED_HZ)
                    phase_consistency = wrap_pi(phase2 - 2 * phase1)
                    rec.update(
                        {
                            "pair": f"{region} -> {response_col}",
                            "region": region,
                            "structure_signal": structure_label,
                            "response_signal": response_label,
                            "response_column": response_col,
                            "method": method,
                            "n": len(base),
                            "tau_conv_s_assumed": tau_conv,
                            "phase_f_rad": phase1,
                            "phase_2f_rad": phase2,
                            "phase_2f_minus_2phase_f_wrapped_rad": phase_consistency,
                            "tau_phase_f_s": tau1,
                            "tau_phase_2f_s": tau2,
                            "tau_phase_diff_s": tau2 - tau1,
                            "coh_like_f": coh1,
                            "coh_like_2f": coh2,
                        }
                    )
                    rec.update(sur)
                    rec["class"] = classify(rec, tau_conv)
                    rows.append(rec)
                    for lag, c in zip(lags, corr):
                        curves.append(
                            {
                                "pair": rec["pair"],
                                "structure_signal": structure_label,
                                "response_signal": response_label,
                                "method": method,
                                "lag_s": lag,
                                "lag_over_T_shed": lag / T_SHED,
                                "corr": c,
                                "sur_abs_p95": sur["sur_abs_p95"],
                                "sur_pos_p95": sur["sur_pos_p95"],
                                "tau_abs_star_s": rec["tau_abs_star_s"],
                                "rho_abs_star": rec["rho_abs_star"],
                                "tau_pos_star_s": rec["tau_pos_star_s"],
                                "rho_pos_star": rec["rho_pos_star"],
                            }
                        )

    summary = pd.DataFrame(rows)
    curve_df = pd.DataFrame(curves)
    summary.to_csv(DATA_DIR / "run010_018_decycling_envelope_phase_summary.csv", index=False, float_format="%.10g")
    curve_df.to_csv(DATA_DIR / "run010_018_decycling_envelope_phase_curves.csv", index=False, float_format="%.10g")

    # Figure: the main I_Lambda2* -> Nu hypothesis pairs after decycling and envelope transform.
    fig, axes = plt.subplots(len(PAIRS), 2, figsize=(12, 11), sharex=True)
    for i, (region, nu_col, _, _) in enumerate(PAIRS):
        pair = f"{region} -> {nu_col}"
        for j, method in enumerate(["decycled_residual", "envelope"]):
            ax = axes[i, j]
            c = curve_df[
                (curve_df["pair"] == pair)
                & (curve_df["structure_signal"] == "I_Lambda2*")
                & (curve_df["response_signal"] == "Nu")
                & (curve_df["method"] == method)
            ]
            r = summary[
                (summary["pair"] == pair)
                & (summary["structure_signal"] == "I_Lambda2*")
                & (summary["response_signal"] == "Nu")
                & (summary["method"] == method)
            ].iloc[0]
            ax.plot(c["lag_s"], c["corr"], color="#2f5d8c", lw=1.5)
            ax.axhline(0, color="0.25", lw=0.8)
            ax.fill_between(c["lag_s"], -c["sur_abs_p95"], c["sur_abs_p95"], color="#f2c14e", alpha=0.22)
            ax.axvline(r["tau_abs_star_s"], color="#1b9e77", lw=1.1)
            ax.axvline(r["tau_pos_star_s"], color="#d95f02", lw=1.1, ls="--")
            ax.set_title(f"{pair}, {method}: abs={r['rho_abs_star']:+.2f}@{r['tau_abs_star_s']:+.2f}s, pos={r['rho_pos_star']:+.2f}")
            ax.set_ylabel("rho")
    axes[-1, 0].set_xlabel("lag tau [s]")
    axes[-1, 1].set_xlabel("lag tau [s]")
    fig.suptitle("run010 layer 018: decycled residual and envelope lag tests, I_Lambda2* -> Nu", y=0.995)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run010_018_decycled_envelope_lambda2_nu.png", dpi=220)
    fig.savefig(FIG_DIR / "run010_018_decycled_envelope_lambda2_nu.pdf")
    plt.close(fig)

    l2nu = summary[(summary["structure_signal"] == "I_Lambda2*") & (summary["response_signal"] == "Nu")]
    iqnu = summary[(summary["structure_signal"] == "I_Q*") & (summary["response_signal"] == "Nu")]
    best_env = summary[summary["method"] == "envelope"].sort_values("rho_pos_star", ascending=False).head(8)
    best_dec = summary[summary["method"] == "decycled_residual"].sort_values("abs_rho_abs_star", ascending=False).head(8)

    def md_table(df: pd.DataFrame, cols: list[str]) -> str:
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, row in df[cols].iterrows():
            vals = []
            for col in cols:
                val = row[col]
                vals.append(f"{val:.4g}" if isinstance(val, float) else str(val))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    report = [
        "# V4b_3D run010 layer 018",
        "",
        "Decycling, envelope-correlation, and harmonic phase-consistency tests on layer-017 uniform signals.",
        "",
        "## Method",
        "",
        "- `raw`: direct signal after linear detrending and z-score.",
        "- `decycled_residual`: least-squares removal of `f_shed` and `2*f_shed` from both structure and heat signals, then lag scan of residuals.",
        "- `envelope`: analytic-signal envelope lag scan, testing cycle-by-cycle amplitude modulation.",
        "- cyclic-shift surrogates: `1000` per pair/method.",
        "- positive lag means structure signal leads heat response.",
        "- `rho_pos_star` tracks the strongest positive correlation; `rho_abs_star` tracks the strongest signed relation by absolute magnitude.",
        "",
        "## I_Lambda2* -> Nu, all methods",
        "",
        md_table(
            l2nu[
                [
                    "pair",
                    "method",
                    "rho_abs_star",
                    "tau_abs_star_s",
                    "rho_pos_star",
                    "tau_pos_star_s",
                    "sur_pos_p95",
                    "phase_2f_minus_2phase_f_wrapped_rad",
                    "tau_phase_f_s",
                    "tau_phase_2f_s",
                    "class",
                ]
            ],
            [
                "pair",
                "method",
                "rho_abs_star",
                "tau_abs_star_s",
                "rho_pos_star",
                "tau_pos_star_s",
                "sur_pos_p95",
                "phase_2f_minus_2phase_f_wrapped_rad",
                "tau_phase_f_s",
                "tau_phase_2f_s",
                "class",
            ],
        ),
        "",
        "## Strongest envelope positive correlations",
        "",
        md_table(
            best_env[
                [
                    "pair",
                    "structure_signal",
                    "response_signal",
                    "rho_pos_star",
                    "tau_pos_star_s",
                    "sur_pos_p95",
                    "class",
                ]
            ],
            ["pair", "structure_signal", "response_signal", "rho_pos_star", "tau_pos_star_s", "sur_pos_p95", "class"],
        ),
        "",
        "## Strongest decycled residual signed relations",
        "",
        md_table(
            best_dec[
                [
                    "pair",
                    "structure_signal",
                    "response_signal",
                    "rho_abs_star",
                    "tau_abs_star_s",
                    "rho_pos_star",
                    "tau_pos_star_s",
                    "sur_abs_p95",
                    "class",
                ]
            ],
            ["pair", "structure_signal", "response_signal", "rho_abs_star", "tau_abs_star_s", "rho_pos_star", "tau_pos_star_s", "sur_abs_p95", "class"],
        ),
        "",
        "## Interpretation",
        "",
        "If decycled residual correlations collapse, the layer-017 coupling is mostly common shedding rhythm.",
        "If envelope correlations remain positive and significant at positive lag, stronger cycles of vortex activity precede stronger heat-transfer cycles.",
        "If `phase_2f_minus_2phase_f_wrapped_rad` is near zero and `tau_phase_f_s` is close to `tau_phase_2f_s`, a true time-delay interpretation is plausible.",
        "Large phase mismatch means mode-specific phase locking rather than one convective delay.",
    ]
    (DATA_DIR / "run010_018_decycling_envelope_phase_analysis.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (DATA_DIR / "run010_018_decycling_envelope_phase_metadata.json").write_text(
        json.dumps({"n_surrogates": N_SUR, "f_shed_hz": F_SHED_HZ, "dt": DT}, indent=2),
        encoding="utf-8",
    )

    print("\n".join(report))


if __name__ == "__main__":
    main()
