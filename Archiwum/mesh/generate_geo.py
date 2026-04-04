#!/usr/bin/env python3
"""
Generate Gmsh .geo files for V&V study: confined circular cylinder in channel.

Geometry (from plan):
  D    = 12 mm   cylinder diameter
  Pt   = 32 mm   transverse pitch = channel height (blockage beta = D/Pt = 0.375)
  L_in = 96 mm   inlet stretch (8D upstream)
  L_out= 240 mm  outlet stretch (20D downstream)
  Lz   = 2.86 mm z-span (air gap between fins)

Three mesh levels for grid independence study:
  coarse  -intentionally under-resolved (GCI lower bound, expected deviation > 5%)
  medium  -MINIMUM resolution that matches confined-cylinder literature (~400-700K cells)
  fine    -clearly over-resolved (GCI upper bound, for convergence confirmation)

The medium mesh targets Sahin & Owens (2004) / Singha & Sinhamahapatra (2010) accuracy
for the 2D confined cylinder at beta = 0.375, Re = 100.

Usage:
    python generate_geo.py
Outputs:
    cylinder_channel_coarse.geo
    cylinder_channel_medium.geo
    cylinder_channel_fine.geo
"""

import os
import math

# ============================================================
# FIXED GEOMETRY
# ============================================================
D     = 0.012       # cylinder diameter [m]
R     = D / 2       # radius
Pt    = 0.032       # channel height (transverse pitch) [m]
L_in  = 0.096       # 8D upstream [m]
L_out = 0.240       # 20D downstream [m]
Lz    = 0.00286     # fin-to-fin gap [m]

# ============================================================
# MESH PARAMETER SETS
# ============================================================
#
# Design philosophy:
#   medium -each parameter is chosen at the minimum value that keeps
#            discretisation error < 2-3% vs. literature reference data
#            for Cd, St, Nu at Re=100, beta=0.375 (laminar, no turbulence model).
#
#   coarse -all parameters approximately halved from medium; expected GCI > 5%
#            so it serves as the "clearly coarser" point on the convergence curve.
#
#   fine   -all parameters approximately doubled from medium; expected GCI < 0.5%
#            serves as the "clearly finer" reference for Richardson extrapolation.
#
# Boundary layer on cylinder (r-direction):
#   dr1     = first cell height at cylinder wall
#   N_bl    = number of BL layers
#   bl_r    = growth ratio for BL
#   N_circ  = circumferential divisions on cylinder perimeter
#
# Wake and background (x-y plane):
#   dw      = target cell size in near-wake box (cylinder to 5D downstream)
#   dbg     = background cell size away from wake
#
# Z-direction (fin walls):
#   N_z     = total cells in z (must be even -symmetric BL on both fin walls)
#   z_r     = geometric growth ratio from fin wall toward channel midplane
#
# Estimated 3-D cell counts (approximate):
#   coarse  ~ 60 000 – 120 000
#   medium  ~ 400 000 – 700 000
#   fine    ~ 2 500 000 – 4 000 000

