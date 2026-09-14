$ErrorActionPreference="Stop"
$Root = if ($env:IGAN_PROJECT_ROOT) { $env:IGAN_PROJECT_ROOT } else { (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path }
$Out = Join-Path $Root '1_data\scrna\IgAN\GSE127136'
$Audit = Join-Path $Root '3_results\00_audit\R6A3A'
New-Item -ItemType Directory -Force -Path $Out,$Audit | Out-Null
$Count = Join-Path $Out 'GSE127136_project_IgA_nephropathy_counts.csv.gz'
$Soft = Join-Path $Out 'GSE127136_family.soft.gz'
$CountUrl='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE127nnn/GSE127136/suppl/GSE127136_project_IgA_nephropathy_counts.csv.gz'
$SoftUrl='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE127nnn/GSE127136/soft/GSE127136_family.soft.gz'
function Fetch([string]$Url,[string]$Dest) {
  if(!(Test-Path $Dest)){
    $Part="$Dest.part"
    & curl.exe -L --fail --retry 10 --retry-delay 3 --retry-all-errors -C - -o $Part $Url
    if($LASTEXITCODE-ne 0){throw "curl failed $Url"}
    Move-Item -Force $Part $Dest
  }
}
Fetch $CountUrl $Count
Fetch $SoftUrl $Soft
$ExpectedCountBytes=15703242
$ExpectedCountSha='89c3580ad550ae5df9e736bba97101f0ae02e724201b61d2e1f5fa4247dbce40'
if((Get-Item $Count).Length -ne $ExpectedCountBytes){throw "GSE127136 count byte mismatch"}
if((Get-FileHash -Algorithm SHA256 $Count).Hash.ToLower() -ne $ExpectedCountSha){throw "GSE127136 count SHA256 mismatch"}
@(
 [pscustomobject]@{file=(Split-Path $Count -Leaf);url=$CountUrl;bytes=(Get-Item $Count).Length;sha256=(Get-FileHash -Algorithm SHA256 $Count).Hash.ToLower();status='PASS'},
 [pscustomobject]@{file=(Split-Path $Soft -Leaf);url=$SoftUrl;bytes=(Get-Item $Soft).Length;sha256=(Get-FileHash -Algorithm SHA256 $Soft).Hash.ToLower();status='PASS'}
) | Export-Csv -Delimiter "`t" -NoTypeInformation -Encoding utf8 (Join-Path $Audit 'R6A3A_GSE127136_byte_receipt.tsv')
