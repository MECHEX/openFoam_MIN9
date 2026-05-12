#!/usr/bin/env pvpython
"""Render first-pass Q and Lambda2 iso-surfaces for run008 layer 014.

Run with:

    pvpython --force-offscreen-rendering render_run008_q_lambda2_isosurfaces_014.py

This script reads the decomposed VTK files exported by layer 013.  It writes
only PNG screenshots and small metadata files to the repository.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from paraview.simple import *  # type: ignore


RUN_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/results/run008")
DATA_DIR = RUN_DIR / "data" / "014"
FIG_DIR = RUN_DIR / "figures" / "014"
VTK_ROOT = Path("/home/hexmachina/of_runs/V4b_3D_run008_q_lambda2_013/vtk_processors")

Q_ISO = 3000.0
LAMBDA2_ISO = -1000.0


def read_selected() -> list[dict[str, str]]:
    path = RUN_DIR / "data" / "013" / "run008_013_selected_q_lambda2_times.csv"
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def internal_files(time_s: str) -> list[str]:
    files = sorted(str(p) for p in VTK_ROOT.glob(f"processor*/VTK/processor*_{time_s}.vtk"))
    if len(files) != 20:
        raise RuntimeError(f"Expected 20 processor VTK files for t={time_s}, found {len(files)}")
    return files


def setup_view(title: str):
    view = CreateView("RenderView")
    view.ViewSize = [1600, 1000]
    view.Background = [1.0, 1.0, 1.0]
    view.OrientationAxesVisibility = 1
    view.CenterOfRotation = [0.04, 0.0, 0.0]
    return view


def render_time(row: dict[str, str]) -> dict[str, object]:
    label = row["label"]
    time_s = f"{float(row['selected_time_s']):g}"
    phase = float(row["selected_phase_deg"])
    files = internal_files(time_s)

    reader = LegacyVTKReader(FileNames=files)
    append = AppendDatasets(Input=reader)
    c2p = CellDatatoPointData(Input=append)
    c2p.PassCellData = 1

    q_contour = Contour(Input=c2p)
    q_contour.ContourBy = ["POINTS", "Q"]
    q_contour.Isosurfaces = [Q_ISO]

    l2_contour = Contour(Input=c2p)
    l2_contour.ContourBy = ["POINTS", "Lambda2"]
    l2_contour.Isosurfaces = [LAMBDA2_ISO]

    # Add hot patches as geometric context.  They are small and useful for
    # orienting the tube-fin junction in screenshots.
    tube_files = sorted(str(p) for p in VTK_ROOT.glob(f"processor*/VTK/hot_tube/hot_tube_{time_s}.vtk"))
    fin_min_files = sorted(str(p) for p in VTK_ROOT.glob(f"processor*/VTK/hot_fin_z_min/hot_fin_z_min_{time_s}.vtk"))
    fin_max_files = sorted(str(p) for p in VTK_ROOT.glob(f"processor*/VTK/hot_fin_z_max/hot_fin_z_max_{time_s}.vtk"))
    tube = LegacyVTKReader(FileNames=tube_files) if tube_files else None
    fin_min = LegacyVTKReader(FileNames=fin_min_files) if fin_min_files else None
    fin_max = LegacyVTKReader(FileNames=fin_max_files) if fin_max_files else None

    view = setup_view(label)
    q_disp = Show(q_contour, view)
    q_disp.Representation = "Surface"
    q_disp.ColorArrayName = [None, ""]
    q_disp.DiffuseColor = [0.95, 0.38, 0.08]
    q_disp.Opacity = 0.88

    l2_disp = Show(l2_contour, view)
    l2_disp.Representation = "Surface"
    l2_disp.DiffuseColor = [0.05, 0.22, 0.75]
    l2_disp.Opacity = 0.38

    for patch, color in [(tube, [0.85, 0.1, 0.1]), (fin_min, [0.8, 0.8, 0.8]), (fin_max, [0.8, 0.8, 0.8])]:
        if patch is None:
            continue
        disp = Show(patch, view)
        disp.Representation = "Surface"
        disp.DiffuseColor = color
        disp.Opacity = 0.35

    # Oblique top/front view: x streamwise, y transverse, z fin pitch.
    view.CameraPosition = [0.084, -0.060, 0.036]
    view.CameraFocalPoint = [0.040, 0.0, 0.004]
    view.CameraViewUp = [0.0, 0.0, 1.0]
    view.CameraParallelProjection = 1
    view.CameraParallelScale = 0.024
    Render(view)

    text = Text()
    text.Text = f"{label} | t={time_s}s | phase={phase:.1f} deg | orange: Q={Q_ISO:g}, blue: Lambda2={LAMBDA2_ISO:g}"
    text_disp = Show(text, view)
    text_disp.WindowLocation = "Upper Center"
    text_disp.FontSize = 18
    text_disp.Color = [0.05, 0.05, 0.05]
    Render(view)

    out = FIG_DIR / f"run008_014_iso_Q_Lambda2_{label}.png"
    SaveScreenshot(str(out), view, ImageResolution=[1600, 1000])

    Delete(text)
    Delete(view)
    Delete(reader)

    return {
        "label": label,
        "time_s": float(time_s),
        "phase_deg": phase,
        "q_iso": Q_ISO,
        "lambda2_iso": LAMBDA2_ISO,
        "screenshot": str(out.relative_to(RUN_DIR)),
        "processor_vtk_files": len(files),
        "tube_patch_files": len(tube_files),
        "fin_patch_files": len(fin_min_files) + len(fin_max_files),
    }


def write_report(rows: list[dict[str, object]]) -> None:
    lines = [
        "# V4b_3D run008 Q/Lambda2 iso-surface render pass",
        "",
        "## Method",
        "",
        f"- input VTK root: `{VTK_ROOT}`",
        f"- Q iso-surface: `Q = {Q_ISO:g}`",
        f"- Lambda2 iso-surface: `Lambda2 = {LAMBDA2_ISO:g}`",
        "- Q surfaces are rendered in orange.",
        "- Lambda2 surfaces are overlaid in blue as a companion vortex-core check.",
        "- hot tube and fin patches are shown as translucent context geometry.",
        "",
        "## Screenshots",
        "",
        "| label | time [s] | phase [deg] | screenshot |",
        "|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['label']}` | {float(row['time_s']):.3f} | "
            f"{float(row['phase_deg']):.2f} | `{row['screenshot']}` |"
        )
    lines += [
        "",
        "## Reading",
        "",
        "This is a visual structure-identification layer.  It should be read together",
        "with layer `013`, which records the selected phases and first-pass global",
        "cell-count metrics. The next useful quantitative step is to restrict the",
        "Q/Lambda2 measures to near-wake and tube-fin-junction regions.",
        "",
    ]
    (DATA_DIR / "run008_014_q_lambda2_isosurface_render.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    rows = [render_time(row) for row in read_selected()]
    with (DATA_DIR / "run008_014_q_lambda2_isosurface_render.json").open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)
    with (DATA_DIR / "run008_014_q_lambda2_isosurface_render.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    write_report(rows)


if __name__ == "__main__":
    main()
