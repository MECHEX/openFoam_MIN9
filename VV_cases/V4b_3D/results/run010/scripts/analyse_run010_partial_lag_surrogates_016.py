#!/usr/bin/env python3
"""Partial run010 lag scan with cyclic-shift surrogates.

This is an intentionally diagnostic layer. The input vortex series are the
48 phase-selected layer-015 snapshots, not a complete uniformly sampled
I_R(t) record. The script therefore interpolates the sparse selected samples to
the field-output cadence and labels all outputs as partial/sparse.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_IN = ROOT / "data" / "015_partial" / "run010_015_partial_region_structure_heat_merged.csv"
DATA_OUT = ROOT / "data" / "016_partial_lag_surrogates"
FIG_OUT = ROOT / "figures" / "016_partial_lag_surrogates"

F_SHED_HZ = 3.24675
T_SHED = 1.0 / F_SHED_HZ
DT_GRID = 0.02
N_SUR = 1000
RNG_SEED = 20260514

PAIRS = [
    {
        "pair": "R_sep -> Nu_tube_wall",
        "region": "R_sep",
        "surface": "Nu_tube_wall",
        "nu_column": "paired_Nu",
        "q_column": "paired_Q",
        "L_RS_m": 0.009,
    },
    {
        "pair": "R_near_wake -> Nu_tube_wall",
        "region": "R_near_wake",
        "surface": "Nu_tube_wall",
        "nu_column": "paired_Nu",
        "q_column": "paired_Q",
        "L_RS_m": 0.018,
    },
    {
        "pair": "R_fin_junction -> Nu_wall",
        "region": "R_fin_junction",
        "surface": "Nu_wall",
        "nu_column": "paired_Nu",
        "q_column": "paired_Q",
        "L_RS_m": 0.006,
    },
    {
        "pair": "R_fin_sweep -> Nu_fins_wall",
        "region": "R_fin_sweep",
        "surface": "Nu_fins_wall",
        "nu_column": "paired_Nu",
        "q_column": "paired_Q",
        "L_RS_m": 0.020,
    },
    {
        "pair": "R_far_wake -> Nu_fins_wall",
        "region": "R_far_wake",
        "surface": "Nu_fins_wall",
        "nu_column": "paired_Nu",
        "q_column": "paired_Q",
        "L_RS_m": 0.040,
    },
]


def zscore(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    a = a - np.nanmean(a)
    s = np.nanstd(a)
    if not np.isfinite(s) or s <= 0:
        return np.zeros_like(a)
    return a / s


def detrend_linear(y: np.ndarray) -> np.ndarray:
    x = np.arange(len(y), dtype=float)
    ok = np.isfinite(y)
    if ok.sum() < 3:
        return y - np.nanmean(y)
    p = np.polyfit(x[ok], y[ok], 1)
    return y - np.polyval(p, x)


def tukey(n: int, alpha: float = 0.1) -> np.ndarray:
    if alpha <= 0:
        return np.ones(n)
    if alpha >= 1:
        return np.hanning(n)
    w = np.ones(n)
    edge = int(math.floor(alpha * (n - 1) / 2.0))
    if edge < 1:
        return w
    x = np.linspace(0, 1, edge + 1)
    taper = 0.5 * (1 + np.cos(np.pi * (2 * x / alpha - 1)))
    w[: edge + 1] = taper
    w[-edge - 1 :] = taper[::-1]
    return w


def interp_to_grid(t: np.ndarray, y: np.ndarray, grid: np.ndarray) -> np.ndarray:
    order = np.argsort(t)
    t = np.asarray(t, dtype=float)[order]
    y = np.asarray(y, dtype=float)[order]
    uniq_t, uniq_idx = np.unique(t, return_index=True)
    uniq_y = y[uniq_idx]
    return np.interp(grid, uniq_t, uniq_y)


def xcorr_lag(x: np.ndarray, y: np.ndarray, dt: float, max_lag_s: float) -> tuple[np.ndarray, np.ndarray]:
    """Return corr(lag) where positive lag means x(t) leads y(t + lag)."""
    max_k = int(round(max_lag_s / dt))
    lags = np.arange(-max_k, max_k + 1)
    out = []
    for k in lags:
        if k > 0:
            xs, ys = x[:-k], y[k:]
        elif k < 0:
            xs, ys = x[-k:], y[:k]
        else:
            xs, ys = x, y
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < 5:
            out.append(np.nan)
            continue
        xs = zscore(xs[ok])
        ys = zscore(ys[ok])
        out.append(float(np.mean(xs * ys)))
    return lags * dt, np.asarray(out)


def best_lag(lags: np.ndarray, corr: np.ndarray) -> tuple[float, float]:
    idx = int(np.nanargmax(np.abs(corr)))
    return float(lags[idx]), float(corr[idx])


def spectral_phase_tau(x: np.ndarray, y: np.ndarray, dt: float, f_target: float) -> tuple[float, float]:
    freqs = np.fft.rfftfreq(len(x), d=dt)
    xh = np.fft.rfft(zscore(x))
    yh = np.fft.rfft(zscore(y))
    idx = int(np.argmin(np.abs(freqs - f_target)))
    cpsd = np.conj(xh[idx]) * yh[idx]
    phase = float(np.angle(cpsd))
    tau = phase / (2 * np.pi * freqs[idx]) if freqs[idx] > 0 else np.nan
    # Wrap to the principal shedding period.
    while tau > 0.5 / freqs[idx]:
        tau -= 1.0 / freqs[idx]
    while tau < -0.5 / freqs[idx]:
        tau += 1.0 / freqs[idx]
    return float(tau), float(freqs[idx])


def verdict(rho_abs: float, tau: float, p95: float, p99: float, tau_conv: float) -> str:
    if not np.isfinite(rho_abs):
        return "invalid"
    if rho_abs <= p95:
        return "not significant"
    if tau <= 0:
        return "significant but wrong-direction/zero-lag"
    if tau > 0.5 * T_SHED:
        return "significant but lag > T_shed/2"
    if abs(tau - tau_conv) > 0.5 * T_SHED:
        return "significant but convection-lag mismatch"
    if rho_abs > p99:
        return "confirmed p<0.01 diagnostic"
    return "confirmed p<0.05 diagnostic"


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append(f"{val:.4g}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    FIG_OUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_IN)
    rng = np.random.default_rng(RNG_SEED)
    t_min = float(df["time_s"].min())
    t_max = float(df["time_s"].max())
    grid = np.arange(t_min, t_max + 0.5 * DT_GRID, DT_GRID)
    win = tukey(len(grid), alpha=0.1)
    max_shift_lo = max(1, int(round(0.2 * len(grid))))
    max_shift_hi = max(max_shift_lo + 1, int(round(0.8 * len(grid))))

    rows = []
    curves = []

    for pair in PAIRS:
        sub = df[df["region"] == pair["region"]].copy().sort_values("time_s")
        t = sub["time_s"].to_numpy(float)
        y_nu_raw = sub[pair["nu_column"]].to_numpy(float)
        y_q_raw = sub[pair["q_column"]].to_numpy(float)
        tau_conv = pair["L_RS_m"] / 0.253

        for structure_col, structure_label in [
            ("I_Lambda2_star", "I_Lambda2*"),
            ("I_Q_star", "I_Q*"),
        ]:
            x_raw = sub[structure_col].to_numpy(float)
            x = interp_to_grid(t, x_raw, grid)
            y_nu = interp_to_grid(t, y_nu_raw, grid)
            y_q = interp_to_grid(t, y_q_raw, grid)

            for response_label, y in [("Nu", y_nu), ("Q", y_q)]:
                xp = zscore(detrend_linear(x)) * win
                yp = zscore(detrend_linear(y)) * win
                lags, corr = xcorr_lag(xp, yp, DT_GRID, T_SHED)
                tau_star, rho_star = best_lag(lags, corr)
                rho_abs = abs(rho_star)

                sur_max = []
                for _ in range(N_SUR):
                    shift = int(rng.integers(max_shift_lo, max_shift_hi))
                    xs = np.roll(xp, shift)
                    _, cs = xcorr_lag(xs, yp, DT_GRID, T_SHED)
                    sur_max.append(float(np.nanmax(np.abs(cs))))
                sur_max = np.asarray(sur_max)
                p95 = float(np.nanpercentile(sur_max, 95))
                p99 = float(np.nanpercentile(sur_max, 99))
                p_emp = float((1 + np.sum(sur_max >= rho_abs)) / (N_SUR + 1))
                tau_phase, f_bin = spectral_phase_tau(xp, yp, DT_GRID, F_SHED_HZ)

                rows.append(
                    {
                        "pair": pair["pair"],
                        "region": pair["region"],
                        "surface": pair["surface"],
                        "structure_signal": structure_label,
                        "response_signal": response_label,
                        "n_selected_snapshots": len(sub),
                        "n_interpolated_grid": len(grid),
                        "dt_grid_s": DT_GRID,
                        "f_shed_hz": F_SHED_HZ,
                        "T_shed_s": T_SHED,
                        "rho_star": rho_star,
                        "abs_rho_star": rho_abs,
                        "tau_star_s": tau_star,
                        "tau_over_T_shed": tau_star / T_SHED,
                        "surrogate_p95_absrho": p95,
                        "surrogate_p99_absrho": p99,
                        "empirical_p": p_emp,
                        "tau_phase_s": tau_phase,
                        "phase_frequency_bin_hz": f_bin,
                        "L_RS_m_assumed": pair["L_RS_m"],
                        "tau_conv_s_assumed": tau_conv,
                        "verdict": verdict(rho_abs, tau_star, p95, p99, tau_conv),
                    }
                )

                for lag, c in zip(lags, corr):
                    curves.append(
                        {
                            "pair": pair["pair"],
                            "structure_signal": structure_label,
                            "response_signal": response_label,
                            "lag_s": lag,
                            "lag_over_T_shed": lag / T_SHED,
                            "corr": c,
                            "surrogate_p95_absrho": p95,
                            "surrogate_p99_absrho": p99,
                            "tau_star_s": tau_star,
                            "rho_star": rho_star,
                            "tau_conv_s_assumed": tau_conv,
                        }
                    )

    result = pd.DataFrame(rows)
    curve_df = pd.DataFrame(curves)
    result.to_csv(DATA_OUT / "run010_016_partial_lag_surrogate_summary.csv", index=False)
    curve_df.to_csv(DATA_OUT / "run010_016_partial_lag_surrogate_curves.csv", index=False)

    # Main figure: Lambda2 -> Nu for the five hypothesis pairs.
    fig, axes = plt.subplots(len(PAIRS), 1, figsize=(8.4, 10.8), sharex=True)
    if len(PAIRS) == 1:
        axes = [axes]
    for ax, pair in zip(axes, PAIRS):
        mask = (
            (curve_df["pair"] == pair["pair"])
            & (curve_df["structure_signal"] == "I_Lambda2*")
            & (curve_df["response_signal"] == "Nu")
        )
        c = curve_df[mask].copy()
        r = result[
            (result["pair"] == pair["pair"])
            & (result["structure_signal"] == "I_Lambda2*")
            & (result["response_signal"] == "Nu")
        ].iloc[0]
        ax.plot(c["lag_s"], c["corr"], color="#2f5d8c", lw=1.8)
        ax.axhline(0, color="0.25", lw=0.8)
        ax.fill_between(
            c["lag_s"],
            -c["surrogate_p95_absrho"],
            c["surrogate_p95_absrho"],
            color="#f2c14e",
            alpha=0.25,
            label="surrogate 95%" if ax is axes[0] else None,
        )
        ax.fill_between(
            c["lag_s"],
            -c["surrogate_p99_absrho"],
            c["surrogate_p99_absrho"],
            color="#d95d39",
            alpha=0.16,
            label="surrogate 99%" if ax is axes[0] else None,
        )
        ax.axvline(r["tau_star_s"], color="#1b9e77", lw=1.4)
        ax.axvline(r["tau_conv_s_assumed"], color="#7b3294", lw=1.2, ls="--")
        ax.axvline(-r["tau_conv_s_assumed"], color="#7b3294", lw=1.0, ls=":")
        ax.set_ylabel("rho")
        ax.set_title(
            f"{pair['pair']}: rho*={r['rho_star']:+.3f}, "
            f"tau*={r['tau_star_s']:+.3f}s, p={r['empirical_p']:.3f}"
        )
    axes[-1].set_xlabel("lag tau [s], positive = structure leads heat")
    axes[0].legend(loc="upper right", frameon=False)
    fig.suptitle("run010 partial layer 016: sparse lag scan, I_Lambda2* -> Nu", y=0.995)
    fig.tight_layout()
    fig.savefig(FIG_OUT / "run010_016_partial_lag_surrogate_lambda2_nu.png", dpi=220)
    fig.savefig(FIG_OUT / "run010_016_partial_lag_surrogate_lambda2_nu.pdf")
    plt.close(fig)

    # Compact heatmap-like summary for all structure/response combinations.
    compact = result.pivot_table(
        index=["pair", "structure_signal"],
        columns="response_signal",
        values=["rho_star", "tau_star_s", "empirical_p"],
        aggfunc="first",
    )
    compact.to_csv(DATA_OUT / "run010_016_partial_lag_surrogate_compact.csv")

    best = result.sort_values(["empirical_p", "abs_rho_star"], ascending=[True, False]).head(8)
    md = [
        "# V4b_3D run010 partial layer 016",
        "",
        "Sparse lag scan with cyclic-shift surrogates for the incomplete run010.",
        "",
        "## Important limitation",
        "",
        "This analysis uses the 48 phase-selected layer-015 snapshots, not a",
        "complete uniformly sampled vortex-intensity time series. The selected",
        "samples were interpolated to `dt = 0.02 s` before lag scanning. Treat",
        "this as a diagnostic/prototype result only; recompute after run010",
        "reaches `t = 10 s` using a uniformly sampled `I_R(t)` series.",
        "",
        "## Inputs",
        "",
        f"- input table: `{DATA_IN.relative_to(ROOT)}`",
        f"- selected snapshots per region: `48`",
        f"- interpolated grid: `{len(grid)}` samples, `dt = {DT_GRID:.3f} s`",
        f"- lag range: `+-T_shed = +-{T_SHED:.4f} s`",
        f"- cyclic-shift surrogates: `{N_SUR}`",
        "",
        "## Best diagnostic associations",
        "",
        markdown_table(
            best[
                [
                    "pair",
                    "structure_signal",
                    "response_signal",
                    "rho_star",
                    "tau_star_s",
                    "tau_over_T_shed",
                    "surrogate_p95_absrho",
                    "surrogate_p99_absrho",
                    "empirical_p",
                    "tau_conv_s_assumed",
                    "verdict",
                ]
            ]
        ),
        "",
        "## Interpretation",
        "",
        "A positive `tau_star_s` means that the structure signal leads the heat",
        "response. A negative value means the heat response leads, or the pair is",
        "phase-locked in a way that the present sparse diagnostic cannot resolve",
        "directionally. Because the input is phase-selected rather than uniformly",
        "sampled, the surrogate p-values should be read as screening metrics, not",
        "final publication-grade significance.",
    ]
    (DATA_OUT / "run010_016_partial_lag_surrogate_analysis.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8"
    )

    meta = {
        "status": "partial sparse diagnostic",
        "input": str(DATA_IN),
        "outputs": {
            "summary_csv": str(DATA_OUT / "run010_016_partial_lag_surrogate_summary.csv"),
            "curves_csv": str(DATA_OUT / "run010_016_partial_lag_surrogate_curves.csv"),
            "figure_png": str(FIG_OUT / "run010_016_partial_lag_surrogate_lambda2_nu.png"),
        },
        "f_shed_hz": F_SHED_HZ,
        "T_shed_s": T_SHED,
        "dt_grid_s": DT_GRID,
        "n_surrogates": N_SUR,
        "limitation": "48 phase-selected snapshots interpolated to uniform grid; not full time series",
    }
    (DATA_OUT / "run010_016_partial_lag_surrogate_metadata.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
