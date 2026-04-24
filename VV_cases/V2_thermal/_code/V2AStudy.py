"""
V2AStudy.py
-----------
Level A thermal verification for an unconfined heated cylinder.

The active V2a architecture is:
    buoyantBoussinesqPimpleFoam + g = 0

This script manages the active run-002 validation branch.

Usage:
  python _code/V2AStudy.py setup
  python _code/V2AStudy.py run
  python _code/V2AStudy.py run Re10
  python _code/V2AStudy.py analyze
  python _code/V2AStudy.py all
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path


CODE_DIR = Path(__file__).resolve().parent
REPO_CASE = CODE_DIR.parent
TEMPLATE = CODE_DIR / "templates" / "base_case"
RUN_ROOT = Path(r"C:\openfoam-case\VV_cases\V2_thermal_run002")
RESULTS_DIR = REPO_CASE / "results" / "study_v2a"
ACTIVE_RUN_SLUG = "002_data_v2a_boussinesq_validation"
ACTIVE_RUN_DIR = RESULTS_DIR / "runs" / ACTIVE_RUN_SLUG

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OF_BASHRC = "/home/kik/openfoam/OpenFOAM-v2512/etc/bashrc"


D = 0.012
L_Z = 0.010
MU = 1.825e-5
RHO0 = 1.2040
NU = MU / RHO0
PR = 0.713
PRT = 0.9
CP_FLUID = 1005.0                      # J/(kg·K), dry air
K_FLUID = MU * CP_FLUID / PR          # thermal conductivity [W/(m·K)] ≈ 0.02574
T_IN = 293.15
T_W = 303.15
DT = T_W - T_IN
BETA_T = 1.0 / T_IN

H_HALF = 10 * D
L_IN = 15 * D
L_OUT = 30 * D
BG_DX = 0.005


def nu_lange(reynolds: int | float) -> float:
    chi = 0.05 + 0.226 * reynolds ** 0.085
    return 0.082 * reynolds ** 0.5 + 0.734 * reynolds ** chi


BHARTI_NU = {10: 1.8623, 20: 2.4653, 40: 3.2825}


CASES = [
    {"name": "Re10", "Re": 10, "steady": True, "endTime": 100.0, "writeInterval": 1.0},
    {"name": "Re10_long100s", "Re": 10, "steady": True, "endTime": 100.0, "writeInterval": 1.0},
    {"name": "Re20", "Re": 20, "steady": True, "endTime": 100.0, "writeInterval": 1.0},
    {"name": "Re40", "Re": 40, "steady": True, "endTime": 100.0, "writeInterval": 1.0},
    {"name": "Re100", "Re": 100, "steady": False, "endTime": 25.0, "writeInterval": 0.5},
    {"name": "Re200", "Re": 200, "steady": False, "endTime": 15.0, "writeInterval": 0.25},
]


def get_case(name_or_re: str) -> dict:
    for case in CASES:
        if case["name"] == name_or_re or str(case["Re"]) == str(name_or_re):
            return case
    raise ValueError(f"Unknown case: {name_or_re}")


def domain_params(reynolds: int) -> tuple[float, float]:
    l_out = 40 * D if reynolds >= 100 else L_OUT
    return L_IN, l_out


def ensure_run_layout() -> None:
    ACTIVE_RUN_DIR.mkdir(parents=True, exist_ok=True)
    (ACTIVE_RUN_DIR / "simulations").mkdir(parents=True, exist_ok=True)


def simulation_repo_dir(name: str) -> Path:
    return ACTIVE_RUN_DIR / "simulations" / name


def ensure_simulation_layout(name: str) -> Path:
    sim_dir = simulation_repo_dir(name)
    sim_dir.mkdir(parents=True, exist_ok=True)
    return sim_dir


def write_run_docs() -> None:
    ensure_run_layout()
    lines = [
        f"# {ACTIVE_RUN_SLUG}",
        "",
        "## Purpose",
        "",
        "First production-oriented V2a run built on the accepted Boussinesq architecture.",
        "This run supersedes the earlier debug-only compressible branch.",
        "",
        "## Accepted architecture",
        "",
        "- solver: `buoyantBoussinesqPimpleFoam`",
        "- gravity: `g = (0 0 0)`",
        "- regime: pure forced convection",
        "- physical model: incompressible Boussinesq transport",
        "",
        "## Simulation matrix",
        "",
        "| case | Re | regime | endTime [s] | role |",
        "|---|---:|---|---:|---|",
    ]
    for case in CASES:
        regime = "steady" if case["steady"] else "unsteady"
        role = "first smoke-test" if case["name"] == "Re10" else "planned"
        lines.append(
            f"| {case['name']} | {case['Re']} | {regime} | {case['endTime']:.1f} | {role} |"
        )
    lines += [
        "",
        "## Next step",
        "",
        "- run `Re10` first as the production smoke-test for run 002",
        "- then continue with `Re20` and `Re40` before the unsteady cases",
    ]
    (ACTIVE_RUN_DIR / "run.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_simulation_notes(case: dict, output_lines: list[str] | None = None) -> None:
    sim_dir = ensure_simulation_layout(case["name"])
    l_in, l_out = domain_params(case["Re"])
    u_inf = case["Re"] * NU / D
    lines = [
        f"# {case['name']}",
        "",
        "## Setup",
        "",
        "- study: V2a unconfined heated cylinder",
        "- architecture: `buoyantBoussinesqPimpleFoam` with `g = 0`",
        f"- Reynolds number: `{case['Re']}`",
        f"- inlet velocity: `{u_inf:.6f} m/s`",
        f"- inlet temperature: `{T_IN:.2f} K`",
        f"- wall temperature: `{T_W:.2f} K`",
        f"- diameter: `{D:.6f} m`",
        f"- upstream length: `{l_in / D:.1f}D`",
        f"- downstream length: `{l_out / D:.1f}D`",
        f"- domain height: `{2.0 * H_HALF / D:.1f}D`",
        "",
        "## Intended outputs",
        "",
        "- mean Nusselt number `Nu`",
        "- mean drag coefficient `Cd`",
        "- shedding metric `St` for unsteady cases",
    ]
    if output_lines:
        lines += ["", "## Results", ""] + output_lines
    (sim_dir / "notes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_blockMeshDict(l_in: float, l_out: float, h_half: float, bg_dx: float) -> str:
    nx = round((l_in + l_out) / bg_dx)
    ny = round(2 * h_half / bg_dx)
    xmin = -l_in
    xmax = l_out
    ymin = -h_half
    ymax = h_half
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

// V2A: unconfined cylinder, H=20D (beta~5%), slip walls
// L_in={l_in*1000:.0f}mm  L_out={l_out*1000:.0f}mm  H={2*h_half*1000:.0f}mm  dx=dy={bg_dx*1000:.1f}mm
// background: {nx} x {ny} x 1 cells

scale 1;

vertices
(
    ({xmin:.4f} {ymin:.4f} -0.005)
    ({xmax:.4f} {ymin:.4f} -0.005)
    ({xmax:.4f} {ymax:.4f} -0.005)
    ({xmin:.4f} {ymax:.4f} -0.005)
    ({xmin:.4f} {ymin:.4f}  0.005)
    ({xmax:.4f} {ymin:.4f}  0.005)
    ({xmax:.4f} {ymax:.4f}  0.005)
    ({xmin:.4f} {ymax:.4f}  0.005)
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
        faces ( (0 4 7 3) );
    }}
    outlet
    {{
        type patch;
        faces ( (1 2 6 5) );
    }}
    bottom
    {{
        type patch;
        faces ( (0 1 5 4) );
    }}
    top
    {{
        type patch;
        faces ( (3 7 6 2) );
    }}
    front
    {{
        type empty;
        faces ( (0 3 2 1) );
    }}
    back
    {{
        type empty;
        faces ( (4 5 6 7) );
    }}
);

mergePatchPairs ();
"""


