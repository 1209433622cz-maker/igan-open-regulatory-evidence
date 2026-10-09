$ErrorActionPreference = 'Stop'

$Repo = 'H:\SCI2\YR1\github\igan-open-regulatory-evidence'
$Tag = 'r7b4b0-preauthor-final-submission-gate-2026-10-10'
$ReleaseCommit = 'cc8e7cdf177d574615fefa7d9fa12c73c5f3add7'

Set-Location -LiteralPath $Repo
if ((git branch --show-current).Trim() -ne 'main') { throw 'Repository is not on main.' }
if (git status --porcelain) { throw 'Repository is not clean.' }
$head = (git rev-parse HEAD).Trim()
git merge-base --is-ancestor $ReleaseCommit $head
if ($LASTEXITCODE -ne 0) { throw 'R7B4B0 release commit is not an ancestor of HEAD.' }

$tagCommit = (git rev-parse "refs/tags/$Tag^{}").Trim()
if ($tagCommit -ne $ReleaseCommit) { throw "Local release tag mismatch: $tagCommit" }

$large = Get-ChildItem -LiteralPath @(
    "$Repo\analysis\r7b4b",
    "$Repo\results\r7b4b0",
    "$Repo\protocols\R7B4B"
) -Recurse -File | Where-Object Length -gt 10MB
if ($large) { throw "Public size gate failed: $($large.FullName -join ', ')" }

$pattern = '(api[_-]?key\s*[:=]|access[_-]?token\s*[:=]|password\s*[:=]|passwd\s*[:=]|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,})'
$scan = rg -n -i $pattern analysis/r7b4b results/r7b4b0 protocols/R7B4B `
    'reports/99_CMM_R7B4B0_作者信息前独立投稿门复核_2026-10-10.md'
if ($LASTEXITCODE -eq 0) { throw "Secret-pattern scan returned hits:`n$scan" }
if ($LASTEXITCODE -ne 1) { throw 'Secret scan did not complete normally.' }

git fetch origin main --tags
$remoteBefore = (git rev-parse origin/main).Trim()
git merge-base --is-ancestor $remoteBefore $head
if ($LASTEXITCODE -ne 0) { throw "Refusing non-fast-forward push from $remoteBefore to $head" }

git push origin main
git push origin "refs/tags/$Tag"
git fetch origin main --tags
$remoteAfter = (git rev-parse origin/main).Trim()
$remoteTag = (git rev-parse "refs/tags/$Tag^{}").Trim()
if ($remoteAfter -ne $head) { throw "Remote main mismatch: $remoteAfter" }
if ($remoteTag -ne $ReleaseCommit) { throw "Remote tag mismatch: $remoteTag" }
Write-Output "GITHUB_SYNC_PASS`t$remoteAfter`t$Tag`t$remoteTag"
