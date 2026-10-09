$ErrorActionPreference = 'Stop'

$Root = 'H:\SCI2\YR1'
$Repo = Join-Path $Root 'github\igan-open-regulatory-evidence'
$Code = Join-Path $Root '2_code\11_manuscript\R7B4B1'
$Receipt = Join-Path $Root '6_release\R7B4B2_2026-10-10\R7B4B2_zenodo_receipt.json'
$Tag = 'r7b4b2-author-approved-open-research-release-2026-10-10'
$Python = 'D:\bioinfor\python.exe'

if ([string]::IsNullOrWhiteSpace($env:ZENODO_TOKEN)) {
    Write-Host @'
ZENODO_TOKEN is not set. Create a Zenodo token at
https://zenodo.org/account/settings/applications/tokens/new/
with deposit:write and deposit:actions scopes. The next prompt is masked; do not
paste the token into chat, scripts, Git or a text file.
'@
    $SecureToken = Read-Host 'Zenodo token' -AsSecureString
    $env:ZENODO_TOKEN = [System.Net.NetworkCredential]::new('', $SecureToken).Password
    if ([string]::IsNullOrWhiteSpace($env:ZENODO_TOKEN)) { throw 'No Zenodo token supplied' }
}

& $Python (Join-Path $Code 'publish_r7b4b2_to_zenodo.py') --publish
if ($LASTEXITCODE -ne 0) { throw "Zenodo publisher failed with exit code $LASTEXITCODE" }

& $Python (Join-Path $Code 'bind_r7b4b2_zenodo_doi.py') --receipt $Receipt
if ($LASTEXITCODE -ne 0) { throw "DOI binder failed with exit code $LASTEXITCODE" }

git -C $Repo diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff --check failed' }

$secretHit = rg -n --hidden --glob '!.git/**' 'ZENODO_TOKEN\s*=\s*["''][^"'']+' $Repo
if ($LASTEXITCODE -eq 0) { throw "Possible token literal detected:`n$secretHit" }

git -C $Repo add -- CITATION.cff README.md MANIFEST.sha256 results/r7b4b2 reports/r7b4b2
git -C $Repo commit -m 'Bind R7B4B2 Zenodo DOI'
git -C $Repo push origin main

$ReceiptObject = Get-Content $Receipt -Raw | ConvertFrom-Json
$Doi = if ($ReceiptObject.doi) { $ReceiptObject.doi } else { $ReceiptObject.reserved_doi }
$CurrentBody = gh release view $Tag --repo '1209433622cz-maker/igan-open-regulatory-evidence' --json body --jq .body
$Notes = Join-Path (Split-Path $Receipt) 'GITHUB_RELEASE_NOTES_WITH_DOI.md'
Set-Content -LiteralPath $Notes -Encoding utf8 -Value ($CurrentBody.TrimEnd() + "`n`nZenodo DOI: https://doi.org/$Doi`n")
gh release edit $Tag --repo '1209433622cz-maker/igan-open-regulatory-evidence' --notes-file $Notes

Write-Output "ZENODO_DOI_PUBLISHED=https://doi.org/$Doi"
