from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/007_strong_indicators/00_fullNu3D_xt"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_002 = REPO_DIR / "VV_cases/presentation_data/002_Nu_and_vorticity"
import sys

sys.path.insert(0, str(SOURCE_002))
from build_stripwise_heat_figures import PATCH_FILES, polygon_area, read_vtk_polydata  # noqa: E402


CASES = [
    {"Re": 100.0, "case": "run012_re100", "path": Path("/home/hexmachina/of_runs/V4b_3D_run012_re100_production"), "window": (8.0, 10.0), "regime": "steady"},
    {"Re": 150.0, "case": "run013_re150", "path": Path("/home/hexmachina/of_runs/V4b_3D_run013_re150_production"), "window": (8.0, 10.0), "regime": "steady"},
    {"Re": 160.0, "case": "run015_re160", "path": Path("/home/hexmachina/of_runs/V4b_3D_run015_re160_production"), "window": (8.0, 10.0), "regime": "shedding"},
    {"Re": 175.0, "case": "run014_re175", "path": Path("/home/hexmachina/of_runs/V4b_3D_run014_re175_production"), "window": (8.0, 10.0), "regime": "shedding"},
    {"Re": 200.0, "case": "run008_re200", "path": Path("/home/hexmachina/of_runs/V4b_3D_run008"), "window": (8.0, 10.0), "regime": "production shedding"},
]

DX_M = 0.001
TIME_STRIDE = 10
D_REF_M = 0.012
K_AIR_W_MK = 0.028
T_WALL_K = 343.15
POSITIVE_UX_EPS = 1.0e-10


def run_bash(command: str, cwd: Path | None = None) -> None:
    full = f"source /opt/openfoam13/etc/bashrc; {command}"
    subprocess.run(["bash", "-lc", full], cwd=str(cwd) if cwd else None, check=True)


def numeric_time_dirs(base: Path) -> list[tuple[float, str]]:
    out: list[tuple[float, str]] = []
    if not base.exists():
        return out
    for p in base.iterdir():
        if not p.is_dir():
            continue
        try:
            out.append((float(p.name), p.name))
        except ValueError:
            continue
    return sorted(out, key=lambda item: item[0])


def selected_surface_times(case: dict) -> list[str]:
    t0, t1 = case["window"]
    surface = {round(t, 10): name for t, name in numeric_time_dirs(case["path"] / "postProcessing/hot_tube_surface")}
    vals: list[tuple[float, str]] = []
    for t, name in numeric_time_dirs(case["path"] / "processor0"):
        key = round(t, 10)
        field_dir = case["path"] / "processor0" / name
        if (
            t0 <= t <= t1
            and (field_dir / "U").exists()
            and (field_dir / "T").exists()
            and (field_dir / "rho").exists()
            and key in surface
        ):
            vals.append((t, surface[key]))
    vals.sort(key=lambda item: item[0])
    return [name for _, name in vals]


def n_processors(case_dir: Path) -> int:
    return len([p for p in case_dir.iterdir() if p.is_dir() and p.name.startswith("processor")])


