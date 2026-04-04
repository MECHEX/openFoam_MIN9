from __future__ import annotations

from pathlib import Path
import csv
import json
import math
import re
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO_CASE = Path(__file__).resolve().parent
RUN_ROOT = Path(r"C:\openfoam-case\re100Cylinder3D")
CASE_NAME = "min3d_u12_d30_h15_z0p5D_nz2"
RESULTS_ROOT = REPO_CASE / "results" / "study_re100_3d_min"
PLOTS_DIR = RESULTS_ROOT / "plots"

D = 0.012
R = D / 2.0
NU = 1.5e-5
U_INF = 0.125
RHO = 1.225
TARGET_ST = 0.165
END_TIME = 8.0

UPSTREAM_D = 12.0
DOWNSTREAM_D = 30.0
HALF_HEIGHT_D = 15.0
BASE_DX = 0.0032
SPAN_D = 0.5
NZ = 2

Z_MIN = -0.5 * SPAN_D * D
Z_MAX = 0.5 * SPAN_D * D


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def case_dir() -> Path:
    return RUN_ROOT / CASE_NAME


def base_mesh_counts() -> tuple[int, int]:
    length = (UPSTREAM_D + DOWNSTREAM_D) * D
    height = 2.0 * HALF_HEIGHT_D * D
    nx = max(80, int(round(length / BASE_DX)))
    ny = max(60, int(round(height / BASE_DX)))
    return nx, ny


def dimensions() -> dict[str, float]:
    xmin = -UPSTREAM_D * D
    xmax = DOWNSTREAM_D * D
    ymin = -HALF_HEIGHT_D * D
    ymax = HALF_HEIGHT_D * D
    return {
        "x_min_m": xmin,
        "x_max_m": xmax,
        "y_min_m": ymin,
        "y_max_m": ymax,
        "z_min_m": Z_MIN,
        "z_max_m": Z_MAX,
        "length_m": xmax - xmin,
        "height_m": ymax - ymin,
        "span_m": Z_MAX - Z_MIN,
    }


def block_mesh_dict() -> str:
    dims = dimensions()
    nx, ny = base_mesh_counts()
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

scale 1;

vertices
(
    ({dims['x_min_m']:.6f} {dims['y_min_m']:.6f} {Z_MIN:.6f})
    ({dims['x_max_m']:.6f} {dims['y_min_m']:.6f} {Z_MIN:.6f})
    ({dims['x_max_m']:.6f} {dims['y_max_m']:.6f} {Z_MIN:.6f})
    ({dims['x_min_m']:.6f} {dims['y_max_m']:.6f} {Z_MIN:.6f})
    ({dims['x_min_m']:.6f} {dims['y_min_m']:.6f} {Z_MAX:.6f})
    ({dims['x_max_m']:.6f} {dims['y_min_m']:.6f} {Z_MAX:.6f})
    ({dims['x_max_m']:.6f} {dims['y_max_m']:.6f} {Z_MAX:.6f})
    ({dims['x_min_m']:.6f} {dims['y_max_m']:.6f} {Z_MAX:.6f})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} {NZ}) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    inlet
    {{
        type patch;
        faces
        (
            (0 4 7 3)
        );
    }}

    outlet
    {{
        type patch;
        faces
        (
            (1 2 6 5)
        );
    }}

    bottom
    {{
        type symmetryPlane;
        faces
        (
            (0 1 5 4)
        );
    }}

    top
    {{
        type symmetryPlane;
        faces
        (
            (3 7 6 2)
        );
    }}

    front
    {{
        type cyclic;
        neighbourPatch back;
        faces
        (
            (0 3 2 1)
        );
    }}

    back
    {{
        type cyclic;
        neighbourPatch front;
        faces
        (
            (4 5 6 7)
        );
    }}
);

