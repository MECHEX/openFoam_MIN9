"""
V1ParityPlots.py
----------------
Parity plots (DNS vs S&O reference):
  - St_DNS vs St_S&O  (+/- 2% band)
  - Cd_DNS vs Cd_S&O  (+/- 2% band)  [requires SO_CD dict below]

Run after `_code/V1Run2Study.py analyze`.
"""

from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent.parent
SIMS_DIR = (
    HERE / "results" / "study_v1" / "runs"
    / "002_data_sahin_owens_poiseuille_verification" / "02_simulations"
)
OUT_DIR = HERE / "results" / "study_v1" / "publication" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── color / marker per beta ────────────────────────────────────────────────────
STYLE = {
    0.30:  {"color": "#0b5ed7", "marker": "o", "label": r"$\beta=0.30$"},
    0.375: {"color": "#6c757d", "marker": "s", "label": r"$\beta=0.375$"},
    0.50:  {"color": "#dc3545", "marker": "^", "label": r"$\beta=0.50$"},
    0.60:  {"color": "#198754", "marker": "D", "label": r"$\beta=0.60$"},
}

# ── S&O Cd reference (add values here when available) ─────────────────────────
# Key: (beta, Re) -> Cd_SO
# Example entry: (0.50, 200): 2.34   # from S&O Table IV / Figure
SO_CD: dict[tuple[float, float], float] = {
    # (0.50, 200): 2.34,   # placeholder — fill from S&O paper
}

# ── load data ─────────────────────────────────────────────────────────────────
records = []
for p in sorted(SIMS_DIR.glob("*/03_processed_data/summary.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    m = d.get("metrics", {})
    c = d.get("comparison", {})
    meta = d.get("metadata", {})
    St_dns = m.get("St")
    Cd_dns = m.get("Cd_mean")
    St_so  = c.get("so_St_crit")
    beta   = float(meta.get("beta", 0))
    Re     = float(meta.get("reynolds", 0))
    if St_dns is None or Cd_dns is None:
        continue
    Cd_so = SO_CD.get((beta, Re))
    records.append({"beta": beta, "Re": Re, "St_dns": St_dns, "St_so": St_so,
                    "Cd_dns": Cd_dns, "Cd_so": Cd_so})

# ── helper: draw one parity panel ─────────────────────────────────────────────
def parity_panel(ax, ref_vals, dns_vals, betas, xlabel, ylabel, title, vmin, vmax):
    margin = 0.03
    lo = vmin * (1 - margin)
    hi = vmax * (1 + margin)
    x_line = np.array([lo, hi])

    # 1:1 line
    ax.plot(x_line, x_line, "k-", lw=1.2, zorder=2, label="1:1")

    # ±2% band
    ax.fill_between(x_line, x_line * 0.98, x_line * 1.02,
                    color="silver", alpha=0.55, zorder=1, label=r"$\pm 2\,\%$")

    # data points grouped by beta
    plotted = set()
    for ref, dns, beta in zip(ref_vals, dns_vals, betas):
        s = STYLE.get(beta, {"color": "#333", "marker": "o", "label": f"b={beta}"})
        lbl = s["label"] if beta not in plotted else "_"
        plotted.add(beta)
        ax.plot(ref, dns, marker=s["marker"], color=s["color"],
                ms=7, linestyle="none", zorder=5, label=lbl,
                markeredgecolor="white", markeredgewidth=0.4)

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.legend(fontsize=8.5, loc="upper left", framealpha=0.9)
    ax.grid(which="major", linestyle="--", lw=0.5, alpha=0.5)
    ax.xaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))


# ── collect St data ────────────────────────────────────────────────────────────
st_ref  = [r["St_so"]  for r in records if r["St_so"]  is not None]
st_dns  = [r["St_dns"] for r in records if r["St_so"]  is not None]
st_beta = [r["beta"]   for r in records if r["St_so"]  is not None]

# ── collect Cd data (only where S&O Cd available) ─────────────────────────────
cd_ref  = [r["Cd_so"]  for r in records if r["Cd_so"]  is not None]
cd_dns  = [r["Cd_dns"] for r in records if r["Cd_so"]  is not None]
cd_beta = [r["beta"]   for r in records if r["Cd_so"]  is not None]

has_cd = len(cd_ref) > 0

# ── figure ─────────────────────────────────────────────────────────────────────
ncols = 2 if has_cd else 1
fig_w = 11.0 if has_cd else 5.5
fig, axes = plt.subplots(1, ncols, figsize=(fig_w, 5.2), dpi=180)
if ncols == 1:
    axes = [axes]

parity_panel(
    axes[0],
    st_ref, st_dns, st_beta,
    xlabel="St  S&O",
    ylabel="St  DNS",
    title="Strouhal number",
    vmin=min(st_ref + st_dns),
    vmax=max(st_ref + st_dns),
)

if has_cd:
    parity_panel(
        axes[1],
        cd_ref, cd_dns, cd_beta,
        xlabel=r"$C_{d,\mathrm{S\&O}}$",
        ylabel=r"$C_{d,\mathrm{DNS}}$",
        title="Drag coefficient",
        vmin=min(cd_ref + cd_dns),
        vmax=max(cd_ref + cd_dns),
    )
else:
    print("NOTE: SO_CD dict is empty — Cd parity panel skipped.")
    print("      Add (beta, Re): Cd_SO entries to SO_CD to enable it.")

fig.suptitle(
    "DNS vs Sahin & Owens (2004) — parity comparison",
    fontsize=11,
)
fig.tight_layout()

out_png = OUT_DIR / "parity_St_Cd.png"
out_svg = OUT_DIR / "parity_St_Cd.svg"
fig.savefig(out_png, dpi=180, bbox_inches="tight")
fig.savefig(out_svg, bbox_inches="tight")
print(f"Saved: {out_png}")
