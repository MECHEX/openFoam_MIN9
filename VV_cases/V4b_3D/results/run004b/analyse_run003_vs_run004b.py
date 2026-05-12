"""
Compare V4b_3D run003 (Lout=5D) against run004b (Lout=8D).

The active run004b forceCoeffs live in WSL. The run003 raw force file is not
available in this checkout, so run003 is treated as an archived summary
baseline unless a raw force file is found in one of the known locations.
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
REPO_ROOT = SCRIPT_DIR.parents[3]
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
WINDOW_STARTS = (2.0, 3.0, 4.0)
RECOMMENDED_WINDOW = 3.0

RUN004B_FORCE_CANDIDATES = [
    Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run004b\postProcessing\forceCoeffs\0\forceCoeffs.dat"),
    Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run004b\postProcessing\forceCoeffs\0\forceCoeffs.dat"),
    Path("/home/hexmachina/of_runs/V4b_3D_run004b/postProcessing/forceCoeffs/0/forceCoeffs.dat"),
]

RUN004B_CASE_CANDIDATES = [
    Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run004b"),
    Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run004b"),
    Path("/home/hexmachina/of_runs/V4b_3D_run004b"),
]

RUN003_FORCE_CANDIDATES = [
    Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run003\postProcessing\forceCoeffs\0\forceCoeffs.dat"),
    Path(r"\\wsl.localhost\Ubuntu\home\kik\of_runs\V4b_3D_run003\postProcessing\forces_tube\0\force.dat"),
    Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run003\postProcessing\forces_tube\0\force.dat"),
]


@dataclass
class ForceStats:
    run: str
    source: str
    window: str
    n: int | None
    Cd_mean: float | None
    Cl_mean: float | None
    Cl_rms: float | None
    Cd_min: float | None
    Cd_max: float | None
    Cl_min: float | None
    Cl_max: float | None
    f_peak_picking_Hz: float | None
    f_psd_Hz: float | None
    f_second_harmonic_Hz: float | None
    St: float | None
    Cd_diff_pct_vs_run003: float | None = None
    Cl_mean_diff_pct_vs_run003: float | None = None
    Cl_rms_diff_pct_vs_run003: float | None = None
    St_diff_pct_vs_run003: float | None = None


@dataclass
class ThermalStats:
    run: str
    source: str
    window: str
    n_times: int
    T_out_area_K: float
    T_out_area_std_K: float
    T_out_mass_K: float
    outlet_area_m2: float
    m_dot_kg_s: float
    m_dot_std_kg_s: float
    Q_total_W: float
    Q_total_std_W: float
    LMTD_K: float
    Nu_EB_LMTD: float
    Nu_EB_LMTD_std: float
    T_out_diff_K_vs_run003: float
    Nu_diff_pct_vs_run003: float
    Q_diff_pct_vs_run003: float


def _fmt(value: float | None, digits: int = 4) -> str:
    if value is None or not math.isfinite(value):
        return "N/A"
    return f"{value:.{digits}f}"


def _pct(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "N/A"
    return f"{value:+.2f}%"


def first_existing(candidates: list[Path]) -> Path | None:
    for path in candidates:
        try:
            if path.exists():
                return path
        except OSError:
            continue
    return None


def parse_force_coeffs(path: Path) -> dict[str, np.ndarray]:
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            rows.append([float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])])
    if not rows:
        raise ValueError(f"No force coefficient rows found in {path}")
    arr = np.asarray(rows, dtype=float)
    return {"time": arr[:, 0], "Cm": arr[:, 1], "Cd": arr[:, 2], "Cl": arr[:, 3]}


def parse_run003_archived() -> dict[str, float]:
    summary = (RUN003_DIR / "summary.md").read_text(encoding="utf-8", errors="replace")

    def table_value(name: str) -> float:
        match = re.search(rf"\|\s*{re.escape(name)}\s*\|\s*\**\s*([0-9.+\-eE]+)", summary)
        if not match:
            raise ValueError(f"Could not find {name} in run003 summary.md")
        return float(match.group(1))

    return {
        "Cd_mean": table_value("Cd_mean"),
        "Cl_rms": table_value("Cl_rms"),
        "Cl_mean": table_value("Cl_mean"),
        "f_shed": table_value("f_shed"),
        "St": table_value("St"),
        "T_out": table_value("T_out"),
        "Nu_EB": table_value("**EB+LMTD** (preferred)"),
        "Q_total": bullet_value("Q_total"),
        "LMTD": bullet_value("LMTD"),
    }


def bullet_value(name: str) -> float:
    summary = (RUN003_DIR / "summary.md").read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(name)}\s*=\s*([0-9.+\-eE]+)", summary)
    if not match:
        raise ValueError(f"Could not find {name} in run003 summary.md")
    return float(match.group(1))


def local_maxima_times(time: np.ndarray, signal: np.ndarray, start: float) -> np.ndarray:
    mask = time >= start
    t = time[mask]
    y = signal[mask]
    if len(t) < 3:
        return np.asarray([], dtype=float)
    peaks = []
    for i in range(1, len(t) - 1):
        if y[i] > y[i - 1] and y[i] > y[i + 1]:
            peaks.append(t[i])
    return np.asarray(peaks, dtype=float)


def peak_pick_frequency(time: np.ndarray, cl: np.ndarray, start: float) -> tuple[float | None, float | None]:
    peaks = local_maxima_times(time, cl, start)
    if len(peaks) < 3:
        return None, None
    adjacent = np.diff(peaks)
    every_second = peaks[2:] - peaks[:-2]
    f_second_harmonic = 1.0 / float(np.mean(adjacent))
    f_fundamental = 1.0 / float(np.mean(every_second))
    return f_fundamental, f_second_harmonic


def psd_frequency(time: np.ndarray, cl: np.ndarray, start: float) -> tuple[float | None, float | None, np.ndarray, np.ndarray]:
    mask = time >= start
    t = time[mask]
    y = cl[mask]
    if len(t) < 16:
        return None, None, np.asarray([]), np.asarray([])
    dt = float(np.median(np.diff(t)))
    uniform_t = np.arange(t[0], t[-1], dt)
    uniform_y = np.interp(uniform_t, t, y)
    uniform_y = uniform_y - np.mean(uniform_y)
    fs = 1.0 / dt
    nperseg = min(len(uniform_y), 2048)
    freqs, psd = welch(uniform_y, fs=fs, nperseg=nperseg)

    def peak_in(lo: float, hi: float) -> float | None:
        band = (freqs >= lo) & (freqs <= hi)
        if not np.any(band):
            return None
        idxs = np.where(band)[0]
        return float(freqs[idxs[np.argmax(psd[idxs])]])

    return peak_in(2.5, 4.0), peak_in(5.5, 7.5), freqs, psd


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def _parse_scalar_list_after_value(section: str) -> np.ndarray:
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.asarray([float(uniform.group(1))], dtype=float)
    match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, flags=re.S)
    if not match:
        raise ValueError("Could not parse nonuniform scalar boundary values")
    n = int(match.group(1))
    vals = np.fromstring(match.group(2), sep=" ", dtype=float)
    if len(vals) != n:
        raise ValueError(f"Expected {n} boundary values, parsed {len(vals)}")
    return vals


def boundary_patch(case_dir: Path, patch_name: str) -> dict[str, int]:
    text = (case_dir / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
    pattern = rf"{re.escape(patch_name)}\s*\{{(.*?)\}}"
    match = re.search(pattern, text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name!r} not found in boundary")
    section = match.group(1)
    n_faces = int(re.search(r"nFaces\s+(\d+)\s*;", section).group(1))
    start_face = int(re.search(r"startFace\s+(\d+)\s*;", section).group(1))
    return {"nFaces": n_faces, "startFace": start_face}


def field_patch_values(case_dir: Path, time_name: str, field_name: str, patch_name: str, n_faces: int) -> np.ndarray:
    text = (case_dir / time_name / field_name).read_text(encoding="utf-8", errors="replace")
    pattern = rf"{re.escape(patch_name)}\s*\{{(.*?)\n\s*\}}"
    match = re.search(pattern, text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name!r} not found in field {field_name}")
    values = _parse_scalar_list_after_value(match.group(1))
    if len(values) == 1:
        values = np.full(n_faces, float(values[0]))
    if len(values) != n_faces:
        raise ValueError(f"{field_name}:{patch_name} has {len(values)} values, expected {n_faces}")
    return values


def parse_points(path: Path) -> np.ndarray:
    text = _strip_comments(path.read_text(encoding="utf-8", errors="replace"))
    match = re.search(r"\n\s*(\d+)\s*\(\s*(.*?)\s*\)\s*$", text, flags=re.S)
    if not match:
        raise ValueError(f"Could not parse points from {path}")
    vals = np.fromstring(match.group(2).replace("(", " ").replace(")", " "), sep=" ", dtype=float)
    return vals.reshape((-1, 3))


def outlet_faces(path: Path, start_face: int, n_faces: int) -> list[list[int]]:
    faces: list[list[int]] = []
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
            if face_index >= start_face and face_index < end_face:
                nums = [int(v) for v in re.findall(r"\d+", line)]
                if len(nums) < 4:
                    raise ValueError(f"Could not parse face line: {line}")
                n = nums[0]
                faces.append(nums[1: 1 + n])
            face_index += 1
            if face_index >= end_face:
                break
    if len(faces) != n_faces:
        raise ValueError(f"Expected {n_faces} outlet faces, parsed {len(faces)}")
    return faces


def polygon_area(points: np.ndarray) -> float:
    if len(points) < 3:
        return 0.0
    origin = points[0]
    area_vec = np.zeros(3)
    for i in range(1, len(points) - 1):
        area_vec += np.cross(points[i] - origin, points[i + 1] - origin)
    return 0.5 * float(np.linalg.norm(area_vec))


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    if d1 <= 0 or d2 <= 0:
        raise ValueError("Invalid LMTD temperature differences")
    if abs(d1 - d2) < 1e-12:
        return d1
    return (d1 - d2) / math.log(d1 / d2)


def available_reconstructed_times(case_dir: Path, start: float, end: float) -> list[str]:
    times: list[tuple[float, str]] = []
    for path in case_dir.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if start <= t <= end and (path / "T").exists() and (path / "phi").exists():
            times.append((t, path.name))
    return [name for _, name in sorted(times)]


def compute_run004b_thermal(case_dir: Path, run003_values: dict[str, float], start: float = 3.0, end: float = 6.0) -> ThermalStats:
    patch = boundary_patch(case_dir, "outlet")
    n_faces = patch["nFaces"]
    pts = parse_points(case_dir / "constant" / "polyMesh" / "points")
    faces = outlet_faces(case_dir / "constant" / "polyMesh" / "faces", patch["startFace"], n_faces)
    areas = np.asarray([polygon_area(pts[face]) for face in faces], dtype=float)
    outlet_area = float(np.sum(areas))
    time_names = available_reconstructed_times(case_dir, start, end)
    if not time_names:
        raise ValueError(f"No reconstructed times found in {case_dir} for {start}..{end}")

    t_area_values = []
    t_mass_values = []
    m_dot_values = []
    q_values = []
    lmtd_values = []
    nu_values = []
    for time_name in time_names:
        t_vals = field_patch_values(case_dir, time_name, "T", "outlet", n_faces)
        phi_vals = field_patch_values(case_dir, time_name, "phi", "outlet", n_faces)
        t_area_i = float(np.sum(t_vals * areas) / outlet_area)
        positive_phi = np.maximum(phi_vals, 0.0)
        m_dot_i = float(np.sum(positive_phi))
        if m_dot_i <= 0:
            m_dot_i = float(abs(np.sum(phi_vals)))
            weights = np.abs(phi_vals)
        else:
            weights = positive_phi
        t_mass_i = float(np.sum(t_vals * weights) / np.sum(weights))
        q_total_i = m_dot_i * CP_AIR * (t_area_i - T_IN)
        lmtd_i = lmtd(t_area_i)
        h_i = q_total_i / (A_HOT_TOTAL * lmtd_i)
        nu_i = h_i * D / K_AIR
        t_area_values.append(t_area_i)
        t_mass_values.append(t_mass_i)
        m_dot_values.append(m_dot_i)
        q_values.append(q_total_i)
        lmtd_values.append(lmtd_i)
        nu_values.append(nu_i)

    t_area = float(np.mean(t_area_values))
    t_mass = float(np.mean(t_mass_values))
    m_dot = float(np.mean(m_dot_values))
    q_total = float(np.mean(q_values))
    lmtd_value = float(np.mean(lmtd_values))
    nu = float(np.mean(nu_values))
    return ThermalStats(
        run="run004b",
        source="reconstructed outlet patch values",
        window=f"t = {start:g}..{end:g} s",
        n_times=len(time_names),
        T_out_area_K=t_area,
        T_out_area_std_K=float(np.std(t_area_values)),
        T_out_mass_K=t_mass,
        outlet_area_m2=outlet_area,
        m_dot_kg_s=m_dot,
        m_dot_std_kg_s=float(np.std(m_dot_values)),
        Q_total_W=q_total,
        Q_total_std_W=float(np.std(q_values)),
        LMTD_K=lmtd_value,
        Nu_EB_LMTD=nu,
        Nu_EB_LMTD_std=float(np.std(nu_values)),
        T_out_diff_K_vs_run003=t_area - run003_values["T_out"],
        Nu_diff_pct_vs_run003=pct_diff(nu, run003_values["Nu_EB"]) or float("nan"),
        Q_diff_pct_vs_run003=pct_diff(q_total, run003_values["Q_total"]) or float("nan"),
    )


def stats_for_window(data: dict[str, np.ndarray], start: float) -> ForceStats:
    time = data["time"]
    cd = data["Cd"]
    cl = data["Cl"]
    mask = time >= start
    t = time[mask]
    cdw = cd[mask]
    clw = cl[mask]
    if len(t) == 0:
        raise ValueError(f"No run004b samples for t >= {start}")

    cl_mean = float(np.mean(clw))
    cl_rms = float(np.sqrt(np.mean((clw - cl_mean) ** 2)))
    f_peak, f_peak_2 = peak_pick_frequency(time, cl, start)
    f_psd, f_psd_2, _, _ = psd_frequency(time, cl, start)
    f_for_st = f_peak if f_peak is not None else f_psd

    return ForceStats(
        run="run004b",
        source="raw forceCoeffs",
        window=f"t >= {start:g} s",
        n=int(len(t)),
        Cd_mean=float(np.mean(cdw)),
        Cl_mean=cl_mean,
        Cl_rms=cl_rms,
        Cd_min=float(np.min(cdw)),
        Cd_max=float(np.max(cdw)),
        Cl_min=float(np.min(clw)),
        Cl_max=float(np.max(clw)),
        f_peak_picking_Hz=f_peak,
        f_psd_Hz=f_psd,
        f_second_harmonic_Hz=f_peak_2 if f_peak_2 is not None else f_psd_2,
        St=(f_for_st * D / U_IN) if f_for_st is not None else None,
    )


def archived_run003_stats(values: dict[str, float]) -> ForceStats:
    return ForceStats(
        run="run003",
        source="archived summary baseline",
        window="archived reported window",
        n=None,
        Cd_mean=values["Cd_mean"],
        Cl_mean=values["Cl_mean"],
        Cl_rms=values["Cl_rms"],
        Cd_min=None,
        Cd_max=None,
        Cl_min=None,
        Cl_max=None,
        f_peak_picking_Hz=values["f_shed"],
        f_psd_Hz=None,
        f_second_harmonic_Hz=2.0 * values["f_shed"],
        St=values["St"],
    )


def add_diffs(rows: list[ForceStats], baseline: ForceStats) -> None:
    for row in rows:
        if row.run == baseline.run:
            continue
        row.Cd_diff_pct_vs_run003 = pct_diff(row.Cd_mean, baseline.Cd_mean)
        row.Cl_mean_diff_pct_vs_run003 = pct_diff(row.Cl_mean, baseline.Cl_mean)
        row.Cl_rms_diff_pct_vs_run003 = pct_diff(row.Cl_rms, baseline.Cl_rms)
        row.St_diff_pct_vs_run003 = pct_diff(row.St, baseline.St)


def pct_diff(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline in (None, 0):
        return None
    return 100.0 * (value - baseline) / baseline


def write_csv(path: Path, rows: list[ForceStats]) -> None:
    keys = list(asdict(rows[0]).keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def plot_time_traces(data: dict[str, np.ndarray], baseline: ForceStats) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    time = data["time"]
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(time, data["Cd"], color="#2f6f73", lw=1.1, label="run004b raw")
    axes[0].axhline(baseline.Cd_mean, color="#c05746", ls="--", lw=1.2, label="run003 archived mean")
    axes[0].set_ylabel("Cd")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.25)

    axes[1].plot(time, data["Cl"], color="#395b9d", lw=1.1, label="run004b raw")
    axes[1].axhline(baseline.Cl_mean, color="#c05746", ls="--", lw=1.2, label="run003 archived mean")
    axes[1].set_ylabel("Cl")
    axes[1].set_xlabel("time [s]")
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.25)

    for ax in axes:
        ax.axvspan(RECOMMENDED_WINDOW, time[-1], color="#f2c14e", alpha=0.10, label=None)
    fig.suptitle("run004b force coefficients with run003 archived mean references")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run003_vs_run004b_force_traces.png", dpi=180)
    plt.close(fig)


def plot_psd(data: dict[str, np.ndarray], baseline: ForceStats) -> None:
    f_psd, f2_psd, freqs, psd = psd_frequency(data["time"], data["Cl"], RECOMMENDED_WINDOW)
    if len(freqs) == 0:
        return
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.semilogy(freqs, psd, color="#594157", lw=1.2)
    ax.axvline(baseline.f_peak_picking_Hz, color="#c05746", ls="--", lw=1.1, label="run003 f_shed")
    if f_psd is not None:
        ax.axvline(f_psd, color="#2f6f73", ls="-", lw=1.1, label=f"run004b PSD fundamental band {f_psd:.3f} Hz")
    if f2_psd is not None:
        ax.axvline(f2_psd, color="#e0a100", ls=":", lw=1.4, label=f"run004b PSD 2nd harmonic band {f2_psd:.3f} Hz")
    ax.set_xlim(0, 12)
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("PSD(Cl)")
    ax.set_title("run004b Cl spectrum, t >= 3 s")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run004b_cl_psd.png", dpi=180)
    plt.close(fig)


def markdown_summary(
    rows: list[ForceStats],
    run003_values: dict[str, float],
    raw_run003_found: bool,
    thermal: ThermalStats | None,
) -> str:
    rec = next(r for r in rows if r.run == "run004b" and r.window == f"t >= {RECOMMENDED_WINDOW:g} s")
    run003 = rows[0]
    lines = [
        "## Final run003 vs run004b comparison",
        "",
        "This section is generated by `analyse_run003_vs_run004b.py`.",
        "",
        "Data status:",
        "",
        f"- `run004b`: raw `forceCoeffs.dat`, completed to `t = 6 s`.",
        f"- `run003`: {'raw force file found' if raw_run003_found else 'archived summary baseline; raw force file not found in the active WSL/repo checkout'}.",
        "",
        "| Run/window | Cd_mean | Cl_mean | Cl_rms/std | f_shed | St | Cd diff vs run003 | St diff vs run003 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        f = row.f_peak_picking_Hz or row.f_psd_Hz
        lines.append(
            "| "
            f"{row.run} {row.window} | {_fmt(row.Cd_mean, 3)} | {_fmt(row.Cl_mean, 3)} | "
            f"{_fmt(row.Cl_rms, 3)} | {_fmt(f, 3)} | {_fmt(row.St, 4)} | "
            f"{_pct(row.Cd_diff_pct_vs_run003)} | {_pct(row.St_diff_pct_vs_run003)} |"
        )
    lines += [
        "",
        f"Recommended comparison window: `t >= {RECOMMENDED_WINDOW:g} s`.",
        "",
        "Interpretation:",
        "",
        f"- The flow regime remains periodic; `run004b` gives `St = {_fmt(rec.St, 4)}` versus `run003` `St = {_fmt(run003.St, 4)}`.",
        f"- The mean lift offset is essentially unchanged: `Cl_mean = {_fmt(rec.Cl_mean, 3)}` versus `run003` `{_fmt(run003.Cl_mean, 3)}`.",
        f"- The shedding amplitude is comparable: `Cl_rms/std = {_fmt(rec.Cl_rms, 3)}` versus `run003` `{_fmt(run003.Cl_rms, 3)}`.",
        f"- Drag remains measurably higher in the `Lout=8D` case: `Cd_mean = {_fmt(rec.Cd_mean, 3)}`, `{_pct(rec.Cd_diff_pct_vs_run003)}` versus `run003`.",
        "",
        "Decision:",
        "",
        "Do not start `Lout=16D` as a broad new campaign yet. The `8D` outlet confirms the same qualitative shedding regime, but the persistent drag offset is large enough that a short `16D` drag/outlet-independence check is scientifically justified if drag accuracy is important for the final claim. The thermal comparison below decides whether heat transfer also needs that `16D` check.",
        "",
        "Generated outputs:",
        "",
        "- `run003_vs_run004b_force_compare.csv`",
        "- `run003_vs_run004b_force_compare.json`",
        "- `figures/run003_vs_run004b_force_traces.png`",
        "- `figures/run004b_cl_psd.png`",
        "",
    ]
    if thermal is None:
        lines.append(
            f"Archived thermal baseline from `run003`: `T_out = {_fmt(run003_values.get('T_out'), 2)} K`; "
            "no matched `run004b` thermal value is available from the current postProcessing files."
        )
    else:
        lines += [
            "",
            "## Thermal EB+LMTD comparison",
            "",
            "Thermal metrics are computed from reconstructed `run004b` outlet patch values and averaged over the same recommended late window.",
            "",
            f"| Quantity | run003 archived | run004b {thermal.window} | Difference |",
            "|---|---:|---:|---:|",
            f"| T_out area-average | {_fmt(run003_values['T_out'], 2)} K | {_fmt(thermal.T_out_area_K, 2)} +/- {_fmt(thermal.T_out_area_std_K, 2)} K | {thermal.T_out_diff_K_vs_run003:+.2f} K |",
            f"| T_out mass-weighted check | N/A | {_fmt(thermal.T_out_mass_K, 2)} K | N/A |",
            f"| Q_total | {_fmt(run003_values['Q_total'], 3)} W | {_fmt(thermal.Q_total_W, 3)} +/- {_fmt(thermal.Q_total_std_W, 3)} W | {_pct(thermal.Q_diff_pct_vs_run003)} |",
            f"| LMTD | {_fmt(run003_values['LMTD'], 3)} K | {_fmt(thermal.LMTD_K, 3)} K | N/A |",
            f"| Nu_EB_LMTD | {_fmt(run003_values['Nu_EB'], 3)} | {_fmt(thermal.Nu_EB_LMTD, 3)} +/- {_fmt(thermal.Nu_EB_LMTD_std, 3)} | {_pct(thermal.Nu_diff_pct_vs_run003)} |",
            "",
            f"Constants used for `run004b`: `Cp = {CP_AIR:.1f} J/(kg K)`, `k = {K_AIR:.5f} W/(m K)`, "
            f"`A_hot_total = {A_HOT_TOTAL:.6f} m2`, `D = {D:.3f} m`.",
            "",
            "Thermal interpretation: the `Lout=8D` case gives a higher outlet temperature and higher EB+LMTD Nusselt number than the archived `run003` value. This means the outlet-length sensitivity is not only a drag question; heat-transfer metrics should be included in the `8D` vs possible `16D` decision.",
        ]
    return "\n".join(lines) + "\n"


def main() -> None:
    run004b_force = first_existing(RUN004B_FORCE_CANDIDATES)
    if run004b_force is None:
        raise FileNotFoundError("Could not find run004b forceCoeffs.dat in known WSL locations")

    raw_run003_found = first_existing(RUN003_FORCE_CANDIDATES) is not None
    run004b_case = first_existing(RUN004B_CASE_CANDIDATES)
    run004b = parse_force_coeffs(run004b_force)
    run003_values = parse_run003_archived()
    baseline = archived_run003_stats(run003_values)
    rows = [baseline] + [stats_for_window(run004b, start) for start in WINDOW_STARTS]
    add_diffs(rows, baseline)

    write_csv(SCRIPT_DIR / "run003_vs_run004b_force_compare.csv", rows)
    (SCRIPT_DIR / "run003_vs_run004b_force_compare.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "D_m": D,
                    "U_in_m_per_s": U_IN,
                    "run004b_force_file": str(run004b_force),
                    "run003_raw_force_found": raw_run003_found,
                    "recommended_window": f"t >= {RECOMMENDED_WINDOW:g} s",
                },
                "rows": [asdict(row) for row in rows],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    plot_time_traces(run004b, baseline)
    plot_psd(run004b, baseline)
    thermal = None
    if run004b_case is not None and (run004b_case / "6" / "T").exists():
        thermal = compute_run004b_thermal(run004b_case, run003_values)
        (SCRIPT_DIR / "run003_vs_run004b_thermal_compare.json").write_text(
            json.dumps(
                {
                    "metadata": {
                        "method": "EB+LMTD from reconstructed outlet patch values",
                        "T_in_K": T_IN,
                        "T_hot_K": T_HOT,
                        "D_m": D,
                        "A_hot_total_m2": A_HOT_TOTAL,
                        "Cp_J_per_kgK": CP_AIR,
                        "k_W_per_mK": K_AIR,
                    },
                    "run003_archived": {
                        "T_out_K": run003_values["T_out"],
                        "Q_total_W": run003_values["Q_total"],
                        "LMTD_K": run003_values["LMTD"],
                        "Nu_EB_LMTD": run003_values["Nu_EB"],
                    },
                    "run004b": asdict(thermal),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        with (SCRIPT_DIR / "run003_vs_run004b_thermal_compare.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["quantity", "run003_archived", "run004b_t3_to_t6_mean", "difference"])
            writer.writerow(["T_out_area_K", run003_values["T_out"], thermal.T_out_area_K, thermal.T_out_diff_K_vs_run003])
            writer.writerow(["T_out_area_std_K", "", thermal.T_out_area_std_K, ""])
            writer.writerow(["T_out_mass_K", "", thermal.T_out_mass_K, ""])
            writer.writerow(["Q_total_W", run003_values["Q_total"], thermal.Q_total_W, thermal.Q_diff_pct_vs_run003])
            writer.writerow(["Q_total_std_W", "", thermal.Q_total_std_W, ""])
            writer.writerow(["LMTD_K", run003_values["LMTD"], thermal.LMTD_K, ""])
            writer.writerow(["Nu_EB_LMTD", run003_values["Nu_EB"], thermal.Nu_EB_LMTD, thermal.Nu_diff_pct_vs_run003])
            writer.writerow(["Nu_EB_LMTD_std", "", thermal.Nu_EB_LMTD_std, ""])
    (SCRIPT_DIR / "run003_vs_run004b_summary_section.md").write_text(
        markdown_summary(rows, run003_values, raw_run003_found, thermal),
        encoding="utf-8",
    )
    print(f"Wrote comparison outputs in {SCRIPT_DIR}")


if __name__ == "__main__":
    main()
