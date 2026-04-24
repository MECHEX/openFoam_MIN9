from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import V2AStudy as study


RUN_DIR = study.ACTIVE_RUN_DIR
PLOTS_DIR = RUN_DIR / "plots"


def ensure_dirs() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def load_force_coeffs(case_dir: Path) -> list[tuple[float, float, float]]:
    coeff_file = study.latest_force_coeff_file(case_dir)
    if coeff_file is None or not coeff_file.exists():
        return []

    rows: list[tuple[float, float, float]] = []
    for line in coeff_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 5:
            continue
        rows.append((float(parts[0]), float(parts[1]), float(parts[4])))
    return rows


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def rms(values: list[float]) -> float | None:
    if not values:
        return None
    avg = mean(values)
    assert avg is not None
    return math.sqrt(sum((v - avg) ** 2 for v in values) / len(values))


def spectral_peak(case: dict, coeffs: list[tuple[float, float, float]]) -> dict[str, float | int | bool | None]:
    if len(coeffs) < 20:
        return {
            "samples": len(coeffs),
            "window_start_s": None,
            "window_end_s": None,
            "Cl_rms": None,
            "freq_hz": None,
            "St_peak": None,
            "lowest_bin_peak": None,
        }

    tail = max(20, len(coeffs) // 2)
    tail_rows = coeffs[-tail:]
    times = [row[0] for row in tail_rows]
    cls = [row[2] for row in tail_rows]
    dt = mean([b - a for a, b in zip(times[:-1], times[1:])])
    if dt is None or dt <= 0.0:
        return {
            "samples": len(tail_rows),
            "window_start_s": times[0],
            "window_end_s": times[-1],
            "Cl_rms": None,
            "freq_hz": None,
            "St_peak": None,
            "lowest_bin_peak": None,
        }

    cl_mean = mean(cls)
    assert cl_mean is not None
    centered = [value - cl_mean for value in cls]
    cl_rms = rms(centered)
    if cl_rms is None or cl_rms < 1e-9:
        return {
            "samples": len(tail_rows),
            "window_start_s": times[0],
            "window_end_s": times[-1],
            "Cl_rms": cl_rms,
            "freq_hz": None,
            "St_peak": None,
            "lowest_bin_peak": None,
        }

    spectrum = study._fft(centered)
    n_fft = len(spectrum)
    best_idx = None
    best_amp = -1.0
    for idx in range(1, n_fft // 2):
        amp = abs(spectrum[idx])
        if amp > best_amp:
            best_amp = amp
            best_idx = idx

    if best_idx is None:
        return {
            "samples": len(tail_rows),
            "window_start_s": times[0],
            "window_end_s": times[-1],
            "Cl_rms": cl_rms,
            "freq_hz": None,
            "St_peak": None,
            "lowest_bin_peak": None,
        }

    freq_hz = best_idx / (n_fft * dt)
    u_inf = case["Re"] * study.NU / study.D
    st_peak = freq_hz * study.D / u_inf
    return {
        "samples": len(tail_rows),
        "window_start_s": times[0],
        "window_end_s": times[-1],
        "Cl_rms": cl_rms,
        "freq_hz": freq_hz,
        "St_peak": st_peak,
        "lowest_bin_peak": best_idx == 1,
    }


def write_nu_csv(case_name: str, nu_series: list[tuple[float, float]]) -> Path:
    out = RUN_DIR / f"{case_name}_Nu_timeseries.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time_s", "Nu"])
        writer.writerows(nu_series)
    return out


def write_force_csv(case_name: str, coeffs: list[tuple[float, float, float]]) -> Path:
    out = RUN_DIR / f"{case_name}_forceCoeffs_timeseries.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time_s", "Cd", "Cl"])
        writer.writerows(coeffs)
    return out


