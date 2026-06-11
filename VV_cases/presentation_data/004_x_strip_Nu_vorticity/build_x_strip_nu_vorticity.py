from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
SOURCE_DIR = REPO_DIR / "VV_cases/presentation_data/002_Nu_and_vorticity"
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/004_x_strip_Nu_vorticity"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SOURCE_DIR))
from build_stripwise_heat_figures import CASES, DX, PATCH_FILES, polygon_area, read_vtk_polydata, time_dirs  # noqa: E402


D_REF = 0.012
R_REF = 0.5 * D_REF
NEAR_WALL_THICKNESS = 0.0015
T_WALL = 343.15
K_AIR = 0.028
TIME_STRIDE = 10
AIR_UX_EPS = 1.0e-7


def write_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def discover_x_range() -> tuple[float, float]:
    xs = []
    for case in CASES:
        t0, t1 = case["window"]
        for surf in ["hot_tube_surface", "hot_fin_surface"]:
            names = time_dirs(case["path"], surf, t0, t1)
            if not names:
                continue
            time = names[len(names) // 2]
            files = [
                case["path"] / "postProcessing" / tpl.format(time=time)
                for group in PATCH_FILES.values()
                for tpl in group
            ]
            for f in files:
                if f.exists():
                    pts, _, _ = read_vtk_polydata(f)
                    xs.extend([float(pts[:, 0].min()), float(pts[:, 0].max())])
    return float(np.floor(min(xs) / DX) * DX), float(np.ceil(max(xs) / DX) * DX)


def lmtd(delta_in: float, delta_out: float) -> float:
    delta_in = max(delta_in, 1.0e-9)
    delta_out = max(delta_out, 1.0e-9)
    if abs(delta_in - delta_out) < 1.0e-8:
        return 0.5 * (delta_in + delta_out)
    ratio = delta_in / delta_out
    if ratio <= 0:
        return 0.5 * (delta_in + delta_out)
    return (delta_in - delta_out) / math.log(ratio)


def surface_q_area_for_vtk(path: Path, edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    points, polygons, fields = read_vtk_polydata(path)
    q = fields["wallHeatFlux"]
    q_sum = np.zeros(len(edges) - 1)
    area_sum = np.zeros(len(edges) - 1)
    for poly in polygons:
        idx = np.asarray(poly, dtype=int)
        verts = points[idx]
        x_centroid = float(verts[:, 0].mean())
        bin_idx = int(np.searchsorted(edges, x_centroid, side="right") - 1)
        if bin_idx < 0 or bin_idx >= len(q_sum):
            continue
        area = polygon_area(verts)
        q_sum[bin_idx] += float(q[idx].mean()) * area
        area_sum[bin_idx] += area
    return q_sum, area_sum


def triangle_gradient_xy(xy: np.ndarray, values: np.ndarray) -> tuple[float, float] | None:
    mat = np.column_stack([np.ones(3), xy[:, 0], xy[:, 1]])
    try:
        coeff = np.linalg.solve(mat, values)
    except np.linalg.LinAlgError:
        return None
    return float(coeff[1]), float(coeff[2])


def midspan_metrics_for_vtk(path: Path, edges: np.ndarray) -> tuple[np.ndarray, ...]:
    points, polygons, fields = read_vtk_polydata(path)
    temp = fields["T"]
    vel = fields["U"]
    n = len(edges) - 1
    t_weighted = np.zeros(n)
    flux_weight = np.zeros(n)
    omega_weighted = np.zeros(n)
    omega_area = np.zeros(n)
    qcrit_pos_weighted = np.zeros(n)
    lambda_ci_weighted = np.zeros(n)
    vortex_area = np.zeros(n)
    near_wall_omega_weighted = np.zeros(n)
    near_wall_qcrit_weighted = np.zeros(n)
    near_wall_lambda_ci_weighted = np.zeros(n)
    near_wall_area = np.zeros(n)
    wake_omega_weighted = np.zeros(n)
    wake_qcrit_weighted = np.zeros(n)
    wake_lambda_ci_weighted = np.zeros(n)
    wake_area = np.zeros(n)
    bulk_omega_weighted = np.zeros(n)
    bulk_qcrit_weighted = np.zeros(n)
    bulk_lambda_ci_weighted = np.zeros(n)
    bulk_area = np.zeros(n)

    for poly in polygons:
        if len(poly) < 3:
            continue
        idx_full = np.asarray(poly, dtype=int)
        verts_full = points[idx_full]
        x_centroid = float(verts_full[:, 0].mean())
        bin_idx = int(np.searchsorted(edges, x_centroid, side="right") - 1)
        if bin_idx < 0 or bin_idx >= n:
            continue

        area = polygon_area(verts_full)
        ux_mean = float(vel[idx_full, 0].mean())
        if ux_mean > AIR_UX_EPS:
            w = ux_mean * area
            t_weighted[bin_idx] += float(temp[idx_full].mean()) * w
            flux_weight[bin_idx] += w

        # Estimate local spanwise vorticity on the z=0 plane.
        for i in range(1, len(idx_full) - 1):
            tri_idx = idx_full[[0, i, i + 1]]
            xy = points[tri_idx, :2]
            tri_area = polygon_area(points[tri_idx])
            if tri_area <= 0:
                continue
            grad_ux = triangle_gradient_xy(xy, vel[tri_idx, 0])
            grad_uy = triangle_gradient_xy(xy, vel[tri_idx, 1])
            if grad_ux is None or grad_uy is None:
                continue
            dux_dy = grad_ux[1]
            dux_dx = grad_ux[0]
            duy_dx = grad_uy[0]
            duy_dy = grad_uy[1]
            omega_z = duy_dx - dux_dy
            omega_weighted[bin_idx] += abs(omega_z) * tri_area
            omega_area[bin_idx] += tri_area

            grad = np.asarray([[dux_dx, dux_dy], [duy_dx, duy_dy]], dtype=float)
            strain = 0.5 * (grad + grad.T)
            rotation = 0.5 * (grad - grad.T)
            qcrit = 0.5 * (float(np.sum(rotation * rotation)) - float(np.sum(strain * strain)))
            eig = np.linalg.eigvals(grad)
            lambda_ci = float(np.max(np.abs(np.imag(eig))))
            qcrit_pos_weighted[bin_idx] += max(qcrit, 0.0) * tri_area
            lambda_ci_weighted[bin_idx] += lambda_ci * tri_area
            vortex_area[bin_idx] += tri_area

            centroid = points[tri_idx, :2].mean(axis=0)
            radius = float(np.linalg.norm(centroid))
            qcrit_pos = max(qcrit, 0.0)
            is_near_wall = (R_REF * 0.98) <= radius <= (R_REF + NEAR_WALL_THICKNESS)
            is_wake = centroid[0] >= R_REF and radius > (R_REF + NEAR_WALL_THICKNESS)
            if is_near_wall:
                near_wall_omega_weighted[bin_idx] += abs(omega_z) * tri_area
                near_wall_qcrit_weighted[bin_idx] += qcrit_pos * tri_area
                near_wall_lambda_ci_weighted[bin_idx] += lambda_ci * tri_area
                near_wall_area[bin_idx] += tri_area
            else:
                bulk_omega_weighted[bin_idx] += abs(omega_z) * tri_area
                bulk_qcrit_weighted[bin_idx] += qcrit_pos * tri_area
                bulk_lambda_ci_weighted[bin_idx] += lambda_ci * tri_area
                bulk_area[bin_idx] += tri_area
            if is_wake:
                wake_omega_weighted[bin_idx] += abs(omega_z) * tri_area
                wake_qcrit_weighted[bin_idx] += qcrit_pos * tri_area
                wake_lambda_ci_weighted[bin_idx] += lambda_ci * tri_area
                wake_area[bin_idx] += tri_area

    t_bulk = np.divide(t_weighted, flux_weight, out=np.full(n, np.nan), where=flux_weight > 0)
    omega_mean = np.divide(omega_weighted, omega_area, out=np.full(n, np.nan), where=omega_area > 0)
    qcrit_pos_mean = np.divide(qcrit_pos_weighted, vortex_area, out=np.full(n, np.nan), where=vortex_area > 0)
    lambda_ci_mean = np.divide(lambda_ci_weighted, vortex_area, out=np.full(n, np.nan), where=vortex_area > 0)
    near_wall_omega = np.divide(near_wall_omega_weighted, near_wall_area, out=np.full(n, np.nan), where=near_wall_area > 0)
    near_wall_qcrit = np.divide(near_wall_qcrit_weighted, near_wall_area, out=np.full(n, np.nan), where=near_wall_area > 0)
    near_wall_lambda_ci = np.divide(
        near_wall_lambda_ci_weighted, near_wall_area, out=np.full(n, np.nan), where=near_wall_area > 0
    )
    wake_omega = np.divide(wake_omega_weighted, wake_area, out=np.full(n, np.nan), where=wake_area > 0)
    wake_qcrit = np.divide(wake_qcrit_weighted, wake_area, out=np.full(n, np.nan), where=wake_area > 0)
    wake_lambda_ci = np.divide(wake_lambda_ci_weighted, wake_area, out=np.full(n, np.nan), where=wake_area > 0)
    bulk_omega = np.divide(bulk_omega_weighted, bulk_area, out=np.full(n, np.nan), where=bulk_area > 0)
    bulk_qcrit = np.divide(bulk_qcrit_weighted, bulk_area, out=np.full(n, np.nan), where=bulk_area > 0)
    bulk_lambda_ci = np.divide(bulk_lambda_ci_weighted, bulk_area, out=np.full(n, np.nan), where=bulk_area > 0)
    return (
        t_bulk,
        omega_mean,
        qcrit_pos_mean,
        lambda_ci_mean,
        near_wall_omega,
        near_wall_qcrit,
        near_wall_lambda_ci,
        wake_omega,
        wake_qcrit,
        wake_lambda_ci,
        bulk_omega,
        bulk_qcrit,
        bulk_lambda_ci,
    )


def case_u_ref_from_edges(edges: np.ndarray) -> float:
    # Fallback only; actual U_ref is read from forceCoeffs header per case where possible.
    return 0.25


def read_u_inf(case_dir: Path) -> float:
    coeff = case_dir / "postProcessing/forceCoeffs/0/forceCoeffs.dat"
    if coeff.exists():
        for line in coeff.read_text(errors="ignore").splitlines():
            if "magUInf" in line:
                try:
                    return float(line.split(":")[-1])
                except ValueError:
                    pass
    return 0.25


def summarize_case(case: dict, edges: np.ndarray) -> list[dict]:
    t0, t1 = case["window"]
    times = time_dirs(case["path"], "hot_tube_surface", t0, t1)[:: max(1, TIME_STRIDE // 10)]
    if not times:
        raise RuntimeError(f"No surface times for {case['case']}")

    q_tube_acc = []
    a_tube_acc = []
    q_fins_acc = []
    a_fins_acc = []
    t_bulk_acc = []
    omega_acc = []
    qcrit_acc = []
    lambda_ci_acc = []
    near_wall_omega_acc = []
    near_wall_qcrit_acc = []
    near_wall_lambda_ci_acc = []
    wake_omega_acc = []
    wake_qcrit_acc = []
    wake_lambda_ci_acc = []
    bulk_omega_acc = []
    bulk_qcrit_acc = []
    bulk_lambda_ci_acc = []
    u_ref = read_u_inf(case["path"])

    for time in times:
        q_tube = np.zeros(len(edges) - 1)
        a_tube = np.zeros(len(edges) - 1)
        q_fins = np.zeros(len(edges) - 1)
        a_fins = np.zeros(len(edges) - 1)
        for tpl in PATCH_FILES["tube"]:
            f = case["path"] / "postProcessing" / tpl.format(time=time)
            if f.exists():
                q_part, a_part = surface_q_area_for_vtk(f, edges)
                q_tube += q_part
                a_tube += a_part
        for tpl in PATCH_FILES["fins"]:
            f = case["path"] / "postProcessing" / tpl.format(time=time)
            if f.exists():
                q_part, a_part = surface_q_area_for_vtk(f, edges)
                q_fins += q_part
                a_fins += a_part
        mid = case["path"] / "postProcessing/midspan_z0" / time / "z0.vtk"
        if mid.exists():
            (
                t_bulk,
                omega_mean,
                qcrit_pos_mean,
                lambda_ci_mean,
                near_wall_omega,
                near_wall_qcrit,
                near_wall_lambda_ci,
                wake_omega,
                wake_qcrit,
                wake_lambda_ci,
                bulk_omega,
                bulk_qcrit,
                bulk_lambda_ci,
            ) = midspan_metrics_for_vtk(mid, edges)
            t_bulk_acc.append(t_bulk)
            omega_acc.append(omega_mean)
            qcrit_acc.append(qcrit_pos_mean)
            lambda_ci_acc.append(lambda_ci_mean)
            near_wall_omega_acc.append(near_wall_omega)
            near_wall_qcrit_acc.append(near_wall_qcrit)
            near_wall_lambda_ci_acc.append(near_wall_lambda_ci)
            wake_omega_acc.append(wake_omega)
            wake_qcrit_acc.append(wake_qcrit)
            wake_lambda_ci_acc.append(wake_lambda_ci)
            bulk_omega_acc.append(bulk_omega)
            bulk_qcrit_acc.append(bulk_qcrit)
            bulk_lambda_ci_acc.append(bulk_lambda_ci)
        q_tube_acc.append(q_tube)
        a_tube_acc.append(a_tube)
        q_fins_acc.append(q_fins)
        a_fins_acc.append(a_fins)

    q_tube_mean = np.vstack(q_tube_acc).mean(axis=0)
    q_fins_mean = np.vstack(q_fins_acc).mean(axis=0)
    a_tube_mean = np.vstack(a_tube_acc).mean(axis=0)
    a_fins_mean = np.vstack(a_fins_acc).mean(axis=0)
    t_bulk_mean = np.nanmean(np.vstack(t_bulk_acc), axis=0)
    omega_mean = np.nanmean(np.vstack(omega_acc), axis=0)
    qcrit_pos_mean = np.nanmean(np.vstack(qcrit_acc), axis=0)
    lambda_ci_mean = np.nanmean(np.vstack(lambda_ci_acc), axis=0)
    near_wall_omega_mean = np.nanmean(np.vstack(near_wall_omega_acc), axis=0)
    near_wall_qcrit_mean = np.nanmean(np.vstack(near_wall_qcrit_acc), axis=0)
    near_wall_lambda_ci_mean = np.nanmean(np.vstack(near_wall_lambda_ci_acc), axis=0)
    wake_omega_mean = np.nanmean(np.vstack(wake_omega_acc), axis=0)
    wake_qcrit_mean = np.nanmean(np.vstack(wake_qcrit_acc), axis=0)
    wake_lambda_ci_mean = np.nanmean(np.vstack(wake_lambda_ci_acc), axis=0)
    bulk_omega_mean = np.nanmean(np.vstack(bulk_omega_acc), axis=0)
    bulk_qcrit_mean = np.nanmean(np.vstack(bulk_qcrit_acc), axis=0)
    bulk_lambda_ci_mean = np.nanmean(np.vstack(bulk_lambda_ci_acc), axis=0)
    omega_nd = omega_mean * D_REF / max(u_ref, 1.0e-12)
    qcrit_nd = qcrit_pos_mean * D_REF * D_REF / max(u_ref * u_ref, 1.0e-12)
    lambda_ci_nd = lambda_ci_mean * D_REF / max(u_ref, 1.0e-12)
    near_wall_omega_nd = near_wall_omega_mean * D_REF / max(u_ref, 1.0e-12)
    near_wall_qcrit_nd = near_wall_qcrit_mean * D_REF * D_REF / max(u_ref * u_ref, 1.0e-12)
    near_wall_lambda_ci_nd = near_wall_lambda_ci_mean * D_REF / max(u_ref, 1.0e-12)
    wake_omega_nd = wake_omega_mean * D_REF / max(u_ref, 1.0e-12)
    wake_qcrit_nd = wake_qcrit_mean * D_REF * D_REF / max(u_ref * u_ref, 1.0e-12)
    wake_lambda_ci_nd = wake_lambda_ci_mean * D_REF / max(u_ref, 1.0e-12)
    bulk_omega_nd = bulk_omega_mean * D_REF / max(u_ref, 1.0e-12)
    bulk_qcrit_nd = bulk_qcrit_mean * D_REF * D_REF / max(u_ref * u_ref, 1.0e-12)
    bulk_lambda_ci_nd = bulk_lambda_ci_mean * D_REF / max(u_ref, 1.0e-12)

    # Boundary temperatures are approximated from neighboring strip-center bulk values.
    t_in = np.empty_like(t_bulk_mean)
    t_out = np.empty_like(t_bulk_mean)
    for i in range(len(t_bulk_mean)):
        t_in[i] = t_bulk_mean[i] if i == 0 else 0.5 * (t_bulk_mean[i - 1] + t_bulk_mean[i])
        t_out[i] = t_bulk_mean[i] if i == len(t_bulk_mean) - 1 else 0.5 * (t_bulk_mean[i] + t_bulk_mean[i + 1])

    rows = []
    for i in range(len(edges) - 1):
        q_total = q_tube_mean[i] + q_fins_mean[i]
        area_total = a_tube_mean[i] + a_fins_mean[i]
        delta_t_in = T_WALL - t_in[i]
        delta_t_out = T_WALL - t_out[i]
        delta_t_lm = lmtd(delta_t_in, delta_t_out)
        alpha = q_total / (area_total * delta_t_lm) if area_total > 0 and delta_t_lm > 0 else np.nan
        nu = alpha * D_REF / K_AIR if np.isfinite(alpha) else np.nan
        rows.append(
            {
                "Re": case["Re"],
                "case": case["case"],
                "regime": case["regime"],
                "x_left_mm": edges[i] * 1000,
                "x_right_mm": edges[i + 1] * 1000,
                "x_center_mm": 0.5 * (edges[i] + edges[i + 1]) * 1000,
                "Q_total_strip_W": q_total,
                "Q_tube_strip_W": q_tube_mean[i],
                "Q_fins_strip_W": q_fins_mean[i],
                "A_total_strip_m2": area_total,
                "A_tube_strip_m2": a_tube_mean[i],
                "A_fins_strip_m2": a_fins_mean[i],
                "T_bulk_midspan_center_K": t_bulk_mean[i],
                "T_bulk_in_proxy_K": t_in[i],
                "T_bulk_out_proxy_K": t_out[i],
                "deltaT_lm_proxy_K": delta_t_lm,
                "alpha_strip_W_m2K": alpha,
                "Nu_strip_proxy": nu,
                "omega_z_abs_mean_1_s": omega_mean[i],
                "omega_z_abs_nd": omega_nd[i],
                "Qcriterion_2D_positive_mean_1_s2": qcrit_pos_mean[i],
                "Qcriterion_2D_positive_nd": qcrit_nd[i],
                "lambda_ci_2D_mean_1_s": lambda_ci_mean[i],
                "lambda_ci_2D_nd": lambda_ci_nd[i],
                "near_wall_omega_z_abs_nd": near_wall_omega_nd[i],
                "near_wall_Qcriterion_2D_positive_nd": near_wall_qcrit_nd[i],
                "near_wall_lambda_ci_2D_nd": near_wall_lambda_ci_nd[i],
                "wake_omega_z_abs_nd": wake_omega_nd[i],
                "wake_Qcriterion_2D_positive_nd": wake_qcrit_nd[i],
                "wake_lambda_ci_2D_nd": wake_lambda_ci_nd[i],
                "bulk_without_tube_near_wall_omega_z_abs_nd": bulk_omega_nd[i],
                "bulk_without_tube_near_wall_Qcriterion_2D_positive_nd": bulk_qcrit_nd[i],
                "bulk_without_tube_near_wall_lambda_ci_2D_nd": bulk_lambda_ci_nd[i],
                "U_ref_m_s": u_ref,
                "k_air_W_mK": K_AIR,
                "D_ref_m": D_REF,
                "n_times_used": len(times),
            }
        )
    return rows


def rows_to_grid(rows: list[dict], metric: str) -> tuple[list[float], np.ndarray, np.ndarray]:
    res = sorted({float(r["Re"]) for r in rows})
    xs = np.asarray(sorted({float(r["x_center_mm"]) for r in rows}), dtype=float)
    grid = np.full((len(res), len(xs)), np.nan)
    re_idx = {re: i for i, re in enumerate(res)}
    x_idx = {x: i for i, x in enumerate(xs)}
    for r in rows:
        grid[re_idx[float(r["Re"])], x_idx[float(r["x_center_mm"])]] = float(r[metric])
    return res, xs, grid


def add_tube_markers(ax) -> None:
    ax.axvline(-6, color="0.35", ls="--", lw=0.8)
    ax.axvline(6, color="0.35", ls="--", lw=0.8)


def save_line_plot(xs: np.ndarray, series: dict[str, np.ndarray], ylabel: str, title: str, filename: str) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 4.9))
    cmap = plt.get_cmap("viridis")
    for i, (label, values) in enumerate(series.items()):
        ax.plot(xs, values, lw=2.0, color=cmap(i / max(1, len(series) - 1)), label=label)
    add_tube_markers(ax)
    ax.set_xlabel("x position from tube center [mm], 1 mm strips")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{filename}.png", dpi=220)
    fig.savefig(OUT_DIR / f"{filename}.pdf")
    plt.close(fig)


def zscore(values: np.ndarray) -> np.ndarray:
    values = values.astype(float)
    mean = np.nanmean(values)
    std = np.nanstd(values)
    if not np.isfinite(std) or std < 1.0e-14:
        return values * np.nan
    return (values - mean) / std


def save_nu_proxy_overlay(
    xs: np.ndarray,
    selected: list[float],
    re_idx: dict[float, int],
    nu_excess_by_re: dict[float, np.ndarray],
    proxy_grid: np.ndarray,
    proxy_label: str,
    title: str,
    filename: str,
) -> None:
    fig, axes = plt.subplots(len(selected), 1, figsize=(10.6, 3.25 * len(selected)), sharex=True)
    if len(selected) == 1:
        axes = [axes]
    for ax, re in zip(axes, selected):
        nu_scaled = zscore(nu_excess_by_re[re])
        proxy_scaled = zscore(proxy_grid[re_idx[re], :])
        ax.plot(xs, nu_scaled, color="#1f5f8b", lw=2.1, label="Nu excess, z-score")
        ax.plot(xs, proxy_scaled, color="#e07a5f", lw=1.9, label=f"{proxy_label}, z-score")
        ax.axhline(0, color="0.2", lw=0.8)
        add_tube_markers(ax)
        ax.set_ylabel(f"Re {re:g}\nz-score")
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=2, loc="upper right")
    axes[-1].set_xlabel("x position from tube center [mm], 1 mm strips")
    fig.suptitle(title, y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{filename}.png", dpi=220)
    fig.savefig(OUT_DIR / f"{filename}.pdf")
    plt.close(fig)


def save_nu_proxy_scatter(
    selected: list[float],
    re_idx: dict[float, int],
    nu_excess_by_re: dict[float, np.ndarray],
    proxy_grid: np.ndarray,
    xlabel: str,
    title: str,
    filename: str,
) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 5.5))
    cmap = plt.get_cmap("magma")
    for i, re in enumerate(selected):
        nu_excess = nu_excess_by_re[re]
        proxy = proxy_grid[re_idx[re], :]
        valid = np.isfinite(nu_excess) & np.isfinite(proxy)
        corr = float(np.corrcoef(proxy[valid], nu_excess[valid])[0, 1]) if valid.sum() > 2 else np.nan
        ax.scatter(
            proxy[valid],
            nu_excess[valid],
            s=38,
            alpha=0.82,
            color=cmap(i / max(1, len(selected) - 1)),
            label=f"Re {re:g}, r={corr:.2f}",
        )
    ax.axhline(0, color="0.2", lw=0.8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("local Nu gain / mean Nu gain - 1 [-]")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{filename}.png", dpi=220)
    fig.savefig(OUT_DIR / f"{filename}.pdf")
    plt.close(fig)


def main() -> None:
    xmin, xmax = discover_x_range()
    edges = np.arange(xmin, xmax + 0.5 * DX, DX)
    rows: list[dict] = []
    for case in CASES:
        rows.extend(summarize_case(case, edges))
    write_csv(rows, OUT_DIR / "x_strip_1mm_Nu_vorticity.csv")

    res, xs, nu_grid = rows_to_grid(rows, "Nu_strip_proxy")
    _, _, omega_grid = rows_to_grid(rows, "omega_z_abs_nd")
    _, _, qcrit_grid = rows_to_grid(rows, "Qcriterion_2D_positive_nd")
    _, _, lambda_ci_grid = rows_to_grid(rows, "lambda_ci_2D_nd")
    _, _, near_wall_omega_grid = rows_to_grid(rows, "near_wall_omega_z_abs_nd")
    _, _, near_wall_qcrit_grid = rows_to_grid(rows, "near_wall_Qcriterion_2D_positive_nd")
    _, _, near_wall_lambda_ci_grid = rows_to_grid(rows, "near_wall_lambda_ci_2D_nd")
    _, _, wake_omega_grid = rows_to_grid(rows, "wake_omega_z_abs_nd")
    _, _, wake_qcrit_grid = rows_to_grid(rows, "wake_Qcriterion_2D_positive_nd")
    _, _, wake_lambda_ci_grid = rows_to_grid(rows, "wake_lambda_ci_2D_nd")
    _, _, bulk_omega_grid = rows_to_grid(rows, "bulk_without_tube_near_wall_omega_z_abs_nd")
    _, _, bulk_qcrit_grid = rows_to_grid(rows, "bulk_without_tube_near_wall_Qcriterion_2D_positive_nd")
    _, _, bulk_lambda_ci_grid = rows_to_grid(rows, "bulk_without_tube_near_wall_lambda_ci_2D_nd")
    _, _, q_grid = rows_to_grid(rows, "Q_total_strip_W")
    re_idx = {re: i for i, re in enumerate(res)}

    save_line_plot(
        xs,
        {f"Re {re:g}": nu_grid[re_idx[re], :] for re in res},
        "Nu_strip proxy [-]",
        "Local strip Nusselt number from Q/(A*LMTD_proxy)",
        "fig01_x_strip_Nu_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": omega_grid[re_idx[re], :] for re in res},
        "mean |omega_z| D / U_ref [-]",
        "Local midspan vorticity/mixing proxy in the same x-strips",
        "fig02_x_strip_vorticity_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": qcrit_grid[re_idx[re], :] for re in res},
        "mean max(Q_2D,0) D^2 / U_ref^2 [-]",
        "One-number Q-criterion proxy per x-strip on midspan plane",
        "fig07_x_strip_Qcriterion2D_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": lambda_ci_grid[re_idx[re], :] for re in res},
        "mean lambda_ci D / U_ref [-]",
        "One-number swirling-strength proxy per x-strip on midspan plane",
        "fig08_x_strip_lambda_ci_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": near_wall_omega_grid[re_idx[re], :] for re in res},
        "near-wall mean |omega_z| D / U_ref [-]",
        "Near-wall shear/rotation proxy separated from wake",
        "fig09_x_strip_near_wall_omega_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": near_wall_qcrit_grid[re_idx[re], :] for re in res},
        "near-wall mean max(Q_2D,0) D^2 / U_ref^2 [-]",
        "Near-wall Q-criterion proxy around the tube",
        "fig12_x_strip_near_wall_Qcriterion2D_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": near_wall_lambda_ci_grid[re_idx[re], :] for re in res},
        "near-wall mean lambda_ci D / U_ref [-]",
        "Near-wall swirling-strength proxy around the tube",
        "fig13_x_strip_near_wall_lambda_ci_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": wake_qcrit_grid[re_idx[re], :] for re in res},
        "wake mean max(Q_2D,0) D^2 / U_ref^2 [-]",
        "Wake-only Q-criterion proxy separated from near-wall shear",
        "fig10_x_strip_wake_Qcriterion2D_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": wake_lambda_ci_grid[re_idx[re], :] for re in res},
        "wake mean lambda_ci D / U_ref [-]",
        "Wake-only swirling-strength proxy separated from near-wall shear",
        "fig11_x_strip_wake_lambda_ci_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": bulk_qcrit_grid[re_idx[re], :] for re in res},
        "bulk mean max(Q_2D,0) D^2 / U_ref^2 [-]",
        "Whole-domain midspan Q-criterion after removing tube near-wall region",
        "fig14_x_strip_bulk_no_near_wall_Qcriterion2D_profiles_by_Re",
    )
    save_line_plot(
        xs,
        {f"Re {re:g}": bulk_lambda_ci_grid[re_idx[re], :] for re in res},
        "bulk mean lambda_ci D / U_ref [-]",
        "Whole-domain midspan swirling strength after removing tube near-wall region",
        "fig15_x_strip_bulk_no_near_wall_lambda_ci_profiles_by_Re",
    )

    selected = [re for re in (160.0, 175.0, 200.0) if re in re_idx]
    nu_global = {re: float(np.nanmean(nu_grid[re_idx[re], :])) for re in res}
    derived_rows = []
    for re in res:
        g_gain = nu_global[re] / nu_global[150.0]
        for j, x_mm in enumerate(xs):
            local_gain = nu_grid[re_idx[re], j] / nu_grid[re_idx[150.0], j]
            derived_rows.append(
                {
                    "Re": re,
                    "x_center_mm": x_mm,
                    "Nu_strip_proxy": nu_grid[re_idx[re], j],
                    "Nu_global_mean_proxy": nu_global[re],
                    "Nu_local_gain_vs_Re150": local_gain,
                    "Nu_global_gain_vs_Re150": g_gain,
                    "Nu_local_excess_over_global_gain": local_gain / g_gain - 1.0,
                    "omega_z_abs_nd": omega_grid[re_idx[re], j],
                    "Qcriterion_2D_positive_nd": qcrit_grid[re_idx[re], j],
                    "lambda_ci_2D_nd": lambda_ci_grid[re_idx[re], j],
                    "near_wall_omega_z_abs_nd": near_wall_omega_grid[re_idx[re], j],
                    "near_wall_Qcriterion_2D_positive_nd": near_wall_qcrit_grid[re_idx[re], j],
                    "near_wall_lambda_ci_2D_nd": near_wall_lambda_ci_grid[re_idx[re], j],
                    "wake_omega_z_abs_nd": wake_omega_grid[re_idx[re], j],
                    "wake_Qcriterion_2D_positive_nd": wake_qcrit_grid[re_idx[re], j],
                    "wake_lambda_ci_2D_nd": wake_lambda_ci_grid[re_idx[re], j],
                    "bulk_without_tube_near_wall_omega_z_abs_nd": bulk_omega_grid[re_idx[re], j],
                    "bulk_without_tube_near_wall_Qcriterion_2D_positive_nd": bulk_qcrit_grid[re_idx[re], j],
                    "bulk_without_tube_near_wall_lambda_ci_2D_nd": bulk_lambda_ci_grid[re_idx[re], j],
                }
            )
    write_csv(derived_rows, OUT_DIR / "x_strip_1mm_Nu_vorticity_derived.csv")
    nu_excess_by_re = {
        re: np.asarray([r["Nu_local_excess_over_global_gain"] for r in derived_rows if r["Re"] == re])
        for re in selected
    }

    save_line_plot(
        xs,
        {
            f"Re {re:g}": np.asarray(
                [r["Nu_local_excess_over_global_gain"] for r in derived_rows if r["Re"] == re]
            )
            for re in selected
        },
        "local Nu gain / mean Nu gain - 1 [-]",
        "Local Nu amplification after removing mean Nu scaling",
        "fig03_x_strip_Nu_excess_over_global_gain",
    )

    fig, axes = plt.subplots(len(selected), 1, figsize=(10.6, 3.25 * len(selected)), sharex=True)
    if len(selected) == 1:
        axes = [axes]
    for ax, re in zip(axes, selected):
        nu_excess = np.asarray([r["Nu_local_excess_over_global_gain"] for r in derived_rows if r["Re"] == re])
        vort = omega_grid[re_idx[re], :]
        vort_scaled = (vort - np.nanmean(vort)) / np.nanstd(vort)
        nu_scaled = (nu_excess - np.nanmean(nu_excess)) / np.nanstd(nu_excess)
        ax.plot(xs, nu_scaled, color="#1f5f8b", lw=2.1, label="Nu excess, z-score")
        ax.plot(xs, vort_scaled, color="#e07a5f", lw=1.9, label="|omega_z|D/U, z-score")
        ax.axhline(0, color="0.2", lw=0.8)
        add_tube_markers(ax)
        ax.set_ylabel(f"Re {re:g}\nz-score")
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=2, loc="upper right")
    axes[-1].set_xlabel("x position from tube center [mm], 1 mm strips")
    fig.suptitle("Local Nu amplification vs local vorticity proxy in the same strips", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig04_x_strip_Nu_excess_and_vorticity_overlay.png", dpi=220)
    fig.savefig(OUT_DIR / "fig04_x_strip_Nu_excess_and_vorticity_overlay.pdf")
    plt.close(fig)

    save_nu_proxy_overlay(
        xs,
        selected,
        re_idx,
        nu_excess_by_re,
        bulk_qcrit_grid,
        "bulk-no-wall Qcrit",
        "Nu excess vs inner/bulk vortex proxy after removing tube near-wall region",
        "fig16_Nu_excess_vs_bulk_no_wall_Qcriterion_overlay",
    )
    save_nu_proxy_scatter(
        selected,
        re_idx,
        nu_excess_by_re,
        bulk_qcrit_grid,
        "bulk-no-wall mean max(Q_2D,0) D^2 / U_ref^2 [-]",
        "Correlation: inner/bulk vortex proxy vs local Nu excess",
        "fig17_Nu_excess_vs_bulk_no_wall_Qcriterion_scatter",
    )
    save_nu_proxy_overlay(
        xs,
        selected,
        re_idx,
        nu_excess_by_re,
        bulk_lambda_ci_grid,
        "bulk-no-wall lambda_ci",
        "Nu excess vs inner/bulk swirling strength after removing tube near-wall region",
        "fig18_Nu_excess_vs_bulk_no_wall_lambda_ci_overlay",
    )
    save_nu_proxy_scatter(
        selected,
        re_idx,
        nu_excess_by_re,
        bulk_lambda_ci_grid,
        "bulk-no-wall mean lambda_ci D / U_ref [-]",
        "Correlation: inner/bulk swirling strength vs local Nu excess",
        "fig19_Nu_excess_vs_bulk_no_wall_lambda_ci_scatter",
    )
    save_nu_proxy_overlay(
        xs,
        selected,
        re_idx,
        nu_excess_by_re,
        near_wall_qcrit_grid,
        "near-wall Qcrit",
        "Nu excess vs tube near-wall Q-criterion proxy",
        "fig20_Nu_excess_vs_near_wall_Qcriterion_overlay",
    )
    save_nu_proxy_scatter(
        selected,
        re_idx,
        nu_excess_by_re,
        near_wall_qcrit_grid,
        "near-wall mean max(Q_2D,0) D^2 / U_ref^2 [-]",
        "Correlation: tube near-wall Q-criterion proxy vs local Nu excess",
        "fig21_Nu_excess_vs_near_wall_Qcriterion_scatter",
    )
    save_nu_proxy_overlay(
        xs,
        selected,
        re_idx,
        nu_excess_by_re,
        near_wall_lambda_ci_grid,
        "near-wall lambda_ci",
        "Nu excess vs tube near-wall swirling strength",
        "fig22_Nu_excess_vs_near_wall_lambda_ci_overlay",
    )
    save_nu_proxy_scatter(
        selected,
        re_idx,
        nu_excess_by_re,
        near_wall_lambda_ci_grid,
        "near-wall mean lambda_ci D / U_ref [-]",
        "Correlation: tube near-wall swirling strength vs local Nu excess",
        "fig23_Nu_excess_vs_near_wall_lambda_ci_scatter",
    )

    scatter_rows = []
    fig, axes = plt.subplots(3, 3, figsize=(16.8, 13.2), sharey=True)
    axes_flat = axes.ravel()
    cmap = plt.get_cmap("magma")
    scatter_metrics = [
        ("omega_z_abs_nd", omega_grid, "mean |omega_z| D / U_ref [-]", "vorticity proxy"),
        ("Qcriterion_2D_positive_nd", qcrit_grid, "mean max(Q_2D,0) D^2 / U_ref^2 [-]", "Q-criterion proxy"),
        ("lambda_ci_2D_nd", lambda_ci_grid, "mean lambda_ci D / U_ref [-]", "swirling strength"),
        ("near_wall_omega_z_abs_nd", near_wall_omega_grid, "near-wall |omega_z| D / U_ref [-]", "near-wall shear/rotation"),
        ("wake_Qcriterion_2D_positive_nd", wake_qcrit_grid, "wake max(Q_2D,0) D^2 / U_ref^2 [-]", "wake Q-criterion"),
        ("wake_lambda_ci_2D_nd", wake_lambda_ci_grid, "wake lambda_ci D / U_ref [-]", "wake swirling strength"),
        (
            "bulk_without_tube_near_wall_Qcriterion_2D_positive_nd",
            bulk_qcrit_grid,
            "bulk-no-wall max(Q_2D,0) D^2 / U_ref^2 [-]",
            "bulk Q-criterion, no tube near-wall",
        ),
        (
            "bulk_without_tube_near_wall_lambda_ci_2D_nd",
            bulk_lambda_ci_grid,
            "bulk-no-wall lambda_ci D / U_ref [-]",
            "bulk swirling strength, no tube near-wall",
        ),
    ]
    for ax, (metric_name, metric_grid, xlabel, title) in zip(axes_flat, scatter_metrics):
        for i, re in enumerate(selected):
            nu_excess = np.asarray([r["Nu_local_excess_over_global_gain"] for r in derived_rows if r["Re"] == re])
            metric_values = metric_grid[re_idx[re], :]
            valid = np.isfinite(nu_excess) & np.isfinite(metric_values)
            corr = float(np.corrcoef(metric_values[valid], nu_excess[valid])[0, 1]) if valid.sum() > 2 else np.nan
            scatter_rows.append({"Re": re, "metric": metric_name, "pearson_r_vs_Nu_excess": corr, "n_strips": int(valid.sum())})
            ax.scatter(
                metric_values[valid],
                nu_excess[valid],
                s=35,
                alpha=0.8,
                color=cmap(i / max(1, len(selected) - 1)),
                label=f"Re {re:g}, r={corr:.2f}",
            )
        ax.axhline(0, color="0.2", lw=0.8)
        ax.set_xlabel(xlabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False)
    for ax in axes_flat[len(scatter_metrics) :]:
        ax.axis("off")
    axes[0, 0].set_ylabel("local Nu gain / mean Nu gain - 1 [-]")
    axes[1, 0].set_ylabel("local Nu gain / mean Nu gain - 1 [-]")
    axes[2, 0].set_ylabel("local Nu gain / mean Nu gain - 1 [-]")
    fig.suptitle("Stripwise relation between vortex proxies and local Nu excess", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig05_scatter_vorticity_vs_Nu_excess.png", dpi=220)
    fig.savefig(OUT_DIR / "fig05_scatter_vorticity_vs_Nu_excess.pdf")
    plt.close(fig)
    write_csv(scatter_rows, OUT_DIR / "x_strip_vorticity_Nu_correlation.csv")

    save_line_plot(
        xs,
        {f"Re {re:g}": q_grid[re_idx[re], :] for re in res},
        "Q_total per strip [W]",
        "Reference: integrated heat transfer used before Nu normalization",
        "fig06_x_strip_Q_reference_profiles_by_Re",
    )

    (OUT_DIR / "README.md").write_text(
        f"""# 004_x_strip_Nu_vorticity

Local x-strip Nusselt and vorticity-proxy analysis.

## Method

- Strips are 1 mm wide along the streamwise `x` direction.
- `Q_strip` and `A_strip` are integrated directly from hot tube and hot fin VTK surfaces.
- `alpha_strip = Q_strip / (A_strip * deltaT_lm_proxy)`.
- `Nu_strip_proxy = alpha_strip * D / k_air`.
- Constants used: `D = {D_REF} m`, `T_wall = {T_WALL} K`, `k_air = {K_AIR} W/(m K)`.
- `deltaT_lm_proxy` is based on midspan `T_bulk` proxy from the `z=0` sampled plane, weighted by positive `Ux`.
- Vorticity proxy is `mean(|omega_z|) * D / U_ref`, computed on the same `z=0` sampled plane.
- Regional metrics separate near-wall and wake mechanisms:
  near-wall uses a tube annulus from `R` to `R + {NEAR_WALL_THICKNESS} m`;
  wake uses `x >= R` and excludes that near-wall annulus.
- `bulk_without_tube_near_wall` uses the whole midspan plane over the full x-domain,
  but removes the tube near-wall annulus.

## Important Limitation

This is a presentation/mechanism metric, not yet a full publication-grade local Nu.
For strict validation, `T_bulk(x_left)` and `T_bulk(x_right)` should be computed from full
`y-z` cross-sections using mass-flow weighting. Here they are approximated from the midspan plane.

## Figures

`fig01_x_strip_Nu_profiles_by_Re.png`: local strip Nusselt profiles.

`fig02_x_strip_vorticity_profiles_by_Re.png`: local vorticity/mixing proxy profiles.

`fig03_x_strip_Nu_excess_over_global_gain.png`: local Nu excess after removing mean Nu scaling.

`fig04_x_strip_Nu_excess_and_vorticity_overlay.png`: z-scored overlay of Nu excess and vorticity proxy.

`fig05_scatter_vorticity_vs_Nu_excess.png`: stripwise correlation between vorticity proxy and Nu excess.

`fig06_x_strip_Q_reference_profiles_by_Re.png`: original Q profiles for reference.

`fig07_x_strip_Qcriterion2D_profiles_by_Re.png`: one positive `Q_2D` criterion number per x-strip.

`fig08_x_strip_lambda_ci_profiles_by_Re.png`: one 2D swirling-strength number per x-strip.

`fig09_x_strip_near_wall_omega_profiles_by_Re.png`: near-wall shear/rotation separated from wake.

`fig10_x_strip_wake_Qcriterion2D_profiles_by_Re.png`: wake-only positive `Q_2D` proxy.

`fig11_x_strip_wake_lambda_ci_profiles_by_Re.png`: wake-only 2D swirling strength.

`fig12_x_strip_near_wall_Qcriterion2D_profiles_by_Re.png`: near-wall positive `Q_2D` around the tube.

`fig13_x_strip_near_wall_lambda_ci_profiles_by_Re.png`: near-wall 2D swirling strength around the tube.

`fig14_x_strip_bulk_no_near_wall_Qcriterion2D_profiles_by_Re.png`: full x-domain midspan positive `Q_2D` after removing tube near-wall region.

`fig15_x_strip_bulk_no_near_wall_lambda_ci_profiles_by_Re.png`: full x-domain midspan swirling strength after removing tube near-wall region.

`fig16`-`fig19`: direct Nu-excess comparison with inner/bulk vortex proxies after removing tube near-wall region.

`fig20`-`fig23`: direct Nu-excess comparison with tube near-wall vortex/shear proxies.

`x_strip_vorticity_Nu_correlation.csv`: Pearson correlations between Nu excess and each vortex proxy.
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
