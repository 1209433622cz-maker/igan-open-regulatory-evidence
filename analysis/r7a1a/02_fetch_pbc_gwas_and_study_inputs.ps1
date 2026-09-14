param(
  [string]$ProjectRoot=$env:R7_PROJECT_ROOT,
  [switch]$DownloadFullGJOKA
)
$ErrorActionPreference='Stop'
if([string]::IsNullOrWhiteSpace($ProjectRoot)){
  $RepoCandidate=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
  if(Test-Path -LiteralPath (Join-Path $RepoCandidate '.git')){$ProjectRoot=$RepoCandidate}
  else{$ProjectRoot=(Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path}
}
$Out=Join-Path $ProjectRoot '1_data\gwas\R7A1A\PBC'
$Study=Join-Path $ProjectRoot '1_data\study_inputs\PBC_GJOKA'
$Audit=Join-Path $ProjectRoot '3_results\01_intake\R7A1A'
$Fetch=Join-Path $PSScriptRoot '00_segmented_fetch.py'
New-Item -ItemType Directory -Force -Path $Out,$Study,$Audit | Out-Null
$url='https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST90061001-GCST90062000/GCST90061440/GCST90061440_buildGRCh37.tsv'
$dest=Join-Path $Out 'GCST90061440_buildGRCh37.tsv'
if(!(Test-Path -LiteralPath $dest)){
  python $Fetch --connections 8 $url $dest
  if($LASTEXITCODE-ne 0){throw 'PBC GWAS download failed'}
}
$row=[pscustomobject]@{candidate='PBC';accession='GCST90061440';role='eligible_core';url=$url;file=(Split-Path -Leaf $dest);
 bytes=(Get-Item -LiteralPath $dest).Length;md5=(Get-FileHash -LiteralPath $dest -Algorithm MD5).Hash.ToLower();
 sha256=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLower();status='PASS'}
$row | Export-Csv -Delimiter "`t" -NoTypeInformation -Encoding utf8 (Join-Path $Audit 'R7A1A_PBC_byte_receipt.tsv')

python (Join-Path $PSScriptRoot '05_inventory_gjoka_remote_zip.py')
if($LASTEXITCODE-ne 0){throw 'GJOKA remote inventory failed'}
if($DownloadFullGJOKA){
  $z=Join-Path $Study 'GJOKA_SUMSTATS.zip'
  if(!(Test-Path -LiteralPath $z)){
    python $Fetch --connections 8 'https://www.staff.ncl.ac.uk/heather.cordell/GJOKA_SUMSTATS.zip' $z
    if($LASTEXITCODE-ne 0){throw 'GJOKA full archive download failed'}
  }
  Get-FileHash -LiteralPath $z -Algorithm SHA256 | Format-Table -AutoSize
}
$row | Format-Table -AutoSize
