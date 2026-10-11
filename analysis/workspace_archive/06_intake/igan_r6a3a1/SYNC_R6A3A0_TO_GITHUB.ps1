param(
    [Parameter(Mandatory=$false)]
    [string]$RepoPath = 'H:\SCI2\YR1\9.Version\public_repro\igan-open-regulatory-evidence'
)
$ErrorActionPreference='Stop'

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = Split-Path -Parent $Here

if(!(Test-Path -LiteralPath $RepoPath)){ throw "RepoPath not found: $RepoPath" }
if(!(Test-Path -LiteralPath (Join-Path $RepoPath '.git'))){ throw "Not a git clone: $RepoPath" }

# Exact public-only paths from the execution package.
$Map = @(
    @{Src=(Join-Path $PackageRoot 'analysis\r6a3a'); Dst=(Join-Path $RepoPath 'analysis\r6a3a')},
    @{Src=(Join-Path $PackageRoot 'protocols\R6A3A_completion_design_gate_v2.md'); Dst=(Join-Path $RepoPath 'protocols\R6A3A_completion_design_gate_v2.md')},
    @{Src=(Join-Path $PackageRoot 'data\R6A3A_OPEN_DATA_MANIFEST.tsv'); Dst=(Join-Path $RepoPath 'data\R6A3A_OPEN_DATA_MANIFEST.tsv')},
    @{Src=(Join-Path $PackageRoot 'reports\00_CMM_R6A3A0_执行摘要_completion_design_gate.md'); Dst=(Join-Path $RepoPath 'reports\00_CMM_R6A3A0_执行摘要_completion_design_gate.md')},
    @{Src=(Join-Path $PackageRoot 'reports\99_CMM_R6A3A0_详细行动记录_2026-09-14.md'); Dst=(Join-Path $RepoPath 'reports\99_CMM_R6A3A0_详细行动记录_2026-09-14.md')},
    @{Src=(Join-Path $PackageRoot 'results\r6a3a\R6A3A0_state.json'); Dst=(Join-Path $RepoPath 'results\r6a3a\R6A3A0_state.json')}
)

foreach($m in $Map){
    if(!(Test-Path -LiteralPath $m.Src)){ throw "Missing package source: $($m.Src)" }
    $parent=Split-Path -Parent $m.Dst
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    if((Get-Item -LiteralPath $m.Src).PSIsContainer){
        New-Item -ItemType Directory -Force -Path $m.Dst | Out-Null
        Copy-Item -LiteralPath (Join-Path $m.Src '*') -Destination $m.Dst -Recurse -Force
    } else {
        Copy-Item -LiteralPath $m.Src -Destination $m.Dst -Force
    }
}

# Hard large-file gate.
$TooLarge = Get-ChildItem -LiteralPath $RepoPath -Recurse -File |
    Where-Object { $_.FullName -notmatch '\\.git\\' -and $_.Length -gt 10MB }
if($TooLarge){
    $TooLarge | Select-Object FullName,Length | Format-Table -AutoSize
    throw "Public repo contains file(s) >10 MB; aborting push."
}

# Targeted sensitive-string gate. This is deliberately conservative.
$Patterns = @(
    'ghp_[A-Za-z0-9]{20,}',
    'github_pat_[A-Za-z0-9_]{20,}',
    '-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----',
    '(?i)password\s*[:=]\s*["''][^"'']+["'']',
    '(?i)token\s*[:=]\s*["''][A-Za-z0-9_\-]{12,}["'']'
)
$PublicFiles = Get-ChildItem -LiteralPath $RepoPath -Recurse -File |
    Where-Object { $_.FullName -notmatch '\\.git\\' -and $_.Extension -match '\.(md|txt|tsv|csv|json|py|r|ps1|yml|yaml)$' }
foreach($f in $PublicFiles){
    $txt = Get-Content -LiteralPath $f.FullName -Raw -ErrorAction SilentlyContinue
    foreach($pat in $Patterns){
        if($txt -match $pat){ throw "Potential secret pattern found in $($f.FullName); aborting push." }
    }
}

Push-Location $RepoPath
try {
    $branch = (git branch --show-current).Trim()
    if($branch -ne 'main'){ throw "Expected main branch, found: $branch" }

    git fetch origin main
    if($LASTEXITCODE -ne 0){ throw "git fetch failed" }

    $local = (git rev-parse HEAD).Trim()
    $remote = (git rev-parse origin/main).Trim()
    if($local -ne $remote){
        throw "Local HEAD ($local) != origin/main ($remote). Reconcile manually before publishing."
    }

    git add -- analysis/r6a3a protocols/R6A3A_completion_design_gate_v2.md `
        data/R6A3A_OPEN_DATA_MANIFEST.tsv `
        reports/00_CMM_R6A3A0_执行摘要_completion_design_gate.md `
        reports/99_CMM_R6A3A0_详细行动记录_2026-09-14.md `
        results/r6a3a/R6A3A0_state.json

    $st = git status --short
    if(-not $st){
        Write-Host "No R6A3A0 public changes to commit."
        exit 0
    }

    Write-Host $st
    git diff --cached --check
    if($LASTEXITCODE -ne 0){ throw "git diff --check failed" }

    git commit -m 'Add R6A3A completion-design execution gate'
    if($LASTEXITCODE -ne 0){ throw "git commit failed" }

    git push origin main
    if($LASTEXITCODE -ne 0){ throw "git push failed" }

    $head=(git rev-parse HEAD).Trim()
    $remote2=(git ls-remote origin refs/heads/main).Split("`t")[0].Trim()
    if($head -ne $remote2){ throw "Remote HEAD verification failed: local=$head remote=$remote2" }

    Write-Host "R6A3A0_PUBLIC_SYNC_PASS"
    Write-Host "HEAD=$head"
} finally {
    Pop-Location
}
