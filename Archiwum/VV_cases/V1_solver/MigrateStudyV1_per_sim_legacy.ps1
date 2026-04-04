Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$studyDir = Join-Path $PSScriptRoot "results\study_v1"
$runsDir = Join-Path $studyDir "runs"
$studySummaryDir = Join-Path $studyDir "study_summary"
$publicationDir = Join-Path $studyDir "publication"
$workingRoot = "C:\openfoam-case\VV_cases\V1_solver"
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$archiveRoot = Join-Path $repoRoot "Archiwum"
$archiveV1Root = Join-Path $archiveRoot "VV_cases\V1_solver"

$orderedSlugs = @(
    "baseline_medium_Re090",
    "baseline_medium_Re100",
    "baseline_medium_Re110",
    "baseline_medium_Re120",
    "baseline_medium_Re140",
    "baseline_medium_Re160",
    "baseline_coarse_Re120",
    "baseline_coarse_Re160",
    "baseline_fine_Re120",
    "baseline_fine_Re160",
    "long_medium_Re120",
    "long_medium_Re160",
    "long_medium_Re200",
    "long_target100k_Re160"
)

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Ensure-RunLayout {
    param([string]$Path)
    Ensure-Dir $Path
    foreach ($name in @("00_notes", "01_openfoam_setup", "02_raw_data", "03_processed_data", "04_plots", "05_logs")) {
        Ensure-Dir (Join-Path $Path $name)
    }
}

Ensure-Dir $archiveV1Root
Ensure-Dir $studySummaryDir
Ensure-Dir $publicationDir

$legacyTopArchive = Join-Path $archiveV1Root "study_v1_pre_cleanup"
Ensure-Dir $legacyTopArchive

for ($i = 0; $i -lt $orderedSlugs.Count; $i++) {
    $slug = $orderedSlugs[$i]
    $index = "{0:D3}" -f ($i + 1)
    $newRunDir = Join-Path $runsDir "${index}_data_${slug}"
    $legacyRunDir = Join-Path $runsDir $slug
    $workingCaseDir = Join-Path $workingRoot $slug

    Ensure-RunLayout $newRunDir

    $legacyInput = Join-Path $legacyRunDir "input.md"
    $workingInput = Join-Path $workingCaseDir "input.md"
    if (Test-Path -LiteralPath $legacyInput) {
        Copy-Item -LiteralPath $legacyInput -Destination (Join-Path $newRunDir "00_notes\input.md") -Force
    } elseif (Test-Path -LiteralPath $workingInput) {
        Copy-Item -LiteralPath $workingInput -Destination (Join-Path $newRunDir "00_notes\input.md") -Force
    }

    $legacyOutput = Join-Path $legacyRunDir "output.md"
    if (Test-Path -LiteralPath $legacyOutput) {
        Copy-Item -LiteralPath $legacyOutput -Destination (Join-Path $newRunDir "00_notes\output_legacy.md") -Force
    }

    $legacyPlot = Join-Path $studyDir "plots\$slug`_Cl.png"
    if (Test-Path -LiteralPath $legacyPlot) {
        Copy-Item -LiteralPath $legacyPlot -Destination (Join-Path $newRunDir "04_plots\Cl_vs_time_legacy.png") -Force
    }

    if (Test-Path -LiteralPath $workingCaseDir) {
        foreach ($item in @("0.orig", "constant", "system", "Allrun", "caseMeta.json")) {
            $source = Join-Path $workingCaseDir $item
            if (Test-Path -LiteralPath $source) {
                Copy-Item -LiteralPath $source -Destination (Join-Path $newRunDir "01_openfoam_setup") -Recurse -Force
            }
        }

        $postProcessing = Join-Path $workingCaseDir "postProcessing"
        if (Test-Path -LiteralPath $postProcessing) {
            Copy-Item -LiteralPath $postProcessing -Destination (Join-Path $newRunDir "02_raw_data") -Recurse -Force
        }

        $logsDir = Join-Path $workingCaseDir "logs"
        if (Test-Path -LiteralPath $logsDir) {
            Copy-Item -LiteralPath $logsDir -Destination (Join-Path $newRunDir "05_logs") -Recurse -Force
        }
    }

    if (Test-Path -LiteralPath $legacyRunDir) {
        Remove-Item -LiteralPath $legacyRunDir -Recurse -Force
    }
}

foreach ($name in @("summary.csv", "summary.md", "manifest.json", "study_plan.md")) {
    $source = Join-Path $studyDir $name
    if (Test-Path -LiteralPath $source) {
        Move-Item -LiteralPath $source -Destination $legacyTopArchive -Force
    }
}

$legacyPlots = Join-Path $studyDir "plots"
if (Test-Path -LiteralPath $legacyPlots) {
    Move-Item -LiteralPath $legacyPlots -Destination $legacyTopArchive -Force
}

$legacyPdfPages = Join-Path $studyDir "_pdf_pages"
if (Test-Path -LiteralPath $legacyPdfPages) {
    Move-Item -LiteralPath $legacyPdfPages -Destination $legacyTopArchive -Force
}

Write-Host "V1 study migration completed."
Write-Host "Study root: $studyDir"