LEVELS = {
    "coarse": dict(
        dr1    = 0.00015,   # 0.15 mm  -y+ ~ 2-4, under-resolved BL
        N_bl   = 10,
        bl_r   = 1.25,
        N_circ = 40,        # 9 deg/cell -coarse stagnation region
        dw     = 0.0010,    # 1.0 mm near-wake
        dbg    = 0.0025,    # 2.5 mm background
        N_z    = 6,         # 3 cells each half-span
        z_r    = 1.30,
    ),
    "medium": dict(
        # ---- minimum-resolution literature-matching mesh ----
        # 80 circumferential cells ->4.5 deg/cell, adequate for laminar Re=100
        # dr1=0.05 mm ->y+ ~ 0.3-0.8 at stagnation (wall-resolved laminar BL)
        # 15 BL layers at ratio 1.2 ->BL extent ~ 3.7 mm > estimated delta_BL ~ 1.5 mm
        # dw = 0.4 mm = D/30 in near-wake ->resolves Kármán vortex street
        # N_z = 12 ->6 cells per half-span, enough for quasi-2D flow (Lz/D = 0.238)
        dr1    = 0.00005,   # 0.05 mm
        N_bl   = 15,
        bl_r   = 1.20,
        N_circ = 80,
        dw     = 0.0004,    # 0.4 mm
        dbg    = 0.0010,    # 1.0 mm
        N_z    = 12,
        z_r    = 1.20,
    ),
    "fine": dict(
        dr1    = 0.00002,   # 0.02 mm  -y+ < 0.3
        N_bl   = 20,
        bl_r   = 1.15,
        N_circ = 140,       # 2.6 deg/cell
        dw     = 0.00015,   # 0.15 mm
        dbg    = 0.00050,   # 0.5 mm
        N_z    = 20,        # 10 cells per half-span
        z_r    = 1.15,
    ),
}


def bl_extent(dr1, N_bl, r):
    """Total radial extent of the BL layer stack."""
    if abs(r - 1.0) < 1e-12:
        return dr1 * N_bl
    return dr1 * (r**N_bl - 1.0) / (r - 1.0)


def z_layers(Lz, N_z, z_r):
    """
    Symmetric geometric progression for z-extrusion.

    N_z cells total, half from each fin wall, meeting at midplane.
    Returns (dz1, layer_fractions) where layer_fractions is a list of N_z
    cumulative heights normalised to 1.0 (last entry = 1.0).
    """
    assert N_z % 2 == 0, "N_z must be even"
    N_h = N_z // 2
    r   = z_r
    # dz1 * sum_{i=0}^{N_h-1} r^i = Lz/2
    if abs(r - 1.0) < 1e-12:
        dz1 = (Lz / 2.0) / N_h
    else:
        dz1 = (Lz / 2.0) * (r - 1.0) / (r**N_h - 1.0)

    # individual layer heights: grow from z=0, then mirror for z=Lz half
    h_half = [dz1 * r**i for i in range(N_h)]
    heights = h_half + h_half[::-1]

    # cumulative, normalised
    total = sum(heights)
    cum   = []
    s     = 0.0
    for h in heights:
        s += h
        cum.append(s / total)
    cum[-1] = 1.0   # ensure exactly 1.0

    return dz1, heights, cum


