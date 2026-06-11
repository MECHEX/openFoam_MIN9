from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/007_strong_indicators/03_EPOD_velocity_to_Nu"
NU_FILE = REPO_DIR / "VV_cases/presentation_data/007_strong_indicators/00_fullNu3D_xt/fullNu3D_xt_time_resolved.csv"
SOURCE_002 = REPO_DIR / "VV_cases/presentation_data/002_Nu_and_vorticity"
sys.path.insert(0, str(SOURCE_002))
from build_stripwise_heat_figures import read_vtk_polydata  # noqa: E402


OUT_DIR.mkdir(parents=True, exist_ok=True)

CASES = [
    {"Re": 100.0, "case": "run012_re100", "path": Path("/home/hexmachina/of_runs/V4b_3D_run012_re100_production"), "regime": "steady"},
    {"Re": 150.0, "case": "run013_re150", "path": Path("/home/hexmachina/of_runs/V4b_3D_run013_re150_production"), "regime": "steady"},
    {"Re": 160.0, "case": "run015_re160", "path": Path("/home/hexmachina/of_runs/V4b_3D_run015_re160_production"), "regime": "shedding"},
    {"Re": 175.0, "case": "run014_re175", "path": Path("/home/hexmachina/of_runs/V4b_3D_run014_re175_production"), "regime": "shedding"},
    {"Re": 200.0, "case": "run008_re200", "path": Path("/home/hexmachina/of_runs/V4b_3D_run008"), "regime": "production shedding"},
]

N_MODES = 6
SELECTED_X_MM = [-5.5, 0.5, 5.5, 10.5]


def safe_float_name(t: float) -> str:
    return f"{t:g}"


def read_velocity_snapshot(case_dir: Path, time_s: float) -> tuple[np.ndarray, np.ndarray]:
    f = case_dir / "postProcessing/midspan_z0" / safe_float_name(time_s) / "z0.vtk"
    if not f.exists():
        raise FileNotFoundError(f)
    points, _, fields = read_vtk_polydata(f)
    u = fields["U"][:, :2]
    return points[:, :2], u


