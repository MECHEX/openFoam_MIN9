from __future__ import annotations

import csv
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


CODE_DIR = Path(__file__).resolve().parent
REPO_CASE = CODE_DIR.parent
RESULTS_ROOT = REPO_CASE / "results" / "study_v1"
RUN_SLUG = "004_data_of13_fluid_consistency_short"
RUN_DIR = RESULTS_ROOT / "runs" / RUN_SLUG
PLOTS_DIR = RUN_DIR / "plots"
SIMS_DIR = RUN_DIR / "simulations"
OLD_SUMMARY = RESULTS_ROOT / "runs" / "002_data_sahin_owens_poiseuille_verification" / "summary.csv"

WORK_ROOT = Path("/home/hexmachina/of_runs/V1_run_of13_fluid_short")
OF_BASHRC = "/opt/openfoam13/etc/bashrc"
NPROCS = 6

D = 0.012
NU = 1.516e-5
RHO = 1.205
MU = RHO * NU
PR = 0.713
T_REF = 293.15
BETA_T = 1.0 / T_REF
SPAN = 0.01
Z_MIN = -0.5 * SPAN
Z_MAX = 0.5 * SPAN
UP_D = 8.0
DOWN_D = 20.0

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
    beta: float
    reynolds: float
    end_time_s: float
    purpose: str
    mesh: MeshVariant

    @property
    def H(self) -> float:
        return D / self.beta

    @property
    def half_H(self) -> float:
        return 0.5 * self.H

    @property
    def u_max(self) -> float:
        return self.reynolds * NU / D


MESH = MeshVariant("medium", 0.0025, 3, 2, 1, 6, 2, 0.25, 1.20)

CASES = [
    StudyCase("b030_medium_Re090", 0.30, 90.0, 6.0, "direct literature point, periodic", MESH),
    StudyCase("b030_medium_Re095", 0.30, 95.0, 6.0, "direct literature point, periodic", MESH),
    StudyCase("b0375_medium_Re105", 0.375, 105.0, 6.0, "geometry-relevant near onset", MESH),
    StudyCase("b0375_medium_Re120", 0.375, 120.0, 6.0, "geometry-relevant periodic", MESH),
    StudyCase("b050_medium_Re125", 0.50, 125.0, 10.0, "direct literature point, just below onset", MESH),
    StudyCase("b050_medium_Re135", 0.50, 135.0, 10.0, "direct literature point, periodic", MESH),
    StudyCase("b060_medium_Re125", 0.60, 125.0, 10.0, "additional confinement, just below onset", MESH),
    StudyCase("b060_medium_Re135", 0.60, 135.0, 8.0, "additional confinement, periodic", MESH),
]
CASE_MAP = {case.name: case for case in CASES}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def selected_cases(names: list[str]) -> list[StudyCase]:
    if not names:
        return CASES
    return [CASE_MAP[name] for name in names]


def so_ref(beta: float) -> dict[str, float | bool]:
    exact = SAHIN_OWENS.get(beta)
    if exact:
        return {"Re_crit": exact["Re_crit"], "St_crit": exact["St_crit"], "interpolated": False}
    betas = sorted(SAHIN_OWENS)
    lo = max(b for b in betas if b <= beta)
    hi = min(b for b in betas if b >= beta)
    t = (beta - lo) / (hi - lo)
    return {
        "Re_crit": SAHIN_OWENS[lo]["Re_crit"] * (1.0 - t) + SAHIN_OWENS[hi]["Re_crit"] * t,
        "St_crit": SAHIN_OWENS[lo]["St_crit"] * (1.0 - t) + SAHIN_OWENS[hi]["St_crit"] * t,
        "interpolated": True,
    }


def domain(case: StudyCase) -> dict[str, float]:
    xmin = -UP_D * D
    xmax = DOWN_D * D
    return {"xmin": xmin, "xmax": xmax, "length": xmax - xmin}


def base_counts(case: StudyCase) -> tuple[int, int]:
    d = domain(case)
    return max(120, int(round(d["length"] / case.mesh.base_dx))), max(8, int(round(case.H / case.mesh.base_dx)))


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", newline="\n")


def case_runtime_dir(case: StudyCase) -> Path:
    return WORK_ROOT / case.name


