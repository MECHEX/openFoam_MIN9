from __future__ import annotations

from pathlib import Path


D = 0.012
RADIUS = 0.5 * D
RHO = 1.205
MU = 1.827e-5
NU = MU / RHO
PR = 0.713
CV = 1005.0
T_REF = 293.15
BETA_T = 1.0 / T_REF
SPAN = 0.012
Z_HALF = 0.5 * SPAN

# V4b-like compact production family
X0 = -0.037855
X1 = -0.013855
X2 = 0.013855
X3 = 0.109855
Y_HALF = 0.016

NEAR_MIN_X = -0.024
NEAR_MAX_X = 0.036
NEAR_HALF_Y = 0.012
WAKE_MIN_X = 0.0
WAKE_MAX_X = 0.084
WAKE_HALF_Y = 0.014


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", newline="\n")


def block_mesh_dict(top_type: str, bottom_type: str) -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

scale 1;

vertices
(
    ({X0:.6f} {-Y_HALF:.6f} {-Z_HALF:.6f})
    ({X1:.6f} {-Y_HALF:.6f} {-Z_HALF:.6f})
    ({X2:.6f} {-Y_HALF:.6f} {-Z_HALF:.6f})
    ({X3:.6f} {-Y_HALF:.6f} {-Z_HALF:.6f})
    ({X0:.6f} {Y_HALF:.6f} {-Z_HALF:.6f})
    ({X1:.6f} {Y_HALF:.6f} {-Z_HALF:.6f})
    ({X2:.6f} {Y_HALF:.6f} {-Z_HALF:.6f})
    ({X3:.6f} {Y_HALF:.6f} {-Z_HALF:.6f})

    ({X0:.6f} {-Y_HALF:.6f} {Z_HALF:.6f})
    ({X1:.6f} {-Y_HALF:.6f} {Z_HALF:.6f})
    ({X2:.6f} {-Y_HALF:.6f} {Z_HALF:.6f})
    ({X3:.6f} {-Y_HALF:.6f} {Z_HALF:.6f})
    ({X0:.6f} {Y_HALF:.6f} {Z_HALF:.6f})
    ({X1:.6f} {Y_HALF:.6f} {Z_HALF:.6f})
    ({X2:.6f} {Y_HALF:.6f} {Z_HALF:.6f})
    ({X3:.6f} {Y_HALF:.6f} {Z_HALF:.6f})
);

blocks
(
    hex (0 1 5 4 8 9 13 12)   (12 16 6) simpleGrading (1 1 1)
    hex (1 2 6 5 9 10 14 13)  (14 16 6) simpleGrading (1 1 1)
    hex (2 3 7 6 10 11 15 14) (48 16 6) simpleGrading (1 1 1)
);

edges ();

boundary
(
    inlet
    {{
        type patch;
        faces
        (
            (0 8 12 4)
        );
    }}

    outlet
    {{
        type patch;
        faces
        (
            (3 7 15 11)
        );
    }}

    bottom
    {{
        type {bottom_type};
        faces
        (
            (0 1 9 8)
            (1 2 10 9)
            (2 3 11 10)
        );
    }}

    top
    {{
        type {top_type};
        faces
        (
            (4 12 13 5)
            (5 13 14 6)
            (6 14 15 7)
        );
    }}

    front
    {{
        type symmetryPlane;
        faces
        (
            (0 4 5 1)
            (1 5 6 2)
            (2 6 7 3)
        );
    }}

    back
    {{
        type symmetryPlane;
        faces
        (
            (8 9 13 12)
            (9 10 14 13)
            (10 11 15 14)
        );
    }}
);

mergePatchPairs ();
"""


def snappy_hex_mesh_dict(
    *,
    cylinder_level: int = 2,
    near_level: int = 1,
    wake_level: int = 0,
) -> str:
    return f"""FoamFile
{{
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
        type    searchableCylinder;
        point1  (0 0 {-Z_HALF:.6f});
        point2  (0 0  {Z_HALF:.6f});
        radius  {RADIUS:.6f};
    }}

    nearCylinder
    {{
        type searchableBox;
        min ({NEAR_MIN_X:.6f} {-NEAR_HALF_Y:.6f} {-Z_HALF:.6f});
        max ({NEAR_MAX_X:.6f}  {NEAR_HALF_Y:.6f}  {Z_HALF:.6f});
    }}

    wakeBox
    {{
        type searchableBox;
        min ({WAKE_MIN_X:.6f} {-WAKE_HALF_Y:.6f} {-Z_HALF:.6f});
        max ({WAKE_MAX_X:.6f}  {WAKE_HALF_Y:.6f}  {Z_HALF:.6f});
    }}
}}