def velocity_matrix(case: dict, times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    coords_ref = None
    rows = []
    for t in times:
        coords, u = read_velocity_snapshot(case["path"], float(t))
        if coords_ref is None:
            coords_ref = coords
        elif coords.shape != coords_ref.shape or not np.allclose(coords, coords_ref, atol=1.0e-12):
            raise RuntimeError(f"Midspan mesh changed for {case['case']} at t={t:g}")
        rows.append(u.reshape(-1))
    return np.vstack(rows), coords_ref


def pod_from_snapshots(x: np.ndarray) -> dict[str, np.ndarray]:
    x_fluc = x - x.mean(axis=0, keepdims=True)
    # Snapshot POD through economy SVD. Rows are time snapshots.
    u_time, singular, vt = np.linalg.svd(x_fluc, full_matrices=False)
    eig = singular**2 / max(1, x.shape[0] - 1)
    energy = eig / eig.sum() if eig.sum() > 0 else np.full_like(eig, np.nan)
    coeff = u_time * singular
    return {"x_fluc": x_fluc, "singular": singular, "energy": energy, "coeff": coeff, "modes": vt}


def standardized(a: np.ndarray) -> np.ndarray:
    std = a.std(axis=0, ddof=1)
    return (a - a.mean(axis=0)) / np.where(std > 0, std, np.nan)


def regression_r2(a: np.ndarray, y: np.ndarray, n_modes: int) -> np.ndarray:
    x = np.column_stack([np.ones(len(a)), a[:, :n_modes]])
    out = []
    for j in range(y.shape[1]):
        yy = y[:, j]
        mask = np.isfinite(yy) & np.all(np.isfinite(x), axis=1)
        if mask.sum() <= n_modes + 1 or np.std(yy[mask]) <= 0:
            out.append(np.nan)
            continue
        beta, *_ = np.linalg.lstsq(x[mask], yy[mask], rcond=None)
        pred = x[mask] @ beta
        ss_res = float(np.sum((yy[mask] - pred) ** 2))
        ss_tot = float(np.sum((yy[mask] - yy[mask].mean()) ** 2))
        out.append(1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan)
    return np.asarray(out)


def analyse_case(case: dict, nu_all: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    nu = nu_all[np.isclose(nu_all["Re"], case["Re"])].copy()
    times = np.asarray(sorted(nu["time_s"].unique()), dtype=float)
    x_positions = np.asarray(sorted(nu["x_center_mm"].unique()), dtype=float)
    xvel, coords = velocity_matrix(case, times)
    pod = pod_from_snapshots(xvel)
    coeff = pod["coeff"][:, :N_MODES]
    coeff_z = standardized(coeff)

    y = (
        nu.pivot_table(index="time_s", columns="x_center_mm", values="Nu_3D_xt")
        .reindex(index=times, columns=x_positions)
        .to_numpy()
    )
    y_z = standardized(y)

    corr = np.full((N_MODES, len(x_positions)), np.nan)
    cov = np.full_like(corr, np.nan)
    for k in range(N_MODES):
        for j in range(len(x_positions)):
            if np.isfinite(y_z[:, j]).all() and np.std(y[:, j]) > 0 and np.std(coeff[:, k]) > 0:
                corr[k, j] = float(np.corrcoef(coeff[:, k], y[:, j])[0, 1])
                cov[k, j] = float(np.mean((coeff[:, k] - coeff[:, k].mean()) * (y[:, j] - y[:, j].mean())))
    r2 = regression_r2(coeff_z, y_z, min(3, N_MODES))

    energy_rows = []
    for k in range(min(N_MODES, len(pod["energy"]))):
        energy_rows.append(
            {
                "Re": case["Re"],
                "case": case["case"],
                "regime": case["regime"],
                "mode": k + 1,
                "energy_fraction": float(pod["energy"][k]),
                "cumulative_energy": float(np.nansum(pod["energy"][: k + 1])),
                "singular_value": float(pod["singular"][k]),
            }
        )

    corr_rows = []
    for k in range(N_MODES):
        for j, x_mm in enumerate(x_positions):
            corr_rows.append(
                {
                    "Re": case["Re"],
                    "case": case["case"],
                    "regime": case["regime"],
                    "mode": k + 1,
                    "x_center_mm": x_mm,
                    "corr_mode_coeff_vs_Nu": corr[k, j],
                    "cov_mode_coeff_vs_Nu": cov[k, j],
                    "abs_corr": abs(corr[k, j]) if np.isfinite(corr[k, j]) else np.nan,
                    "R2_Nu_from_first3_velocity_modes": r2[j],
                }
            )

    temporal_rows = []
    selected_cols = [float(x) for x in SELECTED_X_MM if np.any(np.isclose(x_positions, x))]
    for i, t in enumerate(times):
        row = {"Re": case["Re"], "case": case["case"], "regime": case["regime"], "time_s": t}
        for k in range(N_MODES):
            row[f"a{k+1}_velocity_POD"] = coeff[i, k]
            row[f"a{k+1}_velocity_POD_z"] = coeff_z[i, k]
        for x_mm in selected_cols:
            j = int(np.where(np.isclose(x_positions, x_mm))[0][0])
            row[f"Nu_x{x_mm:g}_mm"] = y[i, j]
            row[f"Nu_x{x_mm:g}_mm_z"] = y_z[i, j]
        temporal_rows.append(row)

    plot_case(case, x_positions, pod, corr, r2, times, coeff_z, y_z)
    return pd.DataFrame(energy_rows), pd.DataFrame(corr_rows), pd.DataFrame(temporal_rows)


def plot_case(case: dict, x_positions: np.ndarray, pod: dict[str, np.ndarray], corr: np.ndarray, r2: np.ndarray, times: np.ndarray, coeff_z: np.ndarray, y_z: np.ndarray) -> None:
    re = int(case["Re"])
    fig, ax = plt.subplots(figsize=(7.6, 4.5))
    energy = pod["energy"][:N_MODES]
    ax.bar(np.arange(1, len(energy) + 1), energy, color="#4477aa")
    ax.plot(np.arange(1, len(energy) + 1), np.cumsum(energy), marker="o", color="#cc6677", label="cumulative")
    ax.set_xlabel("velocity POD mode")
    ax.set_ylabel("energy fraction")
    ax.set_title(f"Midspan velocity POD energy, Re {re}")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"fig01_velocity_POD_energy_Re{re}.png", dpi=240)
    fig.savefig(OUT_DIR / f"fig01_velocity_POD_energy_Re{re}.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.0, 4.8))
    im = ax.imshow(
        corr,
        aspect="auto",
        origin="lower",
        extent=[x_positions.min(), x_positions.max(), 1, N_MODES],
        vmin=-1,
        vmax=1,
        cmap="coolwarm",
    )
    ax.axvline(-6, color="0.2", ls="--", lw=0.8)
    ax.axvline(6, color="0.2", ls="--", lw=0.8)
    ax.set_xlabel("x position [mm]")
    ax.set_ylabel("velocity POD mode")
    ax.set_title(f"EPOD map: corr(velocity POD coefficient, local Nu_3D), Re {re}")
    fig.colorbar(im, ax=ax, label="correlation")
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"fig02_EPOD_corr_map_Re{re}.png", dpi=240)
    fig.savefig(OUT_DIR / f"fig02_EPOD_corr_map_Re{re}.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.plot(x_positions, r2, marker="o", lw=2.0, color="#228833")
    ax.axvline(-6, color="0.35", ls="--", lw=0.8)
    ax.axvline(6, color="0.35", ls="--", lw=0.8)
    ax.set_xlabel("x position [mm]")
    ax.set_ylabel("R2")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(f"How much local Nu_3D is explained by first 3 velocity POD modes, Re {re}")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"fig03_R2_Nu_from_velocity_modes_Re{re}.png", dpi=240)
    fig.savefig(OUT_DIR / f"fig03_R2_Nu_from_velocity_modes_Re{re}.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(len(SELECTED_X_MM), 1, figsize=(10.0, 8.5), sharex=True)
    for ax, x_mm in zip(axes, SELECTED_X_MM):
        if not np.any(np.isclose(x_positions, x_mm)):
            continue
        j = int(np.where(np.isclose(x_positions, x_mm))[0][0])
        ax.plot(times, coeff_z[:, 0], color="0.2", lw=1.5, label="velocity POD a1")
        ax.plot(times, y_z[:, j], color="#d55e00", lw=1.5, label=f"Nu z-score x={x_mm:g} mm")
        ax.set_ylabel(f"x={x_mm:g}")
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=2)
    axes[-1].set_xlabel("time [s]")
    fig.suptitle(f"Leading velocity POD coefficient vs selected local Nu_3D, Re {re}")
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"fig04_a1_vs_selected_Nu_Re{re}.png", dpi=240)
    fig.savefig(OUT_DIR / f"fig04_a1_vs_selected_Nu_Re{re}.pdf")
    plt.close(fig)


