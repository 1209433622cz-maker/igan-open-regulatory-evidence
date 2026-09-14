$ErrorActionPreference="Stop"
$Root = if ($env:IGAN_PROJECT_ROOT) { $env:IGAN_PROJECT_ROOT } else { (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path }
$Data = Join-Path $Root '1_data\qtl\eQTLCatalogue\Sun_2018_QTD000584'
$Ref = Join-Path $Root '1_data\reference\liftover'
$Audit = Join-Path $Root '3_results\00_audit\R6A3A'
$Candidate = Join-Path $Root '3_results\04_integration\R6A3A\R6A3A_pqtl_candidate_molecular_traits.tsv'
New-Item -ItemType Directory -Force -Path $Data,$Ref,$Audit | Out-Null
if (!(Test-Path $Candidate)) { throw "Run 02_screen_sun2018_frozen_targets.py first" }
$lines = (Get-Content $Candidate | Measure-Object -Line).Lines
if ($lines -le 1) { Write-Host "No pQTL candidate molecular traits. Full download not triggered."; exit 20 }

$Items = @(
  @{Name='QTD000584.all.tsv.gz'; Url='https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/QTS000035/QTD000584/QTD000584.all.tsv.gz'; Declared='698M'},
  @{Name='QTD000584.all.tsv.gz.tbi'; Url='https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/QTS000035/QTD000584/QTD000584.all.tsv.gz.tbi'; Declared='1.2M'},
  @{Name='QTD000584.lbf_variable.txt.gz'; Url='https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/susie/QTS000035/QTD000584/QTD000584.lbf_variable.txt.gz'; Declared='438M'}
)
function Get-ResumeFile([string]$Url,[string]$Dest) {
  if (Test-Path $Dest) { Write-Host "EXISTS $Dest"; return }
  $Part="$Dest.part"
  & curl.exe -L --fail --retry 10 --retry-delay 3 --retry-all-errors -C - -o $Part $Url
  if($LASTEXITCODE-ne 0){throw "curl failed: $Url"}
  Move-Item -Force $Part $Dest
}
$Rows=@()
foreach($it in $Items){
  $dest=Join-Path $Data $it.Name
  if($it.Name -in @('QTD000584.all.tsv.gz','QTD000584.lbf_variable.txt.gz')){
    $Fetcher=Join-Path $Root 'analysis\r6a3a\00_segmented_fetch.py'
    & python $Fetcher $it.Url $dest --connections 8
    if($LASTEXITCODE-ne 0){throw "segmented download failed: $($it.Url)"}
  } else {
    Get-ResumeFile $it.Url $dest
  }
  $Rows += [pscustomobject]@{file=$it.Name;url=$it.Url;ftp_declared_size=$it.Declared;bytes=(Get-Item $dest).Length;
    md5=(Get-FileHash -Algorithm MD5 $dest).Hash.ToLower();sha256=(Get-FileHash -Algorithm SHA256 $dest).Hash.ToLower();status='PASS'}
}

$chainGz=Join-Path $Ref 'hg19ToHg38.over.chain.gz'
$chain=Join-Path $Ref 'hg19ToHg38.over.chain'
Get-ResumeFile 'https://hgdownload.soe.ucsc.edu/goldenPath/hg19/liftOver/hg19ToHg38.over.chain.gz' $chainGz
if(!(Test-Path $chain)){
  python -c "import gzip,shutil; gzip.open(r'$chainGz','rb').read(1); i=gzip.open(r'$chainGz','rb'); o=open(r'$chain','wb'); shutil.copyfileobj(i,o); i.close(); o.close()"
  if($LASTEXITCODE-ne 0){throw 'chain decompression failed'}
}
$Rows += [pscustomobject]@{file='hg19ToHg38.over.chain';url='https://hgdownload.soe.ucsc.edu/goldenPath/hg19/liftOver/hg19ToHg38.over.chain.gz';
  ftp_declared_size='NA';bytes=(Get-Item $chain).Length;md5=(Get-FileHash -Algorithm MD5 $chain).Hash.ToLower();
  sha256=(Get-FileHash -Algorithm SHA256 $chain).Hash.ToLower();status='PASS'}
$Rows | Export-Csv -Delimiter "`t" -NoTypeInformation -Encoding utf8 (Join-Path $Audit 'R6A3A_Sun2018_full_byte_receipt.tsv')
