from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import pandas as pd
from scipy.interpolate import griddata


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/008_U_T_z_slices"
RAW_DIR = OUT_DIR / "raw_vtk"
FIG_DIR = OUT_DIR / "figures"
CSV_DIR = OUT_DIR / "csv"

for path in (OUT_DIR, RAW_DIR, FIG_DIR, CSV_DIR):
    path.mkdir(parents=True, exist_ok=True)


CASES = [
    {"Re": 150, "case": "run013_re150", "path": Path("/home/hexmachina/of_runs/V4b_3D_run013_re150_production")},
    {"Re": 159, "case": "run018_re159", "path": Path("/home/hexmachina/of_runs/V4b_3D_run018_re159_production")},
    {"Re": 160, "case": "run015_re160", "path": Path("/home/hexmachina/of_runs/V4b_3D_run015_re160_production")},
    {"Re": 200, "case": "run008_re200", "path": Path("/home/hexmachina/of_runs/V4b_3D_run008")},
]

TIME = "10"
Z_MIN = -0.006
Z_MAX = 0.006
Z_PLANES = [
    {"name": "z20", "fraction": 0.20, "z": Z_MIN + 0.20 * (Z_MAX - Z_MIN), "label": "1/5 gap, z=-3.6 mm"},
    {"name": "z50", "fraction": 0.50, "z": Z_MIN + 0.50 * (Z_MAX - Z_MIN), "label": "mid-gap, z=0.0 mm"},
    {"name": "z80", "fraction": 0.80, "z": Z_MIN + 0.80 * (Z_MAX - Z_MIN), "label": "4/5 gap, z=+3.6 mm"},
]


def run_bash(command: str, cwd: Path | None = None) -> None:
    full = f"source /opt/openfoam13/etc/bashrc; {command}"
    subprocess.run(["bash", "-lc", full], cwd=str(cwd) if cwd else None, check=True)


def n_processors(case_dir: Path) -> int:
    return len([p for p in case_dir.iterdir() if p.is_dir() and p.name.startswith("processor")])


def write_slice_dict() -> Path:
    dict_path = OUT_DIR / "z_slices_functions"
    lines = [
        "FoamFile",
        "{",
        "    format      ascii;",
        "    class       dictionary;",
        "    object      functions;",
        "}",
        "",
        "zSlices",
        "{",
        "    type                surfaces;",
        "    libs                (\"libsampling.so\");",
        "    executeControl      timeStep;",
        "    writeControl        timeStep;",
        "    writeInterval       1;",
        "    surfaceFormat       vtk;",
        "    fields              (U T Q Lambda2);",
        "    interpolationScheme cellPoint;",
        "    surfaces",
        "    {",
    ]
    for plane in Z_PLANES:
        lines.extend(
            [
                f"        {plane['name']}",
                "        {",
                "            type        cutPlane;",
                "            interpolate true;",
                "            planeType   pointAndNormal;",
                f"            point       (0 0 {plane['z']:.9g});",
                "            normal      (0 0 1);",
                "        }",
            ]
        )
    lines.extend(["    }", "}", ""])
    dict_path.write_text("\n".join(lines), encoding="ascii")
    return dict_path


def ensure_slices(case: dict, dict_path: Path) -> None:
    case_dir = case["path"]
    expected = [case_dir / "postProcessing" / "zSlices" / TIME / f"{plane['name']}.vtk" for plane in Z_PLANES]
    if all(path.exists() and vtk_has_fields(path, ["U", "T", "Q", "Lambda2"]) for path in expected):
        return
    ensure_vortex_fields(case)
    shutil.rmtree(case_dir / "postProcessing" / "zSlices" / TIME, ignore_errors=True)
    nproc = n_processors(case_dir)
    if nproc <= 0:
        raise RuntimeError(f"No processor directories found in {case_dir}")
    cmd = (
        f"cd {case_dir}; "
        f"mpirun --oversubscribe -np {nproc} postProcess -parallel "
        f"-dict {dict_path} -time {TIME}"
    )
    run_bash(cmd, cwd=case_dir)