def write_readme(energy: pd.DataFrame, corr: pd.DataFrame) -> None:
    top = corr.sort_values("abs_corr", ascending=False).head(8)
    text = f"""# 03_EPOD_velocity_to_Nu

This stage links midspan velocity structures to the full-surface local heat-transfer response.

Definition:

- Velocity side: POD of `U_x, U_y` fluctuations on the existing `midspan_z0` sampled plane.
- Thermal side: full `Nu_3D(x,t)` from stage `00_fullNu3D_xt`.
- EPOD indicator: correlation/covariance between each velocity POD temporal coefficient and each local `Nu_3D(x,t)` strip.
- Additional scalar: `R2_Nu_from_first3_velocity_modes`, the fraction of local Nu fluctuation variance explained by the first three velocity POD coefficients.

Important limitation:

This is not a full-volume 3D velocity POD. It uses the midspan plane because those data are already available at all matching full-field times. Treat it as a mechanistic indicator: which coherent velocity modes appear to drive or mirror local air-side heat-transfer response.

Outputs:

- `stage03_velocity_POD_energy.csv`
- `stage03_EPOD_mode_Nu_correlations.csv`
- `stage03_temporal_coefficients_and_selected_Nu.csv`
- `fig01_velocity_POD_energy_Re*`
- `fig02_EPOD_corr_map_Re*`
- `fig03_R2_Nu_from_velocity_modes_Re*`
- `fig04_a1_vs_selected_Nu_Re*`

Strongest mode-Nu links found:

```text
{top[["Re", "mode", "x_center_mm", "corr_mode_coeff_vs_Nu", "R2_Nu_from_first3_velocity_modes"]].to_string(index=False)}
```
"""
    (OUT_DIR / "README.md").write_text(text, encoding="utf-8")


