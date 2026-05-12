"""
Run008 campaign comparison and production-reference decision.

Layer 011:
- place run008 against run004b, run005, and run007c,
- show global regime continuity in Cd, Cl_rms, St, Nu,
- compare short 0.5..2 s smoke behavior with production 2..10 s,
- document why run007a remains a variable-property diagnostic, not production,
- close the decision: production reference = run008.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


RUN_DIR = Path(__file__).resolve().parent.parent
ROOT_RESULTS = RUN_DIR.parent
DATA_DIR = RUN_DIR / "data" / "011"
FIG_DIR = RUN_DIR / "figures" / "011"

WINDOW_PROD = "2..10"
WINDOW_DOMAIN = "3..6"
WINDOW_SHORT = "0.5..2"


@dataclass
class RegimeRow:
    run: str
    role: str
    model: str
    window: str
    Cd_mean: float
    Cl_rms: float
    St: float | None
    Nu: float
    Nu_definition: str
    closure_pct: float | None
    status: str


@dataclass
class ShortRow:
    run: str
    model: str
    window: str
    Cd_mean: float
    Cl_rms: float
    Q_wall_W: float
    Q_air_case_W: float
    Nu_wall_case_k: float
    Nu_wall_ref_k: float
    wall_vs_air_case_pct: float
    note: str


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def f(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in {"", None} else float("nan")


def load_domain_rows() -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(ROOT_RESULTS / "run005" / "run004b_vs_run005_inlet_compare.csv")
    return {r["run"]: r for r in rows}


def load_run008_audit() -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(RUN_DIR / "data" / "001" / "run008_audit_window_uncertainty.csv")
    return {r["window"]: r for r in rows}


def load_run007c_short() -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(ROOT_RESULTS / "run007c" / "run004b_run007a_run007c_final_0p5_2_compare.csv")
    return {r["run"]: r for r in rows}


def load_run008_production() -> RegimeRow:
    audit = load_run008_audit()["2_10"]
    return RegimeRow(
        run="run008",
        role="production reference",
        model="eConst/Boussinesq, capacity=1005, production sampling",
        window="2..10 s",
        Cd_mean=f(audit, "Cd_mean"),
        Cl_rms=f(audit, "Cl_rms"),
        St=f(audit, "St"),
        Nu=f(audit, "Nu_EB_mean"),
        Nu_definition="Nu_EB",
        closure_pct=f(audit, "closure_mean_pct"),
        status="accepted production reference",
    )


def build_tables() -> tuple[list[RegimeRow], list[ShortRow], dict[str, object]]:
    domain = load_domain_rows()
    short = load_run007c_short()
    run008 = load_run008_production()

    run004b = domain["run004b"]
    run005 = domain["run005"]
    run007c = short["run007c"]
    run007a = short["run007a"]

    regime_rows = [
        RegimeRow(
            run="run004b",
            role="accepted domain baseline",
            model="eConst/Boussinesq, old capacity scale",
            window="3..6 s",
            Cd_mean=f(run004b, "Cd_mean"),
            Cl_rms=f(run004b, "Cl_rms"),
            St=f(run004b, "St"),
            Nu=f(run004b, "Nu_EB_LMTD"),
            Nu_definition="Nu_EB_LMTD",
            closure_pct=None,
            status="domain baseline, pre-Cp cleanup",
        ),
        RegimeRow(
            run="run005",
            role="inlet sensitivity",
            model="same as run004b, Lin=4D",
            window="3..6 s",
            Cd_mean=f(run005, "Cd_mean"),
            Cl_rms=f(run005, "Cl_rms"),
            St=f(run005, "St"),
            Nu=f(run005, "Nu_EB_LMTD"),
            Nu_definition="Nu_EB_LMTD",
            closure_pct=None,
            status="inlet sensitivity closed",
        ),
        RegimeRow(
            run="run007c",
            role="Cp-capacity smoke",
            model="eConst/Boussinesq, capacity=1005",
            window="0.5..2 s",
            Cd_mean=f(run007c, "Cd_mean"),
            Cl_rms=f(run007c, "Cl_rms"),
            St=None,
            Nu=f(run007c, "Nu_wall_case_k"),
            Nu_definition="Nu_wall_case_k",
            closure_pct=f(run007c, "wall_vs_air_case_pct"),
            status="short smoke, same model family as run008",
        ),
        run008,
    ]

    short_rows = []
    for run_name, note in [
        ("run004b", "old capacity scale; short-window baseline"),
        ("run007a", "variable-property diagnostic; not production"),
        ("run007c", "constant-property Cp-capacity smoke; parent of run008 settings"),
    ]:
        r = short[run_name]
        short_rows.append(
            ShortRow(
                run=run_name,
                model=r["model"],
                window=r["force_window"],
                Cd_mean=f(r, "Cd_mean"),
                Cl_rms=f(r, "Cl_rms"),
                Q_wall_W=f(r, "Q_wall_hot_W"),
                Q_air_case_W=f(r, "Q_air_case_W"),
                Nu_wall_case_k=f(r, "Nu_wall_case_k"),
                Nu_wall_ref_k=f(r, "Nu_wall_ref_k"),
                wall_vs_air_case_pct=f(r, "wall_vs_air_case_pct"),
                note=note,
            )
        )

    run008_prod = {
        "Cd_mean": run008.Cd_mean,
        "Cl_rms": run008.Cl_rms,
        "St": run008.St,
        "Nu_EB": run008.Nu,
        "Nu_wall": load_run008_audit()["2_10"]["Nu_wall_mean"],
        "closure_pct": run008.closure_pct,
    }

    decision = {
        "production_reference": "run008",
        "reason": [
            "matches established aerodynamic regime from run004b/run005",
            "inherits run007c Cp-consistent constant-property setup",
            "uses 2..10 s production record with 25.98 shedding cycles",
            "has closed heat balance: Q_wall-Q_air about +0.706%",
            "contains measurement-rich sampling needed for POD/EPOD/coherence/local Nu story",
        ],
        "run007a_status": "variable-property experiment, not production reference because short-window wall-air closure was about -27.4%",
        "run008_production": run008_prod,
    }
    return regime_rows, short_rows, decision


def pct_diff(value: float, ref: float) -> float:
    return 100.0 * (value - ref) / ref


def plot_regime(regime_rows: list[RegimeRow]) -> None:
    runs = [r.run for r in regime_rows]
    x = np.arange(len(runs))
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    metrics = [
        ("Cd_mean", [r.Cd_mean for r in regime_rows], "Cd mean"),
        ("Cl_rms", [r.Cl_rms for r in regime_rows], "Cl RMS"),
        ("St", [np.nan if r.St is None else r.St for r in regime_rows], "St"),
        ("Nu", [r.Nu for r in regime_rows], "Nu"),
    ]
    colors = ["#8ecae6", "#219ebc", "#ffb703", "#2a9d8f"]
    for ax, (_, vals, label) in zip(axes.ravel(), metrics):
        ax.bar(x, vals, color=colors)
        ax.set_xticks(x)
        ax.set_xticklabels(runs, rotation=25, ha="right")
        ax.set_ylabel(label)
        ax.grid(True, axis="y", alpha=0.25)
    axes[0, 0].set_title("Global regime across campaign")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_011_campaign_global_regime.png", dpi=180)
    plt.close(fig)


def plot_delta_vs_run008(regime_rows: list[RegimeRow]) -> None:
    ref = next(r for r in regime_rows if r.run == "run008")
    compare = [r for r in regime_rows if r.run != "run008"]
    labels = [r.run for r in compare]
    metrics = [
        ("Cd", [pct_diff(r.Cd_mean, ref.Cd_mean) for r in compare]),
        ("Cl_rms", [pct_diff(r.Cl_rms, ref.Cl_rms) for r in compare]),
        ("Nu", [pct_diff(r.Nu, ref.Nu) for r in compare]),
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(labels))
    width = 0.25
    for i, (name, vals) in enumerate(metrics):
        ax.bar(x + (i - 1) * width, vals, width=width, label=name)
    ax.axhline(0, color="0.4", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("difference vs run008 [%]")
    ax.set_title("Earlier checks relative to run008 production reference")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_011_differences_vs_production.png", dpi=180)
    plt.close(fig)


def plot_short_vs_production(short_rows: list[ShortRow], regime_rows: list[RegimeRow]) -> None:
    run008 = next(r for r in regime_rows if r.run == "run008")
    run007c = next(r for r in short_rows if r.run == "run007c")
    labels = ["run007c short\n0.5..2", "run008 production\n2..10"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].bar(labels, [run007c.Cd_mean, run008.Cd_mean], color=["#ffb703", "#2a9d8f"])
    axes[0].set_ylabel("Cd mean")
    axes[1].bar(labels, [run007c.Cl_rms, run008.Cl_rms], color=["#ffb703", "#2a9d8f"])
    axes[1].set_ylabel("Cl RMS")
    axes[2].bar(labels, [run007c.Nu_wall_case_k, run008.Nu], color=["#ffb703", "#2a9d8f"])
    axes[2].set_ylabel("Nu")
    axes[2].set_title("short uses Nu_wall; production uses Nu_EB")
    for ax in axes:
        ax.grid(True, axis="y", alpha=0.25)
    fig.suptitle("Short smoke window vs production record")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_011_short_vs_production.png", dpi=180)
    plt.close(fig)


def plot_run007a_status(short_rows: list[ShortRow]) -> None:
    labels = [r.run for r in short_rows]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].bar(x, [r.wall_vs_air_case_pct for r in short_rows], color=["#8ecae6", "#e76f51", "#2a9d8f"])
    axes[0].axhline(0, color="0.4", lw=0.8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels)
    axes[0].set_ylabel("100*(Q_wall-Q_air)/Q_air [%]")
    axes[0].set_title("Short-window heat-balance closure")
    axes[1].bar(x, [r.Cd_mean for r in short_rows], color=["#8ecae6", "#e76f51", "#2a9d8f"])
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].set_ylabel("Cd mean")
    axes[1].set_title("Variable-property run007a also shifts drag")
    for ax in axes:
        ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_011_run007a_diagnostic_status.png", dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    regime_rows, short_rows, decision = build_tables()
    write_csv(DATA_DIR / "run008_011_campaign_regime_table.csv", [asdict(r) for r in regime_rows])
    write_csv(DATA_DIR / "run008_011_short_window_table.csv", [asdict(r) for r in short_rows])
    (DATA_DIR / "run008_011_campaign_decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")

    plot_regime(regime_rows)
    plot_delta_vs_run008(regime_rows)
    plot_short_vs_production(short_rows, regime_rows)
    plot_run007a_status(short_rows)

    ref = next(r for r in regime_rows if r.run == "run008")
    run004b = next(r for r in regime_rows if r.run == "run004b")
    run005 = next(r for r in regime_rows if r.run == "run005")
    run007c = next(r for r in regime_rows if r.run == "run007c")
    run007a_short = next(r for r in short_rows if r.run == "run007a")
    run007c_short = next(r for r in short_rows if r.run == "run007c")

    lines = [
        "# V4b_3D run008 campaign comparison and production decision",
        "",
        "This layer places the production record in the full V4b_3D campaign context.",
        "",
        "## Global regime table",
        "",
        "| Run | Role | Window | Cd_mean | Cl_rms | St | Nu | Nu definition | Closure | Status |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for r in regime_rows:
        st = "" if r.St is None else f"{r.St:.5f}"
        closure = "" if r.closure_pct is None else f"{r.closure_pct:+.2f}%"
        lines.append(
            f"| {r.run} | {r.role} | {r.window} | {r.Cd_mean:.6f} | {r.Cl_rms:.6f} | {st} | "
            f"{r.Nu:.6f} | {r.Nu_definition} | {closure} | {r.status} |"
        )
    lines.extend(
        [
            "",
            "## Differences relative to run008",
            "",
            "| Run | Cd diff | Cl_rms diff | Nu diff |",
            "|---|---:|---:|---:|",
            f"| run004b | {pct_diff(run004b.Cd_mean, ref.Cd_mean):+.3f}% | {pct_diff(run004b.Cl_rms, ref.Cl_rms):+.3f}% | {pct_diff(run004b.Nu, ref.Nu):+.3f}% |",
            f"| run005 | {pct_diff(run005.Cd_mean, ref.Cd_mean):+.3f}% | {pct_diff(run005.Cl_rms, ref.Cl_rms):+.3f}% | {pct_diff(run005.Nu, ref.Nu):+.3f}% |",
            f"| run007c smoke | {pct_diff(run007c.Cd_mean, ref.Cd_mean):+.3f}% | {pct_diff(run007c.Cl_rms, ref.Cl_rms):+.3f}% | {pct_diff(run007c.Nu, ref.Nu):+.3f}% |",
            "",
            "Note: `run007c` is a short smoke test, so its St is intentionally not used as a regime metric; the short FFT is dominated by transient/window limits.",
            "",
            "## Short-window context",
            "",
            "| Run | Model | Cd | Cl_rms | Q_wall [W] | Q_air case [W] | Nu_wall case-k | wall-air diff |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for r in short_rows:
        lines.append(
            f"| {r.run} | {r.model} | {r.Cd_mean:.6f} | {r.Cl_rms:.6f} | {r.Q_wall_W:.4f} | "
            f"{r.Q_air_case_W:.4f} | {r.Nu_wall_case_k:.4f} | {r.wall_vs_air_case_pct:+.1f}% |"
        )
    lines.extend(
        [
            "",
            "## run007a status",
            "",
            f"`run007a` remains a useful variable-property diagnostic, but not a production reference. In the matched `0.5..2 s` window it has wall-air closure `{run007a_short.wall_vs_air_case_pct:+.1f}%`, while `run007c` closes at `{run007c_short.wall_vs_air_case_pct:+.1f}%`.",
            "",
            "The variable-property case also shifts drag (`Cd = 3.4736`) relative to the accepted constant-property regime (`Cd ~= 3.361`). Until its energy balance is made internally consistent, it should not define the production model.",
            "",
            "## Decision",
            "",
            "`run008` is the production reference for this campaign.",
            "",
            "Rationale:",
            "",
        ]
    )
    for reason in decision["reason"]:
        lines.append(f"- {reason}")
    lines.extend(
        [
            "",
            "## Figures",
            "",
            "- `../../figures/011/run008_011_campaign_global_regime.png`",
            "- `../../figures/011/run008_011_differences_vs_production.png`",
            "- `../../figures/011/run008_011_short_vs_production.png`",
            "- `../../figures/011/run008_011_run007a_diagnostic_status.png`",
        ]
    )
    report = DATA_DIR / "run008_011_campaign_comparison.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
