from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from V1Study import ACTIVE_RUN_PUBLICATION_DIR, PUBLICATION_DIR, RUN_ROOT, STUDY_SUMMARY_DIR, coeff_paths, load_coeffs


ARTICLE_DIR = PUBLICATION_DIR / "figures"
RUN_ARTICLE_DIR = ACTIVE_RUN_PUBLICATION_DIR / "figures"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def as_float(value: str | None) -> float | None:
    if value in (None, "", "None"):
        return None
    return float(value)


def load_summary() -> list[dict[str, object]]:
    summary_path = STUDY_SUMMARY_DIR / "summary.csv"
    rows: list[dict[str, object]] = []
    with summary_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "case": row["case"],
                    "purpose": row["purpose"],
                    "Re": float(row["Re"]),
                    "mesh": row["mesh"],
                    "upstream_D": float(row["upstream_D"]),
                    "downstream_D": float(row["downstream_D"]),
                    "cells": as_float(row["cells"]),
                    "regime": row["regime"],
                    "Cd_mean": as_float(row["Cd_mean"]),
                    "Cl_rms": as_float(row["Cl_rms"]),
                    "frequency_hz": as_float(row["frequency_hz"]),
                    "St": as_float(row["St"]),
                    "time_max_s": as_float(row["time_max_s"]),
                    "status": row["status"],
                }
            )
    return rows


def save_figure(fig: plt.Figure, stem: str) -> None:
    for directory in (ARTICLE_DIR, RUN_ARTICLE_DIR):
        ensure_dir(directory)
        fig.savefig(directory / f"{stem}.png", dpi=300, bbox_inches="tight")
        fig.savefig(directory / f"{stem}.svg", bbox_inches="tight")
    plt.close(fig)


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 11,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def plot_transition_sweep(rows: list[dict[str, object]]) -> None:
    order = [
        "baseline_medium_Re100",
        "baseline_medium_Re120",
        "baseline_medium_Re140",
        "baseline_medium_Re160",
    ]
    selected = [next(row for row in rows if row["case"] == name) for name in order]
    re_vals = [row["Re"] for row in selected]
    cd_vals = [row["Cd_mean"] for row in selected]
    cl_vals = [row["Cl_rms"] for row in selected]

    fig, axes = plt.subplots(2, 1, figsize=(7.2, 7.0), sharex=True, constrained_layout=True)

    axes[0].plot(re_vals, cd_vals, color="#153b7a", marker="o", linewidth=1.8, markersize=6)
    axes[0].set_ylabel(r"$\overline{C_d}$ [-]")
    axes[0].grid(True, alpha=0.25)
    axes[0].set_title("V1 confined-cylinder transition sweep on the medium mesh")

    axes[1].plot(re_vals, cl_vals, color="#9a3412", marker="s", linewidth=1.8, markersize=6)
    axes[1].set_yscale("log")
    axes[1].set_xlabel("Re [-]")
    axes[1].set_ylabel(r"$C_{l,\mathrm{rms}}$ [-]")
    axes[1].grid(True, alpha=0.25, which="both")
    axes[1].axvline(160.0, color="0.45", linestyle="--", linewidth=1.0)
    axes[1].text(160.5, cl_vals[-1] * 1.1, "onset of periodic shedding", color="0.35", fontsize=9)

    save_figure(fig, "V1_Fig01_transition_sweep")


def plot_mesh_domain_convergence(rows: list[dict[str, object]]) -> None:
    order = [
        "baseline_coarse_Re160",
        "baseline_medium_Re160",
        "long_medium_Re160",
        "long_target100k_Re160",
    ]
    labels = [
        "coarse\n8D/20D",
        "medium\n8D/20D",
        "medium\n10D/30D",
        "~100k\n10D/30D",
    ]
    selected = [next(row for row in rows if row["case"] == name) for name in order]
    x = np.arange(len(selected))
    cd_vals = [row["Cd_mean"] for row in selected]
    st_vals = [row["St"] for row in selected]
    cells = [int(row["cells"]) if row["cells"] is not None else None for row in selected]

    fig, axes = plt.subplots(2, 1, figsize=(7.6, 7.2), sharex=True, constrained_layout=True)

    axes[0].plot(x, cd_vals, color="#153b7a", marker="o", linewidth=1.8, markersize=6)
    axes[0].set_ylabel(r"$\overline{C_d}$ [-]")
    axes[0].grid(True, alpha=0.25)
    axes[0].set_title("V1 Re = 160 mesh and streamwise-domain sensitivity")
    for xi, yi, cell in zip(x, cd_vals, cells):
        axes[0].annotate(f"{cell:,}", (xi, yi), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)

    axes[1].plot(x, st_vals, color="#0f766e", marker="D", linewidth=1.8, markersize=6)
    axes[1].set_ylabel("St [-]")
    axes[1].set_xlabel("Case")
    axes[1].grid(True, alpha=0.25)
    axes[1].set_xticks(x, labels)
    for xi, yi in zip(x, st_vals):
        if yi is not None:
            axes[1].annotate(f"{yi:.4f}", (xi, yi), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)

    save_figure(fig, "V1_Fig02_mesh_domain_convergence")


def plot_re160_cl_tail(rows: list[dict[str, object]]) -> None:
    selections = [
        ("baseline_medium_Re160", "medium 8D/20D", "#153b7a", "-"),
        ("long_medium_Re160", "medium 10D/30D", "#9a3412", "--"),
        ("long_target100k_Re160", "~100k 10D/30D", "#0f766e", "-"),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 4.8), constrained_layout=True)

    for case_name, label, color, line_style in selections:
        case_dir = RUN_ROOT / case_name
        time, _, cl = load_coeffs(coeff_paths(case_dir))
        if time.size == 0:
            continue
        t_end = float(time.max())
        mask = time >= max(0.0, t_end - 1.0)
        t_plot = time[mask] - time[mask][0]
        cl_plot = cl[mask]
        ax.plot(t_plot, cl_plot, label=label, color=color, linestyle=line_style, linewidth=1.7)

    ax.set_xlabel("Late-time window [s]")
    ax.set_ylabel(r"$C_l$ [-]")
    ax.set_title("V1 Re = 160 late-time lift-coefficient response")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, loc="upper right")

    save_figure(fig, "V1_Fig03_re160_cl_tail")


def main() -> None:
    style()
    rows = load_summary()
    plot_transition_sweep(rows)
    plot_mesh_domain_convergence(rows)
    plot_re160_cl_tail(rows)
    print(ARTICLE_DIR)


if __name__ == "__main__":
    main()
