$ErrorActionPreference = 'Stop'

$Repo = 'H:\SCI2\YR1\github\igan-open-regulatory-evidence'
$Tag = 'r7b4a-human-genomics-interface-2026-10-10'
$ExpectedAssetCommit = 'f1c7040c3db114967c7f8385d6ad9f126a4d2d3f'

Set-Location -LiteralPath $Repo
if ((git branch --show-current).Trim() -ne 'main') { throw 'Repository is not on main.' }
if (git status --porcelain) { throw 'Repository is not clean. Review local changes before sync.' }

$head = (git rev-parse HEAD).Trim()
if (-not (git merge-base --is-ancestor $ExpectedAssetCommit $head)) {
    throw "Expected R7B4A asset commit is not an ancestor of HEAD: $ExpectedAssetCommit"
}

$large = Get-ChildItem -LiteralPath @(
    "$Repo\analysis\r7b4a",
    "$Repo\figures\R7B4A",
    "$Repo\manuscript\r7b4a",
    "$Repo\results\r7b4a"
) -Recurse -File | Where-Object Length -gt 10MB
if ($large) { throw "Public-file size gate failed: $($large.FullName -join ', ')" }

$pattern = '(api[_-]?key\s*[:=]|access[_-]?token\s*[:=]|password\s*[:=]|passwd\s*[:=]|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,})'
$scan = rg -n -i $pattern analysis/r7b4a figures/R7B4A manuscript/r7b4a results/r7b4a `
    'protocols/R7B4B_作者补全与最终投稿QA冻结协议.md' `
    'reports/99_CMM_R7B4A_期刊资格冻结与投稿接口_详细行动记录_2026-10-10.md'
if ($LASTEXITCODE -eq 0) { throw "Secret-pattern scan returned hits:`n$scan" }
if ($LASTEXITCODE -ne 1) { throw 'Secret-pattern scan did not complete normally.' }

git fetch origin main
$remoteBefore = (git rev-parse origin/main).Trim()
if (-not (git merge-base --is-ancestor $remoteBefore $head)) {
    throw "Remote main is not an ancestor of local HEAD. Refusing non-fast-forward push: $remoteBefore"
}

if (-not (git tag --list $Tag)) {
    git tag -a $Tag -m 'R7B4A Human Genomics submission interface'
}
elseif ((git rev-list -n 1 $Tag).Trim() -ne $head) {
    throw "Local tag $Tag exists at a different commit."
}

git push origin main
git push origin "refs/tags/$Tag"
git fetch origin main --tags

$remoteAfter = (git rev-parse origin/main).Trim()
$remoteTag = (git rev-list -n 1 $Tag).Trim()
if ($remoteAfter -ne $head) { throw "Remote HEAD mismatch: local=$head remote=$remoteAfter" }
if ($remoteTag -ne $head) { throw "Tag mismatch: local=$head tag=$remoteTag" }

Write-Output "GITHUB_SYNC_PASS`t$remoteAfter`t$Tag"
