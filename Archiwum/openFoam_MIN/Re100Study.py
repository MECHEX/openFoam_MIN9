from __future__ import annotations

from dataclasses import dataclass, asdict
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
RUN_ROOT = Path(r"C:\openfoam-case\re100Cylinder")
RESULTS_ROOT = REPO_CASE / "results" / "study_re100"
PLOTS_DIR = RESULTS_ROOT / "plots"

D = 0.012
R = D / 2.0
NU = 1.5e-5
U_INF = 0.125
RHO = 1.225
SPAN = 0.01
Z_MIN = -SPAN / 2.0
Z_MAX = SPAN / 2.0
TARGET_ST = 0.165
END_TIME_SWEEP = 8.0
END_TIME_FINAL = 12.0


@dataclass(frozen=True)
class Variant:
    name: str
    upstream_D: float
    downstream_D: float
    half_height_D: float
    base_dx: float


VARIANTS = [
    Variant("v1_u10_d25_h10", 10.0, 25.0, 10.0, 0.0030),
    Variant("v2_u12_d30_h15", 12.0, 30.0, 15.0, 0.0032),
    Variant("v3_u11_d27_h12", 11.0, 27.0, 12.0, 0.0031),
]
VARIANTS_BY_NAME = {variant.name: variant for variant in VARIANTS}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def base_mesh_counts(variant: Variant) -> tuple[int, int]:
    length = (variant.upstream_D + variant.downstream_D) * D
    height = 2.0 * variant.half_height_D * D
    nx = max(80, int(round(length / variant.base_dx)))
    ny = max(60, int(round(height / variant.base_dx)))
    return nx, ny


def domain_dimensions(variant: Variant) -> dict[str, float]:
    xmin = -variant.upstream_D * D
    xmax = variant.downstream_D * D
    ymin = -variant.half_height_D * D
    ymax = variant.half_height_D * D
    return {
        "x_min_m": xmin,
        "x_max_m": xmax,
        "y_min_m": ymin,
        "y_max_m": ymax,
        "length_m": xmax - xmin,
        "height_m": ymax - ymin,
    }


def block_mesh_dict(variant: Variant) -> str:
    xmin = -variant.upstream_D * D
    xmax = variant.downstream_D * D
    ymin = -variant.half_height_D * D
    ymax = variant.half_height_D * D
    nx, ny = base_mesh_counts(variant)
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
    ({xmin:.6f} {ymin:.6f} {Z_MIN:.6f})
    ({xmax:.6f} {ymin:.6f} {Z_MIN:.6f})
    ({xmax:.6f} {ymax:.6f} {Z_MIN:.6f})
    ({xmin:.6f} {ymax:.6f} {Z_MIN:.6f})
    ({xmin:.6f} {ymin:.6f} {Z_MAX:.6f})
    ({xmax:.6f} {ymin:.6f} {Z_MAX:.6f})
    ({xmax:.6f} {ymax:.6f} {Z_MAX:.6f})
    ({xmin:.6f} {ymax:.6f} {Z_MAX:.6f})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1)
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
        type empty;
        faces
        (
            (0 3 2 1)
        );
    }}

    back
    {{
        type empty;
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


def snappy_hex_mesh_dict(variant: Variant) -> str:
    near = 3.0 * D
    wake_xmin = -1.0 * D
    wake_xmax = 18.0 * D
    wake_half_height = 3.0 * D
    xmin = -variant.upstream_D * D
    location = xmin + 0.001

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
    maxLocalCells 250000;
    maxGlobalCells 2000000;
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
        type            empty;
    }

    back
    {
        type            empty;
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
        type            empty;
    }

    back
    {
        type            empty;
    }

    cylinder
    {
        type            zeroGradient;
    }
}
"""


def control_dict(end_time: float) -> str:
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
endTime         {end_time:g};

deltaT          0.001;
adjustTimeStep  yes;
maxCo           0.8;

writeControl    runTime;
writeInterval   0.1;

purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;

timeFormat      general;
timePrecision   8;

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
        Aref            {D*SPAN};
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

readFields      ( U );

expressions
(
    U
    {{
        field       U;
        create      no;
        dimensions  [0 1 -1 0 0 0 0];
        expression
        #{{ vector
            (
                {U_INF}*(1 + 0.02*tanh((pos().y()-0.0015)/0.003)),
                0.0025*exp(-pow((pos().x()-0.018)/0.012,2) - pow((pos().y()-0.003)/0.006,2)),
                0
            )
        #}};
    }}
);
"""


