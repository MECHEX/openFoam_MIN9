# 009_air_props_comparison

Purpose: preliminary comparison between the accepted constant-property
Boussinesq `Re=200` model and the new temperature-dependent air-properties
control run.

## Cases compared

| label | WSL case path | model |
|---|---|---|
| constant-property baseline | `/home/hexmachina/of_runs/V4b_3D_run022_re200_dense_t10_14_np5` | `eConst + Boussinesq + const transport` |
| airProps(T) control | `/home/hexmachina/of_runs/V4b_3D_run024_re200_fullAirPropsT_from_t10_np5` | `sutherland + janaf + incompressiblePerfectGas` |

Both cases are run with:

- OpenFOAM Foundation v13
- `foamRun -solver fluid`
- `Re = 200`
- `5` MPI processes
- hot tube and hot fin wall heat-flux outputs

## Thermophysical control model

The temperature-dependent control uses:

```text
transport       sutherland
thermo          janaf
equationOfState incompressiblePerfectGas
energy          sensibleInternalEnergy
```

Interpretation:

- `sutherland`: dynamic viscosity varies with temperature.
- `janaf`: thermodynamic properties vary with temperature.
- `incompressiblePerfectGas`: density varies with temperature at reference
  pressure, while preserving a low-Mach formulation.
- `sensibleInternalEnergy`: the solved energy variable is the sensible internal
  energy associated with temperature.

## Current output

- `preliminary_run024_vs_run022_summary.csv`

The CSV compares force coefficients and integrated heat-transfer metrics on
the short common window available when the check was made:

```text
t = 10.005..10.110 s
```

## Preliminary result

On the short common window, the airProps(T) run showed:

- `Cd_mean`: about `-1.2%` vs constant-property baseline
- `Cl_mean`: about `+1.1%`
- `Q_total`: about `-3.9%`
- `Nu_proxy`: about `-3.9%`

On a shorter tail of the same early window (`10.08..10.11 s`), the heat-transfer
difference appeared closer to `-8..-9%`.

## Important limitation

This is not yet a final statistical comparison. The airProps(T) case was
restarted from the constant-property `t=10 s` field, so the first part of the
record contains thermophysical relaxation. A final comparison should be made
after the control run has accumulated a longer stable window.

`St` should not be reported from this early comparison window. The available
airProps(T) signal is too short to extract a reliable shedding frequency.

