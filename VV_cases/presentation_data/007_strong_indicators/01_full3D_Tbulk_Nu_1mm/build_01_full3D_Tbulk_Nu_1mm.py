from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/007_strong_indicators/01_full3D_Tbulk_Nu_1mm"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FULL3D = REPO_DIR / "VV_cases/presentation_data/006_full3D_x_strip_1mm/full3D_x_strip_1mm_merged_with_heat.csv"
HEAT005 = REPO_DIR / "VV_cases/presentation_data/005_x_strip_robustness_analysis/x_strip_enriched_dx1mm.csv"

T_WALL = 343.15
K_AIR = 0.028
D_REF = 0.012
BASELINE_RE = 150.0
SELECTED_RE = [100.0, 150.0, 160.0, 175.0, 200.0]
POST_ONSET_RE = [160.0, 175.0, 200.0]


def lmtd(delta_left: np.ndarray, delta_right: np.ndarray) -> np.ndarray:
    left = np.maximum(delta_left.astype(float), 1.0e-9)
    right = np.maximum(delta_right.astype(float), 1.0e-9)
    out = np.empty_like(left)
    same = np.abs(left - right) < 1.0e-10
    out[same] = 0.5 * (left[same] + right[same])
    ratio = left[~same] / right[~same]
    out[~same] = (left[~same] - right[~same]) / np.log(ratio)
    return out


def add_tube(ax) -> None:
    ax.axvline(-6, color="0.25", ls="--", lw=0.9)
    ax.axvline(6, color="0.25", ls="--", lw=0.9)
    ax.axvspan(-6, 6, color="0.7", alpha=0.08, lw=0)


def load_data() -> pd.DataFrame:
    full = pd.read_csv(FULL3D)
    heat = pd.read_csv(HEAT005)
    full["Re"] = pd.to_numeric(full["Re"], errors="coerce")
    heat["Re"] = pd.to_numeric(heat["Re"], errors="coerce")
    full["x_center_mm"] = pd.to_numeric(full["x_center_mm"], errors="coerce")
    heat["x_center_mm"] = pd.to_numeric(heat["x_center_mm"], errors="coerce")
    full["x_key_mm"] = full["x_center_mm"].round(6)
    heat["x_key_mm"] = heat["x_center_mm"].round(6)
    keep = [
        "Re",
        "x_key_mm",
        "A_total_strip_m2",
        "A_tube_strip_m2",
        "A_fins_strip_m2",
        "Q_total_strip_W",
        "Q_tube_strip_W",
        "Q_fins_strip_W",
        "Nu_strip_proxy",
        "relative_local_sensitivity_vs_Re150",
        "Delta_Nu_vs_Re150",
        "Delta_Q_vs_Re150_W",
        "Q_strip_share_of_total",
        "deltaT_lm_proxy_K",
        "Nu_tube_strip_proxy",
        "Nu_fins_strip_proxy",
    ]
    drop_from_full = [c for c in keep if c not in {"Re", "x_key_mm"} and c in full.columns]
    df = full.drop(columns=drop_from_full).merge(heat[keep], on=["Re", "x_key_mm"], how="left", suffixes=("", "_005"))
    df = df.drop(columns=["x_key_mm"])
    return df.sort_values(["Re", "x_center_mm"]).reset_index(drop=True)


