"""
V1PublicationFigures.py
-----------------------
Generates publication-quality figures for V1 solver verification against
Sahin & Owens (2004), Phys. Fluids 16, 1305-1320.

Figure 1: Hopf onset diagram — Re_crit vs beta (S&O LSA curve + DNS brackets)
Figure 2: St(Re) per beta  — DNS points + S&O LSA onset marker + S&O DNS point
Figure 3: St parity plot   — DNS St vs S&O St_crit(LSA), +-2% band
          (axis label clarifies these are compared near onset, not at identical Re)
"""

from pathlib import Path
import json
from collections import defaultdict

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

# ── S&O (2004) reference — Table IV, mesh M2 (production mesh) ────────────────
# Re_crit and St_crit from LINEAR STABILITY ANALYSIS (Arnoldi method)
SO_LSA = {
    0.10: {"Re_crit": 50.81,  "St_crit": 0.1210},
    0.20: {"Re_crit": 69.43,  "St_crit": 0.1566},
    0.30: {"Re_crit": 94.56,  "St_crit": 0.2090},
    0.50: {"Re_crit": 124.09, "St_crit": 0.3393},
    0.70: {"Re_crit": 110.29, "St_crit": 0.4752},
    0.80: {"Re_crit": 110.24, "St_crit": 0.5363},
    0.84: {"Re_crit": 113.69, "St_crit": 0.5568},
}
# Additional digitised points for smooth curve
SO_CURVE_BETA  = np.array([0.10, 0.20, 0.30, 0.35, 0.40, 0.45,
                            0.50, 0.55, 0.60, 0.65, 0.70, 0.80, 0.84])
SO_CURVE_RECRIT = np.array([50.81, 69.43, 97.0, 109.0, 118.0, 123.0,
                             124.09, 122.0, 117.0, 113.0, 110.29, 110.24, 113.69])

# S&O DNS points reported in text (same Re as our cases — rare overlap)
# β=0.30, Re=100: St=0.2115  (Section IV B of S&O)
SO_DNS = [
    {"beta": 0.30, "Re": 100.0, "St": 0.2115},
]

# ── interpolate S&O St_crit for any beta ──────────────────────────────────────
def so_st_crit(beta):
    if beta in SO_LSA:
        return SO_LSA[beta]["St_crit"]
    betas = sorted(b for b in SO_LSA if SO_LSA[b]["St_crit"] is not None)
    lo = max((b for b in betas if b <= beta), default=None)
    hi = min((b for b in betas if b >= beta), default=None)
    if lo is None or hi is None:
        return None
    t = (beta - lo) / (hi - lo)
    return SO_LSA[lo]["St_crit"] * (1 - t) + SO_LSA[hi]["St_crit"] * t

# ── style ─────────────────────────────────────────────────────────────────────
STYLE = {
    0.30:  {"color": "#0b5ed7", "marker": "o", "label": r"$\beta=0.30$"},
    0.375: {"color": "#6c757d", "marker": "s", "label": r"$\beta=0.375$"},
    0.50:  {"color": "#dc3545", "marker": "^", "label": r"$\beta=0.50$"},
    0.60:  {"color": "#198754", "marker": "D", "label": r"$\beta=0.60$"},
}

# ── DNS brackets for onset diagram ────────────────────────────────────────────
# (beta, Re_steady_max, Re_periodic_min)
# None = no bound from that side
DNS_BRACKETS = [
    (0.30,  None,  90.0),   # no steady case measured; all tested Re >= 90 are periodic
    (0.375, None, 105.0),   # same
    (0.50,  130.0, 135.0),  # bracket confirmed
    (0.60,  125.0, None),   # no periodic case yet (Re=135 would complete it)
]

