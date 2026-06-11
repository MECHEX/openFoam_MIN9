from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUT_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/presentation_data/002_Nu_and_vorticity")
OUT_DIR.mkdir(parents=True, exist_ok=True)

D = 0.012
U_RE200 = 0.25266
NU_WALL_RE200 = 7.816521

CASES = [
    {
        "Re": 100,
        "case": "run012_re100",
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run012_re100_production"),
        "window": (8.0, 10.0),
        "regime": "steady",
    },
    {
        "Re": 150,
        "case": "run013_re150",
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run013_re150_production"),
        "window": (8.0, 10.0),
        "regime": "steady",
    },
    {
        "Re": 160,
        "case": "run015_re160",
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run015_re160_production"),
        "window": (8.0, 10.0),
        "regime": "shedding",
    },
    {
        "Re": 175,
        "case": "run014_re175",
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run014_re175_production"),
        "window": (8.0, 10.0),
        "regime": "shedding",
    },
    {
        "Re": 200,
        "case": "run008_re200",
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run008"),
        "window": (2.0, 10.0),
        "regime": "production shedding",
    },
]


def read_force_coeffs(case_dir: Path) -> list[dict[str, float]]:
    path = case_dir / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat"
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        t, cm, cd, cl, clf, clr = [float(x) for x in line.split()[:6]]
        rows.append({"time": t, "Cm": cm, "Cd": cd, "Cl": cl, "Clf": clf, "Clr": clr})
    return rows


def read_wall_heat(case_dir: Path) -> list[dict[str, float | str]]:
    path = case_dir / "postProcessing" / "wallHeatFlux" / "0" / "wallHeatFlux.dat"
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split()
        rows.append(
            {
                "time": float(parts[0]),
                "patch": parts[1],
                "q_min": float(parts[2]),
                "q_max": float(parts[3]),
                "Q": float(parts[4]),
                "q_mean": float(parts[5]),
            }
        )
    return rows


def mean_std(values: list[float]) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    return float(arr.mean()), float(arr.std(ddof=0))


def dominant_frequency(rows: list[dict[str, float]], t0: float, t1: float) -> tuple[float | None, float | None]:
    data = [r for r in rows if t0 <= r["time"] <= t1]
    if len(data) < 20:
        return None, None
    t = np.asarray([r["time"] for r in data])
    cl = np.asarray([r["Cl"] for r in data])
    dt = float(np.median(np.diff(t)))
    signal = cl - cl.mean()
    freq = np.fft.rfftfreq(len(signal), dt)
    amp = np.abs(np.fft.rfft(signal))
    amp[0] = 0.0
    idx = int(np.argmax(amp))
    f = float(freq[idx])
    st = f * D / U_RE200 if f > 0 else None
    return f, st


def summarize_case(case: dict) -> dict:
    t0, t1 = case["window"]
    force = read_force_coeffs(case["path"])
    heat = read_wall_heat(case["path"])

    force_win = [r for r in force if t0 <= r["time"] <= t1]
    cl_vals = [r["Cl"] for r in force_win]
    cd_vals = [r["Cd"] for r in force_win]
    cl_mean = sum(cl_vals) / len(cl_vals)
    cl_std = math.sqrt(sum((v - cl_mean) ** 2 for v in cl_vals) / len(cl_vals))
    cd_mean, cd_std = mean_std(cd_vals)
    f_peak, st = dominant_frequency(force, t0, t1)
    if cl_std < 1e-3:
        f_peak, st = None, None

    by_time: dict[float, dict[str, float]] = {}
    for row in heat:
        if t0 <= row["time"] <= t1:
            by_time.setdefault(float(row["time"]), {})[str(row["patch"])] = float(row["Q"])

    q_total = []
    q_tube = []
    q_fins = []
    for patches in by_time.values():
        tube = patches.get("hot_tube", 0.0)
        fins = patches.get("hot_fin_z_min", 0.0) + patches.get("hot_fin_z_max", 0.0)
        if tube or fins:
            q_tube.append(tube)
            q_fins.append(fins)
            q_total.append(tube + fins)

    q_wall_mean, q_wall_std = mean_std(q_total)
    q_tube_mean, q_tube_std = mean_std(q_tube)
    q_fins_mean, q_fins_std = mean_std(q_fins)

    return {
        "Re": case["Re"],
        "case": case["case"],
        "window": f"{t0:g}-{t1:g} s",
        "regime": case["regime"],
        "Cd_mean": cd_mean,
        "Cd_std": cd_std,
        "Cl_mean": cl_mean,
        "Cl_rms": cl_std,
        "f_peak_Hz": f_peak,
        "St_using_U200": st,
        "Q_wall_W": q_wall_mean,
        "Q_wall_std_W": q_wall_std,
        "Q_tube_W": q_tube_mean,
        "Q_tube_std_W": q_tube_std,
        "Q_fins_W": q_fins_mean,
        "Q_fins_std_W": q_fins_std,
    }


