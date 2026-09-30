$ErrorActionPreference = 'Stop'

$repo = 'H:\SCI2\YR1\github\igan-open-regulatory-evidence'
if (-not (Test-Path -LiteralPath (Join-Path $repo '.git'))) {
    throw "Git repository not found: $repo"
}

$branch = (git -C $repo branch --show-current).Trim()
if ($branch -ne 'main') {
    throw "Expected branch main, found: $branch"
}

$dirty = git -C $repo status --porcelain=v1
if ($dirty) {
    throw "Working tree is not clean. Review local changes before pushing."
}

git -C $repo diff HEAD^ HEAD --check
if ($LASTEXITCODE -ne 0) {
    throw "git diff --check failed for the release commit."
}

$oversized = git -C $repo ls-tree -r -l HEAD |
    ForEach-Object {
        if ($_ -match '^\d+\s+blob\s+[0-9a-f]+\s+(\d+)\t(.+)$') {
            [pscustomobject]@{ Bytes = [int64]$matches[1]; Path = $matches[2] }
        }
    } |
    Where-Object { $_.Bytes -gt 10MB }
if ($oversized) {
    $oversized | Format-Table -AutoSize | Out-String | Write-Host
    throw 'Files larger than 10 MB are present in HEAD.'
}

git -C $repo fetch origin main
if ($LASTEXITCODE -ne 0) {
    throw 'Could not fetch origin/main.'
}

$localHead = (git -C $repo rev-parse HEAD).Trim()
$remoteHead = (git -C $repo rev-parse origin/main).Trim()
$mergeBase = (git -C $repo merge-base HEAD origin/main).Trim()
if ($mergeBase -ne $remoteHead) {
    throw "Push is not a fast-forward. Local=$localHead Remote=$remoteHead MergeBase=$mergeBase"
}

git -C $repo push origin main
if ($LASTEXITCODE -ne 0) {
    throw 'git push failed.'
}

git -C $repo fetch origin main
$verifiedRemote = (git -C $repo rev-parse origin/main).Trim()
if ($verifiedRemote -ne $localHead) {
    throw "Remote verification failed. Local=$localHead Remote=$verifiedRemote"
}

Write-Host "R7A2A5 GitHub sync PASS: $verifiedRemote"