mergePatchPairs
(
);
"""


def snappy_hex_mesh_dict() -> str:
    near = 3.0 * D
    wake_xmin = -1.0 * D
    wake_xmax = 18.0 * D
    wake_half_height = 3.0 * D
    location = dimensions()["x_min_m"] + 0.001

    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}

castellatedMesh true;
snap            true;
addLayers       false;

geometry
{{
    cylinder
    {{
        type searchableCylinder;
        point1 (0 0 {Z_MIN:.6f});
        point2 (0 0 {Z_MAX:.6f});
        radius {R:.6f};
    }}

    nearCylinder
    {{
        type searchableBox;
        min ({-near:.6f} {-near:.6f} {Z_MIN:.6f});
        max ({near:.6f} {near:.6f} {Z_MAX:.6f});
    }}

    wakeBox
    {{
        type searchableBox;
        min ({wake_xmin:.6f} {-wake_half_height:.6f} {Z_MIN:.6f});
        max ({wake_xmax:.6f} {wake_half_height:.6f} {Z_MAX:.6f});
    }}
}}

castellatedMeshControls
{{
    maxLocalCells 400000;
    maxGlobalCells 2500000;
    minRefinementCells 0;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;
    resolveFeatureAngle 30;

    features
    (
    );

    refinementSurfaces
    {{
        cylinder
        {{
            level (3 3);
            patchInfo
            {{
                type wall;
            }}
        }}
    }}

    refinementRegions
    {{
        nearCylinder
        {{
            mode inside;
            levels ((1E15 2));
        }}

        wakeBox
        {{
            mode inside;
            levels ((1E15 1));
        }}
    }}

    locationInMesh ({location:.6f} 0 0);
    allowFreeStandingZoneFaces true;
}}

snapControls
{{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 100;
    nRelaxIter 5;
    nFeatureSnapIter 10;
    implicitFeatureSnap false;
    explicitFeatureSnap false;
    multiRegionFeatureSnap false;
}}

addLayersControls
{{
    relativeSizes true;
    layers
    {{
    }}
    expansionRatio 1.0;
    finalLayerThickness 0.0;
    minThickness 0.0;
    nGrow 0;
    featureAngle 180;
    nRelaxIter 3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedianAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 0;
}}

meshQualityControls
{{
    #include "meshQualityDict"

    relaxed
    {{
        maxNonOrtho 75;
    }}
}}

writeFlags
(
    scalarLevels
    layerSets
    layerFields
);

mergeTolerance 1e-6;
"""


def u_file() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0.125 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (0.125 0 0);
    }

    outlet
    {
        type            inletOutlet;
        inletValue      uniform (0.125 0 0);
        value           uniform (0.125 0 0);
    }

    top
    {
        type            symmetryPlane;
    }

    bottom
    {
        type            symmetryPlane;
    }

    front
    {
        type            cyclic;
    }

    back
    {
        type            cyclic;
    }

    cylinder
    {
        type            noSlip;
    }
}
"""


def p_file() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      p;
}

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            zeroGradient;
    }

    outlet
    {
        type            fixedValue;
        value           uniform 0;
    }

    top
    {
        type            symmetryPlane;
    }

    bottom
    {
        type            symmetryPlane;
    }

    front
    {
        type            cyclic;
    }

    back
    {
        type            cyclic;
    }

    cylinder
    {
        type            zeroGradient;
    }
}
"""


def control_dict() -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}}

application     pimpleFoam;

startFrom       startTime;
startTime       0;

stopAt          endTime;
endTime         {END_TIME};

deltaT          0.001;
adjustTimeStep  yes;
maxCo           0.8;

writeControl    runTime;
writeInterval   0.1;

purgeWrite      0;
writeFormat     ascii;
writePrecision  12;
writeCompression off;

timeFormat      general;
timePrecision   12;

runTimeModifiable true;

functions
{{
    forceCoeffs
    {{
        type            forceCoeffs;
        libs            (forces);
        executeControl  timeStep;
        executeInterval 1;
        writeControl    timeStep;
        writeInterval   1;
        log             yes;
        patches         (cylinder);
        rho             rhoInf;
        rhoInf          {RHO};
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         {U_INF};
        lRef            {D};
        Aref            {D * (Z_MAX - Z_MIN)};
    }}

    residuals
    {{
        type            solverInfo;
        libs            (utilityFunctionObjects);
        fields          (U p);
        executeControl  timeStep;
        executeInterval 1;
        writeControl    timeStep;
        writeInterval   1;
    }}
}}
"""


def set_expr_fields_dict() -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      setExprFieldsDict;
}}

expressions
(
    U
    {{
        field U;
        expression
        #{{ vector
            (
                {U_INF}*(1 + 0.02*tanh((pos().y()-0.0015)/0.003)),
                0.0025*exp(-pow((pos().x()-0.018)/0.012, 2) - pow((pos().y()-0.003)/0.006, 2)),
                0.0004*tanh(pos().z()/0.0008)*exp(-pow((pos().x()-0.018)/0.012, 2) - pow(pos().y()/0.010, 2))
            )
        #}};
    }}
);
"""


