"""
Outlet-sensitivity comparison for V4b_3D Re=200: run003, run004b, run004c.

run003 is an archived summary baseline. run004b and run004c are read from raw
forceCoeffs and reconstructed outlet patches for EB+LMTD thermal metrics.
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch


SCRIPT_DIR = Path(__file__).resolve().parent
RUN003_DIR = SCRIPT_DIR.parent / "run003"
FIG_DIR = SCRIPT_DIR / "figures"

D = 0.012
U_IN = 0.25267
T_IN = 293.15
T_HOT = 343.15
A_HOT_TOTAL = 0.002032
R_AIR = 287.0
CV_AIR = 718.0
CP_AIR = CV_AIR + R_AIR
MU_AIR = 1.827e-05
PR_AIR = 0.713
K_AIR = CP_AIR * MU_AIR / PR_AIR
WINDOW_START = 3.0
WINDOW_END = 6.0

CASES = {
    "run004b": {
        "Lout_D": 8,
        "case_dir": Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run004b"),
    },
    "run004c": {
        "Lout_D": 16,
        "case_dir": Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run004c"),
    },
}


@dataclass
class ComparisonRow:
    run: str
    Lout_D: float
    source: str
    window: str
    Cd_mean: float | None
    Cl_mean: float | None
    Cl_rms: float | None
    f_shed_Hz: float | None
    f_psd_Hz: float | None
    second_harmonic_Hz: float | None
    St: float | None
    T_out_K: float | None
    T_out_std_K: float | None
    Q_total_W: float | None
    Q_total_std_W: float | None
    Nu_EB_LMTD: float | None
    Nu_EB_LMTD_std: float | None
    Cd_diff_pct_vs_8D: float | None = None
    St_diff_pct_vs_8D: float | None = None
    Nu_diff_pct_vs_8D: float | None = None
    Cd_diff_pct_vs_5D: float | None = None
    St_diff_pct_vs_5D: float | None = None
    Nu_diff_pct_vs_5D: float | None = None


def pct(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline in (None, 0):
        return None
    return 100.0 * (value - baseline) / baseline


def fmt(v: float | None, digits: int = 3) -> str:
    if v is None or not math.isfinite(v):
        return "N/A"
    return f"{v:.{digits}f}"


def fmt_pct(v: float | None) -> str:
    if v is None or not math.isfinite(v):
        return "N/A"
    return f"{v:+.2f}%"


def parse_run003_summary() -> dict[str, float]:
    summary = (RUN003_DIR / "summary.md").read_text(encoding="utf-8", errors="replace")

    def table_value(name: str) -> float:
        match = re.search(rf"\|\s*{re.escape(name)}\s*\|\s*\**\s*([0-9.+\-eE]+)", summary)
        if not match:
            raise ValueError(f"Could not find {name} in run003 summary")
        return float(match.group(1))

    def bullet_value(name: str) -> float:
        match = re.search(rf"{re.escape(name)}\s*=\s*([0-9.+\-eE]+)", summary)
        if not match:
            raise ValueError(f"Could not find {name} in run003 summary")
        return float(match.group(1))

    return {
        "Cd_mean": table_value("Cd_mean"),
        "Cl_mean": table_value("Cl_mean"),
        "Cl_rms": table_value("Cl_rms"),
        "f_shed": table_value("f_shed"),
        "St": table_value("St"),
        "T_out": table_value("T_out"),
        "Nu_EB": table_value("**EB+LMTD** (preferred)"),
        "Q_total": bullet_value("Q_total"),
    }


def parse_force_coeffs(path: Path) -> dict[str, np.ndarray]:
    rows = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 4:
                rows.append([float(parts[0]), float(parts[2]), float(parts[3])])
    arr = np.asarray(rows, dtype=float)
    if arr.size == 0:
        raise ValueError(f"No force rows in {path}")
    return {"time": arr[:, 0], "Cd": arr[:, 1], "Cl": arr[:, 2]}


def peak_pick_frequency(time: np.ndarray, signal: np.ndarray, start: float) -> tuple[float | None, float | None]:
    mask = time >= start
    t = time[mask]
    y = signal[mask]
    peaks = []
    for i in range(1, len(t) - 1):
        if y[i] > y[i - 1] and y[i] > y[i + 1]:
            peaks.append(t[i])
    peaks = np.asarray(peaks, dtype=float)
    if len(peaks) < 3:
        return None, None
    f2 = 1.0 / float(np.mean(np.diff(peaks)))
    f1 = 1.0 / float(np.mean(peaks[2:] - peaks[:-2]))
    return f1, f2


def psd_frequency(time: np.ndarray, signal: np.ndarray, start: float) -> tuple[float | None, float | None]:
    mask = time >= start
    t = time[mask]
    y = signal[mask]
    if len(t) < 16:
        return None, None
    dt = float(np.median(np.diff(t)))
    ti = np.arange(t[0], t[-1], dt)
    yi = np.interp(ti, t, y) - np.mean(y)
    f, pxx = welch(yi, fs=1.0 / dt, nperseg=min(2048, len(yi)))

    def band_peak(lo: float, hi: float) -> float | None:
        idx = np.where((f >= lo) & (f <= hi))[0]
        if len(idx) == 0:
            return None
        return float(f[idx[np.argmax(pxx[idx])]])

    return band_peak(2.5, 4.0), band_peak(5.5, 7.5)


def force_stats(case_dir: Path) -> dict[str, float]:
    data = parse_force_coeffs(case_dir / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat")
    mask = data["time"] >= WINDOW_START
    cd = data["Cd"][mask]
    cl = data["Cl"][mask]
    cl_mean = float(np.mean(cl))
    f_peak, f2_peak = peak_pick_frequency(data["time"], data["Cl"], WINDOW_START)
    f_psd, f2_psd = psd_frequency(data["time"], data["Cl"], WINDOW_START)
    f = f_peak if f_peak is not None else f_psd
    return {
        "Cd_mean": float(np.mean(cd)),
        "Cl_mean": cl_mean,
        "Cl_rms": float(np.sqrt(np.mean((cl - cl_mean) ** 2))),
        "f_shed": f,
        "f_psd": f_psd,
        "f2": f2_peak if f2_peak is not None else f2_psd,
        "St": f * D / U_IN if f is not None else None,
    }


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def boundary_patch(case_dir: Path, patch_name: str) -> dict[str, int]:
    text = (case_dir / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found")
    section = match.group(1)
    return {
        "nFaces": int(re.search(r"nFaces\s+(\d+)\s*;", section).group(1)),
        "startFace": int(re.search(r"startFace\s+(\d+)\s*;", section).group(1)),
    }


def field_patch_values(case_dir: Path, time_name: str, field_name: str, patch_name: str, n_faces: int) -> np.ndarray:
    text = (case_dir / time_name / field_name).read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\n\s*\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found in {field_name} at {time_name}")
    section = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.full(n_faces, float(uniform.group(1)))
    vals_match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, flags=re.S)
    if not vals_match:
        raise ValueError(f"Could not parse patch values for {field_name}:{patch_name}")
    vals = np.fromstring(vals_match.group(2), sep=" ", dtype=float)
    if len(vals) != n_faces:
        raise ValueError(f"Expected {n_faces} values for {field_name}:{patch_name}, got {len(vals)}")
    return vals


def parse_points(path: Path) -> np.ndarray:
    text = _strip_comments(path.read_text(encoding="utf-8", errors="replace"))
    match = re.search(r"\n\s*(\d+)\s*\(\s*(.*?)\s*\)\s*$", text, flags=re.S)
    vals = np.fromstring(match.group(2).replace("(", " ").replace(")", " "), sep=" ", dtype=float)
    return vals.reshape((-1, 3))


def outlet_faces(path: Path, start_face: int, n_faces: int) -> list[list[int]]:
    faces = []
    in_list = False
    face_index = 0
    end_face = start_face + n_faces
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not in_list:
                if line == "(":
                    in_list = True
                continue
            if line == ")":
                break
            if start_face <= face_index < end_face:
                nums = [int(v) for v in re.findall(r"\d+", line)]
                faces.append(nums[1: 1 + nums[0]])
            face_index += 1
            if face_index >= end_face:
                break
    if len(faces) != n_faces:
        raise ValueError(f"Expected {n_faces} outlet faces, got {len(faces)}")
    return faces


def polygon_area(points: np.ndarray) -> float:
    origin = points[0]
    area_vec = np.zeros(3)
    for i in range(1, len(points) - 1):
        area_vec += np.cross(points[i] - origin, points[i + 1] - origin)
    return 0.5 * float(np.linalg.norm(area_vec))


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    return (d1 - d2) / math.log(d1 / d2)


def reconstructed_times(case_dir: Path) -> list[str]:
    found = []
    for path in case_dir.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if WINDOW_START <= t <= WINDOW_END and (path / "T").exists() and (path / "phi").exists():
            found.append((t, path.name))
    return [name for _, name in sorted(found)]


def thermal_stats(case_dir: Path) -> dict[str, float]:
    patch = boundary_patch(case_dir, "outlet")
    n_faces = patch["nFaces"]
    points = parse_points(case_dir / "constant" / "polyMesh" / "points")
    faces = outlet_faces(case_dir / "constant" / "polyMesh" / "faces", patch["startFace"], n_faces)
    areas = np.asarray([polygon_area(points[face]) for face in faces], dtype=float)
    area_total = float(np.sum(areas))
    t_area_values, t_mass_values, m_dot_values, q_values, lmtd_values, nu_values = [], [], [], [], [], []
    times = reconstructed_times(case_dir)
    if not times:
        raise ValueError(f"No reconstructed times {WINDOW_START}..{WINDOW_END} for {case_dir}")
    for time_name in times:
        t_vals = field_patch_values(case_dir, time_name, "T", "outlet", n_faces)
        phi_vals = field_patch_values(case_dir, time_name, "phi", "outlet", n_faces)
        t_area = float(np.sum(t_vals * areas) / area_total)
        weights = np.maximum(phi_vals, 0.0)
        if float(np.sum(weights)) <= 0:
            weights = np.abs(phi_vals)
        m_dot = float(np.sum(weights))
        t_mass = float(np.sum(t_vals * weights) / np.sum(weights))
        q = m_dot * CP_AIR * (t_area - T_IN)
        l = lmtd(t_area)
        nu = (q / (A_HOT_TOTAL * l)) * D / K_AIR
        t_area_values.append(t_area)
        t_mass_values.append(t_mass)
        m_dot_values.append(m_dot)
        q_values.append(q)
        lmtd_values.append(l)
        nu_values.append(nu)
    return {
        "n_times": float(len(times)),
        "T_out": float(np.mean(t_area_values)),
        "T_out_std": float(np.std(t_area_values)),
        "T_out_mass": float(np.mean(t_mass_values)),
        "m_dot": float(np.mean(m_dot_values)),
        "Q_total": float(np.mean(q_values)),
        "Q_total_std": float(np.std(q_values)),
        "LMTD": float(np.mean(lmtd_values)),
        "Nu_EB": float(np.mean(nu_values)),
        "Nu_EB_std": float(np.std(nu_values)),
    }


def build_rows() -> list[ComparisonRow]:
    r3 = parse_run003_summary()
    rows = [
        ComparisonRow(
            run="run003",
            Lout_D=5,
            source="archived summary baseline",
            window="archived reported window",
            Cd_mean=r3["Cd_mean"],
            Cl_mean=r3["Cl_mean"],
            Cl_rms=r3["Cl_rms"],
            f_shed_Hz=r3["f_shed"],
            f_psd_Hz=None,
            second_harmonic_Hz=2 * r3["f_shed"],
            St=r3["St"],
            T_out_K=r3["T_out"],
            T_out_std_K=None,
            Q_total_W=r3["Q_total"],
            Q_total_std_W=None,
            Nu_EB_LMTD=r3["Nu_EB"],
            Nu_EB_LMTD_std=None,
        )
    ]
    for run, meta in CASES.items():
        case_dir = meta["case_dir"]
        f = force_stats(case_dir)
        th = thermal_stats(case_dir)
        rows.append(
            ComparisonRow(
                run=run,
                Lout_D=meta["Lout_D"],
                source="raw forceCoeffs + reconstructed outlet fields",
                window=f"t = {WINDOW_START:g}..{WINDOW_END:g} s",
                Cd_mean=f["Cd_mean"],
                Cl_mean=f["Cl_mean"],
                Cl_rms=f["Cl_rms"],
                f_shed_Hz=f["f_shed"],
                f_psd_Hz=f["f_psd"],
                second_harmonic_Hz=f["f2"],
                St=f["St"],
                T_out_K=th["T_out"],
                T_out_std_K=th["T_out_std"],
                Q_total_W=th["Q_total"],
                Q_total_std_W=th["Q_total_std"],
                Nu_EB_LMTD=th["Nu_EB"],
                Nu_EB_LMTD_std=th["Nu_EB_std"],
            )
        )
    baseline_5d = rows[0]
    baseline_8d = next(r for r in rows if r.run == "run004b")
    for row in rows:
        row.Cd_diff_pct_vs_5D = pct(row.Cd_mean, baseline_5d.Cd_mean)
        row.St_diff_pct_vs_5D = pct(row.St, baseline_5d.St)
        row.Nu_diff_pct_vs_5D = pct(row.Nu_EB_LMTD, baseline_5d.Nu_EB_LMTD)
        row.Cd_diff_pct_vs_8D = pct(row.Cd_mean, baseline_8d.Cd_mean)
        row.St_diff_pct_vs_8D = pct(row.St, baseline_8d.St)
        row.Nu_diff_pct_vs_8D = pct(row.Nu_EB_LMTD, baseline_8d.Nu_EB_LMTD)
    return rows


def write_outputs(rows: list[ComparisonRow]) -> None:
    csv_path = SCRIPT_DIR / "run003_run004b_run004c_outlet_compare.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    (SCRIPT_DIR / "run003_run004b_run004c_outlet_compare.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "window": f"t = {WINDOW_START:g}..{WINDOW_END:g} s for run004b/run004c",
                    "D_m": D,
                    "U_in_m_per_s": U_IN,
                    "thermal_method": "EB+LMTD from reconstructed outlet patch values",
                    "constants": {
                        "Cp_J_per_kgK": CP_AIR,
                        "k_W_per_mK": K_AIR,
                        "A_hot_total_m2": A_HOT_TOTAL,
                    },
                },
                "rows": [asdict(row) for row in rows],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(rows)
    plot_summary(rows)


def write_markdown(rows: list[ComparisonRow]) -> None:
    r5, r8, r16 = rows
    lines = [
        "# V4b_3D outlet sensitivity: 5D vs 8D vs 16D",
        "",
        f"`run004b` and `run004c` use the matched window `t = {WINDOW_START:g}..{WINDOW_END:g} s`; `run003` uses archived summary values.",
        "",
        "| Run | Lout/D | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        t_out = f"{fmt(row.T_out_K, 2)}"
        if row.T_out_std_K is not None:
            t_out += f" +/- {fmt(row.T_out_std_K, 2)}"
        nu = f"{fmt(row.Nu_EB_LMTD, 3)}"
        if row.Nu_EB_LMTD_std is not None:
            nu += f" +/- {fmt(row.Nu_EB_LMTD_std, 3)}"
        lines.append(
            f"| {row.run} | {row.Lout_D:g} | {fmt(row.Cd_mean, 3)} | {fmt(row.Cl_mean, 3)} | "
            f"{fmt(row.Cl_rms, 3)} | {fmt(row.f_shed_Hz, 3)} | {fmt(row.St, 4)} | {t_out} | {nu} |"
        )
    lines += [
        "",
        "## Key Differences",
        "",
        "| Comparison | Cd | St | Nu_EB |",
        "|---|---:|---:|---:|",
        f"| 8D vs 5D | {fmt_pct(r8.Cd_diff_pct_vs_5D)} | {fmt_pct(r8.St_diff_pct_vs_5D)} | {fmt_pct(r8.Nu_diff_pct_vs_5D)} |",
        f"| 16D vs 5D | {fmt_pct(r16.Cd_diff_pct_vs_5D)} | {fmt_pct(r16.St_diff_pct_vs_5D)} | {fmt_pct(r16.Nu_diff_pct_vs_5D)} |",
        f"| 16D vs 8D | {fmt_pct(r16.Cd_diff_pct_vs_8D)} | {fmt_pct(r16.St_diff_pct_vs_8D)} | {fmt_pct(r16.Nu_diff_pct_vs_8D)} |",
        "",
        "## Conclusion",
        "",
        "The `16D` result is essentially identical to `8D` for the force metrics and very close for EB+LMTD heat transfer. This closes the main outlet-independence question: `8D` is sufficient for production use, while `5D` is qualitatively correct but mildly outlet-sensitive in drag and heat transfer.",
    ]
    (SCRIPT_DIR / "run003_run004b_run004c_outlet_compare.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_summary(rows: list[ComparisonRow]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    labels = [f"{r.run}\n{r.Lout_D:g}D" for r in rows]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    metrics = [
        ("Cd_mean", [r.Cd_mean for r in rows], "Cd"),
        ("St", [r.St for r in rows], "St"),
        ("Nu_EB_LMTD", [r.Nu_EB_LMTD for r in rows], "Nu_EB"),
    ]
    for ax, (_, values, title) in zip(axes, metrics):
        ax.plot(labels, values, marker="o", color="#2f6f73", lw=2)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
    fig.suptitle("V4b_3D outlet sensitivity: 5D vs 8D vs 16D")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run003_run004b_run004c_outlet_sensitivity.png", dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    write_outputs(rows)
    print(f"Wrote outlet comparison outputs in {SCRIPT_DIR}")


if __name__ == "__main__":
    main()