castellatedMeshControls
{{
    maxLocalCells           800000;
    maxGlobalCells          3000000;
    minRefinementCells      0;
    maxLoadUnbalance        0.10;
    nCellsBetweenLevels     3;
    resolveFeatureAngle     30;
    features ();

    refinementSurfaces
    {{
        cylinder
        {{
            level   ({cylinder_level} {cylinder_level});
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
            mode    inside;
            levels  ((1e15 {near_level}));
        }}
        wakeBox
        {{
            mode    inside;
            levels  ((1e15 {wake_level}));
        }}
    }}

    locationInMesh (-0.030 0 0);
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

writeFlags ( scalarLevels );
mergeTolerance 1e-6;
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
value           (0 -9.81 0);
"""


def physical_properties(*, cv: float = CV) -> str:
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
        Cv              {cv:.6f};
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


def p_file(top_type: str, bottom_type: str) -> str:
    top_patch = "symmetryPlane" if top_type == "symmetryPlane" else "calculated"
    bottom_patch = "symmetryPlane" if bottom_type == "symmetryPlane" else "calculated"
    return f"""FoamFile
{{
    format      ascii;
    class       volScalarField;
    object      p;
}}

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{{
    inlet {{ type calculated; value $internalField; }}
    outlet {{ type calculated; value $internalField; }}
    bottom {{ type {bottom_patch}; value $internalField; }}
    top {{ type {top_patch}; value $internalField; }}
    cylinder {{ type calculated; value $internalField; }}
    front {{ type symmetryPlane; }}
    back {{ type symmetryPlane; }}
}}
"""


def p_rgh_file(top_type: str, bottom_type: str) -> str:
    top_patch = "symmetryPlane" if top_type == "symmetryPlane" else "fixedFluxPressure"
    bottom_patch = "symmetryPlane" if bottom_type == "symmetryPlane" else "fixedFluxPressure"
    top_tail = "" if top_patch == "symmetryPlane" else " value uniform 0;"
    bottom_tail = "" if bottom_patch == "symmetryPlane" else " value uniform 0;"
    return f"""FoamFile
{{
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}}

dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{{
    inlet {{ type fixedFluxPressure; value uniform 0; }}
    outlet {{ type fixedValue; value uniform 0; }}
    bottom {{ type {bottom_patch};{bottom_tail} }}
    top {{ type {top_patch};{top_tail} }}
    cylinder {{ type fixedFluxPressure; value uniform 0; }}
    front {{ type symmetryPlane; }}
    back {{ type symmetryPlane; }}
}}
"""


def alphat_file(top_type: str, bottom_type: str) -> str:
    top_patch = "symmetryPlane" if top_type == "symmetryPlane" else "calculated"
    bottom_patch = "symmetryPlane" if bottom_type == "symmetryPlane" else "calculated"
    return f"""FoamFile
{{
    format      ascii;
    class       volScalarField;
    object      alphat;
}}

dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;

boundaryField
{{
    inlet {{ type calculated; value uniform 0; }}
    outlet {{ type calculated; value uniform 0; }}
    bottom {{ type {bottom_patch}; value uniform 0; }}
    top {{ type {top_patch}; value uniform 0; }}
    cylinder {{ type calculated; value uniform 0; }}
    front {{ type symmetryPlane; }}
    back {{ type symmetryPlane; }}
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


def decompose_par_dict(nprocs: int) -> str:
    return f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}}

numberOfSubdomains {nprocs};
method scotch;
"""


def allrun_file(of_bashrc: str, nprocs: int) -> str:
    return f"""#!/usr/bin/env bash
export ZSH_NAME="${{ZSH_NAME-}}"
source {of_bashrc}
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
blockMesh | tee logs/log.blockMesh
snappyHexMesh -overwrite | tee logs/log.snappyHexMesh
checkMesh -allTopology -allGeometry | tee logs/log.checkMesh
postProcess -func writeCellCentres -time 0 | tee logs/log.writeCellCentres
decomposePar -force | tee logs/log.decomposePar
mpirun --use-hwthread-cpus -np {nprocs} foamRun -solver fluid -parallel | tee logs/log.foamRun
"""