def vtk_has_fields(path: Path, names: list[str]) -> bool:
    if not path.exists():
        return False
    text = path.read_text(errors="ignore")
    return all(f" {name} " in text or f"\n{name} " in text for name in names)


def ensure_vortex_fields(case: dict) -> None:
    case_dir = case["path"]
    nproc = n_processors(case_dir)
    q_proc = case_dir / "processor0" / TIME / "Q"
    lambda_proc = case_dir / "processor0" / TIME / "Lambda2"
    if q_proc.exists() and lambda_proc.exists():
        return
    if nproc <= 0:
        raise RuntimeError(f"No processor directories found in {case_dir}")
    cmd = f"cd {case_dir}; mpirun --oversubscribe -np {nproc} postProcess -parallel -funcs '(Q Lambda2)' -time {TIME}"
    run_bash(cmd, cwd=case_dir)


def copy_slices(case: dict) -> list[Path]:
    copied: list[Path] = []
    for plane in Z_PLANES:
        src = case["path"] / "postProcessing" / "zSlices" / TIME / f"{plane['name']}.vtk"
        dst = RAW_DIR / f"Re{case['Re']}_{plane['name']}_t{TIME}.vtk"
        shutil.copy2(src, dst)
        copied.append(dst)
    return copied


def read_vtk_polydata(path: Path) -> tuple[np.ndarray, list[list[int]], dict[str, np.ndarray]]:
    tokens = path.read_text(errors="ignore").split()

    i = tokens.index("POINTS")
    n_points = int(tokens[i + 1])
    start = i + 3
    points = np.asarray([float(v) for v in tokens[start : start + 3 * n_points]], dtype=float).reshape(n_points, 3)

    i = tokens.index("POLYGONS")
    n_polys = int(tokens[i + 1])
    total = int(tokens[i + 2])
    raw = [int(float(v)) for v in tokens[i + 3 : i + 3 + total]]
    polygons: list[list[int]] = []
    j = 0
    for _ in range(n_polys):
        n = raw[j]
        polygons.append(raw[j + 1 : j + 1 + n])
        j += n + 1

    fields: dict[str, np.ndarray] = {}
    if "POINT_DATA" not in tokens:
        return points, polygons, fields
    i = tokens.index("POINT_DATA") + 2
    while i < len(tokens):
        key = tokens[i]
        if key == "FIELD":
            n_fields = int(tokens[i + 2])
            i += 3
            for _ in range(n_fields):
                name = tokens[i]
                ncomp = int(tokens[i + 1])
                ntuples = int(tokens[i + 2])
                start = i + 4
                arr = np.asarray([float(v) for v in tokens[start : start + ncomp * ntuples]], dtype=float)
                arr = arr.reshape(ntuples, ncomp)
                fields[name] = arr[:, 0] if ncomp == 1 else arr
                i = start + ncomp * ntuples
        elif key == "SCALARS":
            name = tokens[i + 1]
            ncomp = 1
            if tokens[i + 3] != "LOOKUP_TABLE":
                ncomp = int(tokens[i + 3])
                i += 1
            start = i + 5
            arr = np.asarray([float(v) for v in tokens[start : start + ncomp * n_points]], dtype=float)
            arr = arr.reshape(n_points, ncomp)
            fields[name] = arr[:, 0] if ncomp == 1 else arr
            i = start + ncomp * n_points
        elif key == "VECTORS":
            name = tokens[i + 1]
            start = i + 3
            fields[name] = np.asarray([float(v) for v in tokens[start : start + 3 * n_points]], dtype=float).reshape(n_points, 3)
            i = start + 3 * n_points
        else:
            i += 1
    return points, polygons, fields


