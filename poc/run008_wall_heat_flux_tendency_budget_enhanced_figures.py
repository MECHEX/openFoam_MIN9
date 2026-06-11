from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent / "run008_wall_heat_flux_tendency_budget"
FIG_DIR = ROOT / "figures"

REGION_LABELS = {
    "tube_rear": "tube rear",
    "tube_separation": "tube separation",
    "tube_junction": "tube-fin junction",
    "fin_sweep": "fin sweep",
    "fin_near_tube": "fin near tube",
    "fin_control": "fin control",
}

REGION_COLORS = {
    "tube_rear": "#a63d40",
    "tube_separation": "#d77a61",
    "tube_junction": "#7f4f8b",
    "fin_sweep": "#2f6f73",
    "fin_near_tube": "#5b8e7d",
    "fin_control": "#64748b",
}

TUBE_REGIONS = ["tube_rear", "tube_separation", "tube_junction"]
FIN_REGIONS = ["fin_sweep", "fin_near_tube", "fin_control"]
STORY_REGIONS = ["tube_rear", "tube_junction", "fin_sweep"]


def label(region: str) -> str:
    return REGION_LABELS.get(region, region.replace("_", " "))


def zscore(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    sigma = np.nanstd(values)
    if not np.isfinite(sigma) or sigma == 0:
        return np.zeros_like(values)
    return (values - np.nanmean(values)) / sigma


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary = pd.read_csv(ROOT / "run008_budget_region_summary.csv")
    phase = pd.read_csv(ROOT / "run008_budget_region_phase_average.csv")
    time = pd.read_csv(ROOT / "run008_budget_region_timeseries.csv")
    faces = pd.read_csv(ROOT / "run008_budget_face_catalog.csv")
    return summary, phase, time, faces


def plot_region_layout(faces: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6), constrained_layout=True)

    ax = axes[0]
    for region in TUBE_REGIONS:
        g = faces[faces["region"] == region]
        ax.scatter(g["x"] * 1000, g["y"] * 1000, s=3, color=REGION_COLORS[region], alpha=0.45, label=label(region))
    theta = np.linspace(0, 2 * np.pi, 300)
    ax.plot(6 * np.cos(theta), 6 * np.sin(theta), color="0.15", lw=1.0)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x relative to tube centre [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title("A. Tube wall regions")
    ax.legend(frameon=False, markerscale=4, loc="upper right", fontsize=8)

    ax = axes[1]
    for region in FIN_REGIONS:
        g = faces[faces["region"] == region]
        ax.scatter(g["x"] * 1000, g["y"] * 1000, s=3, color=REGION_COLORS[region], alpha=0.38, label=label(region))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x relative to tube centre [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title("B. Fin wall regions, projected onto x-y")
    ax.legend(frameon=False, markerscale=4, loc="upper right", fontsize=8)

    fig.suptitle("Where the PoC budget is sampled", y=1.03)
    fig.savefig(FIG_DIR / "run008_budget_region_layout.png", dpi=220)
    plt.close(fig)


def plot_attribution_dashboard(summary: pd.DataFrame) -> None:
    ordered = summary.sort_values("p_q_rms_wm2s", ascending=True).reset_index(drop=True)
    regions = ordered["region"].to_list()
    y = np.arange(len(ordered))

    adv_ratio = ordered["p_adv_rms_wm2s"] / ordered["p_q_rms_wm2s"]
    diff_ratio = ordered["p_diff_rms_wm2s"] / ordered["p_q_rms_wm2s"]
    cancellation = 1.0 - ordered["p_q_rms_wm2s"] / (ordered["p_adv_rms_wm2s"] + ordered["p_diff_rms_wm2s"])
    cancellation = cancellation.clip(lower=0.0, upper=1.0)

    fig, axes = plt.subplots(1, 3, figsize=(13.6, 5.6), constrained_layout=True, sharey=True)

    ax = axes[0]
    ax.barh(y, ordered["p_q_rms_wm2s"], color=[REGION_COLORS[r] for r in regions])
    ax.set_yticks(y)
    ax.set_yticklabels([label(r) for r in regions])
    ax.set_xlabel("RMS(P_q) [W m$^{-2}$ s$^{-1}$]")
    ax.set_title("A. Where q'' changes fastest")

    ax = axes[1]
    ax.barh(y - 0.18, adv_ratio, height=0.34, color="#1f77b4", label="RMS(P_adv)/RMS(P_q)")
    ax.barh(y + 0.18, diff_ratio, height=0.34, color="#d62728", label="RMS(P_diff)/RMS(P_q)")
    ax.axvline(1.0, color="0.25", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("term strength relative to P_q")
    ax.set_title("B. How large each term is")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[2]
    ax.barh(y - 0.24, ordered["corr_pq_padv"], height=0.22, color="#1f77b4", label="corr(P_q,P_adv)")
    ax.barh(y, ordered["corr_pq_pdiff"], height=0.22, color="#d62728", label="corr(P_q,P_diff)")
    ax.barh(y + 0.24, cancellation, height=0.22, color="#6b7280", label="cancellation index")
    ax.axvline(0.0, color="0.25", lw=0.8)
    ax.axvline(1.0, color="0.25", lw=0.8, ls=":")
    ax.set_xlim(-1.0, 1.05)
    ax.set_xlabel("correlation / cancellation")
    ax.set_title("C. Which term actually tracks P_q")
    ax.legend(frameon=False, fontsize=8, loc="lower right")

    fig.suptitle("Wall-heat-flux tendency budget: strength, tracking, and cancellation", y=1.03)
    fig.savefig(FIG_DIR / "run008_budget_attribution_dashboard.png", dpi=220)
    plt.close(fig)


def plot_phase_fingerprint(phase: pd.DataFrame) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(9.0, 9.6), sharex=True, constrained_layout=True)

    for ax, region in zip(axes, STORY_REGIONS):
        g = phase[phase["region"] == region].sort_values("phase_center_deg")
        pq = zscore(g["p_q_direct_wm2s"].to_numpy())
        padv = zscore(g["p_adv_wm2s"].to_numpy())
        pdiff = zscore(g["p_diff_wm2s"].to_numpy())
        ax.plot(g["phase_center_deg"], pq, color="0.1", lw=2.2, label="P_q direct")
        ax.plot(g["phase_center_deg"], padv, color="#1f77b4", lw=1.8, label="P_adv estimate")
        ax.plot(g["phase_center_deg"], pdiff, color="#d62728", lw=1.8, label="P_diff estimate")
        ax.axhline(0, color="0.4", lw=0.8)
        ax.set_ylabel("phase z-score")
        ax.set_title(label(region))
    axes[-1].set_xlabel("Cl phase [deg]")
    axes[0].legend(frameon=False, ncol=3, loc="upper right")
    fig.suptitle("Phase fingerprint after normalisation: same cycle, different local budgets", y=1.02)
    fig.savefig(FIG_DIR / "run008_budget_phase_fingerprint.png", dpi=220)
    plt.close(fig)


def plot_term_tracking_scatter(time: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(13.0, 8.2), constrained_layout=True)

    for col, region in enumerate(STORY_REGIONS):
        g = time[time["region"] == region]
        pq = g["p_q_direct_wm2s"].to_numpy()
        padv = g["p_adv_wm2s"].to_numpy()
        pdiff = g["p_diff_wm2s"].to_numpy()
        pq_anom = pq - np.nanmean(pq)
        padv_anom = padv - np.nanmean(padv)
        pdiff_anom = pdiff - np.nanmean(pdiff)
        phase = g["phase_deg"].to_numpy()

        ax = axes[0, col]
        ax.scatter(padv_anom, pq_anom, c=phase, s=24, cmap="twilight", alpha=0.86, edgecolors="none")
        r = np.corrcoef(padv, pq)[0, 1]
        ax.axhline(0, color="0.35", lw=0.7)
        ax.axvline(0, color="0.35", lw=0.7)
        set_symmetric_limits(ax, padv_anom, pq_anom)
        ax.set_title(f"{label(region)}\nP_adv anomaly vs P_q anomaly, r={r:+.2f}", fontsize=10)
        ax.set_xlabel("P_adv anomaly [W m$^{-2}$ s$^{-1}$]")

        ax = axes[1, col]
        sc = ax.scatter(pdiff_anom, pq_anom, c=phase, s=24, cmap="twilight", alpha=0.86, edgecolors="none")
        r = np.corrcoef(pdiff, pq)[0, 1]
        ax.axhline(0, color="0.35", lw=0.7)
        ax.axvline(0, color="0.35", lw=0.7)
        set_symmetric_limits(ax, pdiff_anom, pq_anom)
        ax.set_title(f"P_diff anomaly vs P_q anomaly, r={r:+.2f}", fontsize=10)
        ax.set_xlabel("P_diff anomaly [W m$^{-2}$ s$^{-1}$]")

    axes[0, 0].set_ylabel("P_q direct [W m$^{-2}$ s$^{-1}$]")
    axes[1, 0].set_ylabel("P_q direct [W m$^{-2}$ s$^{-1}$]")
    cbar = fig.colorbar(sc, ax=axes.ravel().tolist(), shrink=0.85, pad=0.012)
    cbar.set_label("Cl phase [deg]")
    fig.suptitle("Term tracking test: which estimated term follows the direct wall-flux tendency?", y=1.02)
    fig.savefig(FIG_DIR / "run008_budget_term_tracking_scatter.png", dpi=220)
    plt.close(fig)


def set_symmetric_limits(ax: plt.Axes, x: np.ndarray, y: np.ndarray) -> None:
    xlim = np.nanpercentile(np.abs(x), 98) * 1.15
    ylim = np.nanpercentile(np.abs(y), 98) * 1.15
    if np.isfinite(xlim) and xlim > 0:
        ax.set_xlim(-xlim, xlim)
    if np.isfinite(ylim) and ylim > 0:
        ax.set_ylim(-ylim, ylim)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    summary, phase, time, faces = load_data()
    plot_region_layout(faces)
    plot_attribution_dashboard(summary)
    plot_phase_fingerprint(phase)
    plot_term_tracking_scatter(time)
    print("Wrote enhanced budget figures:")
    for name in [
        "run008_budget_region_layout.png",
        "run008_budget_attribution_dashboard.png",
        "run008_budget_phase_fingerprint.png",
        "run008_budget_term_tracking_scatter.png",
    ]:
        print(FIG_DIR / name)


if __name__ == "__main__":
    main()
