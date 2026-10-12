[CmdletBinding()]
param(
  [switch]$Execute
)

$ErrorActionPreference = 'Stop'
$CodeRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = (Resolve-Path (Join-Path $CodeRoot '..\..\..')).Path
$Destination = Join-Path $WorkspaceRoot '1_data\gwas\outcome\ssc_finngen_r12_r13\metadata\regenie_single_sex_drop_list_plus_reason_262_endpoints.txt'
$Uri = 'gs://finngen-production-library-green/finngen_R12/finngen_R12_analysis_data/sex_difference/regenie_single_sex_drop_list_plus_reason_262_endpoints.txt'

$Gcloud = Get-Command 'gcloud.cmd' -ErrorAction SilentlyContinue
if (-not $Gcloud) {
  Write-Output 'HOLD_GREEN_LIBRARY_AUTH_REQUIRED: gcloud.cmd is not installed or not on PATH'
  exit 3
}
$RawAccounts = & $Gcloud.Source auth list '--format=json' 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Output 'HOLD_GREEN_LIBRARY_AUTH_REQUIRED: unable to read gcloud authentication state'
  exit 3
}
$AccountObjects = if ($RawAccounts) { @($RawAccounts | ConvertFrom-Json) } else { @() }
$Accounts = @($AccountObjects | Where-Object { $_.status -eq 'ACTIVE' } | ForEach-Object { $_.account })
if ($Accounts.Count -eq 0) {
  Write-Output 'HOLD_GREEN_LIBRARY_AUTH_REQUIRED: no active gcloud account'
  Write-Output 'Authenticate the account authorized by the FinnGen access email, then rerun with -Execute.'
  exit 3
}

Write-Output "Active account: $($Accounts -join ', ')"
Write-Output "Source: $Uri"
Write-Output "Destination: $Destination"
if (-not $Execute) {
  Write-Output 'DRY_RUN_ONLY: rerun with -Execute to copy the small drop-list object.'
  exit 0
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
gsutil cp $Uri $Destination
if ($LASTEXITCODE -ne 0) {
  throw "gsutil failed with exit code $LASTEXITCODE"
}
$Matches = @(Select-String -LiteralPath $Destination -Pattern '^M13_SYSTSLCE(?:\s|$)' -CaseSensitive)
$Status = if ($Matches.Count -gt 0) { 'R12_SEX_SPECIFIC_UNAVAILABLE_BY_DESIGN' } else { 'R12_SEX_SPECIFIC_NOT_IN_DROP_LIST_CONTINUE_OBJECT_DISCOVERY' }
[pscustomobject]@{
  status = $Status
  source = $Uri
  destination = $Destination
  bytes = (Get-Item -LiteralPath $Destination).Length
  sha256 = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash.ToLower()
  exact_match_count = $Matches.Count
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath ($Destination + '.receipt.json') -Encoding utf8
Write-Output $Status
