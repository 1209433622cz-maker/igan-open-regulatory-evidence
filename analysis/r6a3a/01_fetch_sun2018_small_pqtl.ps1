$ErrorActionPreference = "Stop"
$Root = if ($env:IGAN_PROJECT_ROOT) { $env:IGAN_PROJECT_ROOT } else { (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path }
$Out = Join-Path $Root '1_data\qtl\eQTLCatalogue\Sun_2018_QTD000584'
$Audit = Join-Path $Root '3_results\00_audit\R6A3A'
New-Item -ItemType Directory -Force -Path $Out,$Audit | Out-Null

$Items = @(
  @{Name='QTD000584.permuted.tsv.gz'; Url='https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/QTS000035/QTD000584/QTD000584.permuted.tsv.gz'; Declared='128K'},
  @{Name='QTD000584.credible_sets.tsv.gz'; Url='https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/susie/QTS000035/QTD000584/QTD000584.credible_sets.tsv.gz'; Declared='1.0M'}
)

function Get-ResumeFile([string]$Url,[string]$Dest) {
    if (Test-Path $Dest) {
        Write-Host "EXISTS $Dest"
        return
    }
    $Part = "$Dest.part"
    & curl.exe -L --fail --retry 10 --retry-delay 3 --retry-all-errors -C - -o $Part $Url
    if ($LASTEXITCODE -ne 0) { throw "curl failed: $Url" }
    Move-Item -Force $Part $Dest
}

$Rows = @()
foreach ($it in $Items) {
    $dest = Join-Path $Out $it.Name
    Get-ResumeFile $it.Url $dest
    $fi = Get-Item $dest
    $sha = (Get-FileHash -Algorithm SHA256 $dest).Hash.ToLower()
    $md5 = (Get-FileHash -Algorithm MD5 $dest).Hash.ToLower()
    $Rows += [pscustomobject]@{
        dataset_id='QTD000584'; study='Sun_2018'; donors=3301; assay='aptamer'; build='GRCh38'
        effect_allele='ALT'; file=$it.Name; url=$it.Url; ftp_declared_size=$it.Declared
        bytes=$fi.Length; md5=$md5; sha256=$sha; status='PASS'
    }
}
$Receipt = Join-Path $Audit 'R6A3A_Sun2018_small_byte_receipt.tsv'
$Rows | Export-Csv -Delimiter "`t" -NoTypeInformation -Encoding utf8 $Receipt
Write-Host "WROTE $Receipt"
