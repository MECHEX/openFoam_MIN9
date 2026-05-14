from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import find_peaks


ROOT = Path(__file__).resolve().parents[4]
RUN008_DIR = ROOT / "V4b_3D" / "results" / "run008"
RUN009_DIR = ROOT / "V4b_3D" / "results" / "run009"
DATA_DIR = RUN009_DIR / "data" / "002"

RUN009_CASE_CANDIDATES = [
    Path("/home/hexmachina/of_runs/V4b_3D_run009_varprops_movie"),
    Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run009_varprops_movie"),
    Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run009_varprops_movie"),
]

D = 0.012
U_REF = 0.25266
T_IN = 293.15
T_HOT = 343.15
CP_AIR = 1005.0
MU_AIR = 1.827e-05
PR_AIR = 0.713
K_AIR = CP_AIR * MU_AIR / PR_AIR
A_HOT_TOTAL = 0.002032
WINDOW = (2.0, 10.0)


@dataclass
class RunMetrics:
    run: str
    model: str
    Cd_mean: float
    Cd_std: float
    Cl_mean: float
    Cl_rms: float
    Cl_min: float
    Cl_max: float
    f_shed_hz: float
    f_cl_adjacent_hz: float
    St: float
    Nu_EB: float
    Nu_wall: float
    Nu_tube_wall: float
    Nu_fins_wall: float
    Q_wall: float
    Q_air: float
    closure_pct: float


def find_run009_case() -> Path:
    for path in RUN009_CASE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Could not find run009 case directory")


def read_force_coeffs(path: Path) -> pd.DataFrame:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 4:
            rows.append(
                {
                    "time_s": float(parts[0]),
                    "Cm": float(parts[1]),
                    "Cd": float(parts[2]),
                    "Cl": float(parts[3]),
                }
            )
    return pd.DataFrame(rows)


def shedding_from_cl(time: np.ndarray, cl: np.ndarray) -> tuple[float, float, float]:
    dt = float(np.median(np.diff(time)))
    y = cl - float(np.mean(cl))
    peaks, _ = find_peaks(y, distance=max(1, int(0.1 / dt)))
    peak_times = time[peaks]
    adjacent_period = float(np.mean(np.diff(peak_times)))
    adjacent_freq = 1.0 / adjacent_period
    shed_freq = 0.5 * adjacent_freq
    return shed_freq, adjacent_freq, shed_freq * D / U_REF


def read_run008_metrics() -> RunMetrics:
    aero = json.loads((RUN008_DIR / "data" / "002" / "run008_002_aerodynamics.json").read_text())
    heat = pd.read_csv(RUN008_DIR / "data" / "003" / "run008_003_heat_balance_summary.csv")
    heat_map = {row.metric: row for row in heat.itertuples(index=False)}

    # Use the accepted audit values for the headline table.
    campaign = pd.read_csv(RUN008_DIR / "data" / "011" / "run008_011_campaign_regime_table.csv")
    accepted = campaign[campaign["run"] == "run008"].iloc[0]

    phase = pd.read_csv(RUN008_DIR / "data" / "009" / "run008_009_phase_global_cycle.csv")
    cl_mean = float(phase["Cl"].mean())
    cl_min = float(phase["Cl"].min())
    cl_max = float(phase["Cl"].max())

    return RunMetrics(
        run="run008",
        model="constant properties: eConst/Boussinesq",
        Cd_mean=float(accepted["Cd_mean"]),
        Cd_std=float("nan"),
        Cl_mean=cl_mean,
        Cl_rms=float(accepted["Cl_rms"]),
        Cl_min=cl_min,
        Cl_max=cl_max,
        f_shed_hz=float(aero["f0_hz"]),
        f_cl_adjacent_hz=float(aero["adjacent_peak_frequency_hz"]),
        St=float(aero["St"]),
        Nu_EB=float(accepted["Nu"]),
        Nu_wall=float(heat_map["Nu_total_wall"].mean),
        Nu_tube_wall=float(heat_map["Nu_tube_wall"].mean),
        Nu_fins_wall=float(heat_map["Nu_fins_wall"].mean),
        Q_wall=float(heat_map["Q_wall"].mean),
        Q_air=float(heat_map["Q_air"].mean),
        closure_pct=float(accepted["closure_pct"]),
    )


def read_wall_heat_flux(case_dir: Path) -> dict[str, np.ndarray]:
    path = case_dir / "postProcessing" / "wallHeatFlux" / "0" / "wallHeatFlux.dat"
    per_time: dict[float, dict[str, dict[str, float]]] = {}
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 6:
                per_time.setdefault(float(parts[0]), {})[parts[1]] = {
                    "Q": float(parts[4]),
                    "q": float(parts[5]),
                }
    times = np.asarray(sorted(per_time), dtype=float)
    patches = ["hot_tube", "hot_fin_z_min", "hot_fin_z_max"]
    out = {"time": times}
    for patch in patches:
        out[f"Q_{patch}"] = np.asarray([per_time[t].get(patch, {}).get("Q", np.nan) for t in times])
        out[f"q_{patch}"] = np.asarray([per_time[t].get(patch, {}).get("q", np.nan) for t in times])
        out[f"A_{patch}_raw"] = out[f"Q_{patch}"] / out[f"q_{patch}"]
    out["Q_tube"] = out["Q_hot_tube"]
    out["Q_fin_min"] = out["Q_hot_fin_z_min"]
    out["Q_fin_max"] = out["Q_hot_fin_z_max"]
    out["Q_fins"] = out["Q_fin_min"] + out["Q_fin_max"]
    out["Q_wall"] = out["Q_tube"] + out["Q_fins"]
    return out