def case_archive_dir(case: StudyCase) -> Path:
    return SIMS_DIR / case.name


def block_mesh_dict(case: StudyCase) -> str:
    d = domain(case)
    nx, ny = base_counts(case)
    return f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
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
    front  {{ type symmetryPlane; faces ((0 3 2 1)); }}
    back   {{ type symmetryPlane; faces ((4 5 6 7)); }}
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
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}

castellatedMesh true;
snap true;
addLayers true;

geometry
{{
    cylinder
    {{
        type searchableCylinder;
        point1 (0 0 -0.010);
        point2 (0 0 0.010);
        radius {D/2.0:.6f};
    }}
    nearCylinder
    {{
        type searchableBox;
        min ({-2.5*D:.6f} {-near_h:.6f} -0.010);
        max ({6.0*D:.6f} {near_h:.6f} 0.010);
    }}
    wakeBox
    {{
        type searchableBox;
        min (0 {-wake_h:.6f} -0.010);
        max ({12.0*D:.6f} {wake_h:.6f} 0.010);
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
            level ({m.surface_level} {m.surface_level});
            patchInfo {{ type wall; }}
        }}
    }}
    refinementRegions
    {{
        nearCylinder {{ mode inside; levels ((1e15 {m.near_level})); }}
        wakeBox {{ mode inside; levels ((1e15 {m.wake_level})); }}
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
        top {{ nSurfaceLayers {m.wall_layers}; }}
        bottom {{ nSurfaceLayers {m.wall_layers}; }}
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
    return f"""FoamFile
{{
    format      ascii;
    class       volVectorField;
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({case.u_max:.9f} {0.001*case.u_max:.9f} 0);

boundaryField
{{
    inlet
    {{
        type            codedFixedValue;
        name            poiseuilleInlet;
        value           uniform (0 0 0);
        code
        #{{
            vectorField v(this->patch().size(), vector::zero);
            const vectorField& cf = this->patch().Cf();
            forAll(v, i)
            {{
                const scalar y = cf[i].y();
                v[i].x() = {case.u_max:.9f}*(1.0 - sqr(2.0*y/{case.H:.9f}));
            }}
            operator==(v);
        #}};
    }}
    outlet
    {{
        type            pressureInletOutletVelocity;
        value           uniform ({case.u_max:.9f} 0 0);
    }}
    top
    {{
        type            noSlip;
    }}
    bottom
    {{
        type            noSlip;
    }}
    cylinder
    {{
        type            noSlip;
    }}
    front
    {{
        type            symmetryPlane;
    }}
    back
    {{
        type            symmetryPlane;
    }}
}}
"""


def t_file() -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       volScalarField;
    object      T;
}}

dimensions      [0 0 0 1 0 0 0];
internalField   uniform {T_REF:.2f};

boundaryField
{{
    inlet {{ type fixedValue; value uniform {T_REF:.2f}; }}
    outlet {{ type inletOutlet; inletValue uniform {T_REF:.2f}; value uniform {T_REF:.2f}; }}
    top {{ type zeroGradient; }}
    bottom {{ type zeroGradient; }}
    cylinder {{ type zeroGradient; }}
    front {{ type symmetryPlane; }}
    back {{ type symmetryPlane; }}
}}
"""


def p_rgh_file() -> str:
    return """FoamFile
{
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet { type fixedFluxPressure; value uniform 0; }
    outlet { type fixedValue; value uniform 0; }
    top { type fixedFluxPressure; value uniform 0; }
    bottom { type fixedFluxPressure; value uniform 0; }
    cylinder { type fixedFluxPressure; value uniform 0; }
    front { type symmetryPlane; }
    back { type symmetryPlane; }
}
"""


def p_file() -> str:
    return """FoamFile
{
    format      ascii;
    class       volScalarField;
    object      p;
}

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet { type calculated; value $internalField; }
    outlet { type calculated; value $internalField; }
    top { type calculated; value $internalField; }
    bottom { type calculated; value $internalField; }
    cylinder { type calculated; value $internalField; }
    front { type symmetryPlane; }
    back { type symmetryPlane; }
}
"""


def control_dict(case: StudyCase) -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    object      controlDict;
}}

solver          fluid;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {case.end_time_s:.3f};
deltaT          0.001;
adjustTimeStep  yes;
maxCo           0.8;
writeControl    adjustableRunTime;
writeInterval   0.10;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
timeFormat      general;
timePrecision   8;
runTimeModifiable true;

functions
{{
    forceCoeffs
    {{
        type            forceCoeffs;
        libs            ("libforces.so");
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   0.01;
        log             yes;
        patches         (cylinder);
        rho             rhoInf;
        rhoInf          {RHO:.6f};
        CofR            (0 0 0);
        liftDir         (0 1 0);
        dragDir         (1 0 0);
        pitchAxis       (0 0 1);
        magUInf         {case.u_max:.9f};
        lRef            {D:.6f};
        Aref            {D*SPAN:.9f};
    }}

    residuals
    {{
        type            residuals;
        libs            ("libutilityFunctionObjects.so");
        fields          (U p_rgh e);
        executeControl  timeStep;
        writeControl    adjustableRunTime;
        writeInterval   0.05;
    }}
}}
"""


