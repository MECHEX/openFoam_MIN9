"""
plot_hopf_onset.py
------------------
Hopf bifurcation onset Re_crit vs blockage ratio beta = D/H.

Reference: Sahin & Owens (2004), Phys. Fluids 16, 1305-1320.
  - Table IV: beta = 0.10, 0.20, 0.30, 0.50, 0.70, 0.80, 0.84
  - Figure (digitised): beta = 0.35, 0.40, 0.45 (additional intermediate points)
DNS data:  V1 run 002 pilot subset (Poiseuille inlet, medium mesh, 5 s).

Output: study_summary/002_.../plots/hopf_onset_vs_beta.png
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── paths ──────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent.parent
OUT_DIR = (
    HERE / "results" / "study_v1" / "study_summary"
    / "002_data_sahin_owens_poiseuille_verification" / "plots"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Sahin & Owens (2004) ───────────────────────────────────────────────────────
# Re = U_max * D / nu,  St = f * D / U_max
# Table IV (beta=0.10, 0.20, 0.80, 0.84) + intermediate points digitised from figure
SO_BETA  = np.array([0.10,  0.20,  0.30, 0.35,  0.40,  0.45,  0.50,  0.55,  0.60,  0.65,  0.70,  0.80,   0.84])
SO_RECRIT = np.array([50.81, 69.43, 97.0, 109.0, 118.0, 123.0, 124.0, 122.0, 117.0, 113.0, 112.0, 110.24, 113.69])

# ── DNS pilot data (V1 run 002) ────────────────────────────────────────────────
# Each entry: (beta, Re_last_steady, Re_first_periodic)
# None = not measured (no bound from that side)
DNS = [
    (0.30,   None,  95.0),   # Re 95 → periodic; no sub-95 case run → onset ≤ 95
    (0.375,  None, 110.0),   # Re 110 → periodic; no lower case run → onset ≤ 110
    (0.50,  130.0, 135.0),   # Re 130 → steady, Re 135 → periodic → bracket (130,135)
]

# ── dense curve for band ───────────────────────────────────────────────────────
b_dense = np.linspace(SO_BETA[0], SO_BETA[-1], 800)
Re_dense = np.interp(b_dense, SO_BETA, SO_RECRIT)

# ── figure ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.5, 5.0))

# ±5 % band
ax.fill_between(
    b_dense, Re_dense * 0.95, Re_dense * 1.05,
    color="silver", alpha=0.55, zorder=1,
    label=r"Sahin & Owens $\pm 5\,\%$",
)

# S&O reference curve — line only, no markers
ax.plot(
    SO_BETA, SO_RECRIT,
    color="black", linewidth=1.6, zorder=3,
    label="Sahin & Owens (2004)",
)

# ── DNS points: green = shedding, red = steady ─────────────────────────────────
# (beta, Re, periodic?)
DNS_CASES = [
    # β = 0.30
    (0.30,   90.0, True),    # new — periodic → onset < 90
    (0.30,   95.0, True),
    (0.30,  100.0, True),
    # β = 0.375
    (0.375, 105.0, True),    # new — periodic → onset < 105
    (0.375, 110.0, True),
    (0.375, 120.0, True),
    # β = 0.50
    (0.50,  120.0, False),
    (0.50,  125.0, False),
    (0.50,  130.0, False),
    (0.50,  135.0, True),    # new — bracket now (130, 135)
    (0.50,  140.0, True),
    # β = 0.60
    (0.60,  120.0, False),
    (0.60,  125.0, False),   # new — steady
]

first_green = first_red = True
for (beta, Re, periodic) in DNS_CASES:
    if periodic:
        lbl = "Present Work — shedding" if first_green else "_"
        first_green = False
        ax.plot(beta, Re, marker="o", color="tab:green",
                markersize=6, linestyle="none", zorder=6, label=lbl)
    else:
        lbl = "Present Work — steady" if first_red else "_"
        first_red = False
        ax.plot(beta, Re, marker="o", color="tab:red",
                markersize=6, linestyle="none", zorder=6, label=lbl)

# vertical guides at tested beta values
for b in [0.30, 0.375, 0.50, 0.60]:
    ax.axvline(b, color="lightgray", linewidth=0.8, linestyle="--", zorder=0)

# ── cosmetics ──────────────────────────────────────────────────────────────────
ax.set_xlabel(r"$\beta = D/H$", fontsize=12)
ax.set_ylabel(r"$Re = U_\mathrm{max}\,D/\nu$", fontsize=12)

ax.set_xlim(0.05, 0.90)
ax.set_ylim(35, 155)
ax.xaxis.set_major_locator(mticker.MultipleLocator(0.10))
ax.xaxis.set_minor_locator(mticker.MultipleLocator(0.05))
ax.yaxis.set_major_locator(mticker.MultipleLocator(20))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(10))
ax.grid(which="major", linestyle="--", linewidth=0.5, alpha=0.5)
ax.grid(which="minor", linestyle=":",  linewidth=0.3, alpha=0.3)

ax.legend(loc="upper left", fontsize=9, framealpha=0.9)

fig.tight_layout()
out_path = OUT_DIR / "hopf_onset_vs_beta.png"
fig.savefig(out_path, dpi=180, bbox_inches="tight")
print(f"Saved: {out_path}")
