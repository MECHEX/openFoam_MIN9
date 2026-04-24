"""
V1PublicationTable.py
---------------------
Generates:
  1. publication/verification_table.md  — Table X for the article
  2. publication/figures/St_Cd_vs_Re.png — St and Cd vs Re per beta

Run after all relevant cases are analyzed:
    python _code/V1Run2Study.py analyze
    python _code/V1PublicationTable.py
"""

from pathlib import Path
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent.parent
RUN002_SIMS = (
    HERE / "results" / "study_v1" / "runs"
    / "002_data_sahin_owens_poiseuille_verification" / "02_simulations"
)
PUB_DIR = HERE / "results" / "study_v1" / "publication" / "figures"
PUB_DIR.mkdir(parents=True, exist_ok=True)

# ── Sahin & Owens (2004) reference data ───────────────────────────────────────
# Re_crit and St_crit from Table IV + digitised curve
# St_crit is at Re_crit; no tabulated Cd at matching Re available from S&O.
SO = {
    0.10: {"Re_crit": 50.81,  "St_crit": 0.1210},
    0.20: {"Re_crit": 69.43,  "St_crit": 0.1566},
    0.30: {"Re_crit": 94.56,  "St_crit": 0.2090},
    0.50: {"Re_crit": 124.09, "St_crit": 0.3393},
    0.60: {"Re_crit": 117.0,  "St_crit": None},   # digitised, St_crit not tabulated
    0.70: {"Re_crit": 110.29, "St_crit": 0.4752},
    0.80: {"Re_crit": 110.24, "St_crit": 0.5363},
    0.84: {"Re_crit": 113.69, "St_crit": 0.5568},
}

def so_st(beta: float):
    """Interpolated S&O St_crit for a given beta (None if not available)."""
    if beta in SO and SO[beta]["St_crit"] is not None:
        return SO[beta]["St_crit"]
    betas = sorted(b for b in SO if SO[b]["St_crit"] is not None)
    lo = max((b for b in betas if b <= beta), default=None)
    hi = min((b for b in betas if b >= beta), default=None)
    if lo is None or hi is None or lo == hi:
        return None
    t = (beta - lo) / (hi - lo)
    return round(SO[lo]["St_crit"] * (1 - t) + SO[hi]["St_crit"] * t, 4)

# ── cases to include in the table (in order) ──────────────────────────────────
TABLE_CASES = [
    "b030_medium_Re090",
    "b030_medium_Re095",
    "b0375_medium_Re105",
    "b0375_medium_Re110",
    "b0375_medium_Re120",
    "b050_medium_Re130",
    "b050_medium_Re135",
    "b050_medium_Re140",
    "b060_medium_Re125",
    "b060_medium_Re135",
]

# ── load summary data ──────────────────────────────────────────────────────────
def load(case_name: str) -> dict:
    p = RUN002_SIMS / case_name / "03_processed_data" / "summary.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))

rows = []
for name in TABLE_CASES:
    d = load(name)
    if not d:
        print(f"  missing: {name}")
        continue
    meta = d.get("metadata", {})
    metrics = d.get("metrics", {})
    beta = float(meta.get("beta", 0))
    Re = float(meta.get("reynolds", 0))
    regime = metrics.get("regime", "—")
    St_dns = metrics.get("St")
    Cd_dns = metrics.get("Cd_mean")
    St_so = so_st(beta)
    dSt = None
    if St_dns is not None and St_so is not None:
        dSt = round(100.0 * (St_dns - St_so) / St_so, 1)
    rows.append({
        "name": name,
        "beta": beta,
        "Re": Re,
        "regime": regime,
        "St_dns": St_dns,
        "Cd_dns": Cd_dns,
        "St_so": St_so,
        "dSt": dSt,
    })

# ── 1. Markdown table ──────────────────────────────────────────────────────────
def fmt(v, digits=3, dash="—"):
    if v is None:
        return dash
    return f"{v:.{digits}f}"

def fmt_dSt(v):
    if v is None:
        return "—"
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.1f}"

lines = [
    "# Table X. Verification against Sahin & Owens (2004)",
    "",
    "All cases: 2D channel, Poiseuille inlet, no-slip walls, medium mesh (~38–56 k cells).",
    "Re = U_max D / ν.  St = f D / U_max.  Cd = F_drag / (0.5 ρ U_max² D L_z).",
    "S&O St values: Table IV (β=0.30, 0.50, 0.70, 0.80, 0.84) or linear interpolation (β=0.375).",
    "S&O Cd at identical Re not available; DNS Cd shown for reference.",
    "",
    "| β    | Re  | Regime   | St_DNS | St_S&O | ΔSt [%] | Cd_DNS |",
    "|------|-----|----------|--------|--------|---------|--------|",
]
for r in rows:
    regime_short = "periodic" if "periodic" in r["regime"] else "steady"
    lines.append(
        f"| {r['beta']:.3f} | {int(r['Re']):3d} | {regime_short:<8} "
        f"| {fmt(r['St_dns'])} | {fmt(r['St_so'])} "
        f"| {fmt_dSt(r['dSt']):>7} | {fmt(r['Cd_dns'], 3)} |"
    )

