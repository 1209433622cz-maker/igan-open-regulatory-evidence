param(
  [string]$RepoPath='H:\SCI2\YR1\9.Version\public_repro\igan-open-regulatory-evidence'
)
$ErrorActionPreference='Stop'
$Here=Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot=Split-Path -Parent $Here
if(!(Test-Path -LiteralPath $RepoPath)){throw "RepoPath not found: $RepoPath"}
if(!(Test-Path -LiteralPath (Join-Path $RepoPath '.git'))){throw "Not a git clone: $RepoPath"}

$Map=@(
 @{Src=(Join-Path $PackageRoot 'reports\00_CMM_R7A0_执行摘要_portfolio_preflight.md');Dst=(Join-Path $RepoPath 'reports\00_CMM_R7A0_执行摘要_portfolio_preflight.md')},
 @{Src=(Join-Path $PackageRoot 'reports\99_CMM_R7A0_详细行动记录_2026-09-15.md');Dst=(Join-Path $RepoPath 'reports\99_CMM_R7A0_详细行动记录_2026-09-15.md')},
 @{Src=(Join-Path $PackageRoot 'reports\SOURCES_CHECKED_R7A0_2026-09-15.md');Dst=(Join-Path $RepoPath 'reports\SOURCES_CHECKED_R7A0_2026-09-15.md')},
 @{Src=(Join-Path $PackageRoot 'protocol\R7A1A_PBC_CeD_true_byte_QTL_preflight_v1.md');Dst=(Join-Path $RepoPath 'protocols\R7A1A_PBC_CeD_true_byte_QTL_preflight_v1.md')},
 @{Src=(Join-Path $PackageRoot 'results\R7A0_portfolio_decision_matrix.tsv');Dst=(Join-Path $RepoPath 'results\r7a0\R7A0_portfolio_decision_matrix.tsv')},
 @{Src=(Join-Path $PackageRoot 'results\R7A1A_frozen_positive_controls.tsv');Dst=(Join-Path $RepoPath 'results\r7a0\R7A1A_frozen_positive_controls.tsv')},
 @{Src=(Join-Path $PackageRoot 'results\R7A0_state.json');Dst=(Join-Path $RepoPath 'results\r7a0\R7A0_state.json')},
 @{Src=(Join-Path $PackageRoot 'data\R7A0_public_source_matrix.tsv');Dst=(Join-Path $RepoPath 'data\R7A0_public_source_matrix.tsv')}
)
foreach($m in $Map){
  if(!(Test-Path -LiteralPath $m.Src)){throw "Missing source: $($m.Src)"}
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $m.Dst) | Out-Null
  Copy-Item -LiteralPath $m.Src -Destination $m.Dst -Force
}
$TooLarge=Get-ChildItem -LiteralPath $RepoPath -Recurse -File | Where-Object {$_.FullName -notmatch '\\.git\\' -and $_.Length -gt 10MB}
if($TooLarge){$TooLarge|Select FullName,Length|Format-Table;throw 'Public repo >10 MB file gate failed'}

Push-Location $RepoPath
try{
  git fetch origin main
  if($LASTEXITCODE-ne 0){throw 'git fetch failed'}
  $local=(git rev-parse HEAD).Trim()
  $remote=(git rev-parse origin/main).Trim()
  if($local -ne $remote){throw "Local HEAD $local != origin/main $remote"}
  git add -- reports/00_CMM_R7A0_执行摘要_portfolio_preflight.md `
    reports/99_CMM_R7A0_详细行动记录_2026-09-15.md `
    reports/SOURCES_CHECKED_R7A0_2026-09-15.md `
    protocols/R7A1A_PBC_CeD_true_byte_QTL_preflight_v1.md `
    results/r7a0/R7A0_portfolio_decision_matrix.tsv `
    results/r7a0/R7A1A_frozen_positive_controls.tsv `
    results/r7a0/R7A0_state.json `
    data/R7A0_public_source_matrix.tsv
  git diff --cached --check
  if($LASTEXITCODE-ne 0){throw 'git diff --check failed'}
  if(-not (git status --short)){Write-Host 'NO_CHANGES';exit 0}
  git commit -m 'Add R7A0 completion-first portfolio preflight'
  if($LASTEXITCODE-ne 0){throw 'git commit failed'}
  git push origin main
  if($LASTEXITCODE-ne 0){throw 'git push failed'}
  $head=(git rev-parse HEAD).Trim()
  $remote2=(git ls-remote origin refs/heads/main).Split("`t")[0].Trim()
  if($head -ne $remote2){throw "remote verification failed: $head != $remote2"}
  Write-Host "R7A0_SYNC_PASS HEAD=$head"
} finally {Pop-Location}
