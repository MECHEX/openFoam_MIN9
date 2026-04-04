$ErrorActionPreference = "Stop"

$repoCase = Split-Path -Parent $MyInvocation.MyCommand.Path
$workCase = "C:\openfoam-case\cylinder2D"
$resultsDir = Join-Path $repoCase "results"
$rawResultsDir = Join-Path $resultsDir "rawResults"
$caseName = Split-Path $repoCase -Leaf

if (-not (Test-Path $workCase)) {
    Write-Error "Nie znaleziono katalogu roboczego: $workCase"
}

New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null
New-Item -ItemType Directory -Force -Path $rawResultsDir | Out-Null

$itemsToCopy = @(
    "postProcessing",
    "constant\polyMesh"
)

foreach ($item in $itemsToCopy) {
    $source = Join-Path $workCase $item
    if (Test-Path $source) {
        $target = Join-Path $resultsDir $item
        if (Test-Path $target) {
            Remove-Item -Path $target -Recurse -Force
        }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        Copy-Item -Path $source -Destination $target -Recurse -Force
    }
}

Get-ChildItem -Path $workCase -Directory |
    Where-Object { $_.Name -match '^[0-9]' } |
    ForEach-Object {
        $target = Join-Path $rawResultsDir $_.Name
        if (Test-Path $target) {
            Remove-Item -Path $target -Recurse -Force
        }
        Copy-Item -Path $_.FullName -Destination $target -Recurse -Force
    }

$legacyFoamFile = Join-Path $resultsDir "cylinder2D.foam"
if (Test-Path $legacyFoamFile) {
    Remove-Item -Path $legacyFoamFile -Force
}

$foamFile = Join-Path $resultsDir "$caseName.foam"
if (-not (Test-Path $foamFile)) {
    New-Item -ItemType File -Path $foamFile | Out-Null
}

Write-Host "Wyniki skopiowane do: $resultsDir"
