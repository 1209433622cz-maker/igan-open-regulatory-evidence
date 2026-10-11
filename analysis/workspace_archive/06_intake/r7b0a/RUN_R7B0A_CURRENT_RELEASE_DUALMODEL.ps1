param(
  [string]$ProjectRoot = 'H:\SCI2\YR1',
  [string]$PythonExe = 'D:\bioinfor\python.exe',
  [string]$RscriptExe = 'H:\SCI2\YR1\0_admin\tooling\R\R-4.6.1\bin\x64\Rscript.exe'
)

$ErrorActionPreference = 'Stop'
$env:R7_PROJECT_ROOT = $ProjectRoot

$code = Join-Path $ProjectRoot '2_code\06_intake\r7b0'
$r7b0a = Join-Path $ProjectRoot '2_code\06_intake\r7b0a'
New-Item -ItemType Directory -Force -Path $r7b0a | Out-Null

# Expected files from R7B0.
$required = @(
  (Join-Path $code '01_r7b0_targeted_pf50_tensorqtl_compatible.py'),
  (Join-Path $r7b0a '05_build_r7b0a_model_identity_manifest.py'),
  (Join-Path $r7b0a '06_r7b0a_current_release_dualmodel_multisignal.R'),
  (Join-Path $r7b0a '07_adjudicate_r7b0a_current_models.py')
)
foreach ($p in $required) {
  if (-not (Test-Path -LiteralPath $p)) { throw "Missing required file: $p" }
}
if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) { throw "Missing Python executable: $PythonExe" }
if (-not (Test-Path -LiteralPath $RscriptExe -PathType Leaf)) { throw "Missing Rscript executable: $RscriptExe" }

Write-Host 'Step 1/4: regenerate current-release PF10 and PF50 nominal summaries for the frozen 7 comparisons'
& $PythonExe (Join-Path $code '01_r7b0_targeted_pf50_tensorqtl_compatible.py')
if ($LASTEXITCODE -ne 0) { throw "Targeted QTL generation failed with exit code $LASTEXITCODE" }

$targetDir = Join-Path $ProjectRoot '3_results\03_qtl\R7B0\pf50_targeted'
$pf10 = @(Get-ChildItem -LiteralPath $targetDir -Filter '*_PF10.tsv.gz' -File)
$pf50 = @(Get-ChildItem -LiteralPath $targetDir -Filter '*_PF50.tsv.gz' -File)
if ($pf10.Count -ne 7 -or $pf50.Count -ne 7) {
  throw "Expected 7 PF10 and 7 PF50 targeted summaries; got PF10=$($pf10.Count), PF50=$($pf50.Count)"
}

Write-Host 'Step 2/4: freeze hashes and verify donor/covariate/allele/variant/LD identity'
& $PythonExe (Join-Path $r7b0a '05_build_r7b0a_model_identity_manifest.py')
if ($LASTEXITCODE -ne 0) { throw "Identity-manifest build failed with exit code $LASTEXITCODE" }

Write-Host 'Step 3/4: run current-release PF10/PF50 matched SuSiE/coloc.susie'
& $RscriptExe (Join-Path $r7b0a '06_r7b0a_current_release_dualmodel_multisignal.R')
if ($LASTEXITCODE -ne 0) { throw "SuSiE/coloc run failed with exit code $LASTEXITCODE" }

Write-Host 'Step 4/4: adjudicate model identity/QC separately from biological class'
& $PythonExe (Join-Path $r7b0a '07_adjudicate_r7b0a_current_models.py')
if ($LASTEXITCODE -ne 0) { throw "Adjudication failed with exit code $LASTEXITCODE" }

$state = Join-Path $ProjectRoot '3_results\04_integration\R7B0A\current_release_dualmodel\R7B0A_state.json'
if (-not (Test-Path -LiteralPath $state)) { throw "Missing state: $state" }
Get-Content -LiteralPath $state -Raw

Write-Host 'R7B0A targeted current-release dual-model run completed.'
