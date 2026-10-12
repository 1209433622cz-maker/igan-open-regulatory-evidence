param(
  [Parameter(Mandatory=$true)][string]$RepoPath,
  [Parameter(Mandatory=$true)][string]$PackDir
)
$ErrorActionPreference='Stop'
$RepoPath=(Resolve-Path -LiteralPath $RepoPath).Path
$PackDir=(Resolve-Path -LiteralPath $PackDir).Path
if(!(Test-Path -LiteralPath (Join-Path $RepoPath '.git'))){throw "Not a git repository: $RepoPath"}
$mapping=@{
 'code\01_build_reep3_cd4nc_source_ld.py'='analysis\r6a2c\01_build_reep3_cd4nc_source_ld.py';
 'code\02_build_reep3_residual_ld.py'='analysis\r6a2c\02_build_reep3_residual_ld.py';
 'code\03_run_reep3_multisignal.R'='analysis\r6a2c\03_run_reep3_multisignal.R';
 'code\04_adjudicate_reep3.py'='analysis\r6a2c\04_adjudicate_reep3.py';
 'code\RUN_R6A2C_REEP3_FALSIFICATION.ps1'='analysis\r6a2c\RUN_R6A2C_REEP3_FALSIFICATION.ps1';
 'protocol\R6A2C_frozen_config.json'='protocols\R6A2C_frozen_config.json';
 'reports\00_CMM_R6A2C0_执行摘要_REEP3执行闭环.md'='reports\00_CMM_R6A2C0_执行摘要_REEP3执行闭环.md';
 'reports\99_CMM_R6A2C0_详细行动记录_2026-09-14.md'='reports\99_CMM_R6A2C0_详细行动记录_2026-09-14.md';
 'results\R6A2C_frozen_smoke_baseline.tsv'='results\r6a2c\R6A2C_frozen_smoke_baseline.tsv'
}
foreach($srcRel in $mapping.Keys){
 $src=Join-Path $PackDir $srcRel; if(!(Test-Path -LiteralPath $src)){throw "Missing pack file: $src"}
 $dst=Join-Path $RepoPath $mapping[$srcRel]; New-Item -ItemType Directory -Force -Path (Split-Path $dst -Parent)|Out-Null; Copy-Item -LiteralPath $src -Destination $dst -Force
}
Push-Location $RepoPath
try{
 git status --short
 git add analysis/r6a2c protocols/R6A2C_frozen_config.json reports/00_CMM_R6A2C0_执行摘要_REEP3执行闭环.md reports/99_CMM_R6A2C0_详细行动记录_2026-09-14.md results/r6a2c/R6A2C_frozen_smoke_baseline.tsv
 if((git diff --cached --name-only).Count -eq 0){Write-Host 'No staged changes.'; exit 0}
 git commit -m 'Add R6A2C REEP3 ancestry-specific falsification gate'
 git push origin main
 git rev-parse HEAD
} finally { Pop-Location }
