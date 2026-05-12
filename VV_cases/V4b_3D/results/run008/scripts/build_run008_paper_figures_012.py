"""
Build paper-grade final figures for V4b_3D run008.

Layer 012:
Figure 1: geometry/domain/sampling layout.
Figure 2: Cd(t), Cl(t), PSD Cl.
Figure 3: heat balance Q_air/Q_wall and Nu_EB/Nu_wall.
Figure 4: mean and RMS Nu(theta,z) on the tube.
Figure 5: phase-averaged Nu(theta) at selected phases.
Figure 6: fin Nu_local(x) mean/RMS/coherence.
Figure 7: POD energy and mode-map panel.
Figure 8: EPOD / Cl-correlated thermal structure.
Figure 9: Cl-Nu coherence maps.
Figure 10: summary mechanism schematic.
"""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal


RUN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = RUN_DIR / "data" / "012"
FIG_DIR = RUN_DIR / "figures" / "012"

D = 0.012
F_SHED = 3.2787
F2_SHED = 2.0 * F_SHED
WINDOW = (2.0, 10.0)


@dataclass
class Caption:
    figure: str
    file_png: str
    file_pdf: str
    title: str
    caption: str


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def resolve_case_dir() -> Path:
    candidates = [
        Path("/home/hexmachina/of_runs/V4b_3D_run008"),
        Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run008"),
        Path(r"\\wsl$\Ubuntu\home\hexmachina\of_runs\V4b_3D_run008"),
    ]
    for path in candidates:
        if (path / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat").exists():
            return path
    raise FileNotFoundError("Cannot find run008 case")


CASE_DIR = resolve_case_dir()
POST_DIR = CASE_DIR / "postProcessing"


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save(fig: plt.Figure, stem: str) -> tuple[str, str]:
    png = FIG_DIR / f"{stem}.png"
    pdf = FIG_DIR / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return str(png.relative_to(RUN_DIR)), str(pdf.relative_to(RUN_DIR))


def read_csv_cols(path: Path) -> dict[str, np.ndarray]:
    cols: dict[str, list[float]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key, value in row.items():
                try:
                    cols.setdefault(key, []).append(float(value))
                except ValueError:
                    pass
    return {k: np.asarray(v, dtype=float) for k, v in cols.items()}


def write_caption_files(captions: list[Caption]) -> None:
    with (DATA_DIR / "run008_012_final_figure_captions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["figure", "file_png", "file_pdf", "title", "caption"])
        writer.writeheader()
        for cap in captions:
            writer.writerow(cap.__dict__)
    lines = ["# run008 final paper-grade figure set", ""]
    for cap in captions:
        lines.extend([f"## {cap.figure}: {cap.title}", "", f"- PNG: `{cap.file_png}`", f"- PDF: `{cap.file_pdf}`", "", cap.caption, ""])
    (DATA_DIR / "run008_012_final_figure_captions.md").write_text("\n".join(lines), encoding="utf-8")


def read_force_coeffs() -> dict[str, np.ndarray]:
    rows = []
    with (POST_DIR / "forceCoeffs" / "0" / "forceCoeffs.dat").open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            vals = [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", stripped)]
            if len(vals) >= 5:
                rows.append(vals)
    arr = np.asarray(rows, dtype=float)
    mask = (arr[:, 0] >= WINDOW[0] - 1e-12) & (arr[:, 0] <= WINDOW[1] + 1e-12)
    arr = arr[mask]
    return {"time": arr[:, 0], "Cm": arr[:, 1], "Cd": arr[:, 2], "Cl": arr[:, 3]}


def figure_01() -> Caption:
    fig = plt.figure(figsize=(8.2, 5.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 0.95], width_ratios=[1.35, 1.0])
    ax = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    lin = 24.0
    lf = 27.71
    lout = 96.0
    lx = lin + lf + lout
    yc = 0.0
    h = 36.0
    tube_x = lin + lf / 2
    tube_r = 6.0

    ax.add_patch(plt.Rectangle((0, -h / 2), lx, h, facecolor="#eef4f8", edgecolor="#31572c", lw=1.3))
    ax.add_patch(plt.Rectangle((lin, -h / 2), lf, h, facecolor="#f7d9c4", edgecolor="none", alpha=0.75))
    ax.add_patch(plt.Circle((tube_x, yc), tube_r, facecolor="#9b2226", edgecolor="#5f0f40", lw=1.2))
    ax.arrow(6, 0, 12, 0, width=0.5, head_width=3.0, head_length=4.0, color="#1d3557")
    ax.text(7, 4, "inlet", color="#1d3557")
    ax.text(lx - 15, 4, "outlet", color="#1d3557")
    ax.text(lin + lf / 2, -h / 2 - 6, "heated fin zone", ha="center")
    ax.text(tube_x, 0, "D", color="white", ha="center", va="center", fontweight="bold")
    ax.annotate("Lin=2D", xy=(lin / 2, h / 2 + 3), ha="center")
    ax.annotate("Lout=8D", xy=(lin + lf + lout / 2, h / 2 + 3), ha="center")
    ax.annotate("Lx=147.71 mm", xy=(lx / 2, h / 2 + 9), ha="center", fontweight="bold")

    probes = np.array(
        [
            (0.01, 0, 0),
            (0.02, 0, 0),
            (0.03, 0, 0),
            (0.04, 0, 0),
            (0.06, 0, 0),
            (0.08, 0, 0),
            (0.10, 0, 0),
            (0.02, 0.006, 0),
            (0.04, 0.006, 0),
            (0.06, 0.006, 0),
            (0.02, -0.006, 0),
            (0.04, -0.006, 0),
            (0.06, -0.006, 0),
        ]
    )
    ax.scatter(probes[:, 0] * 1000, probes[:, 1] * 1000, marker="x", color="#023047", label="wake probes")
    ax.set_xlim(-3, lx + 3)
    ax.set_ylim(-28, 28)
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title("Domain, heated surfaces, and wake-probe layout")
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="upper right")

    ax2.add_patch(plt.Rectangle((0, 0), lf, 12, facecolor="#f7d9c4", edgecolor="#8d6b4f"))
    ax2.add_patch(plt.Circle((lf / 2, 6), 6, facecolor="#9b2226", edgecolor="#5f0f40"))
    ax2.text(lf / 2, 6, "tube", color="white", ha="center", va="center")
    ax2.text(lf / 2, 12.8, "hot_fin_z_max", ha="center")
    ax2.text(lf / 2, -2.0, "hot_fin_z_min", ha="center")
    ax2.set_xlim(-2, lf + 2)
    ax2.set_ylim(-4, 16)
    ax2.set_xlabel("fin-zone x [mm]")
    ax2.set_ylabel("z [mm]")
    ax2.set_title("Heated surfaces")
    ax2.set_aspect("equal", adjustable="box")

    items = [
        ("forces / surfaces", 0.005, "200 Hz"),
        ("wake probes", 0.005, "200 Hz"),
        ("midspan z=0", 0.020, "50 Hz"),
        ("full 3D fields", 0.080, "12.5 Hz"),
    ]
    y = np.arange(len(items))[::-1]
    ax3.barh(y, [it[1] for it in items], color=["#2a9d8f", "#457b9d", "#e9c46a", "#f4a261"])
    ax3.set_yticks(y)
    ax3.set_yticklabels([it[0] for it in items])
    for yi, it in zip(y, items):
        ax3.text(it[1] + 0.003, yi, it[2], va="center")
    ax3.set_xlabel("write interval [s]")
    ax3.set_title("Sampling cadence")
    ax3.set_xlim(0, 0.1)
    fig.suptitle("Figure 1. Geometry, domain, and sampling layout", fontweight="bold")
    png, pdf = save(fig, "fig01_geometry_domain_sampling")
    return Caption("Figure 1", png, pdf, "Geometry, domain, and sampling layout", "Production domain Lin=2D, Lout=8D with heated tube/fins, wake probes, and high-cadence sampling used for force, heat-transfer, POD, and coherence analyses.")


def figure_02() -> Caption:
    force = read_force_coeffs()
    t = force["time"]
    cl = force["Cl"]
    cd = force["Cd"]
    fs = 1.0 / np.median(np.diff(t))
    f, pxx = signal.welch(cl - np.mean(cl), fs=fs, nperseg=1024, noverlap=512)
    fig, axes = plt.subplots(2, 2, figsize=(8.4, 5.6), sharex=False)
    axes[0, 0].plot(t, cd, color="#31572c", lw=0.9)
    axes[0, 0].set_ylabel("Cd")
    axes[0, 0].set_title("Drag coefficient")
    axes[1, 0].plot(t, cl, color="#9b2226", lw=0.9)
    axes[1, 0].set_xlabel("time [s]")
    axes[1, 0].set_ylabel("Cl")
    axes[1, 0].set_title("Lift coefficient")
    axes[0, 1].plot(t, cl - np.mean(cl), color="#9b2226", lw=0.8)
    axes[0, 1].set_title("Lift fluctuation")
    axes[0, 1].set_ylabel("Cl'")
    axes[1, 1].semilogy(f, pxx, color="#1d3557", lw=1.2)
    axes[1, 1].axvline(F_SHED, color="#9b2226", ls="--", label="f_shed")
    axes[1, 1].axvline(F2_SHED, color="#5f0f40", ls=":", label="2f_shed")
    axes[1, 1].set_xlim(0, 12)
    axes[1, 1].set_xlabel("frequency [Hz]")
    axes[1, 1].set_ylabel("PSD(Cl)")
    axes[1, 1].legend()
    for ax in axes.ravel():
        ax.grid(True, alpha=0.25)
    fig.suptitle("Figure 2. Force history and lift spectrum", fontweight="bold")
    png, pdf = save(fig, "fig02_forces_cl_psd")
    return Caption("Figure 2", png, pdf, "Cd(t), Cl(t), and PSD(Cl)", "Production-window force histories and lift spectrum show the established periodic regime with shedding near St=0.154 and a strong second-harmonic/adjacent-peak component.")


def figure_03() -> Caption:
    h = read_csv_cols(RUN_DIR / "data" / "003" / "run008_003_heat_balance_timeseries.csv")
    t = h["time"]
    fig, axes = plt.subplots(2, 2, figsize=(8.4, 5.6), sharex=True)
    axes[0, 0].plot(t, h["Q_air"], label="Q_air", color="#1d3557")
    axes[0, 0].plot(t, h["Q_wall"], label="Q_wall", color="#9b2226")
    axes[0, 0].set_ylabel("Q [W]")
    axes[0, 0].set_title("Energy balance")
    axes[0, 0].legend()
    axes[1, 0].plot(t, h["closure_pct"], color="#6c757d", lw=0.8)
    axes[1, 0].axhline(0, color="0.3", lw=0.8)
    axes[1, 0].set_xlabel("time [s]")
    axes[1, 0].set_ylabel("closure [%]")
    axes[1, 0].set_title("Instantaneous closure")
    axes[0, 1].plot(t, h["Nu_EB"], label="Nu_EB", color="#2a9d8f")
    axes[0, 1].plot(t, h["Nu_total_wall"], label="Nu_wall", color="#e76f51")
    axes[0, 1].set_ylabel("Nu")
    axes[0, 1].set_title("Independent Nu estimates")
    axes[0, 1].legend()
    axes[1, 1].scatter(h["Nu_EB"], h["Nu_total_wall"], s=8, alpha=0.45, color="#457b9d")
    lo = min(np.nanmin(h["Nu_EB"]), np.nanmin(h["Nu_total_wall"]))
    hi = max(np.nanmax(h["Nu_EB"]), np.nanmax(h["Nu_total_wall"]))
    axes[1, 1].plot([lo, hi], [lo, hi], color="0.4", ls="--")
    axes[1, 1].set_xlabel("Nu_EB")
    axes[1, 1].set_ylabel("Nu_wall")
    axes[1, 1].set_title("Nu consistency")
    for ax in axes.ravel():
        ax.grid(True, alpha=0.25)
    fig.suptitle("Figure 3. Heat balance and Nusselt closure", fontweight="bold")
    png, pdf = save(fig, "fig03_heat_balance_nu_closure")
    return Caption("Figure 3", png, pdf, "Heat balance and Nusselt closure", "Wall-integrated and air-side heat rates close within about one percent, while Nu_EB and wall-side Nu provide independent, consistent heat-transfer estimates.")


def figure_04() -> Caption:
    a = np.load(RUN_DIR / "data" / "004" / "run008_004_tube_nu_arrays.npz")
    theta = np.degrees(a["theta_centers"])
    z = a["z_centers"] * 1000
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6), sharey=True)
    im0 = axes[0].pcolormesh(theta, z, a["mean_map"], shading="auto", cmap="magma")
    axes[0].set_title("mean Nu(theta,z)")
    axes[0].set_xlabel("theta [deg]")
    axes[0].set_ylabel("z [mm]")
    fig.colorbar(im0, ax=axes[0], label="Nu")
    im1 = axes[1].pcolormesh(theta, z, a["rms_map"], shading="auto", cmap="viridis")
    axes[1].set_title("RMS Nu(theta,z)")
    axes[1].set_xlabel("theta [deg]")
    fig.colorbar(im1, ax=axes[1], label="Nu RMS")
    fig.suptitle("Figure 4. Tube local Nusselt statistics", fontweight="bold")
    png, pdf = save(fig, "fig04_tube_nu_mean_rms")
    return Caption("Figure 4", png, pdf, "Mean and RMS Nu(theta,z) on the tube", "Mean and RMS maps expose the circumferential/spanwise organization of tube heat transfer and identify where unsteady shedding modulates local Nu.")


def figure_05() -> Caption:
    a = np.load(RUN_DIR / "data" / "009" / "run008_009_phase_arrays.npz")
    theta = np.degrees(a["theta_centers"])
    phase_deg = a["phase_deg"]
    tube = a["tube_nu_phase"]
    profile = np.nanmean(tube, axis=1)
    selected = [0, 2, 4, 6, 8, 10, 12, 14]
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    cmap = plt.get_cmap("twilight")
    for k, idx in enumerate(selected):
        ax.plot(theta, profile[idx], color=cmap(k / len(selected)), lw=1.4, label=f"{phase_deg[idx]:.0f} deg")
    ax.set_xlabel("theta [deg]")
    ax.set_ylabel("z-averaged Nu(theta)")
    ax.set_title("Phase-averaged tube Nu profiles")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=4, title="phase", fontsize=7)
    fig.suptitle("Figure 5. Phase-resolved Nu(theta)", fontweight="bold")
    png, pdf = save(fig, "fig05_phase_averaged_tube_nu_theta")
    return Caption("Figure 5", png, pdf, "Phase-averaged Nu(theta)", "Eight phase-conditioned tube profiles show how the circumferential heat-transfer peak moves and changes intensity over the shedding cycle.")


