param(
  [string]$ProjectRoot='H:\SCI2\YR1',
  [switch]$DeleteBamAfterSuccessfulPanel = $true
)
$ErrorActionPreference='Stop'
$env:R7_PROJECT_ROOT=$ProjectRoot
$Code=Join-Path $ProjectRoot '2_code\06_intake\r7a1c1'
$Data=Join-Path $ProjectRoot '1_data\scrna\PBC\HRA008003'
$Out=Join-Path $ProjectRoot '3_results\05_tissue\R7A1C1'
$Audit=Join-Path $ProjectRoot '3_results\00_audit\R7A1C1'
New-Item -ItemType Directory -Force -Path $Data,$Out,$Audit | Out-Null

python -c "import pysam" 2>$null
if($LASTEXITCODE-ne 0){ python -m pip install pysam }
if($LASTEXITCODE-ne 0){ throw 'pysam install/import failed' }

$runs=@('HRR1849459','HRR1849460','HRR1849461','HRR1849462','HRR1849463')
$base='https://download.cncb.ac.cn/gsa-human/HRA008003'

function Resolve-HraUrl([string]$run){
  $candidates=@(
    "$base/$run.bam",
    "$base/$run/$run.bam"
  )
  foreach($u in $candidates){
    & curl.exe -L -sS --fail --range 0-0 -o NUL $u
    if($LASTEXITCODE -eq 0){ return $u }
  }
  # Fallback: inspect official run page HTML for a BAM URL/path.
  $page="https://ngdc.cncb.ac.cn/gsa-human/browse/runDetail/$run"
  $tmp=Join-Path $Audit "$run.runDetail.html"
  & curl.exe -L -sS --fail -o $tmp $page
  if($LASTEXITCODE -eq 0){
    $html=Get-Content -LiteralPath $tmp -Raw
    $m=[regex]::Match($html,'https?://[^"''<>\s]+?'+[regex]::Escape($run)+'\.bam')
    if($m.Success){return $m.Value}
  }
  throw "Cannot resolve direct BAM URL for $run. Official page: $page ; study root: $base"
}

$receipts=@()
foreach($run in $runs){
  $sum=Join-Path $Out "$run`_target_panel_summary.json"
  if(Test-Path $sum){
    Write-Host "SUMMARY_EXISTS $run"
    continue
  }
  $url=Resolve-HraUrl $run
  $bam=Join-Path $Data "$run.bam"
  $part="$bam.part"
  if(!(Test-Path $bam)){
    Write-Host "DOWNLOAD $run $url"
    & curl.exe -L --fail --retry 20 --retry-delay 5 --retry-all-errors -C - -o $part $url
    if($LASTEXITCODE-ne 0){throw "download failed $run"}
    Move-Item -Force $part $bam
  }
  $sha=(Get-FileHash -Algorithm SHA256 $bam).Hash.ToLower()
  $bytes=(Get-Item $bam).Length
  Write-Host "ANALYZE $run bytes=$bytes sha256=$sha"
  python (Join-Path $Code '02_hra_bam_target_panel.py') --bam $bam --run $run --outdir $Out
  if($LASTEXITCODE-ne 0){throw "target panel failed $run"}
  $receipts += [pscustomobject]@{run=$run;url=$url;bytes=$bytes;sha256=$sha;status='PASS_TARGET_PANEL'}
  if($DeleteBamAfterSuccessfulPanel){
    Remove-Item -LiteralPath $bam -Force
    Write-Host "DELETED_LOCAL_BAM_AFTER_SUCCESS $run"
  }
}
$receipts | Export-Csv -Delimiter "`t" -NoTypeInformation -Encoding utf8 (Join-Path $Audit 'R7A1C1_HRA008003_receipts.tsv')
python (Join-Path $Code '03_adjudicate_HRA008003_liver_gate.py') --summary-dir $Out --out (Join-Path $Out 'R7A1C1_liver_final_adjudication.json')
if($LASTEXITCODE-ne 0){throw 'liver adjudication failed'}
Get-Content (Join-Path $Out 'R7A1C1_liver_final_adjudication.json')
