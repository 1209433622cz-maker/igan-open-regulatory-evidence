$ErrorActionPreference="Stop"
$Root = if ($env:IGAN_PROJECT_ROOT) { $env:IGAN_PROJECT_ROOT } else { (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path }
$env:IGAN_PROJECT_ROOT=$Root
$Code=Join-Path $Root 'analysis\r6a3a'
Write-Host "[A1] Public Sun 2018 small bytes"
pwsh -File (Join-Path $Code '01_fetch_sun2018_small_pqtl.ps1')
Write-Host "[A2] Frozen target pQTL screen"
python (Join-Path $Code '02_screen_sun2018_frozen_targets.py')
if($LASTEXITCODE-ne 0){throw "pQTL target screen failed"}
$Cand=Join-Path $Root '3_results\04_integration\R6A3A\R6A3A_pqtl_candidate_molecular_traits.tsv'
if((Get-Content $Cand | Measure-Object -Line).Lines -le 1){
  Write-Host "Track A has no measured/source-signal target. Skipping large pQTL downloads."
  $StatePath=Join-Path $Root '3_results\04_integration\R6A3A\R6A3A_pqtl_track_state.json'
  @{track='A_pQTL';pass_loci=0;pass_locus_names=@();status='FAIL_NO_SOURCE_SUPPORTED_TARGET'} |
    ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $StatePath -Encoding utf8
} else {
  Write-Host "[A3] Triggered dense pQTL + source SuSiE LBF bytes"
  pwsh -File (Join-Path $Code '03_fetch_sun2018_full_if_triggered.ps1')
  if($LASTEXITCODE -notin 0,20){throw "pQTL full fetch failed"}
  python -c "import pyliftover" 2>$null
  if($LASTEXITCODE-ne 0){ python -m pip install pyliftover }
  python (Join-Path $Code '04_extract_target_pqtl_and_lbf.py')
  if($LASTEXITCODE-ne 0){throw "target pQTL extraction failed"}
  python (Join-Path $Code '05_harmonize_igan_to_pqtl.py')
  if($LASTEXITCODE-ne 0){throw "IgAN-pQTL harmonization failed"}
  $R=Join-Path $Root 'tools\R\R-4.6.1\bin\Rscript.exe'
  if(!(Test-Path $R)){ $R=(Get-Command Rscript -ErrorAction SilentlyContinue).Source }
  if(-not $R){throw "Rscript not found"}
  & $R (Join-Path $Code '06_run_pqtl_signal_coloc.R')
  if($LASTEXITCODE-ne 0){throw "pQTL signal coloc failed"}
  python (Join-Path $Code '07_adjudicate_pqtl_track.py')
  if($LASTEXITCODE-ne 0){throw "pQTL adjudication failed"}
}
Write-Host "[B1] Verify/fetch GSE127136"
pwsh -File (Join-Path $Code '10_verify_or_fetch_GSE127136.ps1')
Write-Host "[B2] ZMIZ1 donor-level aggregate kidney pseudobulk"
python (Join-Path $Code '11_zmiz1_kidney_donor_pseudobulk.py')
if($LASTEXITCODE-ne 0){throw "ZMIZ1 donor pseudobulk failed"}
Write-Host "[B3] Provisional marker localization (secondary only)"
python (Join-Path $Code '12_provisional_kidney_marker_localization.py')
if($LASTEXITCODE-ne 0){throw "marker localization failed"}
Write-Host "[FINAL] Frozen R6A3A adjudication"
python (Join-Path $Code '13_finalize_r6a3a.py')
if($LASTEXITCODE-ne 0){throw "R6A3A final gate failed"}
Get-Content (Join-Path $Root '3_results\04_integration\R6A3A\R6A3A_final_adjudication.json')