def make_snappyHexMeshDict(l_in: float, l_out: float, h_half: float) -> str:
    loc_x = -l_in * 0.5
    nc_y = min(4 * D, h_half * 0.8)
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}

// V2A: unconfined cylinder, BL on cylinder only (no wall BL)

castellatedMesh true;
snap            true;
addLayers       false;

geometry
{{
    cylinder
    {{
        type    searchableCylinder;
        point1  (0  0  -{L_Z/2:.4f});
        point2  (0  0   {L_Z/2:.4f});
        radius  {D/2:.4f};
    }}

    nearCylinder
    {{
        type searchableBox;
        min (-{3*D:.4f} -{nc_y:.4f} -{L_Z/2:.4f});
        max ( {8*D:.4f}  {nc_y:.4f}  {L_Z/2:.4f});
    }}

    wakeBox
    {{
        type searchableBox;
        min ( 0.000 -{nc_y:.4f} -{L_Z/2:.4f});
        max ( {l_out*0.8:.4f}  {nc_y:.4f}  {L_Z/2:.4f});
    }}
}}

castellatedMeshControls
{{
    maxLocalCells           500000;
    maxGlobalCells          2000000;
    minRefinementCells      0;
    maxLoadUnbalance        0.10;
    nCellsBetweenLevels     3;
    resolveFeatureAngle     30;
    features ();

    refinementSurfaces
    {{
        cylinder
        {{
            level   (3 3);
            patchInfo {{ type wall; }}
        }}
    }}

    refinementRegions
    {{
        nearCylinder
        {{
            mode    inside;
            levels  ((1e15 2));
        }}
        wakeBox
        {{
            mode    inside;
            levels  ((1e15 1));
        }}
    }}

    locationInMesh ({loc_x:.4f} 0 0);
    allowFreeStandingZoneFaces true;
}}

