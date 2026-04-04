from __future__ import annotations

from dataclasses import dataclass
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
RUN_ROOT = Path(r"C:\openfoam-case\VV_cases\V1_solver")
RESULTS_ROOT = REPO_CASE / "results" / "study_v1"
RUNS_RESULTS_ROOT = RESULTS_ROOT / "runs"
STUDY_SUMMARY_DIR = RESULTS_ROOT / "study_summary"
STUDY_PLOTS_DIR = STUDY_SUMMARY_DIR / "plots"
PUBLICATION_DIR = RESULTS_ROOT / "publication"
ACTIVE_RUN_NAME = "001_data_beta05_initial_verification"
ACTIVE_RUN_DIR = RUNS_RESULTS_ROOT / ACTIVE_RUN_NAME
ACTIVE_RUN_NOTES_DIR = ACTIVE_RUN_DIR / "00_notes"
ACTIVE_RUN_SETUP_DIR = ACTIVE_RUN_DIR / "01_run_setup"
ACTIVE_RUN_SIMS_DIR = ACTIVE_RUN_DIR / "02_simulations"
ACTIVE_RUN_SUMMARY_DIR = ACTIVE_RUN_DIR / "03_run_summary"
ACTIVE_RUN_PUBLICATION_DIR = ACTIVE_RUN_DIR / "04_publication_candidates"
ACTIVE_RUN_LOGS_DIR = ACTIVE_RUN_DIR / "05_run_logs"

D = 0.012
NU = 1.516e-5
RHO = 1.205
BETA = 0.5
H = D / BETA
HALF_H = H / 2.0
SPAN = 0.01
Z_MIN = -SPAN / 2.0
Z_MAX = SPAN / 2.0

BASE_UP_D = 8.0
BASE_DOWN_D = 20.0
LONG_UP_D = 10.0
LONG_DOWN_D = 30.0

LITERATURE_PRIMARY = "Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285"
LITERATURE_SUPPORT = "Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084"


@dataclass(frozen=True)
class MeshVariant:
    name: str
    base_dx: float
    surface_level: int
    near_level: int
    wake_level: int
    cylinder_layers: int
    wall_layers: int
    final_layer_thickness: float
    expansion_ratio: float


@dataclass(frozen=True)
class StudyCase:
    name: str
    purpose: str
    reynolds: float
    upstream_D: float
    downstream_D: float
    mesh: MeshVariant
    end_time_s: float


MESHES = {
    "coarse": MeshVariant("coarse", 0.0030, 2, 1, 1, 4, 1, 0.20, 1.25),
    "medium": MeshVariant("medium", 0.0025, 3, 2, 1, 6, 2, 0.25, 1.20),
    "target100k": MeshVariant("target100k", 0.0022, 4, 2, 2, 6, 2, 0.25, 1.20),
    "fine": MeshVariant("fine", 0.0020, 4, 3, 2, 8, 4, 0.30, 1.20),
}


CASES = [
    StudyCase("baseline_coarse_Re160", "mesh-study", 160.0, BASE_UP_D, BASE_DOWN_D, MESHES["coarse"], 3.0),
    StudyCase("baseline_medium_Re100", "transition-sweep", 100.0, BASE_UP_D, BASE_DOWN_D, MESHES["medium"], 2.0),
    StudyCase("baseline_medium_Re120", "transition-sweep", 120.0, BASE_UP_D, BASE_DOWN_D, MESHES["medium"], 2.0),
    StudyCase("baseline_medium_Re140", "transition-sweep", 140.0, BASE_UP_D, BASE_DOWN_D, MESHES["medium"], 2.5),
    StudyCase("baseline_medium_Re160", "mesh-study+transition-sweep", 160.0, BASE_UP_D, BASE_DOWN_D, MESHES["medium"], 3.0),
    StudyCase("long_medium_Re200", "benchmark-vs-sahin", 200.0, LONG_UP_D, LONG_DOWN_D, MESHES["medium"], 4.0),
    StudyCase("baseline_fine_Re160", "mesh-study", 160.0, BASE_UP_D, BASE_DOWN_D, MESHES["fine"], 3.0),
    StudyCase("long_medium_Re160", "streamwise-domain-check", 160.0, LONG_UP_D, LONG_DOWN_D, MESHES["medium"], 3.0),
    StudyCase("long_target100k_Re160", "mesh-study replacement around 100k cells", 160.0, LONG_UP_D, LONG_DOWN_D, MESHES["target100k"], 3.0),
]
CASE_MAP = {case.name: case for case in CASES}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def ensure_run_layout(run_dir: Path) -> None:
    for name in ("00_notes", "01_run_setup", "02_simulations", "03_run_summary", "04_publication_candidates", "05_run_logs"):
        ensure_dir(run_dir / name)


