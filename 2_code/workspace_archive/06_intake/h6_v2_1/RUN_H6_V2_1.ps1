param(
    [Parameter(Mandatory = $true)][string]$InputFile,
    [Parameter(Mandatory = $true)][string]$MetadataFile,
    [Parameter(Mandatory = $true)][ValidateSet("female", "male")][string]$Label,
    [Parameter(Mandatory = $true)][string]$OutputDir
)

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script = Join-Path $Here "inspect_sex_specific_sumstats_v2_1.py"

if (Test-Path -LiteralPath "D:\bioinfor\python.exe" -PathType Leaf) {
    $PythonExe = "D:\bioinfor\python.exe"
} else {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $PythonCommand) {
        throw "Python 3 was not found. Install Python 3.11+ or edit RUN_H6_V2_1.ps1 with its exact path."
    }
    $PythonExe = $PythonCommand.Source
}

$ResolvedInput = (Resolve-Path -LiteralPath $InputFile).Path
$ResolvedMetadata = (Resolve-Path -LiteralPath $MetadataFile).Path
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$ResolvedOutput = (Resolve-Path -LiteralPath $OutputDir).Path

& $PythonExe $Script --input $ResolvedInput --metadata $ResolvedMetadata --label $Label --output-dir $ResolvedOutput
$ToolExit = $LASTEXITCODE
$ResultPath = Join-Path $ResolvedOutput "${Label}_intake_v2_1.json"

if (Test-Path -LiteralPath $ResultPath -PathType Leaf) {
    $Result = Get-Content -LiteralPath $ResultPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Host "H6 v2.1 status: $($Result.status)"
    Write-Host "Result: $ResultPath"
    if ($ToolExit -eq 0 -and $Result.status -ne "PASS_FROZEN_REGIONS_INTAKE_READY_FOR_HARMONIZATION") {
        throw "Safety invariant failed: exit 0 without the exact PASS status."
    }
}

exit $ToolExit
