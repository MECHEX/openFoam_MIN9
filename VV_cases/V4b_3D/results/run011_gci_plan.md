# V4b_3D run011 GCI plan

Data: 2026-06-04

Cel: przygotowac formalny test niezaleznosci siatki dla produkcyjnej geometrii `V4b` po uwagach recenzenta.

## 1. Zalozenie

`run008` pozostaje siatka srednia i punktem odniesienia:

| Level | Case | Target cells | Role |
|---|---|---:|---|
| coarse | `V4b_3D_run011_gci_coarse` | `~185k-210k` | siatka rzadsza |
| medium | `V4b_3D_run008` | `407,440` | obecna produkcja |
| fine | `V4b_3D_run011_gci_fine` | `~800k-900k` | siatka gestsza |

Proponowany stosunek zagęszczenia liniowego wynosi około `r = 1.25-1.30`.
W 3D oznacza to zmiane liczby komorek o okolo `r^3 ~= 2.0-2.2`.

## 2. Stale elementy kampanii

Warianty GCI maja utrzymac:

- `Re = 200`;
- `Lin = 2D`;
- `Lout = 8D`;
- `Lz = 1D`;
- solver `foamRun -solver fluid`;
- model `eConst + Boussinesq + sensibleInternalEnergy`;
- capacity coefficient `1005`;
- `maxCo = 0.8`;
- te same definicje `forceCoeffs`, `forces_raw`, `wallHeatFlux`, surface sampling i outlet reconstruction.

## 3. Przygotowane skrypty

Skrypt przygotowania:

```bash
bash VV_cases/V4b_3D/_code/prepare_run011_gci_meshes.sh
```

Domyslnie tworzy:

```text
/home/hexmachina/of_runs/V4b_3D_run011_gci_coarse
/home/hexmachina/of_runs/V4b_3D_run011_gci_fine
```

Skrypt startu w tle:

```bash
CASE_DIR=/home/hexmachina/of_runs/V4b_3D_run011_gci_coarse \
NPROCS=20 TAG=run011_gci_coarse_smoke \
bash VV_cases/V4b_3D/_code/start_run011_gci_bg.sh
```

Analogicznie dla `fine`.

## 4. Kolejnosc wykonania

### Etap 1: mesh smoke

Dla `coarse` i `fine`:

```bash
cd /home/hexmachina/of_runs/V4b_3D_run011_gci_coarse
./mesh.sh
./decompose_case.sh
```

```bash
cd /home/hexmachina/of_runs/V4b_3D_run011_gci_fine
./mesh.sh
./decompose_case.sh
```

Kryteria przejscia:

- `checkMesh` normalny: `Mesh OK`;
- brak powaznego pogorszenia non-orthogonality/skewness wzgledem `run008`;
- warstwy na `hot_tube` i finach dodane sensownie;
- finalna liczba komorek w oczekiwanym zakresie.

### Etap 2: krotki smoke run

Domyslnie nowe przypadki maja `endTime = 3 s`.

Celem nie jest jeszcze finalny GCI, tylko sprawdzenie:

- stabilnosci Couranta;
- czy solver wchodzi w petle czasowa;
- czy `forceCoeffs`, `wallHeatFlux`, surfaces i probes pisza dane;
- czy `Cd`, `Cl_rms`, `St`, `Nu` nie sa ewidentnie niefizyczne;
- czy bilans ciepla nie rozpada sie juz na starcie.

### Etap 3: pelny GCI

Jesli smoke przejdzie, ustawic `endTime = 6 s` albo `10 s`.

Rekomendacja:

- `t=6 s` jako tanszy GCI publication-check;
- `t=10 s` jesli chcemy pelna zgodnosc z `run008`.

Metryki do GCI:

| Metric | Reason |
|---|---|
| `Cd_mean` | drag convergence |
| `Cl_rms` | shedding amplitude convergence |
| `St` | shedding frequency convergence |
| `Nu_EB` | global heat-transfer convergence |
| `Nu_wall` | wall-flux heat-transfer convergence |
| closure | energy-balance consistency |
| `Q_tube/Q_fins` | heat split convergence |

## 5. GCI equations

Po uzyskaniu trzech wynikow:

```text
r21 = (N_medium / N_coarse)^(1/3)
r32 = (N_fine / N_medium)^(1/3)
```

Dla danej metryki `phi`:

```text
epsilon21 = phi_medium - phi_coarse
epsilon32 = phi_fine - phi_medium
```

Nastepnie wyznaczyc obserwowany rzad `p` i GCI zgodnie ze standardowym Richardson/GCI. Jesli monotonicznosc nie jest zachowana, raportowac jako non-monotonic grid response i nie udawac formalnego GCI.

## 6. Ryzyka

- `fine ~850k` moze kosztowac okolo 2x wiecej CPU i storage niz `run008`.
- Snappy mesh nie gwarantuje idealnego systematycznego `r`, dlatego nalezy liczyc `r` z realnej liczby komorek po meshu.
- Warstwy przy tube-fin junction moga zachowac sie inaczej na fine mesh; trzeba sprawdzic layer coverage.
- `Cl_rms` moze miec wieksza niepewnosc czasowa niz `Cd` i `Nu`, wiec GCI dla `Cl_rms` wymaga ostroznej interpretacji.

