param(
  [string]$RepoPath='H:\SCI2\YR1\9.Version\public_repro\igan-open-regulatory-evidence'
)
$ErrorActionPreference='Stop'
$Here=Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot=Split-Path -Parent $Here
if(!(Test-Path -LiteralPath $RepoPath)){throw "RepoPath not found: $RepoPath"}
if(!(Test-Path -LiteralPath (Join-Path $RepoPath '.git'))){throw "Not a git clone: $RepoPath"}
$Map=@(
 @{Src=(Join-Path $PackageRoot 'code');Dst=(Join-Path $RepoPath 'analysis\r7a1b')},
 @{Src=(Join-Path $PackageRoot 'protocol\R7A1B_PBC_3control_bounded_signal_gate_v2.md');Dst=(Join-Path $RepoPath 'protocols\R7A1B_PBC_3control_bounded_signal_gate_v2.md')},
 @{Src=(Join-Path $PackageRoot 'reports\00_CMM_R7A1B0_执行摘要_PBC三正控signal_gate加固.md');Dst=(Join-Path $RepoPath 'reports\r7a1b\00_CMM_R7A1B0_执行摘要_PBC三正控signal_gate加固.md')},
 @{Src=(Join-Path $PackageRoot 'reports\99_CMM_R7A1B0_详细行动记录_2026-09-15.md');Dst=(Join-Path $RepoPath 'reports\r7a1b\99_CMM_R7A1B0_详细行动记录_2026-09-15.md')},
 @{Src=(Join-Path $PackageRoot 'reports\SOURCES_CHECKED_R7A1B0_2026-09-15.md');Dst=(Join-Path $RepoPath 'reports\r7a1b\SOURCES_CHECKED_R7A1B0_2026-09-15.md')},
 @{Src=(Join-Path $PackageRoot 'results');Dst=(Join-Path $RepoPath 'results\r7a1b0')}
)
foreach($m in $Map){
  if(!(Test-Path -LiteralPath $m.Src)){throw "Missing source: $($m.Src)"}
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $m.Dst) | Out-Null
  if((Get-Item -LiteralPath $m.Src).PSIsContainer){
    New-Item -ItemType Directory -Force -Path $m.Dst | Out-Null
    Copy-Item -Path (Join-Path $m.Src '*') -Destination $m.Dst -Recurse -Force
  }else{Copy-Item -LiteralPath $m.Src -Destination $m.Dst -Force}
}
# Remove compiled caches if copied.
Get-ChildItem -LiteralPath $RepoPath -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
$TooLarge=Get-ChildItem -LiteralPath $RepoPath -Recurse -File | Where-Object {$_.FullName -notmatch '\\.git\\' -and $_.Length -gt 10MB}
if($TooLarge){$TooLarge|Select FullName,Length|Format-Table;throw 'Public repo >10 MB gate failed'}
$patterns=@('ghp_[A-Za-z0-9]{20,}','github_pat_[A-Za-z0-9_]{20,}','-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----')
$files=Get-ChildItem -LiteralPath $RepoPath -Recurse -File | Where-Object {$_.FullName -notmatch '\\.git\\' -and $_.Extension -match '\.(md|txt|tsv|csv|json|py|r|ps1|yml|yaml)$'}
foreach($f in $files){$txt=Get-Content -LiteralPath $f.FullName -Raw -ErrorAction SilentlyContinue;foreach($pat in $patterns){if($txt -match $pat){throw "Potential secret in $($f.FullName)"}}}
Push-Location $RepoPath
try{
  if((git branch --show-current).Trim() -ne 'main'){throw 'Expected main branch'}
  git fetch origin main;if($LASTEXITCODE-ne 0){throw 'git fetch failed'}
  $local=(git rev-parse HEAD).Trim();$remote=(git rev-parse origin/main).Trim()
  if($local -ne $remote){throw "Local HEAD $local != origin/main $remote"}
  git add -- analysis/r7a1b protocols/R7A1B_PBC_3control_bounded_signal_gate_v2.md reports/r7a1b results/r7a1b0
  git diff --cached --check;if($LASTEXITCODE-ne 0){throw 'git diff --check failed'}
  if(-not (git status --short)){Write-Host 'NO_CHANGES';exit 0}
  git commit -m 'Add R7A1B PBC bounded signal gate hardening';if($LASTEXITCODE-ne 0){throw 'git commit failed'}
  git push origin main;if($LASTEXITCODE-ne 0){throw 'git push failed'}
  $head=(git rev-parse HEAD).Trim();$remote2=(git ls-remote origin refs/heads/main).Split("`t")[0].Trim()
  if($head -ne $remote2){throw "remote verification failed: $head != $remote2"}
  Write-Host "R7A1B0_SYNC_PASS HEAD=$head"
}finally{Pop-Location}