def ensure_sim_layout(sim_dir: Path) -> None:
    for name in ("00_notes", "01_openfoam_setup", "02_raw_data", "03_processed_data", "04_plots", "05_logs"):
        ensure_dir(sim_dir / name)


def ensure_active_run() -> None:
    ensure_dir(RUNS_RESULTS_ROOT)
    ensure_run_layout(ACTIVE_RUN_DIR)


def simulation_archive_dir(case_name: str, create: bool = False) -> Path:
    ensure_active_run()
    sim_dir = ACTIVE_RUN_SIMS_DIR / case_name
    if create:
        ensure_sim_layout(sim_dir)
    return sim_dir


def u_centerline(reynolds: float) -> float:
    return reynolds * NU / D


def u_bulk(reynolds: float) -> float:
    return (2.0 / 3.0) * u_centerline(reynolds)


def dims(case: StudyCase) -> dict[str, float]:
    xmin = -case.upstream_D * D
    xmax = case.downstream_D * D
    return {"xmin": xmin, "xmax": xmax, "length": xmax - xmin}


def base_counts(case: StudyCase) -> tuple[int, int]:
    d = dims(case)
    nx = max(120, int(round(d["length"] / case.mesh.base_dx)))
    ny = max(12, int(round(H / case.mesh.base_dx)))
    return nx, ny


def resolve_cases(names: list[str]) -> list[StudyCase]:
    if not names:
        return CASES
    resolved = []
    for name in names:
        if name not in CASE_MAP:
            raise SystemExit(f"Unknown case '{name}'.")
        resolved.append(CASE_MAP[name])
    return resolved


def metadata(case: StudyCase) -> dict[str, object]:
    d = dims(case)
    nx, ny = base_counts(case)
    return {
        "case": case.name,
        "purpose": case.purpose,
        "mesh": case.mesh.name,
        "reynolds": case.reynolds,
        "u_centerline_m_per_s": u_centerline(case.reynolds),
        "u_bulk_m_per_s": u_bulk(case.reynolds),
        "upstream_D": case.upstream_D,
        "downstream_D": case.downstream_D,
        "beta": BETA,
        "diameter_m": D,
        "channel_height_m": H,
        "span_m": SPAN,
        "base_dx_m": case.mesh.base_dx,
        "base_nx": nx,
        "base_ny": ny,
        "surface_level": case.mesh.surface_level,
        "near_level": case.mesh.near_level,
        "wake_level": case.mesh.wake_level,
        "cylinder_layers": case.mesh.cylinder_layers,
        "wall_layers": case.mesh.wall_layers,
        "end_time_s": case.end_time_s,
        "x_min_m": d["xmin"],
        "x_max_m": d["xmax"],
        "length_m": d["length"],
    }


def block_mesh_dict(case: StudyCase) -> str:
    d = dims(case)
    nx, ny = base_counts(case)
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
    ({d['xmin']:.6f} {-HALF_H:.6f} {Z_MIN:.6f})
    ({d['xmax']:.6f} {-HALF_H:.6f} {Z_MIN:.6f})
    ({d['xmax']:.6f} {HALF_H:.6f} {Z_MIN:.6f})
    ({d['xmin']:.6f} {HALF_H:.6f} {Z_MIN:.6f})
    ({d['xmin']:.6f} {-HALF_H:.6f} {Z_MAX:.6f})
    ({d['xmax']:.6f} {-HALF_H:.6f} {Z_MAX:.6f})
    ({d['xmax']:.6f} {HALF_H:.6f} {Z_MAX:.6f})
    ({d['xmin']:.6f} {HALF_H:.6f} {Z_MAX:.6f})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1)
);

edges ();

boundary
(
    inlet
    {{
        type patch;
        faces ((0 4 7 3));
    }}
    outlet
    {{
        type patch;
        faces ((1 2 6 5));
    }}
    bottom
    {{
        type wall;
        faces ((0 1 5 4));
    }}
    top
    {{
        type wall;
        faces ((3 7 6 2));
    }}
    front
    {{
        type empty;
        faces ((0 3 2 1));
    }}
    back
    {{
        type empty;
        faces ((4 5 6 7));
    }}
);

