"""
V2PublicationNuRePlot.py
------------------------
Publication-oriented article comparison figures for V2A thermal verification.

The figure set separates what the two reference papers actually provide:
  - Bharti et al. (2007): Nu(Re, Pr) for steady low-Re cross-flow, no St/Cd/Cl curve.
  - Lange et al. (1998): Nu correlation, St correlation/onset, and digitized Cd trend.

The present data are read from run 004 O-grid results.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import V2AStudy as base


CODE_DIR = Path(__file__).resolve().parent
REPO_CASE = CODE_DIR.parent
RUN_DIR = REPO_CASE / "results" / "study_v2a" / "runs" / "004_data_v2a_ogrid_cylinder_validation"
SUMMARY_CSV = RUN_DIR / "summary.csv"
PLOTS_DIR = RUN_DIR / "plots"
WORK_ROOT = Path(r"C:\openfoam-case\VV_cases\V2_thermal_run004")

BHARTI_RE_RANGE = (10.0, 45.0)
LANGE_RE_RANGE = (1.0e-4, 200.0)
LANGE_RE_CRIT = 45.9
BHARTI_PR_FOR_TABLE = 0.7

BHARTI_CWT_TABLE = {
    10.0: 1.8623,
    20.0: 2.4653,
    40.0: 3.2825,
}

BHARTI_UHF_TABLE = {
    10.0: 2.0400,
    20.0: 2.7788,
    40.0: 3.7755,
}

# Approximate present-result readings from Lange et al. Fig. 4/5. These are
# digitized/working values, not tabulated values from the paper.
LANGE_CD_DIGITIZED = [
    (1.0, 10.0),
    (2.0, 6.0),
    (5.0, 3.6),
    (10.0, 2.5),
    (20.0, 1.8),
    (40.0, 1.45),
    (100.0, 1.2),
]

LANGE_ST_SAMPLE_RE = [50.0, 60.0, 70.0, 100.0, 150.0, 200.0]
LANGE_NU_SAMPLE_RE = [10.0, 20.0, 40.0, 45.0, 60.0, 100.0, 150.0, 200.0]
REFERENCE_BANDS = (0.10, 0.05)


def nu_lange(reynolds: float) -> float:
    """Lange et al. (1998) Nu correlation, PDF-checked plus sign in exponent."""
    return base.nu_lange(reynolds)


def nu_bharti_cwt(reynolds: float, prandtl: float = BHARTI_PR_FOR_TABLE) -> float:
    return 0.6738 * reynolds**0.4679 * prandtl ** (1.0 / 3.0)


def nu_bharti_uhf(reynolds: float, prandtl: float = BHARTI_PR_FOR_TABLE) -> float:
    return 0.7837 * reynolds**0.4658 * prandtl ** (1.0 / 3.0)


def st_lange_williamson(reynolds: float) -> float:
    return -3.3265 / reynolds + 0.1816 + 1.6e-4 * reynolds


def read_force_tail(case_name: str) -> dict[str, float | None]:
    coeff_file = WORK_ROOT / case_name / "postProcessing" / "forceCoeffs" / "0" / "coefficient.dat"
    if not coeff_file.exists():
        return {"Cd_tail_mean_from_file": None, "Cl_tail_mean": None, "Cl_tail_rms": None}

    rows: list[tuple[float, float, float]] = []
    for line in coeff_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        rows.append((float(parts[0]), float(parts[1]), float(parts[4])))
    if not rows:
        return {"Cd_tail_mean_from_file": None, "Cl_tail_mean": None, "Cl_tail_rms": None}

    tail = rows[-max(1, len(rows) // 5) :]
    cds = [row[1] for row in tail]
    cls = [row[2] for row in tail]
    cl_mean = sum(cls) / len(cls)
    cl_rms = math.sqrt(sum((value - cl_mean) ** 2 for value in cls) / len(cls))
    return {
        "Cd_tail_mean_from_file": sum(cds) / len(cds),
        "Cl_tail_mean": cl_mean,
        "Cl_tail_rms": cl_rms,
    }


def read_present() -> list[dict[str, float | str | None]]:
    rows: list[dict[str, float | str | None]] = []
    with SUMMARY_CSV.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if not row.get("Nu_tail_mean"):
                continue
            force_tail = read_force_tail(row["case"])
            re_val = float(row["Re"])
            st_value = float(row["St_present"]) if row.get("St_present") else None
            rows.append(
                {
                    "case": row["case"],
                    "Re": re_val,
                    "Nu": float(row["Nu_tail_mean"]),
                    "Cd": float(row["Cd_tail_mean"]) if row.get("Cd_tail_mean") else None,
                    "St": st_value,
                    "Cl_rms": float(row["Cl_tail_rms"]) if row.get("Cl_tail_rms") else force_tail["Cl_tail_rms"],
                    "Cl_mean": float(row["Cl_tail_mean"]) if row.get("Cl_tail_mean") else force_tail["Cl_tail_mean"],
                    "regime_note": "steady; St undefined" if re_val < LANGE_RE_CRIT and st_value is None else "Cl FFT tail peak",
                }
            )
    return sorted(rows, key=lambda item: float(item["Re"]))


def write_tables(present: list[dict[str, float | str | None]]) -> tuple[Path, Path, Path]:
    nu_out = RUN_DIR / "publication_Nu_Re_data.csv"
    long_out = RUN_DIR / "publication_articles_vs_present_data.csv"
    plan_out = RUN_DIR / "publication_article_comparison_plan.md"
    present_max = max((float(row["Re"]) for row in present), default=0.0)
    present_min = min((float(row["Re"]) for row in present), default=0.0)
    steady_note = "all current cases are below Lange Re_c = 45.9" if present_max < LANGE_RE_CRIT else "includes cases above Lange Re_c = 45.9"

    with nu_out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["source", "case", "Re", "Nu", "note"])
        for re_val, nu_val in sorted(BHARTI_CWT_TABLE.items()):
            writer.writerow(["Bharti et al. (2007)", "", re_val, nu_val, "CWT tabulated reference"])
        for re_val in LANGE_NU_SAMPLE_RE:
            writer.writerow(["Lange et al. (1998)", "", re_val, nu_lange(re_val), "correlation value"])
        for row in present:
            writer.writerow(["Present work", row["case"], row["Re"], row["Nu"], "run 004 O-grid"])

    with long_out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["quantity", "source", "case", "Re", "value", "note"])
        for re_val, nu_val in sorted(BHARTI_CWT_TABLE.items()):
            writer.writerow(["Nu", "Bharti et al. (2007)", "", re_val, nu_val, "CWT tabulated"])
        for re_val, nu_val in sorted(BHARTI_UHF_TABLE.items()):
            writer.writerow(["Nu", "Bharti et al. (2007)", "", re_val, nu_val, "UHF tabulated, not present boundary condition"])
        for re_val in [10.0, 20.0, 40.0, 45.0]:
            writer.writerow(["Nu", "Bharti et al. (2007)", "", re_val, nu_bharti_cwt(re_val), "CWT power-law fit"])
        for re_val in LANGE_NU_SAMPLE_RE:
            writer.writerow(["Nu", "Lange et al. (1998)", "", re_val, nu_lange(re_val), "correlation"])
        for re_val in LANGE_ST_SAMPLE_RE:
            writer.writerow(["St", "Lange et al. (1998)", "", re_val, st_lange_williamson(re_val), "Williamson fit cited by Lange"])
        for re_val, cd_val in LANGE_CD_DIGITIZED:
            writer.writerow(["Cd", "Lange et al. (1998)", "", re_val, cd_val, "approximate digitized reading"])
        for row in present:
            writer.writerow(["Nu", "Present work", row["case"], row["Re"], row["Nu"], "run 004 O-grid"])
            writer.writerow(["Cd", "Present work", row["case"], row["Re"], row["Cd"], "tail mean from forceCoeffs"])
            writer.writerow(["St", "Present work", row["case"], row["Re"], row["St"], row["regime_note"]])
            writer.writerow(["Cl_rms", "Present work", row["case"], row["Re"], row["Cl_rms"], "tail RMS; no article curve"])

    lines = [
        "# V2A article comparison and next simulations",
        "",
        "## Reference ranges",
        "",
        "| source | usable quantities here | Re range | max Re | notes |",
        "|---|---|---:|---:|---|",
        "| Bharti et al. (2007) | Nu for CWT/UHF steady cross-flow | 10-45 | 45 | no useful Cd, Cl, or St curve for our comparison |",
        "| Lange et al. (1998) | Nu, St, onset, digitized Cd trend | 1e-4-200 | 200 | Cl is not given as a usable Cl(Re) curve |",
        f"| Present work, run 004 | Nu, Cd, Cl tail diagnostics; St only once shedding exists | {present_min:g}-{present_max:g} so far | {present_max:g} | {steady_note} |",
        "",
        "## Nu correlation sign check",
        "",
        "The Lange Nu fit used here is the PDF-checked version already implemented in `V2AStudy.py`:",
        "",
        "`Nu = 0.082 Re^0.5 + 0.734 Re^x`, with `x = 0.05 + 0.226 Re^0.085`.",
        "",
        "The alternative `x = -0.05 + ...` would give the lower values listed in the scratch notes, but it does not match the local Lange PDF extraction.",
        "",
        "## Recommended next simulations",
        "",
        "| priority | case | role | suggested endTime | suggested writeInterval | main metrics |",
        "|---:|---|---|---:|---:|---|",
        "| 1 | Re45_ogrid | closes Bharti max-Re point and sits just below Lange onset | 120 s | 0.5 s | Nu, Cd, bounded T, no St expected |",
        "| 2 | Re60_ogrid | first clean shedding case above Re_c | 80 s | 0.1 s | time-mean Nu, Cd, St from Cl FFT |",
        "| 3 | Re100_ogrid | mid-range Lange unsteady validation | 60 s | 0.05 s | time-mean Nu, Cd, St |",
        "| 4 | Re200_ogrid | maximum Lange-range check | 40 s | 0.025 s | time-mean Nu, Cd, St; mesh sensitivity likely needed |",
        "",
        "If Re200 differs by more than about 5% in Nu or St, repeat Re100/Re200 on a refined O-grid before using the high-Re points in the article.",
    ]
    plan_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return nu_out, long_out, plan_out


def _curve(start: float, stop: float, n: int) -> list[float]:
    return [start + i * (stop - start) / max(1, n - 1) for i in range(n)]


def _reference_band(values: list[float], pct: float) -> tuple[list[float], list[float]]:
    return (
        [value * (1.0 - pct) for value in values],
        [value * (1.0 + pct) for value in values],
    )


def _add_formula_box(ax, text: str, xy: tuple[float, float] = (0.98, 0.08), ha: str = "right") -> None:
    ax.text(
        xy[0],
        xy[1],
        text,
        transform=ax.transAxes,
        ha=ha,
        va="bottom",
        fontsize=8.5,
        color="#292524",
        bbox={"boxstyle": "round,pad=0.35", "fc": "#f8fafc", "ec": "#cbd5e1", "lw": 0.8, "alpha": 0.92},
    )


def _plot_reference_bands(ax, x_values: list[float], y_values: list[float], *, label: bool = False, alpha_scale: float = 1.0) -> None:
    for pct, alpha in ((REFERENCE_BANDS[0], 0.12 * alpha_scale), (REFERENCE_BANDS[1], 0.24 * alpha_scale)):
        ax.fill_between(
            x_values,
            *_reference_band(y_values, pct),
            color="#9ca3af",
            alpha=alpha,
            lw=0,
            label=f"literature +/-{pct * 100.0:.0f}%" if label else None,
        )


def plot_nu(present: list[dict[str, float | str | None]]) -> tuple[Path, Path]:
    re_lange = _curve(10.0, LANGE_RE_RANGE[1], 400)
    re_bharti = _curve(BHARTI_RE_RANGE[0], BHARTI_RE_RANGE[1], 150)
    nu_lange_values = [nu_lange(re_val) for re_val in re_lange]
    nu_bharti_values = [nu_bharti_cwt(re_val) for re_val in re_bharti]

    fig, ax = plt.subplots(figsize=(7.6, 4.9), dpi=220)
    _plot_reference_bands(ax, re_lange, nu_lange_values, label=True)
    _plot_reference_bands(ax, re_bharti, nu_bharti_values)
    ax.plot(re_lange, nu_lange_values, color="#8a5a14", lw=1.7, label="Lange et al. (1998), Nu fit")
    ax.plot(re_bharti, nu_bharti_values, color="#1f5f99", lw=1.4, ls=":", label="Bharti et al. (2007), CWT fit")
    ax.plot(
        list(BHARTI_CWT_TABLE),
        list(BHARTI_CWT_TABLE.values()),
        linestyle="none",
        marker="s",
        ms=6.2,
        color="#1f5f99",
        label="Bharti et al. (2007), CWT table",
    )
    ax.plot(
        [float(row["Re"]) for row in present],
        [float(row["Nu"]) for row in present],
        linestyle="-",
        marker="o",
        ms=7.0,
        markeredgewidth=1.0,
        markeredgecolor="#111827",
        color="#d9480f",
        label="Present work, O-grid",
        zorder=5,
    )
    ax.axvspan(*BHARTI_RE_RANGE, color="#dbeafe", alpha=0.18, lw=0)
    ax.axvline(LANGE_RE_CRIT, color="#44403c", lw=1.0, ls="--")
    ax.text(LANGE_RE_CRIT + 3, 1.55, r"$Re_c=45.9$", fontsize=8.5, color="#44403c")
    ax.set_xlabel(r"$Re$")
    ax.set_ylabel(r"$\overline{Nu}$")
    ax.set_xlim(5.0, 210.0)
    ax.set_ylim(1.2, 8.2)
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    _add_formula_box(ax, r"Present: $\overline{Nu}=\frac{D}{T_w-T_\infty}\langle\mathrm{snGrad}(T)\rangle_A$")
    ax.legend(frameon=False, fontsize=8.0, loc="upper left")
    fig.tight_layout()

    out_png = PLOTS_DIR / "V2A_Nu_Re_articles_vs_present.png"
    out_svg = PLOTS_DIR / "V2A_Nu_Re_articles_vs_present.svg"
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    fig.savefig(out_svg, bbox_inches="tight")
    plt.close(fig)
    return out_png, out_svg


def plot_st(present: list[dict[str, float | str | None]]) -> tuple[Path, Path]:
    re_lange = _curve(50.0, LANGE_RE_RANGE[1], 400)
    st_lange_values = [st_lange_williamson(re_val) for re_val in re_lange]

    fig, ax = plt.subplots(figsize=(7.6, 4.9), dpi=220)
    _plot_reference_bands(ax, re_lange, st_lange_values, label=True)
    ax.plot(re_lange, st_lange_values, color="#7c2d12", lw=1.8, label="Lange/Williamson St fit")
    st_rows = [row for row in present if row["St"] is not None]
    if st_rows:
        ax.plot(
            [float(row["Re"]) for row in st_rows],
            [float(row["St"]) for row in st_rows],
            linestyle="none",
            marker="o",
            ms=7.5,
            color="#d9480f",
            markeredgecolor="#111827",
            label="Present work: St from Cl FFT",
            zorder=6,
        )
    ax.set_xlabel(r"$Re$")
    ax.set_ylabel(r"$St$")
    ax.set_xlim(50.0, 210.0)
    ax.set_ylim(0.10, 0.23)
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    _add_formula_box(ax, r"Present: $St=\frac{fD}{U_\infty}$" + "\n" + r"$f$: FFT peak of $C_L(t)$", xy=(0.04, 0.08), ha="left")
    ax.legend(frameon=False, fontsize=8.0, loc="lower right")
    fig.tight_layout()

    out_png = PLOTS_DIR / "V2A_St_Re_articles_vs_present.png"
    out_svg = PLOTS_DIR / "V2A_St_Re_articles_vs_present.svg"
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    fig.savefig(out_svg, bbox_inches="tight")
    plt.close(fig)
    return out_png, out_svg


def plot_cd(present: list[dict[str, float | str | None]]) -> tuple[Path, Path]:
    cd_re = [row[0] for row in LANGE_CD_DIGITIZED]
    cd_values = [row[1] for row in LANGE_CD_DIGITIZED]

    fig, ax = plt.subplots(figsize=(7.6, 4.9), dpi=220)
    _plot_reference_bands(ax, cd_re, cd_values, label=True)
    ax.plot(
        cd_re,
        cd_values,
        color="#334155",
        lw=1.4,
        ls="--",
        marker="o",
        ms=4.5,
        label="Lange et al. (1998), digitized Cd trend",
    )
    cd_rows = [row for row in present if row["Cd"] is not None]
    ax.plot(
        [float(row["Re"]) for row in cd_rows],
        [float(row["Cd"]) for row in cd_rows],
        color="#d9480f",
        lw=1.3,
        marker="o",
        ms=7.0,
        markeredgecolor="#111827",
        label="Present work, O-grid",
        zorder=5,
    )
    ax.axvspan(*BHARTI_RE_RANGE, color="#dbeafe", alpha=0.18, lw=0, label="Bharti: no Cd curve")
    ax.set_xlabel(r"$Re$")
    ax.set_ylabel(r"$C_D$")
    ax.set_xlim(0.0, 210.0)
    ax.set_ylim(0.8, 10.8)
    ax.grid(True, color="#d6d3d1", lw=0.6, alpha=0.85)
    ax.legend(frameon=False, fontsize=8.0, loc="upper right")
    fig.tight_layout()

    out_png = PLOTS_DIR / "V2A_Cd_Re_articles_vs_present.png"
    out_svg = PLOTS_DIR / "V2A_Cd_Re_articles_vs_present.svg"
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    fig.savefig(out_svg, bbox_inches="tight")
    plt.close(fig)
    return out_png, out_svg


def plot_dashboard(present: list[dict[str, float | str | None]]) -> tuple[Path, Path]:
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2), dpi=200)
    ax_nu, ax_st, ax_cd = axes.flatten()

    re_lange_nu = _curve(10.0, LANGE_RE_RANGE[1], 300)
    re_bharti = _curve(BHARTI_RE_RANGE[0], BHARTI_RE_RANGE[1], 120)
    dashboard_nu_lange = [nu_lange(re_val) for re_val in re_lange_nu]
    dashboard_nu_bharti = [nu_bharti_cwt(re_val) for re_val in re_bharti]
    _plot_reference_bands(ax_nu, re_lange_nu, dashboard_nu_lange, label=True, alpha_scale=0.9)
    _plot_reference_bands(ax_nu, re_bharti, dashboard_nu_bharti, alpha_scale=0.9)
    ax_nu.plot(re_lange_nu, dashboard_nu_lange, color="#8a5a14", lw=1.5, label="Lange Nu")
    ax_nu.plot(re_bharti, dashboard_nu_bharti, color="#1f5f99", lw=1.2, ls=":", label="Bharti CWT fit")
    ax_nu.plot(list(BHARTI_CWT_TABLE), list(BHARTI_CWT_TABLE.values()), "s", color="#1f5f99", ms=5.0, label="Bharti CWT table")
    ax_nu.plot([float(r["Re"]) for r in present], [float(r["Nu"]) for r in present], "o-", color="#d9480f", ms=5.5, label="Present")
    ax_nu.set_xlim(5, 210)
    ax_nu.set_ylim(1.2, 8.2)
    ax_nu.set_xlabel("Re")
    ax_nu.set_ylabel("Nu")
    ax_nu.grid(True, color="#d6d3d1", lw=0.5, alpha=0.8)
    _add_formula_box(ax_nu, r"$\overline{Nu}=\frac{D}{T_w-T_\infty}\langle\mathrm{snGrad}(T)\rangle_A$", xy=(0.98, 0.05))
    ax_nu.legend(frameon=False, fontsize=7.3)

    re_lange_st = _curve(50.0, LANGE_RE_RANGE[1], 300)
    dashboard_st = [st_lange_williamson(re_val) for re_val in re_lange_st]
    _plot_reference_bands(ax_st, re_lange_st, dashboard_st, label=True, alpha_scale=0.9)
    ax_st.plot(re_lange_st, dashboard_st, color="#7c2d12", lw=1.5, label="Lange/Williamson")
    st_rows = [r for r in present if r["St"] is not None]
    if st_rows:
        ax_st.plot([float(r["Re"]) for r in st_rows], [float(r["St"]) for r in st_rows], "o", color="#d9480f", ms=5.5, label="Present FFT")
    ax_st.set_xlim(50, 210)
    ax_st.set_ylim(0.10, 0.23)
    ax_st.set_xlabel("Re")
    ax_st.set_ylabel("St")
    ax_st.grid(True, color="#d6d3d1", lw=0.5, alpha=0.8)
    _add_formula_box(ax_st, r"$St=fD/U_\infty$", xy=(0.04, 0.05), ha="left")
    ax_st.legend(frameon=False, fontsize=7.3)

    cd_re = [row[0] for row in LANGE_CD_DIGITIZED]
    cd_values = [row[1] for row in LANGE_CD_DIGITIZED]
    _plot_reference_bands(ax_cd, cd_re, cd_values, label=True, alpha_scale=0.9)
    ax_cd.plot(cd_re, cd_values, "o--", color="#334155", ms=4.0, label="Lange digitized")
    cd_rows = [r for r in present if r["Cd"] is not None]
    ax_cd.plot([float(r["Re"]) for r in cd_rows], [float(r["Cd"]) for r in cd_rows], "o-", color="#d9480f", ms=5.5, label="Present")
    ax_cd.set_xlim(0, 210)
    ax_cd.set_ylim(0.8, 10.8)
    ax_cd.set_xlabel("Re")
    ax_cd.set_ylabel("Cd")
    ax_cd.grid(True, color="#d6d3d1", lw=0.5, alpha=0.8)
    ax_cd.legend(frameon=False, fontsize=7.3)

    fig.tight_layout()
    out_png = PLOTS_DIR / "V2A_articles_vs_present_dashboard.png"
    out_svg = PLOTS_DIR / "V2A_articles_vs_present_dashboard.svg"
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    fig.savefig(out_svg, bbox_inches="tight")
    plt.close(fig)
    return out_png, out_svg


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    present = read_present()
    table_paths = write_tables(present)
    plot_paths = [
        *plot_nu(present),
        *plot_st(present),
        *plot_cd(present),
        *plot_dashboard(present),
    ]
    for path in table_paths:
        print(f"Wrote {path}")
    for path in plot_paths:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
