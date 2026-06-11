"""V2_confined study — confined cylinder, Poiseuille inlet, β ∈ {0.30, 0.375, 0.50}.

Usage (from WSL with OpenFOAM sourced):
    python V2Study.py prepare            # write all case dirs to RUN_ROOT
    python V2Study.py prepare b030_medium_Re080   # single case
    python V2Study.py prepare --overwrite         # force-recreate
    python V2Study.py analyze            # read results, write summary.csv
    python V2Study.py compare            # print Sahin & Owens comparison table
    python V2Study.py run b030_medium_Re080       # prepare + Allrun

Definitions (matching Sahin & Owens 2004, Phys. Fluids 16, 1305):
    Re = U_max * D / ν       (U_max = centreline velocity of Poiseuille inlet)
    St = f * D / U_max
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
import math
import re
import shutil
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_CASE = Path(__file__).resolve().parent
RUN_ROOT = Path(r"C:\openfoam-case\VV_cases\V2_confined")
RESULTS_ROOT = REPO_CASE / "results" / "study_v2"
RUNS_RESULTS_ROOT = RESULTS_ROOT / "runs"
PLOTS_DIR = RESULTS_ROOT / "plots"

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
D = 0.012        # cylinder diameter [m]
NU = 1.516e-5    # kinematic viscosity, air [m²/s]
RHO = 1.205      # density [kg/m³]
SPAN = 0.01      # z-span for 2-D (empty) [m]
Z_MIN = -SPAN / 2.0
Z_MAX = SPAN / 2.0

UP_D = 8.0    # upstream length [D]
DOWN_D = 20.0  # downstream length [D]

# ---------------------------------------------------------------------------
# Sahin & Owens (2004) Table IV reference — curve AC (primary Hopf), mesh M2
# Re = U_max·D/ν,  St = f·D/U_max
# ---------------------------------------------------------------------------
SAHIN_OWENS = {
    0.10: {"Re_crit": 50.81,  "St_crit": 0.1210},
    0.20: {"Re_crit": 69.43,  "St_crit": 0.1566},
    0.30: {"Re_crit": 94.56,  "St_crit": 0.2090},
    0.50: {"Re_crit": 124.09, "St_crit": 0.3393},
    0.70: {"Re_crit": 110.29, "St_crit": 0.4752},
    0.80: {"Re_crit": 110.24, "St_crit": 0.5363},
    0.84: {"Re_crit": 113.69, "St_crit": 0.5568},
}

LITERATURE = "Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305–1320, doi:10.1063/1.1668285"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
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
    beta: float          # blockage ratio D/H
    reynolds: float      # Re = U_max·D/ν
    upstream_D: float
    downstream_D: float
    mesh: MeshVariant
    end_time_s: float

    @property
    def H(self) -> float:
        """Channel height [m]."""
        return D / self.beta

    @property
    def half_H(self) -> float:
        return self.H / 2.0

    @property
    def u_max(self) -> float:
        """Centreline (peak) inlet velocity [m/s]."""
        return self.reynolds * NU / D

    @property
    def u_bulk(self) -> float:
        """Bulk (mean) velocity for Poiseuille profile [m/s] = (2/3)·U_max."""
        return (2.0 / 3.0) * self.u_max


MESHES = {
    "coarse": MeshVariant("coarse", 0.0030, 2, 1, 1, 4, 1, 0.20, 1.25),
    "medium": MeshVariant("medium", 0.0025, 3, 2, 1, 6, 2, 0.25, 1.20),
    "fine":   MeshVariant("fine",   0.0020, 4, 3, 2, 8, 4, 0.30, 1.20),
}

# ---------------------------------------------------------------------------
# Cases: β ∈ {0.30, 0.375, 0.50}
#   Re values chosen to bracket Re_crit for each β.
#   β = 0.30  → Re_crit = 94.56  (Sahin & Owens, direct comparison)
#   β = 0.375 → Re_crit ≈ 109    (interpolated; actual fin-and-tube geometry)
#   β = 0.50  → Re_crit = 124.09 (Sahin & Owens, direct comparison)
# ---------------------------------------------------------------------------
CASES = [
    # --- β = 0.30 -------------------------------------------------------
    StudyCase("b030_medium_Re080", "β=0.30 below Re_crit (should be steady)",
              0.30, 80.0,  UP_D, DOWN_D, MESHES["medium"], 5.0),
    StudyCase("b030_medium_Re095", "β=0.30 just above Re_crit",
              0.30, 95.0,  UP_D, DOWN_D, MESHES["medium"], 5.0),
    StudyCase("b030_medium_Re100", "β=0.30 above Re_crit, St reference",
              0.30, 100.0, UP_D, DOWN_D, MESHES["medium"], 5.0),
    StudyCase("b030_medium_Re120", "β=0.30 well above Re_crit",
              0.30, 120.0, UP_D, DOWN_D, MESHES["medium"], 5.0),

    # --- β = 0.375  (D/Pt, actual fin-and-tube pitch) -------------------
    StudyCase("b0375_medium_Re090", "β=0.375 below interpolated Re_crit",
              0.375, 90.0,  UP_D, DOWN_D, MESHES["medium"], 5.0),
    StudyCase("b0375_medium_Re110", "β=0.375 near interpolated Re_crit",
              0.375, 110.0, UP_D, DOWN_D, MESHES["medium"], 5.0),
    StudyCase("b0375_medium_Re120", "β=0.375 above interpolated Re_crit",
              0.375, 120.0, UP_D, DOWN_D, MESHES["medium"], 5.0),
    StudyCase("b0375_medium_Re135", "β=0.375 well above Re_crit",
              0.375, 135.0, UP_D, DOWN_D, MESHES["medium"], 5.0),

    # --- β = 0.50 -------------------------------------------------------
    StudyCase("b050_medium_Re100", "β=0.50 below Re_crit (should be steady)",
              0.50, 100.0, UP_D, DOWN_D, MESHES["medium"], 5.0),
    StudyCase("b050_medium_Re120", "β=0.50 below Re_crit",
              0.50, 120.0, UP_D, DOWN_D, MESHES["medium"], 5.0),
    StudyCase("b050_medium_Re130", "β=0.50 just above Re_crit",
              0.50, 130.0, UP_D, DOWN_D, MESHES["medium"], 5.0),
    StudyCase("b050_medium_Re150", "β=0.50 well above Re_crit",
              0.50, 150.0, UP_D, DOWN_D, MESHES["medium"], 5.0),
]
CASE_MAP = {c.name: c for c in CASES}


# ---------------------------------------------------------------------------
# File generators
# ---------------------------------------------------------------------------
def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _domain(case: StudyCase) -> dict[str, float]:
    xmin = -case.upstream_D * D
    xmax = case.downstream_D * D
    return {"xmin": xmin, "xmax": xmax, "length": xmax - xmin}


def _base_counts(case: StudyCase) -> tuple[int, int]:
    d = _domain(case)
    nx = max(120, int(round(d["length"] / case.mesh.base_dx)))
    ny = max(8, int(round(case.H / case.mesh.base_dx)))
    return nx, ny


def block_mesh_dict(case: StudyCase) -> str:
    d = _domain(case)
    nx, ny = _base_counts(case)
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

// V2_confined  beta={case.beta:.4f}  H={case.H*1000:.1f} mm
// upstream={case.upstream_D:.0f}D  downstream={case.downstream_D:.0f}D
// base mesh {nx} x {ny} x 1  (dx ~ {case.mesh.base_dx*1000:.1f} mm)

scale 1;

vertices
(
    ({d['xmin']:.6f} {-case.half_H:.6f} {Z_MIN:.6f})
    ({d['xmax']:.6f} {-case.half_H:.6f} {Z_MIN:.6f})
    ({d['xmax']:.6f} {case.half_H:.6f} {Z_MIN:.6f})
    ({d['xmin']:.6f} {case.half_H:.6f} {Z_MIN:.6f})
    ({d['xmin']:.6f} {-case.half_H:.6f} {Z_MAX:.6f})
    ({d['xmax']:.6f} {-case.half_H:.6f} {Z_MAX:.6f})
    ({d['xmax']:.6f} {case.half_H:.6f} {Z_MAX:.6f})
    ({d['xmin']:.6f} {case.half_H:.6f} {Z_MAX:.6f})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1)
);

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
    near_xmin = -2.5 * D
    near_xmax = 6.0 * D
    near_h = 1.20 * case.H
    wake_xmin = 0.0
    wake_xmax = 12.0 * D
    wake_h = 0.85 * case.H
    loc_x = _domain(case)["xmin"] + 0.5 * D
    m = case.mesh
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
        point2 (0 0  0.010);
        radius {D / 2.0:.6f};
    }}
    nearCylinder
    {{
        type searchableBox;
        min ({near_xmin:.6f} {-near_h:.6f} -0.010);
        max ({near_xmax:.6f}  {near_h:.6f}  0.010);
    }}
    wakeBox
    {{
        type searchableBox;
        min ({wake_xmin:.6f} {-wake_h:.6f} -0.010);
        max ({wake_xmax:.6f}  {wake_h:.6f}  0.010);
    }}
}}

castellatedMeshControls
{{
    maxLocalCells  600000;
    maxGlobalCells 2400000;
    minRefinementCells 0;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;
    resolveFeatureAngle 30;
    features ();
    refinementSurfaces
    {{
        cylinder {{ level ({m.surface_level} {m.surface_level}); patchInfo {{ type wall; }} }}
    }}
    refinementRegions
    {{
        nearCylinder {{ mode inside; levels ((1e15 {m.near_level})); }}
        wakeBox      {{ mode inside; levels ((1e15 {m.wake_level})); }}
    }}
    locationInMesh ({loc_x:.6f} 0 0);
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
    layers
    {{
        cylinder {{ nSurfaceLayers {m.cylinder_layers}; }}
        top      {{ nSurfaceLayers {m.wall_layers}; }}
        bottom   {{ nSurfaceLayers {m.wall_layers}; }}
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
    """Poiseuille inlet: u(y) = U_max * (1 - (2y/H)^2)."""
    uc = case.u_max
    H = case.H
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}

// V2_confined  beta={case.beta:.4f}  Re={case.reynolds:.1f}
// Inlet: Poiseuille profile, Re = U_max*D/nu (Sahin & Owens convention)
// U_max = {uc:.9f} m/s,  U_bulk = {case.u_bulk:.9f} m/s

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({uc:.9f} 0 0);

boundaryField
{{
    inlet
    {{
        type        exprFixedValue;
        valueExpr   "vector({uc:.9f}*(1.0 - pow(2.0*pos().y()/{H:.9f}, 2.0)), 0, 0)";
        value       uniform (0 0 0);
    }}
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
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}

dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet    { type zeroGradient; }
    outlet   { type fixedValue; value uniform 0; }
    top      { type zeroGradient; }
    bottom   { type zeroGradient; }
    cylinder { type zeroGradient; }
    front    { type empty; }
    back     { type empty; }
}
"""


