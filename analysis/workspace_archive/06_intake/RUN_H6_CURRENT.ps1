param(
    [Parameter(Mandatory = $true)][string]$InputFile,
    [Parameter(Mandatory = $true)][string]$MetadataFile,
    [Parameter(Mandatory = $true)][ValidateSet("female", "male")][string]$Label,
    [Parameter(Mandatory = $true)][string]$OutputDir
)

$ErrorActionPreference = "Stop"
$CurrentRunner = Join-Path $PSScriptRoot "h6_v2_1\RUN_H6_V2_1.ps1"
if (-not (Test-Path -LiteralPath $CurrentRunner -PathType Leaf)) {
    throw "Current H6 v2.1 runner is missing: $CurrentRunner"
}

& $CurrentRunner -InputFile $InputFile -MetadataFile $MetadataFile -Label $Label -OutputDir $OutputDir
exit $LASTEXITCODE
