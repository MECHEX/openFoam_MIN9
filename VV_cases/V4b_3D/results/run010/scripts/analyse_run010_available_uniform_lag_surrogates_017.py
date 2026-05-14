#!/usr/bin/env python3
"""Uniform-time lag/surrogate analysis for the currently available run010 data.

This layer is stronger than the 48-phase sparse layer 016. It reads Q and
Lambda2 volScalarFields from the decomposed OpenFOAM time directories after
foamPostProcess, computes region-limited I_R(t) on a uniform dt=0.02 s grid,
pairs those signals with wall heat-transfer metrics, and runs cyclic-shift
surrogate lag scans.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RUN_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = RUN_DIR.parents[3]
DATA_DIR = RUN_DIR / "data" / "017_available_uniform_lag_surrogates"
FIG_DIR = RUN_DIR / "figures" / "017_available_uniform_lag_surrogates"

CASE_DIR = Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run010_varprops_cp")
VTK_ROOT = Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run010_varprops_cp_q_lambda2_partial48\vtk_processors")

D = 0.012
U_REF = 0.25266
T_IN = 293.15
T_HOT = 343.15
C_AIR = 1005.0
MU_AIR = 1.827e-5
PR_AIR = 0.713
K_AIR = C_AIR * MU_AIR / PR_AIR
A_HOT_TOTAL = 0.002032

Q_THR = 3000.0
L2_THR = 3000.0
F_SHED_HZ = 3.24675
T_SHED = 1.0 / F_SHED_HZ
DT_GRID = 0.02
T_START = 2.0
T_STOP = 7.52
N_SUR = 1000
RNG_SEED = 20260514

PAIRS = [
    ("R_sep", "Nu_tube_wall", "Q_tube", 0.009),
    ("R_near_wake", "Nu_tube_wall", "Q_tube", 0.018),
    ("R_fin_junction", "Nu_wall", "Q_wall", 0.006),
    ("R_fin_sweep", "Nu_fins_wall", "Q_fins", 0.020),
    ("R_far_wake", "Nu_fins_wall", "Q_fins", 0.040),
]


def load_run008_015_module():
    path = REPO_ROOT / "VV_cases" / "V4b_3D" / "results" / "run008" / "scripts" / "analyse_run008_region_structure_heat_015.py"
    spec = importlib.util.spec_from_file_location("run008_layer015", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def processor_id(path: Path) -> int:
    name = next(part for part in path.parts if part.startswith("processor"))
    return int(name.replace("processor", ""))


def build_region_cache(run008_layer, first_time: float) -> dict[int, dict[str, object]]:
    time_name = f"{first_time:g}"
    files = sorted(VTK_ROOT.glob(f"processor*/VTK/processor*_{time_name}.vtk"), key=processor_id)
    if not files:
        # Use the first available partial VTK time only for static geometry.
        files = sorted(VTK_ROOT.glob("processor*/VTK/processor*_*.vtk"), key=processor_id)
        seen = set()
        unique = []
        for path in files:
            pid = processor_id(path)
            if pid not in seen:
                seen.add(pid)
                unique.append(path)
        files = unique
    if len(files) != 20:
        raise RuntimeError(f"Expected 20 processor VTK geometry files, found {len(files)}")

    cache: dict[int, dict[str, object]] = {}
    for path in files:
        grid = run008_layer.read_legacy_vtk(path)
        centers = np.asarray([grid.points[ids].mean(axis=0) for ids in grid.cells])
        volumes = np.asarray(
            [run008_layer.cell_volume(grid.points, ids, int(ct)) for ids, ct in zip(grid.cells, grid.cell_types)]
        )
        x = centers[:, 0]
        y = centers[:, 1]
        z = centers[:, 2]
        r = np.sqrt(x * x + y * y)
        d_tube = r - D / 2.0
        d_fin = np.minimum(np.abs(z + 0.006), np.abs(z - 0.006))
        masks = {
            "R_sep": (d_tube > 0.0) & (d_tube < 0.25 * D) & (np.abs(y) > 0.35 * D) & (np.abs(y) < 1.05 * D),
            "R_near_wake": (x > 0.25 * D) & (x < 2.5 * D) & (np.abs(y) < 1.0 * D),
            "R_fin_junction": (d_tube > 0.0) & (d_tube < 0.35 * D) & (d_fin < 0.20 * D),
            "R_fin_sweep": (d_fin < 0.15 * D) & (x > -0.5 * D) & (x < 3.0 * D),
            "R_far_wake": (x > 3.0 * D) & (x < 6.0 * D) & (np.abs(y) < 1.5 * D),
            "R_global_control": volumes > 0,
        }
        masks = {key: mask & (volumes > 0) for key, mask in masks.items()}
        cell_ids = np.asarray(grid.cell_data.get("cellID"), dtype=int)
        if len(cell_ids) != len(volumes):
            raise RuntimeError(f"Missing/invalid cellID mapping in {path}")
        cache[processor_id(path)] = {"volumes": volumes, "masks": masks, "cell_ids": cell_ids}
    return cache


def parse_internal_scalar(path: Path) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)\s*;", text, re.S)
    if not m:
        u = re.search(r"internalField\s+uniform\s+([0-9eE.+\-]+)\s*;", text)
        if not u:
            raise RuntimeError(f"Cannot parse internal scalar field {path}")
        return np.asarray([float(u.group(1))])
    n = int(m.group(1))
    arr = np.fromstring(m.group(2), sep=" ")
    if len(arr) != n:
        raise RuntimeError(f"Expected {n} values, got {len(arr)} in {path}")
    return arr


def time_name(t: float) -> str:
    return f"{t:.8f}".rstrip("0").rstrip(".")


def available_uniform_times() -> list[float]:
    times = []
    for i in range(int(round((T_STOP - T_START) / DT_GRID)) + 1):
        t = round(T_START + i * DT_GRID, 8)
        name = time_name(t)
        if (CASE_DIR / "processor0" / name / "Q").exists() and (CASE_DIR / "processor0" / name / "Lambda2").exists():
            times.append(t)
    return times


def compute_vortex_series() -> pd.DataFrame:
    run008_layer = load_run008_015_module()
    cache = build_region_cache(run008_layer, 3.58)
    times = available_uniform_times()
    if len(times) < 20:
        raise RuntimeError("Too few available Q/Lambda2 times for uniform analysis")

    rows = []
    for idx, t in enumerate(times, start=1):
        name = time_name(t)
        accum: dict[str, dict[str, float]] = {}
        for proc_dir in sorted(CASE_DIR.glob("processor*"), key=lambda p: int(p.name.replace("processor", ""))):
            pid = int(proc_dir.name.replace("processor", ""))
            proc_cache = cache[pid]
            volumes = proc_cache["volumes"]
            cell_ids = proc_cache["cell_ids"]
            q = parse_internal_scalar(proc_dir / name / "Q")
            l2 = parse_internal_scalar(proc_dir / name / "Lambda2")
            if int(np.max(cell_ids)) >= len(q) or int(np.max(cell_ids)) >= len(l2):
                raise RuntimeError(f"Field/geometry length mismatch in {proc_dir / name}")
            q = q[cell_ids]
            l2 = l2[cell_ids]
            for region, mask in proc_cache["masks"].items():
                vr = float(np.sum(volumes[mask]))
                rec = accum.setdefault(region, {"volume": 0.0, "IQ": 0.0, "IL2": 0.0, "Qfrac": 0.0, "L2frac": 0.0})
                rec["volume"] += vr
                rec["IQ"] += float(np.sum(np.maximum(q[mask] - Q_THR, 0.0) * volumes[mask]))
                rec["IL2"] += float(np.sum(np.maximum(-l2[mask] - L2_THR, 0.0) * volumes[mask]))
                rec["Qfrac"] += float(np.sum((q[mask] > Q_THR) * volumes[mask]))
                rec["L2frac"] += float(np.sum((l2[mask] < -L2_THR) * volumes[mask]))
        for region, rec in accum.items():
            vol = rec["volume"]
            iq = rec["IQ"] / vol
            il2 = rec["IL2"] / vol
            rows.append(
                {
                    "time_s": t,
                    "region": region,
                    "volume_m3": vol,
                    "I_Q": iq,
                    "I_Lambda2": il2,
                    "Q_volume_fraction": rec["Qfrac"] / vol,
                    "Lambda2_volume_fraction": rec["L2frac"] / vol,
                    "I_Q_star": iq * D * D / (U_REF * U_REF),
                    "I_Lambda2_star": il2 * D * D / (U_REF * U_REF),
                }
            )
        if idx % 25 == 0 or idx == len(times):
            print(f"processed vortex time {idx}/{len(times)} t={name}", flush=True)
    return pd.DataFrame(rows)


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    return (d1 - d2) / math.log(d1 / d2)


def read_wall_heat_flux() -> dict[str, np.ndarray]:
    records: dict[float, dict[str, dict[str, float]]] = {}
    for path in sorted((CASE_DIR / "postProcessing" / "wallHeatFlux").glob("*/wallHeatFlux.dat")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 6:
                t = float(parts[0])
                records.setdefault(t, {})[parts[1]] = {"Q": float(parts[4]), "q": float(parts[5])}
    times = np.asarray(sorted(t for t in records if T_START <= t <= T_STOP), dtype=float)
    out = {"time": times}
    for patch in ["hot_tube", "hot_fin_z_min", "hot_fin_z_max"]:
        q_rate = np.asarray([records[t].get(patch, {}).get("Q", np.nan) for t in times])
        q_flux = np.asarray([records[t].get(patch, {}).get("q", np.nan) for t in times])
        out[f"Q_{patch}"] = q_rate
        out[f"Araw_{patch}"] = q_rate / q_flux
    out["Q_tube"] = out["Q_hot_tube"]
    out["Q_fin_min"] = out["Q_hot_fin_z_min"]
    out["Q_fin_max"] = out["Q_hot_fin_z_max"]
    out["Q_fins"] = out["Q_fin_min"] + out["Q_fin_max"]
    out["Q_wall"] = out["Q_tube"] + out["Q_fins"]
    return out


def patch_nfaces(boundary_text: str, name: str) -> int:
    match = re.search(rf"{re.escape(name)}\s*\{{(.*?)\}}", boundary_text, re.S)
    if not match:
        return 0
    nmatch = re.search(r"nFaces\s+(\d+)\s*;", match.group(1))
    return int(nmatch.group(1)) if nmatch else 0


def patch_values(path: Path, patch: str, n_faces: int) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch)}\s*\{{(.*?)\n\s*\}}", text, re.S)
    if not match:
        raise RuntimeError(f"Patch {patch} not found in {path}")
    section = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.full(n_faces, float(uniform.group(1)))
    vals = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, re.S)
    if not vals:
        raise RuntimeError(f"Patch values not found for {patch} in {path}")
    arr = np.fromstring(vals.group(2), sep=" ")
    if len(arr) != n_faces:
        raise RuntimeError(f"Expected {n_faces} values, got {len(arr)} in {path}")
    return arr


def outlet_at_time(t: float) -> dict[str, float]:
    name = time_name(t)
    mdot = 0.0
    mt = 0.0
    for proc in sorted(CASE_DIR.glob("processor*"), key=lambda p: int(p.name.replace("processor", ""))):
        boundary = (proc / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
        n_faces = patch_nfaces(boundary, "outlet")
        if n_faces <= 0:
            continue
        t_path = proc / name / "T"
        phi_path = proc / name / "phi"
        if not t_path.exists() or not phi_path.exists():
            continue
        temp = patch_values(t_path, "outlet", n_faces)
        phi = patch_values(phi_path, "outlet", n_faces)
        weights = np.maximum(phi, 0.0)
        mdot += float(np.sum(weights))
        mt += float(np.sum(weights * temp))
    if mdot <= 0:
        return {"T_out": np.nan, "m_dot": np.nan, "Q_air": np.nan, "LMTD": np.nan, "Nu_EB": np.nan}
    t_out = mt / mdot
    q_air = mdot * C_AIR * (t_out - T_IN)
    l_val = lmtd(t_out)
    nu_eb = (q_air / (A_HOT_TOTAL * l_val)) * D / K_AIR
    return {"T_out": t_out, "m_dot": mdot, "Q_air": q_air, "LMTD": l_val, "Nu_EB": nu_eb}


def compute_heat_series(times: list[float]) -> pd.DataFrame:
    wall = read_wall_heat_flux()
    wt = wall["time"]
    raw_areas = {
        "tube": float(np.nanmean(wall["Araw_hot_tube"])),
        "fin_min": float(np.nanmean(wall["Araw_hot_fin_z_min"])),
        "fin_max": float(np.nanmean(wall["Araw_hot_fin_z_max"])),
    }
    scale = A_HOT_TOTAL / sum(raw_areas.values())
    areas = {k: v * scale for k, v in raw_areas.items()}
    rows = []
    for idx, t in enumerate(times, start=1):
        q_tube = float(np.interp(t, wt, wall["Q_tube"]))
        q_fins = float(np.interp(t, wt, wall["Q_fins"]))
        q_wall = float(np.interp(t, wt, wall["Q_wall"]))
        out = outlet_at_time(t)
        l_val = out["LMTD"]
        rows.append(
            {
                "time_s": t,
                "Q_tube": q_tube,
                "Q_fins": q_fins,
                "Q_wall": q_wall,
                "Q_air": out["Q_air"],
                "closure_pct": 100.0 * (q_wall - out["Q_air"]) / out["Q_air"],
                "Nu_tube_wall": (q_tube / (areas["tube"] * l_val)) * D / K_AIR,
                "Nu_fins_wall": (q_fins / ((areas["fin_min"] + areas["fin_max"]) * l_val)) * D / K_AIR,
                "Nu_wall": (q_wall / A_HOT_TOTAL / l_val) * D / K_AIR,
                "Nu_EB": out["Nu_EB"],
                "T_out": out["T_out"],
            }
        )
        if idx % 50 == 0 or idx == len(times):
            print(f"processed heat time {idx}/{len(times)} t={time_name(t)}", flush=True)
    return pd.DataFrame(rows)


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


def tukey(n: int, alpha: float = 0.1) -> np.ndarray:
    w = np.ones(n)
    edge = int(math.floor(alpha * (n - 1) / 2.0))
    if edge < 1:
        return w
    x = np.linspace(0, 1, edge + 1)
    taper = 0.5 * (1 + np.cos(np.pi * (2 * x / alpha - 1)))
    w[: edge + 1] = taper
    w[-edge - 1 :] = taper[::-1]
    return w


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


def spectral_phase_tau(x: np.ndarray, y: np.ndarray, dt: float, f_target: float) -> tuple[float, float]:
    freqs = np.fft.rfftfreq(len(x), d=dt)
    idx = int(np.argmin(np.abs(freqs - f_target)))
    cpsd = np.conj(np.fft.rfft(zscore(x))[idx]) * np.fft.rfft(zscore(y))[idx]
    tau = float(np.angle(cpsd) / (2 * np.pi * freqs[idx]))
    while tau > 0.5 / freqs[idx]:
        tau -= 1.0 / freqs[idx]
    while tau < -0.5 / freqs[idx]:
        tau += 1.0 / freqs[idx]
    return tau, float(freqs[idx])


def verdict(rho_abs: float, tau: float, p95: float, p99: float, tau_conv: float) -> str:
    if rho_abs <= p95:
        return "not significant"
    if tau <= 0:
        return "significant but wrong-direction/zero-lag"
    if tau > 0.5 * T_SHED:
        return "significant but lag > T_shed/2"
    if abs(tau - tau_conv) > 0.5 * T_SHED:
        return "significant but convection-lag mismatch"
    return "confirmed p<0.01" if rho_abs > p99 else "confirmed p<0.05"


def run_lag_scan(vortex: pd.DataFrame, heat: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RNG_SEED)
    win = tukey(len(heat), 0.1)
    max_shift_lo = int(round(0.2 * len(heat)))
    max_shift_hi = int(round(0.8 * len(heat)))
    rows = []
    curves = []
    for region, nu_col, q_col, dist in PAIRS:
        sub = vortex[vortex["region"] == region].sort_values("time_s")
        merged = sub.merge(heat, on="time_s", how="inner")
        tau_conv = dist / 0.253
        for structure_col, structure_label in [("I_Lambda2_star", "I_Lambda2*"), ("I_Q_star", "I_Q*")]:
            x = zscore(detrend_linear(merged[structure_col].to_numpy(float))) * win
            for response_label, response_col in [("Nu", nu_col), ("Q", q_col)]:
                y = zscore(detrend_linear(merged[response_col].to_numpy(float))) * win
                lags, corr = xcorr_lag(x, y, DT_GRID, T_SHED)
                idx = int(np.nanargmax(np.abs(corr)))
                tau_star = float(lags[idx])
                rho_star = float(corr[idx])
                sur = []
                for _ in range(N_SUR):
                    xs = np.roll(x, int(rng.integers(max_shift_lo, max_shift_hi)))
                    _, cs = xcorr_lag(xs, y, DT_GRID, T_SHED)
                    sur.append(float(np.nanmax(np.abs(cs))))
                sur = np.asarray(sur)
                p95 = float(np.nanpercentile(sur, 95))
                p99 = float(np.nanpercentile(sur, 99))
                p_emp = float((1 + np.sum(sur >= abs(rho_star))) / (N_SUR + 1))
                tau_phase, f_bin = spectral_phase_tau(x, y, DT_GRID, F_SHED_HZ)
                rec = {
                    "pair": f"{region} -> {nu_col}",
                    "region": region,
                    "structure_signal": structure_label,
                    "response_signal": response_label,
                    "response_column": response_col,
                    "n": len(merged),
                    "rho_star": rho_star,
                    "abs_rho_star": abs(rho_star),
                    "tau_star_s": tau_star,
                    "tau_over_T_shed": tau_star / T_SHED,
                    "surrogate_p95_absrho": p95,
                    "surrogate_p99_absrho": p99,
                    "empirical_p": p_emp,
                    "tau_phase_s": tau_phase,
                    "phase_frequency_bin_hz": f_bin,
                    "L_RS_m_assumed": dist,
                    "tau_conv_s_assumed": tau_conv,
                    "verdict": verdict(abs(rho_star), tau_star, p95, p99, tau_conv),
                }
                rows.append(rec)
                for lag, c in zip(lags, corr):
                    curves.append(
                        {
                            "pair": rec["pair"],
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
    return pd.DataFrame(rows), pd.DataFrame(curves)


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            vals.append(f"{val:.4g}" if isinstance(val, float) else str(val))
        out.append("| " + " | ".join(vals) + " |")
    return "\n".join(out)


def make_figure(summary: pd.DataFrame, curves: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(len(PAIRS), 1, figsize=(8.4, 10.8), sharex=True)
    for ax, (region, nu_col, _, _) in zip(axes, PAIRS):
        pair = f"{region} -> {nu_col}"
        c = curves[(curves["pair"] == pair) & (curves["structure_signal"] == "I_Lambda2*") & (curves["response_signal"] == "Nu")]
        r = summary[(summary["pair"] == pair) & (summary["structure_signal"] == "I_Lambda2*") & (summary["response_signal"] == "Nu")].iloc[0]
        ax.plot(c["lag_s"], c["corr"], color="#2f5d8c", lw=1.8)
        ax.axhline(0, color="0.25", lw=0.8)
        ax.fill_between(c["lag_s"], -c["surrogate_p95_absrho"], c["surrogate_p95_absrho"], color="#f2c14e", alpha=0.25, label="surrogate 95%" if ax is axes[0] else None)
        ax.fill_between(c["lag_s"], -c["surrogate_p99_absrho"], c["surrogate_p99_absrho"], color="#d95d39", alpha=0.16, label="surrogate 99%" if ax is axes[0] else None)
        ax.axvline(r["tau_star_s"], color="#1b9e77", lw=1.4)
        ax.axvline(r["tau_conv_s_assumed"], color="#7b3294", lw=1.2, ls="--")
        ax.axvline(-r["tau_conv_s_assumed"], color="#7b3294", lw=1.0, ls=":")
        ax.set_ylabel("rho")
        ax.set_title(f"{pair}: rho*={r['rho_star']:+.3f}, tau*={r['tau_star_s']:+.3f}s, p={r['empirical_p']:.3f}")
    axes[-1].set_xlabel("lag tau [s], positive = structure leads heat")
    axes[0].legend(loc="upper right", frameon=False)
    fig.suptitle("run010 layer 017: available uniform lag scan, I_Lambda2* -> Nu", y=0.995)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run010_017_available_uniform_lag_surrogate_lambda2_nu.png", dpi=220)
    fig.savefig(FIG_DIR / "run010_017_available_uniform_lag_surrogate_lambda2_nu.pdf")
    plt.close(fig)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    vortex = compute_vortex_series()
    times = sorted(vortex["time_s"].unique())
    heat = compute_heat_series(times)
    summary, curves = run_lag_scan(vortex, heat)

    vortex.to_csv(DATA_DIR / "run010_017_available_uniform_region_q_lambda2_timeseries.csv", index=False, float_format="%.10g")
    heat.to_csv(DATA_DIR / "run010_017_available_uniform_heat_timeseries.csv", index=False, float_format="%.10g")
    summary.to_csv(DATA_DIR / "run010_017_available_uniform_lag_surrogate_summary.csv", index=False, float_format="%.10g")
    curves.to_csv(DATA_DIR / "run010_017_available_uniform_lag_surrogate_curves.csv", index=False, float_format="%.10g")
    make_figure(summary, curves)

    best = summary.sort_values(["empirical_p", "abs_rho_star"], ascending=[True, False]).head(12)
    l2nu = summary[(summary["structure_signal"] == "I_Lambda2*") & (summary["response_signal"] == "Nu")]
    md = [
        "# V4b_3D run010 layer 017",
        "",
        "Lag scan with cyclic-shift surrogates using the currently available incomplete run010 data.",
        "",
        "## Inputs",
        "",
        f"- time window: `{min(times):.3f}..{max(times):.3f} s`",
        f"- uniform vortex/heat grid: `{len(times)}` samples at `dt = {DT_GRID:.3f} s`",
        f"- lag range: `+-T_shed = +-{T_SHED:.4f} s`",
        f"- cyclic-shift surrogates: `{N_SUR}`",
        "- region intensities computed from decomposed OpenFOAM `Q` and `Lambda2` fields",
        "",
        "## Heat balance on the analysis grid",
        "",
        f"- `Q_wall_mean = {heat['Q_wall'].mean():.6g} W`",
        f"- `Q_air_mean = {heat['Q_air'].mean():.6g} W`",
        f"- `closure_mean = {heat['closure_pct'].mean():+.4f}%`",
        f"- `Nu_wall_mean = {heat['Nu_wall'].mean():.6g}`",
        f"- `Nu_EB_mean = {heat['Nu_EB'].mean():.6g}`",
        "",
        "## I_Lambda2* -> Nu hypothesis pairs",
        "",
        markdown_table(l2nu[["pair", "rho_star", "tau_star_s", "tau_over_T_shed", "surrogate_p95_absrho", "surrogate_p99_absrho", "empirical_p", "tau_phase_s", "tau_conv_s_assumed", "verdict"]]),
        "",
        "## Strongest associations across all screened signals",
        "",
        markdown_table(best[["pair", "structure_signal", "response_signal", "rho_star", "tau_star_s", "empirical_p", "verdict"]]),
        "",
        "## Interpretation",
        "",
        "This is a stronger diagnostic than layer 016 because it uses a uniform time series instead of 48 phase-selected samples.",
        "A positive `tau_star_s` means that the regional structure metric leads the heat response.",
        "Pairs marked as confirmed pass the cyclic-shift surrogate threshold and have a positive lag within the expected convection-time range.",
        "Because run010 is still incomplete, repeat this layer after the solver reaches `t = 10 s` before using it as a final paper-grade claim.",
    ]
    (DATA_DIR / "run010_017_available_uniform_lag_surrogate_analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (DATA_DIR / "run010_017_available_uniform_lag_surrogate_metadata.json").write_text(
        json.dumps(
            {
                "status": "incomplete-run uniform diagnostic",
                "t_start": min(times),
                "t_stop": max(times),
                "dt_grid": DT_GRID,
                "n_samples": len(times),
                "n_surrogates": N_SUR,
                "f_shed_hz": F_SHED_HZ,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("\n".join(md))


if __name__ == "__main__":
    main()
