// ============================================================
// Gmsh mesh: Confined circular cylinder in heated channel
// V&V Phase 0 -buoyantPimpleFoam (ESI OpenFOAM)
//
// Mesh level : fine
// Geometry   : D=12 mm, Pt=32 mm, beta=0.375,
//              L_in=96 mm (8D), L_out=240 mm (20D),
//              Lz=2.86 mm (Lz/D=0.238)
//
// Mesh parameters (fine):
//   dr1     = 0.0200 mm   first cell height at cylinder wall
//   N_bl    = 20           BL layers on cylinder, ratio 1.15
//   N_circ  = 140          circumferential cells on cylinder
//   BL ext  = 2.049 mm   total BL stack thickness
//   dw      = 0.150 mm   near-wake cell size (0 ->5D)
//   dbg     = 0.500 mm   background cell size
//   N_z     = 20           z-direction cells (symmetric, 10 per half)
//   dz1     = 0.0704 mm   first z-cell at fin wall, ratio 1.15
//   z layers (mm): 0.0704, 0.0810, 0.0931, 0.1071, 0.1232, 0.1417, 0.1629, 0.1873, 0.2154, 0.2478, 0.2478, 0.2154, 0.1873, 0.1629, 0.1417, 0.1232, 0.1071, 0.0931, 0.0810, 0.0704
//
// OpenFOAM patches:
//   inlet      -x = -0.0960 m  (velocity inlet)
//   outlet     -x = 0.2400 m  (pressure outlet)
//   topWall    -y = +0.01600 m  (symmetryPlane)
//   bottomWall -y = -0.01600 m  (symmetryPlane)
//   finBottom  -z = 0              (heated fin, Tw = 343.15 K)
//   finTop     -z = 0.00286 m  (heated fin, Tw = 343.15 K)
//   cylinder   -curved wall        (heated cylinder, Tw = 343.15 K)
//   fluid      -interior volume
//
// Conversion:
//   gmsh cylinder_channel_fine.geo -3 -format msh2 \
//        -o cylinder_fine.msh
//   gmshToFoam cylinder_fine.msh
//   checkMesh
//
// After gmshToFoam, verify patch names with:
//   foamInfo boundary   (or grep 'type' constant/polyMesh/boundary)
// ============================================================

// ===================================================
// GEOMETRY CONSTANTS
// ===================================================
D     = 0.012;
R     = D/2;
Pt    = 0.032;
L_in  = 0.096;
L_out = 0.24;
Lz    = 0.00286;

x_in  = -L_in;
x_out =  L_out;
y_lo  = -Pt/2;
y_hi  = +Pt/2;

// ===================================================
// 2-D POINTS  (z = 0 plane)
// ===================================================

// Channel corners (mesh size = background)
p1 = newp; Point(p1) = {x_in,  y_lo, 0, 0.0005};
p2 = newp; Point(p2) = {x_out, y_lo, 0, 0.0005};
p3 = newp; Point(p3) = {x_out, y_hi, 0, 0.0005};
p4 = newp; Point(p4) = {x_in,  y_hi, 0, 0.0005};

// Inlet/outlet midpoints (for structured inlet zone if needed -currently unused)
// Cylinder: centre + 4 cardinal points (N, E, S, W)
pc = newp; Point(pc) = {0, 0, 0};               // centre (no mesh node)
pE = newp; Point(pE) = { R, 0, 0, 2e-05};
pN = newp; Point(pN) = {0,  R, 0, 2e-05};
pW = newp; Point(pW) = {-R, 0, 0, 2e-05};
pS = newp; Point(pS) = {0, -R, 0, 2e-05};

// ===================================================
// 2-D LINES & ARCS  (z = 0 plane)
// ===================================================

// Channel boundary -CCW when viewed from +z
l_bottom = newl; Line(l_bottom) = {p1, p2};  // y = y_lo  ->bottomWall
l_outlet = newl; Line(l_outlet) = {p2, p3};  // x = x_out ->outlet
l_top    = newl; Line(l_top)    = {p3, p4};  // y = y_hi  ->topWall
l_inlet  = newl; Line(l_inlet)  = {p4, p1};  // x = x_in  ->inlet

// Cylinder arcs -CCW (same winding as outer loop)
c1 = newl; Circle(c1) = {pE, pc, pN};  // quadrant I   (0° ->90°)
c2 = newl; Circle(c2) = {pN, pc, pW};  // quadrant II  (90° ->180°)
c3 = newl; Circle(c3) = {pW, pc, pS};  // quadrant III (180° ->270°)
c4 = newl; Circle(c4) = {pS, pc, pE};  // quadrant IV  (270° ->360°)

// ===================================================
// 2-D SURFACE  (channel cross-section with cylinder hole)
// ===================================================
// Outer loop CCW, inner (cylinder) loop CCW  ->subtract with -cl_cyl
cl_outer = newll; Curve Loop(cl_outer) = {l_bottom, l_outlet, l_top, l_inlet};
cl_cyl   = newll; Curve Loop(cl_cyl)   = {c1, c2, c3, c4};

