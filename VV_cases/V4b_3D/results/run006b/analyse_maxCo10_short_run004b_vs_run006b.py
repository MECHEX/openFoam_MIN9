"""
Short maxCo=1.0 smoke-test comparison for V4b_3D Re=200.

Compares run006b (maxCo=1.0, t=2 s) against run004b (maxCo=0.8) over matched
early windows. This is a speed/safety smoke test, not a production averaging
window.
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
D = 0.012
U_IN = 0.25267
T_IN = 293.15
T_HOT = 343.15
A_HOT_TOTAL = 0.002032
CP_AIR = 1005.0
MU_AIR = 1.827e-05
PR_AIR = 0.713
K_AIR = CP_AIR * MU_AIR / PR_AIR

CASE_DIRS = {
    "run004b": Path("/home/hexmachina/of_runs/V4b_3D_run004b"),
    "run006b": Path("/home/hexmachina/of_runs/V4b_3D_run006b"),
}
WINDOWS = ((0.5, 2.0), (1.0, 2.0), (1.5, 2.0))


@dataclass
class Row:
    run: str
    maxCo: float
    window: str
    n_force: int
    n_thermal_times: int
    Cd_mean: float
    Cl_mean: float
    Cl_rms: float
    f_peak_Hz: float | None
    f_fft_Hz: float | None
    St: float | None
    T_out_K: float
    T_out_std_K: float
    Q_total_W: float
    Q_total_std_W: float
    Nu_EB_LMTD: float
    Nu_EB_LMTD_std: float
    Cd_diff_pct_vs_run004b: float | None = None
    Cl_rms_diff_pct_vs_run004b: float | None = None
    St_diff_pct_vs_run004b: float | None = None
    T_out_diff_K_vs_run004b: float | None = None
    Nu_diff_pct_vs_run004b: float | None = None


def pct(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline in (None, 0):
        return None
    return 100.0 * (value - baseline) / baseline


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None or not math.isfinite(value):
        return "N/A"
    return f"{value:.{digits}f}"


def fmt_pct(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "N/A"
    return f"{value:+.2f}%"


def parse_force_coeffs(path: Path) -> dict[str, np.ndarray]:
    rows = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            rows.append([float(parts[0]), float(parts[2]), float(parts[3])])
    arr = np.asarray(rows, dtype=float)
    return {"time": arr[:, 0], "Cd": arr[:, 1], "Cl": arr[:, 2]}


def frequency_estimates(time: np.ndarray, signal: np.ndarray, start: float, end: float) -> tuple[float | None, float | None]:
    mask = (time >= start) & (time <= end)
    t = time[mask]
    y = signal[mask]
    peaks = []
    for i in range(1, len(t) - 1):
        if y[i] > y[i - 1] and y[i] > y[i + 1]:
            peaks.append(t[i])
    f_peak = None
    if len(peaks) >= 3:
        peaks = np.asarray(peaks)
        f_peak = 1.0 / float(np.mean(peaks[2:] - peaks[:-2]))
    if len(t) < 16:
        return f_peak, None
    dt = float(np.median(np.diff(t)))
    ti = np.arange(t[0], t[-1], dt)
    yi = np.interp(ti, t, y) - float(np.mean(y))
    freqs = np.fft.rfftfreq(len(yi), d=dt)
    power = np.abs(np.fft.rfft(yi)) ** 2
    idx = np.where((freqs >= 2.5) & (freqs <= 4.0))[0]
    f_fft = float(freqs[idx[np.argmax(power[idx])]]) if len(idx) else None
    return f_peak, f_fft


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def boundary_patch(case_dir: Path, patch_name: str) -> dict[str, int]:
    text = (case_dir / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\}}", text, flags=re.S)
    section = match.group(1)
    return {
        "nFaces": int(re.search(r"nFaces\s+(\d+)\s*;", section).group(1)),
        "startFace": int(re.search(r"startFace\s+(\d+)\s*;", section).group(1)),
    }


def field_patch_values(case_dir: Path, time_name: str, field_name: str, patch_name: str, n_faces: int) -> np.ndarray:
    text = (case_dir / time_name / field_name).read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\n\s*\}}", text, flags=re.S)
    section = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.full(n_faces, float(uniform.group(1)))
    vals_match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, flags=re.S)
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


def reconstructed_times(case_dir: Path, start: float, end: float) -> list[str]:
    found = []
    for path in case_dir.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if start <= t <= end and (path / "T").exists() and (path / "phi").exists():
            found.append((t, path.name))
    return [name for _, name in sorted(found)]


def force_stats(case_dir: Path, start: float, end: float) -> dict[str, float | None]:
    data = parse_force_coeffs(case_dir / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat")
    mask = (data["time"] >= start) & (data["time"] <= end)
    cd = data["Cd"][mask]
    cl = data["Cl"][mask]
    cl_mean = float(np.mean(cl))
    f_peak, f_fft = frequency_estimates(data["time"], data["Cl"], start, end)
    f = f_peak if f_peak is not None else f_fft
    return {
        "n": int(len(cd)),
        "Cd_mean": float(np.mean(cd)),
        "Cl_mean": cl_mean,
        "Cl_rms": float(np.sqrt(np.mean((cl - cl_mean) ** 2))),
        "f_peak": f_peak,
        "f_fft": f_fft,
        "St": f * D / U_IN if f is not None else None,
    }


def thermal_stats(case_dir: Path, start: float, end: float) -> dict[str, float]:
    patch = boundary_patch(case_dir, "outlet")
    n_faces = patch["nFaces"]
    points = parse_points(case_dir / "constant" / "polyMesh" / "points")
    faces = outlet_faces(case_dir / "constant" / "polyMesh" / "faces", patch["startFace"], n_faces)
    areas = np.asarray([polygon_area(points[face]) for face in faces], dtype=float)
    area_total = float(np.sum(areas))
    t_area_values, q_values, nu_values = [], [], []
    times = reconstructed_times(case_dir, start, end)
    if not times:
        raise ValueError(f"No reconstructed times {start}..{end} for {case_dir}")
    for time_name in times:
        t_vals = field_patch_values(case_dir, time_name, "T", "outlet", n_faces)
        phi_vals = field_patch_values(case_dir, time_name, "phi", "outlet", n_faces)
        t_area = float(np.sum(t_vals * areas) / area_total)
        weights = np.maximum(phi_vals, 0.0)
        if float(np.sum(weights)) <= 0:
            weights = np.abs(phi_vals)
        m_dot = float(np.sum(weights))
        q = m_dot * CP_AIR * (t_area - T_IN)
        nu = (q / (A_HOT_TOTAL * lmtd(t_area))) * D / K_AIR
        t_area_values.append(t_area)
        q_values.append(q)
        nu_values.append(nu)
    return {
        "n_times": int(len(times)),
        "T_out": float(np.mean(t_area_values)),
        "T_out_std": float(np.std(t_area_values)),
        "Q_total": float(np.mean(q_values)),
        "Q_total_std": float(np.std(q_values)),
        "Nu_EB": float(np.mean(nu_values)),
        "Nu_EB_std": float(np.std(nu_values)),
    }


def build_rows() -> list[Row]:
    rows = []
    for start, end in WINDOWS:
        baseline = None
        for run, case_dir in CASE_DIRS.items():
            f = force_stats(case_dir, start, end)
            th = thermal_stats(case_dir, start, end)
            row = Row(
                run=run,
                maxCo=0.8 if run == "run004b" else 1.0,
                window=f"t = {start:g}..{end:g} s",
                n_force=int(f["n"]),
                n_thermal_times=int(th["n_times"]),
                Cd_mean=f["Cd_mean"],
                Cl_mean=f["Cl_mean"],
                Cl_rms=f["Cl_rms"],
                f_peak_Hz=f["f_peak"],
                f_fft_Hz=f["f_fft"],
                St=f["St"],
                T_out_K=th["T_out"],
                T_out_std_K=th["T_out_std"],
                Q_total_W=th["Q_total"],
                Q_total_std_W=th["Q_total_std"],
                Nu_EB_LMTD=th["Nu_EB"],
                Nu_EB_LMTD_std=th["Nu_EB_std"],
            )
            if run == "run004b":
                baseline = row
            else:
                row.Cd_diff_pct_vs_run004b = pct(row.Cd_mean, baseline.Cd_mean)
                row.Cl_rms_diff_pct_vs_run004b = pct(row.Cl_rms, baseline.Cl_rms)
                row.St_diff_pct_vs_run004b = pct(row.St, baseline.St)
                row.T_out_diff_K_vs_run004b = row.T_out_K - baseline.T_out_K
                row.Nu_diff_pct_vs_run004b = pct(row.Nu_EB_LMTD, baseline.Nu_EB_LMTD)
            rows.append(row)
    return rows


def write_outputs(rows: list[Row]) -> None:
    with (SCRIPT_DIR / "run004b_vs_run006b_maxCo10_short_compare.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    (SCRIPT_DIR / "run004b_vs_run006b_maxCo10_short_compare.json").write_text(
        json.dumps({"rows": [asdict(row) for row in rows]}, indent=2),
        encoding="utf-8",
    )
    write_markdown(rows)


def write_markdown(rows: list[Row]) -> None:
    primary = [r for r in rows if r.window == "t = 0.5..2 s"]
    run006 = primary[-1]
    lines = [
        "# V4b_3D short maxCo=1.0 smoke test",
        "",
        "`run006b` completed to `t = 2 s`. This is a speed/safety smoke test, not the final production averaging window.",
        "",
        "| Run | maxCo | window | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in primary:
        lines.append(
            f"| {row.run} | {row.maxCo:g} | {row.window} | {fmt(row.Cd_mean, 6)} | "
            f"{fmt(row.Cl_mean, 6)} | {fmt(row.Cl_rms, 6)} | {fmt(row.f_peak_Hz, 4)} | "
            f"{fmt(row.St, 5)} | {fmt(row.T_out_K, 3)} +/- {fmt(row.T_out_std_K, 3)} | "
            f"{fmt(row.Nu_EB_LMTD, 4)} +/- {fmt(row.Nu_EB_LMTD_std, 4)} |"
        )
    lines += [
        "",
        "Differences for `run006b` versus matched `run004b`:",
        "",
        "| Quantity | Difference |",
        "|---|---:|",
        f"| Cd_mean | {fmt_pct(run006.Cd_diff_pct_vs_run004b)} |",
        f"| Cl_rms | {fmt_pct(run006.Cl_rms_diff_pct_vs_run004b)} |",
        f"| St | {fmt_pct(run006.St_diff_pct_vs_run004b)} |",
        f"| T_out | {run006.T_out_diff_K_vs_run004b:+.3f} K |",
        f"| Nu_EB | {fmt_pct(run006.Nu_diff_pct_vs_run004b)} |",
        "",
        "Interpretation: `maxCo=1.0` completed cleanly and matches the `maxCo=0.8` reference extremely closely over the early common window. This supports stability/speed viability for short checks, but `maxCo=0.8` remains the more conservative production default.",
    ]
    (SCRIPT_DIR / "run004b_vs_run006b_maxCo10_short_compare.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_outputs(rows)
    for row in rows:
        if row.run == "run006b":
            print(
                f"{row.window}: Cd diff={row.Cd_diff_pct_vs_run004b:.4f}%, "
                f"St diff={row.St_diff_pct_vs_run004b:.4f}%, "
                f"Nu diff={row.Nu_diff_pct_vs_run004b:.4f}%"
            )


if __name__ == "__main__":
    main()
