param(
  [string]$ProjectRoot = 'H:\SCI2\YR1',
  [int]$AriaConnections = 16,
  [int]$SamtoolsThreads = 4,
  [switch]$DeleteBamAfterSuccessfulPanel = $true
)

$ErrorActionPreference = 'Stop'
$env:R7_PROJECT_ROOT = $ProjectRoot
$Code = Join-Path $ProjectRoot '2_code\06_intake\r7a1c1'
$ManifestPath = Join-Path $ProjectRoot '1_data\scrna\PBC\HRA008003\manifests\HRA008003_PBC_liver_primary_run_manifest_v2.tsv'
$Data = Join-Path $ProjectRoot '1_data\scrna\PBC\HRA008003\bam'
$Out = Join-Path $ProjectRoot '3_results\05_tissue\R7A1C1'
$Audit = Join-Path $ProjectRoot '3_results\00_audit\R7A1C1'
$Work = Join-Path $ProjectRoot '3_results\05_tissue\R7A1C1_work'
$Aria = Join-Path $ProjectRoot '1_data\software\aria2\aria2-1.37.0\aria2-1.37.0-win-64bit-build1\aria2c.exe'
New-Item -ItemType Directory -Force -Path $Data,$Out,$Audit,$Work | Out-Null

foreach($required in @(
  $ManifestPath,
  $Aria,
  (Join-Path $Code '00_hash_file_dual.py'),
  (Join-Path $Code '02_hra_bam_target_panel_v2.py'),
  (Join-Path $Code '03_adjudicate_HRA008003_liver_gate_v2.py'),
  (Join-Path $Code '07_validate_HRA008003_manifest.py'),
  (Join-Path $Code '08_check_HRA008003_bam_schema.py')
)) {
  if(!(Test-Path -LiteralPath $required)) { throw "Missing required file: $required" }
}
# R7A1C1B0 fail-closed manifest audit (no biological threshold changed).
$ManifestAudit = Join-Path $Audit 'R7A1C1B0_manifest_preflight.json'
python (Join-Path $Code '07_validate_HRA008003_manifest.py') --manifest $ManifestPath --out $ManifestAudit
if($LASTEXITCODE -ne 0) { throw 'HRA manifest preflight failed' }

if($AriaConnections -lt 1 -or $AriaConnections -gt 16) { throw 'AriaConnections must be 1-16' }
if($SamtoolsThreads -lt 1 -or $SamtoolsThreads -gt 16) { throw 'SamtoolsThreads must be 1-16' }

& wsl.exe -d Ubuntu-22.04 -- bash -lc "command -v samtools >/dev/null && python3 -c 'import pysam; print(pysam.__version__)'"
if($LASTEXITCODE -ne 0) {
  throw 'WSL Ubuntu-22.04 requires samtools and pysam. See INSTALL_R7A1C1_DEPENDENCIES.md.'
}