s_base = news; Plane Surface(s_base) = {cl_outer, -cl_cyl};

// ===================================================
// MESH SIZE FIELDS
// ===================================================

// --- Field 1: Distance from cylinder surface ---
Field[1] = Distance;
Field[1].CurvesList = {c1, c2, c3, c4};
Field[1].Sampling   = 200;

// --- Field 2: Threshold -fine near cylinder, coarser beyond BL ---
// SizeMin at wall, transition to dw at BL edge, to dbg at D from wall
Field[2] = Threshold;
Field[2].InField  = 1;
Field[2].SizeMin  = 2e-05;
Field[2].SizeMax  = 0.00015;
Field[2].DistMin  = 0.0020489;   // BL outer edge
Field[2].DistMax  = 0.012000;           // 1 diameter from wall

// --- Field 3: Box -near-wake refinement (cylinder to 5D downstream) ---
Field[3] = Box;
Field[3].XMin = -0.009000;
Field[3].XMax = 0.060000;
Field[3].YMin = -0.009000;
Field[3].YMax = 0.009000;
Field[3].ZMin = -0.01;
Field[3].ZMax = Lz + 0.01;
Field[3].VIn  = 0.00015;
Field[3].VOut = 0.0005;

// --- Field 4: Box -mid-wake refinement (5D to 10D downstream) ---
Field[4] = Box;
Field[4].XMin = 0.060000;
Field[4].XMax = 0.120000;
Field[4].YMin = -0.012000;
Field[4].YMax = 0.012000;
Field[4].ZMin = -0.01;
Field[4].ZMax = Lz + 0.01;
Field[4].VIn  = 0.000300;
Field[4].VOut = 0.0005;

// --- Field 5: combine (minimum of all size fields) ---
Field[5] = Min;
Field[5].FieldsList = {2, 3, 4};

Background Field = 5;

// --- BoundaryLayer field: structured quad layers around cylinder ---
// (overrides Background Field near the cylinder)
Field[10] = BoundaryLayer;
Field[10].CurvesList    = {c1, c2, c3, c4};
Field[10].PointsList    = {pE, pN, pW, pS};
Field[10].FanPointsList = {pE, pN, pW, pS};
Field[10].Size          = 2e-05;
Field[10].Ratio         = 1.15;
Field[10].NbLayers      = 20;
Field[10].Quads         = 1;

BoundaryLayer Field = 10;

// ===================================================
// 2-D MESH SETTINGS
// ===================================================
Mesh.Algorithm                             = 6;   // Frontal-Delaunay (best with BL)
Mesh.RecombineAll                          = 0;   // quads in BL, tris elsewhere
Mesh.CharacteristicLengthMin               = 0.00001000;
Mesh.CharacteristicLengthMax               = 0.0005;
Mesh.CharacteristicLengthExtendFromBoundary= 0;
Mesh.BoundaryLayerFanElements              = 5;
Mesh.Optimize                             = 1;
Mesh.OptimizeThreshold                    = 0.5;

// Circumferential seeding -enforces N_circ cells on the cylinder perimeter
// Arc length = pi*D/2 per quadrant; size = pi*D/(2*N_circ_per_quarter)
N_circ_quarter = 35;  // cells per arc (quarter circle)
Transfinite Curve{c1, c2, c3, c4} = N_circ_quarter + 1;

// ===================================================
// 3-D EXTRUSION  (z = 0  -> z = Lz)
// ===================================================
// Symmetric geometric BL on both fin walls.
// Layer heights (mm): 0.0704, 0.0810, 0.0931, 0.1071, 0.1232, 0.1417, 0.1629, 0.1873, 0.2154, 0.2478, 0.2478, 0.2154, 0.1873, 0.1629, 0.1417, 0.1232, 0.1071, 0.0931, 0.0810, 0.0704
// Cumulative fractions: first=0.02463, mid=0.50000, last=1.0
//
// ext[] after Extrude{Surface{s_base}; ...}:
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

ext[] = Extrude {0, 0, Lz} {
    Surface{s_base};
    Layers{
        {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
        {0.0246260, 0.0529460, 0.0855139, 0.1229670, 0.1660381, 0.2155698, 0.2725313, 0.3380371, 0.4133687, 0.5000000, 0.5866313, 0.6619629, 0.7274687, 0.7844302, 0.8339619, 0.8770330, 0.9144861, 0.9470540, 0.9753740, 1.0000000}
    };
    Recombine;
};

// ===================================================
// PHYSICAL GROUPS  (→ OpenFOAM patch names)
// ===================================================
Physical Volume("fluid")      = {ext[1]};
Physical Surface("finBottom") = {s_base};
Physical Surface("finTop")    = {ext[0]};
Physical Surface("bottomWall")= {ext[2]};
Physical Surface("outlet")    = {ext[3]};
Physical Surface("topWall")   = {ext[4]};
Physical Surface("inlet")     = {ext[5]};
Physical Surface("cylinder")  = {ext[6], ext[7], ext[8], ext[9]};
