from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import find_peaks, hilbert


RUN_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = RUN_DIR / "data" / "001"

CASE_CANDIDATES = [
    Path("/home/hexmachina/of_runs/V4b_3D_run009_varprops_movie"),
    Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run009_varprops_movie"),
    Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run009_varprops_movie"),
]

N_PHASES = 48
WINDOW_START = 2.0
WINDOW_END = 10.0
PREFERRED_START = 4.0


def find_case_dir() -> Path:
    for path in CASE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Could not find run009 case directory")


def read_force_coeffs(case_dir: Path) -> pd.DataFrame:
    path = case_dir / "postProcessing" / "forceCoeffs" / "0" / "forceCoeffs.dat"
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 4:
            rows.append(
                {
                    "time_s": float(parts[0]),
                    "Cm": float(parts[1]),
                    "Cd": float(parts[2]),
                    "Cl": float(parts[3]),
                }
            )
    return pd.DataFrame(rows)


def full_field_times(case_dir: Path) -> np.ndarray:
    proc0 = case_dir / "processor0"
    times = []
    for item in proc0.iterdir():
        if not item.is_dir() or not (item / "U").exists():
            continue
        try:
            times.append(float(item.name))
        except ValueError:
            pass
    return np.asarray(sorted(times), dtype=float)


def circular_distance(a: np.ndarray, b: float) -> np.ndarray:
    return np.abs(np.angle(np.exp(1j * (a - b))))


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    case_dir = find_case_dir()
    coeffs = read_force_coeffs(case_dir)
    window = coeffs[(coeffs["time_s"] >= WINDOW_START) & (coeffs["time_s"] <= WINDOW_END)].copy()
    if window.empty:
        raise RuntimeError("No force coefficient samples in the requested window")

    t = window["time_s"].to_numpy(float)
    cl = window["Cl"].to_numpy(float)
    dt_force = float(np.median(np.diff(coeffs["time_s"].to_numpy(float))))
    cl_fluct = cl - np.mean(cl)

    min_peak_distance = max(1, int(0.1 / dt_force))
    peaks, _ = find_peaks(cl_fluct, distance=min_peak_distance)
    peak_times = t[peaks]
    periods = np.diff(peak_times)

    phase = np.mod(np.angle(hilbert(cl_fluct)), 2.0 * np.pi)
    phase_unwrapped = np.unwrap(phase)
    phase_interp = interp1d(t, phase_unwrapped, bounds_error=False, fill_value="extrapolate")

    full_times = full_field_times(case_dir)
    full_times = full_times[(full_times >= WINDOW_START) & (full_times <= WINDOW_END)]
    if full_times.size == 0:
        raise RuntimeError("No full U-field snapshots in the requested window")

    full_phase = np.mod(phase_interp(full_times), 2.0 * np.pi)
    bins = np.linspace(0.0, 2.0 * np.pi, N_PHASES + 1)
    centers = 0.5 * (bins[:-1] + bins[1:])
    counts, _ = np.histogram(full_phase, bins)

    rows = []
    used_indices: set[int] = set()
    for i, target in enumerate(centers):
        distance = circular_distance(full_phase, target)
        preferred = np.where(full_times >= PREFERRED_START)[0]
        order = preferred[np.argsort(distance[preferred])] if preferred.size else np.argsort(distance)

        chosen = None
        for idx in order:
            if int(idx) not in used_indices:
                chosen = int(idx)
                break
        if chosen is None:
            chosen = int(np.argmin(distance))
        used_indices.add(chosen)

        rows.append(
            {
                "phase_index": i,
                "target_phase_deg": np.degrees(target),
                "time_s": full_times[chosen],
                "actual_phase_deg": np.degrees(full_phase[chosen]),
                "phase_error_deg": np.degrees(distance[chosen]),
                "source": "full_U_field",
            }
        )

    selected = pd.DataFrame(rows).sort_values("phase_index")
    selected["time_name"] = selected["time_s"].map(lambda x: f"{x:g}")
    selected.to_csv(DATA_DIR / "run009_001_48_phase_snapshot_selection.csv", index=False, float_format="%.10g")

    times_text = ",".join(selected["time_name"].tolist())
    (DATA_DIR / "run009_001_48_phase_times.txt").write_text(times_text + "\n", encoding="utf-8")

    summary_lines = [
        "# V4b_3D run009: 48-phase full-field snapshot selection",
        "",
        f"- case: `{case_dir}`",
        f"- Cl phase window: `{WINDOW_START:g}..{WINDOW_END:g} s`",
        f"- preferred selected-time window: `t >= {PREFERRED_START:g} s`",
        f"- force coefficient samples in window: `{len(window)}`",
        f"- full U-field snapshots in window: `{len(full_times)}`",
        f"- 48 phase-bin coverage: min `{int(counts.min())}`, max `{int(counts.max())}`, empty `{int(np.sum(counts == 0))}`",
        f"- selected unique full-field times: `{selected['time_s'].nunique()}`",
        f"- mean phase error: `{selected['phase_error_deg'].mean():.3f} deg`",
        f"- max phase error: `{selected['phase_error_deg'].max():.3f} deg`",
        f"- Cl mean/min/max/rms in window: `{np.mean(cl):.6g}`, `{np.min(cl):.6g}`, `{np.max(cl):.6g}`, `{np.sqrt(np.mean(cl_fluct**2)):.6g}`",
    ]
    if periods.size:
        summary_lines += [
            f"- detected Cl peaks: `{len(peak_times)}`",
            f"- mean shedding period: `{np.mean(periods):.6g} s`",
            f"- mean shedding frequency: `{1.0 / np.mean(periods):.6g} Hz`",
        ]
    summary_lines += [
        "",
        "Use `run009_001_48_phase_times.txt` as the time selector for Q/Lambda2",
        "post-processing. The list contains one full-field snapshot per phase bin.",
        "",
    ]
    (DATA_DIR / "run009_001_48_phase_snapshot_selection.md").write_text(
        "\n".join(summary_lines), encoding="utf-8"
    )

    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