mergePatchPairs ();
"""


def snappy_hex_mesh_dict(case: StudyCase) -> str:
    near_xmin = -2.5 * D
    near_xmax = 6.0 * D
    near_h = 1.25 * H
    wake_xmin = 0.0
    wake_xmax = 12.0 * D
    wake_h = 0.9 * H
    loc = dims(case)["xmin"] + 0.5 * D
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}

castellatedMesh true;
snap            true;
addLayers       true;

geometry
{{
    cylinder
    {{
        type searchableCylinder;
        point1 (0 0 -0.010);
        point2 (0 0 0.010);
        radius {D / 2.0:.6f};
    }}
    nearCylinder
    {{
        type searchableBox;
        min ({near_xmin:.6f} {-near_h:.6f} -0.010);
        max ({near_xmax:.6f} {near_h:.6f} 0.010);
    }}
    wakeBox
    {{
        type searchableBox;
        min ({wake_xmin:.6f} {-wake_h:.6f} -0.010);
        max ({wake_xmax:.6f} {wake_h:.6f} 0.010);
    }}
}}

castellatedMeshControls
{{
    maxLocalCells 600000;
    maxGlobalCells 2400000;
    minRefinementCells 0;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;
    resolveFeatureAngle 30;
    features ();
    refinementSurfaces
    {{
        cylinder
        {{
            level ({case.mesh.surface_level} {case.mesh.surface_level});
            patchInfo {{ type wall; }}
        }}
    }}
    refinementRegions
    {{
        nearCylinder
        {{
            mode inside;
            levels ((1e15 {case.mesh.near_level}));
        }}
        wakeBox
        {{
            mode inside;
            levels ((1e15 {case.mesh.wake_level}));
        }}
    }}
    locationInMesh ({loc:.6f} 0 0);
    allowFreeStandingZoneFaces true;
}}

snapControls
{{
    nSmoothPatch 5;
    tolerance 2.0;
    nSolveIter 100;
    nRelaxIter 5;
    nFeatureSnapIter 10;
    implicitFeatureSnap true;
    explicitFeatureSnap false;
    multiRegionFeatureSnap false;
}}

addLayersControls
{{
    relativeSizes true;
    expansionRatio {case.mesh.expansion_ratio:.3f};
    finalLayerThickness {case.mesh.final_layer_thickness:.3f};
    minThickness 0.01;
    nGrow 0;
    featureAngle 60;
    nRelaxIter 3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
    nRelaxedIter 20;
    layers
    {{
        cylinder {{ nSurfaceLayers {case.mesh.cylinder_layers}; }}
        top {{ nSurfaceLayers {case.mesh.wall_layers}; }}
        bottom {{ nSurfaceLayers {case.mesh.wall_layers}; }}
    }}
}}

meshQualityControls
{{
    maxNonOrtho 65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave 80;
    minVol 1e-13;
    minTetQuality 1e-30;
    minArea -1;
    minTwist 0.02;
    minDeterminant 0.001;
    minFaceWeight 0.02;
    minVolRatio 0.01;
    minTriangleTwist -1;
    nSmoothScale 4;
    errorReduction 0.75;
    relaxed {{ maxNonOrtho 75; }}
}}

writeFlags ( scalarLevels layerSets );
mergeTolerance 1e-6;
"""


def u_file(case: StudyCase) -> str:
    uc = u_centerline(case.reynolds)
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({uc:.9f} 0 0);

boundaryField
{{
    inlet
    {{
        type exprFixedValue;
        valueExpr "vector({uc:.9f}*(1.0 - pow(2.0*pos().y()/{H:.9f}, 2.0)), 0, 0)";
        value uniform (0 0 0);
    }}
    outlet {{ type zeroGradient; }}
    top {{ type noSlip; }}
    bottom {{ type noSlip; }}
    cylinder {{ type noSlip; }}
    front {{ type empty; }}
    back {{ type empty; }}
}}
"""


def p_file() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}

dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet { type zeroGradient; }
    outlet { type fixedValue; value uniform 0; }
    top { type zeroGradient; }
    bottom { type zeroGradient; }
    cylinder { type zeroGradient; }
    front { type empty; }
    back { type empty; }
}
"""


