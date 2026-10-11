param([string]$ProjectRoot='H:\SCI2\YR1')
$ErrorActionPreference='Stop'
$Code=Join-Path $ProjectRoot '2_code\06_intake\r7a1c1'
$Data=Join-Path $ProjectRoot '1_data\scrna\PBC\HRA008003\paper_supplements'
$Out=Join-Path $ProjectRoot '3_results\00_audit\R7A1C1B0_paper_supplement'
New-Item -ItemType Directory -Force -Path $Data,$Out | Out-Null

$files=@(
  @{
    name='41467_2024_53104_MOESM3_ESM.xlsx';
    url='https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-024-53104-9/MediaObjects/41467_2024_53104_MOESM3_ESM.xlsx';
    bytes=2585688;
    sha256='fc42c213d4a3b6a029fbb51c7f4806a6ae9101f764510a20df3633d81140bd8d'
  },
  @{
    name='41467_2024_53104_MOESM5_ESM.xlsx';
    url='https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-024-53104-9/MediaObjects/41467_2024_53104_MOESM5_ESM.xlsx';
    bytes=16954380;
    sha256='23ca09f165508f92fde22c52e3f0561d02852247a60a0e820c51f8ea56fb00a1'
  }
)
foreach($f in $files){
  $dest=Join-Path $Data $f.name
  $validExisting=(Test-Path -LiteralPath $dest) -and
    ((Get-Item -LiteralPath $dest).Length -eq [int64]$f.bytes) -and
    ((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() -eq $f.sha256)
  if(!$validExisting){
    & curl.exe -L --fail --retry 5 --retry-delay 3 -o $dest $f.url
    if($LASTEXITCODE-ne 0){throw "PMC supplement download failed: $($f.url)"}
  }
  $observedBytes=(Get-Item -LiteralPath $dest).Length
  $observedSha=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
  if($observedBytes -ne [int64]$f.bytes -or $observedSha -ne $f.sha256){
    throw "Supplement byte/SHA gate failed: $dest"
  }
  $signature=[IO.File]::ReadAllBytes($dest)[0..3]
  if($signature[0] -ne 0x50 -or $signature[1] -ne 0x4b -or $signature[2] -ne 0x03 -or $signature[3] -ne 0x04){
    throw "Supplement is not an XLSX ZIP container: $dest"
  }
  python (Join-Path $Code '09_audit_public_PBC_supplement_xlsx.py') --xlsx $dest --outdir $Out
  if($LASTEXITCODE-ne 0){throw "Supplement audit failed: $dest"}
}
Write-Host 'LIGHTWEIGHT_SUPPLEMENT_AUDIT_COMPLETE'
Write-Host 'Important: search hits never auto-pass the frozen donor gate.'