def fv_schemes() -> str:
    return """FoamFile
{
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes
{
    default         backward;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default                                 none;
    div(phi,U)                              Gauss linearUpwind grad(U);
    div(phi,e)                              Gauss upwind;
    div(phi,(p|rho))                        Gauss linear;
    div(phi,p)                              Gauss linear;
    div(phi,rho)                            Gauss linear;
    div(phi,K)                              Gauss linear;
    div(phid,p)                             Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U)))))     Gauss linear;
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
"""


def fv_solution() -> str:
    return """FoamFile
{
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

solvers
{
    "rho.*"
    {
        solver          diagonal;
    }

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
    }

    "(U|e)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-7;
        relTol          0.05;
    }

    "(U|e)Final"
    {
        $U;
        relTol          0;
    }
}

PIMPLE
{
    momentumPredictor          yes;
    nOuterCorrectors           2;
    nCorrectors                2;
    nNonOrthogonalCorrectors   1;
    pRefCell                   0;
    pRefValue                  0;
}
"""


def decompose_par_dict() -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}}

numberOfSubdomains {NPROCS};
method scotch;
"""


def physical_properties() -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    location    "constant";
    object      physicalProperties;
}}

thermoType
{{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          eConst;
    equationOfState Boussinesq;
    specie          specie;
    energy          sensibleInternalEnergy;
}}

mixture
{{
    specie
    {{
        molWeight       28.9;
    }}
    equationOfState
    {{
        rho0            {RHO:.6f};
        T0              {T_REF:.2f};
        beta            {BETA_T:.9e};
    }}
    thermodynamics
    {{
        Cv              1005;
        hf              0;
    }}
    transport
    {{
        mu              {MU:.9e};
        Pr              {PR:.6f};
    }}
}}
"""


def momentum_transport() -> str:
    return """FoamFile
{
    format      ascii;
    class       dictionary;
    location    "constant";
    object      momentumTransport;
}

simulationType  laminar;
"""


def g_file() -> str:
    return """FoamFile
{
    format      ascii;
    class       uniformDimensionedVectorField;
    location    "constant";
    object      g;
}

dimensions      [0 1 -2 0 0 0 0];
value           (0 0 0);
"""


def allrun_file() -> str:
    return f"""#!/usr/bin/env bash
export ZSH_NAME="${{ZSH_NAME-}}"
source {OF_BASHRC}
set -euo pipefail
cd "$(dirname "$0")"
rm -rf 0
cp -r 0.orig 0
mkdir -p logs
blockMesh | tee logs/blockMesh.log
snappyHexMesh -overwrite | tee logs/snappyHexMesh.log
checkMesh | tee logs/checkMesh.log
decomposePar -force | tee logs/decomposePar.log
mpirun --use-hwthread-cpus -np {NPROCS} foamRun -solver fluid -parallel | tee logs/foamRun.log
"""


