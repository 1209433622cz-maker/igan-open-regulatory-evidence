param(
    [ValidateSet("GenotypeOnly", "All")]
    [string]$Mode = "All",
    [string]$Workspace = "H:\SCI2\YR1",
    [ValidateRange(1, 8)]
    [int]$Concurrency = 2
)

$ErrorActionPreference = "Stop"

function Invoke-ResumableDownload {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][string]$Output,
        [Parameter(Mandatory = $true)][long]$ExpectedBytes,
        [Parameter(Mandatory = $true)][string]$ExpectedMd5
    )

    $downloader = Join-Path $Workspace "2_code\06_intake\mg_r5a1\multirange_download.py"
    if (-not (Test-Path -LiteralPath $downloader)) {
        throw "Downloader not found: $downloader"
    }

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null
    & python $downloader $Url $Output --size $ExpectedBytes --workers 8 --concurrency $Concurrency
    if ($LASTEXITCODE -ne 0) {
        throw "Download is incomplete. Re-run this command; completed range files are retained."
    }

    $actualBytes = (Get-Item -LiteralPath $Output).Length
    if ($actualBytes -ne $ExpectedBytes) {
        throw "Byte-size mismatch for $Output`: $actualBytes != $ExpectedBytes"
    }
    $actualMd5 = (Get-FileHash -Algorithm MD5 -LiteralPath $Output).Hash.ToLowerInvariant()
    if ($actualMd5 -ne $ExpectedMd5.ToLowerInvariant()) {
        throw "MD5 mismatch for $Output`: $actualMd5 != $ExpectedMd5"
    }
    Write-Host "BYTE_AND_MD5_PASS`t$Output`t$actualBytes`t$actualMd5"
}

$oneKDir = Join-Path $Workspace "1_data\qtl\OneK1K"
$tenKDir = Join-Path $Workspace "1_data\qtl\TenK10K"

# The current v2 record (18910121) has the same filename, byte count, and MD5 as
# record 18870747. Existing range parts created from the earlier record can resume.
$genotypePath = Join-Path $oneKDir "plink_genotype_merged_980_donors.zip"
Invoke-ResumableDownload `
    -Url "https://zenodo.org/records/18910121/files/plink_genotype_merged_980_donors.zip?download=1" `
    -Output $genotypePath `
    -ExpectedBytes 233198074 `
    -ExpectedMd5 "be1053e34fa023bc808388d4e0bf2aa1"

$genotypeAudit = Join-Path $Workspace "2_code\06_intake\mg_r5a1\audit_onek_genotype.py"
& python $genotypeAudit
if ($LASTEXITCODE -ne 0) {
    throw "OneK1K PLINK audit failed. Do not start LD estimation."
}

if ($Mode -eq "GenotypeOnly") {
    Write-Host "GENOTYPE_ONLY_COMPLETE"
    exit 0
}

Invoke-ResumableDownload `
    -Url "https://zenodo.org/records/18910121/files/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz?download=1" `
    -Output (Join-Path $oneKDir "OneK1K_TensorQTL_raw_eQTL_summary.tar.gz") `
    -ExpectedBytes 10344009571 `
    -ExpectedMd5 "e42239480f40abd21f221c0d77c82cc3"

Invoke-ResumableDownload `
    -Url "https://zenodo.org/records/18221260/files/common_all_cis_pvalues_100kb.zip?download=1" `
    -Output (Join-Path $tenKDir "common_all_cis_pvalues_100kb.zip") `
    -ExpectedBytes 16559137990 `
    -ExpectedMd5 "dd54714b2effb91160ac171ccb941534"

Write-Host "R5A2_LARGE_INPUT_TRANSFER_COMPLETE"