def triangulate(polygons: list[list[int]]) -> np.ndarray:
    tris: list[list[int]] = []
    for poly in polygons:
        if len(poly) < 3:
            continue
        for k in range(1, len(poly) - 1):
            tris.append([poly[0], poly[k], poly[k + 1]])
    return np.asarray(tris, dtype=int)


def export_csv(case: dict, plane: dict, vtk_path: Path) -> pd.DataFrame:
    points, polygons, fields = read_vtk_polydata(vtk_path)
    if "U" not in fields or "T" not in fields:
        raise RuntimeError(f"Missing U/T fields in {vtk_path}")
    u = fields["U"]
    t = fields["T"]
    df = pd.DataFrame(
        {
            "Re": case["Re"],
            "case": case["case"],
            "time_s": float(TIME),
            "plane": plane["name"],
            "z_m": plane["z"],
            "x_m": points[:, 0],
            "y_m": points[:, 1],
            "z_sample_m": points[:, 2],
            "Ux_m_s": u[:, 0],
            "Uy_m_s": u[:, 1],
            "Uz_m_s": u[:, 2],
            "U_mag_m_s": np.linalg.norm(u, axis=1),
            "T_K": t,
            "Q_s2": fields.get("Q", np.full(len(points), np.nan)),
            "Lambda2_s2": fields.get("Lambda2", np.full(len(points), np.nan)),
        }
    )
    df.to_csv(CSV_DIR / f"Re{case['Re']}_{plane['name']}_t{TIME}_points.csv", index=False)
    return df


def grid_plane(df: pd.DataFrame, value_col: str, nx: int = 700, ny: int = 180) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = df["x_m"].to_numpy() * 1000.0
    y = df["y_m"].to_numpy() * 1000.0
    values = df[value_col].to_numpy()
    xi = np.linspace(-38.0, 110.0, nx)
    yi = np.linspace(-16.5, 16.5, ny)
    xx, yy = np.meshgrid(xi, yi)
    zz = griddata((x, y), values, (xx, yy), method="linear")
    return xx, yy, zz


def fill_nearest(df: pd.DataFrame, value_col: str, xx: np.ndarray, yy: np.ndarray, base: np.ndarray) -> np.ndarray:
    x = df["x_m"].to_numpy() * 1000.0
    y = df["y_m"].to_numpy() * 1000.0
    values = df[value_col].to_numpy()
    nearest = griddata((x, y), values, (xx, yy), method="nearest")
    return np.where(np.isfinite(base), base, nearest)


def plot_pair(case: dict, plane: dict, df: pd.DataFrame, u_lim: tuple[float, float], t_lim: tuple[float, float]) -> None:
    xx, yy, u_img = grid_plane(df, "U_mag_m_s")
    _, _, t_img = grid_plane(df, "T_K")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2), constrained_layout=True)
    fig.suptitle(f"Re {case['Re']} | {plane['label']} | t={TIME} s", fontsize=13)

    p0 = axes[0].imshow(u_img, extent=[xx.min(), xx.max(), yy.min(), yy.max()], origin="lower", cmap="viridis", vmin=u_lim[0], vmax=u_lim[1], aspect="auto")
    axes[0].set_title("|U| [m/s]")
    axes[0].set_xlabel("x [mm]")
    axes[0].set_ylabel("y [mm]")
    axes[0].set_aspect("equal", adjustable="box")
    fig.colorbar(p0, ax=axes[0], shrink=0.92)

    p1 = axes[1].imshow(t_img, extent=[xx.min(), xx.max(), yy.min(), yy.max()], origin="lower", cmap="inferno", vmin=t_lim[0], vmax=t_lim[1], aspect="auto")
    axes[1].set_title("T [K]")
    axes[1].set_xlabel("x [mm]")
    axes[1].set_ylabel("y [mm]")
    axes[1].set_aspect("equal", adjustable="box")
    fig.colorbar(p1, ax=axes[1], shrink=0.92)

    for ax in axes:
        ax.set_xlim(-38, 110)
        ax.set_ylim(-16.5, 16.5)
        ax.grid(alpha=0.18, linewidth=0.4)

    out_base = FIG_DIR / f"Re{case['Re']}_{plane['name']}_Umag_T_t{TIME}"
    fig.savefig(out_base.with_suffix(".png"), dpi=220)
    fig.savefig(out_base.with_suffix(".pdf"))
    plt.close(fig)