def set_expr_fields_dict(case: StudyCase) -> str:
    """Perturb initial field to help trigger instability near onset."""
    uc = case.u_max
    H = case.H
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
        #{{
            vector(
                {uc:.9f}*(1.0 - pow(2.0*pos().y()/{H:.9f}, 2.0)),
                0.002*exp(-pow((pos().x()-0.012)/0.010, 2.0)
                          -pow((pos().y()-0.003)/{D:.9f}, 2.0)),
                0
            )
        #}};
    }}
);
"""


def control_dict(case: StudyCase) -> str:
    uc = case.u_max
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
writeInterval   0.1;
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
        type            forceCoeffs;
        libs            (forces);
        executeControl  timeStep;
        executeInterval 1;
        writeControl    timeStep;
        writeInterval   1;
        log             yes;
        patches         (cylinder);
        rho             rhoInf;
        rhoInf          {RHO:.6f};
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         {uc:.9f};
        lRef            {D:.6f};
        Aref            {D * SPAN:.9f};
    }}
    residuals
    {{
        type            solverInfo;
        libs            (utilityFunctionObjects);
        fields          (U p);
        writeControl    timeStep;
        writeInterval   1;
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

ddtSchemes      { default backward; }
gradSchemes     { default Gauss linear; grad(U) Gauss linear; }
divSchemes
{
    default     none;
    div(phi,U)  Gauss linearUpwind grad(U);
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
wallDist        { method meshWave; }
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
    p     { solver GAMG; smoother GaussSeidel; tolerance 1e-7; relTol 0.01; }
    pFinal { $p; relTol 0; tolerance 1e-8; }
    U     { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0.05; }
    UFinal { $U; relTol 0; tolerance 1e-9; }
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
    equations { U 0.9; UFinal 1.0; }
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


def allrun_file() -> str:
    return """#!/bin/bash