def patch_info(boundary_text: str, patch_name: str) -> tuple[int, int]:
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\}}", boundary_text, flags=re.S)
    if not match:
        return 0, 0
    section = match.group(1)
    n_faces = int(re.search(r"nFaces\s+(\d+)\s*;", section).group(1))
    start_face = int(re.search(r"startFace\s+(\d+)\s*;", section).group(1))
    return n_faces, start_face


def field_patch_values(path: Path, patch_name: str, n_faces: int) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\n\s*\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found in {path}")
    section = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.full(n_faces, float(uniform.group(1)))
    vals_match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, flags=re.S)
    if not vals_match:
        raise ValueError(f"Could not parse patch {patch_name} in {path}")
    count = int(vals_match.group(1))
    vals = np.fromstring(vals_match.group(2), sep=" ")
    if count != n_faces or len(vals) != n_faces:
        raise ValueError(f"Expected {n_faces} patch values in {path}, got {len(vals)}")
    return vals


def outlet_series_decomposed(case_dir: Path, times: np.ndarray) -> pd.DataFrame:
    processors = sorted(case_dir.glob("processor*"), key=lambda p: int(p.name.replace("processor", "")))
    outlet_processors = []
    for proc in processors:
        boundary = (proc / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
        n_faces, _ = patch_info(boundary, "outlet")
        if n_faces > 0:
            outlet_processors.append((proc, n_faces))

    rows = []
    for t in times:
        name = f"{t:g}"
        mdot_sum = 0.0
        mt_sum = 0.0
        for proc, n_faces in outlet_processors:
            t_path = proc / name / "T"
            phi_path = proc / name / "phi"
            if not t_path.exists() or not phi_path.exists():
                continue
            t_vals = field_patch_values(t_path, "outlet", n_faces)
            phi_vals = field_patch_values(phi_path, "outlet", n_faces)
            weights = np.maximum(phi_vals, 0.0)
            mdot_sum += float(np.sum(weights))
            mt_sum += float(np.sum(weights * t_vals))
        if mdot_sum <= 0:
            continue
        t_mass = mt_sum / mdot_sum
        q_air = mdot_sum * CP_AIR * (t_mass - T_IN)
        lmtd_val = lmtd(t_mass)
        nu_eb = (q_air / (A_HOT_TOTAL * lmtd_val)) * D / K_AIR
        rows.append({"time_s": t, "T_out_mass": t_mass, "m_dot": mdot_sum, "Q_air": q_air, "LMTD": lmtd_val, "Nu_EB": nu_eb})
    return pd.DataFrame(rows)


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    return (d1 - d2) / math.log(d1 / d2)


def run009_metrics() -> tuple[RunMetrics, pd.DataFrame]:
    case_dir = find_run009_case()
    force = read_force_coeffs(case_dir / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat")
    force_win = force[(force["time_s"] >= WINDOW[0]) & (force["time_s"] <= WINDOW[1])].copy()
    f_shed, f_adj, st = shedding_from_cl(force_win["time_s"].to_numpy(), force_win["Cl"].to_numpy())

    wall = read_wall_heat_flux(case_dir)
    mw = (wall["time"] >= WINDOW[0]) & (wall["time"] <= WINDOW[1])
    time = wall["time"][mw]
    outlet = outlet_series_decomposed(case_dir, time)
    if outlet.empty:
        raise RuntimeError("No decomposed outlet thermal samples were parsed")
    outlet = outlet.sort_values("time_s")
    lmtd_interp = np.interp(time, outlet["time_s"].to_numpy(), outlet["LMTD"].to_numpy())
    qair_interp = np.interp(time, outlet["time_s"].to_numpy(), outlet["Q_air"].to_numpy())
    nueb_interp = np.interp(time, outlet["time_s"].to_numpy(), outlet["Nu_EB"].to_numpy())

    raw_areas = {
        "tube": float(np.nanmean(wall["A_hot_tube_raw"][mw])),
        "fin_min": float(np.nanmean(wall["A_hot_fin_z_min_raw"][mw])),
        "fin_max": float(np.nanmean(wall["A_hot_fin_z_max_raw"][mw])),
    }
    area_scale = A_HOT_TOTAL / sum(raw_areas.values())
    areas = {k: v * area_scale for k, v in raw_areas.items()}
    q_tube = wall["Q_tube"][mw]
    q_fin_min = wall["Q_fin_min"][mw]
    q_fin_max = wall["Q_fin_max"][mw]
    q_fins = q_fin_min + q_fin_max
    q_wall = wall["Q_wall"][mw]
    nu_tube = (q_tube / (areas["tube"] * lmtd_interp)) * D / K_AIR
    nu_fin_min = (q_fin_min / (areas["fin_min"] * lmtd_interp)) * D / K_AIR
    nu_fin_max = (q_fin_max / (areas["fin_max"] * lmtd_interp)) * D / K_AIR
    nu_fins = (q_fins / ((areas["fin_min"] + areas["fin_max"]) * lmtd_interp)) * D / K_AIR
    nu_wall = (q_wall / (A_HOT_TOTAL * lmtd_interp)) * D / K_AIR
    closure = 100.0 * (float(np.mean(q_wall)) - float(np.mean(qair_interp))) / float(np.mean(qair_interp))

    series = pd.DataFrame(
        {
            "time_s": time,
            "Q_wall": q_wall,
            "Q_air_massT": qair_interp,
            "Q_tube": q_tube,
            "Q_fins": q_fins,
            "LMTD_massT": lmtd_interp,
            "Nu_tube_wall": nu_tube,
            "Nu_fin_min_wall": nu_fin_min,
            "Nu_fin_max_wall": nu_fin_max,
            "Nu_fins_wall": nu_fins,
            "Nu_total_wall": nu_wall,
            "Nu_EB_massT": nueb_interp,
            "closure_massT_pct": 100.0 * (q_wall - qair_interp) / qair_interp,
        }
    )

    return (
        RunMetrics(
            run="run009",
            model="variable properties: incompressiblePerfectGas/Sutherland",
            Cd_mean=float(force_win["Cd"].mean()),
            Cd_std=float(force_win["Cd"].std(ddof=1)),
            Cl_mean=float(force_win["Cl"].mean()),
            Cl_rms=float(np.sqrt(np.mean((force_win["Cl"] - force_win["Cl"].mean()) ** 2))),
            Cl_min=float(force_win["Cl"].min()),
            Cl_max=float(force_win["Cl"].max()),
            f_shed_hz=f_shed,
            f_cl_adjacent_hz=f_adj,
            St=st,
            Nu_EB=float(series["Nu_EB_massT"].mean()),
            Nu_wall=float(series["Nu_total_wall"].mean()),
            Nu_tube_wall=float(series["Nu_tube_wall"].mean()),
            Nu_fins_wall=float(series["Nu_fins_wall"].mean()),
            Q_wall=float(series["Q_wall"].mean()),
            Q_air=float(series["Q_air_massT"].mean()),
            closure_pct=closure,
        ),
        series,
    )


def pct_delta(new: float, ref: float) -> float:
    return 100.0 * (new - ref) / ref


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    r8 = read_run008_metrics()
    r9, series9 = run009_metrics()
    series9.to_csv(DATA_DIR / "run009_002_heat_timeseries_massT.csv", index=False, float_format="%.10g")

    rows = []
    for metric in [
        "Cd_mean",
        "Cl_mean",
        "Cl_rms",
        "f_shed_hz",
        "f_cl_adjacent_hz",
        "St",
        "Nu_EB",
        "Nu_wall",
        "Nu_tube_wall",
        "Nu_fins_wall",
        "Q_wall",
        "Q_air",
        "closure_pct",
    ]:
        v8 = getattr(r8, metric)
        v9 = getattr(r9, metric)
        rows.append({"metric": metric, "run008": v8, "run009": v9, "delta": v9 - v8, "delta_pct": pct_delta(v9, v8) if v8 else np.nan})
    comp = pd.DataFrame(rows)
    comp.to_csv(DATA_DIR / "run009_002_vs_run008_global_metrics.csv", index=False, float_format="%.10g")

    model_rows = [r8.__dict__, r9.__dict__]
    pd.DataFrame(model_rows).to_csv(DATA_DIR / "run009_002_global_metric_by_run.csv", index=False, float_format="%.10g")

    lines = [
        "# V4b_3D run009 vs run008 global comparison",
        "",
        f"Window: `t = {WINDOW[0]:g}..{WINDOW[1]:g} s`.",
        "",
        "Run definitions:",
        "",
        "- `run008`: constant-property accepted production reference.",
        "- `run009`: variable-property rerun, completed to `10 s`.",
        "",
        "Important convention: `Cl` has a strong adjacent/second component near",
        "`6.56 Hz`; the reported physical shedding `St` follows the same convention",
        "as run008, using every-second `Cl` peak.",
        "",
        "| metric | run008 | run009 | delta % |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(f"| `{row['metric']}` | {row['run008']:.6g} | {row['run009']:.6g} | {row['delta_pct']:+.3f}% |")
    lines += [
        "",
        "Interpretation:",
        "",
        "- The variable-property run keeps the same shedding frequency/St within this",
        "  metric resolution.",
        "- Drag is higher in run009, consistent with the earlier variable-property",
        "  smoke-run warning.",
        "- Wall-side Nu is the cleaner heat-transfer comparison here; air-side Nu is",
        "  reconstructed from decomposed outlet mass flux and should be treated as a",
        "  diagnostic until a full heat-balance audit is repeated for run009.",
        "",
    ]
    report = "\n".join(lines)
    (DATA_DIR / "run009_002_vs_run008_global_metrics.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