def write_csv(rows: list[dict], path: Path) -> None:
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = [summarize_case(case) for case in CASES]
    q_ref = next(r["Q_wall_W"] for r in rows if r["Re"] == 200)
    for row in rows:
        row["Nu_wall_proxy_scaled_to_Re200"] = row["Q_wall_W"] / q_ref * NU_WALL_RE200
        row["Q_wall_delta_pct_vs_Re150"] = 100.0 * (row["Q_wall_W"] - next(r["Q_wall_W"] for r in rows if r["Re"] == 150)) / next(r["Q_wall_W"] for r in rows if r["Re"] == 150)

    write_csv(rows, OUT_DIR / "nu_vorticity_summary.csv")

    steady_color = "#8a8f98"
    shed_color = "#c2412d"
    prod_color = "#1f5f8b"
    colors = [
        prod_color if r["Re"] == 200 else shed_color if "shedding" in r["regime"] else steady_color
        for r in rows
    ]

    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    x = [r["Cl_rms"] for r in rows]
    y = [r["Q_wall_W"] for r in rows]
    ax.scatter(x, y, s=90, c=colors, edgecolor="black", linewidth=0.8, zorder=3)
    for r in rows:
        ax.annotate(f"Re {r['Re']}", (r["Cl_rms"], r["Q_wall_W"]), xytext=(7, 4), textcoords="offset points", fontsize=9)
    ax.set_xlabel("Vortex-shedding intensity: late-window Cl RMS")
    ax.set_ylabel("Wall heat transfer Q_wall [W]")
    ax.set_title("Global heat transfer versus vortex intensity")
    ax.grid(True, alpha=0.28)
    ax.text(
        0.02,
        0.96,
        "steady/pre-Hopf",
        transform=ax.transAxes,
        color=steady_color,
        va="top",
        fontsize=10,
        fontweight="bold",
    )
    ax.text(
        0.70,
        0.12,
        "shedding/post-Hopf",
        transform=ax.transAxes,
        color=shed_color,
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig01_Qwall_vs_ClRMS.png", dpi=220)
    fig.savefig(OUT_DIR / "fig01_Qwall_vs_ClRMS.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    selected = [r for r in rows if r["Re"] in (150, 160, 175, 200)]
    labels = [f"Re {r['Re']}\n{r['regime']}" for r in selected]
    xi = np.arange(len(selected))
    width = 0.34
    q_tube = np.array([r["Q_tube_W"] for r in selected])
    q_fins = np.array([r["Q_fins_W"] for r in selected])
    ax.bar(xi, q_tube, width=0.58, label="tube heat", color="#e07a5f")
    ax.bar(xi, q_fins, width=0.58, bottom=q_tube, label="fin heat", color="#3d84a8")
    ax.set_xticks(xi, labels)
    ax.set_ylabel("Q_wall partition [W]")
    ax.set_title("Heat-transfer partition before and after vortex shedding onset")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper left", frameon=False)

    ax2 = ax.twinx()
    ax2.plot(xi, [r["Cl_rms"] for r in selected], color="#222222", marker="o", lw=1.8, label="Cl RMS")
    ax2.set_ylabel("Cl RMS")
    ax2.legend(loc="upper right", frameon=False)

    for i, r in enumerate(selected):
        ax.text(i, r["Q_wall_W"] + 0.015, f"{r['Q_wall_W']:.3f} W", ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig02_heat_partition_steady_vs_shedding.png", dpi=220)
    fig.savefig(OUT_DIR / "fig02_heat_partition_steady_vs_shedding.pdf")
    plt.close(fig)

    fig, (ax_q, ax_cl) = plt.subplots(1, 2, figsize=(12.2, 5.2), gridspec_kw={"width_ratios": [1.35, 1.0]})
    re = np.array([r["Re"] for r in rows])
    order = np.argsort(re)
    ordered = [rows[i] for i in order]
    re = np.array([r["Re"] for r in ordered])
    q_total = np.array([r["Q_wall_W"] for r in ordered])
    q_tube = np.array([r["Q_tube_W"] for r in ordered])
    q_fins = np.array([r["Q_fins_W"] for r in ordered])
    cl_rms = np.array([r["Cl_rms"] for r in ordered])

    ax_q.plot(re, q_total, marker="o", lw=2.2, color="#1f5f8b", label="Q_total = Q_wall")
    ax_q.plot(re, q_tube, marker="s", lw=1.8, color="#e07a5f", label="Q_tube")
    ax_q.plot(re, q_fins, marker="^", lw=1.8, color="#3d84a8", label="Q_fins")
    ax_q.axvspan(150, 160, color="#f2c14e", alpha=0.16, label="onset bracket")
    ax_q.set_xlabel("Re")
    ax_q.set_ylabel("Heat transfer Q [W]")
    ax_q.set_title("Heat-transfer level versus Reynolds number")
    ax_q.grid(True, alpha=0.25)
    ax_q.legend(frameon=False, loc="upper left")

    ax_cl.plot(re, cl_rms, marker="o", lw=2.2, color="#222222")
    ax_cl.axvspan(150, 160, color="#f2c14e", alpha=0.22)
    ax_cl.set_xlabel("Re")
    ax_cl.set_ylabel("Cl RMS")
    ax_cl.set_title("Vortex intensity versus Reynolds number")
    ax_cl.grid(True, alpha=0.25)
    for r in ordered:
        label = "steady" if r["Cl_rms"] < 1e-3 else "shed"
        ax_cl.annotate(label, (r["Re"], r["Cl_rms"]), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)

    fig.suptitle("Heat transfer and vortex intensity across Re", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig03_Q_components_and_ClRMS_vs_Re.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT_DIR / "fig03_Q_components_and_ClRMS_vs_Re.pdf", bbox_inches="tight")
    plt.close(fig)

    readme = f"""# 002_Nu_and_vorticity

Two presentation figures relating heat transfer to vortex presence/intensity.

## Figure 1

`fig01_Qwall_vs_ClRMS.png`

- x-axis: late-window `Cl_rms`, used as a global vortex-shedding intensity metric.
- y-axis: integrated wall heat transfer `Q_wall = Q_tube + Q_fins` from `wallHeatFlux`.
- points: completed production-geometry cases Re=100, 150, 160, 175, 200.
- Re=155 is excluded because it was still running when this figure was generated.

## Figure 2

`fig02_heat_partition_steady_vs_shedding.png`

- stacked bars: heat-transfer partition between tube and fins.
- black line: `Cl_rms`, showing vortex intensity on the same cases.
- comparison highlights transition from steady/pre-Hopf cases to shedding/post-Hopf cases.

## Important note

These figures use `Q_wall` directly. The CSV also contains a `Nu_wall_proxy_scaled_to_Re200`
column, obtained by scaling `Q_wall` to the accepted Re=200 `Nu_wall = {NU_WALL_RE200}`.
This proxy is useful for visual intuition, but full `Nu` for each Re should be recomputed
with the same outlet/LMTD post-processing before publication-grade use.

## Figure 3

`fig03_Q_components_and_ClRMS_vs_Re.png`

- left panel: `Q_total`, `Q_tube`, and `Q_fins` as functions of Reynolds number.
- right panel: `Cl_rms` as a compact vortex-intensity/onset indicator.
- shaded band: current onset bracket between steady Re=150 and shedding Re=160.
"""
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