source /home/kik/openfoam/OpenFOAM-v2512/etc/bashrc
set -eo pipefail
cd "$(dirname "$0")"
rm -rf 0
cp -r 0.orig 0
mkdir -p logs
blockMesh          | tee logs/blockMesh.log
snappyHexMesh -overwrite | tee logs/snappyHexMesh.log
checkMesh          | tee logs/checkMesh.log
setExprFields      | tee logs/setExprFields.log
pimpleFoam         | tee logs/pimpleFoam.log
"""


# ---------------------------------------------------------------------------
# Metadata / documentation
# ---------------------------------------------------------------------------
def _so_ref(beta: float) -> dict[str, object]:
    """Nearest Sahin & Owens reference point(s) for a given beta."""
    exact = SAHIN_OWENS.get(beta)
    if exact:
        return {"beta_ref": beta, "Re_crit": exact["Re_crit"],
                "St_crit": exact["St_crit"], "interpolated": False}
    betas = sorted(SAHIN_OWENS.keys())
    lo = max((b for b in betas if b <= beta), default=None)
    hi = min((b for b in betas if b >= beta), default=None)
    if lo is None or hi is None:
        return {"beta_ref": None, "Re_crit": None, "St_crit": None, "interpolated": True}
    t = (beta - lo) / (hi - lo)
    Re_crit = SAHIN_OWENS[lo]["Re_crit"] * (1 - t) + SAHIN_OWENS[hi]["Re_crit"] * t
    St_crit = SAHIN_OWENS[lo]["St_crit"] * (1 - t) + SAHIN_OWENS[hi]["St_crit"] * t
    return {"beta_ref": f"{lo}–{hi} (interp.)", "Re_crit": round(Re_crit, 2),
            "St_crit": round(St_crit, 4), "interpolated": True}


def metadata(case: StudyCase) -> dict[str, object]:
    d = _domain(case)
    nx, ny = _base_counts(case)
    ref = _so_ref(case.beta)
    return {
        "case": case.name,
        "purpose": case.purpose,
        "beta": case.beta,
        "reynolds": case.reynolds,
        "u_max_m_per_s": case.u_max,
        "u_bulk_m_per_s": case.u_bulk,
        "diameter_m": D,
        "channel_height_m": case.H,
        "mesh": case.mesh.name,
        "upstream_D": case.upstream_D,
        "downstream_D": case.downstream_D,
        "base_nx": nx,
        "base_ny": ny,
        "end_time_s": case.end_time_s,
        "x_min_m": d["xmin"],
        "x_max_m": d["xmax"],
        "so_Re_crit": ref["Re_crit"],
        "so_St_crit": ref["St_crit"],
        "so_interpolated": ref["interpolated"],
    }


def write_input_md(case: StudyCase, target: Path) -> None:
    ref = _so_ref(case.beta)
    lines = [
        f"# {case.name} input",
        "",
        "## Purpose",
        f"- {case.purpose}",
        "",
        "## Geometry",
        f"- D = {D*1000:.1f} mm",
        f"- β = D/H = {case.beta:.4f}",
        f"- H = {case.H*1000:.2f} mm",
        f"- upstream = {case.upstream_D:.0f}D,  downstream = {case.downstream_D:.0f}D",
        "",
        "## Flow",
        f"- Re = {case.reynolds:.1f}  (= U_max·D/ν, Sahin & Owens convention)",
        f"- U_max = {case.u_max:.6f} m/s",
        f"- U_bulk = {case.u_bulk:.6f} m/s  (= 2/3 · U_max for Poiseuille)",
        "- inlet: Poiseuille  u(y) = U_max·(1 − (2y/H)²)",
        "- top / bottom: no-slip wall",
        "- cylinder: no-slip",
        "",
        "## Sahin & Owens reference",
        f"- Re_crit = {ref['Re_crit']}  {'(interpolated)' if ref['interpolated'] else '(Table IV, M2)'}",
        f"- St_crit = {ref['St_crit']}",
        f"- source: {LITERATURE}",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Case writing
# ---------------------------------------------------------------------------
def write_case(case: StudyCase, overwrite: bool) -> None:
    case_dir = RUN_ROOT / case.name
    if case_dir.exists():
        if not overwrite:
            print(f"  skip {case.name} (exists, use --overwrite)")
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

    repo_dir = RUNS_RESULTS_ROOT / case.name
    ensure_dir(repo_dir)
    write_input_md(case, repo_dir / "input.md")

    print(f"  wrote {case.name}  (β={case.beta}, Re={case.reynolds})")


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------
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
    return [p for _, p in sorted(paths, key=lambda x: x[0])]


def load_coeffs(paths: list[Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    merged: dict[float, tuple[float, float]] = {}
    for path in paths:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                parts = s.split()
                if len(parts) < 5:
                    continue
                merged[float(parts[0])] = (float(parts[1]), float(parts[4]))
    ordered = sorted(merged.items())
    t   = np.asarray([r[0]    for r in ordered], dtype=float)
    cd  = np.asarray([r[1][0] for r in ordered], dtype=float)
    cl  = np.asarray([r[1][1] for r in ordered], dtype=float)
    return t, cd, cl


def parse_check_mesh(log: Path) -> dict[str, object]:
    res: dict[str, object] = {
        "status": "missing", "cells": None, "max_non_ortho": None}
    if not log.exists():
        return res
    text = log.read_text(encoding="utf-8", errors="ignore")
    res["status"] = "ok" if "Mesh OK." in text else "warn"
    m = re.search(r"cells:\s+(\d+)", text)
    if m:
        res["cells"] = int(m.group(1))
    m = re.search(r"Mesh non-orthogonality Max:\s+([0-9.eE+-]+)", text)
    if m:
        res["max_non_ortho"] = float(m.group(1))
    return res


def compute_metrics(case: StudyCase, time: np.ndarray,
                    cd: np.ndarray, cl: np.ndarray) -> dict[str, object]:
    if time.size < 32:
        return {"status": "insufficient-data", "regime": "undetermined",
                "time_max_s": None, "Cd_mean": None, "Cl_rms": None,
                "frequency_hz": None, "St": None}

    start = max(0.4 * float(time.max()), float(time.max()) - 4.0)
    mask  = time >= start
    t_sel = time[mask]
    cd_sel = cd[mask]
    cl_sel = cl[mask]
    cd_mean = float(np.mean(cd_sel))
    cl_c    = cl_sel - np.mean(cl_sel)
    cl_rms  = float(np.sqrt(np.mean(cl_c**2)))

    if cl_rms < 1e-3:
        return {"status": "ok", "regime": "steady", "analysis_start_s": start,
                "time_max_s": float(time.max()), "Cd_mean": cd_mean,
                "Cl_rms": cl_rms, "frequency_hz": None, "St": None}

    dt   = float(np.mean(np.diff(t_sel)))
    nfft = 1
    while nfft < cl_c.size * 8:
        nfft *= 2
    win   = np.hanning(cl_c.size)
    freqs = np.fft.rfftfreq(nfft, d=dt)
    amps  = np.abs(np.fft.rfft(cl_c * win, n=nfft))
    valid = (freqs > 0) & (freqs < 20.0)
    f_v, a_v = freqs[valid], amps[valid]
    pk = int(np.argmax(a_v))
    freq = float(f_v[pk])
    if 0 < pk < f_v.size - 1:
        a, b, g = a_v[pk-1], a_v[pk], a_v[pk+1]
        denom = a - 2*b + g
        if abs(denom) > 1e-12:
            freq += 0.5 * (a - g) / denom * (f_v[1] - f_v[0])

    St = freq * D / case.u_max   # f·D/U_max — matches Sahin & Owens

    return {"status": "ok", "regime": "periodic", "analysis_start_s": start,
            "time_max_s": float(time.max()), "Cd_mean": cd_mean,
            "Cl_rms": cl_rms, "frequency_hz": freq, "St": float(St)}


def plot_cl(name: str, time: np.ndarray, cl: np.ndarray) -> None:
    ensure_dir(PLOTS_DIR)
    fig, ax = plt.subplots(figsize=(10, 4), dpi=150)
    ax.plot(time, cl, lw=0.8, color="#0b5ed7")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Cl [−]")
    ax.set_title(name)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / f"{name}_Cl.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Study-level routines
# ---------------------------------------------------------------------------
def resolve_cases(names: list[str]) -> list[StudyCase]:
    if not names:
        return CASES
    out = []
    for n in names:
        if n not in CASE_MAP:
            raise SystemExit(f"Unknown case '{n}'. Available: {list(CASE_MAP)}")
        out.append(CASE_MAP[n])
    return out


def prepare(names: list[str], overwrite: bool) -> None:
    ensure_dir(RUN_ROOT)
    ensure_dir(RESULTS_ROOT)
    ensure_dir(RUNS_RESULTS_ROOT)
    ensure_dir(PLOTS_DIR)

    # study plan
    lines = [
        "# V2_confined Study Plan",
        "",
        "Goal: verify solver against Sahin & Owens (2004) at β=0.30 and β=0.50,",
        "      and characterise the actual fin-and-tube geometry at β=0.375.",
        "",
        "Re convention: Re = U_max·D/ν  (Poiseuille centreline, same as reference).",
        "",
        f"Reference: {LITERATURE}",
        "",
        "| case | β | Re | Re_crit (SO) | St_crit (SO) | mesh | end_time |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for c in CASES:
        ref = _so_ref(c.beta)
        lines.append(
            f"| {c.name} | {c.beta} | {c.reynolds:.0f} | "
            f"{ref['Re_crit']} | {ref['St_crit']} | {c.mesh.name} | {c.end_time_s}s |"
        )
    (RESULTS_ROOT / "study_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    for case in resolve_cases(names):
        write_case(case, overwrite)

    (RESULTS_ROOT / "manifest.json").write_text(
        json.dumps({"run_root": str(RUN_ROOT),
                    "cases": [metadata(c) for c in CASES]}, indent=2),
        encoding="utf-8",
    )
    print(f"\nRun root: {RUN_ROOT}")


def analyze(names: list[str]) -> None:
    ensure_dir(RESULTS_ROOT)
    ensure_dir(RUNS_RESULTS_ROOT)
    ensure_dir(PLOTS_DIR)

    rows: list[dict[str, object]] = []
    for case in resolve_cases(names):
        case_dir = RUN_ROOT / case.name
        mesh_info = parse_check_mesh(case_dir / "logs" / "checkMesh.log")
        paths = coeff_paths(case_dir)
        if not paths:
            print(f"  {case.name}: no coefficient data")
            m = {"regime": "no-data", "Cd_mean": None, "Cl_rms": None,
                 "frequency_hz": None, "St": None, "time_max_s": None}
        else:
            time, cd, cl = load_coeffs(paths)
            m = compute_metrics(case, time, cd, cl)
            if time.size:
                plot_cl(case.name, time, cl)

        ref = _so_ref(case.beta)
        row = {
            "case":        case.name,
            "beta":        case.beta,
            "Re":          case.reynolds,
            "mesh":        case.mesh.name,
            "cells":       mesh_info["cells"],
            "regime":      m["regime"],
            "Cd_mean":     m["Cd_mean"],
            "Cl_rms":      m["Cl_rms"],
            "frequency_hz": m["frequency_hz"],
            "St_sim":      m["St"],
            "so_Re_crit":  ref["Re_crit"],
            "so_St_crit":  ref["St_crit"],
            "time_max_s":  m["time_max_s"],
        }
        rows.append(row)
        print(f"  {case.name}: regime={m['regime']}, St={m['St']}")

        repo_dir = RUNS_RESULTS_ROOT / case.name
        ensure_dir(repo_dir)
        (repo_dir / "output.json").write_text(
            json.dumps({**metadata(case), **m, **mesh_info}, indent=2), encoding="utf-8")

    if rows:
        fieldnames = list(rows[0].keys())
        csv_path = RESULTS_ROOT / "summary.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nSummary: {csv_path}")


def compare(names: list[str]) -> None:
    """Print a Sahin & Owens comparison table for cases that have results."""
    csv_path = RESULTS_ROOT / "summary.csv"
    if not csv_path.exists():
        print("No summary.csv found — run 'analyze' first.")
        return

    with csv_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    filter_names = set(names) if names else None

    header = (
        f"{'case':<26} {'β':>5} {'Re':>6} {'Re_crit(SO)':>12} "
        f"{'regime':<24} {'St_sim':>8} {'St_crit(SO)':>12} {'ΔSt%':>7}"
    )
    print("\nSahin & Owens (2004) comparison — V2_confined")
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    for r in rows:
        if filter_names and r["case"] not in filter_names:
            continue
        st_sim  = float(r["St_sim"]) if r["St_sim"] not in ("", "None") else None
        st_ref  = float(r["so_St_crit"]) if r["so_St_crit"] not in ("", "None") else None
        delta   = f"{100*(st_sim - st_ref)/st_ref:+.1f}" if (st_sim and st_ref) else "—"
        st_s    = f"{st_sim:.4f}" if st_sim else "—"
        st_r    = f"{st_ref:.4f}" if st_ref else "—"
        re_c    = r["so_Re_crit"] if r["so_Re_crit"] not in ("", "None") else "—"
        print(
            f"{r['case']:<26} {float(r['beta']):>5.3f} {float(r['Re']):>6.0f} "
            f"{re_c:>12} {r['regime']:<24} {st_s:>8} {st_r:>12} {delta:>7}"
        )
    print("=" * len(header))
    print(f"Reference: {LITERATURE}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0]
    rest = [a for a in args[1:] if not a.startswith("--")]
    overwrite = "--overwrite" in args

    if cmd == "prepare":
        prepare(rest, overwrite)
    elif cmd == "analyze":
        analyze(rest)
    elif cmd == "compare":
        compare(rest)
    elif cmd == "run":
        if not rest:
            raise SystemExit("Usage: V2Study.py run <case_name>")
        prepare(rest, overwrite=True)
        case_dir = RUN_ROOT / rest[0]
        subprocess.run(["bash", "Allrun"], cwd=case_dir, check=True)
        analyze(rest)
        compare([])
    else:
        raise SystemExit(f"Unknown command '{cmd}'. Use prepare / analyze / compare / run.")


if __name__ == "__main__":
    main()
