from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
FIGURES_DIR = ROOT / "figures"

DATASETS = [
    {
        "path": ROOT / "data" / "velocity_snapshots_5x5.json",
        "prefix": "",
        "cmap": "viridis",
        "colorbar_label": "velocity magnitude [a.u.]",
    },
    {
        "path": ROOT / "data" / "heat_flux_wall_snapshots_5x5.json",
        "prefix": "heat_flux_",
        "cmap": "inferno",
        "colorbar_label": "wall heat flux [a.u.]",
    },
]


def plot_dataset(config: dict[str, str | Path]) -> None:
    with Path(config["path"]).open("r", encoding="utf-8") as fh:
        dataset = json.load(fh)

    snapshots = dataset["snapshots"]
    vmax = max(max(max(row) for row in snap["matrix"]) for snap in snapshots)

    for snap in snapshots:
        matrix = snap["matrix"]
        fig, ax = plt.subplots(figsize=(4.8, 4.4), dpi=180)
        image = ax.imshow(matrix, cmap=str(config["cmap"]), vmin=0.0, vmax=vmax, origin="upper")

        ax.set_title(f"{dataset['field']}: {snap['id']}  |  t={snap['time']}", fontsize=9)
        ax.set_xlabel("x index")
        ax.set_ylabel("y index")
        ax.set_xticks(range(5))
        ax.set_yticks(range(5))

        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                color = "white" if value > 0.55 * vmax else "#111827"
                ax.text(x, y, f"{value:g}", ha="center", va="center", color=color, fontsize=8)

        cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label(str(config["colorbar_label"]))
        fig.tight_layout()

        out = FIGURES_DIR / f"{config['prefix']}{snap['id']}.png"
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)
        print(f"Wrote {out}")


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for config in DATASETS:
        plot_dataset(config)


if __name__ == "__main__":
    main()
