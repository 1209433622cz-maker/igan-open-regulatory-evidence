param([string]$ProjectRoot=$env:R7_PROJECT_ROOT)
$ErrorActionPreference='Stop'
if([string]::IsNullOrWhiteSpace($ProjectRoot)){
  $RepoCandidate=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
  if(Test-Path -LiteralPath (Join-Path $RepoCandidate '.git')){$ProjectRoot=$RepoCandidate}
  else{$ProjectRoot=(Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path}
}
$env:R7_PROJECT_ROOT=$ProjectRoot
$Code=$PSScriptRoot
$Audit=Join-Path $ProjectRoot '3_results\01_intake\R7A1A'
New-Item -ItemType Directory -Force -Path $Audit | Out-Null

Write-Host '[1/5] PBC true-byte intake and remote study-LD inventory'
pwsh -File (Join-Path $Code '02_fetch_pbc_gwas_and_study_inputs.ps1') -ProjectRoot $ProjectRoot
Write-Host '[2/5] eligible CeD intake plus 2020 source audit object'
pwsh -File (Join-Path $Code '01_fetch_ced_gwas.ps1') -ProjectRoot $ProjectRoot

Write-Host '[3/5] PBC schema/signal audit'
python (Join-Path $Code '03_audit_candidate_gwas.py') --candidate PBC --file (Join-Path $ProjectRoot '1_data\gwas\R7A1A\PBC\GCST90061440_buildGRCh37.tsv') --outdir $Audit
if($LASTEXITCODE-ne 0){throw 'PBC audit failed'}
Write-Host '[4/5] eligible CeD schema/signal audit'
python (Join-Path $Code '03_audit_candidate_gwas.py') --candidate CeD --file (Join-Path $ProjectRoot '1_data\gwas\R7A1A\CeD\GCST000612_20190752.h.tsv.gz') --outdir $Audit
if($LASTEXITCODE-ne 0){throw 'CeD audit failed'}
Write-Host '[5/5] frozen positive-control QTL screen'
python (Join-Path $Code '04_screen_qtl_positive_controls.py')
if($LASTEXITCODE-ne 0){throw 'QTL positive-control screen failed'}
Write-Host 'R7A1A intake complete. STOP before disease-QTL coloc.'
Get-Content (Join-Path $ProjectRoot '3_results\03_qtl\R7A1A\R7A1A_QTL_control_testability_state.json')
