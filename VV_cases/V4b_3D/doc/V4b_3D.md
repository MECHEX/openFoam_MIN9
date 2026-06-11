# V4b 3D Production Case

## Objective

This document is the canonical technical description for the full 3D thermal production case.

The current target geometry is a single fin-pitch unit cell of a fin-and-tube heat exchanger:
air flows in the streamwise `x` direction, the transverse pitch is represented by the `y`
extent, and the fin-to-fin spacing is represented by the `z` extent.

![V4b geometry concept](figs/v4b_geometry_concept.svg)

## Coordinate system

| direction | meaning | domain interval |
|---|---|---:|
| `x` | streamwise air-flow direction | `0 <= x <= Lx` |
| `y` | transverse tube-pitch direction | `-H/2 <= y <= H/2` |
| `z` | fin-pitch / tube-axis direction | `0 <= z <= Lz` |

The same geometry may also be written with `0 <= y <= H`; in that convention the cylinder
center is at `y = H/2`.

## Accepted dimensions

| quantity | symbol | value | normalized value |
|---|---:|---:|---:|
| tube/cylinder diameter | `D` | `12.00 mm` | `1.000 D` |
| cylinder radius | `R = D/2` | `6.00 mm` | `0.500 D` |
| transverse pitch / channel height | `H = Pt` | `32.00 mm` | `2.667 D` |
| blockage ratio | `beta = D/H` | `0.375` | `-` |
| fin pitch / spanwise domain depth | `Lz` | `12.00 mm` | `1.000 D` |
| heated fin-zone length | `Lf` | `27.71 mm` | `2.309 D` |
| inlet extension | `Lin` | `24.00 mm` | `2.000 D` |
| outlet extension | `Lout` | `96.00 mm` | `8.000 D` |
| total streamwise length | `Lx = Lin + Lf + Lout` | `147.71 mm` | `12.309 D` |
| physical fin thickness | `tf` | `0.14 mm` | `0.0117 D` |

The fin thickness is not meshed as a solid volume in the baseline CFD model. The fins are
represented as constant-temperature wall boundary patches on the two `z` planes.

## Derived positions

| item | value |
|---|---:|
| inlet region | `0 <= x < 24.00 mm` |
| heated fin region | `24.00 <= x <= 51.71 mm` |
| outlet region | `51.71 < x <= 147.71 mm` |
| cylinder center, `x` | `xc = Lin + Lf/2 = 37.855 mm` |
| cylinder center, centered `y` convention | `yc = 0.000 mm` |
| cylinder center, positive `y` convention | `yc = 16.000 mm` |
| cylinder axis | parallel to `z` |
| cylinder span | full `0 <= z <= 12.00 mm` fin pitch |

The cylinder is centered in the heated fin region. Its cross-section in the `x-y` plane is
defined by:

```text
(x - xc)^2 + y^2 = R^2
```

using the centered `y` convention. In the positive `y` convention:

```text
(x - xc)^2 + (y - H/2)^2 = R^2
```

## Heated surfaces

The baseline thermal model uses a constant wall temperature:

```text
T_hot = 343.15 K  = 70 C
T_in  = 293.15 K  = 20 C
Delta T = 50 K
```

Heated surfaces:

- cylinder/tube wall, full span `0 <= z <= Lz`
- fin wall at `z = 0`, only in the heated fin region `Lin <= x <= Lin + Lf`
- fin wall at `z = Lz`, only in the heated fin region `Lin <= x <= Lin + Lf`

The inlet and outlet extensions are not heated fin surfaces.

## Boundary-condition plan

The `z` faces must be split into separate patches because the fin region is a hot solid wall,
while the inlet and outlet extensions are not fins.

| boundary / patch | velocity | temperature | pressure |
|---|---|---|---|
| inlet, `x = 0` | fixed inlet velocity `U = (Uin, 0, 0)` | `fixedValue 293.15 K` | `zeroGradient` |
| outlet, `x = Lx` | `zeroGradient` or `inletOutlet` | `zeroGradient` or `inletOutlet` | fixed reference pressure |
| cylinder wall | `noSlip` | `fixedValue 343.15 K` | `zeroGradient` |
| fin walls, `z = 0/Lz`, fin region only | `noSlip` | `fixedValue 343.15 K` | `zeroGradient` |
| `z = 0/Lz`, inlet and outlet extensions | `symmetryPlane` baseline | no heat flux through symmetry plane | symmetry-plane pressure condition |
| `y = +/-H/2` | `symmetryPlane` baseline | no heat flux through symmetry plane | symmetry-plane pressure condition |