def allrun_file() -> str:
    return """#!/bin/bash
source /home/kik/openfoam/OpenFOAM-v2512/etc/bashrc
set -eo pipefail

cd "$(dirname "$0")"
blockMesh | tee logs/blockMesh.log
snappyHexMesh -overwrite | tee logs/snappyHexMesh.log
checkMesh | tee logs/checkMesh.log
setExprFields | tee logs/setExprFields.log
pimpleFoam | tee logs/pimpleFoam.log
"""


def metadata() -> dict:
    nx, ny = base_mesh_counts()
    return {
        "case": CASE_NAME,
        **dimensions(),
        "diameter_m": D,
        "u_inf_m_per_s": U_INF,
        "nu_m2_per_s": NU,
        "reynolds": U_INF * D / NU,
        "target_st": TARGET_ST,
        "base_nx": nx,
        "base_ny": ny,
        "base_nz": NZ,
        "span_D": SPAN_D,
        "span_cells": NZ,
        "span_bc": "cyclic",
        "top_bottom_bc": "symmetryPlane",
        "outlet_bc": "inletOutlet(U) + fixedValue(p)",
        "inlet_bc": "fixedValue(U) + zeroGradient(p)",
        "startup_perturbation": "setExprFields asymmetric Uy bump + small antisymmetric Uz",
    }


def write_case_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="ascii")