def figure_06() -> Caption:
    a = np.load(RUN_DIR / "data" / "005" / "run008_005_fin_nu_arrays.npz")
    x = a["x_centers"] * 1000
    valid_min = a["valid_min"].astype(bool)
    valid_max = a["valid_max"].astype(bool)
    fig, axes = plt.subplots(3, 1, figsize=(7.4, 7.4), sharex=True)
    axes[0].plot(x[valid_min], a["mean_min"][valid_min], label="z_min", color="#1d3557")
    axes[0].plot(x[valid_max], a["mean_max"][valid_max], label="z_max", color="#9b2226")
    axes[0].set_ylabel("mean Nu")
    axes[0].set_title("Fin Nu_local(x)")
    axes[0].legend()
    axes[1].plot(x[valid_min], a["rms_min"][valid_min], label="z_min", color="#1d3557")
    axes[1].plot(x[valid_max], a["rms_max"][valid_max], label="z_max", color="#9b2226")
    axes[1].set_ylabel("RMS Nu")
    axes[2].plot(x[valid_min], a["coh_min"][valid_min], label="z_min", color="#1d3557")
    axes[2].plot(x[valid_max], a["coh_max"][valid_max], label="z_max", color="#9b2226")
    axes[2].axhline(0.5, color="0.5", ls="--", lw=0.8)
    axes[2].set_ylabel("coh(Cl,Nu)")
    axes[2].set_xlabel("x [mm]")
    for ax in axes:
        ax.grid(True, alpha=0.25)
    fig.suptitle("Figure 6. Fin local heat-transfer response", fontweight="bold")
    png, pdf = save(fig, "fig06_fin_nu_mean_rms_coherence")
    return Caption("Figure 6", png, pdf, "Nu_local(x) on fins", "Mean, RMS, and lift-coherence profiles on the two heated fin surfaces identify streamwise regions actively coupled to vortex shedding.")


