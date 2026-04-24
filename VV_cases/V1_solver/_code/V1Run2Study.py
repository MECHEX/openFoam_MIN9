from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
import math
import re
import shutil
import stat
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO_CASE = Path(__file__).resolve().parent.parent
RUN_ROOT = Path(r"C:\openfoam-case\VV_cases\V1_solver_run002")
RESULTS_ROOT = REPO_CASE / "results" / "study_v1"
RUNS_RESULTS_ROOT = RESULTS_ROOT / "runs"
ACTIVE_RUN_NAME = "002_data_sahin_owens_poiseuille_verification"
ACTIVE_RUN_DIR = RUNS_RESULTS_ROOT / ACTIVE_RUN_NAME
ACTIVE_RUN_NOTES_DIR = ACTIVE_RUN_DIR / "00_notes"
ACTIVE_RUN_SETUP_DIR = ACTIVE_RUN_DIR / "01_run_setup"
ACTIVE_RUN_SIMS_DIR = ACTIVE_RUN_DIR / "02_simulations"
ACTIVE_RUN_SUMMARY_DIR = ACTIVE_RUN_DIR / "03_run_summary"
ACTIVE_RUN_PUBLICATION_DIR = ACTIVE_RUN_DIR / "04_publication_candidates"
STUDY_SUMMARY_DIR = RESULTS_ROOT / "study_summary" / ACTIVE_RUN_NAME
STUDY_PLOTS_DIR = STUDY_SUMMARY_DIR / "plots"
PUBLICATION_DIR = RESULTS_ROOT / "publication" / ACTIVE_RUN_NAME

D = 0.012
NU = 1.516e-5
RHO = 1.205
SPAN = 0.01
Z_MIN = -SPAN / 2.0
Z_MAX = SPAN / 2.0
UP_D = 8.0
DOWN_D = 20.0
LITERATURE = "Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285"

SAHIN_OWENS = {
    0.10: {"Re_crit": 50.81, "St_crit": 0.1210},
    0.20: {"Re_crit": 69.43, "St_crit": 0.1566},
    0.30: {"Re_crit": 94.56, "St_crit": 0.2090},
    0.50: {"Re_crit": 124.09, "St_crit": 0.3393},
    0.70: {"Re_crit": 110.29, "St_crit": 0.4752},
    0.80: {"Re_crit": 110.24, "St_crit": 0.5363},
    0.84: {"Re_crit": 113.69, "St_crit": 0.5568},
}


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
    beta: float
    reynolds: float
    upstream_D: float
    downstream_D: float
    mesh: MeshVariant
    end_time_s: float

    @property
    def H(self) -> float:
        return D / self.beta

    @property
    def half_H(self) -> float:
        return self.H / 2.0

    @property
    def u_max(self) -> float:
        return self.reynolds * NU / D

    @property
    def u_bulk(self) -> float:
        return (2.0 / 3.0) * self.u_max


MESHES = {
    "medium": MeshVariant("medium", 0.0025, 3, 2, 1, 6, 2, 0.25, 1.20),
}