snapControls
{{
    nSmoothPatch        5;
    tolerance           2.0;
    nSolveIter          100;
    nRelaxIter          5;
    nFeatureSnapIter    10;
    implicitFeatureSnap true;
    explicitFeatureSnap false;
    multiRegionFeatureSnap false;
}}

addLayersControls
{{
    relativeSizes       true;
    expansionRatio      1.2;
    finalLayerThickness 0.25;
    minThickness        0.01;
    nGrow               0;
    featureAngle        60;
    nRelaxIter          3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals      3;
    nSmoothThickness    10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle  90;
    nBufferCellsNoExtrude 0;
    nLayerIter          50;
    nRelaxedIter        20;

    layers
    {{
        cylinder
        {{
            nSurfaceLayers  6;
        }}
    }}
}}

meshQualityControls
{{
    maxNonOrtho         65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave          80;
    minVol              1e-13;
    minTetQuality       1e-30;
    minArea             -1;
    minTwist            0.02;
    minDeterminant      0.001;
    minFaceWeight       0.02;
    minVolRatio         0.01;
    minTriangleTwist    -1;
    nSmoothScale        4;
    errorReduction      0.75;

    relaxed
    {{
        maxNonOrtho     75;
    }}
}}

writeFlags ( scalarLevels layerSets );
mergeTolerance 1e-6;
"""


def make_controlDict(reynolds: int, u_inf: float, end_time: float, write_interval: float) -> str:
    aref = D * L_Z
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}}

application     buoyantBoussinesqPimpleFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end_time};

deltaT          1e-4;
adjustTimeStep  yes;
maxCo           0.5;

writeControl    runTime;
writeInterval   {write_interval};
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
        writeControl    timeStep;
        writeInterval   1;
        log             yes;
        patches         (cylinder);
        rho             rhoInf;
        rhoInf          {RHO0:.4f};
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         {u_inf:.6f};
        lRef            {D};
        Aref            {aref:.6f};
    }}

    residuals
    {{
        type            solverInfo;
        libs            (utilityFunctionObjects);
        fields          (U p_rgh T);
        writeControl    timeStep;
        writeInterval   10;
    }}

}}
"""


def make_fvSchemes() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
    grad(U)         Gauss linear;
    grad(T)         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,T)      Gauss limitedLinear01 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method          meshWave;
}
"""


def make_fvSolution() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-8;
        relTol          0.01;
    }
    p_rghFinal
    {
        $p_rgh;
        relTol          0;
        tolerance       1e-9;
    }

    "(U|T)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-8;
        relTol          0.1;
    }
    "(U|T)Final"
    {
        $U;
        relTol          0;
        tolerance       1e-9;
    }
}

PIMPLE
{
    momentumPredictor no;
    nOuterCorrectors        1;
    nCorrectors             2;
    nNonOrthogonalCorrectors 2;
    pRefCell        0;
    pRefValue       0;

    residualControl
    {
        U     { tolerance 1e-5; relTol 0; }
        p_rgh { tolerance 1e-5; relTol 0; }
        T     { tolerance 1e-5; relTol 0; }
    }
}

relaxationFactors
{
    equations
    {
        U       0.9;
        UFinal  1.0;
        T       0.9;
        TFinal  1.0;
    }
}
"""


def make_decomposeParDict(n_subdomains: int = 10) -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}}

numberOfSubdomains {n_subdomains};

method          scotch;
"""


def make_transportProperties() -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}}

transportModel  Newtonian;

nu              {NU:.6g};

beta            {BETA_T:.6g};

TRef            {T_IN:.2f};

Pr              {PR:.3f};

Prt             {PRT:.1f};
"""


def make_g() -> str:
    return """FoamFile { version 2.0; format ascii; class uniformDimensionedVectorField; object g; }
dimensions  [0 1 -2 0 0 0 0];
value       (0 0 0);
"""


def make_turbulenceProperties() -> str:
    return """FoamFile { version 2.0; format ascii; class dictionary; object turbulenceProperties; }
simulationType  laminar;
"""


def make_U(u_inf: float) -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({u_inf:.6f} 0 0);

boundaryField
{{
    inlet
    {{
        type        fixedValue;
        value       uniform ({u_inf:.6f} 0 0);
    }}
    outlet
    {{
        type        zeroGradient;
    }}
    top
    {{
        type        slip;
    }}
    bottom
    {{
        type        slip;
    }}
    cylinder
    {{
        type        noSlip;
    }}
    front
    {{
        type        empty;
    }}
    back
    {{
        type        empty;
    }}
}}
"""


def make_T() -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}}

dimensions      [0 0 0 1 0 0 0];
internalField   uniform {T_IN:.2f};

boundaryField
{{
    inlet
    {{
        type        fixedValue;
        value       uniform {T_IN:.2f};
    }}
    outlet
    {{
        type        inletOutlet;
        inletValue  uniform {T_IN:.2f};
        value       uniform {T_IN:.2f};
    }}
    top
    {{
        type        fixedValue;
        value       uniform {T_IN:.2f};
    }}
    bottom
    {{
        type        fixedValue;
        value       uniform {T_IN:.2f};
    }}
    cylinder
    {{
        type        fixedValue;
        value       uniform {T_W:.2f};
    }}
    front
    {{
        type        empty;
    }}
    back
    {{
        type        empty;
    }}
}}
"""