def setup_case(case: StudyCase, overwrite: bool = False) -> None:
    cdir = case_runtime_dir(case)
    if cdir.exists() and overwrite:
        shutil.rmtree(cdir)
    ensure_dir(cdir / "0.orig")
    ensure_dir(cdir / "constant")
    ensure_dir(cdir / "system")
    write_text(cdir / "0.orig" / "U", u_file(case))
    write_text(cdir / "0.orig" / "T", t_file())
    write_text(cdir / "0.orig" / "p_rgh", p_rgh_file())
    write_text(cdir / "0.orig" / "p", p_file())
    write_text(cdir / "constant" / "physicalProperties", physical_properties())
    write_text(cdir / "constant" / "momentumTransport", momentum_transport())
    write_text(cdir / "constant" / "g", g_file())
    write_text(cdir / "system" / "blockMeshDict", block_mesh_dict(case))
    write_text(cdir / "system" / "snappyHexMeshDict", snappy_hex_mesh_dict(case))
    write_text(cdir / "system" / "controlDict", control_dict(case))
    write_text(cdir / "system" / "fvSchemes", fv_schemes())
    write_text(cdir / "system" / "fvSolution", fv_solution())
    write_text(cdir / "system" / "decomposeParDict", decompose_par_dict())
    write_text(cdir / "Allrun", allrun_file())
    subprocess.run(["bash", "-lc", f"chmod +x '{cdir / 'Allrun'}'"], check=True)
    archive_setup(case)


def archive_setup(case: StudyCase) -> None:
    target = case_archive_dir(case) / "openfoam_setup"
    if target.exists():
        shutil.rmtree(target)
    ensure_dir(target)
    src = case_runtime_dir(case)
    shutil.copytree(src / "0.orig", target / "0.orig")
    shutil.copytree(src / "constant", target / "constant")
    shutil.copytree(src / "system", target / "system")
    shutil.copy2(src / "Allrun", target / "Allrun")


def run_case(case: StudyCase) -> None:
    subprocess.run(["bash", "Allrun"], cwd=case_runtime_dir(case), check=True)


def parse_check_mesh(path: Path) -> dict[str, float | int | str | None]:
    result: dict[str, float | int | str | None] = {
        "status": "missing",
        "cells": None,
        "points": None,
        "faces": None,
        "max_non_ortho": None,
    }
    if not path.exists():
        return result
    text = path.read_text(encoding="utf-8", errors="ignore")
    result["status"] = "ok" if "Mesh OK" in text else "warn"
    import re

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


def coeff_paths(case: StudyCase) -> list[Path]:
    root = case_runtime_dir(case) / "postProcessing" / "forceCoeffs"
    if not root.exists():
        return []
    pairs: list[tuple[float, Path]] = []
    for child in root.iterdir():
        if not child.is_dir():
            continue
        for filename in ("coefficient.dat", "forceCoeffs.dat"):
            coeff = child / filename
            if coeff.exists():
                try:
                    start = float(child.name)
                except ValueError:
                    start = math.inf
                pairs.append((start, coeff))
                break
    return [path for _, path in sorted(pairs, key=lambda item: item[0])]