def plot_comparative_figures(energy: pd.DataFrame, corr: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11.0, 7.2), sharex=True)
    mode1 = corr[corr["mode"] == 1].copy()
    for re, sub in mode1.groupby("Re"):
        label = f"Re {re:g}"
        lw = 2.2 if re >= 160 else 1.6
        alpha = 1.0 if re >= 160 else 0.65
        axes[0].plot(sub["x_center_mm"], sub["corr_mode_coeff_vs_Nu"], marker="o", lw=lw, alpha=alpha, label=label)
        axes[1].plot(sub["x_center_mm"], sub["abs_corr"], marker="o", lw=lw, alpha=alpha, label=label)
    for ax in axes:
        ax.axvline(-6, color="0.35", ls="--", lw=0.8)
        ax.axvline(6, color="0.35", ls="--", lw=0.8)
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=5)
    axes[0].axhline(0, color="0.25", lw=0.8)
    axes[0].set_ylabel("corr(a1 velocity POD, Nu_3D)")
    axes[1].set_ylabel("|corr|")
    axes[1].set_xlabel("x position [mm]")
    axes[0].set_title("EPOD comparison: leading velocity mode to local Nu, steady vs shedding")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig05_comparison_mode1_EPOD_corr_steady_vs_shedding.png", dpi=240)
    fig.savefig(OUT_DIR / "fig05_comparison_mode1_EPOD_corr_steady_vs_shedding.pdf")
    plt.close(fig)

    r2 = corr[["Re", "x_center_mm", "R2_Nu_from_first3_velocity_modes"]].drop_duplicates()
    fig, ax = plt.subplots(figsize=(11.0, 4.8))
    for re, sub in r2.groupby("Re"):
        lw = 2.2 if re >= 160 else 1.6
        alpha = 1.0 if re >= 160 else 0.65
        ax.plot(sub["x_center_mm"], sub["R2_Nu_from_first3_velocity_modes"], marker="o", lw=lw, alpha=alpha, label=f"Re {re:g}")
    ax.axvline(-6, color="0.35", ls="--", lw=0.8)
    ax.axvline(6, color="0.35", ls="--", lw=0.8)
    ax.set_xlabel("x position [mm]")
    ax.set_ylabel("R2 from first 3 velocity modes")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("EPOD comparison: local Nu explained by first 3 velocity modes")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, ncol=5)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig06_comparison_R2_steady_vs_shedding.png", dpi=240)
    fig.savefig(OUT_DIR / "fig06_comparison_R2_steady_vs_shedding.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    pivot = energy[energy["mode"].isin([1, 2, 3])].pivot(index="Re", columns="mode", values="energy_fraction")
    bottom = np.zeros(len(pivot))
    colors = ["#4477aa", "#66ccee", "#228833"]
    for mode, color in zip([1, 2, 3], colors):
        vals = pivot[mode].to_numpy()
        ax.bar(pivot.index.astype(str), vals, bottom=bottom, label=f"mode {mode}", color=color)
        bottom += vals
    ax.set_xlabel("Re")
    ax.set_ylabel("velocity POD energy fraction")
    ax.set_title("Velocity POD energy concentration: steady vs shedding")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig07_comparison_POD_energy_steady_vs_shedding.png", dpi=240)
    fig.savefig(OUT_DIR / "fig07_comparison_POD_energy_steady_vs_shedding.pdf")
    plt.close(fig)

    temporal = pd.read_csv(OUT_DIR / "stage03_temporal_coefficients_and_selected_Nu.csv")
    nu_all = pd.read_csv(NU_FILE)
    amp = (
        nu_all.groupby(["Re", "x_center_mm"], as_index=False)
        .agg(Nu_std=("Nu_3D_xt", "std"), Nu_mean=("Nu_3D_xt", "mean"))
    )
    amp["Nu_cv_percent"] = 100.0 * amp["Nu_std"] / amp["Nu_mean"].abs()
    fig, axes = plt.subplots(2, 1, figsize=(11.0, 7.0), sharex=True)
    for re, sub in amp.groupby("Re"):
        lw = 2.2 if re >= 160 else 1.6
        alpha = 1.0 if re >= 160 else 0.65
        axes[0].plot(sub["x_center_mm"], sub["Nu_std"], marker="o", lw=lw, alpha=alpha, label=f"Re {re:g}")
        axes[1].plot(sub["x_center_mm"], sub["Nu_cv_percent"], marker="o", lw=lw, alpha=alpha, label=f"Re {re:g}")
    for ax in axes:
        ax.axvline(-6, color="0.35", ls="--", lw=0.8)
        ax.axvline(6, color="0.35", ls="--", lw=0.8)
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=5)
    axes[0].set_ylabel("std(Nu_3D)")
    axes[1].set_ylabel("std/mean Nu [%]")
    axes[1].set_xlabel("x position [mm]")
    axes[0].set_title("Thermal-response amplitude: why steady-case EPOD correlations must be treated carefully")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig08_comparison_Nu_fluctuation_amplitude.png", dpi=240)
    fig.savefig(OUT_DIR / "fig08_comparison_Nu_fluctuation_amplitude.pdf")
    plt.close(fig)


def main() -> None:
    nu_all = pd.read_csv(NU_FILE)
    energy_all = []
    corr_all = []
    temporal_all = []
    for case in CASES:
        print(f"Analysing {case['case']}")
        energy, corr, temporal = analyse_case(case, nu_all)
        energy_all.append(energy)
        corr_all.append(corr)
        temporal_all.append(temporal)
    energy_df = pd.concat(energy_all, ignore_index=True)
    corr_df = pd.concat(corr_all, ignore_index=True)
    temporal_df = pd.concat(temporal_all, ignore_index=True)
    energy_df.to_csv(OUT_DIR / "stage03_velocity_POD_energy.csv", index=False)
    corr_df.to_csv(OUT_DIR / "stage03_EPOD_mode_Nu_correlations.csv", index=False)
    temporal_df.to_csv(OUT_DIR / "stage03_temporal_coefficients_and_selected_Nu.csv", index=False)
    plot_comparative_figures(energy_df, corr_df)
    write_readme(energy_df, corr_df)
    print(f"Wrote stage 03 outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