table_path = PUB_DIR.parent / "verification_table.md"
table_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Table written: {table_path}")
for line in lines[7:]:
    print(line.encode("ascii", errors="replace").decode("ascii"))

# ── 2. St and Cd vs Re plot ────────────────────────────────────────────────────
BETA_COLORS = {
    0.30:  "#0b5ed7",
    0.375: "#6c757d",
    0.50:  "#dc3545",
    0.60:  "#198754",
}
BETA_LABELS = {
    0.30:  r"$\beta=0.30$",
    0.375: r"$\beta=0.375$",
    0.50:  r"$\beta=0.50$",
    0.60:  r"$\beta=0.60$",
}

# group by beta
from collections import defaultdict
by_beta: dict[float, list] = defaultdict(list)
for r in rows:
    by_beta[r["beta"]].append(r)
for v in by_beta.values():
    v.sort(key=lambda x: x["Re"])

fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=180)
ax_st, ax_cd = axes

for beta, grp in sorted(by_beta.items()):
    color = BETA_COLORS.get(beta, "#333333")
    label = BETA_LABELS.get(beta, f"β={beta}")

    # DNS points: periodic only for St, all for Cd
    Re_per = [r["Re"] for r in grp if r["St_dns"] is not None]
    St_per = [r["St_dns"] for r in grp if r["St_dns"] is not None]
    Re_cd  = [r["Re"] for r in grp if r["Cd_dns"] is not None]
    Cd_val = [r["Cd_dns"] for r in grp if r["Cd_dns"] is not None]

    # St panel
    if Re_per:
        ax_st.plot(Re_per, St_per, "o-", color=color, lw=1.4, ms=5,
                   label=label + " (DNS)")
    # S&O onset marker
    so_ref = SO.get(beta)
    if so_ref and so_ref["St_crit"] is not None:
        ax_st.plot(so_ref["Re_crit"], so_ref["St_crit"],
                   marker="x", ms=8, mew=2, color=color,
                   label=label + " S&O onset", linestyle="none")
    elif beta == 0.375:
        St_interp = so_st(beta)
        Re_interp = SO[0.30]["Re_crit"] * 0.5 + SO[0.50]["Re_crit"] * 0.5   # mid approx
        # actually interpolate Re_crit too
        t = (0.375 - 0.30) / (0.50 - 0.30)
        Re_interp = SO[0.30]["Re_crit"] * (1-t) + SO[0.50]["Re_crit"] * t
        ax_st.plot(Re_interp, St_interp,
                   marker="x", ms=8, mew=2, color=color,
                   label=label + " S\&O onset (interp)", linestyle="none")

    # Cd panel
    if Re_cd:
        ax_cd.plot(Re_cd, Cd_val, "o-", color=color, lw=1.4, ms=5,
                   label=label + " (DNS)")

# cosmetics St
ax_st.set_xlabel(r"$Re = U_\mathrm{max}\,D/\nu$", fontsize=11)
ax_st.set_ylabel(r"$St = f\,D/U_\mathrm{max}$", fontsize=11)
ax_st.set_title("Strouhal number", fontsize=11)
ax_st.legend(fontsize=7.5, loc="upper left", framealpha=0.9)
ax_st.grid(which="major", linestyle="--", lw=0.5, alpha=0.5)
ax_st.grid(which="minor", linestyle=":", lw=0.3, alpha=0.3)
ax_st.xaxis.set_minor_locator(mticker.AutoMinorLocator(2))
ax_st.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))

# cosmetics Cd
ax_cd.set_xlabel(r"$Re = U_\mathrm{max}\,D/\nu$", fontsize=11)
ax_cd.set_ylabel(r"$C_d$", fontsize=11)
ax_cd.set_title("Drag coefficient", fontsize=11)
ax_cd.legend(fontsize=7.5, loc="upper right", framealpha=0.9)
ax_cd.grid(which="major", linestyle="--", lw=0.5, alpha=0.5)
ax_cd.grid(which="minor", linestyle=":", lw=0.3, alpha=0.3)
ax_cd.xaxis.set_minor_locator(mticker.AutoMinorLocator(2))
ax_cd.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))

fig.suptitle(
    "V1 solver verification vs Sahin & Owens (2004)\n"
    r"2D channel, Poiseuille inlet, $Re = U_\mathrm{max}D/\nu$",
    fontsize=11,
)
fig.tight_layout()
out = PUB_DIR / "St_Cd_vs_Re.png"
fig.savefig(out, dpi=180, bbox_inches="tight")
fig.savefig(out.with_suffix(".svg"), bbox_inches="tight")
print(f"Plot saved: {out}")