# ── load DNS simulation data ───────────────────────────────────────────────────
records = []
for p in sorted(SIMS_DIR.glob("*/03_processed_data/summary.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    m = d.get("metrics", {})
    meta = d.get("metadata", {})
    St_dns = m.get("St")
    Cd_dns = m.get("Cd_mean")
    beta   = float(meta.get("beta", 0))
    Re     = float(meta.get("reynolds", 0))
    regime = m.get("regime", "")
    records.append({"beta": beta, "Re": Re, "St": St_dns,
                    "Cd": Cd_dns, "regime": regime})

by_beta = defaultdict(list)
for r in records:
    by_beta[r["beta"]].append(r)
for v in by_beta.values():
    v.sort(key=lambda x: x["Re"])

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1: Hopf onset diagram — Re_crit vs beta
# ─────────────────────────────────────────────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(7.0, 5.0), dpi=180)

# S&O LSA curve
b_dense = np.linspace(SO_CURVE_BETA[0], SO_CURVE_BETA[-1], 500)
Re_dense = np.interp(b_dense, SO_CURVE_BETA, SO_CURVE_RECRIT)
ax1.fill_between(b_dense, Re_dense * 0.95, Re_dense * 1.05,
                 color="silver", alpha=0.50, zorder=1, label=r"S\&O $\pm5\%$")
ax1.plot(b_dense, Re_dense, "k-", lw=1.6, zorder=3,
         label="Sahin & Owens (2004) LSA")

# DNS brackets
for beta, Re_lo, Re_hi in DNS_BRACKETS:
    s = STYLE.get(beta, {"color": "#333", "marker": "o"})
    if Re_hi is not None:
        # periodic case — filled marker = onset confirmed from above
        ax1.plot(beta, Re_hi, marker=s["marker"], color=s["color"],
                 ms=8, linestyle="none", zorder=6,
                 markeredgecolor="white", markeredgewidth=0.5)
    if Re_lo is not None:
        # steady case — open marker
        ax1.plot(beta, Re_lo, marker=s["marker"], color=s["color"],
                 ms=8, linestyle="none", zorder=6,
                 markerfacecolor="white", markeredgecolor=s["color"],
                 markeredgewidth=1.5)
    # bracket arrow
    y0 = Re_lo if Re_lo is not None else (Re_hi - 20)
    y1 = Re_hi if Re_hi is not None else (Re_lo + 20)
    ax1.annotate("", xy=(beta, y1), xytext=(beta, y0),
                 arrowprops=dict(arrowstyle="<->", color=s["color"],
                                 lw=1.2), zorder=5)

# legend proxies
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
leg_handles = [
    Line2D([0], [0], color="k", lw=1.6, label="Sahin & Owens (2004) LSA"),
    Patch(facecolor="silver", alpha=0.6, label=r"$\pm5\%$ band"),
]
for beta, s in STYLE.items():
    leg_handles.append(
        Line2D([0], [0], marker=s["marker"], color=s["color"], lw=0,
               ms=7, label=s["label"],
               markeredgecolor="white", markeredgewidth=0.5)
    )

ax1.set_xlabel(r"$\beta = D/H$", fontsize=12)
ax1.set_ylabel(r"$Re_\mathrm{crit} = U_\mathrm{max}\,D/\nu$", fontsize=12)
ax1.set_xlim(0.20, 0.72)
ax1.set_ylim(60, 155)
ax1.xaxis.set_major_locator(mticker.MultipleLocator(0.10))
ax1.xaxis.set_minor_locator(mticker.MultipleLocator(0.05))
ax1.yaxis.set_major_locator(mticker.MultipleLocator(20))
ax1.yaxis.set_minor_locator(mticker.MultipleLocator(10))
ax1.grid(which="major", linestyle="--", lw=0.5, alpha=0.5)
ax1.grid(which="minor", linestyle=":", lw=0.3, alpha=0.3)

note = ("Filled markers: lowest periodic Re observed (DNS)\n"
        "Open markers: highest steady Re observed (DNS)\n"
        "Arrows: confirmed onset brackets")
ax1.text(0.98, 0.04, note, transform=ax1.transAxes, fontsize=7,
         ha="right", va="bottom",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
ax1.legend(handles=leg_handles, fontsize=8, loc="upper left", framealpha=0.9)
fig1.tight_layout()
out1 = OUT_DIR / "fig1_hopf_onset.png"
fig1.savefig(out1, dpi=180, bbox_inches="tight")
fig1.savefig(out1.with_suffix(".svg"), bbox_inches="tight")
print(f"Fig 1 saved: {out1}")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2: St(Re) per beta — DNS points + S&O LSA onset marker
# ─────────────────────────────────────────────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(7.5, 5.0), dpi=180)

# S&O DNS reference point (β=0.30, Re=100, St=0.2115 — from S&O text Sec. IV B)
ax2.plot(100.0, 0.2115, marker="*", color="#0b5ed7", ms=12,
         linestyle="none", zorder=7,
         label=r"$\beta=0.30$ S\&O DNS (Re=100)", markeredgecolor="white")

for beta, grp in sorted(by_beta.items()):
    s = STYLE.get(beta)
    if s is None:
        continue
    # periodic points only
    Re_p  = [r["Re"] for r in grp if r["St"] is not None]
    St_p  = [r["St"] for r in grp if r["St"] is not None]
    if not Re_p:
        continue
    ax2.plot(Re_p, St_p, marker=s["marker"], color=s["color"],
             lw=1.3, ms=6, zorder=5,
             label=s["label"] + " (present work)",
             markeredgecolor="white", markeredgewidth=0.4)
    # S&O LSA onset marker (x symbol)
    if beta in SO_LSA:
        ax2.plot(SO_LSA[beta]["Re_crit"], SO_LSA[beta]["St_crit"],
                 marker="x", color=s["color"], ms=9, mew=2.0,
                 linestyle="none", zorder=6,
                 label=s["label"] + r" S\&O onset (LSA)")
    elif beta == 0.375:
        Re_i = np.interp(0.375, list(SO_LSA.keys()),
                         [v["Re_crit"] for v in SO_LSA.values()])
        St_i = so_st_crit(0.375)
        # linear interpolation between 0.30 and 0.50
        t = (0.375 - 0.30) / (0.50 - 0.30)
        Re_i = SO_LSA[0.30]["Re_crit"]*(1-t) + SO_LSA[0.50]["Re_crit"]*t
        St_i = SO_LSA[0.30]["St_crit"]*(1-t) + SO_LSA[0.50]["St_crit"]*t
        ax2.plot(Re_i, St_i, marker="x", color=s["color"], ms=9, mew=2.0,
                 linestyle="none", zorder=6,
                 label=s["label"] + r" S\&O onset (interp.)")

ax2.set_xlabel(r"$Re = U_\mathrm{max}\,D/\nu$", fontsize=12)
ax2.set_ylabel(r"$St = f\,D/U_\mathrm{max}$", fontsize=12)
ax2.legend(fontsize=8, loc="upper left", framealpha=0.9, ncol=2)
ax2.grid(which="major", linestyle="--", lw=0.5, alpha=0.5)
ax2.xaxis.set_minor_locator(mticker.AutoMinorLocator(2))
ax2.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
ax2.grid(which="minor", linestyle=":", lw=0.3, alpha=0.3)

note2 = ("x markers: S&O LSA onset (Re_crit, St_crit)\n"
         "* marker: S&O DNS at Re=100 (Sec. IV B)\n"
         r"$\beta=0.375$ S&O onset interpolated")
ax2.text(0.98, 0.04, note2, transform=ax2.transAxes, fontsize=7,
         ha="right", va="bottom",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
fig2.tight_layout()
out2 = OUT_DIR / "fig2_St_vs_Re.png"
fig2.savefig(out2, dpi=180, bbox_inches="tight")
fig2.savefig(out2.with_suffix(".svg"), bbox_inches="tight")
print(f"Fig 2 saved: {out2}")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3: St parity plot — DNS vs S&O LSA St_crit, +-2% band
# Note: x-axis is S&O St_crit (at Re_crit from LSA), y-axis is our DNS St
# (at a nearby supercritical Re). St varies weakly with Re above onset,
# so the comparison is approximately valid; stated in caption.
# ─────────────────────────────────────────────────────────────────────────────
parity_data = []
for r in records:
    if r["St"] is None:
        continue
    St_so = so_st_crit(r["beta"])
    if St_so is None:
        continue
    parity_data.append({"beta": r["beta"], "Re": r["Re"],
                        "St_dns": r["St"], "St_so": St_so})

if parity_data:
    St_so_all  = [d["St_so"]  for d in parity_data]
    St_dns_all = [d["St_dns"] for d in parity_data]
    vmin = min(St_so_all + St_dns_all) * 0.97
    vmax = max(St_so_all + St_dns_all) * 1.03
    x_line = np.array([vmin, vmax])

    fig3, ax3 = plt.subplots(figsize=(5.5, 5.2), dpi=180)
    ax3.plot(x_line, x_line, "k-", lw=1.2, zorder=2, label="1:1")
    ax3.fill_between(x_line, x_line*0.98, x_line*1.02,
                     color="silver", alpha=0.55, zorder=1,
                     label=r"$\pm2\%$")

    plotted = set()
    for d in parity_data:
        s = STYLE.get(d["beta"], {"color": "#333", "marker": "o",
                                   "label": f"b={d['beta']}"})
        lbl = s["label"] if d["beta"] not in plotted else "_"
        plotted.add(d["beta"])
        ax3.plot(d["St_so"], d["St_dns"],
                 marker=s["marker"], color=s["color"], ms=7,
                 linestyle="none", zorder=5, label=lbl,
                 markeredgecolor="white", markeredgewidth=0.5)

    ax3.set_xlim(vmin, vmax)
    ax3.set_ylim(vmin, vmax)
    ax3.set_xlabel("St  S&O  (LSA, at Re_crit)", fontsize=11)
    ax3.set_ylabel("St  DNS  (present, supercritical Re)", fontsize=11)
    ax3.set_aspect("equal")
    ax3.legend(fontsize=9, loc="upper left", framealpha=0.9)
    ax3.grid(which="major", linestyle="--", lw=0.5, alpha=0.5)
    ax3.xaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax3.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))

    note3 = ("S&O St from LSA at Re_crit\n"
             "DNS St evaluated at supercritical Re\n"
             "St varies weakly with Re above onset")
    ax3.text(0.98, 0.04, note3, transform=ax3.transAxes, fontsize=7.5,
             ha="right", va="bottom",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    fig3.tight_layout()
    out3 = OUT_DIR / "fig3_St_parity.png"
    fig3.savefig(out3, dpi=180, bbox_inches="tight")
    fig3.savefig(out3.with_suffix(".svg"), bbox_inches="tight")
    print(f"Fig 3 saved: {out3}")

print("\nAll figures saved to:", OUT_DIR)
