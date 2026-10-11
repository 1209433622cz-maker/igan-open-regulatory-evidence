[CmdletBinding()]
param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$WorkspaceRoot = "H:\SCI2\YR1",
    [ValidateRange(1, 12)][int]$Workers = 4,
    [ValidateRange(1, 64)][int]$ChunkMiB = 8
)

$ErrorActionPreference = "Stop"
$scriptPath = Join-Path $WorkspaceRoot "2_code\06_intake\tenk10k_il12rb2\download_extract_tenk10k_nk_resume.py"
$outputDir = Join-Path $WorkspaceRoot "1_data\qtl\eqtl\tenk10k\derived\IL12RB2_full\remote_NK"

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python executable not found: $Python"
}
if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    throw "Intake script not found: $scriptPath"
}

$driveName = ([System.IO.Path]::GetPathRoot($outputDir)).TrimEnd('\').TrimEnd(':')
$drive = Get-PSDrive -Name $driveName
if ($drive.Free -lt 2GB) {
    throw "At least 2 GB free space is required for the selective NK cache and outputs."
}

& $Python $scriptPath --self-test
if ($LASTEXITCODE -ne 0) { throw "Downloader self-test failed." }

New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
& $Python $scriptPath --outdir $outputDir --workers $Workers --chunk-mib $ChunkMiB
if ($LASTEXITCODE -ne 0) {
    throw "TenK10K NK selective intake is incomplete. Re-run this same command to resume completed chunks."
}

Write-Host "PASS: NK IL12RB2 full variant-level eQTL extract is ready."
Write-Host (Join-Path $outputDir "NK_IL12RB2_full_variant_eqtl.tsv")