If the final physical model requires solid channel walls at `y = +/-H/2`, replace the baseline
`symmetryPlane` treatment there with `noSlip` and the selected thermal wall condition. For the
current fin-and-tube unit-cell interpretation, `y = +/-H/2` represents transverse symmetry between
neighboring tube rows.

## OpenFOAM-style patch intent

The exact patch names can change during meshing, but the intended split is:

```text
inlet
outlet
symmetry_y_min
symmetry_y_max
symmetry_z_min_inlet
symmetry_z_min_outlet
symmetry_z_max_inlet
symmetry_z_max_outlet
hot_fin_z_min
hot_fin_z_max
hot_tube
```

Example thermal intent:

```text
inlet
{
    type  fixedValue;
    value uniform 293.15;
}

hot_tube
{
    type  fixedValue;
    value uniform 343.15;
}

hot_fin_z_min
{
    type  fixedValue;
    value uniform 343.15;
}

hot_fin_z_max
{
    type  fixedValue;
    value uniform 343.15;
}

symmetry_y_min
{
    type symmetryPlane;
}

symmetry_y_max
{
    type symmetryPlane;
}
```

Example velocity intent:

```text
inlet
{
    type  fixedValue;
    value uniform (Uin 0 0);
}

hot_tube
{
    type  noSlip;
}

hot_fin_z_min
{
    type  noSlip;
}

hot_fin_z_max
{
    type  noSlip;
}

symmetry_y_min
{
    type symmetryPlane;
}

symmetry_y_max
{
    type symmetryPlane;
}
```

## Solver and physical model

The accepted V4b production run uses OpenFOAM 13:

```text
foamRun -solver fluid
```

with the stable Boussinesq thermophysical architecture established during the
V2/V4b debugging campaign. It gives two-way flow-temperature coupling without
requiring a solid-metal conduction region:

- velocity and pressure affect temperature through convective transport
- temperature affects momentum through the Boussinesq buoyancy term
- tube and fin metal are not meshed as solids
- tube and fin surfaces are represented as fixed-temperature wall patches

The old `V4b_3D/templates/base_case` still contains an earlier
`buoyantPimpleFoam` setup. That template should be treated as deprecated until
it is rebuilt.

The accepted `run008` production model is constant-property and Cp-consistent:

```text
T_in  = 293.15 K
T_hot = 343.15 K
DeltaT = 50 K
rho   = 1.205 kg/m3  (coefficient normalization)
mu    = 1.827e-5 Pa s
Pr    = 0.713
capacity coefficient = 1005 J/(kg K)
betaT = 3.41e-3 1/K
```

In OpenFOAM terms, `run008` inherited the `run007c` thermophysics:

```text
eConst + Boussinesq + sensibleInternalEnergy
```

with the energy-capacity coefficient changed from the earlier `718` to `1005`.
This is not the variable-property air model. The variable-property diagnostic
was `run007a`, using `incompressiblePerfectGas + Sutherland`; it changed drag
and thermal response in the short window but did not close the wall-air heat
balance sufficiently for production use. `run008` should therefore be described
as the accepted constant-property, Cp-consistent production reference.

The baseline gravity vector assumes `y` is the vertical direction:

```text
g = (0 -9.81 0)
```

If the physical exchanger orientation changes, only the gravity vector should be rotated.

Because `betaT * DeltaT` is about `0.17`, the Boussinesq approximation remains
a physics assumption. The existing variable-property `run007a` is useful as a
diagnostic, but a production-quality variable-property comparison would need a
closed energy balance before it can replace `run008`.

## Domain strategy

The documented V4b geometry is a physical compact unit-cell, not a numerically large free-cylinder
domain. The accepted production domain after controlled sensitivity checks is:

```text
Lin  = 2D   (24 mm)
Lf   = 2.309D
Lout = 8D   (96 mm)
H    = 2.667D
Lz   = 1D
```

For `Nu`, this is a meaningful physical starting point because heat transfer is
measured on the actual tube and fin surfaces. For `St`, `Cd`, wake structure,
and modal analysis, controlled variants were run before accepting the
production domain:

| variant | purpose |
|---|---|
| `Lout=8D` (`run004b`) | accepted outlet-domain candidate |
| `Lout=16D` (`run004c`) | matched `8D` for `Cd`, `St`, and `Nu_EB` |
| `Lin=4D` (`run005`) | matched `Lin=2D`; inlet sensitivity closed |
| `maxCo=0.4/1.0` checks (`run006a/b`) | supported `maxCo=0.8` as production default |
| `run007a` variable properties | diagnostic only; heat balance not production-ready |
| `run007c` Cp-capacity constant-property smoke test | accepted physics parent for `run008` |

## Measurement plan