def plot_nu(case_name: str, nu_series: list[tuple[float, float]], nu_lange: float, nu_bharti: float | None) -> Path:
    out = PLOTS_DIR / f"{case_name}_Nu_vs_time.png"
    times = [row[0] for row in nu_series]
    nus = [row[1] for row in nu_series]

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=160)
    ax.plot(times, nus, color="#0b5ed7", lw=1.6, label="CFD Nu(t)")
    ax.axhline(nu_lange, color="#198754", lw=1.2, ls="--", label=f"Lange 1998 = {nu_lange:.4f}")
    if nu_bharti is not None:
        ax.axhline(nu_bharti, color="#dc3545", lw=1.2, ls="--", label=f"Bharti 2007 = {nu_bharti:.4f}")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Nu [-]")
    ax.set_title(f"{case_name}: Nusselt number vs time")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_force(case_name: str, coeffs: list[tuple[float, float, float]]) -> Path:
    out = PLOTS_DIR / f"{case_name}_Cd_Cl_vs_time.png"
    times = [row[0] for row in coeffs]
    cds = [row[1] for row in coeffs]
    cls = [row[2] for row in coeffs]

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=160)
    ax.plot(times, cds, color="#0b5ed7", lw=1.2, label="Cd")
    ax.plot(times, cls, color="#dc3545", lw=1.0, label="Cl")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Coefficient [-]")
    ax.set_title(f"{case_name}: force coefficients vs time")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_spectrum(case_name: str, case: dict, coeffs: list[tuple[float, float, float]]) -> Path | None:
    if len(coeffs) < 20:
        return None

    tail = max(20, len(coeffs) // 2)
    tail_rows = coeffs[-tail:]
    times = [row[0] for row in tail_rows]
    cls = [row[2] for row in tail_rows]
    dt = mean([b - a for a, b in zip(times[:-1], times[1:])])
    if dt is None or dt <= 0.0:
        return None

    cl_mean = mean(cls)
    assert cl_mean is not None
    centered = [value - cl_mean for value in cls]
    spectrum = study._fft(centered)
    n_fft = len(spectrum)
    u_inf = case["Re"] * study.NU / study.D

    freqs: list[float] = []
    sts: list[float] = []
    amps: list[float] = []
    for idx in range(1, n_fft // 2):
        freq_hz = idx / (n_fft * dt)
        freqs.append(freq_hz)
        sts.append(freq_hz * study.D / u_inf)
        amps.append(abs(spectrum[idx]))

    out = PLOTS_DIR / f"{case_name}_Cl_spectrum.png"
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=160)
    ax.plot(sts, amps, color="#6f42c1", lw=1.1)
    ax.set_xlabel("St [-]")
    ax.set_ylabel("|FFT(Cl)| [-]")
    ax.set_title(f"{case_name}: spectrum of Cl tail")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def write_comparison(case: dict, nu_series: list[tuple[float, float]], coeffs: list[tuple[float, float, float]], metrics: dict[str, float | int | bool | None]) -> tuple[Path, Path]:
    case_name = case["name"]
    nu_lange = round(study.nu_lange(case["Re"]), 4)
    nu_bharti = study.BHARTI_NU.get(case["Re"])
    tail_count = max(1, len(nu_series) // 2) if nu_series else 0
    nu_tail = mean([value for _, value in nu_series[-tail_count:]]) if tail_count else None
    nu_last10 = mean([value for t, value in nu_series if t >= nu_series[-1][0] - 10.0]) if nu_series else None
    cd_tail = mean([row[1] for row in coeffs[len(coeffs) // 2 :]])
    cl_rms_tail = metrics.get("Cl_rms")
    st_peak = metrics.get("St_peak")

    err_lange = None if nu_tail is None else 100.0 * (nu_tail - nu_lange) / nu_lange
    err_bharti = None if nu_tail is None or nu_bharti is None else 100.0 * (nu_tail - nu_bharti) / nu_bharti

    md_path = RUN_DIR / f"literature_comparison_{case_name}.md"
    csv_path = RUN_DIR / f"literature_comparison_{case_name}.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "case",
            "Re",
            "time_max_s",
            "Nu_tail_mean",
            "Nu_last10s_mean",
            "Nu_Lange",
            "Nu_Bharti",
            "err_vs_Lange_pct",
            "err_vs_Bharti_pct",
            "Cd_tail_mean",
            "Cl_rms_tail",
            "St_peak_transient",
            "St_note",
        ])
        writer.writerow([
            case_name,
            case["Re"],
            nu_series[-1][0] if nu_series else None,
            round(nu_tail, 4) if nu_tail is not None else None,
            round(nu_last10, 4) if nu_last10 is not None else None,
            nu_lange,
            nu_bharti,
            round(err_lange, 2) if err_lange is not None else None,
            round(err_bharti, 2) if err_bharti is not None else None,
            round(cd_tail, 4) if cd_tail is not None else None,
            round(cl_rms_tail, 6) if isinstance(cl_rms_tail, float) else cl_rms_tail,
            round(st_peak, 4) if isinstance(st_peak, float) else st_peak,
            "No literature St in Lange/Bharti; Re=10 expected steady/no periodic shedding.",
        ])

    lines = [
        f"# {case_name} literature comparison",
        "",
        "## Scope",
        "",
        "- case: `Re10_long100s` stopped run post-processing only",
        "- literature for `Nu`: Lange (1998) and Bharti (2007)",
        "- literature for `St`: not reported in these thermal papers; at `Re = 10` the expected regime is steady, so any spectral peak from `Cl` is treated as transient only",
        "",
        "## Summary table",
        "",
        "| quantity | value |",
        "|---|---:|",
        f"| time covered by `Nu(t)` | {nu_series[-1][0]:.4f} s |" if nu_series else "| time covered by `Nu(t)` | n/a |",
        f"| Nu tail mean (second half) | {nu_tail:.4f} |" if nu_tail is not None else "| Nu tail mean (second half) | n/a |",
        f"| Nu mean over last 10 s | {nu_last10:.4f} |" if nu_last10 is not None else "| Nu mean over last 10 s | n/a |",
        f"| Nu_Lange | {nu_lange:.4f} |",
        f"| Nu_Bharti | {nu_bharti:.4f} |" if nu_bharti is not None else "| Nu_Bharti | n/a |",
        f"| error vs Lange | {err_lange:+.2f}% |" if err_lange is not None else "| error vs Lange | n/a |",
        f"| error vs Bharti | {err_bharti:+.2f}% |" if err_bharti is not None else "| error vs Bharti | n/a |",
        f"| Cd tail mean | {cd_tail:.4f} |" if cd_tail is not None else "| Cd tail mean | n/a |",
        f"| Cl_rms tail | {cl_rms_tail:.6f} |" if isinstance(cl_rms_tail, float) else "| Cl_rms tail | n/a |",
        f"| transient spectral peak St | {st_peak:.4f} |" if isinstance(st_peak, float) else "| transient spectral peak St | n/a |",
        "",
        "## Interpretation",
        "",
    ]

    if nu_tail is not None and nu_bharti is not None:
        lines.append(
            f"- `Nu` remains far above the literature target (`{nu_tail:.4f}` vs `{nu_bharti:.4f}` from Bharti and `{nu_lange:.4f}` from Lange), so this stopped run does not yet reproduce the expected steady thermal solution."
        )
    lines += [
        "- `Nu(t)` therefore acts here as a diagnostic curve, not as a validated benchmark result.",
        "- The extracted spectral `St` is reported only as a transient signal descriptor. It is not physically comparable to literature for `Re = 10`, where periodic shedding is not expected.",
    ]

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export V2a time-series and comparison assets for one case")
    parser.add_argument("case", help="Case name, e.g. Re10_long100s")
    args = parser.parse_args()

    ensure_dirs()
    case = study.get_case(args.case)
    case_dir = study.RUN_ROOT / case["name"]

    nu_series = study.nu_time_series(case_dir)
    coeffs = load_force_coeffs(case_dir)
    metrics = spectral_peak(case, coeffs)

    if nu_series:
        write_nu_csv(case["name"], nu_series)
        plot_nu(case["name"], nu_series, round(study.nu_lange(case["Re"]), 4), study.BHARTI_NU.get(case["Re"]))
    if coeffs:
        write_force_csv(case["name"], coeffs)
        plot_force(case["name"], coeffs)
        plot_spectrum(case["name"], case, coeffs)

    md_path, csv_path = write_comparison(case, nu_series, coeffs, metrics)
    print(f"Wrote comparison: {md_path}")
    print(f"Wrote comparison CSV: {csv_path}")
    if nu_series:
        print(f"Wrote Nu series with {len(nu_series)} samples")
    if coeffs:
        print(f"Wrote force series with {len(coeffs)} samples")
        print(f"Transient St peak: {metrics.get('St_peak')}")


if __name__ == "__main__":
    main()