CASES = [
    StudyCase("b030_medium_Re080", "beta=0.30 below Re_crit",        0.30,  80.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b030_medium_Re090", "beta=0.30 steady bracket lower", 0.30,  90.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b030_medium_Re095", "beta=0.30 near Re_crit",         0.30,  95.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b030_medium_Re100", "beta=0.30 above Re_crit",        0.30, 100.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b030_medium_Re120", "beta=0.30 well above Re_crit",   0.30, 120.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b0375_medium_Re090", "beta=0.375 below interpolated Re_crit",      0.375,  90.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b0375_medium_Re105", "beta=0.375 steady bracket lower",            0.375, 105.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b0375_medium_Re110", "beta=0.375 near interpolated Re_crit",       0.375, 110.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b0375_medium_Re120", "beta=0.375 above interpolated Re_crit",      0.375, 120.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b0375_medium_Re135", "beta=0.375 well above interpolated Re_crit", 0.375, 135.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b050_medium_Re100", "beta=0.50 below Re_crit",                0.50, 100.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b050_medium_Re120", "beta=0.50 steady",                        0.50, 120.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b050_medium_Re125", "beta=0.50 steady onset test 15s",         0.50, 125.0, UP_D, DOWN_D, MESHES["medium"], 15.0),
    StudyCase("b050_medium_Re130", "beta=0.50 steady onset test",             0.50, 130.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b050_medium_Re135", "beta=0.50 bracket midpoint test 15s",     0.50, 135.0, UP_D, DOWN_D, MESHES["medium"], 15.0),
    StudyCase("b050_medium_Re140", "beta=0.50 periodic",                      0.50, 140.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b050_medium_Re150", "beta=0.50 well above Re_crit",            0.50, 150.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
    StudyCase("b060_medium_Re120", "beta=0.60 steady onset test 15s",    0.60, 120.0, UP_D, DOWN_D, MESHES["medium"], 15.0),
    StudyCase("b060_medium_Re125", "beta=0.60 bracket lower test 15s",  0.60, 125.0, UP_D, DOWN_D, MESHES["medium"], 15.0),
    StudyCase("b060_medium_Re135", "beta=0.60 periodic above Re_crit",  0.60, 135.0, UP_D, DOWN_D, MESHES["medium"],  5.0),
]
CASE_MAP = {case.name: case for case in CASES}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def ensure_active_run() -> None:
    for path in (
        RUNS_RESULTS_ROOT,
        ACTIVE_RUN_DIR,
        ACTIVE_RUN_NOTES_DIR,
        ACTIVE_RUN_SETUP_DIR,
        ACTIVE_RUN_SIMS_DIR,
        ACTIVE_RUN_SUMMARY_DIR,
        ACTIVE_RUN_PUBLICATION_DIR,
        STUDY_SUMMARY_DIR,
        STUDY_PLOTS_DIR,
        PUBLICATION_DIR,
    ):
        ensure_dir(path)


def ensure_sim_layout(path: Path) -> None:
    for name in ("00_notes", "01_openfoam_setup", "02_raw_data", "03_processed_data", "04_plots", "05_logs"):
        ensure_dir(path / name)


def sim_dir(case_name: str, create: bool = False) -> Path:
    ensure_active_run()
    path = ACTIVE_RUN_SIMS_DIR / case_name
    if create:
        ensure_sim_layout(path)
    return path


def resolve_cases(names: list[str]) -> list[StudyCase]:
    if not names:
        return CASES
    return [CASE_MAP[name] for name in names]


def domain(case: StudyCase) -> dict[str, float]:
    xmin = -case.upstream_D * D
    xmax = case.downstream_D * D
    return {"xmin": xmin, "xmax": xmax, "length": xmax - xmin}


def base_counts(case: StudyCase) -> tuple[int, int]:
    d = domain(case)
    return max(120, int(round(d["length"] / case.mesh.base_dx))), max(8, int(round(case.H / case.mesh.base_dx)))


def so_ref(beta: float) -> dict[str, object]:
    exact = SAHIN_OWENS.get(beta)
    if exact:
        return {"Re_crit": exact["Re_crit"], "St_crit": exact["St_crit"], "interpolated": False}
    betas = sorted(SAHIN_OWENS)
    lo = max(b for b in betas if b <= beta)
    hi = min(b for b in betas if b >= beta)
    t = (beta - lo) / (hi - lo)
    return {
        "Re_crit": round(SAHIN_OWENS[lo]["Re_crit"] * (1 - t) + SAHIN_OWENS[hi]["Re_crit"] * t, 2),
        "St_crit": round(SAHIN_OWENS[lo]["St_crit"] * (1 - t) + SAHIN_OWENS[hi]["St_crit"] * t, 4),
        "interpolated": True,
    }


def metadata(case: StudyCase) -> dict[str, object]:
    nx, ny = base_counts(case)
    ref = so_ref(case.beta)
    return {
        "case": case.name,
        "purpose": case.purpose,
        "beta": case.beta,
        "reynolds": case.reynolds,
        "u_max_m_per_s": case.u_max,
        "u_bulk_m_per_s": case.u_bulk,
        "mesh": case.mesh.name,
        "base_nx": nx,
        "base_ny": ny,
        "so_Re_crit": ref["Re_crit"],
        "so_St_crit": ref["St_crit"],
    }


def write_text(path: Path, text: str, encoding: str = "ascii") -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding=encoding, newline="\n")


def block_mesh_dict(case: StudyCase) -> str:
    d = domain(case)
    nx, ny = base_counts(case)
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object blockMeshDict;
}}
scale 1;
vertices
(
    ({d["xmin"]:.6f} {-case.half_H:.6f} {Z_MIN:.6f})
    ({d["xmax"]:.6f} {-case.half_H:.6f} {Z_MIN:.6f})
    ({d["xmax"]:.6f} {case.half_H:.6f} {Z_MIN:.6f})
    ({d["xmin"]:.6f} {case.half_H:.6f} {Z_MIN:.6f})
    ({d["xmin"]:.6f} {-case.half_H:.6f} {Z_MAX:.6f})
    ({d["xmax"]:.6f} {-case.half_H:.6f} {Z_MAX:.6f})
    ({d["xmax"]:.6f} {case.half_H:.6f} {Z_MAX:.6f})
    ({d["xmin"]:.6f} {case.half_H:.6f} {Z_MAX:.6f})
);
blocks ( hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1) );
edges ();
boundary
(
    inlet  {{ type patch; faces ((0 4 7 3)); }}
    outlet {{ type patch; faces ((1 2 6 5)); }}
    bottom {{ type wall;  faces ((0 1 5 4)); }}
    top    {{ type wall;  faces ((3 7 6 2)); }}
    front  {{ type empty; faces ((0 3 2 1)); }}
    back   {{ type empty; faces ((4 5 6 7)); }}
);
mergePatchPairs ();
"""


def snappy_hex_mesh_dict(case: StudyCase) -> str:
    m = case.mesh
    near_h = 1.20 * case.H
    wake_h = 0.85 * case.H
    loc_x = domain(case)["xmin"] + 0.5 * D
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object snappyHexMeshDict;
}}
castellatedMesh true;
snap true;
addLayers true;
geometry
{{
    cylinder {{ type searchableCylinder; point1 (0 0 -0.010); point2 (0 0 0.010); radius {D/2.0:.6f}; }}
    nearCylinder {{ type searchableBox; min ({-2.5*D:.6f} {-near_h:.6f} -0.010); max ({6.0*D:.6f} {near_h:.6f} 0.010); }}
    wakeBox {{ type searchableBox; min (0 {-wake_h:.6f} -0.010); max ({12.0*D:.6f} {wake_h:.6f} 0.010); }}
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
    refinementSurfaces {{ cylinder {{ level ({m.surface_level} {m.surface_level}); patchInfo {{ type wall; }} }} }}
    refinementRegions {{ nearCylinder {{ mode inside; levels ((1e15 {m.near_level})); }} wakeBox {{ mode inside; levels ((1e15 {m.wake_level})); }} }}
    locationInMesh ({loc_x:.6f} 0 0);
    allowFreeStandingZoneFaces true;
}}
snapControls {{ nSmoothPatch 5; tolerance 2.0; nSolveIter 100; nRelaxIter 5; nFeatureSnapIter 10; implicitFeatureSnap true; explicitFeatureSnap false; multiRegionFeatureSnap false; }}
addLayersControls
{{
    relativeSizes true;
    expansionRatio {m.expansion_ratio:.3f};
    finalLayerThickness {m.final_layer_thickness:.3f};
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
    layers {{ cylinder {{ nSurfaceLayers {m.cylinder_layers}; }} top {{ nSurfaceLayers {m.wall_layers}; }} bottom {{ nSurfaceLayers {m.wall_layers}; }} }}
}}
meshQualityControls {{ maxNonOrtho 65; maxBoundarySkewness 20; maxInternalSkewness 4; maxConcave 80; minVol 1e-13; minTetQuality 1e-30; minArea -1; minTwist 0.02; minDeterminant 0.001; minFaceWeight 0.02; minVolRatio 0.01; minTriangleTwist -1; nSmoothScale 4; errorReduction 0.75; relaxed {{ maxNonOrtho 75; }} }}
writeFlags ( scalarLevels layerSets );
mergeTolerance 1e-6;
"""


