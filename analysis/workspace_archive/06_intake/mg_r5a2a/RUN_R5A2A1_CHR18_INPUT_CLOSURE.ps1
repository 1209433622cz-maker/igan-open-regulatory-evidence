param(
    [ValidateSet("GenotypeAudit", "OneKPrimary", "FullReplication")]
    [string]$Mode = "OneKPrimary",
    [string]$Workspace = "H:\SCI2\YR1",
    [ValidateRange(1, 8)]
    [int]$Concurrency = 2
)

$ErrorActionPreference = "Stop"

function Invoke-CheckedDownload {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][string]$Output,
        [Parameter(Mandatory = $true)][long]$ExpectedBytes,
        [Parameter(Mandatory = $true)][string]$ExpectedMd5
    )
    $downloader = Join-Path $Workspace "2_code\06_intake\mg_r5a1\multirange_download.py"
    if (-not (Test-Path -LiteralPath $downloader)) { throw "Missing downloader: $downloader" }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null
    & python $downloader $Url $Output --size $ExpectedBytes --workers 8 --concurrency $Concurrency
    if ($LASTEXITCODE -ne 0) { throw "Download incomplete. Re-run the same command to resume retained range parts." }
    $bytes = (Get-Item -LiteralPath $Output).Length
    $md5 = (Get-FileHash -Algorithm MD5 -LiteralPath $Output).Hash.ToLowerInvariant()
    if ($bytes -ne $ExpectedBytes) { throw "Byte mismatch: $bytes != $ExpectedBytes" }
    if ($md5 -ne $ExpectedMd5.ToLowerInvariant()) { throw "MD5 mismatch: $md5 != $ExpectedMd5" }
    Write-Host "BYTE_AND_MD5_PASS`t$Output`t$bytes`t$md5"
}

$audit = Join-Path $Workspace "2_code\06_intake\mg_r5a1\audit_onek_genotype.py"
& python $audit
if ($LASTEXITCODE -ne 0) { throw "OneK1K genotype audit failed." }
if ($Mode -eq "GenotypeAudit") { Write-Host "GENOTYPE_AUDIT_COMPLETE"; exit 0 }

$oneK = Join-Path $Workspace "1_data\qtl\OneK1K\OneK1K_TensorQTL_raw_eQTL_summary.tar.gz"
Invoke-CheckedDownload `
    -Url "https://zenodo.org/records/18910121/files/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz?download=1" `
    -Output $oneK `
    -ExpectedBytes 10344009571 `
    -ExpectedMd5 "e42239480f40abd21f221c0d77c82cc3"

if ($Mode -eq "OneKPrimary") {
    Write-Host "ONEK_PRIMARY_INPUT_COMPLETE"
    Write-Host "Return the completed archive for member/schema inspection before starting inference."
    exit 0
}

$tenK = Join-Path $Workspace "1_data\qtl\TenK10K\common_all_cis_pvalues_100kb.zip"
Invoke-CheckedDownload `
    -Url "https://zenodo.org/records/18221260/files/common_all_cis_pvalues_100kb.zip?download=1" `
    -Output $tenK `
    -ExpectedBytes 16559137990 `
    -ExpectedMd5 "dd54714b2effb91160ac171ccb941534"
Write-Host "FULL_REPLICATION_INPUTS_COMPLETE"
