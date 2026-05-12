"""
Inlet-sensitivity comparison for V4b_3D Re=200: run004b vs run005.

run004b is the accepted Lin=2D, Lout=8D reference. run005 keeps Lout=8D and
extends only Lin to 4D. Both runs use raw forceCoeffs and reconstructed outlet
patch fields for EB+LMTD heat-transfer metrics.
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


SCRIPT_DIR = Path(__file__).resolve().parent
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
        "Lin_D": 2.0,
        "Lout_D": 8.0,
        "case_dirs": [
            Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run004b"),
            Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run004b"),
            Path("/home/hexmachina/of_runs/V4b_3D_run004b"),
        ],
    },
    "run005": {
        "Lin_D": 4.0,
        "Lout_D": 8.0,
        "case_dirs": [
            Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run005"),
            Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run005"),
            Path("/home/hexmachina/of_runs/V4b_3D_run005"),
        ],
    },
}


@dataclass
class Row:
    run: str
    Lin_D: float
    Lout_D: float
    source: str
    window: str
    Cd_mean: float
    Cl_mean: float
    Cl_rms: float
    Cd_min: float
    Cd_max: float
    Cl_min: float
    Cl_max: float
    f_peak_Hz: float | None
    f_fft_Hz: float | None
    second_harmonic_Hz: float | None
    St: float | None
    T_out_K: float
    T_out_std_K: float
    T_out_mass_K: float
    m_dot_kg_s: float
    Q_total_W: float
    Q_total_std_W: float
    LMTD_K: float
    Nu_EB_LMTD: float
    Nu_EB_LMTD_std: float
    Cd_diff_pct_vs_run004b: float | None = None
    Cl_rms_diff_pct_vs_run004b: float | None = None
    St_diff_pct_vs_run004b: float | None = None
    T_out_diff_K_vs_run004b: float | None = None
    Nu_diff_pct_vs_run004b: float | None = None


def first_existing(paths: list[Path]) -> Path:
    for path in paths:
        try:
            if path.exists():
                return path
        except OSError:
            continue
    raise FileNotFoundError("None of the case path candidates exists")


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
            if len(parts) >= 4:
                rows.append([float(parts[0]), float(parts[2]), float(parts[3])])
    arr = np.asarray(rows, dtype=float)
    if arr.size == 0:
        raise ValueError(f"No force rows in {path}")
    return {"time": arr[:, 0], "Cd": arr[:, 1], "Cl": arr[:, 2]}


def peak_pick_frequency(time: np.ndarray, signal: np.ndarray) -> tuple[float | None, float | None]:
    mask = (time >= WINDOW_START) & (time <= WINDOW_END)
    t = time[mask]
    y = signal[mask]
    peaks = []
    for i in range(1, len(t) - 1):
        if y[i] > y[i - 1] and y[i] > y[i + 1]:
            peaks.append(t[i])
    peaks = np.asarray(peaks, dtype=float)
    if len(peaks) < 3:
        return None, None
    second_harmonic = 1.0 / float(np.mean(np.diff(peaks)))
    fundamental = 1.0 / float(np.mean(peaks[2:] - peaks[:-2]))
    return fundamental, second_harmonic


def fft_frequency(time: np.ndarray, signal: np.ndarray) -> tuple[float | None, float | None]:
    mask = (time >= WINDOW_START) & (time <= WINDOW_END)
    t = time[mask]
    y = signal[mask]
    if len(t) < 16:
        return None, None
    dt = float(np.median(np.diff(t)))
    ti = np.arange(t[0], t[-1], dt)
    yi = np.interp(ti, t, y) - float(np.mean(y))
    freqs = np.fft.rfftfreq(len(yi), d=dt)
    power = np.abs(np.fft.rfft(yi)) ** 2

    def band_peak(lo: float, hi: float) -> float | None:
        idx = np.where((freqs >= lo) & (freqs <= hi))[0]
        if len(idx) == 0:
            return None
        return float(freqs[idx[np.argmax(power[idx])]])

    return band_peak(2.5, 4.0), band_peak(5.5, 7.5)


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
    if not match:
        raise ValueError(f"Could not parse points from {path}")
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


def force_stats(case_dir: Path) -> dict[str, float | None]:
    data = parse_force_coeffs(case_dir / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat")
    mask = (data["time"] >= WINDOW_START) & (data["time"] <= WINDOW_END)
    cd = data["Cd"][mask]
    cl = data["Cl"][mask]
    cl_mean = float(np.mean(cl))
    f_peak, f2_peak = peak_pick_frequency(data["time"], data["Cl"])
    f_fft, f2_fft = fft_frequency(data["time"], data["Cl"])
    f = f_peak if f_peak is not None else f_fft
    return {
        "Cd_mean": float(np.mean(cd)),
        "Cl_mean": cl_mean,
        "Cl_rms": float(np.sqrt(np.mean((cl - cl_mean) ** 2))),
        "Cd_min": float(np.min(cd)),
        "Cd_max": float(np.max(cd)),
        "Cl_min": float(np.min(cl)),
        "Cl_max": float(np.max(cl)),
        "f_peak": f_peak,
        "f_fft": f_fft,
        "f2": f2_peak if f2_peak is not None else f2_fft,
        "St": f * D / U_IN if f is not None else None,
    }


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


def build_rows() -> list[Row]:
    rows = []
    for run, meta in CASES.items():
        case_dir = first_existing(meta["case_dirs"])
        f = force_stats(case_dir)
        th = thermal_stats(case_dir)
        rows.append(
            Row(
                run=run,
                Lin_D=meta["Lin_D"],
                Lout_D=meta["Lout_D"],
                source="raw forceCoeffs + reconstructed outlet fields",
                window=f"t = {WINDOW_START:g}..{WINDOW_END:g} s",
                Cd_mean=f["Cd_mean"],
                Cl_mean=f["Cl_mean"],
                Cl_rms=f["Cl_rms"],
                Cd_min=f["Cd_min"],
                Cd_max=f["Cd_max"],
                Cl_min=f["Cl_min"],
                Cl_max=f["Cl_max"],
                f_peak_Hz=f["f_peak"],
                f_fft_Hz=f["f_fft"],
                second_harmonic_Hz=f["f2"],
                St=f["St"],
                T_out_K=th["T_out"],
                T_out_std_K=th["T_out_std"],
                T_out_mass_K=th["T_out_mass"],
                m_dot_kg_s=th["m_dot"],
                Q_total_W=th["Q_total"],
                Q_total_std_W=th["Q_total_std"],
                LMTD_K=th["LMTD"],
                Nu_EB_LMTD=th["Nu_EB"],
                Nu_EB_LMTD_std=th["Nu_EB_std"],
            )
        )
    baseline = rows[0]
    for row in rows:
        row.Cd_diff_pct_vs_run004b = pct(row.Cd_mean, baseline.Cd_mean)
        row.Cl_rms_diff_pct_vs_run004b = pct(row.Cl_rms, baseline.Cl_rms)
        row.St_diff_pct_vs_run004b = pct(row.St, baseline.St)
        row.T_out_diff_K_vs_run004b = row.T_out_K - baseline.T_out_K
        row.Nu_diff_pct_vs_run004b = pct(row.Nu_EB_LMTD, baseline.Nu_EB_LMTD)
    return rows


def write_outputs(rows: list[Row]) -> None:
    with (SCRIPT_DIR / "run004b_vs_run005_inlet_compare.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    (SCRIPT_DIR / "run004b_vs_run005_inlet_compare.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "window": f"t = {WINDOW_START:g}..{WINDOW_END:g} s",
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


def write_markdown(rows: list[Row]) -> None:
    r2, r4 = rows
    lines = [
        "# V4b_3D inlet sensitivity: Lin=2D vs Lin=4D",
        "",
        f"Both cases use `Lout=8D` and the matched window `t = {WINDOW_START:g}..{WINDOW_END:g} s`.",
        "",
        "| Run | Lin/D | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.run} | {row.Lin_D:g} | {fmt(row.Cd_mean, 3)} | {fmt(row.Cl_mean, 3)} | "
            f"{fmt(row.Cl_rms, 3)} | {fmt(row.f_peak_Hz, 3)} | {fmt(row.St, 4)} | "
            f"{fmt(row.T_out_K, 3)} +/- {fmt(row.T_out_std_K, 3)} | "
            f"{fmt(row.Nu_EB_LMTD, 3)} +/- {fmt(row.Nu_EB_LMTD_std, 3)} |"
        )
    lines += [
        "",
        "## Differences",
        "",
        "| Comparison | Cd | Cl_rms | St | T_out | Nu_EB |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Lin=4D vs Lin=2D | {fmt_pct(r4.Cd_diff_pct_vs_run004b)} | "
        f"{fmt_pct(r4.Cl_rms_diff_pct_vs_run004b)} | {fmt_pct(r4.St_diff_pct_vs_run004b)} | "
        f"{r4.T_out_diff_K_vs_run004b:+.3f} K | {fmt_pct(r4.Nu_diff_pct_vs_run004b)} |",
        "",
        "## Conclusion",
        "",
        "The `Lin=4D` inlet check is essentially identical to the accepted `Lin=2D`, `Lout=8D` reference for forces, shedding frequency, and EB+LMTD heat transfer. This closes the inlet-sensitivity question for the current medium BL mesh family: `Lin=2D`, `Lout=8D` remains defensible for the next production or timestep-sensitivity run.",
    ]
    (SCRIPT_DIR / "run004b_vs_run005_inlet_compare.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_summary(rows: list[Row]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    labels = [f"{r.run}\nLin={r.Lin_D:g}D" for r in rows]
    fig, axes = plt.subplots(1, 4, figsize=(13, 4))
    metrics = [
        ("Cd", [r.Cd_mean for r in rows]),
        ("St", [r.St for r in rows]),
        ("T_out [K]", [r.T_out_K for r in rows]),
        ("Nu_EB", [r.Nu_EB_LMTD for r in rows]),
    ]
    for ax, (title, values) in zip(axes, metrics):
        ax.plot(labels, values, marker="o", color="#2f6f73", lw=2)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
    fig.suptitle("V4b_3D inlet sensitivity: Lin=2D vs Lin=4D")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run004b_vs_run005_inlet_sensitivity.png", dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    write_outputs(rows)
    print(f"Wrote inlet comparison outputs in {SCRIPT_DIR}")
    for row in rows:
        print(
            f"{row.run}: Cd={row.Cd_mean:.6f}, Cl_rms={row.Cl_rms:.6f}, "
            f"St={row.St:.6f}, T_out={row.T_out_K:.6f}, Nu={row.Nu_EB_LMTD:.6f}"
        )


if __name__ == "__main__":
    main()