def add_thermal_metrics(df: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for re, sub in df.groupby("Re", sort=True):
        sub = sub.sort_values("x_center_mm").copy()
        x = sub["x_center_mm"].to_numpy()
        tb = sub["T_bulk_3D_Ux_volume_weighted_K"].to_numpy()
        x_left = sub["x_left_mm"].to_numpy()
        x_right = sub["x_right_mm"].to_numpy()
        t_left = np.interp(x_left, x, tb)
        t_right = np.interp(x_right, x, tb)
        dt_center = T_WALL - tb
        dt_lm_3d = lmtd(T_WALL - t_left, T_WALL - t_right)
        area = sub["A_total_strip_m2"].to_numpy()
        area_tube = sub["A_tube_strip_m2"].to_numpy()
        area_fins = sub["A_fins_strip_m2"].to_numpy()
        q = sub["Q_total_strip_W"].to_numpy()
        q_tube = sub["Q_tube_strip_W"].to_numpy()
        q_fins = sub["Q_fins_strip_W"].to_numpy()
        sub["T_bulk_3D_left_interp_K"] = t_left
        sub["T_bulk_3D_right_interp_K"] = t_right
        sub["DeltaT_3D_center_K"] = dt_center
        sub["DeltaT_3D_lmtd_K"] = dt_lm_3d
        sub["Nu_3D_Tbulk_center"] = np.divide(q * D_REF, area * K_AIR * dt_center, out=np.full_like(q, np.nan), where=area > 0)
        sub["Nu_3D_Tbulk_lmtd"] = np.divide(q * D_REF, area * K_AIR * dt_lm_3d, out=np.full_like(q, np.nan), where=area > 0)
        sub["Nu_tube_3D_Tbulk_lmtd"] = np.divide(
            q_tube * D_REF, area_tube * K_AIR * dt_lm_3d, out=np.full_like(q_tube, np.nan), where=area_tube > 0
        )
        sub["Nu_fins_3D_Tbulk_lmtd"] = np.divide(
            q_fins * D_REF, area_fins * K_AIR * dt_lm_3d, out=np.full_like(q_fins, np.nan), where=area_fins > 0
        )
        frames.append(sub)
    out = pd.concat(frames, ignore_index=True)

    base = out[out["Re"].eq(BASELINE_RE)][
        ["x_center_mm", "Nu_3D_Tbulk_lmtd", "Q_total_strip_W", "T_bulk_3D_Ux_volume_weighted_K"]
    ].rename(
        columns={
            "Nu_3D_Tbulk_lmtd": "Nu_3D_Re150",
            "Q_total_strip_W": "Q_Re150",
            "T_bulk_3D_Ux_volume_weighted_K": "Tbulk_3D_Re150",
        }
    )
    out = out.merge(base, on="x_center_mm", how="left")
    mean_nu = out.groupby("Re")["Nu_3D_Tbulk_lmtd"].mean()
    mean_gain = {re: mean_nu.loc[re] / mean_nu.loc[BASELINE_RE] for re in mean_nu.index}
    out["Delta_Nu_3D_lmtd_vs_Re150"] = out["Nu_3D_Tbulk_lmtd"] - out["Nu_3D_Re150"]
    out["Delta_Q_vs_Re150_W_confirmed"] = out["Q_total_strip_W"] - out["Q_Re150"]
    out["Delta_Tbulk_3D_vs_Re150_K"] = out["T_bulk_3D_Ux_volume_weighted_K"] - out["Tbulk_3D_Re150"]
    out["relative_local_sensitivity_3D_Nu_vs_Re150"] = [
        (row.Nu_3D_Tbulk_lmtd / row.Nu_3D_Re150) / mean_gain[row.Re] - 1.0
        if row.Re in mean_gain and np.isfinite(row.Nu_3D_Re150) and row.Nu_3D_Re150 != 0
        else np.nan
        for row in out.itertuples()
    ]
    out["Nu_3D_minus_previous_proxy"] = out["Nu_3D_Tbulk_lmtd"] - out["Nu_strip_proxy"]
    out["Nu_3D_over_previous_proxy"] = out["Nu_3D_Tbulk_lmtd"] / out["Nu_strip_proxy"]
    return out


def save_summary(df: pd.DataFrame) -> None:
    rows = []
    for re, sub in df.groupby("Re"):
        valid = sub[np.isfinite(sub["Nu_3D_Tbulk_lmtd"])]
        rows.append(
            {
                "Re": re,
                "n_strips_with_Nu": len(valid),
                "Nu_3D_mean": valid["Nu_3D_Tbulk_lmtd"].mean(),
                "Nu_3D_min": valid["Nu_3D_Tbulk_lmtd"].min(),
                "Nu_3D_max": valid["Nu_3D_Tbulk_lmtd"].max(),
                "Tbulk_3D_inlet_side_K": sub["T_bulk_3D_Ux_volume_weighted_K"].iloc[0],
                "Tbulk_3D_outlet_side_K": sub["T_bulk_3D_Ux_volume_weighted_K"].iloc[-1],
                "Q_total_W": sub["Q_total_strip_W"].sum(),
                "peak_relative_sensitivity_x_mm": valid.loc[valid["relative_local_sensitivity_3D_Nu_vs_Re150"].idxmax(), "x_center_mm"]
                if re != BASELINE_RE and valid["relative_local_sensitivity_3D_Nu_vs_Re150"].notna().any()
                else np.nan,
                "peak_relative_sensitivity_3D": valid["relative_local_sensitivity_3D_Nu_vs_Re150"].max(),
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "stage01_summary_global_indicators.csv", index=False)


def plot_tbulk(df: pd.DataFrame) -> None:
    colors = plt.get_cmap("viridis")
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 7.0), sharex=True)
    for i, re in enumerate(SELECTED_RE):
        sub = df[df["Re"].eq(re)]
        c = colors(i / max(1, len(SELECTED_RE) - 1))
        axes[0].plot(sub["x_center_mm"], sub["T_bulk_3D_Ux_volume_weighted_K"], lw=1.9, color=c, label=f"Re {int(re)}")
        axes[1].plot(sub["x_center_mm"], sub["DeltaT_3D_lmtd_K"], lw=1.9, color=c, label=f"Re {int(re)}")
    axes[0].set_ylabel("3D T_bulk proxy [K]")
    axes[1].set_ylabel("3D DeltaT_lmtd [K]")
    axes[1].set_xlabel("x from tube center [mm], 1 mm strips")
    for ax in axes:
        add_tube(ax)
        ax.grid(True, alpha=0.25)
    axes[0].legend(frameon=False, ncols=5)
    fig.suptitle("Stage 01: 3D bulk-temperature basis for local Nu", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig01_Tbulk3D_and_DeltaT_profiles.png", dpi=240)
    fig.savefig(OUT_DIR / "fig01_Tbulk3D_and_DeltaT_profiles.pdf")
    plt.close(fig)


def plot_nu_profiles(df: pd.DataFrame) -> None:
    colors = {100.0: "0.45", 150.0: "0.1", 160.0: "#31588a", 175.0: "#b35806", 200.0: "#8b1a1a"}
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.4), sharex=True)
    configs = [
        ("Nu_3D_Tbulk_lmtd", "Nu from 3D Tbulk LMTD [-]", "Main local Nu using 3D Tbulk"),
        ("Nu_strip_proxy", "previous Nu proxy [-]", "Previous local Nu proxy"),
        ("Nu_3D_minus_previous_proxy", "Nu_3D - Nu_previous [-]", "Difference caused by Tbulk definition"),
        ("Nu_3D_over_previous_proxy", "Nu_3D / Nu_previous [-]", "Ratio to previous proxy"),
    ]
    for ax, (col, ylabel, title) in zip(axes.ravel(), configs):
        for re in SELECTED_RE:
            sub = df[df["Re"].eq(re)]
            ax.plot(sub["x_center_mm"], sub[col], lw=1.8, color=colors[re], label=f"Re {int(re)}")
        if "minus" in col:
            ax.axhline(0, color="0.2", lw=0.8)
        if "over" in col:
            ax.axhline(1, color="0.2", lw=0.8)
        add_tube(ax)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
    axes[0, 0].legend(frameon=False, ncols=5)
    axes[1, 0].set_xlabel("x from tube center [mm]")
    axes[1, 1].set_xlabel("x from tube center [mm]")
    fig.suptitle("Stage 01: local Nu robustness to 3D Tbulk definition", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig02_Nu3D_profiles_and_proxy_comparison.png", dpi=240)
    fig.savefig(OUT_DIR / "fig02_Nu3D_profiles_and_proxy_comparison.pdf")
    plt.close(fig)


def plot_sensitivity(df: pd.DataFrame) -> None:
    colors = {160.0: "#31588a", 175.0: "#b35806", 200.0: "#8b1a1a"}
    fig, axes = plt.subplots(3, 1, figsize=(11.5, 9.0), sharex=True)
    metrics = [
        ("Delta_Nu_3D_lmtd_vs_Re150", "Delta Nu_3D vs Re150 [-]", "Absolute local Nu change"),
        ("Delta_Q_vs_Re150_W_confirmed", "Delta Q vs Re150 [W]", "Absolute local heat-transfer change"),
        ("relative_local_sensitivity_3D_Nu_vs_Re150", "relative sensitivity [-]", "Relative local sensitivity using 3D Nu"),
    ]
    for ax, (col, ylabel, title) in zip(axes, metrics):
        for re in POST_ONSET_RE:
            sub = df[df["Re"].eq(re)]
            ax.plot(sub["x_center_mm"], sub[col], lw=2.0, color=colors[re], label=f"Re {int(re)}")
        ax.axhline(0, color="0.2", lw=0.8)
        add_tube(ax)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
    axes[0].legend(frameon=False, ncols=3)
    axes[-1].set_xlabel("x from tube center [mm], 1 mm strips")
    fig.suptitle("Stage 01: thermal dependent variable for later coherence/EPOD", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig03_DeltaNu_DeltaQ_relative_sensitivity_3D.png", dpi=240)
    fig.savefig(OUT_DIR / "fig03_DeltaNu_DeltaQ_relative_sensitivity_3D.pdf")
    plt.close(fig)


def plot_tube_fins(df: pd.DataFrame) -> None:
    colors = {160.0: "#31588a", 175.0: "#b35806", 200.0: "#8b1a1a"}
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.4), sharex=True)
    configs = [
        ("Nu_tube_3D_Tbulk_lmtd", "Nu tube, 3D Tbulk [-]", "Tube-only Nu with 3D Tbulk"),
        ("Nu_fins_3D_Tbulk_lmtd", "Nu fins, 3D Tbulk [-]", "Fins-only Nu with 3D Tbulk"),
        ("Q_tube_strip_W", "Q tube strip [W]", "Tube heat transfer"),
        ("Q_fins_strip_W", "Q fins strip [W]", "Fins heat transfer"),
    ]
    for ax, (col, ylabel, title) in zip(axes.ravel(), configs):
        for re in POST_ONSET_RE:
            sub = df[df["Re"].eq(re)]
            ax.plot(sub["x_center_mm"], sub[col], lw=2.0, color=colors[re], label=f"Re {int(re)}")
        add_tube(ax)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
    axes[0, 0].legend(frameon=False, ncols=3)
    axes[1, 0].set_xlabel("x from tube center [mm]")
    axes[1, 1].set_xlabel("x from tube center [mm]")
    fig.suptitle("Stage 01: tube/fins separation with 3D Tbulk Nu", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig04_tube_fins_Nu3D_and_Q_profiles.png", dpi=240)
    fig.savefig(OUT_DIR / "fig04_tube_fins_Nu3D_and_Q_profiles.pdf")
    plt.close(fig)


def write_readme() -> None:
    text = """# 01_full3D_Tbulk_Nu_1mm

Stage 01 builds a stronger local thermal dependent variable for later coherence and EPOD analysis.

Inputs:

- `../../006_full3D_x_strip_1mm/full3D_x_strip_1mm_merged_with_heat.csv`
- `../../005_x_strip_robustness_analysis/x_strip_enriched_dx1mm.csv`

Main definition:

`Nu_3D_Tbulk_lmtd = Q_strip * D / (A_strip * k * DeltaT_3D_lmtd)`

where `Q_strip` and `A_strip` come from full hot tube/fins wall surfaces, while `DeltaT_3D_lmtd` is estimated from the full-3D convective bulk-temperature proxy in each 1 mm x-strip.

Important limitation:

This is stronger than the earlier midspan/LMTD proxy, but it is still based on a 3D strip-wise bulk-temperature proxy. Exact publication-grade `T_bulk(x,t)` should later be computed on y-z cutting planes.

Outputs:

- `stage01_full3D_Tbulk_Nu_1mm.csv`
- `stage01_summary_global_indicators.csv`
- `fig01_Tbulk3D_and_DeltaT_profiles`
- `fig02_Nu3D_profiles_and_proxy_comparison`
- `fig03_DeltaNu_DeltaQ_relative_sensitivity_3D`
- `fig04_tube_fins_Nu3D_and_Q_profiles`
"""
    (OUT_DIR / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    df = add_thermal_metrics(load_data())
    df.to_csv(OUT_DIR / "stage01_full3D_Tbulk_Nu_1mm.csv", index=False)
    save_summary(df)
    plot_tbulk(df)
    plot_nu_profiles(df)
    plot_sensitivity(df)
    plot_tube_fins(df)
    write_readme()
    print(f"Done: {OUT_DIR}")


if __name__ == "__main__":
    main()