def u_file(case: StudyCase) -> str:
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class volVectorField;
    object U;
}}
dimensions [0 1 -1 0 0 0 0];
internalField uniform ({case.u_max:.9f} 0 0);
boundaryField
{{
    inlet {{ type exprFixedValue; valueExpr "vector({case.u_max:.9f}*(1.0 - pow(2.0*pos().y()/{case.H:.9f}, 2.0)), 0, 0)"; value uniform (0 0 0); }}
    outlet   {{ type zeroGradient; }}
    top      {{ type noSlip; }}
    bottom   {{ type noSlip; }}
    cylinder {{ type noSlip; }}
    front    {{ type empty; }}
    back     {{ type empty; }}
}}
"""


def p_file() -> str:
    return """FoamFile
{
    version 2.0;
    format ascii;
    class volScalarField;
    object p;
}
dimensions [0 2 -2 0 0 0 0];
internalField uniform 0;
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


def set_expr_fields_dict(case: StudyCase) -> str:
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object setExprFieldsDict;
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
        #{{ vector({case.u_max:.9f}*(1.0 - pow(2.0*pos().y()/{case.H:.9f}, 2.0)), 0.002*exp(-pow((pos().x()-0.012)/0.010, 2.0)-pow((pos().y()-0.003)/{D:.9f}, 2.0)), 0) #}};
    }}
);
"""


def control_dict(case: StudyCase) -> str:
    return f"""FoamFile
{{
    version 2.0;
    format ascii;
    class dictionary;
    object controlDict;
}}
application pimpleFoam;
startFrom startTime;
startTime 0;
stopAt endTime;
endTime {case.end_time_s:.3f};
deltaT 1e-3;
adjustTimeStep yes;
maxCo 0.9;
writeControl runTime;
writeInterval 0.1;
writeFormat ascii;
writePrecision 10;
timeFormat general;
timePrecision 12;
runTimeModifiable true;
functions
{{
    forceCoeffs {{ type forceCoeffs; libs (forces); executeControl timeStep; executeInterval 1; writeControl timeStep; writeInterval 1; log yes; patches (cylinder); rho rhoInf; rhoInf {RHO:.6f}; CofR (0 0 0); liftDir (0 1 0); dragDir (1 0 0); pitchAxis (0 0 1); magUInf {case.u_max:.9f}; lRef {D:.6f}; Aref {D*SPAN:.9f}; }}
    residuals {{ type solverInfo; libs (utilityFunctionObjects); fields (U p); writeControl timeStep; writeInterval 1; }}
}}
"""


def fv_schemes() -> str:
    return "FoamFile\n{\n    version 2.0;\n    format ascii;\n    class dictionary;\n    object fvSchemes;\n}\nddtSchemes { default backward; }\ngradSchemes { default Gauss linear; grad(U) Gauss linear; }\ndivSchemes { default none; div(phi,U) Gauss linearUpwind grad(U); div((nuEff*dev2(T(grad(U))))) Gauss linear; }\nlaplacianSchemes { default Gauss linear corrected; }\ninterpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\nwallDist { method meshWave; }\n"


def fv_solution() -> str:
    return "FoamFile\n{\n    version 2.0;\n    format ascii;\n    class dictionary;\n    object fvSolution;\n}\nsolvers\n{\n    p { solver GAMG; smoother GaussSeidel; tolerance 1e-7; relTol 0.01; }\n    pFinal { $p; relTol 0; tolerance 1e-8; }\n    U { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0.05; }\n    UFinal { $U; relTol 0; tolerance 1e-9; }\n}\nPIMPLE\n{\n    nOuterCorrectors 1;\n    nCorrectors 2;\n    nNonOrthogonalCorrectors 1;\n    pRefCell 0;\n    pRefValue 0;\n}\nrelaxationFactors { equations { U 0.9; UFinal 1.0; } }\n"


def transport_properties() -> str:
    return f"FoamFile\n{{\n    version 2.0;\n    format ascii;\n    class dictionary;\n    object transportProperties;\n}}\ntransportModel Newtonian;\nnu {NU:.9e};\n"


def turbulence_properties() -> str:
    return "FoamFile\n{\n    version 2.0;\n    format ascii;\n    class dictionary;\n    object turbulenceProperties;\n}\nsimulationType laminar;\n"


def allrun_file() -> str:
    return '#!/bin/bash\n\nsource /home/kik/openfoam/OpenFOAM-v2512/etc/bashrc\nset -eo pipefail\ncd "$(dirname "$0")"\nrm -rf 0\ncp -r 0.orig 0\nmkdir -p logs\nblockMesh | tee logs/blockMesh.log\nsnappyHexMesh -overwrite | tee logs/snappyHexMesh.log\ncheckMesh | tee logs/checkMesh.log\nsetExprFields | tee logs/setExprFields.log\npimpleFoam | tee logs/pimpleFoam.log\n'


def write_input_md(case: StudyCase, target: Path) -> None:
    ref = so_ref(case.beta)
    lines = [
        f"# {case.name} input",
        "",
        f"- purpose = {case.purpose}",
        f"- beta = {case.beta:.4f}",
        f"- H_mm = {case.H*1000:.2f}",
        f"- Re = {case.reynolds:.1f}",
        f"- U_max_m_per_s = {case.u_max:.6f}",
        f"- U_bulk_m_per_s = {case.u_bulk:.6f}",
        f"- Re_crit_ref = {ref['Re_crit']}",
        f"- St_ref = {ref['St_crit']}",
        f"- interpolated_ref = {ref['interpolated']}",
        f"- source = {LITERATURE}",
    ]
    write_text(target, "\n".join(lines) + "\n", encoding="utf-8")


def write_case_matrix() -> None:
    lines = ["# V1 run 002 case matrix", "", f"- run name: {ACTIVE_RUN_NAME}", f"- working run root: `{RUN_ROOT}`", "", "| case | beta | Re | H [mm] | Re_crit_ref | St_ref | purpose |", "|---|---:|---:|---:|---:|---:|---|"]
    for case in CASES:
        ref = so_ref(case.beta)
        lines.append(f"| {case.name} | {case.beta:.3f} | {case.reynolds:.0f} | {case.H*1000:.2f} | {ref['Re_crit']} | {ref['St_crit']} | {case.purpose} |")
    write_text(ACTIVE_RUN_SETUP_DIR / "case_matrix.md", "\n".join(lines) + "\n", encoding="utf-8")


def write_study_plan() -> None:
    lines = ["# V1 run 002 study plan", "", "- Goal: direct comparison against Sahin and Owens with a Poiseuille inlet.", "- Direct literature points: beta = 0.30 and beta = 0.50.", "- Bridge case: beta = 0.375.", "", f"- source = {LITERATURE}", ""]
    write_text(STUDY_SUMMARY_DIR / "study_plan.md", "\n".join(lines) + "\n", encoding="utf-8")


def _rm_readonly(func, path, _):
    """Error handler for shutil.rmtree on Windows read-only files."""
    import os
    os.chmod(path, stat.S_IWRITE)
    func(path)


def replace_dir(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if dst.exists():
        shutil.rmtree(dst, onexc=_rm_readonly)
    shutil.copytree(src, dst)


def replace_file(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)


def sync_archive_from_working(case_name: str) -> None:
    case_dir = RUN_ROOT / case_name
    dst = sim_dir(case_name, create=True)
    for name in ("0.orig", "constant", "system"):
        replace_dir(case_dir / name, dst / "01_openfoam_setup" / name)
    for name in ("Allrun", "caseMeta.json", "input.md"):
        replace_file(case_dir / name, dst / "01_openfoam_setup" / name)
    replace_dir(case_dir / "postProcessing", dst / "02_raw_data" / "postProcessing")
    replace_dir(case_dir / "logs", dst / "05_logs" / "logs")


def write_case(case: StudyCase, overwrite: bool) -> None:
    case_dir = RUN_ROOT / case.name
    if case_dir.exists():
        if not overwrite:
            print(f"  skip {case.name} (exists)")
            return
        shutil.rmtree(case_dir)
    for name in ("0.orig", "constant", "system", "logs"):
        ensure_dir(case_dir / name)
    write_text(case_dir / "0.orig" / "U", u_file(case))
    write_text(case_dir / "0.orig" / "p", p_file())
    write_text(case_dir / "constant" / "transportProperties", transport_properties())
    write_text(case_dir / "constant" / "turbulenceProperties", turbulence_properties())
    write_text(case_dir / "system" / "blockMeshDict", block_mesh_dict(case))
    write_text(case_dir / "system" / "snappyHexMeshDict", snappy_hex_mesh_dict(case))
    write_text(case_dir / "system" / "controlDict", control_dict(case))
    write_text(case_dir / "system" / "fvSchemes", fv_schemes())
    write_text(case_dir / "system" / "fvSolution", fv_solution())
    write_text(case_dir / "system" / "setExprFieldsDict", set_expr_fields_dict(case))
    write_text(case_dir / "Allrun", allrun_file())
    write_text(case_dir / "caseMeta.json", json.dumps(metadata(case), indent=2) + "\n", encoding="utf-8")
    write_input_md(case, case_dir / "input.md")
    write_input_md(case, sim_dir(case.name, create=True) / "00_notes" / "input.md")
    sync_archive_from_working(case.name)
    print(f"  wrote {case.name}")


def parse_check_mesh(path: Path) -> dict[str, object]:
    result: dict[str, object] = {"status": "missing", "cells": None, "points": None, "faces": None, "max_non_ortho": None}
    if not path.exists():
        return result
    text = path.read_text(encoding="utf-8", errors="ignore")
    result["status"] = "ok" if "Mesh OK." in text else "warn"
    for key, pattern in {"points": r"points:\s+(\d+)", "faces": r"faces:\s+(\d+)", "cells": r"cells:\s+(\d+)", "max_non_ortho": r"Mesh non-orthogonality Max:\s+([0-9.eE+-]+)"}.items():
        match = re.search(pattern, text)
        if match:
            result[key] = int(match.group(1)) if key in {"points", "faces", "cells"} else float(match.group(1))
    return result


def coeff_paths(case_dir: Path) -> list[Path]:
    root = case_dir / "postProcessing" / "forceCoeffs"
    if not root.exists():
        return []
    pairs: list[tuple[float, Path]] = []
    for child in root.iterdir():
        coeff = child / "coefficient.dat"
        if child.is_dir() and coeff.exists():
            try:
                start = float(child.name)
            except ValueError:
                start = math.inf
            pairs.append((start, coeff))
    return [path for _, path in sorted(pairs, key=lambda item: item[0])]


def load_coeffs(paths: list[Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    merged: dict[float, tuple[float, float]] = {}
    for path in paths:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 5:
                    merged[float(parts[0])] = (float(parts[1]), float(parts[4]))
    ordered = sorted(merged.items())
    return (
        np.asarray([item[0] for item in ordered], dtype=float),
        np.asarray([item[1][0] for item in ordered], dtype=float),
        np.asarray([item[1][1] for item in ordered], dtype=float),
    )


def compute_metrics(case: StudyCase, time: np.ndarray, cd: np.ndarray, cl: np.ndarray) -> dict[str, object]:
    if time.size < 32:
        return {"status": "insufficient-data", "regime": "undetermined", "time_max_s": float(time.max()) if time.size else None, "Cd_mean": None, "Cd_std": None, "Cl_rms": None, "frequency_hz": None, "St": None}
    start = max(0.4 * float(time.max()), float(time.max()) - 4.0)
    mask = time >= start
    t_sel = time[mask]
    cd_sel = cd[mask]
    cl_sel = cl[mask]
    cd_mean = float(np.mean(cd_sel))
    cd_std = float(np.std(cd_sel))
    cl_centered = cl_sel - np.mean(cl_sel)
    cl_rms = float(np.sqrt(np.mean(cl_centered**2)))
    if t_sel.size < 32 or cl_rms < 1e-3:
        return {"status": "ok", "regime": "steady-or-weakly-unsteady", "time_max_s": float(time.max()), "Cd_mean": cd_mean, "Cd_std": cd_std, "Cl_rms": cl_rms, "frequency_hz": None, "St": None}
    dt = float(np.mean(np.diff(t_sel)))
    nfft = 1
    while nfft < cl_centered.size * 8:
        nfft *= 2
    freqs = np.fft.rfftfreq(nfft, d=dt)
    amps = np.abs(np.fft.rfft(cl_centered * np.hanning(cl_centered.size), n=nfft))
    valid = (freqs > 0.0) & (freqs < 20.0)
    freqs = freqs[valid]
    amps = amps[valid]
    peak = int(np.argmax(amps))
    freq = float(freqs[peak])
    if 0 < peak < freqs.size - 1:
        a, b, g = amps[peak - 1], amps[peak], amps[peak + 1]
        denom = a - 2.0 * b + g
        if abs(denom) > 1e-12:
            freq += float(0.5 * (a - g) / denom * (freqs[1] - freqs[0]))
    return {"status": "ok", "regime": "periodic", "time_max_s": float(time.max()), "Cd_mean": cd_mean, "Cd_std": cd_std, "Cl_rms": cl_rms, "frequency_hz": freq, "St": float(freq * D / case.u_max)}


def plot_cl(case_name: str, time: np.ndarray, cl: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(10, 4), dpi=160)
    ax.plot(time, cl, lw=0.9, color="#0b5ed7")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Cl [-]")
    ax.set_title(f"{case_name}: Cl(t)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(sim_dir(case_name, create=True) / "04_plots" / "Cl_vs_time.png")
    plt.close(fig)


def write_output_md(case: StudyCase, mesh_info: dict[str, object], metrics: dict[str, object]) -> None:
    ref = so_ref(case.beta)
    delta_st = None
    if metrics["St"] is not None and ref["St_crit"] not in (None, 0):
        delta_st = 100.0 * (float(metrics["St"]) - float(ref["St_crit"])) / float(ref["St_crit"])
    lines = [
        f"# {case.name} output",
        "",
        f"- regime = {metrics['regime']}",
        f"- status = {metrics['status']}",
        f"- cells = {mesh_info['cells']}",
        f"- Cd_mean = {metrics['Cd_mean']}",
        f"- Cl_rms = {metrics['Cl_rms']}",
        f"- frequency_hz = {metrics['frequency_hz']}",
        f"- St_sim = {metrics['St']}",
        f"- Re_crit_ref = {ref['Re_crit']}",
        f"- St_ref = {ref['St_crit']}",
        f"- delta_St_percent = {delta_st}",
        f"- source = {LITERATURE}",
    ]
    write_text(sim_dir(case.name, create=True) / "00_notes" / "output.md", "\n".join(lines) + "\n", encoding="utf-8")


def write_summary(rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0].keys())
    targets = (ACTIVE_RUN_SUMMARY_DIR, STUDY_SUMMARY_DIR)
    for target in targets:
        ensure_dir(target)
        with (target / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        lines = ["# V1 run 002 summary", "", "| case | beta | Re | cells | regime | Cd_mean | Cl_rms | f [Hz] | St_sim | Re_crit_ref | St_ref | dSt [%] | status |", "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|"]
        for row in rows:
            lines.append(f"| {row['case']} | {row['beta']} | {row['Re']} | {row['cells']} | {row['regime']} | {row['Cd_mean']} | {row['Cl_rms']} | {row['frequency_hz']} | {row['St_sim']} | {row['so_Re_crit']} | {row['so_St_crit']} | {row['delta_St_percent']} | {row['status']} |")
        write_text(target / "summary.md", "\n".join(lines) + "\n", encoding="utf-8")


def write_comparison(rows: list[dict[str, object]]) -> None:
    selected = [row for row in rows if row["St_sim"] is not None]
    if not selected:
        return
    fields = ["case", "beta", "Re", "regime", "St_sim", "so_Re_crit", "so_St_crit", "delta_St_percent"]
    for target in (ACTIVE_RUN_SUMMARY_DIR, STUDY_SUMMARY_DIR):
        with (target / "comparison_vs_sahin_owens.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in selected:
                writer.writerow({field: row[field] for field in fields})


def plot_st_vs_reference(rows: list[dict[str, object]]) -> None:
    periodic = [row for row in rows if row["St_sim"] is not None]
    if not periodic:
        return
    fig, ax = plt.subplots(figsize=(8.5, 5.0), dpi=180)
    colors = {0.30: "#0b5ed7", 0.375: "#6c757d", 0.50: "#dc3545"}
    for beta in sorted({float(row["beta"]) for row in periodic}):
        group = sorted([row for row in periodic if float(row["beta"]) == beta], key=lambda item: float(item["Re"]))
        ax.plot([float(item["Re"]) for item in group], [float(item["St_sim"]) for item in group], marker="o", lw=1.2, color=colors.get(beta, "#333333"), label=f"beta={beta:.3f} sim")
        ref = so_ref(beta)
        ax.scatter([float(ref["Re_crit"])], [float(ref["St_crit"])], marker="x", s=70, linewidths=2.0, color=colors.get(beta, "#333333"), label=f"beta={beta:.3f} ref")
    ax.set_xlabel("Re = U_max D / nu")
    ax.set_ylabel("St = f D / U_max")
    ax.set_title("V1 run 002: Strouhal number vs Sahin and Owens")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    for target in (ACTIVE_RUN_PUBLICATION_DIR / "figures", PUBLICATION_DIR / "figures", STUDY_PLOTS_DIR):
        ensure_dir(target)
        fig.savefig(target / "V1_run002_St_vs_SahinOwens.png")
        fig.savefig(target / "V1_run002_St_vs_SahinOwens.svg")
    plt.close(fig)


def prepare(names: list[str], overwrite: bool) -> None:
    ensure_dir(RUN_ROOT)
    ensure_active_run()
    write_case_matrix()
    write_study_plan()
    write_text(ACTIVE_RUN_SETUP_DIR / "runtime_locations.md", f"# Runtime locations\n\n- working run root: `{RUN_ROOT}`\n- archive run dir: `{ACTIVE_RUN_DIR}`\n- study summary dir: `{STUDY_SUMMARY_DIR}`\n", encoding="utf-8")
    for case in resolve_cases(names):
        write_case(case, overwrite)
    write_text(STUDY_SUMMARY_DIR / "manifest.json", json.dumps({"run_root": str(RUN_ROOT), "cases": [metadata(case) for case in CASES]}, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared cases in {RUN_ROOT}")


def analyze(names: list[str]) -> None:
    ensure_active_run()
    rows: list[dict[str, object]] = []
    for case in resolve_cases(names):
        case_dir = RUN_ROOT / case.name
        sync_archive_from_working(case.name)
        mesh_info = parse_check_mesh(case_dir / "logs" / "checkMesh.log")
        paths = coeff_paths(case_dir)
        if paths:
            time, cd, cl = load_coeffs(paths)
            metrics = compute_metrics(case, time, cd, cl)
            if time.size:
                plot_cl(case.name, time, cl)
        else:
            metrics = {"status": "missing-force-data", "regime": "not-run-or-failed", "time_max_s": None, "Cd_mean": None, "Cd_std": None, "Cl_rms": None, "frequency_hz": None, "St": None}
        ref = so_ref(case.beta)
        delta = None
        if metrics["St"] is not None and ref["St_crit"] not in (None, 0):
            delta = round(100.0 * (float(metrics["St"]) - float(ref["St_crit"])) / float(ref["St_crit"]), 3)
        row = {"case": case.name, "beta": case.beta, "Re": case.reynolds, "cells": mesh_info["cells"], "regime": metrics["regime"], "Cd_mean": metrics["Cd_mean"], "Cl_rms": metrics["Cl_rms"], "frequency_hz": metrics["frequency_hz"], "St_sim": metrics["St"], "so_Re_crit": ref["Re_crit"], "so_St_crit": ref["St_crit"], "delta_St_percent": delta, "status": metrics["status"]}
        rows.append(row)
        write_text(sim_dir(case.name, create=True) / "03_processed_data" / "summary.json", json.dumps({"metadata": metadata(case), "mesh": mesh_info, "metrics": metrics, "comparison": row}, indent=2) + "\n", encoding="utf-8")
        write_output_md(case, mesh_info, metrics)
        print(f"  {case.name}: regime={metrics['regime']}, St={metrics['St']}")
    if rows:
        write_summary(rows)
        write_comparison(rows)
        plot_st_vs_reference(rows)
        print(f"Summary written to {ACTIVE_RUN_SUMMARY_DIR}")


def compare(names: list[str]) -> None:
    path = ACTIVE_RUN_SUMMARY_DIR / "comparison_vs_sahin_owens.csv"
    if not path.exists():
        print("No comparison file found. Run analyze first.")
        return
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    selected = set(names) if names else None
    header = f"{'case':<24} {'beta':>6} {'Re':>6} {'regime':<24} {'St_sim':>9} {'St_ref':>9} {'dSt%':>8}"
    print(header)
    print("-" * len(header))
    for row in rows:
        if selected and row["case"] not in selected:
            continue
        print(f"{row['case']:<24} {float(row['beta']):>6.3f} {float(row['Re']):>6.0f} {row['regime']:<24} {str(row['St_sim']):>9} {str(row['so_St_crit']):>9} {str(row['delta_St_percent']):>8}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Usage: python _code/V1Run2Study.py prepare|analyze|compare|run [case_name] [--overwrite]")
        return
    cmd = args[0]
    rest = [arg for arg in args[1:] if not arg.startswith("--")]
    overwrite = "--overwrite" in args
    if cmd == "prepare":
        prepare(rest, overwrite)
    elif cmd == "analyze":
        analyze(rest)
    elif cmd == "compare":
        compare(rest)
    elif cmd == "run":
        if not rest:
            raise SystemExit("Usage: _code/V1Run2Study.py run <case_name>")
        prepare(rest, overwrite=True)
        subprocess.run(["bash", "Allrun"], cwd=RUN_ROOT / rest[0], check=True)
        analyze(rest)
        compare(rest)
    else:
        raise SystemExit(f"Unknown command '{cmd}'.")


if __name__ == "__main__":
    main()