def plot_streamlines(case: dict, plane: dict, df: pd.DataFrame, u_lim: tuple[float, float]) -> None:
    xx, yy, ux = grid_plane(df, "Ux_m_s")
    _, _, uy = grid_plane(df, "Uy_m_s")
    _, _, umag = grid_plane(df, "U_mag_m_s")
    ux = fill_nearest(df, "Ux_m_s", xx, yy, ux)
    uy = fill_nearest(df, "Uy_m_s", xx, yy, uy)

    fig, ax = plt.subplots(figsize=(8.8, 4.2), constrained_layout=True)
    im = ax.imshow(umag, extent=[xx.min(), xx.max(), yy.min(), yy.max()], origin="lower", cmap="viridis", vmin=u_lim[0], vmax=u_lim[1], aspect="auto")
    ax.streamplot(xx[0, :], yy[:, 0], ux, uy, color="white", density=2.0, linewidth=0.55, arrowsize=0.65)
    ax.set_title(f"Velocity streamlines | Re {case['Re']} | {plane['label']} | t={TIME} s")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_xlim(-38, 110)
    ax.set_ylim(-16.5, 16.5)
    ax.set_aspect("equal", adjustable="box")
    fig.colorbar(im, ax=ax, shrink=0.9, label="|U| [m/s]")
    out_base = FIG_DIR / f"Re{case['Re']}_{plane['name']}_streamlines_Umag_t{TIME}"
    fig.savefig(out_base.with_suffix(".png"), dpi=220)
    fig.savefig(out_base.with_suffix(".pdf"))
    plt.close(fig)


def plot_vortex_criteria(case: dict, plane: dict, df: pd.DataFrame, q_lim: float, lambda_lim: float) -> None:
    xx, yy, q_img = grid_plane(df, "Q_s2")
    _, _, lambda_img = grid_plane(df, "Lambda2_s2")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2), constrained_layout=True)
    fig.suptitle(f"Vortex criteria | Re {case['Re']} | {plane['label']} | t={TIME} s", fontsize=13)

    q_norm = TwoSlopeNorm(vcenter=0.0, vmin=-q_lim, vmax=q_lim)
    p0 = axes[0].imshow(q_img, extent=[xx.min(), xx.max(), yy.min(), yy.max()], origin="lower", cmap="coolwarm", norm=q_norm, aspect="auto")
    axes[0].contour(xx, yy, q_img, levels=[0.0], colors="black", linewidths=0.45, alpha=0.65)
    axes[0].set_title("Q criterion [1/s²], Q>0 vortex-dominated")
    axes[0].set_xlabel("x [mm]")
    axes[0].set_ylabel("y [mm]")
    fig.colorbar(p0, ax=axes[0], shrink=0.92)

    l_norm = TwoSlopeNorm(vcenter=0.0, vmin=-lambda_lim, vmax=lambda_lim)
    p1 = axes[1].imshow(lambda_img, extent=[xx.min(), xx.max(), yy.min(), yy.max()], origin="lower", cmap="coolwarm_r", norm=l_norm, aspect="auto")
    axes[1].contour(xx, yy, lambda_img, levels=[0.0], colors="black", linewidths=0.45, alpha=0.65)
    axes[1].set_title("Lambda2 [1/s²], Lambda2<0 vortex core")
    axes[1].set_xlabel("x [mm]")
    axes[1].set_ylabel("y [mm]")
    fig.colorbar(p1, ax=axes[1], shrink=0.92)

    for ax in axes:
        ax.set_xlim(-38, 110)
        ax.set_ylim(-16.5, 16.5)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=0.12, linewidth=0.35)

    out_base = FIG_DIR / f"Re{case['Re']}_{plane['name']}_Q_Lambda2_t{TIME}"
    fig.savefig(out_base.with_suffix(".png"), dpi=220)
    fig.savefig(out_base.with_suffix(".pdf"))
    plt.close(fig)


