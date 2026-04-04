#!/bin/bash
set -euo pipefail

repo_case_dir="/mnt/c/Users/kik/My Drive/Politechnika Krakowska/Researches/Repositories/openFoam/openFoam_MIN"
repo_case_dir_win='C:\Users\kik\My Drive\Politechnika Krakowska\Researches\Repositories\openFoam\openFoam_MIN'

powershell.exe -ExecutionPolicy Bypass -File "$repo_case_dir_win\\SyncResults.ps1"
python.exe "$repo_case_dir_win\\PlotCl.py"
python.exe "$repo_case_dir_win\\EstimateSt.py"
