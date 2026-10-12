param([string]$ProjectRoot='H:\SCI2\YR1')
$ErrorActionPreference='Stop'
$Code=Join-Path $ProjectRoot '2_code\06_intake\r7a1c1'
$Data=Join-Path $ProjectRoot '1_data\scrna\PBC\HRA008003\paper_supplements'
$Out=Join-Path $ProjectRoot '3_results\00_audit\R7A1C1B0_paper_supplement'
New-Item -ItemType Directory -Force -Path $Data,$Out | Out-Null

$files=@(
  @{
    name='41467_2024_53104_MOESM3_ESM.xlsx';
    url='https://pmc.ncbi.nlm.nih.gov/articles/instance/11458754/bin/41467_2024_53104_MOESM3_ESM.xlsx'
  },
  @{
    name='41467_2024_53104_MOESM5_ESM.xlsx';
    url='https://pmc.ncbi.nlm.nih.gov/articles/instance/11458754/bin/41467_2024_53104_MOESM5_ESM.xlsx'
  }
)
foreach($f in $files){
  $dest=Join-Path $Data $f.name
  if(!(Test-Path $dest)){
    & curl.exe -L --fail --retry 5 --retry-delay 3 -o $dest $f.url
    if($LASTEXITCODE-ne 0){throw "PMC supplement download failed: $($f.url)"}
  }
  python (Join-Path $Code '09_audit_public_PBC_supplement_xlsx.py') --xlsx $dest --outdir $Out
  if($LASTEXITCODE-ne 0){throw "Supplement audit failed: $dest"}
}
Write-Host 'LIGHTWEIGHT_SUPPLEMENT_AUDIT_COMPLETE'
Write-Host 'Important: search hits never auto-pass the frozen donor gate.'