def plot_overview(all_rows: pd.DataFrame) -> None:
    fig, axes = plt.subplots(len(Z_PLANES), len(CASES), figsize=(14.8, 8.2), sharex=True, sharey=True, constrained_layout=True)
    vmin = float(all_rows["U_mag_m_s"].quantile(0.01))
    vmax = float(all_rows["U_mag_m_s"].quantile(0.99))
    for r, plane in enumerate(Z_PLANES):
        for c, case in enumerate(CASES):
            df = all_rows[(all_rows["Re"] == case["Re"]) & (all_rows["plane"] == plane["name"])]
            ax = axes[r, c]
            xx, yy, img = grid_plane(df, "U_mag_m_s", nx=360, ny=90)
            pc = ax.imshow(img, extent=[xx.min(), xx.max(), yy.min(), yy.max()], origin="lower", cmap="viridis", vmin=vmin, vmax=vmax, aspect="auto")
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlim(-38, 110)
            ax.set_ylim(-16.5, 16.5)
            ax.set_title(f"Re {case['Re']}" if r == 0 else "")
            if c == 0:
                ax.set_ylabel(f"{plane['name']}\ny [mm]")
            if r == len(Z_PLANES) - 1:
                ax.set_xlabel("x [mm]")
    fig.suptitle("|U| on z-slices, common color scale", fontsize=14)
    fig.colorbar(pc, ax=axes.ravel().tolist(), shrink=0.85, label="|U| [m/s]")
    fig.savefig(FIG_DIR / f"overview_Umag_all_Re_t{TIME}.png", dpi=220)
    fig.savefig(FIG_DIR / f"overview_Umag_all_Re_t{TIME}.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(len(Z_PLANES), len(CASES), figsize=(14.8, 8.2), sharex=True, sharey=True, constrained_layout=True)
    vmin = float(all_rows["T_K"].quantile(0.01))
    vmax = float(all_rows["T_K"].quantile(0.99))
    for r, plane in enumerate(Z_PLANES):
        for c, case in enumerate(CASES):
            df = all_rows[(all_rows["Re"] == case["Re"]) & (all_rows["plane"] == plane["name"])]
            ax = axes[r, c]
            xx, yy, img = grid_plane(df, "T_K", nx=360, ny=90)
            pc = ax.imshow(img, extent=[xx.min(), xx.max(), yy.min(), yy.max()], origin="lower", cmap="inferno", vmin=vmin, vmax=vmax, aspect="auto")
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlim(-38, 110)
            ax.set_ylim(-16.5, 16.5)
            ax.set_title(f"Re {case['Re']}" if r == 0 else "")
            if c == 0:
                ax.set_ylabel(f"{plane['name']}\ny [mm]")
            if r == len(Z_PLANES) - 1:
                ax.set_xlabel("x [mm]")
    fig.suptitle("T on z-slices, common color scale", fontsize=14)
    fig.colorbar(pc, ax=axes.ravel().tolist(), shrink=0.85, label="T [K]")
    fig.savefig(FIG_DIR / f"overview_T_all_Re_t{TIME}.png", dpi=220)
    fig.savefig(FIG_DIR / f"overview_T_all_Re_t{TIME}.pdf")
    plt.close(fig)


def write_readme(summary: pd.DataFrame) -> None:
    lines = [
        "# 008 U and T z-slices",
        "",
        "Purpose: visual comparison of velocity magnitude and temperature fields on three streamwise planes between the heated fin walls.",
        "",
        "Planes:",
        "",
        "| plane | fraction from z_min | z [m] | z [mm] |",
        "|---|---:|---:|---:|",
    ]
    for plane in Z_PLANES:
        lines.append(f"| {plane['name']} | {plane['fraction']:.2f} | {plane['z']:.6f} | {plane['z']*1000:.3f} |")
    lines.extend(
        [
            "",
            f"Source time: `t = {TIME} s` from the previously completed production runs.",
            "",
            "Generated outputs:",
            "",
            "- `raw_vtk/`: copied OpenFOAM VTK cut planes.",
            "- `csv/`: pointwise x-y-z, Ux, Uy, Uz, |U| and T for every Re/plane.",
            "- `figures/`: individual and overview plots.",
            "",
            "Summary statistics:",
            "",
            "| Re | plane | U_mean [m/s] | U_max [m/s] | T_mean [K] | T_min [K] | T_max [K] |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in summary.itertuples(index=False):
        lines.append(
            f"| {row.Re:.0f} | {row.plane} | {row.U_mean_m_s:.5f} | {row.U_max_m_s:.5f} | "
            f"{row.T_mean_K:.3f} | {row.T_min_K:.3f} | {row.T_max_K:.3f} |"
        )
    lines.append("")
    (OUT_DIR / "README.md").write_text("\n".join(lines), encoding="ascii")


def main() -> None:
    dict_path = write_slice_dict()
    rows = []
    copied_paths: dict[tuple[int, str], Path] = {}

    for case in CASES:
        ensure_slices(case, dict_path)
        copied = copy_slices(case)
        for plane, vtk_path in zip(Z_PLANES, copied, strict=True):
            df = export_csv(case, plane, vtk_path)
            rows.append(df)
            copied_paths[(case["Re"], plane["name"])] = vtk_path

    all_rows = pd.concat(rows, ignore_index=True)
    all_rows.to_csv(CSV_DIR / f"all_Re_z_slices_t{TIME}_points.csv", index=False)

    summary = (
        all_rows.groupby(["Re", "case", "plane", "z_m"], as_index=False)
        .agg(
            U_mean_m_s=("U_mag_m_s", "mean"),
            U_max_m_s=("U_mag_m_s", "max"),
            T_mean_K=("T_K", "mean"),
            T_min_K=("T_K", "min"),
            T_max_K=("T_K", "max"),
            Q_p95_s2=("Q_s2", lambda s: float(np.nanpercentile(s, 95))),
            Lambda2_p05_s2=("Lambda2_s2", lambda s: float(np.nanpercentile(s, 5))),
        )
        .sort_values(["Re", "z_m"])
    )
    summary.to_csv(CSV_DIR / f"summary_z_slices_t{TIME}.csv", index=False)

    u_lim = (float(all_rows["U_mag_m_s"].quantile(0.01)), float(all_rows["U_mag_m_s"].quantile(0.99)))
    t_lim = (float(all_rows["T_K"].quantile(0.01)), float(all_rows["T_K"].quantile(0.99)))
    q_lim = float(np.nanpercentile(np.abs(all_rows["Q_s2"].to_numpy()), 98))
    lambda_lim = float(np.nanpercentile(np.abs(all_rows["Lambda2_s2"].to_numpy()), 98))
    for case in CASES:
        for plane in Z_PLANES:
            df = all_rows[(all_rows["Re"] == case["Re"]) & (all_rows["plane"] == plane["name"])]
            plot_pair(case, plane, df, u_lim, t_lim)
            plot_streamlines(case, plane, df, u_lim)
            plot_vortex_criteria(case, plane, df, q_lim, lambda_lim)

    plot_overview(all_rows)
    write_readme(summary)


if __name__ == "__main__":
    main()