def make_p_rgh() -> str:
    return """FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}

dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet    { type fixedFluxPressure; rho rhok; value uniform 0; }
    outlet   { type fixedValue; value uniform 0; }
    top      { type fixedFluxPressure; rho rhok; value uniform 0; }
    bottom   { type fixedFluxPressure; rho rhok; value uniform 0; }
    cylinder { type fixedFluxPressure; rho rhok; value uniform 0; }
    front    { type empty; }
    back     { type empty; }
}
"""


def make_alphat() -> str:
    return """FoamFile { version 2.0; format ascii; class volScalarField; object alphat; }
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;
boundaryField { ".*" { type calculated; value uniform 0; } }
"""


def setup_case(case: dict) -> None:
    name = case["name"]
    reynolds = case["Re"]
    u_inf = reynolds * NU / D
    l_in, l_out = domain_params(reynolds)

    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    write_run_docs()
    write_simulation_notes(case)

    case_dir = RUN_ROOT / name
    if case_dir.exists():
        print(f"  [skip] {name} already exists - delete manually to re-setup")
        return

    print(f"  Setting up {name}  Re={reynolds}  U={u_inf:.5f} m/s  l_out={l_out*1000:.0f}mm")
    shutil.copytree(TEMPLATE, case_dir)

    (case_dir / "system" / "blockMeshDict").write_text(
        make_blockMeshDict(l_in, l_out, H_HALF, BG_DX), encoding="utf-8"
    )
    (case_dir / "system" / "snappyHexMeshDict").write_text(
        make_snappyHexMeshDict(l_in, l_out, H_HALF), encoding="utf-8"
    )
    (case_dir / "system" / "controlDict").write_text(
        make_controlDict(reynolds, u_inf, case["endTime"], case["writeInterval"]),
        encoding="utf-8",
    )
    (case_dir / "system" / "decomposeParDict").write_text(
        make_decomposeParDict(10), encoding="utf-8"
    )
    (case_dir / "system" / "fvSchemes").write_text(make_fvSchemes(), encoding="utf-8")
    (case_dir / "system" / "fvSolution").write_text(make_fvSolution(), encoding="utf-8")

    (case_dir / "constant" / "transportProperties").write_text(
        make_transportProperties(), encoding="utf-8"
    )
    (case_dir / "constant" / "g").write_text(make_g(), encoding="utf-8")
    (case_dir / "constant" / "turbulenceProperties").write_text(
        make_turbulenceProperties(), encoding="utf-8"
    )

    (case_dir / "0" / "U").write_text(make_U(u_inf), encoding="utf-8")
    (case_dir / "0" / "T").write_text(make_T(), encoding="utf-8")
    (case_dir / "0" / "p_rgh").write_text(make_p_rgh(), encoding="utf-8")
    (case_dir / "0" / "alphat").write_text(make_alphat(), encoding="utf-8")

    for stale in [
        case_dir / "0" / "h",
        case_dir / "0" / "p",
        case_dir / "constant" / "thermophysicalProperties",
    ]:
        if stale.exists():
            stale.unlink()

    (case_dir / "caseMeta.json").write_text(
        json.dumps(
            {
                "study": "V2A",
                "architecture": "buoyantBoussinesqPimpleFoam",
                "run_slug": ACTIVE_RUN_SLUG,
                "case": name,
                "Re": reynolds,
                "U_in": round(u_inf, 8),
                "T_in": T_IN,
                "T_w": T_W,
                "L_in_D": l_in / D,
                "L_out_D": l_out / D,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  {name} ready at {case_dir}")


def win_to_wsl(path: Path) -> str:
    s = str(path).replace("\\", "/")
    if len(s) > 1 and s[1] == ":":
        s = "/mnt/" + s[0].lower() + s[2:]
    return s


def run_of(cmd: str, cwd: Path, logfile: Path) -> None:
    wsl_cwd = win_to_wsl(cwd)
    full_cmd = f'source {OF_BASHRC} 2>/dev/null && cd "{wsl_cwd}" && {cmd}'
    with logfile.open("w", encoding="utf-8") as lf:
        proc = subprocess.Popen(
            ["wsl", "-e", "bash", "-c", full_cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            lf.write(line)
        proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"{cmd} failed (rc={proc.returncode}), see {logfile}")


def run_case(case: dict) -> None:
    name = case["name"]
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    case_dir = RUN_ROOT / name
    if not case_dir.exists():
        print(f"  [skip] {name} not set up - run setup first")
        return

    logs_dir = case_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    log = lambda stem: logs_dir / f"log.{stem}"

    print(f"\n{'=' * 60}")
    print(f"  Running {name}  (serial Boussinesq)")
    print(f"{'=' * 60}")

    run_of("blockMesh", case_dir, log("blockMesh"))
    run_of("snappyHexMesh -overwrite", case_dir, log("snappyHexMesh"))
    run_of("checkMesh", case_dir, log("checkMesh"))
    run_of("buoyantBoussinesqPimpleFoam", case_dir, log("buoyantBoussinesqPimpleFoam"))

    print(f"  {name} done")


def latest_force_coeff_file(case_dir: Path) -> Path | None:
    fc_dir = case_dir / "postProcessing" / "forceCoeffs"
    if not fc_dir.exists():
        return None
    found: list[tuple[float, Path]] = []
    for time_dir in fc_dir.iterdir():
        coeff = time_dir / "coefficient.dat"
        if coeff.exists():
            try:
                found.append((float(time_dir.name), coeff))
            except ValueError:
                continue
    if not found:
        return None
    found.sort(key=lambda item: item[0])
    return found[-1][1]


def numeric_time_dirs(case_dir: Path) -> list[tuple[float, Path]]:
    found: list[tuple[float, Path]] = []
    for child in case_dir.iterdir():
        if not child.is_dir():
            continue
        try:
            time_value = float(child.name)
        except ValueError:
            continue
        found.append((time_value, child))
    found.sort(key=lambda item: item[0])
    return found


def parse_points(points_path: Path) -> list[tuple[float, float, float]]:
    lines = points_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    count_idx = next(i for i, line in enumerate(lines) if line.strip().isdigit())
    n_points = int(lines[count_idx].strip())
    start = count_idx + 2
    points: list[tuple[float, float, float]] = []
    for line in lines[start:]:
        s = line.strip()
        if s == ");" or s == ")":
            break
        if not s.startswith("("):
            continue
        x, y, z = s.strip("()").split()
        points.append((float(x), float(y), float(z)))
    if len(points) != n_points:
        raise ValueError(f"Expected {n_points} points in {points_path}, got {len(points)}")
    return points


def parse_faces(faces_path: Path) -> list[list[int]]:
    lines = faces_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    count_idx = next(i for i, line in enumerate(lines) if line.strip().isdigit())
    n_faces = int(lines[count_idx].strip())
    start = count_idx + 2
    faces: list[list[int]] = []
    for line in lines[start:]:
        s = line.strip()
        if s == ");" or s == ")":
            break
        match = re.match(r"(\d+)\((.*?)\)", s)
        if not match:
            continue
        faces.append([int(token) for token in match.group(2).split()])
    if len(faces) != n_faces:
        raise ValueError(f"Expected {n_faces} faces in {faces_path}, got {len(faces)}")
    return faces


def parse_boundary(boundary_path: Path) -> dict[str, dict[str, int | str]]:
    lines = boundary_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    count_idx = next(i for i, line in enumerate(lines) if line.strip().isdigit())
    start = count_idx + 2
    patches: dict[str, dict[str, int | str]] = {}
    i = start
    while i < len(lines):
        name = lines[i].strip()
        if name in (")", ");"):
            break
        if not name:
            i += 1
            continue
        i += 1
        while i < len(lines) and lines[i].strip() != "{":
            i += 1
        i += 1
        patch: dict[str, int | str] = {}
        while i < len(lines):
            s = lines[i].strip()
            if s == "}":
                i += 1
                break
            parts = s.rstrip(";").split()
            if len(parts) >= 2:
                key = parts[0]
                value = parts[1]
                if key in ("nFaces", "startFace"):
                    patch[key] = int(value)
                else:
                    patch[key] = value
            i += 1
        patches[name] = patch
    return patches


def _vec_sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _vec_add(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _vec_scale(a: tuple[float, float, float], scalar: float) -> tuple[float, float, float]:
    return (a[0] * scalar, a[1] * scalar, a[2] * scalar)


def _vec_dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _vec_cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _vec_norm(a: tuple[float, float, float]) -> float:
    return math.sqrt(_vec_dot(a, a))


def face_area_vector(face: list[int], points: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    ref = points[face[0]]
    area = (0.0, 0.0, 0.0)
    for i in range(1, len(face) - 1):
        v1 = _vec_sub(points[face[i]], ref)
        v2 = _vec_sub(points[face[i + 1]], ref)
        area = _vec_add(area, _vec_scale(_vec_cross(v1, v2), 0.5))
    return area


def face_center(face: list[int], points: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    center = (0.0, 0.0, 0.0)
    for idx in face:
        center = _vec_add(center, points[idx])
    return _vec_scale(center, 1.0 / len(face))


def cylinder_patch_geometry(
    case_dir: Path,
) -> list[tuple[float, tuple[float, float, float]]]:
    poly = case_dir / "constant" / "polyMesh"
    points = parse_points(poly / "points")
    faces = parse_faces(poly / "faces")
    boundary = parse_boundary(poly / "boundary")
    cyl = boundary["cylinder"]
    start_face = int(cyl["startFace"])
    n_faces = int(cyl["nFaces"])

    patch_faces = faces[start_face : start_face + n_faces]
    geometry: list[tuple[float, tuple[float, float, float]]] = []
    radial_sign_sum = 0.0
    for face in patch_faces:
        area_vec = face_area_vector(face, points)
        area = _vec_norm(area_vec)
        if area <= 0:
            continue
        normal = _vec_scale(area_vec, 1.0 / area)
        center = face_center(face, points)
        radial_sign_sum += center[0] * normal[0] + center[1] * normal[1]
        geometry.append((area, normal))

    if radial_sign_sum > 0:
        geometry = [(area, _vec_scale(normal, -1.0)) for area, normal in geometry]
    return geometry


def read_patch_grad_vectors(field_path: Path, patch_name: str) -> list[tuple[float, float, float]]:
    text = field_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(
        rf"\b{re.escape(patch_name)}\s*\{{.*?value\s+nonuniform\s+List<vector>\s+(\d+)\s*\((.*?)\n\s*\)\s*;",
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError(f"Could not parse patch '{patch_name}' in {field_path}")
    n_values = int(match.group(1))
    block = match.group(2)
    values: list[tuple[float, float, float]] = []
    for raw in block.splitlines():
        s = raw.strip()
        if not s.startswith("("):
            continue
        x, y, z = s.strip("()").split()
        values.append((float(x), float(y), float(z)))
    if len(values) != n_values:
        raise ValueError(f"Expected {n_values} vectors for patch '{patch_name}', got {len(values)}")
    return values


def read_patch_scalar_field(field_path: Path, patch_name: str) -> list[float]:
    text = field_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(
        rf"\b{re.escape(patch_name)}\s*\{{.*?value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)\s*;",
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError(f"Could not parse scalar patch '{patch_name}' in {field_path}")
    n_values = int(match.group(1))
    values = [float(v) for v in match.group(2).split() if v.strip()]
    if len(values) != n_values:
        raise ValueError(f"Expected {n_values} scalars for patch '{patch_name}', got {len(values)}")
    return values


def parse_owner(path: Path) -> list[int]:
    """Read constant/polyMesh/owner: one owner-cell index per face."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^(\d+)\s*\n\s*\(", text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"Cannot parse owner list in {path}")
    n = int(match.group(1))
    start = match.end()
    block = text[start : text.index(")", start)]
    values = [int(v) for v in block.split()]
    if len(values) != n:
        raise ValueError(f"Expected {n} owner entries, got {len(values)}")
    return values


def parse_scalar_internal_field(path: Path) -> list[float]:
    """Read internalField (cell-centre values) from a scalar OF field file."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(
        r"internalField\s+nonuniform\s+List<scalar>\s+(\d+)\s*\n\s*\((.*?)\)\s*;",
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError(f"Cannot parse scalar internalField in {path}")
    n = int(match.group(1))
    values = [float(v) for v in match.group(2).split() if v.strip()]
    if len(values) != n:
        raise ValueError(f"Expected {n} scalar values, got {len(values)}")
    return values


def parse_vector_internal_field(path: Path) -> list[tuple[float, float, float]]:
    """Read internalField (cell-centre values) from a vector OF field file."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(
        r"internalField\s+nonuniform\s+List<vector>\s+(\d+)\s*\n\s*\((.*?)\)\s*;",
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError(f"Cannot parse vector internalField in {path}")
    n = int(match.group(1))
    block = match.group(2)
    values: list[tuple[float, float, float]] = []
    for raw in block.splitlines():
        s = raw.strip()
        if not s.startswith("("):
            continue
        x, y, z = s.strip("()").split()
        values.append((float(x), float(y), float(z)))
    if len(values) != n:
        raise ValueError(f"Expected {n} vector values, got {len(values)}")
    return values


def ensure_cell_centres(case_dir: Path) -> None:
    """Write 0/C (cell-centre positions) via postProcess if not already present."""
    if (case_dir / "0" / "C").exists():
        return
    logs_dir = case_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    run_of(
        "postProcess -func writeCellCentres -time 0",
        case_dir,
        logs_dir / "log.writeCellCentres",
    )


def cylinder_sngrad_setup(
    case_dir: Path,
) -> tuple[list[tuple[float, tuple, tuple, int]], list[tuple[float, float, float]]]:
    """Precompute per-face snGrad geometry for the cylinder patch.

    Returns:
        faces_data : list of (area, normal, face_center, owner_cell_idx)
                     normals point INTO the cylinder (same convention as cylinder_patch_geometry)
        cell_centers: all cell-centre positions from 0/C
    """
    poly = case_dir / "constant" / "polyMesh"
    points = parse_points(poly / "points")
    faces = parse_faces(poly / "faces")
    boundary = parse_boundary(poly / "boundary")
    owner = parse_owner(poly / "owner")

    cyl = boundary["cylinder"]
    start_face = int(cyl["startFace"])
    n_faces = int(cyl["nFaces"])

    patch_faces = faces[start_face : start_face + n_faces]
    patch_owners = owner[start_face : start_face + n_faces]

    raw: list[tuple[float, tuple, tuple]] = []
    radial_sign_sum = 0.0
    for face in patch_faces:
        area_vec = face_area_vector(face, points)
        area = _vec_norm(area_vec)
        if area <= 0:
            raw.append((0.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
            continue
        normal = _vec_scale(area_vec, 1.0 / area)
        center = face_center(face, points)
        radial_sign_sum += center[0] * normal[0] + center[1] * normal[1]
        raw.append((area, normal, center))

    # Ensure normals point inward (toward cylinder center): flip if currently outward
    if radial_sign_sum > 0:
        raw = [(a, _vec_scale(n, -1.0), c) for a, n, c in raw]

    ensure_cell_centres(case_dir)
    cell_centers = parse_vector_internal_field(case_dir / "0" / "C")

    faces_data = [
        (area, normal, center, cell_idx)
        for (area, normal, center), cell_idx in zip(raw, patch_owners)
    ]
    return faces_data, cell_centers


def nu_time_series(case_dir: Path) -> list[tuple[float, float]]:
    """Compute Nu(t) via snGrad(T) on the cylinder patch.

    snGrad(T) = (T_face - T_P) / dot(face_center - cell_center, inward_normal)

    For the fixed-temperature hot wall (T_face = T_W > T_P), both numerator
    and denominator are positive, giving Nu = D * snGrad / DT > 0.
    This avoids the non-orthogonality inflation of the volumetric grad(T) approach.
    """
    faces_data, cell_centers = cylinder_sngrad_setup(case_dir)
    if not faces_data:
        return []

    series: list[tuple[float, float]] = []
    for time_value, time_dir in numeric_time_dirs(case_dir):
        if time_value <= 0.0:
            continue
        t_path = time_dir / "T"
        if not t_path.exists():
            continue
        t_cell = parse_scalar_internal_field(t_path)
        area_sum = 0.0
        sngrad_sum = 0.0
        for area, normal, f_center, cell_idx in faces_data:
            if area <= 0:
                continue
            t_p = t_cell[cell_idx]
            c_p = cell_centers[cell_idx]
            # delta_perp: perpendicular distance from cell centre to face, positive inward
            delta_perp = (
                (f_center[0] - c_p[0]) * normal[0]
                + (f_center[1] - c_p[1]) * normal[1]
                + (f_center[2] - c_p[2]) * normal[2]
            )
            if abs(delta_perp) < 1e-15:
                continue
            sngrad = (T_W - t_p) / delta_perp
            area_sum += area
            sngrad_sum += area * sngrad
        if area_sum <= 0.0:
            continue
        nu_value = D * (sngrad_sum / area_sum) / DT
        series.append((time_value, nu_value))
    return series


def _fft(values: list[float]) -> list[complex]:
    import cmath

    n = len(values)
    p2 = 1
    while p2 < n:
        p2 <<= 1
    values = list(values) + [0.0] * (p2 - n)

    def _inner(seq: list[complex]) -> list[complex]:
        if len(seq) == 1:
            return seq
        even = _inner(seq[0::2])
        odd = _inner(seq[1::2])
        twiddle = [cmath.exp(-2j * cmath.pi * k / len(seq)) * odd[k] for k in range(len(seq) // 2)]
        return [even[k] + twiddle[k] for k in range(len(seq) // 2)] + [
            even[k] - twiddle[k] for k in range(len(seq) // 2)
        ]

    return _inner([complex(v) for v in values])


def analyze_case(case: dict) -> dict:
    name = case["name"]
    reynolds = case["Re"]
    case_dir = RUN_ROOT / name

    result = {
        "metadata": {"case": name, "Re": reynolds, "T_in": T_IN, "T_w": T_W},
        "metrics": {},
        "reference": {"Nu_Lange": round(nu_lange(reynolds), 4), "Nu_Bharti": BHARTI_NU.get(reynolds)},
    }

    coeff_file = latest_force_coeff_file(case_dir)
    cd_mean = None
    st_value = None
    nu_value = None
    nu_last = None
    nu_samples = 0
    nu_series = nu_time_series(case_dir) if case_dir.exists() else []
    if nu_series:
        nu_last = round(nu_series[-1][1], 4)
        nu_samples = len(nu_series)
        if case["steady"]:
            tail_count = max(1, len(nu_series) // 2)
            nu_value = round(sum(value for _, value in nu_series[-tail_count:]) / tail_count, 4)
        else:
            tail_count = max(1, len(nu_series) // 2)
            nu_value = round(sum(value for _, value in nu_series[-tail_count:]) / tail_count, 4)
        result["metrics"]["Nu"] = nu_value
        result["metrics"]["Nu_last"] = nu_last
        result["metrics"]["Nu_samples"] = nu_samples
    if coeff_file and coeff_file.exists():
        lines = [
            line for line in coeff_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        if lines:
            n_avg = max(1, len(lines) // 5)
            cd_vals: list[float] = []
            cl_times: list[float] = []
            cl_vals: list[float] = []
            for line in lines[-n_avg:]:
                parts = line.split()
                if len(parts) > 1:
                    cd_vals.append(float(parts[1]))
            for line in lines:
                parts = line.split()
                if len(parts) > 4:
                    cl_times.append(float(parts[0]))
                    cl_vals.append(float(parts[4]))
            if cd_vals:
                cd_mean = round(sum(cd_vals) / len(cd_vals), 4)
                result["metrics"]["Cd_mean"] = cd_mean
            if not case["steady"] and len(cl_vals) > 20:
                n_tail = max(20, len(cl_vals) // 2)
                t_arr = cl_times[-n_tail:]
                cl_arr = cl_vals[-n_tail:]
                dt = (t_arr[-1] - t_arr[0]) / (len(t_arr) - 1)
                amps = [abs(x) for x in _fft(cl_arr)]
                freqs = [i / (len(cl_arr) * dt) for i in range(len(cl_arr) // 2)]
                if len(freqs) > 1:
                    peak_idx = max(range(1, len(freqs)), key=lambda i: amps[i])
                    f_shed = freqs[peak_idx]
                    st_value = round(f_shed * D / (reynolds * NU / D), 4)
                    result["metrics"]["St"] = st_value

    output_lines = [
        f"- Nu = {nu_value}",
        f"- Nu_last_written_time = {nu_last}",
        f"- Nu_samples = {nu_samples}",
        f"- Cd_mean = {cd_mean}",
        f"- St = {st_value}",
        f"- Nu_Lange = {result['reference'].get('Nu_Lange')}",
        f"- Nu_Bharti = {result['reference'].get('Nu_Bharti')}",
        "- note = Nu is computed from area-weighted snGrad(T) on the cylinder patch (T_wall - T_P) / delta_perp.",
    ]
    write_simulation_notes(case, output_lines)
    print(f"  {name}: Cd={cd_mean}  St={st_value}  Nu={nu_value}")
    return result


def write_run_summary(results: list[dict]) -> None:
    ensure_run_layout()
    fieldnames = [
        "case",
        "Re",
        "Nu",
        "Cd_mean",
        "St",
        "Nu_Lange",
        "Nu_Bharti",
    ]
    rows = []
    for result in results:
        rows.append(
            {
                "case": result["metadata"]["case"],
                "Re": result["metadata"]["Re"],
                "Nu": result["metrics"].get("Nu"),
                "Cd_mean": result["metrics"].get("Cd_mean"),
                "St": result["metrics"].get("St"),
                "Nu_Lange": result["reference"].get("Nu_Lange"),
                "Nu_Bharti": result["reference"].get("Nu_Bharti"),
            }
        )

    with (ACTIVE_RUN_DIR / "summary.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        f"# {ACTIVE_RUN_SLUG} summary",
        "",
        "| case | Re | Nu | Cd_mean | St | Nu_Lange | Nu_Bharti |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['Re']} | {row['Nu']} | {row['Cd_mean']} | {row['St']} | {row['Nu_Lange']} | {row['Nu_Bharti']} |"
        )
    lines += [
        "",
        "Current note: `Nu` is now extracted from the area-averaged wall-normal",
        "temperature gradient on the cylinder patch for the accepted Boussinesq architecture.",
    ]
    (ACTIVE_RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="V2A study manager")
    parser.add_argument("action", choices=["setup", "run", "analyze", "all"], help="Action to perform")
    parser.add_argument("cases", nargs="*", help="Case names (e.g. Re10 Re20); default = all")
    args = parser.parse_args()

    target_cases = [get_case(name) for name in args.cases] if args.cases else CASES

    if args.action in ("setup", "all"):
        print("\n== SETUP ==")
        for case in target_cases:
            setup_case(case)

    if args.action in ("run", "all"):
        print("\n== RUN ==")
        for case in target_cases:
            try:
                run_case(case)
            except RuntimeError as exc:
                print(f"  ERROR: {exc}")

    if args.action in ("analyze", "all"):
        print("\n== ANALYZE ==")
        results = []
        for case in target_cases:
            results.append(analyze_case(case))
        if results:
            write_run_summary(results)


if __name__ == "__main__":
    main()
