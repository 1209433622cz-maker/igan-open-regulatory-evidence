param([string]$ProjectRoot=$env:R7_PROJECT_ROOT)
$ErrorActionPreference='Stop'
if([string]::IsNullOrWhiteSpace($ProjectRoot)){
  $RepoCandidate=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
  if(Test-Path -LiteralPath (Join-Path $RepoCandidate '.git')){$ProjectRoot=$RepoCandidate}
  else{$ProjectRoot=(Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path}
}
$Out=Join-Path $ProjectRoot '1_data\gwas\R7A1A\CeD'
$Audit=Join-Path $ProjectRoot '3_results\01_intake\R7A1A'
$Fetch=Join-Path $PSScriptRoot '00_segmented_fetch.py'
New-Item -ItemType Directory -Force -Path $Out,$Audit | Out-Null

# GCST000612 is the eligible non-UKB genome-wide-array source with a harmonised
# beta/SE/allele schema. GCST010064 is the later Immunochip study that motivated
# the controls; it is retained as a source audit object because it has OR/P but no SE.
$items=@(
 @{Accession='GCST000612';Role='eligible_core';Name='GCST000612_20190752.h.tsv.gz';Url='https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST000001-GCST001000/GCST000612/harmonised/20190752-GCST000612-EFO_0001060.h.tsv.gz'},
 @{Accession='GCST010064';Role='secondary_missing_SE';Name='GCST010064_Meta.PL.IT.IR.SP.UK.AR1.AR2.NL.2017.meta.csv';Url='https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST010001-GCST011000/GCST010064/Meta.PL.IT.IR.SP.UK.AR1.AR2.NL.2017.meta.csv'}
)
$rows=@()
foreach($it in $items){
  $dest=Join-Path $Out $it.Name
  if(!(Test-Path -LiteralPath $dest)){
    python $Fetch --connections 6 $it.Url $dest
    if($LASTEXITCODE-ne 0){throw "Download failed: $($it.Url)"}
  }
  $rows += [pscustomobject]@{candidate='CeD';accession=$it.Accession;role=$it.Role;url=$it.Url;file=$it.Name;
    bytes=(Get-Item -LiteralPath $dest).Length;md5=(Get-FileHash -LiteralPath $dest -Algorithm MD5).Hash.ToLower();
    sha256=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLower();status='PASS'}
}
$rows | Export-Csv -Delimiter "`t" -NoTypeInformation -Encoding utf8 (Join-Path $Audit 'R7A1A_CeD_byte_receipt.tsv')
$rows | Format-Table -AutoSize