## 7. Status wykonania 2026-06-04

Przygotowano przypadki:

```text
/home/hexmachina/of_runs/V4b_3D_run011_gci_coarse
/home/hexmachina/of_runs/V4b_3D_run011_gci_fine
```

Dodane skrypty:

```text
VV_cases/V4b_3D/_code/prepare_run011_gci_meshes.sh
VV_cases/V4b_3D/_code/start_run011_gci_bg.sh
```

### Mesh results

| Level | Case | Cells | Points | Faces | Normal checkMesh | Strict checkMesh |
|---|---|---:|---:|---:|---|---|
| coarse | `V4b_3D_run011_gci_coarse` | `196,938` | `215,574` | `609,166` | `Mesh OK` | failed 3 strict checks |
| medium | `V4b_3D_run008` | `407,440` | `437,881` | `1,252,412` | `Mesh OK` | known strict concave-cell family |
| fine | `V4b_3D_run011_gci_fine` | `829,761` | `880,124` | `2,539,205` | `Mesh OK` | failed 1 strict check |

Quality details:

| Level | Max non-orthogonality | Avg non-orthogonality | Max skewness | Max aspect ratio |
|---|---:|---:|---:|---:|
| coarse | `54.853757` | `5.751684` | `2.6499843` | `35.574217` |
| medium | `62.84` | `5.93` | `3.319` | `33.64` |
| fine | `62.895273` | `5.774253` | `1.5664989` | `33.43709` |

Strict-check notes:

- coarse: `8` cells with determinant `< 0.001`, `5,275` concave cells, `4` faces with small interpolation weight;
- medium reference family: previous accepted mesh reported `9,178` strict concave cells;
- fine: `17,285` concave cells, but normal `checkMesh` passes and max skewness improves.

### Actual refinement ratios

Using actual cell counts:

```text
r21 = (407440 / 196938)^(1/3) = 1.274
r32 = (829761 / 407440)^(1/3) = 1.268
```

This is a good GCI spacing: the two ratios are close and both sit in the planned `1.25-1.30` range.

### Startup smoke status

Both meshes were tested for solver startup and post-processing output.

Coarse:

- foreground startup reached about `t = 0.0189 s`;
- Courant stabilized near `Co_mean ~= 0.112`, `Co_max ~= 0.792`;
- residuals and continuity errors remained finite;
- first post-processing outputs were written, including `forceCoeffs`, `forces_raw`, `wallHeatFlux`, `hot_tube_surface`, `hot_fin_surface`, `midspan_z0`, `probes_wake`, and `residuals`.

Fine:

- background startup reached beyond first write, with `processor0/0.005` present;
- log checkpoint near `t = 0.00699 s`;
- Courant remained controlled, e.g. `Co_mean ~= 0.075`, `Co_max ~= 0.771`;
- residuals and continuity errors remained finite;
- first post-processing outputs were written, including `forceCoeffs`, `forces_raw`, `wallHeatFlux`, `hot_tube_surface`, `hot_fin_surface`, `midspan_z0`, `probes_wake`, and `residuals`;
- run was stopped manually after startup confirmation to avoid leaving a multi-hour job active.

No `run011` solver process is intentionally left running after this startup smoke check.

### Operational conclusion

The proposed GCI mesh triplet is viable:

```text
coarse = 196,938 cells
medium = 407,440 cells
fine   = 829,761 cells
```

Next computational step:

1. run `coarse` to at least `t = 3 s`, preferably `t = 6 s`;
2. run `fine` to the same end time;
3. analyze `Cd_mean`, `Cl_rms`, `St`, `Nu_EB`, `Nu_wall`, closure, and heat split;
4. compute Richardson/GCI only if the responses are monotonic or report non-monotonic grid response honestly.

## 8. t=3 s queue launch 2026-06-04

Queued execution was started after the startup smoke check.

Queue script:

```text
VV_cases/V4b_3D/_code/run011_gci_queue_t3.sh
```

Queue log:

```text
/home/hexmachina/of_runs/run011_gci_t3_queue.20260604_154002_run011_gci_t3_queue.log
```

Execution order:

```text
1. coarse to t = 3 s
2. fine to t = 3 s
```

Current launch status at the time of this note:

- queue is active;
- `coarse` is running on `20` MPI ranks with `mpirun --oversubscribe`;
- log file: `/home/hexmachina/of_runs/V4b_3D_run011_gci_coarse/logs/log.foamRun_parallel.20260604_154002_run011_gci_t3_queue_coarse`;
- early status: `t ~= 0.024 s`, `Co_mean ~= 0.112`, `Co_max ~= 0.790`;
- `fine` will start automatically only after `coarse` finishes.

Monitor commands:

```bash
wsl pgrep -af run011_gci
wsl pgrep -af foamRun
wsl tail -n 80 /home/hexmachina/of_runs/run011_gci_t3_queue.20260604_154002_run011_gci_t3_queue.log
wsl tail -n 80 /home/hexmachina/of_runs/V4b_3D_run011_gci_coarse/logs/log.foamRun_parallel.20260604_154002_run011_gci_t3_queue_coarse
```