function Convert-ToWslPath([string]$WindowsPath) {
  $full = [IO.Path]::GetFullPath($WindowsPath)
  if($full -notmatch '^[A-Za-z]:\\') { throw "Expected an absolute Windows drive path: $full" }
  $driveLetter = $full.Substring(0,1).ToLowerInvariant()
  $relative = $full.Substring(3).Replace('\','/')
  return "/mnt/$driveLetter/$relative"
}

$manifest = Import-Csv -LiteralPath $ManifestPath -Delimiter "`t"
$expectedRuns = @('HRR1849459','HRR1849460','HRR1849461','HRR1849462','HRR1849463')
if($manifest.Count -ne 5 -or (Compare-Object $expectedRuns ($manifest.run_accession | Sort-Object))) {
  throw 'Manifest must contain the exact five frozen PBC liver runs.'
}

$receiptPath = Join-Path $Audit 'R7A1C1_HRA008003_receipts_v2.tsv'
$receipts = @()
if(Test-Path -LiteralPath $receiptPath) {
  $receipts = @(Import-Csv -LiteralPath $receiptPath -Delimiter "`t")
}

foreach($item in $manifest) {
  $run = $item.run_accession
  $summaryPath = Join-Path $Out "$run`_target_panel_summary.json"
  if(Test-Path -LiteralPath $summaryPath) {
    $existing = Get-Content -LiteralPath $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if($existing.schema_version -eq 'CMM_R7A1C1_TARGET_PANEL_2.0' -and $existing.technical_QC -eq 'PASS') {
      Write-Host "VERIFIED_V2_SUMMARY_EXISTS $run"
      if(!($receipts | Where-Object {$_.run -eq $run})) {
        $receipts += [pscustomobject]@{
          run=$run; url=$item.direct_url; bytes=$existing.bam_bytes; official_md5=$item.official_md5
          observed_md5='RECORDED_IN_PRIOR_VALIDATED_RUN'; sha256=$existing.bam_sha256
          status='PASS_TARGET_PANEL_V2_REUSED'; bam_deleted='UNKNOWN_OR_PRIOR_RUN'
        }
      }
      continue
    }
    throw "Existing summary is legacy or failed QC: $summaryPath"
  }

  $bam = Join-Path $Data "$run.bam"
  $part = "$bam.part"
  $expectedBytes = [int64]$item.expected_bytes
  $drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($ProjectRoot).TrimEnd(':','\'))
  if($drive.Free -lt ($expectedBytes + 15GB)) {
    throw "Insufficient free space for $run; require BAM size plus 15 GiB work margin."
  }

  if(!(Test-Path -LiteralPath $bam)) {
    Write-Host "DOWNLOAD $run expected_bytes=$expectedBytes"
    & $Aria `
      --continue=true `
      --max-connection-per-server=$AriaConnections `
      --split=$AriaConnections `
      --min-split-size=4M `
      --piece-length=4M `
      --file-allocation=none `
      --auto-file-renaming=false `
      --allow-overwrite=false `
      --max-tries=0 `
      --retry-wait=5 `
      --timeout=60 `
      --summary-interval=30 `
      --dir=$Data `
      --out="$run.bam.part" `
      $item.direct_url
    if($LASTEXITCODE -ne 0) { throw "aria2 download failed: $run" }
    if((Get-Item -LiteralPath $part).Length -ne $expectedBytes) {
      throw "Downloaded byte mismatch for $run"
    }
    Move-Item -LiteralPath $part -Destination $bam -Force
  }
  if((Get-Item -LiteralPath $bam).Length -ne $expectedBytes) {
    throw "Existing BAM byte mismatch for $run"
  }

  $hashPath = Join-Path $Audit "$run.hashes.json"
  python (Join-Path $Code '00_hash_file_dual.py') $bam --out $hashPath
  if($LASTEXITCODE -ne 0) { throw "hashing failed: $run" }
  $hashes = Get-Content -LiteralPath $hashPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if($hashes.bytes -ne $expectedBytes -or $hashes.md5 -ne $item.official_md5) {
    throw "Official byte/MD5 gate failed for $run"
  }

  # Full-file structural integrity check after provider byte+MD5 verification.
  $bamWslQC = Convert-ToWslPath $bam
  & wsl.exe -d Ubuntu-22.04 -- samtools quickcheck -v $bamWslQC
  if($LASTEXITCODE -ne 0) { throw "samtools quickcheck failed: $run" }

  # Spot-audit required Cell Ranger BAM tags before the expensive full molecule scan.
  $schemaScriptWsl = Convert-ToWslPath (Join-Path $Code '08_check_HRA008003_bam_schema.py')
  $schemaOut = Join-Path $Audit "$run.bam_schema_preflight.json"
  $schemaOutWsl = Convert-ToWslPath $schemaOut
  & wsl.exe -d Ubuntu-22.04 -- python3 $schemaScriptWsl --bam $bamWslQC --run $run --out $schemaOutWsl
  if($LASTEXITCODE -ne 0) { throw "BAM schema preflight failed: $run" }

  $scriptWsl = Convert-ToWslPath (Join-Path $Code '02_hra_bam_target_panel_v2.py')
  $bamWsl = Convert-ToWslPath $bam
  $outWsl = Convert-ToWslPath $Out
  $workWsl = Convert-ToWslPath $Work
  Write-Host "ANALYZE $run sha256=$($hashes.sha256)"
  & wsl.exe -d Ubuntu-22.04 -- python3 $scriptWsl `
    --bam $bamWsl --run $run --outdir $outWsl --workdir $workWsl `
    --samtools-threads $SamtoolsThreads --expected-cells 6000
  if($LASTEXITCODE -ne 0) { throw "target panel v2 failed: $run" }
  $summary = Get-Content -LiteralPath $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if($summary.schema_version -ne 'CMM_R7A1C1_TARGET_PANEL_2.0' -or $summary.technical_QC -ne 'PASS') {
    throw "v2 summary gate failed: $run"
  }

  $receipts = @($receipts | Where-Object {$_.run -ne $run})
  $receipts += [pscustomobject]@{
    run=$run; url=$item.direct_url; bytes=$hashes.bytes; official_md5=$item.official_md5
    observed_md5=$hashes.md5; sha256=$hashes.sha256
    status='PASS_TARGET_PANEL_V2'; bam_deleted=[bool]$DeleteBamAfterSuccessfulPanel
  }
  $receipts | Sort-Object run | Export-Csv -LiteralPath $receiptPath -Delimiter "`t" -NoTypeInformation -Encoding utf8

  if($DeleteBamAfterSuccessfulPanel) {
    $resolvedBam = [IO.Path]::GetFullPath($bam)
    $resolvedData = [IO.Path]::GetFullPath($Data).TrimEnd('\') + '\'
    if(!$resolvedBam.StartsWith($resolvedData,[StringComparison]::OrdinalIgnoreCase)) {
      throw "Refusing to delete BAM outside intended data directory: $resolvedBam"
    }
    Remove-Item -LiteralPath $resolvedBam -Force
    Write-Host "DELETED_LOCAL_BAM_AFTER_VALIDATED_V2_PANEL $run"
  }
}

$adjudicateWsl = Convert-ToWslPath (Join-Path $Code '03_adjudicate_HRA008003_liver_gate_v2.py'),
  (Join-Path $Code '07_validate_HRA008003_manifest.py'),
  (Join-Path $Code '08_check_HRA008003_bam_schema.py')
$outWsl = Convert-ToWslPath $Out
$finalPath = Join-Path $Out 'R7A1C1_liver_final_adjudication_v2.json'
$finalWsl = Convert-ToWslPath $finalPath
& wsl.exe -d Ubuntu-22.04 -- python3 $adjudicateWsl --summary-dir $outWsl --out $finalWsl
if($LASTEXITCODE -ne 0) { throw 'liver adjudication v2 failed' }
Get-Content -LiteralPath $finalPath -Raw -Encoding UTF8