def write_geo(level_name, p):
    """Write a complete Gmsh .geo file for the given mesh level."""

    dz1, z_h, z_cum = z_layers(Lz, p["N_z"], p["z_r"])
    bl_thick         = bl_extent(p["dr1"], p["N_bl"], p["bl_r"])

    # Gmsh Layers{} strings
    N_z      = p["N_z"]
    lay_n    = ", ".join(["1"] * N_z)
    lay_h    = ", ".join(f"{f:.7f}" for f in z_cum)
    lay_h_mm = ", ".join(f"{h*1e3:.4f}" for h in z_h)

    fname = f"cylinder_channel_{level_name}.geo"
    with open(fname, "w", encoding="utf-8") as fh:
        fh.write(f"""\
// ============================================================
// Gmsh mesh: Confined circular cylinder in heated channel
// V&V Phase 0 -buoyantPimpleFoam (ESI OpenFOAM)
//
// Mesh level : {level_name}
// Geometry   : D={D*1e3:.0f} mm, Pt={Pt*1e3:.0f} mm, beta={D/Pt:.3f},
//              L_in={L_in*1e3:.0f} mm (8D), L_out={L_out*1e3:.0f} mm (20D),
//              Lz={Lz*1e3:.2f} mm (Lz/D={Lz/D:.3f})
//
// Mesh parameters ({level_name}):
//   dr1     = {p["dr1"]*1e3:.4f} mm   first cell height at cylinder wall
//   N_bl    = {p["N_bl"]}           BL layers on cylinder, ratio {p["bl_r"]}
//   N_circ  = {p["N_circ"]}          circumferential cells on cylinder
//   BL ext  = {bl_thick*1e3:.3f} mm   total BL stack thickness
//   dw      = {p["dw"]*1e3:.3f} mm   near-wake cell size (0 ->5D)
//   dbg     = {p["dbg"]*1e3:.3f} mm   background cell size
//   N_z     = {N_z}           z-direction cells (symmetric, {N_z//2} per half)
//   dz1     = {dz1*1e3:.4f} mm   first z-cell at fin wall, ratio {p["z_r"]}
//   z layers (mm): {lay_h_mm}
//
// OpenFOAM patches:
//   inlet      -x = {-L_in:.4f} m  (velocity inlet)
//   outlet     -x = {+L_out:.4f} m  (pressure outlet)
//   topWall    -y = +{Pt/2:.5f} m  (symmetryPlane)
//   bottomWall -y = -{Pt/2:.5f} m  (symmetryPlane)
//   finBottom  -z = 0              (heated fin, Tw = 343.15 K)
//   finTop     -z = {Lz:.5f} m  (heated fin, Tw = 343.15 K)
//   cylinder   -curved wall        (heated cylinder, Tw = 343.15 K)
//   fluid      -interior volume
//
// Conversion:
//   gmsh cylinder_channel_{level_name}.geo -3 -format msh2 \\
//        -o cylinder_{level_name}.msh
//   gmshToFoam cylinder_{level_name}.msh
//   checkMesh
//
// After gmshToFoam, verify patch names with:
//   foamInfo boundary   (or grep 'type' constant/polyMesh/boundary)
// ============================================================

// ===================================================
// GEOMETRY CONSTANTS
// ===================================================
D     = {D};
R     = D/2;
Pt    = {Pt};
L_in  = {L_in};
L_out = {L_out};
Lz    = {Lz};

x_in  = -L_in;
x_out =  L_out;
y_lo  = -Pt/2;
y_hi  = +Pt/2;

// ===================================================
// 2-D POINTS  (z = 0 plane)
// ===================================================

// Channel corners (mesh size = background)
p1 = newp; Point(p1) = {{x_in,  y_lo, 0, {p["dbg"]}}};
p2 = newp; Point(p2) = {{x_out, y_lo, 0, {p["dbg"]}}};
p3 = newp; Point(p3) = {{x_out, y_hi, 0, {p["dbg"]}}};
p4 = newp; Point(p4) = {{x_in,  y_hi, 0, {p["dbg"]}}};

// Inlet/outlet midpoints (for structured inlet zone if needed -currently unused)
// Cylinder: centre + 4 cardinal points (N, E, S, W)
pc = newp; Point(pc) = {{0, 0, 0}};               // centre (no mesh node)
pE = newp; Point(pE) = {{ R, 0, 0, {p["dr1"]}}};
pN = newp; Point(pN) = {{0,  R, 0, {p["dr1"]}}};
pW = newp; Point(pW) = {{-R, 0, 0, {p["dr1"]}}};
pS = newp; Point(pS) = {{0, -R, 0, {p["dr1"]}}};

// ===================================================
// 2-D LINES & ARCS  (z = 0 plane)
// ===================================================

// Channel boundary -CCW when viewed from +z
l_bottom = newl; Line(l_bottom) = {{p1, p2}};  // y = y_lo  ->bottomWall
l_outlet = newl; Line(l_outlet) = {{p2, p3}};  // x = x_out ->outlet
l_top    = newl; Line(l_top)    = {{p3, p4}};  // y = y_hi  ->topWall
l_inlet  = newl; Line(l_inlet)  = {{p4, p1}};  // x = x_in  ->inlet

// Cylinder arcs -CCW (same winding as outer loop)
c1 = newl; Circle(c1) = {{pE, pc, pN}};  // quadrant I   (0° ->90°)
c2 = newl; Circle(c2) = {{pN, pc, pW}};  // quadrant II  (90° ->180°)
c3 = newl; Circle(c3) = {{pW, pc, pS}};  // quadrant III (180° ->270°)
c4 = newl; Circle(c4) = {{pS, pc, pE}};  // quadrant IV  (270° ->360°)

// ===================================================
// 2-D SURFACE  (channel cross-section with cylinder hole)
// ===================================================
// Outer loop CCW, inner (cylinder) loop CCW  ->subtract with -cl_cyl
cl_outer = newll; Curve Loop(cl_outer) = {{l_bottom, l_outlet, l_top, l_inlet}};
cl_cyl   = newll; Curve Loop(cl_cyl)   = {{c1, c2, c3, c4}};

s_base = news; Plane Surface(s_base) = {{cl_outer, -cl_cyl}};

// ===================================================
// MESH SIZE FIELDS
// ===================================================

// --- Field 1: Distance from cylinder surface ---
Field[1] = Distance;
Field[1].CurvesList = {{c1, c2, c3, c4}};
Field[1].Sampling   = 200;

// --- Field 2: Threshold -fine near cylinder, coarser beyond BL ---
// SizeMin at wall, transition to dw at BL edge, to dbg at D from wall
Field[2] = Threshold;
Field[2].InField  = 1;
Field[2].SizeMin  = {p["dr1"]};
Field[2].SizeMax  = {p["dw"]};
Field[2].DistMin  = {bl_thick:.7f};   // BL outer edge
Field[2].DistMax  = {D:.6f};           // 1 diameter from wall

// --- Field 3: Box -near-wake refinement (cylinder to 5D downstream) ---
Field[3] = Box;
Field[3].XMin = {-1.5*R:.6f};
Field[3].XMax = {5.0*D:.6f};
Field[3].YMin = {-1.5*R:.6f};
Field[3].YMax = {+1.5*R:.6f};
Field[3].ZMin = -0.01;
Field[3].ZMax = Lz + 0.01;
Field[3].VIn  = {p["dw"]};
Field[3].VOut = {p["dbg"]};

// --- Field 4: Box -mid-wake refinement (5D to 10D downstream) ---
Field[4] = Box;
Field[4].XMin = {5.0*D:.6f};
Field[4].XMax = {10.0*D:.6f};
Field[4].YMin = {-2.0*R:.6f};
Field[4].YMax = {+2.0*R:.6f};
Field[4].ZMin = -0.01;
Field[4].ZMax = Lz + 0.01;
Field[4].VIn  = {2*p["dw"]:.6f};
Field[4].VOut = {p["dbg"]};

// --- Field 5: combine (minimum of all size fields) ---
Field[5] = Min;
Field[5].FieldsList = {{2, 3, 4}};

Background Field = 5;

// --- BoundaryLayer field: structured quad layers around cylinder ---
// (overrides Background Field near the cylinder)
Field[10] = BoundaryLayer;
Field[10].CurvesList    = {{c1, c2, c3, c4}};
Field[10].PointsList    = {{pE, pN, pW, pS}};
Field[10].FanPointsList = {{pE, pN, pW, pS}};
Field[10].Size          = {p["dr1"]};
Field[10].Ratio         = {p["bl_r"]};
Field[10].NbLayers      = {p["N_bl"]};
Field[10].Quads         = 1;

BoundaryLayer Field = 10;

// ===================================================
// 2-D MESH SETTINGS
// ===================================================
Mesh.Algorithm                             = 6;   // Frontal-Delaunay (best with BL)
Mesh.RecombineAll                          = 0;   // quads in BL, tris elsewhere
Mesh.CharacteristicLengthMin               = {p["dr1"]/2:.8f};
Mesh.CharacteristicLengthMax               = {p["dbg"]};
Mesh.CharacteristicLengthExtendFromBoundary= 0;
Mesh.BoundaryLayerFanElements              = 5;
Mesh.Optimize                             = 1;
Mesh.OptimizeThreshold                    = 0.5;

// Circumferential seeding -enforces N_circ cells on the cylinder perimeter
// Arc length = pi*D/2 per quadrant; size = pi*D/(2*N_circ_per_quarter)
N_circ_quarter = {p["N_circ"] // 4};  // cells per arc (quarter circle)
Transfinite Curve{{c1, c2, c3, c4}} = N_circ_quarter + 1;

// ===================================================
// 3-D EXTRUSION  (z = 0  -> z = Lz)
// ===================================================
// Symmetric geometric BL on both fin walls.
// Layer heights (mm): {lay_h_mm}
// Cumulative fractions: first={z_cum[0]:.5f}, mid={z_cum[N_z//2-1]:.5f}, last=1.0
//
// ext[] after Extrude{{Surface{{s_base}}; ...}}:
//   ext[0] = finTop  surface  (z = Lz)
//   ext[1] = fluid   volume
//   ext[2] = bottomWall surface (from l_bottom)
//   ext[3] = outlet  surface  (from l_outlet)
//   ext[4] = topWall surface  (from l_top)
//   ext[5] = inlet   surface  (from l_inlet)
//   ext[6..9] = cylinder arcs 1-4 extruded surfaces
// NOTE: If BoundaryLayer field adds extra internal curves the indices above may
//       shift by +1 or +2. Verify with: Tools ->Statistics in Gmsh GUI,
//       or inspect constant/polyMesh/boundary after gmshToFoam.

ext[] = Extrude {{0, 0, Lz}} {{
    Surface{{s_base}};
    Layers{{
        {{{lay_n}}},
        {{{lay_h}}}
    }};
    Recombine;
}};

// ===================================================
// PHYSICAL GROUPS  (→ OpenFOAM patch names)
// ===================================================
Physical Volume("fluid")      = {{ext[1]}};
Physical Surface("finBottom") = {{s_base}};
Physical Surface("finTop")    = {{ext[0]}};
Physical Surface("bottomWall")= {{ext[2]}};
Physical Surface("outlet")    = {{ext[3]}};
Physical Surface("topWall")   = {{ext[4]}};
Physical Surface("inlet")     = {{ext[5]}};
Physical Surface("cylinder")  = {{ext[6], ext[7], ext[8], ext[9]}};
""")
    print(f"  Written: {fname}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("Generating Gmsh .geo files for confined cylinder V&V meshing")
    print(f"  D={D*1e3:.0f} mm, Pt={Pt*1e3:.0f} mm, beta={D/Pt:.3f}, "
          f"L={L_in*1e3:.0f}+{L_out*1e3:.0f} mm, Lz={Lz*1e3:.2f} mm\n")

    for level_name, params in LEVELS.items():
        # diagnostic printout
        dz1, z_h, z_cum = z_layers(Lz, params["N_z"], params["z_r"])
        thick = bl_extent(params["dr1"], params["N_bl"], params["bl_r"])
        print(f"--- {level_name.upper()} ---")
        print(f"  Cyl BL  : dr1={params['dr1']*1e3:.4f} mm, "
              f"N_bl={params['N_bl']}, r={params['bl_r']}, extent={thick*1e3:.3f} mm")
        print(f"  N_circ  : {params['N_circ']} (arc spacing ~{math.pi*D/params['N_circ']*1e3:.3f} mm)")
        print(f"  Wake    : dw={params['dw']*1e3:.3f} mm, dbg={params['dbg']*1e3:.3f} mm")
        print(f"  Z-dir   : N_z={params['N_z']}, dz1={dz1*1e3:.4f} mm, "
              f"sum={sum(z_h)*1e3:.4f} mm (Lz={Lz*1e3:.2f} mm)")
        write_geo(level_name, params)
        print()

    print("Done.  Next steps:")
    print("  bash generate_meshes.sh coarse   (or medium / fine)")
    print("  bash generate_meshes.sh all")