def load_coeffs(paths: list[Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    merged: dict[float, tuple[float, float]] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 4:
                merged[float(parts[0])] = (float(parts[2]), float(parts[3]))
    ordered = sorted(merged.items())
    return (
        np.asarray([item[0] for item in ordered], dtype=float),
        np.asarray([item[1][0] for item in ordered], dtype=float),
        np.asarray([item[1][1] for item in ordered], dtype=float),
    )


def compute_metrics(case: StudyCase, time: np.ndarray, cd: np.ndarray, cl: np.ndarray) -> dict[str, object]:
    if time.size < 32:
        return {"status": "insufficient-data", "regime": "undetermined", "Cd_mean": None, "Cl_rms": None, "frequency_hz": None, "St": None}
    start = max(0.4 * float(time.max()), float(time.max()) - 4.0)
    mask = time >= start
    t_sel = time[mask]
    cd_sel = cd[mask]
    cl_sel = cl[mask]
    cd_mean = float(np.mean(cd_sel))
    cl_centered = cl_sel - np.mean(cl_sel)
    cl_rms = float(np.sqrt(np.mean(cl_centered**2)))
    if t_sel.size < 32 or cl_rms < 1e-3:
        return {"status": "ok", "regime": "steady-or-weakly-unsteady", "Cd_mean": cd_mean, "Cl_rms": cl_rms, "frequency_hz": None, "St": None}
    dt = float(np.mean(np.diff(t_sel)))
    nfft = 1
    while nfft < cl_centered.size * 8:
        nfft *= 2
    freqs = np.fft.rfftfreq(nfft, d=dt)
    amps = np.abs(np.fft.rfft(cl_centered * np.hanning(cl_centered.size), n=nfft))
    valid = (freqs > 0.0) & (freqs < 25.0)
    freqs = freqs[valid]
    amps = amps[valid]
    idx = int(np.argmax(amps))
    freq = float(freqs[idx])
    return {
        "status": "ok",
        "regime": "periodic",
        "Cd_mean": cd_mean,
        "Cl_rms": cl_rms,
        "frequency_hz": freq,
        "St": float(freq * D / case.u_max),
    }


def plot_cl(case: StudyCase, time: np.ndarray, cl: np.ndarray) -> None:
    out = case_archive_dir(case) / "plots"
    ensure_dir(out)
    fig, ax = plt.subplots(figsize=(9, 4), dpi=160)
    ax.plot(time, cl, lw=0.9, color="#0b5ed7")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Cl [-]")
    ax.set_title(f"{case.name}: Cl(t) on OF13 fluid")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "Cl_vs_time.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def load_old_summary() -> dict[str, dict[str, str]]:
    with OLD_SUMMARY.open(encoding="utf-8") as handle:
        return {row["case"]: row for row in csv.DictReader(handle)}


def analyze_cases(cases: list[StudyCase]) -> list[dict[str, object]]:
    old = load_old_summary()
    rows: list[dict[str, object]] = []
    for case in cases:
        mesh_info = parse_check_mesh(case_runtime_dir(case) / "logs" / "checkMesh.log")
        paths = coeff_paths(case)
        if not paths:
            continue
        time, cd, cl = load_coeffs(paths)
        metrics = compute_metrics(case, time, cd, cl)
        plot_cl(case, time, cl)
        ref = so_ref(case.beta)
        old_row = old.get(case.name, {})
        old_st = float(old_row["St_sim"]) if old_row.get("St_sim") not in {"", "None", None} else None
        old_cd = float(old_row["Cd_mean"]) if old_row.get("Cd_mean") not in {"", "None", None} else None
        delta_vs_old = None
        if metrics["St"] is not None and old_st not in (None, 0.0):
            delta_vs_old = 100.0 * (float(metrics["St"]) - old_st) / old_st
        row = {
            "case": case.name,
            "beta": case.beta,
            "Re": case.reynolds,
            "cells": mesh_info["cells"],
            "regime_new": metrics["regime"],
            "Cd_old": old_cd,
            "Cd_new": metrics["Cd_mean"],
            "Cl_rms_old": float(old_row["Cl_rms"]) if old_row.get("Cl_rms") not in {"", "None", None} else None,
            "Cl_rms_new": metrics["Cl_rms"],
            "St_old": old_st,
            "St_new": metrics["St"],
            "St_ref": ref["St_crit"],
            "dSt_old_vs_ref_pct": (100.0 * (old_st - float(ref["St_crit"])) / float(ref["St_crit"])) if old_st is not None else None,
            "dSt_new_vs_ref_pct": (100.0 * (float(metrics["St"]) - float(ref["St_crit"])) / float(ref["St_crit"])) if metrics["St"] is not None else None,
            "dSt_new_vs_old_pct": delta_vs_old,
            "status": metrics["status"],
        }
        rows.append(row)
        write_text(case_archive_dir(case) / "summary.json", json.dumps(row, indent=2) + "\n")
    return rows


def write_summary(rows: list[dict[str, object]]) -> None:
    ensure_dir(RUN_DIR)
    ensure_dir(PLOTS_DIR)
    with (RUN_DIR / "summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        f"# {RUN_SLUG}",
        "",
        "| case | beta | Re | Cd old | Cd new | Cl_rms old | Cl_rms new | St old | St new | St ref | dSt new vs old [%] | dSt new vs ref [%] |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['beta']} | {row['Re']} | {row['Cd_old']} | {row['Cd_new']} | "
            f"{row['Cl_rms_old']} | {row['Cl_rms_new']} | {row['St_old']} | {row['St_new']} | "
            f"{row['St_ref']} | {row['dSt_new_vs_old_pct']} | {row['dSt_new_vs_ref_pct']} |"
        )
    write_text(RUN_DIR / "summary.md", "\n".join(lines) + "\n")


def plot_comparison(rows: list[dict[str, object]]) -> None:
    periodic = [row for row in rows if row["St_old"] is not None and row["St_new"] is not None]
    if not periodic:
        return

    fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=180)
    xs = [float(row["St_old"]) for row in periodic]
    ys = [float(row["St_new"]) for row in periodic]
    ax.scatter(xs, ys, s=42, color="#0f766e")
    lo = min(xs + ys) * 0.98
    hi = max(xs + ys) * 1.02
    ax.plot([lo, hi], [lo, hi], "--", color="#9ca3af", lw=1.0)
    for row in periodic:
        ax.text(float(row["St_old"]), float(row["St_new"]), row["case"].split("_")[0], fontsize=7)
    ax.set_xlabel("St old")
    ax.set_ylabel("St new (OF13 fluid)")
    ax.set_title("V1 consistency: old vs new St")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "V1_of13_old_vs_new_st.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    colors = {0.30: "#0b5ed7", 0.375: "#6b7280", 0.50: "#dc2626", 0.60: "#7c3aed"}
    fig, ax = plt.subplots(figsize=(8.2, 5.0), dpi=180)
    for beta in sorted({float(row["beta"]) for row in periodic}):
        group = sorted([row for row in periodic if float(row["beta"]) == beta], key=lambda item: float(item["Re"]))
        ax.plot([float(item["Re"]) for item in group], [float(item["St_old"]) for item in group], "o--", lw=1.0, color=colors[beta], label=f"beta={beta:.3f} old")
        ax.plot([float(item["Re"]) for item in group], [float(item["St_new"]) for item in group], "s-", lw=1.2, color=colors[beta], label=f"beta={beta:.3f} new")
        ref = so_ref(beta)
        ax.scatter([float(ref["Re_crit"])], [float(ref["St_crit"])], marker="x", s=70, color=colors[beta])
    ax.set_xlabel("Re = Umax D / nu")
    ax.set_ylabel("St = f D / Umax")
    ax.set_title("V1 consistency: Sahin-Owens parity on OF13 fluid")
    ax.grid(True, alpha=0.3)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "V1_of13_st_reference_overlay.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_run_doc() -> None:
    ensure_dir(RUN_DIR)
    ensure_dir(SIMS_DIR)
    ensure_dir(PLOTS_DIR)
    lines = [
        f"# {RUN_SLUG}",
        "",
        "Short solver-consistency rerun of V1 on the OF13 `foamRun -solver fluid` chain used by V4b.",
        "",
        f"- runtime root: `{WORK_ROOT}`",
        f"- solver chain: `foamRun -solver fluid`",
        f"- thermophysical model: `heRhoThermo + eConst + Boussinesq + sensibleInternalEnergy`",
        f"- thermal mode for V1: effectively isothermal (`g=0`, uniform `T`) so the run remains hydrodynamic in practice",
        "",
        "## Case matrix",
        "",
        "| case | beta | Re | endTime [s] | role |",
        "|---|---:|---:|---:|---|",
    ]
    for case in CASES:
        lines.append(f"| {case.name} | {case.beta:.3f} | {case.reynolds:.0f} | {case.end_time_s:.1f} | {case.purpose} |")
    write_text(RUN_DIR / "run.md", "\n".join(lines) + "\n")


def setup(names: list[str], overwrite: bool = False) -> None:
    write_run_doc()
    ensure_dir(WORK_ROOT)
    for case in selected_cases(names):
        setup_case(case, overwrite=overwrite)


def run(names: list[str]) -> None:
    for case in selected_cases(names):
        run_case(case)


def analyze(names: list[str]) -> None:
    rows = analyze_cases(selected_cases(names))
    if not rows:
        raise SystemExit("No analyzable V1 OF13 cases found.")
    write_summary(rows)
    plot_comparison(rows)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 V1FluidConsistencyStudy.py setup|run|analyze|all [case names...]")
    cmd = sys.argv[1]
    names = sys.argv[2:]
    if cmd == "setup":
        setup(names, overwrite=True)
    elif cmd == "run":
        run(names)
    elif cmd == "analyze":
        analyze(names)
    elif cmd == "all":
        setup(names, overwrite=True)
        run(names)
        analyze(names)
    else:
        raise SystemExit(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