def allrun_file() -> str:
    return """#!/bin/bash
set -euo pipefail

source /home/kik/openfoam/OpenFOAM-v2512/etc/bashrc

cd "$(dirname "$0")"
blockMesh | tee logs/blockMesh.log
snappyHexMesh -overwrite | tee logs/snappyHexMesh.log
checkMesh | tee logs/checkMesh.log
setExprFields | tee logs/setExprFields.log
pimpleFoam | tee logs/pimpleFoam.log
"""


def metadata(variant: Variant) -> dict:
    nx, ny = base_mesh_counts(variant)
    return {
        **asdict(variant),
        **domain_dimensions(variant),
        "diameter_m": D,
        "radius_m": R,
        "u_inf_m_per_s": U_INF,
        "nu_m2_per_s": NU,
        "reynolds": U_INF * D / NU,
        "span_m": SPAN,
        "base_nx": nx,
        "base_ny": ny,
        "target_st": TARGET_ST,
    }


def resolve_variants(case_names: list[str]) -> list[Variant]:
    if not case_names:
        return VARIANTS

    resolved = []
    for name in case_names:
        variant = VARIANTS_BY_NAME.get(name)
        if variant is None:
            valid = ", ".join(VARIANTS_BY_NAME)
            raise SystemExit(f"Unknown case '{name}'. Valid cases: {valid}")
        resolved.append(variant)
    return resolved


