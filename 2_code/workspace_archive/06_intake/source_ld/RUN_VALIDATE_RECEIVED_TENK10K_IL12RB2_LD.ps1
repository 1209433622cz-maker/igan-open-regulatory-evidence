[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Bim,

    [Parameter(Mandatory = $true)]
    [string]$Ld,

    [string]$Workspace = 'H:\SCI2\YR1',

    [string]$OutputDirectory = 'H:\SCI2\YR1\3_results\02_coloc\R4A12FG8_source_ld_intake'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$validator = Join-Path $Workspace '2_code\06_intake\source_ld\validate_received_tenk10k_source_ld_v2.py'
$manifestDir = Join-Path $Workspace '1_data\manifests\R4A12FG7'
$variantManifest = Join-Path $manifestDir 'IL12RB2_TenK10K_100kb_native_variants_1366.tsv'
$csManifest = Join-Path $manifestDir 'IL12RB2_four_cell_source_CS_manifest.tsv'
$anchors = Join-Path $manifestDir 'IL12RB2_required_anchors.tsv'

foreach ($path in @($Bim, $Ld, $validator, $variantManifest, $csManifest, $anchors)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required file not found: $path"
    }
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$report = Join-Path $OutputDirectory 'source_ld_validation.json'
$subsetPrefix = Join-Path $OutputDirectory 'ENSG00000081985.requested1366'

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
    throw 'Python was not found on PATH.'
}

& $python.Source $validator `
    --bim $Bim `
    --ld $Ld `
    --variant-manifest $variantManifest `
    --cs-manifest $csManifest `
    --anchors $anchors `
    --out-json $report `
    --subset-prefix $subsetPrefix
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "PASS: TenK10K molecular-QTL source-LD structural gate."
    Write-Host "Receipt: $report"
    Write-Host "Frozen subset: $subsetPrefix.bim / $subsetPrefix.ld"
    exit 0
}

Write-Host "HOLD or validator error (exit $exitCode). Inspect: $report" -ForegroundColor Yellow
exit $exitCode
