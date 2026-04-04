from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


CASE_DIR = Path(__file__).resolve().parent
COEFF_FILE = CASE_DIR / "results" / "postProcessing" / "forceCoeffs" / "0" / "coefficient.dat"
PLOTS_DIR = CASE_DIR / "results" / "plots"
OUT_FILE = PLOTS_DIR / "Cl_vs_time.png"


def load_cl_data(path: Path) -> tuple[list[float], list[float]]:
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

    return time, cl


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    time, cl = load_cl_data(COEFF_FILE)
    if not time:
        raise RuntimeError(f"No Cl data found in {COEFF_FILE}")

    plt.figure(figsize=(10, 5), dpi=160)
    plt.plot(time, cl, color="#0b5ed7", linewidth=1.2)
    plt.xlabel("Time [s]")
    plt.ylabel("Cl [-]")
    plt.title("Lift Coefficient vs Time")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_FILE)

    print(OUT_FILE)
    print(f"points={len(time)}")
    print(f"time_range=({min(time):.6f}, {max(time):.6f})")
    print(f"cl_range=({min(cl):.6f}, {max(cl):.6f})")


if __name__ == "__main__":
    main()
