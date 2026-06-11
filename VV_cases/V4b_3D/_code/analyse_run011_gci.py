from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


CASES = [
    {
        "name": "coarse",
        "cells": 196_938,
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run011_gci_coarse/postProcessing/forceCoeffs/0/forceCoeffs.dat"),
    },
    {
        "name": "medium_run008",
        "cells": 407_440,
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run008/postProcessing/forceCoeffs/0/forceCoeffs.dat"),
    },
    {
        "name": "fine",
        "cells": 829_761,
        "path": Path("/home/hexmachina/of_runs/V4b_3D_run011_gci_fine/postProcessing/forceCoeffs/0/forceCoeffs.dat"),
    },
]

OUT_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/results/run011_gci_analysis")
METRICS = ["Cm", "Cd", "Cl", "Clf", "Clr"]


def read_force_coeffs(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        t, cm, cd, cl, clf, clr = [float(x) for x in line.split()]
        rows.append({"time": t, "Cm": cm, "Cd": cd, "Cl": cl, "Clf": clf, "Clr": clr})
    return rows


def summarize(rows: list[dict[str, float]], window: tuple[float, float]) -> dict[str, float]:
    t0, t1 = window
    nearest = min(rows, key=lambda row: abs(row["time"] - t1))
    win = [row for row in rows if t0 <= row["time"] <= t1]
    out: dict[str, float] = {
        "n_all": float(len(rows)),
        "n_window": float(len(win)),
        "time_final": nearest["time"],
    }
    for metric in METRICS:
        out[f"{metric}_t{t1:g}"] = nearest[metric]
        out[f"{metric}_mean_{t0:g}_{t1:g}"] = sum(row[metric] for row in win) / len(win)
    out[f"Cl_rms_{t0:g}_{t1:g}"] = math.sqrt(sum(row["Cl"] ** 2 for row in win) / len(win))
    return out


def apparent_order(phi1: float, phi2: float, phi3: float, r21: float, r32: float) -> float | None:
    # Celik et al. fixed-point form for three-grid GCI with potentially unequal ratios.
    e21 = phi2 - phi1
    e32 = phi3 - phi2
    if e21 == 0 or e32 == 0 or e21 * e32 <= 0:
        return None
    s = 1.0 if e32 / e21 > 0 else -1.0
    p = max(0.1, abs(math.log(abs(e32 / e21)) / math.log(r21)))
    for _ in range(100):
        numerator = r21**p - s
        denominator = r32**p - s
        if numerator <= 0 or denominator <= 0:
            return None
        q = math.log(numerator / denominator)
        p_new = abs((math.log(abs(e32 / e21)) + q) / math.log(r21))
        if abs(p_new - p) < 1e-10:
            return p_new
        p = p_new
    return p


def gci(phi1: float, phi2: float, phi3: float, n1: int, n2: int, n3: int) -> dict[str, float | str | None]:
    r21 = (n1 / n2) ** (1.0 / 3.0)
    r32 = (n2 / n3) ** (1.0 / 3.0)
    p = apparent_order(phi1, phi2, phi3, r21, r32)
    if p is None:
        return {"r21": r21, "r32": r32, "p": None, "GCI21_percent": None, "GCI32_percent": None, "status": "non-monotonic"}
    eps21 = abs((phi1 - phi2) / phi1)
    eps32 = abs((phi2 - phi3) / phi2)
    fs = 1.25
    gci21 = fs * eps21 / (r21**p - 1.0) * 100.0
    gci32 = fs * eps32 / (r32**p - 1.0) * 100.0
    return {"r21": r21, "r32": r32, "p": p, "GCI21_percent": gci21, "GCI32_percent": gci32, "status": "monotonic"}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    keys = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object, digits: int = 6) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    loaded = []
    summary_rows = []
    for case in CASES:
        rows = read_force_coeffs(case["path"])
        summary = summarize(rows, (2.0, 3.0))
        summary_rows.append({"case": case["name"], "cells": case["cells"], **summary})
        loaded.append({**case, "rows": rows, "summary": summary})

    write_csv(OUT_DIR / "run011_gci_force_coeff_summary.csv", summary_rows)

    gci_rows = []
    for source in ["t3", "mean_2_3"]:
        for metric in ["Cd", "Cl", "Cm"]:
            key = f"{metric}_t3" if source == "t3" else f"{metric}_mean_2_3"
            phi3 = loaded[0]["summary"][key]
            phi2 = loaded[1]["summary"][key]
            phi1 = loaded[2]["summary"][key]
            result = gci(phi1, phi2, phi3, loaded[2]["cells"], loaded[1]["cells"], loaded[0]["cells"])
            gci_rows.append({"metric": metric, "source": source, "coarse": phi3, "medium": phi2, "fine": phi1, **result})
    write_csv(OUT_DIR / "run011_gci_results.csv", gci_rows)

    for metric in ["Cd", "Cl", "Cm"]:
        plt.figure(figsize=(8, 4.8))
        for case in loaded:
            times = [row["time"] for row in case["rows"] if 2.0 <= row["time"] <= 3.0]
            values = [row[metric] for row in case["rows"] if 2.0 <= row["time"] <= 3.0]
            plt.plot(times, values, label=f"{case['name']} ({case['cells']:,} cells)")
        plt.xlabel("time [s]")
        plt.ylabel(metric)
        plt.title(f"V4b GCI check: {metric}, common window 2-3 s")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT_DIR / f"run011_gci_{metric}_timeseries_2_3s.png", dpi=180)
        plt.close()

    for source, suffix in [("t3", "t=3 s"), ("mean_2_3", "mean 2-3 s")]:
        plt.figure(figsize=(8, 4.8))
        xs = [row["cells"] for row in summary_rows]
        for metric in ["Cd", "Cl"]:
            key = f"{metric}_t3" if source == "t3" else f"{metric}_mean_2_3"
            ys = [row[key] for row in summary_rows]
            plt.plot(xs, ys, marker="o", label=metric)
        plt.xlabel("cell count")
        plt.ylabel("coefficient value")
        plt.title(f"V4b GCI check: grid trend ({suffix})")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT_DIR / f"run011_gci_grid_trend_{source}.png", dpi=180)
        plt.close()

    report = [
        "# V4b run011 GCI analysis",
        "",
        "Date: 2026-06-05",
        "",
        "## Mesh levels",
        "",
        "| Level | Cells | Role |",
        "|---|---:|---|",
    ]
    for row in summary_rows:
        report.append(f"| {row['case']} | {int(row['cells'])} | forceCoeffs comparison, common 2-3 s window |")
    report += [
        "",
        "## Force coefficient summary",
        "",
        "| Case | Cells | Cd(t=3) | Cl(t=3) | Cm(t=3) | Cd mean 2-3s | Cl mean 2-3s | Cl RMS 2-3s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        report.append(
            "| {case} | {cells} | {cd3} | {cl3} | {cm3} | {cdm} | {clm} | {clrms} |".format(
                case=row["case"],
                cells=int(row["cells"]),
                cd3=fmt(row["Cd_t3"], 8),
                cl3=fmt(row["Cl_t3"], 8),
                cm3=fmt(row["Cm_t3"], 8),
                cdm=fmt(row["Cd_mean_2_3"], 8),
                clm=fmt(row["Cl_mean_2_3"], 8),
                clrms=fmt(row["Cl_rms_2_3"], 8),
            )
        )
    report += [
        "",
        "## GCI results",
        "",
        "| Metric | Source | p | GCI fine/medium [%] | GCI medium/coarse [%] | Status |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in gci_rows:
        report.append(
            f"| {row['metric']} | {row['source']} | {fmt(row['p'], 5)} | {fmt(row['GCI21_percent'], 5)} | {fmt(row['GCI32_percent'], 5)} | {row['status']} |"
        )
    report += [
        "",
        "## Interpretation",
        "",
        "- `Cd` shows monotonic convergence for both the instantaneous `t=3 s` value and the common `2-3 s` average.",
        "- `Cl` is very close across the three grids; GCI is small for the `2-3 s` mean, but the apparent order is high because the medium-fine difference is much smaller than the coarse-medium difference.",
        "- `Cm` should be treated as a secondary, small-amplitude diagnostic. The `2-3 s` mean is non-monotonic, so a formal GCI is not reported for that averaged quantity.",
        "- This is a production-geometry grid sensitivity/GCI check for force coefficients, not an external experimental validation.",
        "",
        "## Generated figures",
        "",
        "- `run011_gci_Cd_timeseries_2_3s.png`",
        "- `run011_gci_Cl_timeseries_2_3s.png`",
        "- `run011_gci_Cm_timeseries_2_3s.png`",
        "- `run011_gci_grid_trend_t3.png`",
        "- `run011_gci_grid_trend_mean_2_3.png`",
        "",
    ]
    (OUT_DIR / "run011_gci_report.md").write_text("\n".join(report))


if __name__ == "__main__":
    main()