def figure_07() -> Caption:
    energy = read_csv_cols(RUN_DIR / "data" / "006" / "run008_006_pod_energy.csv")
    # Fallback to existing mode-map panel for spatial mode shapes.
    mode_img = mpimg.imread(RUN_DIR / "figures" / "006" / "run008_006_pod_mode_maps.png")
    fig = plt.figure(figsize=(9.0, 6.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[0.85, 1.5])
    ax = fig.add_subplot(gs[0, 0])
    ax_img = fig.add_subplot(gs[0, 1])
    rows = []
    with (RUN_DIR / "data" / "006" / "run008_006_pod_energy.csv").open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if int(row["mode"]) <= 8:
                rows.append(row)
    for pod_set, color in [("U", "#1d3557"), ("T", "#9b2226"), ("U+T", "#2a9d8f")]:
        modes = [int(r["mode"]) for r in rows if r["pod_set"] == pod_set]
        vals = [100 * float(r["energy_fraction"]) for r in rows if r["pod_set"] == pod_set]
        ax.plot(modes, vals, marker="o", label=pod_set, color=color)
    ax.set_xlabel("POD mode")
    ax.set_ylabel("energy [%]")
    ax.set_title("POD energy")
    ax.grid(True, alpha=0.25)
    ax.legend()
    ax_img.imshow(mode_img)
    ax_img.axis("off")
    ax_img.set_title("Mode 1/2 maps (from layer 006)")
    fig.suptitle("Figure 7. POD energy and dominant mode maps", fontweight="bold")
    png, pdf = save(fig, "fig07_pod_energy_modes")
    return Caption("Figure 7", png, pdf, "POD energy and mode 1/2 maps", "The first two modes form the dominant shedding pair in velocity and temperature; the spatial mode maps show the coherent wake/thermal structures.")


def figure_08() -> Caption:
    img = mpimg.imread(RUN_DIR / "figures" / "006" / "run008_006_epod_spod_maps.png")
    fig, ax = plt.subplots(figsize=(8.8, 5.5))
    ax.imshow(img)
    ax.axis("off")
    ax.set_title("Figure 8. EPOD and coherent thermal structures", fontweight="bold")
    png, pdf = save(fig, "fig08_epod_cl_thermal_structure")
    return Caption("Figure 8", png, pdf, "EPOD / Cl-correlated thermal structure", "EPOD regression fields and single-frequency coherent amplitudes expose the midspan thermal structures correlated with lift and heat-transfer metrics.")


def figure_09() -> Caption:
    a = np.load(RUN_DIR / "data" / "007" / "run008_007_coherence_arrays.npz")
    theta = np.degrees(a["theta"])
    z = a["z"] * 1000
    tube_f1 = a["tube_coh_f1"].reshape((len(z), len(theta)))
    tube_f2 = a["tube_coh_f2"].reshape((len(z), len(theta)))
    x = a["fin_x"] * 1000
    fig = plt.figure(figsize=(8.4, 6.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 0.8])
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1], sharey=ax0)
    ax2 = fig.add_subplot(gs[1, :])
    im0 = ax0.pcolormesh(theta, z, tube_f1, shading="auto", cmap="viridis", vmin=0, vmax=1)
    ax0.set_title("tube coherence f_shed")
    ax0.set_xlabel("theta [deg]")
    ax0.set_ylabel("z [mm]")
    im1 = ax1.pcolormesh(theta, z, tube_f2, shading="auto", cmap="viridis", vmin=0, vmax=1)
    ax1.set_title("tube coherence 2f_shed")
    ax1.set_xlabel("theta [deg]")
    fig.colorbar(im1, ax=[ax0, ax1], label="coherence")
    ax2.plot(x, a["fin_z_min_coh_f1"], label="z_min f_shed", color="#1d3557")
    ax2.plot(x, a["fin_z_max_coh_f1"], label="z_max f_shed", color="#9b2226")
    ax2.plot(x, a["fin_z_min_coh_f2"], ls="--", color="#1d3557", label="z_min 2f")
    ax2.plot(x, a["fin_z_max_coh_f2"], ls="--", color="#9b2226", label="z_max 2f")
    ax2.set_xlabel("fin x [mm]")
    ax2.set_ylabel("coh(Cl,Nu)")
    ax2.grid(True, alpha=0.25)
    ax2.legend(ncol=2)
    fig.suptitle("Figure 9. Coherence between lift and local Nu", fontweight="bold")
    png, pdf = save(fig, "fig09_cl_nu_coherence_maps")
    return Caption("Figure 9", png, pdf, "Coherence Cl <-> local Nu", "Spatial coherence maps reveal localized fundamental coupling and nearly global second-harmonic organization of the local heat-transfer response.")