def prepare(overwrite: bool) -> None:
    ensure_dir(RUN_ROOT)
    ensure_dir(RESULTS_ROOT)
    ensure_dir(PLOTS_DIR)

    out = case_dir()
    if out.exists():
        if not overwrite:
            print(f"skip existing {out}")
            return
        shutil.rmtree(out)

    shutil.copytree(REPO_CASE / "0", out / "0")
    shutil.copytree(REPO_CASE / "constant", out / "constant")
    shutil.copytree(REPO_CASE / "system", out / "system")
    ensure_dir(out / "logs")

    write_case_file(out / "0" / "U", u_file())
    write_case_file(out / "0" / "p", p_file())
    write_case_file(out / "system" / "blockMeshDict", block_mesh_dict())
    write_case_file(out / "system" / "snappyHexMeshDict", snappy_hex_mesh_dict())
    write_case_file(out / "system" / "controlDict", control_dict())
    write_case_file(out / "system" / "setExprFieldsDict", set_expr_fields_dict())
    (out / "Allrun").write_text(allrun_file(), encoding="ascii", newline="\n")
    (out / "studyMeta.json").write_text(json.dumps(metadata(), indent=2), encoding="utf-8")

    manifest = {
        "case_dir": str(out),
        "results_root": str(RESULTS_ROOT),
        "metadata": metadata(),
    }
    (RESULTS_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(out)


def parse_cells(check_mesh_log: Path) -> int | None:
    if not check_mesh_log.exists():
        return None
    match = re.search(r"cells:\s+(\d+)", check_mesh_log.read_text(encoding="utf-8", errors="ignore"))
    return int(match.group(1)) if match else None


def coeff_paths() -> list[Path]:
    root = case_dir() / "postProcessing" / "forceCoeffs"
    if not root.exists():
        return []

    candidates = []
    for child in root.iterdir():
        coeff_path = child / "coefficient.dat"
        if not child.is_dir() or not coeff_path.exists():
            continue
        try:
            start_time = float(child.name)
        except ValueError:
            start_time = math.inf
        candidates.append((start_time, coeff_path))
    return [path for _, path in sorted(candidates, key=lambda item: item[0])]


def load_cl(paths: list[Path]) -> tuple[np.ndarray, np.ndarray]:
    merged: dict[float, float] = {}
    for coeff_path in paths:
        with coeff_path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                parts = stripped.split()
                if len(parts) < 5:
                    continue
                merged[float(parts[0])] = float(parts[4])

    ordered = sorted(merged.items())
    time = np.asarray([item[0] for item in ordered], dtype=float)
    cl = np.asarray([item[1] for item in ordered], dtype=float)
    return time, cl


def estimate_st(time: np.ndarray, cl: np.ndarray) -> dict:
    if time.size < 32:
        raise RuntimeError("Not enough Cl samples")

    analysis_start = max(2.0, float(time.max()) - 4.0)
    mask = time >= analysis_start
    time = time[mask]
    cl = cl[mask]
    if time.size < 32:
        raise RuntimeError("Not enough Cl samples after transient cut")

    centered = cl - np.mean(cl)
    dt = float(np.mean(np.diff(time)))

    maxima = np.where((centered[1:-1] > centered[:-2]) & (centered[1:-1] >= centered[2:]))[0] + 1
    amp_threshold = 0.25 * np.max(np.abs(centered))
    maxima = maxima[centered[maxima] > amp_threshold]
    peak_freq = None
    if maxima.size >= 3:
        peak_freq = float(1.0 / np.mean(np.diff(time[maxima])))

    window = np.hanning(centered.size)
    nfft = 1
    while nfft < centered.size * 8:
        nfft *= 2
    amps = np.abs(np.fft.rfft(centered * window, n=nfft))
    freqs = np.fft.rfftfreq(nfft, d=dt)
    valid = (freqs >= 0.5) & (freqs <= 4.0)
    freqs = freqs[valid]
    amps = amps[valid]
    peak_idx = int(np.argmax(amps))
    fft_freq = float(freqs[peak_idx])
    if 0 < peak_idx < freqs.size - 1:
        alpha = amps[peak_idx - 1]
        beta = amps[peak_idx]
        gamma = amps[peak_idx + 1]
        denom = alpha - 2.0 * beta + gamma
        if abs(denom) > 1e-12:
            shift = 0.5 * (alpha - gamma) / denom
            fft_freq += float(shift * (freqs[1] - freqs[0]))

    st = fft_freq * D / U_INF
    return {
        "analysis_start_s": analysis_start,
        "time_max_s": float(time.max()),
        "frequency_hz": fft_freq,
        "frequency_peak_hz": peak_freq,
        "frequency_fft_hz": fft_freq,
        "selection_method": "fft",
        "St": float(st),
        "St_error_pct": float(100.0 * abs(st - TARGET_ST) / TARGET_ST),
    }


def analyze() -> None:
    ensure_dir(RESULTS_ROOT)
    ensure_dir(PLOTS_DIR)

    meta_path = case_dir() / "studyMeta.json"
    meta = metadata()
    if meta_path.exists():
        meta.update(json.loads(meta_path.read_text(encoding="utf-8")))

    row = {
        "case": CASE_NAME,
        "length_m": meta["length_m"],
        "height_m": meta["height_m"],
        "span_m": meta["span_m"],
        "base_nx": meta["base_nx"],
        "base_ny": meta["base_ny"],
        "base_nz": meta["base_nz"],
        "cells": parse_cells(case_dir() / "logs" / "checkMesh.log"),
        "Re": meta["reynolds"],
        "span_bc": meta["span_bc"],
        "startup_perturbation": meta["startup_perturbation"],
        "status": "missing",
    }

    paths = coeff_paths()
    if paths:
        time, cl = load_cl(paths)
        if time.size:
            metrics = estimate_st(time, cl)
            row.update(metrics)
            row["status"] = "ok"

            plt.figure(figsize=(10, 5), dpi=160)
            plt.plot(time, cl, linewidth=1.1)
            plt.xlabel("Time [s]")
            plt.ylabel("Cl [-]")
            plt.title(f"{CASE_NAME}: Cl(t)")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(PLOTS_DIR / "Cl_vs_time.png")
            plt.close()

    csv_path = RESULTS_ROOT / "summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)

    md_path = RESULTS_ROOT / "summary.md"
    with md_path.open("w", encoding="utf-8") as handle:
        handle.write("| case | Lx [m] | Ly [m] | Lz [m] | nx | ny | nz | cells | Re | f [Hz] | St | err [%] | span BC | status |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|\n")
        handle.write(
            f"| {row['case']} | {row['length_m']:.3f} | {row['height_m']:.3f} | {row['span_m']:.3f} | "
            f"{row['base_nx']} | {row['base_ny']} | {row['base_nz']} | {row.get('cells', '')} | "
            f"{row['Re']:.1f} | {row.get('frequency_hz', '')} | {row.get('St', '')} | "
            f"{row.get('St_error_pct', '')} | {row['span_bc']} | {row['status']} |\n"
        )
        handle.write("\n")
        handle.write(f"Startup perturbation: `{row['startup_perturbation']}`\n")

    print(csv_path)
    print(md_path)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "analyze"])
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.command == "prepare":
        prepare(args.overwrite)
    else:
        analyze()


if __name__ == "__main__":
    main()
