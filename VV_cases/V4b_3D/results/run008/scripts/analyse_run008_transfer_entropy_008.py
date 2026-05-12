"""
Run008 exploratory transfer-entropy analysis.

Layer 008:
- directional TE between Cl and global heat-transfer signals,
- TE from Cl to reduced/bin-averaged fin Nu_local(x),
- TE between Cl/Q_wall and selected POD coefficients,
- circular-shift surrogate test for confidence thresholds.

This is intentionally conservative: 8 s at 200 Hz is useful, but not a huge
record for nonlinear directionality. Results are reported as exploratory and
only highlighted when they exceed the surrogate confidence level.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


RUN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = RUN_DIR / "data" / "008"
FIG_DIR = RUN_DIR / "figures" / "008"

WINDOW = (2.0, 10.0)
F_SHED = 3.2787
RNG_SEED = 842008

# TE settings. Lag grid covers short convective/filter response without
# overfitting too many delays for a 1601-sample record.
N_BINS = 4
GLOBAL_LAGS_S = np.array([0.005, 0.010, 0.020, 0.040, 0.060, 0.080, 0.120, 0.160, 0.240, 0.320, 0.480])
FIN_LAGS_S = np.array([0.005, 0.020, 0.040, 0.080, 0.160, 0.320])
N_SURROGATES_GLOBAL = 250
N_SURROGATES_SPATIAL = 160
N_FIN_GROUPS = 16


@dataclass
class TERow:
    pair: str
    source: str
    target: str
    category: str
    lag_s: float
    te_bits: float
    surrogate_mean_bits: float
    surrogate_p95_bits: float
    surrogate_p99_bits: float
    excess_over_p95_bits: float
    z_score: float
    p_empirical: float
    significant_p95: bool
    significant_p99: bool


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_cols(path: Path) -> dict[str, np.ndarray]:
    cols: dict[str, list[float]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key, val in row.items():
                cols.setdefault(key, []).append(float(val))
    return {k: np.asarray(v, dtype=float) for k, v in cols.items()}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def standardize(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    finite = np.isfinite(x)
    out = np.full_like(x, np.nan)
    if np.sum(finite) < 8:
        return out
    mu = float(np.mean(x[finite]))
    sd = float(np.std(x[finite]))
    if sd == 0.0 or not np.isfinite(sd):
        return out
    out[finite] = (x[finite] - mu) / sd
    return out


def quantile_discretize(x: np.ndarray, n_bins: int = N_BINS) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    finite = np.isfinite(x)
    out = np.full(x.shape, -1, dtype=np.int16)
    vals = x[finite]
    if vals.size < n_bins * 8 or np.nanstd(vals) == 0:
        return out
    edges = np.nanquantile(vals, np.linspace(0, 1, n_bins + 1)[1:-1])
    edges = np.unique(edges)
    if edges.size == 0:
        return out
    out[finite] = np.digitize(vals, edges, right=False).astype(np.int16)
    return out


def transfer_entropy_discrete(source: np.ndarray, target: np.ndarray, lag: int, n_bins: int = N_BINS) -> float:
    """TE source -> target in bits: I(y_future; x_past | y_past)."""
    if lag < 1 or len(source) != len(target) or len(source) <= lag + 8:
        return float("nan")

    x = quantile_discretize(source, n_bins)
    y = quantile_discretize(target, n_bins)
    y_future = y[lag:]
    y_past = y[:-lag]
    x_past = x[:-lag]
    valid = (x_past >= 0) & (y_past >= 0) & (y_future >= 0)
    if np.sum(valid) < 50:
        return float("nan")

    xf = x_past[valid].astype(np.int64)
    yp = y_past[valid].astype(np.int64)
    yf = y_future[valid].astype(np.int64)
    base = n_bins

    idx_yf_yp_xp = (yf * base + yp) * base + xf
    idx_yp_xp = yp * base + xf
    idx_yf_yp = yf * base + yp
    idx_yp = yp

    c_yf_yp_xp = np.bincount(idx_yf_yp_xp, minlength=base**3).astype(float)
    c_yp_xp = np.bincount(idx_yp_xp, minlength=base**2).astype(float)
    c_yf_yp = np.bincount(idx_yf_yp, minlength=base**2).astype(float)
    c_yp = np.bincount(idx_yp, minlength=base).astype(float)
    n = float(len(yf))

    te = 0.0
    for a in range(base):
        for b in range(base):
            denom_yf_yp = c_yf_yp[a * base + b]
            denom_yp = c_yp[b]
            if denom_yf_yp <= 0 or denom_yp <= 0:
                continue
            p_yf_given_yp = denom_yf_yp / denom_yp
            for c in range(base):
                count = c_yf_yp_xp[(a * base + b) * base + c]
                denom_yp_xp = c_yp_xp[b * base + c]
                if count <= 0 or denom_yp_xp <= 0:
                    continue
                p_joint = count / n
                p_yf_given_yp_xp = count / denom_yp_xp
                te += p_joint * math.log2(p_yf_given_yp_xp / p_yf_given_yp)
    return float(max(te, 0.0))


def surrogate_shifts(n: int, n_surrogates: int, lag: int, rng: np.random.Generator) -> np.ndarray:
    # Avoid tiny shifts that leave source and target nearly aligned.
    lo = max(10 * lag, n // 20)
    hi = n - lo
    if hi <= lo:
        lo, hi = max(lag + 2, 8), n - max(lag + 2, 8)
    return rng.integers(lo, hi, size=n_surrogates)


def te_with_surrogates(
    time: np.ndarray,
    source: np.ndarray,
    target: np.ndarray,
    lags_s: np.ndarray,
    n_surrogates: int,
    rng: np.random.Generator,
) -> tuple[TERow, list[dict[str, float]]]:
    dt = float(np.median(np.diff(time)))
    source = standardize(source)
    target = standardize(target)
    valid = np.isfinite(source) & np.isfinite(target)
    source = source[valid]
    target = target[valid]
    lag_curve: list[dict[str, float]] = []
    best: TERow | None = None
    for lag_s in lags_s:
        lag = max(1, int(round(float(lag_s) / dt)))
        actual = transfer_entropy_discrete(source, target, lag)
        shifts = surrogate_shifts(len(source), n_surrogates, lag, rng)
        sur = np.asarray([transfer_entropy_discrete(np.roll(source, int(s)), target, lag) for s in shifts], dtype=float)
        sur = sur[np.isfinite(sur)]
        if sur.size == 0 or not np.isfinite(actual):
            mean = p95 = p99 = z = p_emp = float("nan")
            sig95 = sig99 = False
        else:
            mean = float(np.mean(sur))
            std = float(np.std(sur, ddof=1)) if sur.size > 1 else float("nan")
            p95 = float(np.percentile(sur, 95))
            p99 = float(np.percentile(sur, 99))
            z = float((actual - mean) / std) if std > 0 else float("nan")
            p_emp = float((1 + np.sum(sur >= actual)) / (sur.size + 1))
            sig95 = bool(actual > p95)
            sig99 = bool(actual > p99)
        lag_curve.append(
            {
                "lag_s": float(lag * dt),
                "te_bits": float(actual),
                "surrogate_mean_bits": mean,
                "surrogate_p95_bits": p95,
                "surrogate_p99_bits": p99,
                "z_score": z,
                "p_empirical": p_emp,
            }
        )
        row = TERow(
            pair="",
            source="",
            target="",
            category="",
            lag_s=float(lag * dt),
            te_bits=float(actual),
            surrogate_mean_bits=mean,
            surrogate_p95_bits=p95,
            surrogate_p99_bits=p99,
            excess_over_p95_bits=float(actual - p95) if np.isfinite(p95) else float("nan"),
            z_score=z,
            p_empirical=p_emp,
            significant_p95=sig95,
            significant_p99=sig99,
        )
        if best is None or (row.excess_over_p95_bits > best.excess_over_p95_bits):
            best = row
    assert best is not None
    return best, lag_curve


def annotate_row(row: TERow, pair: str, source: str, target: str, category: str) -> TERow:
    row.pair = pair
    row.source = source
    row.target = target
    row.category = category
    return row


def load_global_signals() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    fin = np.load(RUN_DIR / "data" / "005" / "run008_005_fin_nu_arrays.npz")
    time = np.asarray(fin["times"], dtype=float)
    cl = np.asarray(fin["cl"], dtype=float)
    heat = read_csv_cols(RUN_DIR / "data" / "003" / "run008_003_heat_balance_timeseries.csv")
    signals = {
        "Cl": cl,
        "Q_wall": np.interp(time, heat["time"], heat["Q_wall"]),
        "Q_tube": np.interp(time, heat["time"], heat["Q_tube"]),
        "Q_fins": np.interp(time, heat["time"], heat["Q_fins"]),
        "Nu_tube": np.interp(time, heat["time"], heat["Nu_tube_wall"]),
        "Nu_fins": np.interp(time, heat["time"], heat["Nu_fins_wall"]),
        "Nu_EB": np.interp(time, heat["time"], heat["Nu_EB"]),
    }
    return time, signals


def reduced_fin_groups() -> tuple[np.ndarray, list[tuple[str, float, np.ndarray]]]:
    data = np.load(RUN_DIR / "data" / "005" / "run008_005_fin_nu_arrays.npz")
    x = np.asarray(data["x_centers"], dtype=float)
    rows: list[tuple[str, float, np.ndarray]] = []
    for label, series_key, valid_key in [
        ("fin_z_min", "min_series", "valid_min"),
        ("fin_z_max", "max_series", "valid_max"),
    ]:
        series = np.asarray(data[series_key], dtype=float)
        valid = np.asarray(data[valid_key], dtype=bool)
        valid_idx = np.where(valid)[0]
        chunks = np.array_split(valid_idx, N_FIN_GROUPS)
        for i, idx in enumerate(chunks):
            if idx.size == 0:
                continue
            x_mid = float(np.nanmean(x[idx]))
            rows.append((f"{label}_xbin_{i+1:02d}", x_mid, np.nanmean(series[:, idx], axis=1)))
    return np.asarray(data["times"], dtype=float), rows


def modal_signals() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    data = np.load(RUN_DIR / "data" / "006" / "run008_006_modal_arrays.npz")
    t = np.asarray(data["times"], dtype=float)
    out: dict[str, np.ndarray] = {}
    for prefix, key in [("U", "pod_u_coeff"), ("T", "pod_t_coeff"), ("joint", "pod_joint_coeff")]:
        coeff = np.asarray(data[key], dtype=float)
        for i in range(min(4, coeff.shape[0])):
            out[f"POD_{prefix}_{i+1}"] = coeff[i]
    heat = read_csv_cols(RUN_DIR / "data" / "003" / "run008_003_heat_balance_timeseries.csv")
    _, global_sig = load_global_signals()
    t_force = np.load(RUN_DIR / "data" / "005" / "run008_005_fin_nu_arrays.npz")["times"]
    out["Cl"] = np.interp(t, t_force, global_sig["Cl"])
    out["Q_wall"] = np.interp(t, heat["time"], heat["Q_wall"])
    out["Nu_tube"] = np.interp(t, heat["time"], heat["Nu_tube_wall"])
    return t, out


def plot_global_te(rows: list[TERow]) -> None:
    global_rows = [r for r in rows if r.category == "global"]
    labels = [f"{r.source}->{r.target}" for r in global_rows]
    x = np.arange(len(global_rows))
    fig, ax = plt.subplots(figsize=(12, 5))
    colors = ["#2a9d8f" if r.significant_p95 else "#adb5bd" for r in global_rows]
    ax.bar(x, [r.te_bits for r in global_rows], color=colors, label="TE")
    ax.scatter(x, [r.surrogate_p95_bits for r in global_rows], color="#9b2226", s=24, label="surrogate 95%")
    ax.scatter(x, [r.surrogate_p99_bits for r in global_rows], color="#5f0f40", s=20, marker="x", label="surrogate 99%")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("TE [bits]")
    ax.set_title("Exploratory directional transfer entropy: global signals")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_008_global_transfer_entropy.png", dpi=180)
    plt.close(fig)


def plot_lag_curves(curves: dict[str, list[dict[str, float]]]) -> None:
    selected = [k for k in curves if k in ["Cl->Q_wall", "Q_wall->Cl", "Cl->Q_tube", "Cl->Q_fins"]]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    axes = axes.ravel()
    for ax, key in zip(axes, selected):
        c = curves[key]
        lags = np.asarray([r["lag_s"] for r in c])
        te = np.asarray([r["te_bits"] for r in c])
        p95 = np.asarray([r["surrogate_p95_bits"] for r in c])
        ax.plot(lags, te, marker="o", label="TE")
        ax.plot(lags, p95, ls="--", color="#9b2226", label="surrogate 95%")
        ax.axvline(1.0 / F_SHED, color="0.6", ls=":", lw=1, label="T_shed")
        ax.set_title(key)
        ax.set_ylabel("bits")
        ax.grid(True, alpha=0.25)
    for ax in axes[-2:]:
        ax.set_xlabel("lag [s]")
    axes[0].legend(fontsize=8)
    fig.suptitle("TE lag sensitivity for key global directions")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_008_global_te_lag_sensitivity.png", dpi=180)
    plt.close(fig)


def plot_fin_te(fin_rows: list[dict[str, object]]) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for ax, side in zip(axes, ["fin_z_min", "fin_z_max"]):
        rows = [r for r in fin_rows if r["side"] == side]
        x = np.asarray([float(r["x_mm"]) for r in rows])
        te = np.asarray([float(r["te_bits"]) for r in rows])
        p95 = np.asarray([float(r["surrogate_p95_bits"]) for r in rows])
        sig = np.asarray([bool(r["significant_p95"]) for r in rows])
        ax.plot(x, te, marker="o", label="Cl -> Nu_x TE")
        ax.plot(x, p95, ls="--", color="#9b2226", label="surrogate 95%")
        ax.scatter(x[sig], te[sig], color="#2a9d8f", s=42, zorder=3, label=">95%" if np.any(sig) else None)
        ax.set_ylabel("TE [bits]")
        ax.set_title(side)
        ax.grid(True, alpha=0.25)
    axes[-1].set_xlabel("x [mm]")
    axes[0].legend(fontsize=8)
    fig.suptitle("Reduced fin-bin transfer entropy: Cl -> Nu_local(x)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_008_fin_te_x_profiles.png", dpi=180)
    plt.close(fig)


def plot_modal_te(modal_rows: list[TERow]) -> None:
    signals = sorted({r.target for r in modal_rows if r.source in {"Cl", "Q_wall"}})
    sources = ["Cl", "Q_wall"]
    mat = np.full((len(sources), len(signals)), np.nan)
    sig = np.zeros_like(mat, dtype=bool)
    for i, src in enumerate(sources):
        for j, tgt in enumerate(signals):
            candidates = [r for r in modal_rows if r.source == src and r.target == tgt]
            if candidates:
                mat[i, j] = candidates[0].te_bits - candidates[0].surrogate_p95_bits
                sig[i, j] = candidates[0].significant_p95
    fig, ax = plt.subplots(figsize=(12, 3.6))
    im = ax.imshow(mat, aspect="auto", cmap="coolwarm", vmin=-np.nanmax(np.abs(mat)), vmax=np.nanmax(np.abs(mat)))
    ax.set_xticks(np.arange(len(signals)))
    ax.set_xticklabels(signals, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(sources)))
    ax.set_yticklabels(sources)
    for i in range(len(sources)):
        for j in range(len(signals)):
            if np.isfinite(mat[i, j]):
                ax.text(j, i, "*" if sig[i, j] else "", ha="center", va="center", color="black", fontsize=14)
    ax.set_title("Modal TE excess over surrogate 95% threshold")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("TE - surrogate95 [bits]")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_008_modal_te_heatmap.png", dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    rng = np.random.default_rng(RNG_SEED)

    time, signals = load_global_signals()
    rows: list[TERow] = []
    curves: dict[str, list[dict[str, float]]] = {}

    global_pairs = [
        ("Cl", "Q_wall"),
        ("Q_wall", "Cl"),
        ("Cl", "Q_tube"),
        ("Q_tube", "Cl"),
        ("Cl", "Q_fins"),
        ("Q_fins", "Cl"),
        ("Cl", "Nu_tube"),
        ("Nu_tube", "Cl"),
        ("Cl", "Nu_fins"),
        ("Nu_fins", "Cl"),
        ("Cl", "Nu_EB"),
        ("Nu_EB", "Cl"),
    ]
    for src, tgt in global_pairs:
        row, curve = te_with_surrogates(time, signals[src], signals[tgt], GLOBAL_LAGS_S, N_SURROGATES_GLOBAL, rng)
        rows.append(annotate_row(row, f"{src}->{tgt}", src, tgt, "global"))
        curves[f"{src}->{tgt}"] = curve

    fin_time, fin_groups = reduced_fin_groups()
    fin_rows: list[dict[str, object]] = []
    for label, x_mid, series in fin_groups:
        side = "fin_z_min" if label.startswith("fin_z_min") else "fin_z_max"
        row, _ = te_with_surrogates(fin_time, signals["Cl"], series, FIN_LAGS_S, N_SURROGATES_SPATIAL, rng)
        row = annotate_row(row, f"Cl->{label}", "Cl", label, "fin_x_bin")
        rows.append(row)
        d = asdict(row)
        d["side"] = side
        d["x_m"] = x_mid
        d["x_mm"] = 1000.0 * x_mid
        fin_rows.append(d)

    modal_time, modes = modal_signals()
    modal_rows: list[TERow] = []
    for src in ["Cl", "Q_wall"]:
        for tgt in [k for k in modes if k.startswith("POD_")]:
            lags = np.array([0.02, 0.04, 0.08, 0.16, 0.32])
            row, _ = te_with_surrogates(modal_time, modes[src], modes[tgt], lags, N_SURROGATES_GLOBAL, rng)
            row = annotate_row(row, f"{src}->{tgt}", src, tgt, "modal")
            rows.append(row)
            modal_rows.append(row)
            rev, _ = te_with_surrogates(modal_time, modes[tgt], modes[src], lags, N_SURROGATES_GLOBAL, rng)
            rev = annotate_row(rev, f"{tgt}->{src}", tgt, src, "modal_reverse")
            rows.append(rev)

    write_csv(DATA_DIR / "run008_008_transfer_entropy_global_modal.csv", [asdict(r) for r in rows if r.category in {"global", "modal", "modal_reverse"}])
    write_csv(DATA_DIR / "run008_008_transfer_entropy_fin_xbins.csv", fin_rows)
    lag_rows = []
    for key, curve in curves.items():
        for c in curve:
            row = dict(c)
            row["pair"] = key
            lag_rows.append(row)
    write_csv(DATA_DIR / "run008_008_transfer_entropy_lag_curves.csv", lag_rows)

    plot_global_te(rows)
    plot_lag_curves(curves)
    plot_fin_te(fin_rows)
    plot_modal_te(modal_rows)

    # Compact JSON summary for machine reuse.
    global_summary = [asdict(r) for r in rows if r.category == "global"]
    significant_global = [r for r in global_summary if r["significant_p95"]]
    significant_fin = [r for r in fin_rows if r["significant_p95"]]
    significant_modal = [asdict(r) for r in rows if r.category in {"modal", "modal_reverse"} and r.significant_p95]
    summary = {
        "method": {
            "window_s": WINDOW,
            "n_bins": N_BINS,
            "global_lags_s": GLOBAL_LAGS_S.tolist(),
            "fin_lags_s": FIN_LAGS_S.tolist(),
            "surrogate": "circular shift of source signal; p95/p99 thresholds",
            "n_surrogates_global": N_SURROGATES_GLOBAL,
            "n_surrogates_spatial": N_SURROGATES_SPATIAL,
            "interpretation": "exploratory; highlight only TE above surrogate confidence",
        },
        "global": global_summary,
        "significant_global_p95": significant_global,
        "significant_fin_xbins_p95_count": len(significant_fin),
        "significant_modal_p95": significant_modal,
    }
    (DATA_DIR / "run008_008_transfer_entropy_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    def fmt_sig(items: list[dict[str, object]], limit: int = 12) -> list[str]:
        if not items:
            return ["- none above surrogate 95% threshold"]
        out = []
        for item in items[:limit]:
            out.append(
                f"- `{item['source']} -> {item['target']}`: TE `{float(item['te_bits']):.4f}` bits, "
                f"lag `{float(item['lag_s']):.3f} s`, surrogate95 `{float(item['surrogate_p95_bits']):.4f}`, "
                f"p_emp `{float(item['p_empirical']):.3f}`"
            )
        return out

    fin_sig_by_side = {
        side: sum(1 for r in significant_fin if r["side"] == side)
        for side in ["fin_z_min", "fin_z_max"]
    }
    n_by_side = {
        side: sum(1 for r in fin_rows if r["side"] == side)
        for side in ["fin_z_min", "fin_z_max"]
    }
    strongest_fin = sorted(significant_fin, key=lambda r: float(r["excess_over_p95_bits"]), reverse=True)[:8]

    lines = [
        "# V4b_3D run008 transfer entropy / directionality",
        "",
        "This is an exploratory nonlinear directionality layer. TE uses discretized signals with quantile bins and a circular-shift surrogate test. Results should be treated as support for hypotheses, not as standalone proof of causality.",
        "",
        "## Method",
        "",
        f"- Window: `{WINDOW[0]}..{WINDOW[1]} s`.",
        f"- Sampling for global/fin TE: `{1.0 / np.median(np.diff(time)):.1f} Hz`, `{len(time)}` samples.",
        f"- Discretization: `{N_BINS}` quantile bins.",
        f"- Global lags tested: `{', '.join(f'{x:.3f}' for x in GLOBAL_LAGS_S)} s`.",
        f"- Surrogates: circular source shifts, `{N_SURROGATES_GLOBAL}` for global/modal and `{N_SURROGATES_SPATIAL}` for fin x-bins.",
        "",
        "## Global directional TE",
        "",
        "| Source -> target | lag [s] | TE [bits] | surrogate95 | surrogate99 | p_emp | significant95 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in [x for x in rows if x.category == "global"]:
        lines.append(
            f"| {r.source} -> {r.target} | {r.lag_s:.3f} | {r.te_bits:.4f} | {r.surrogate_p95_bits:.4f} | "
            f"{r.surrogate_p99_bits:.4f} | {r.p_empirical:.3f} | {str(r.significant_p95)} |"
        )
    fin_sig_lines = [
        f"- `{r['target']}` at x=`{float(r['x_mm']):.2f} mm`: TE `{float(r['te_bits']):.4f}` bits, "
        f"lag `{float(r['lag_s']):.3f} s`, surrogate95 `{float(r['surrogate_p95_bits']):.4f}`"
        for r in strongest_fin
    ]
    if not fin_sig_lines:
        fin_sig_lines = ["- none above surrogate 95% threshold"]

    lines.extend(
        [
            "",
            "Significant global directions above surrogate 95%:",
            "",
            *fmt_sig(significant_global),
            "",
            "## Reduced fin-bin TE",
            "",
            f"- z_min significant x-bins: `{fin_sig_by_side['fin_z_min']}/{n_by_side['fin_z_min']}`.",
            f"- z_max significant x-bins: `{fin_sig_by_side['fin_z_max']}/{n_by_side['fin_z_max']}`.",
            "",
            "Strongest fin-bin directions:",
            "",
            *fin_sig_lines,
            "",
            "## Modal TE",
            "",
            "Significant modal directions above surrogate 95%:",
            "",
            *fmt_sig(significant_modal, limit=16),
            "",
            "## Interpretation",
            "",
            "- Treat TE here as a directionality screen. Coherence/cross-phase from layer 007 remain the safer publication-grade evidence.",
            "- A direction is highlighted only when actual TE exceeds the circular-shift surrogate 95% threshold.",
            "- If global heat-transfer TE is weak while coherence is strong, that usually means the coupling is periodic/phase-locked but not strongly nonlinear-directional under this short-record estimator.",
            "",
            "## Figures",
            "",
            "- `../../figures/008/run008_008_global_transfer_entropy.png`",
            "- `../../figures/008/run008_008_global_te_lag_sensitivity.png`",
            "- `../../figures/008/run008_008_fin_te_x_profiles.png`",
            "- `../../figures/008/run008_008_modal_te_heatmap.png`",
        ]
    )
    report = DATA_DIR / "run008_008_transfer_entropy_analysis.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
