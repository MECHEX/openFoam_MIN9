# Cylinder Crossflow Case

Manual OpenFOAM setup for 2D flow around a cylinder with diameter `12 mm`.

Assumptions:
- air, incompressible
- `nu = 1.5e-5 m2/s`
- `Uinf = 0.125 m/s`
- `Re = Uinf * D / nu = 100`
- domain height `20D`
- inlet offset `10D`
- outlet offset `25D`

Main outputs:
- transient lift coefficient `Cl(t)` from `postProcessing/forceCoeffs/.../coefficient.dat`
- transient drag coefficient `Cd(t)`

Run in WSL:

```bash
source /home/kik/openfoam/OpenFOAM-v2512/etc/bashrc
cd /mnt/c/openfoam-case/cylinder2D
./Allrun
```

`Allrun` now also:
- copies results back into the repository
- regenerates `results/plots/Cl_vs_time.png`
- updates `results/analysis/st_estimate.json`

Copy results back into the repository:

```powershell
cd "C:\Users\kik\My Drive\Politechnika Krakowska\Researches\Repositories\openFoam\cylinder2D"
.\SyncResults.ps1
```

Copied outputs are stored in `results/`.
- time directories are copied into `results/rawResults/`

Generate the `Cl(t)` plot:

```powershell
python .\PlotCl.py
```

Estimate the Strouhal number from `Cl(t)`:

```powershell
python .\EstimateSt.py
```
