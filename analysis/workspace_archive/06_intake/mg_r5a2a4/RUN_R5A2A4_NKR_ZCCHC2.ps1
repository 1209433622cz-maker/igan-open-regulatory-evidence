[CmdletBinding()]
param(
    [switch]$RebuildLD,
    [switch]$SkipFigure
)

$ErrorActionPreference = 'Stop'
$Workspace = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$Python = (Get-Command python).Source
$Rscript = Join-Path $Workspace '0_admin\tooling\R\R-4.6.1\bin\Rscript.exe'
$RLibrary = Join-Path $Workspace '0_admin\tooling\R-library'

if (-not (Test-Path -LiteralPath $Rscript)) {
    throw "Rscript not found: $Rscript"
}

Set-Location -LiteralPath $Workspace
$env:R_LIBS_USER = $RLibrary

& $Python '2_code\06_intake\mg_r5a2a4\audit_r5a2a3_import_and_recalculation.py'
if ($LASTEXITCODE -ne 0) { throw 'R5A2A3 audit failed' }

if ($RebuildLD) {
    & $Python '2_code\06_intake\mg_r5a2a4\build_nkr_zcchc2_source_ld.py'
    if ($LASTEXITCODE -ne 0) { throw 'Source LD build failed' }
    & $Python '2_code\06_intake\mg_r5a2a4\build_nkr_zcchc2_covariate_residual_ld.py'
    if ($LASTEXITCODE -ne 0) { throw 'Residualized LD build failed' }
}

& $Rscript '2_code\06_intake\mg_r5a2a4\validate_r5a2a3_with_coloc_R.R'
if ($LASTEXITCODE -ne 0) { throw 'Official coloc validation failed' }

& $Rscript '2_code\06_intake\mg_r5a2a4\run_susie_nkr_zcchc2.R'
if ($LASTEXITCODE -ne 0) { throw 'SuSiE-RSS failed' }

& $Python '2_code\06_intake\mg_r5a2a4\audit_top_eqtl_and_forced_conditioning.py'
if ($LASTEXITCODE -ne 0) { throw 'Final adjudication failed' }

if (-not $SkipFigure) {
    & $Python '2_code\06_intake\mg_r5a2a4\plot_r5a2a4_adjudication.py'
    if ($LASTEXITCODE -ne 0) { throw 'Figure generation failed' }
}

Write-Host 'R5A2A4 completed.'