The measurement plan is split into three levels so that mesh/domain checks remain cheap while final
modal runs still contain enough data for POD, EPOD, coherence, transfer entropy, and related
analyses.

### Level 1: every shakedown, mesh, and domain variant

These quantities are lightweight and should be written for every run:

```text
Nu_tube(t)
Nu_fin_z_min(t)
Nu_fin_z_max(t)
Nu_total_hot_surfaces(t)
Cd_tube(t)
Cl_tube(t)
pressure_drop(t)
T_min(t), T_max(t)
Courant(t)
residuals
mass balance
heat balance
```

This level is sufficient to decide whether the case is numerically healthy:

- temperature remains bounded
- residuals are acceptable
- heat and mass balances are plausible
- `Nu` and integral force signals are statistically stable
- domain and mesh changes do not shift key metrics beyond the accepted tolerance

### Level 2: unsteady-frequency and signal analysis

For cases where shedding or oscillatory heat transfer is expected, also write evenly sampled time
signals or signals that can be resampled later:

```text
Cl(t)
Cd(t)
Nu_total(t)
Nu_tube(t)
Nu_fin_z_min(t), Nu_fin_z_max(t)
q_wall_mean_tube(t)
q_wall_mean_fin(t)
pressure_drop(t)
selected U/T/p probes in the wake
selected U/T/p probes in the upper and lower gaps
```

This level supports:

- `St` from `Cl(t)`
- `St` from `Nu(t)` or `q_wall(t)`
- spectral coherence between wake dynamics and heat transfer
- transfer entropy between probe signals and heat-transfer response

### Level 3: final modal-analysis runs only

Full-field snapshots should be reserved for the selected final mesh/domain candidates, not for
every exploratory run.

Required final modal data:

```text
U(x,y,z,t)
T(x,y,z,t)
p_rgh(x,y,z,t)
vorticity or fields sufficient to compute it later
snGrad(T) or q_wall on hot_tube
snGrad(T) or q_wall on hot_fin_z_min
snGrad(T) or q_wall on hot_fin_z_max
local Nu(theta,z,t) on the tube if available
local Nu(x,y,t) on the fins if available
```

Useful sampled surfaces/planes:

```text
mid-span x-y plane
centerline x-z plane
several y-z wake cross-sections
tube wall map q_wall(theta,z,t)
fin wall maps q_wall(x,y,t)
```

This level supports:

- POD of velocity, temperature, pressure, or vorticity fields
- POD of wall heat-flux / local Nusselt maps
- EPOD from flow structures to wall heat-transfer structures
- coherence between POD temporal coefficients
- transfer entropy between modal coefficients or probe signals

Full modal recording should start only after the transient is rejected. For shedding cases, the
target sampling should be at least `50-100` samples per shedding period and should cover at least
`10-20` periods, preferably more for final statistics.

## Mesh requirements

The first V4b mesh does not need to be final, but it must be good enough to avoid misleading heat
transfer and shedding conclusions.

Baseline criteria:

| region / metric | target |
|---|---|
| tube circumference | at least `160-240` cells around the circumference for production |
| first hot-wall cell height | about `0.02-0.05 mm` as a starting range |
| wall layers on tube and fins | `12-20` layers, growth ratio `<= 1.15-1.20` |
| thermal boundary layer | at least `10-20` cells in the wall-normal direction |
| upper/lower flow gaps | at least `40-60` cells across each gap in a useful first mesh |
| wake refinement | at least `D/40`; for final `St`, target `D/60-D/80` if affordable |
| `z` direction | enough cells and wall layers near both fins; avoid a coarse few-cell span |
| hot-wall non-orthogonality | preferably `< 30 deg` near hot walls |
| global max non-orthogonality | preferably `< 60-65 deg` |
| boundary-layer coverage | preferably `> 95%` on hot walls |

The tube-fin junction is the highest-risk meshing area. The mesh generator must avoid duplicate
overlapping wall patches, tiny sliver cells, and accidental gaps at the hot tube/hot fin contact.

## Runtime storage policy

Heavy OpenFOAM simulations must not be copied into the Git repository.

Working cases, processor directories, time directories, raw fields, logs, and reconstructed heavy
outputs should live on the C-drive OpenFOAM workspace:

```text
Windows path: C:\openfoam-case\VV_cases\V4b_3D_run001
WSL path:     /mnt/c/openfoam-case/VV_cases/V4b_3D_run001
```

Future campaigns should use the same pattern:

```text
C:\openfoam-case\VV_cases\V4b_3D_run002
/mnt/c/openfoam-case/VV_cases/V4b_3D_run002
```

The repository should store only lightweight, intentional artefacts:

- documentation
- case-generation scripts
- small configuration templates
- compact summary tables if explicitly needed
- selected publication plots if their size is reasonable

The repository should not store:

- OpenFOAM time directories
- `processor*` directories
- reconstructed volume fields
- large VTK/Ensight/foamToVTK outputs
- raw modal snapshot databases

If a final run needs to be archived, archive it outside Git and write only a pointer, checksum, and
summary metadata into the repository.

## Geometry notes for meshing

- The tube is a cylinder with axis parallel to `z`; it passes through the full fin pitch.
- The fin plates are boundary surfaces at `z = 0` and `z = Lz`, not meshed solid fins.
- The tube-fin junction must be handled as one consistent hot-wall topology; avoid duplicate
  overlapping wall patches at the intersection between the tube and fin planes.
- The `z` faces cannot be one global periodic pair in the baseline setup because the fin-zone
  portion is a hot wall while the inlet/outlet portions are symmetry/adiabatic patches.
- A later periodic variant is possible only if the geometry and patching are rebuilt so that the
  periodic surfaces are geometrically and physically consistent.

## Current status

`run008` is the accepted production reference for the current V4b campaign.

| quantity | value |
|---|---:|
| `Re` | `200` |
| production window | `t = 2..10 s` |
| effective shedding cycles | `25.98` |
| `Cd_mean` | `3.361014 +/- 0.000772` |
| `Cl_rms` | `0.176441 +/- 0.011097` |
| `St` | `0.154261 +/- 0.009574` |
| `Nu_EB` | `7.770004 +/- 0.091573` |
| `Nu_wall` | `7.816521 +/- 0.012286` |
| wall-air heat closure | `+0.706 +/- 1.075%` |

The integrated heat transfer is fin-dominated: `Q_tube = 0.3618 W`,
`Q_fins = 1.1189 W`, corresponding to about `24.4% / 75.6%` of the wall heat
input. The shedding state is pressure-dominated and stable. POD/DMD,
coherence, transfer-entropy screening, wake-probe analysis, and phase averaging
are completed for the production window.

The strongest current mechanism statement is:

> In the accepted Re=200 production domain, vortex shedding establishes a
> stable pressure-dominated aerodynamic cycle. The same cycle organizes local
> tube and fin heat transfer, but the global wall heat response is
> fin-dominated and phase-shifted relative to lift. Wall-side and air-side heat
> balances close to within about one percent, supporting the production
> Nusselt estimates and the phase-resolved interpretation.

The curated paper-figure layer for `run008` contains ten article-planning
figures covering geometry, forces, heat balance, local tube/fin Nu, POD/EPOD,
coherence maps, and a mechanism schematic.

## Immediate next steps

Two follow-up directions are technically ready:

- Re-scan below `Re=200`, for example `Re=120, 140, 160, 180`, to quantify how
  the onset of shedding changes local and global heat transfer.
- Use the existing full 3D snapshots to compute `Q`-criterion or `lambda2`
  structures and connect named vortical structures with local `Nu(theta,z,t)`
  and fin `Nu_local(x,t)`.

## 2026-06-11 follow-up status

The two directions above have now moved from planning into execution.

Reynolds-number scan:

- production-like cases were added for `Re=100, 150, 155, 158, 159, 160, 175`
  and `200`;
- `Re=159, 160, 175, 200` were selected for dense `t=10..14 s` follow-up
  sampling around the onset/shedding region;
- the dense `Re=159` case has completed to `t=14 s`;
- dense `Re=160`, `Re=175` and `Re=200` were still running at the latest
  status check.

Local heat-transfer and structure analysis:

- `VV_cases/presentation_data/007_strong_indicators/` now contains the stronger
  `Nu_3D(x,t)` and wall-local `Nu_wall_local(s,t)` pipelines;
- `VV_cases/presentation_data/008_U_T_z_slices/` contains qualitative
  velocity, temperature, streamline, `Q` and `Lambda2` z-slice figures;
- the existing `Q`, `Lambda2`, vorticity and strip diagnostics should be used
  as mechanism indicators, not as standalone proof of causality.

Thermophysical-model control:

- a new `Re=200` temperature-dependent air-properties control case was launched:
  `/home/hexmachina/of_runs/V4b_3D_run024_re200_fullAirPropsT_from_t10_np5`;
- the stable control model uses OpenFOAM Foundation v13 `foamRun -solver fluid`
  with `sutherland + janaf + incompressiblePerfectGas +
  sensibleInternalEnergy`;
- the first short-window comparison suggests that heat-transfer metrics may
  shift by several percent relative to the constant-property Boussinesq model,
  but the control run must reach a longer stable window before it can be used
  as a final uncertainty statement.