def control_dict(case: StudyCase) -> str:
    uc = u_centerline(case.reynolds)
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
endTime         {case.end_time_s:.3f};
deltaT          1e-3;
adjustTimeStep  yes;
maxCo           0.9;
writeControl    runTime;
writeInterval   0.2;
purgeWrite      0;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
timeFormat      general;
timePrecision   12;
runTimeModifiable true;

functions
{{
    forceCoeffs
    {{
        type forceCoeffs;
        libs (forces);
        executeControl timeStep;
        executeInterval 1;
        writeControl timeStep;
        writeInterval 1;
        log yes;
        patches (cylinder);
        rho rhoInf;
        rhoInf {RHO:.6f};
        CofR (0 0 0);
        liftDir (0 1 0);
        dragDir (1 0 0);
        pitchAxis (0 0 1);
        magUInf {uc:.9f};
        lRef {D:.6f};
        Aref {D * SPAN:.9f};
    }}
    residuals
    {{
        type solverInfo;
        libs (utilityFunctionObjects);
        fields (U p);
        writeControl timeStep;
        writeInterval 1;
    }}
    CourantNo
    {{
        type CourantNo;
        libs (fieldFunctionObjects);
        writeControl writeTime;
    }}
}}
"""


def fv_schemes() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes { default backward; }
gradSchemes { default Gauss linear; grad(U) Gauss linear; }
divSchemes
{
    default none;
    div(phi,U) Gauss linearUpwind grad(U);
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
wallDist { method meshWave; }
"""


def fv_solution() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

solvers
{
    p
    {
        solver GAMG;
        smoother GaussSeidel;
        tolerance 1e-7;
        relTol 0.01;
    }
    pFinal
    {
        $p;
        relTol 0;
        tolerance 1e-8;
    }
    U
    {
        solver PBiCGStab;
        preconditioner DILU;
        tolerance 1e-8;
        relTol 0.05;
    }
    UFinal
    {
        $U;
        relTol 0;
        tolerance 1e-9;
    }
}

PIMPLE
{
    nOuterCorrectors 1;
    nCorrectors 2;
    nNonOrthogonalCorrectors 1;
    pRefCell 0;
    pRefValue 0;
}

relaxationFactors
{
    equations
    {
        U 0.9;
        UFinal 1.0;
    }
}
"""


def transport_properties() -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}}

transportModel  Newtonian;
nu              {NU:.9e};
"""


def turbulence_properties() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}

simulationType laminar;
"""


def set_expr_fields_dict(case: StudyCase) -> str:
    uc = u_centerline(case.reynolds)
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      setExprFieldsDict;
}}

readFields ( U );

expressions
(
    U
    {{
        field U;
        create no;
        dimensions [0 1 -1 0 0 0 0];
        expression
        #{{ vector
            (
                {uc:.9f}*(1.0 - pow(2.0*pos().y()/{H:.9f}, 2.0)),
                0.0025*exp(-pow((pos().x()-0.012)/0.010, 2.0) - pow((pos().y()-0.0035)/0.0035, 2.0)),
                0
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
rm -rf 0
cp -r 0.orig 0
mkdir -p logs
blockMesh | tee logs/blockMesh.log
snappyHexMesh -overwrite | tee logs/snappyHexMesh.log
checkMesh | tee logs/checkMesh.log
setExprFields | tee logs/setExprFields.log
pimpleFoam | tee logs/pimpleFoam.log
"""