def figure_10() -> Caption:
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.axis("off")
    boxes = [
        ("Vortex shedding\nCl phase", (0.12, 0.58), "#9b2226"),
        ("Near-wake sensor\nprobe 2: Uy-Cl coh=0.883", (0.37, 0.72), "#457b9d"),
        ("Tube heat pickup\nQ_tube peaks with max |Cl|", (0.37, 0.42), "#e76f51"),
        ("Fin response\nQ_fins lag +0.057 s", (0.64, 0.42), "#f4a261"),
        ("Global closure\nQ_wall ~= Q_air\n+0.706%", (0.84, 0.58), "#2a9d8f"),
        ("Local Nu coherence\n2f_shed dominates", (0.64, 0.76), "#6a4c93"),
    ]
    for text, (x, y), color in boxes:
        ax.text(x, y, text, ha="center", va="center", color="white", fontsize=9, fontweight="bold", bbox=dict(boxstyle="round,pad=0.45", fc=color, ec="none"))
    arrows = [
        ((0.20, 0.62), (0.30, 0.70)),
        ((0.20, 0.56), (0.30, 0.44)),
        ((0.46, 0.42), (0.55, 0.42)),
        ((0.72, 0.45), (0.78, 0.55)),
        ((0.46, 0.72), (0.55, 0.76)),
        ((0.72, 0.76), (0.80, 0.62)),
    ]
    for p0, p1 in arrows:
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="->", lw=1.5, color="0.25"))
    ax.text(0.50, 0.16, "Mechanism: periodic shedding organizes wake velocity, redistributes tube/fin local Nu,\nand produces a delayed fin-dominated contribution to total wall heat pickup.", ha="center", va="center", fontsize=10)
    ax.set_title("Figure 10. Summary schematic of force-heat coupling", fontweight="bold")
    png, pdf = save(fig, "fig10_mechanism_schematic")
    return Caption("Figure 10", png, pdf, "Summary mechanism schematic", "Conceptual mechanism distilled from the production run: shedding phase drives coherent wake probes, local tube/fin Nu redistribution, and a delayed fin-dominated heat-transfer response while maintaining global heat-balance closure.")


def main() -> None:
    ensure_dirs()
    set_style()
    captions = [
        figure_01(),
        figure_02(),
        figure_03(),
        figure_04(),
        figure_05(),
        figure_06(),
        figure_07(),
        figure_08(),
        figure_09(),
        figure_10(),
    ]
    write_caption_files(captions)
    summary = {"figures": [cap.__dict__ for cap in captions]}
    (DATA_DIR / "run008_012_final_figures_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print((DATA_DIR / "run008_012_final_figure_captions.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
