from pathlib import Path
import json

import numpy as np


CASE_DIR = Path(__file__).resolve().parent
COEFF_FILE = CASE_DIR / "results" / "postProcessing" / "forceCoeffs" / "0" / "coefficient.dat"
ANALYSIS_DIR = CASE_DIR / "results" / "analysis"
OUT_FILE = ANALYSIS_DIR / "st_estimate.json"

D = 0.012
U_INF = 0.125
T_START = 1.0


def load_cl_data(path: Path) -> tuple[np.ndarray, np.ndarray]:
    time = []
    cl = []

    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            parts = stripped.split()
            if len(parts) < 5:
                continue

            time.append(float(parts[0]))
            cl.append(float(parts[4]))

    return np.asarray(time), np.asarray(cl)


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    time, cl = load_cl_data(COEFF_FILE)
    mask = time >= T_START
    time = time[mask]
    cl = cl[mask]

    if time.size < 16:
        raise RuntimeError("Not enough Cl samples after transient removal to estimate Strouhal number")

    dt = np.mean(np.diff(time))
    cl_centered = cl - np.mean(cl)

    freqs = np.fft.rfftfreq(cl_centered.size, d=dt)
    amps = np.abs(np.fft.rfft(cl_centered))

    positive = freqs > 0
    freqs = freqs[positive]
    amps = amps[positive]

    peak_idx = int(np.argmax(amps))
    shedding_freq = float(freqs[peak_idx])
    st = shedding_freq * D / U_INF

    result = {
        "input": {
            "diameter_m": D,
            "u_inf_m_per_s": U_INF,
            "analysis_time_start_s": T_START,
        },
        "signal": {
            "samples_used": int(time.size),
            "time_min_s": float(time.min()),
            "time_max_s": float(time.max()),
            "mean_dt_s": float(dt),
        },
        "result": {
            "shedding_frequency_hz": shedding_freq,
            "strouhal_number": float(st),
        },
    }

    OUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(OUT_FILE)
    print(f"f={shedding_freq:.6f} Hz")
    print(f"St={st:.6f}")


if __name__ == "__main__":
    main()