def write_input_md(case: StudyCase, target: Path) -> None:
    meta = metadata(case)
    lines = [
        f"# {case.name} input",
        "",
        "## Purpose",
        "",
        f"- {case.purpose}",
        "",
        "## Geometry",
        "",
        f"- D = {D:.6f} m",
        f"- beta = {BETA:.3f}",
        f"- upstream = {case.upstream_D:.1f}D",
        f"- downstream = {case.downstream_D:.1f}D",
        f"- H = {H:.6f} m",
        "",
        "## Flow setup",
        "",
        f"- Re = {case.reynolds:.1f}",
        f"- Uc = {meta['u_centerline_m_per_s']:.9f} m/s",
        f"- Ub = {meta['u_bulk_m_per_s']:.9f} m/s",
        "- inlet profile = parabolic",
        "- top/bottom/cylinder = no-slip",
        "- front/back = empty",
        "",
        "## Mesh setup",
        "",
        f"- mesh level = {case.mesh.name}",
        f"- base dx = {case.mesh.base_dx:.6f} m",
        f"- base mesh = {meta['base_nx']} x {meta['base_ny']} x 1",
        f"- surface / near / wake levels = {case.mesh.surface_level} / {case.mesh.near_level} / {case.mesh.wake_level}",
        f"- cylinder layers = {case.mesh.cylinder_layers}",
        f"- wall layers = {case.mesh.wall_layers}",
        "",
        "## Notes",
        "",
        "- For V1, channel height is physics because it sets beta = 0.5.",
        "- Domain sensitivity therefore means streamwise padding, not height variation.",
        f"- Primary benchmark family: {LITERATURE_PRIMARY}",
        f"- Supporting setup note: {LITERATURE_SUPPORT}",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_case(case: StudyCase, overwrite: bool) -> None:
    case_dir = RUN_ROOT / case.name
    if case_dir.exists():
        if not overwrite:
            return
        shutil.rmtree(case_dir)

    ensure_dir(case_dir / "0.orig")
    ensure_dir(case_dir / "constant")
    ensure_dir(case_dir / "system")
    ensure_dir(case_dir / "logs")
    (case_dir / "0.orig" / "U").write_text(u_file(case), encoding="ascii")
    (case_dir / "0.orig" / "p").write_text(p_file(), encoding="ascii")
    (case_dir / "constant" / "transportProperties").write_text(transport_properties(), encoding="ascii")
    (case_dir / "constant" / "turbulenceProperties").write_text(turbulence_properties(), encoding="ascii")
    (case_dir / "system" / "blockMeshDict").write_text(block_mesh_dict(case), encoding="ascii")
    (case_dir / "system" / "snappyHexMeshDict").write_text(snappy_hex_mesh_dict(case), encoding="ascii")
    (case_dir / "system" / "controlDict").write_text(control_dict(case), encoding="ascii")
    (case_dir / "system" / "fvSchemes").write_text(fv_schemes(), encoding="ascii")
    (case_dir / "system" / "fvSolution").write_text(fv_solution(), encoding="ascii")
    (case_dir / "system" / "setExprFieldsDict").write_text(set_expr_fields_dict(case), encoding="ascii")
    (case_dir / "Allrun").write_text(allrun_file(), encoding="ascii", newline="\n")
    (case_dir / "caseMeta.json").write_text(json.dumps(metadata(case), indent=2), encoding="utf-8")
    write_input_md(case, case_dir / "input.md")

    sim_dir = simulation_archive_dir(case.name, create=True)
    write_input_md(case, sim_dir / "00_notes" / "input.md")


def write_study_plan() -> None:
    ensure_dir(STUDY_SUMMARY_DIR)
    lines = [
        "# V1 Study Plan",
        "",
        "- Goal: verify V1 on a confined no-slip cylinder benchmark before moving to V2-V4b.",
        "- Height is not a free domain variable in V1 because it sets beta = 0.5.",
        "- Streamwise domain sensitivity is checked with a longer 10D/30D case.",
        "- Mesh sensitivity is checked at Re = 160 where periodic shedding should be easier to resolve.",
        "- A medium-mesh Re sweep brackets the onset region.",
        "",
        f"- Benchmark family: {LITERATURE_PRIMARY}",
        f"- Setup support: {LITERATURE_SUPPORT}",
        "",
        "| case | purpose | Re | mesh | upstream | downstream |",
        "|---|---|---:|---|---:|---:|",
    ]
    for case in CASES:
        lines.append(
            f"| {case.name} | {case.purpose} | {case.reynolds:.0f} | {case.mesh.name} | "
            f"{case.upstream_D:.0f}D | {case.downstream_D:.0f}D |"
        )
    (STUDY_SUMMARY_DIR / "study_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_run_scope() -> None:
    ensure_active_run()
    lines = [
        f"# {ACTIVE_RUN_NAME}",
        "",
        "## Meaning of this run",
        "",
        "- In V1, one run is one verification campaign / attempt.",
        "- Multiple simulations with different Reynolds numbers, meshes, or domain lengths belong to the same run.",
        "- A new run number is used only when the whole attempt is repeated after a failed or superseded campaign.",
        "",
        "## Simulations included in this run",
        "",
        "| simulation | purpose | Re | mesh | upstream | downstream |",
        "|---|---|---:|---|---:|---:|",
    ]
    for case in CASES:
        lines.append(
            f"| {case.name} | {case.purpose} | {case.reynolds:.0f} | {case.mesh.name} | "
            f"{case.upstream_D:.0f}D | {case.downstream_D:.0f}D |"
        )
    (ACTIVE_RUN_NOTES_DIR / "run_scope.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare(case_names: list[str], overwrite: bool) -> None:
    ensure_dir(RUN_ROOT)
    ensure_dir(RESULTS_ROOT)
    ensure_dir(RUNS_RESULTS_ROOT)
    ensure_dir(STUDY_SUMMARY_DIR)
    ensure_dir(STUDY_PLOTS_DIR)
    ensure_dir(PUBLICATION_DIR)
    ensure_active_run()
    write_study_plan()
    write_run_scope()
    for case in resolve_cases(case_names):
        write_case(case, overwrite)
    (STUDY_SUMMARY_DIR / "manifest.json").write_text(
        json.dumps({"run_root": str(RUN_ROOT), "cases": [metadata(c) for c in CASES]}, indent=2),
        encoding="utf-8",
    )
    print(RUN_ROOT)


def parse_check_mesh(log_path: Path) -> dict[str, object]:
    result: dict[str, object] = {"status": "missing", "cells": None, "points": None, "faces": None, "max_non_ortho": None}
    if not log_path.exists():
        return result
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    result["status"] = "ok" if "Mesh OK." in text else "warn"
    for key, pattern in {
        "points": r"points:\s+(\d+)",
        "faces": r"faces:\s+(\d+)",
        "cells": r"cells:\s+(\d+)",
        "max_non_ortho": r"Mesh non-orthogonality Max:\s+([0-9.eE+-]+)",
    }.items():
        match = re.search(pattern, text)
        if match:
            result[key] = int(match.group(1)) if key in {"points", "faces", "cells"} else float(match.group(1))
    return result


def coeff_paths(case_dir: Path) -> list[Path]:
    root = case_dir / "postProcessing" / "forceCoeffs"
    if not root.exists():
        return []
    paths = []
    for child in root.iterdir():
        coeff = child / "coefficient.dat"
        if child.is_dir() and coeff.exists():
            try:
                start = float(child.name)
            except ValueError:
                start = math.inf
            paths.append((start, coeff))
    return [path for _, path in sorted(paths, key=lambda item: item[0])]


def load_coeffs(paths: list[Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    merged: dict[float, tuple[float, float]] = {}
    for path in paths:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                parts = stripped.split()
                if len(parts) < 5:
                    continue
                merged[float(parts[0])] = (float(parts[1]), float(parts[4]))
    ordered = sorted(merged.items())
    time = np.asarray([item[0] for item in ordered], dtype=float)
    cd = np.asarray([item[1][0] for item in ordered], dtype=float)
    cl = np.asarray([item[1][1] for item in ordered], dtype=float)
    return time, cd, cl


def metrics(case: StudyCase, time: np.ndarray, cd: np.ndarray, cl: np.ndarray) -> dict[str, object]:
    if time.size < 32:
        return {"status": "insufficient-data", "regime": "undetermined", "time_max_s": float(time.max()) if time.size else None, "Cd_mean": None, "Cd_std": None, "Cl_rms": None, "frequency_hz": None, "St": None}

    start = max(0.4 * float(time.max()), float(time.max()) - 4.0)
    mask = time >= start
    t = time[mask]
    cd_sel = cd[mask]
    cl_sel = cl[mask]
    cd_mean = float(np.mean(cd_sel))
    cd_std = float(np.std(cd_sel))
    cl_centered = cl_sel - np.mean(cl_sel)
    cl_rms = float(np.sqrt(np.mean(cl_centered**2)))
    if t.size < 32 or cl_rms < 1e-3:
        return {"status": "ok", "regime": "steady-or-weakly-unsteady", "analysis_start_s": start, "time_max_s": float(time.max()), "Cd_mean": cd_mean, "Cd_std": cd_std, "Cl_rms": cl_rms, "frequency_hz": None, "St": None}

    dt = float(np.mean(np.diff(t)))
    window = np.hanning(cl_centered.size)
    nfft = 1
    while nfft < cl_centered.size * 8:
        nfft *= 2
    freqs = np.fft.rfftfreq(nfft, d=dt)
    amps = np.abs(np.fft.rfft(cl_centered * window, n=nfft))
    valid = (freqs > 0.0) & (freqs < 20.0)
    freqs = freqs[valid]
    amps = amps[valid]
    peak = int(np.argmax(amps))
    freq = float(freqs[peak])
    if 0 < peak < freqs.size - 1:
        alpha = amps[peak - 1]
        beta = amps[peak]
        gamma = amps[peak + 1]
        denom = alpha - 2.0 * beta + gamma
        if abs(denom) > 1e-12:
            freq += float(0.5 * (alpha - gamma) / denom * (freqs[1] - freqs[0]))
    return {
        "status": "ok",
        "regime": "periodic",
        "analysis_start_s": start,
        "time_max_s": float(time.max()),
        "Cd_mean": cd_mean,
        "Cd_std": cd_std,
        "Cl_rms": cl_rms,
        "frequency_hz": freq,
        "St": float(freq * D / u_centerline(case.reynolds)),
    }


def plot_cl(case_name: str, time: np.ndarray, cl: np.ndarray) -> None:
    sim_dir = simulation_archive_dir(case_name, create=True)
    ensure_dir(sim_dir / "04_plots")
    plt.figure(figsize=(10, 5), dpi=160)
    plt.plot(time, cl, linewidth=1.0, color="#0b5ed7")
    plt.xlabel("Time [s]")
    plt.ylabel("Cl [-]")
    plt.title(f"{case_name}: Cl(t)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(sim_dir / "04_plots" / "Cl_vs_time.png")
    plt.close()


def write_output_md(case: StudyCase, target: Path, mesh_info: dict[str, object], run_metrics: dict[str, object], all_metrics: dict[str, dict[str, object]]) -> None:
    baseline = all_metrics.get("baseline_medium_Re160", {})
    notes = []
    if baseline.get("Cd_mean") is not None and run_metrics.get("Cd_mean") is not None:
        base_cd = float(baseline["Cd_mean"])
        cur_cd = float(run_metrics["Cd_mean"])
        notes.append(f"Delta Cd_mean vs baseline_medium_Re160 = {100.0 * (cur_cd - base_cd) / base_cd:+.2f}%.")
    if baseline.get("St") is not None and run_metrics.get("St") is not None:
        base_st = float(baseline["St"])
        cur_st = float(run_metrics["St"])
        notes.append(f"Delta St vs baseline_medium_Re160 = {100.0 * (cur_st - base_st) / base_st:+.2f}%.")
    if not notes:
        notes.append("Relative comparison is limited because one of the cases is not periodic.")

    lines = [
        f"# {case.name} output",
        "",
        "## Run status",
        "",
        f"- mesh check status = {mesh_info['status']}",
        f"- interpreted regime = {run_metrics['regime']}",
        "",
        "## Mesh summary",
        "",
        f"- cells = {mesh_info['cells']}",
        f"- points = {mesh_info['points']}",
        f"- faces = {mesh_info['faces']}",
        f"- max non-orthogonality = {mesh_info['max_non_ortho']}",
        "",
        "## Force metrics",
        "",
        f"- time reached [s] = {run_metrics.get('time_max_s')}",
        f"- Cd_mean = {run_metrics.get('Cd_mean')}",
        f"- Cd_std = {run_metrics.get('Cd_std')}",
        f"- Cl_rms = {run_metrics.get('Cl_rms')}",
        f"- frequency [Hz] = {run_metrics.get('frequency_hz')}",
        f"- St = {run_metrics.get('St')}",
        "",
        "## Benchmark comment",
        "",
        "- Comparison is against the Sahin confined-cylinder benchmark family, with emphasis on onset behaviour and force convergence.",
        f"- {' '.join(notes)}",
        "- For V1, height is not treated as a numerical-domain variable because it defines beta = 0.5.",
        "",
        "## Sources",
        "",
        f"- {LITERATURE_PRIMARY}",
        f"- {LITERATURE_SUPPORT}",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def analyze(case_names: list[str]) -> None:
    ensure_dir(RESULTS_ROOT)
    ensure_dir(RUNS_RESULTS_ROOT)
    ensure_dir(STUDY_SUMMARY_DIR)
    ensure_dir(STUDY_PLOTS_DIR)
    ensure_active_run()
    write_run_scope()
    selected = resolve_cases(case_names)
    rows: list[dict[str, object]] = []
    all_metrics: dict[str, dict[str, object]] = {}
    signals: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    for case in selected:
        case_dir = RUN_ROOT / case.name
        mesh_info = parse_check_mesh(case_dir / "logs" / "checkMesh.log")
        paths = coeff_paths(case_dir)
        if paths:
            time, cd, cl = load_coeffs(paths)
            run_metrics = metrics(case, time, cd, cl)
            if time.size:
                plot_cl(case.name, time, cl)
                signals[case.name] = (time, cl)
        else:
            run_metrics = {"status": "missing-force-data", "regime": "not-run-or-failed", "time_max_s": None, "Cd_mean": None, "Cd_std": None, "Cl_rms": None, "frequency_hz": None, "St": None}
        all_metrics[case.name] = run_metrics
        rows.append({
            "case": case.name,
            "purpose": case.purpose,
            "Re": case.reynolds,
            "mesh": case.mesh.name,
            "upstream_D": case.upstream_D,
            "downstream_D": case.downstream_D,
            "cells": mesh_info["cells"],
            "regime": run_metrics["regime"],
            "Cd_mean": run_metrics["Cd_mean"],
            "Cl_rms": run_metrics["Cl_rms"],
            "frequency_hz": run_metrics["frequency_hz"],
            "St": run_metrics["St"],
            "time_max_s": run_metrics["time_max_s"],
            "status": run_metrics["status"],
        })

    for case in selected:
        mesh_info = parse_check_mesh(RUN_ROOT / case.name / "logs" / "checkMesh.log")
        sim_dir = simulation_archive_dir(case.name, create=True)
        (sim_dir / "03_processed_data" / "summary.json").write_text(
            json.dumps(
                {
                    "case": case.name,
                    "metadata": metadata(case),
                    "mesh": mesh_info,
                    "metrics": all_metrics[case.name],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        write_output_md(case, sim_dir / "00_notes" / "output.md", mesh_info, all_metrics[case.name], all_metrics)

    if rows:
        lines = [
            "# V1 Summary",
            "",
            "| case | purpose | Re | mesh | upstream | downstream | cells | regime | Cd_mean | Cl_rms | f [Hz] | St | status |",
            "|---|---|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---|",
        ]
        for row in rows:
            lines.append(
                f"| {row['case']} | {row['purpose']} | {row['Re']} | {row['mesh']} | {row['upstream_D']}D | {row['downstream_D']}D | "
                f"{row['cells']} | {row['regime']} | {row['Cd_mean']} | {row['Cl_rms']} | {row['frequency_hz']} | {row['St']} | {row['status']} |"
            )
        for target_dir in (STUDY_SUMMARY_DIR, ACTIVE_RUN_SUMMARY_DIR):
            ensure_dir(target_dir)
            with (target_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            (target_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    mesh_cases = [name for name in signals if "Re160" in name and name != "long_medium_Re160"]
    if mesh_cases:
        plt.figure(figsize=(11, 6), dpi=160)
        for name in mesh_cases:
            time, cl = signals[name]
            plt.plot(time, cl, linewidth=1.0, label=name)
        plt.xlabel("Time [s]")
        plt.ylabel("Cl [-]")
        plt.title("V1 mesh-study comparison at Re = 160")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(STUDY_PLOTS_DIR / "mesh_study_Cl_overlay.png")
        ensure_dir(ACTIVE_RUN_SUMMARY_DIR / "plots")
        plt.savefig(ACTIVE_RUN_SUMMARY_DIR / "plots" / "mesh_study_Cl_overlay.png")
        plt.close()

    transition_cases = [name for name in signals if "baseline_medium_Re" in name]
    if transition_cases:
        plt.figure(figsize=(11, 6), dpi=160)
        for name in transition_cases:
            time, cl = signals[name]
            plt.plot(time, cl, linewidth=1.0, label=name)
        plt.xlabel("Time [s]")
        plt.ylabel("Cl [-]")
        plt.title("V1 medium-mesh transition sweep")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(STUDY_PLOTS_DIR / "transition_sweep_Cl_overlay.png")
        ensure_dir(ACTIVE_RUN_SUMMARY_DIR / "plots")
        plt.savefig(ACTIVE_RUN_SUMMARY_DIR / "plots" / "transition_sweep_Cl_overlay.png")
        plt.close()

    print(RESULTS_ROOT)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Prepare and analyze V1 confined-cylinder study cases.")
    parser.add_argument("command", choices=["prepare", "analyze"])
    parser.add_argument("cases", nargs="*")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.cases, args.overwrite)
    else:
        analyze(args.cases)


if __name__ == "__main__":
    main()