def discover_edges_from_surfaces() -> np.ndarray:
    xs: list[float] = []
    for case in CASES:
        times = selected_surface_times(case)
        if not times:
            continue
        time = times[len(times) // 2]
        for group in PATCH_FILES.values():
            for tpl in group:
                f = case["path"] / "postProcessing" / tpl.format(time=time)
                if f.exists():
                    pts, _, _ = read_vtk_polydata(f)
                    xs.extend([float(pts[:, 0].min()), float(pts[:, 0].max())])
    if not xs:
        raise RuntimeError("Could not discover x range from hot-surface VTK files.")
    left = math.floor(min(xs) / DX_M) * DX_M
    right = math.ceil(max(xs) / DX_M) * DX_M
    return np.arange(left, right + 0.5 * DX_M, DX_M)


def plane_name(x_m: float) -> str:
    return f"xPlane_{int(round(x_m * 10000)):p}".replace("-", "m").replace("+", "p")


def safe_plane_name(x_m: float) -> str:
    n = int(round(x_m * 10000))
    return f"xPlane_m{abs(n):04d}" if n < 0 else f"xPlane_p{abs(n):04d}"


def write_cutplane_dict(edges: np.ndarray) -> Path:
    path = OUT_DIR / "fullNu3D_yz_cutplanes_functions"
    lines = [
        "FoamFile",
        "{",
        "    format      ascii;",
        "    class       dictionary;",
        "    object      functions;",
        "}",
        "",
    ]
    for x_m in edges:
        name = safe_plane_name(float(x_m))
        lines.extend(
            [
                "#includeFunc cutPlaneSurface",
                "(",
                f"    name={name},",
                f"    point=({x_m:.9g} 0 0),",
                "    normal=(1 0 0),",
                "    fields=(U T rho)",
                ")",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="ascii")
    return path


def ensure_cutplanes(case: dict, times: list[str], edges: np.ndarray, dict_path: Path) -> None:
    missing = []
    for time in times:
        for x_m in edges:
            f = case["path"] / "postProcessing" / safe_plane_name(float(x_m)) / time / "cutPlane.vtk"
            if not f.exists():
                missing.append(time)
                break
    if not missing:
        return
    nproc = n_processors(case["path"])
    if nproc <= 0:
        raise RuntimeError(f"No processor directories in {case['path']}")
    time_list = ",".join(dict.fromkeys(missing))
    cmd = (
        f"cd {case['path']}; "
        f"mpirun -np {nproc} --oversubscribe --allow-run-as-root "
        f"postProcess -parallel -dict {dict_path} -time {time_list}"
    )
    run_bash(cmd, cwd=case["path"])


def surface_q_area(path: Path, edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    points, polygons, fields = read_vtk_polydata(path)
    q = fields["wallHeatFlux"]
    q_sum = np.zeros(len(edges) - 1)
    a_sum = np.zeros(len(edges) - 1)
    for poly in polygons:
        idx = np.asarray(poly, dtype=int)
        verts = points[idx]
        b = int(np.searchsorted(edges, float(verts[:, 0].mean()), side="right") - 1)
        if b < 0 or b >= len(q_sum):
            continue
        area = polygon_area(verts)
        q_sum[b] += float(q[idx].mean()) * area
        a_sum[b] += area
    return q_sum, a_sum


def read_vtk_polydata_robust(path: Path) -> tuple[np.ndarray, list[list[int]], dict[str, np.ndarray]]:
    lines = path.read_text(errors="ignore").splitlines()
    i = 0
    points = None
    polygons: list[list[int]] = []
    fields: dict[str, np.ndarray] = {}
    n_points = 0
    while i < len(lines):
        parts = lines[i].split()
        if not parts:
            i += 1
            continue
        key = parts[0]
        if key == "POINTS":
            n_points = int(parts[1])
            vals: list[float] = []
            i += 1
            while len(vals) < 3 * n_points and i < len(lines):
                vals.extend(float(x) for x in lines[i].split())
                i += 1
            points = np.asarray(vals[: 3 * n_points], dtype=float).reshape(n_points, 3)
            continue
        if key == "POLYGONS":
            n_poly = int(parts[1])
            raw: list[int] = []
            i += 1
            while len(polygons) < n_poly and i < len(lines):
                if lines[i].split():
                    raw.extend(int(float(x)) for x in lines[i].split())
                j = 0
                while j < len(raw) and len(polygons) < n_poly:
                    nverts = raw[j]
                    if j + 1 + nverts > len(raw):
                        break
                    polygons.append(raw[j + 1 : j + 1 + nverts])
                    j += 1 + nverts
                raw = raw[j:]
                i += 1
            continue
        if key in {"POINT_DATA", "CELL_DATA"}:
            i += 1
            continue
        if key == "FIELD":
            n_fields = int(parts[2])
            i += 1
            for _ in range(n_fields):
                while i < len(lines) and not lines[i].split():
                    i += 1
                header = lines[i].split()
                name = header[0]
                n_comp = int(header[1])
                n_tuple = int(header[2])
                count = n_comp * n_tuple
                vals: list[float] = []
                i += 1
                while len(vals) < count and i < len(lines):
                    if lines[i].split():
                        vals.extend(float(x) for x in lines[i].split())
                    i += 1
                arr = np.asarray(vals[:count], dtype=float)
                if n_comp > 1:
                    arr = arr.reshape(n_tuple, n_comp)
                fields[name] = arr
            continue
        i += 1
    if points is None:
        raise ValueError(f"No POINTS in {path}")
    return points, polygons, fields


def read_plane_tbulk(path: Path) -> dict[str, float]:
    points, polygons, fields = read_vtk_polydata_robust(path)
    if "U" not in fields or "T" not in fields:
        return {
            "T_bulk_yz_plane_K": np.nan,
            "rhoUx_area_integral_kg_s_m2_proxy": np.nan,
            "positive_Ux_plane_area_m2": np.nan,
        }
    u = fields["U"]
    t = fields["T"]
    rho = fields.get("rho", np.ones(len(points)))
    mass_flux = 0.0
    heat_flux = 0.0
    area_sum = 0.0
    for poly in polygons:
        idx = np.asarray(poly, dtype=int)
        verts = points[idx]
        area = polygon_area(verts)
        ux = float(u[idx, 0].mean())
        if ux <= POSITIVE_UX_EPS:
            continue
        rho_mean = float(rho[idx].mean())
        t_mean = float(t[idx].mean())
        w = rho_mean * ux * area
        mass_flux += w
        heat_flux += w * t_mean
        area_sum += area
    return {
        "T_bulk_yz_plane_K": heat_flux / mass_flux if mass_flux > 0 else np.nan,
        "rhoUx_area_integral_kg_s_m2_proxy": mass_flux,
        "positive_Ux_plane_area_m2": area_sum,
    }


def lmtd(delta_left: float, delta_right: float) -> float:
    delta_left = max(delta_left, 1.0e-12)
    delta_right = max(delta_right, 1.0e-12)
    if abs(delta_left - delta_right) < 1.0e-10:
        return 0.5 * (delta_left + delta_right)
    return (delta_left - delta_right) / math.log(delta_left / delta_right)


def compute_case(case: dict, edges: np.ndarray) -> list[dict]:
    rows: list[dict] = []
    times = selected_surface_times(case)
    x_centers = 0.5 * (edges[:-1] + edges[1:])
    for time in times:
        q_tube = np.zeros(len(edges) - 1)
        a_tube = np.zeros(len(edges) - 1)
        q_fins = np.zeros(len(edges) - 1)
        a_fins = np.zeros(len(edges) - 1)
        for tpl in PATCH_FILES["tube"]:
            f = case["path"] / "postProcessing" / tpl.format(time=time)
            if f.exists():
                q, a = surface_q_area(f, edges)
                q_tube += q
                a_tube += a
        for tpl in PATCH_FILES["fins"]:
            f = case["path"] / "postProcessing" / tpl.format(time=time)
            if f.exists():
                q, a = surface_q_area(f, edges)
                q_fins += q
                a_fins += a

        plane = []
        for x_m in edges:
            f = case["path"] / "postProcessing" / safe_plane_name(float(x_m)) / time / "cutPlane.vtk"
            plane.append(read_plane_tbulk(f))
        t_bulk = np.asarray([p["T_bulk_yz_plane_K"] for p in plane])
        mass_flux = np.asarray([p["rhoUx_area_integral_kg_s_m2_proxy"] for p in plane])

        for i, x_m in enumerate(x_centers):
            q_total = q_tube[i] + q_fins[i]
            a_total = a_tube[i] + a_fins[i]
            dt_left = T_WALL_K - t_bulk[i]
            dt_right = T_WALL_K - t_bulk[i + 1]
            dt_lm = lmtd(dt_left, dt_right)
            alpha_total = q_total / (a_total * dt_lm) if a_total > 0 and dt_lm > 0 else np.nan
            alpha_tube = q_tube[i] / (a_tube[i] * dt_lm) if a_tube[i] > 0 and dt_lm > 0 else np.nan
            alpha_fins = q_fins[i] / (a_fins[i] * dt_lm) if a_fins[i] > 0 and dt_lm > 0 else np.nan
            rows.append(
                {
                    "Re": case["Re"],
                    "case": case["case"],
                    "regime": case["regime"],
                    "time_s": float(time),
                    "x_left_mm": edges[i] * 1000.0,
                    "x_right_mm": edges[i + 1] * 1000.0,
                    "x_center_mm": x_m * 1000.0,
                    "Q_total_strip_W": q_total,
                    "Q_tube_strip_W": q_tube[i],
                    "Q_fins_strip_W": q_fins[i],
                    "A_total_strip_m2": a_total,
                    "A_tube_strip_m2": a_tube[i],
                    "A_fins_strip_m2": a_fins[i],
                    "T_bulk_left_yz_K": t_bulk[i],
                    "T_bulk_right_yz_K": t_bulk[i + 1],
                    "DeltaT_left_K": dt_left,
                    "DeltaT_right_K": dt_right,
                    "DeltaT_lm_yz_K": dt_lm,
                    "rhoUx_left_integral": mass_flux[i],
                    "rhoUx_right_integral": mass_flux[i + 1],
                    "alpha_3D_xt_W_m2K": alpha_total,
                    "Nu_3D_xt": alpha_total * D_REF_M / K_AIR_W_MK if np.isfinite(alpha_total) else np.nan,
                    "Nu_tube_3D_xt_shared_Tbulk": alpha_tube * D_REF_M / K_AIR_W_MK if np.isfinite(alpha_tube) else np.nan,
                    "Nu_fins_3D_xt_shared_Tbulk": alpha_fins * D_REF_M / K_AIR_W_MK if np.isfinite(alpha_fins) else np.nan,
                    "D_ref_m": D_REF_M,
                    "k_air_W_mK": K_AIR_W_MK,
                    "T_wall_K": T_WALL_K,
                }
            )
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_outputs(df: pd.DataFrame) -> None:
    avg = (
        df.groupby(["Re", "case", "regime", "x_center_mm"], as_index=False)
        .agg(
            Nu_3D_xt_mean=("Nu_3D_xt", "mean"),
            Nu_3D_xt_std=("Nu_3D_xt", "std"),
            Q_total_strip_W_mean=("Q_total_strip_W", "mean"),
            Q_total_strip_W_std=("Q_total_strip_W", "std"),
            DeltaT_lm_yz_K_mean=("DeltaT_lm_yz_K", "mean"),
            T_bulk_left_yz_K_mean=("T_bulk_left_yz_K", "mean"),
            T_bulk_right_yz_K_mean=("T_bulk_right_yz_K", "mean"),
            n_times=("time_s", "count"),
        )
    )
    avg.to_csv(OUT_DIR / "fullNu3D_xt_time_averaged_by_x.csv", index=False)
    summary = (
        df.groupby(["Re", "case", "regime"], as_index=False)
        .agg(
            n_times=("time_s", "nunique"),
            Q_total_W_mean=("Q_total_strip_W", "sum"),
            Nu_3D_xt_mean=("Nu_3D_xt", "mean"),
            Nu_3D_xt_std=("Nu_3D_xt", "std"),
            DeltaT_lm_yz_K_mean=("DeltaT_lm_yz_K", "mean"),
        )
    )
    # Correct global Q mean after the strip/time groupby above.
    q_global = df.groupby(["Re", "time_s"])["Q_total_strip_W"].sum().groupby("Re").agg(["mean", "std"]).reset_index()
    summary = summary.drop(columns=["Q_total_W_mean"]).merge(q_global.rename(columns={"mean": "Q_total_W_mean", "std": "Q_total_W_std"}), on="Re")
    summary.to_csv(OUT_DIR / "fullNu3D_xt_summary_by_Re.csv", index=False)

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    for re, sub in avg.groupby("Re"):
        ax.plot(sub["x_center_mm"], sub["Nu_3D_xt_mean"], lw=2.0, label=f"Re {re:g}")
        ax.fill_between(
            sub["x_center_mm"].to_numpy(),
            (sub["Nu_3D_xt_mean"] - sub["Nu_3D_xt_std"]).to_numpy(),
            (sub["Nu_3D_xt_mean"] + sub["Nu_3D_xt_std"]).to_numpy(),
            alpha=0.12,
        )
    ax.axvline(-6, color="0.35", ls="--", lw=0.8)
    ax.axvline(6, color="0.35", ls="--", lw=0.8)
    ax.set_xlabel("x position from tube center [mm], 1 mm strips")
    ax.set_ylabel("Nu_3D(x,t), time mean +/- 1 std")
    ax.set_title("Publication-grade strip Nu using full hot surfaces and y-z-plane Tbulk")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig01_Nu3D_xt_profiles_time_mean.png", dpi=240)
    fig.savefig(OUT_DIR / "fig01_Nu3D_xt_profiles_time_mean.pdf")
    plt.close(fig)

    selected_re = [160.0, 175.0, 200.0]
    selected_x = [-5.5, 5.5, 10.5]
    fig, axes = plt.subplots(len(selected_re), 1, figsize=(10.5, 8.0), sharex=True)
    for ax, re in zip(axes, selected_re):
        sub = df[np.isclose(df["Re"], re)]
        for x in selected_x:
            sx = sub[np.isclose(sub["x_center_mm"], x)]
            if not sx.empty:
                ax.plot(sx["time_s"], sx["Nu_3D_xt"], lw=1.4, label=f"x={x:g} mm")
        ax.set_ylabel(f"Re {re:g}\nNu")
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=3)
    axes[-1].set_xlabel("time [s]")
    fig.suptitle("Time-resolved Nu_3D(x,t) at selected strips")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig02_Nu3D_xt_time_traces_selected_strips.png", dpi=240)
    fig.savefig(OUT_DIR / "fig02_Nu3D_xt_time_traces_selected_strips.pdf")
    plt.close(fig)

    for re in selected_re:
        sub = df[np.isclose(df["Re"], re)]
        pivot = sub.pivot_table(index="x_center_mm", columns="time_s", values="Nu_3D_xt")
        fig, ax = plt.subplots(figsize=(10.5, 5.6))
        im = ax.imshow(
            pivot.to_numpy(),
            origin="lower",
            aspect="auto",
            extent=[pivot.columns.min(), pivot.columns.max(), pivot.index.min(), pivot.index.max()],
            cmap="magma",
        )
        ax.axhline(-6, color="white", ls="--", lw=0.8)
        ax.axhline(6, color="white", ls="--", lw=0.8)
        ax.set_xlabel("time [s]")
        ax.set_ylabel("x position from tube center [mm]")
        ax.set_title(f"Nu_3D(x,t) heatmap, Re {re:g}")
        fig.colorbar(im, ax=ax, label="Nu_3D_xt")
        fig.tight_layout()
        fig.savefig(OUT_DIR / f"fig03_Nu3D_xt_heatmap_Re{int(re)}.png", dpi=240)
        fig.savefig(OUT_DIR / f"fig03_Nu3D_xt_heatmap_Re{int(re)}.pdf")
        plt.close(fig)

    readme = f"""# 00_fullNu3D_xt

This folder contains the first time-resolved full-3D strip Nusselt dataset.

Definition used here:

`Nu_3D(x,t) = Q_strip(x,t) * D_ref / (A_strip(x,t) * k_air * DeltaT_lm_yz(x,t))`

where:

- `Q_strip(x,t)` is integrated from the full hot tube and fin `wallHeatFlux` VTK surfaces.
- `A_strip(x,t)` is the corresponding hot-surface area in each 1 mm x-strip.
- `T_bulk_left/right_yz(x,t)` is computed from full y-z cut planes as
  `integral(rho Ux T dA) / integral(rho Ux dA)`, using positive `Ux`.
- `DeltaT_lm_yz` is the logarithmic wall-to-air temperature difference between the left and right strip boundaries.

Settings:

- strip width: `{DX_M * 1000:g} mm`
- time window: 8-10 s for all cases
- time sampling: all available volume-field snapshots with matching hot-surface files; 26 snapshots per Re in the current dataset
- wall temperature: `{T_WALL_K:g} K`
- reference diameter: `{D_REF_M:g} m`
- air conductivity: `{K_AIR_W_MK:g} W/(m K)`

Outputs:

- `fullNu3D_xt_time_resolved.csv`: main `x,t` dataset.
- `fullNu3D_xt_time_averaged_by_x.csv`: time-mean profile by strip.
- `fullNu3D_xt_summary_by_Re.csv`: scalar summary by Reynolds number.
- `fig01_Nu3D_xt_profiles_time_mean`: x-profiles with temporal standard deviation.
- `fig02_Nu3D_xt_time_traces_selected_strips`: selected time traces.
- `fig03_Nu3D_xt_heatmap_Re*`: x-time heatmaps for shedding cases.

Important note:

Tube/fins split columns use the same local y-z bulk temperature for a strip. This is physically defensible for air-side local Nu, but it is not a separate wall-temperature field for tube and fins.
"""
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    edges = discover_edges_from_surfaces()
    dict_path = write_cutplane_dict(edges)
    all_rows: list[dict] = []
    for case in CASES:
        times = selected_surface_times(case)
        print(f"{case['case']}: {len(times)} time frames, {len(edges)} y-z cut planes")
        ensure_cutplanes(case, times, edges, dict_path)
        all_rows.extend(compute_case(case, edges))
    write_csv(all_rows, OUT_DIR / "fullNu3D_xt_time_resolved.csv")
    df = pd.DataFrame(all_rows)
    make_outputs(df)
    print(f"Wrote {len(all_rows)} rows to {OUT_DIR}")


if __name__ == "__main__":
    main()