def prepare(case_names: list[str], overwrite: bool) -> None:
    ensure_dir(RUN_ROOT)
    ensure_dir(RESULTS_ROOT)

    selected = resolve_variants(case_names)

    for variant in selected:
        case_dir = RUN_ROOT / variant.name
        if case_dir.exists():
            if not overwrite:
                print(f"skip existing {case_dir}")
                continue
            shutil.rmtree(case_dir)

        shutil.copytree(REPO_CASE / "0", case_dir / "0")
        shutil.copytree(REPO_CASE / "constant", case_dir / "constant")
        shutil.copytree(REPO_CASE / "system", case_dir / "system")
        ensure_dir(case_dir / "logs")

        (case_dir / "0" / "U").write_text(u_file(), encoding="ascii")
        (case_dir / "0" / "p").write_text(p_file(), encoding="ascii")
        (case_dir / "system" / "blockMeshDict").write_text(block_mesh_dict(variant), encoding="ascii")
        (case_dir / "system" / "snappyHexMeshDict").write_text(snappy_hex_mesh_dict(variant), encoding="ascii")
        (case_dir / "system" / "controlDict").write_text(control_dict(END_TIME_SWEEP), encoding="ascii")
        (case_dir / "system" / "setExprFieldsDict").write_text(set_expr_fields_dict(), encoding="ascii")
        (case_dir / "Allrun").write_text(allrun_file(), encoding="ascii", newline="\n")
        (case_dir / "studyMeta.json").write_text(json.dumps(metadata(variant), indent=2), encoding="utf-8")

    manifest = {
        "run_root": str(RUN_ROOT),
        "results_root": str(RESULTS_ROOT),
        "variants": [asdict(v) for v in VARIANTS],
    }
    (RESULTS_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(RUN_ROOT)


def parse_cells(check_mesh_log: Path) -> int | None:
    if not check_mesh_log.exists():
        return None
    match = re.search(r"cells:\s+(\d+)", check_mesh_log.read_text(encoding="utf-8", errors="ignore"))
    return int(match.group(1)) if match else None


def coeff_paths(case_dir: Path) -> list[Path]:
    root = case_dir / "postProcessing" / "forceCoeffs"
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

    # Peak-based estimate
    maxima = np.where((centered[1:-1] > centered[:-2]) & (centered[1:-1] >= centered[2:]))[0] + 1
    amp_threshold = 0.25 * np.max(np.abs(centered))
    maxima = maxima[centered[maxima] > amp_threshold]
    peak_freq = None
    if maxima.size >= 3:
        peak_periods = np.diff(time[maxima])
        peak_freq = float(1.0 / np.mean(peak_periods))

    # FFT estimate
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

    frequency = fft_freq
    method = "fft"

    st = frequency * D / U_INF

    return {
        "analysis_start_s": analysis_start,
        "samples_used": int(time.size),
        "time_min_s": float(time.min()),
        "time_max_s": float(time.max()),
        "mean_dt_s": dt,
        "frequency_peak_hz": peak_freq,
        "frequency_fft_hz": fft_freq,
        "frequency_selected_hz": frequency,
        "selection_method": method,
        "strouhal_number": float(st),
        "st_error_pct": float(100.0 * abs(st - TARGET_ST) / TARGET_ST),
    }


def plot_case(case_name: str, time: np.ndarray, cl: np.ndarray) -> None:
    ensure_dir(PLOTS_DIR)
    plt.figure(figsize=(10, 5), dpi=160)
    plt.plot(time, cl, linewidth=1.1)
    plt.xlabel("Time [s]")
    plt.ylabel("Cl [-]")
    plt.title(f"{case_name}: Cl(t)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"{case_name}_Cl.png")
    plt.close()


def analyze() -> None:
    ensure_dir(RESULTS_ROOT)
    ensure_dir(PLOTS_DIR)

    rows = []
    overlay = []

    for variant in VARIANTS:
        case_dir = RUN_ROOT / variant.name
        force_coeff_paths = coeff_paths(case_dir)
        meta_path = case_dir / "studyMeta.json"
        meta = metadata(variant)
        if meta_path.exists():
            meta.update(json.loads(meta_path.read_text(encoding="utf-8")))

        row = {
            "case": variant.name,
            "upstream_D": variant.upstream_D,
            "downstream_D": variant.downstream_D,
            "half_height_D": variant.half_height_D,
            "length_m": meta["length_m"],
            "height_m": meta["height_m"],
            "base_nx": meta["base_nx"],
            "base_ny": meta["base_ny"],
            "Re": meta["reynolds"],
            "cells": parse_cells(case_dir / "logs" / "checkMesh.log"),
            "status": "missing",
        }

        if force_coeff_paths:
            time, cl = load_cl(force_coeff_paths)
            if time.size:
                metrics = estimate_st(time, cl)
                row.update(
                    {
                        "status": "ok",
                        "time_max_s": float(time.max()),
                        "frequency_hz": metrics["frequency_selected_hz"],
                        "frequency_peak_hz": metrics["frequency_peak_hz"],
                        "frequency_fft_hz": metrics["frequency_fft_hz"],
                        "selection_method": metrics["selection_method"],
                        "St": metrics["strouhal_number"],
                        "St_error_pct": metrics["st_error_pct"],
                    }
                )
                overlay.append((variant.name, time, cl))
                plot_case(variant.name, time, cl)
        rows.append(row)

    csv_path = RESULTS_ROOT / "summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_path = RESULTS_ROOT / "summary.md"
    with md_path.open("w", encoding="utf-8") as handle:
        handle.write("| case | up_D | down_D | halfHeight_D | Lx [m] | Ly [m] | base_nx | base_ny | cells | Re | f [Hz] | St | err [%] | status |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|\n")
        for row in rows:
            handle.write(
                f"| {row['case']} | {row['upstream_D']} | {row['downstream_D']} | {row['half_height_D']} | "
                f"{row['length_m']:.3f} | {row['height_m']:.3f} | {row['base_nx']} | {row['base_ny']} | {row.get('cells', '')} | {row['Re']:.1f} | "
                f"{row.get('frequency_hz', '')} | {row.get('St', '')} | {row.get('St_error_pct', '')} | {row['status']} |\n"
            )

    if overlay:
        plt.figure(figsize=(11, 6), dpi=160)
        for name, time, cl in overlay:
            plt.plot(time, cl, linewidth=1.0, label=name)
        plt.xlabel("Time [s]")
        plt.ylabel("Cl [-]")
        plt.title("Cl(t) comparison across Re=100 cylinder variants")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / "Cl_overlay.png")
        plt.close()

        ok_rows = [row for row in rows if row["status"] == "ok"]
        if ok_rows:
            plt.figure(figsize=(8, 5), dpi=160)
            names = [row["case"] for row in ok_rows]
            st_values = [row["St"] for row in ok_rows]
            plt.plot(names, st_values, marker="o", linewidth=1.2)
            plt.axhline(TARGET_ST, color="crimson", linestyle="--", label="literature target")
            plt.ylabel("St [-]")
            plt.title("Strouhal comparison by geometry variant")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.savefig(PLOTS_DIR / "St_by_variant.png")
            plt.close()

    print(csv_path)
    print(md_path)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "analyze"])
    parser.add_argument("cases", nargs="*")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.command == "prepare":
        prepare(args.cases, args.overwrite)
    elif args.command == "analyze":
        analyze()


if __name__ == "__main__":
    main()
