# R7A2A1 transport-hardened runner
# Derived from the frozen 2026-09-28 runner.
# CHANGE SCOPE: transfer reliability only.
# NO changes to manifest, checksums, BAM schema gate, target-panel code, lineage gates, biological thresholds, comparison statistics, or deletion gate.
# Default aria2 concurrency lowered to 2; process-level restart loop added; after 3 failed outer attempts concurrency falls to 1.

param(
  [string]$ProjectRoot = 'H:\SCI2\YR1',
  [int]$AriaConnections = 2,
  [int]$AriaOuterAttempts = 50,
  [int]$AriaOuterRetryWaitSeconds = 30,
  [int]$SamtoolsThreads = 4,
  [switch]$DeleteBamAfterSuccessfulPanel = $true,
  [switch]$PreflightOnly
)

$ErrorActionPreference = 'Stop'
$env:R7_PROJECT_ROOT = $ProjectRoot
$Code = Join-Path $ProjectRoot '2_code\06_intake\r7a2'
$FrozenCode = Join-Path $ProjectRoot '2_code\06_intake\r7a1c1'
$ManifestPath = Join-Path $ProjectRoot '1_data\scrna\PBC\HRA008003\manifests\HRA008003_control_liver_primary_run_manifest_v1.tsv'
$Data = Join-Path $ProjectRoot '1_data\scrna\PBC\HRA008003\bam_control'
$Out = Join-Path $ProjectRoot '3_results\05_tissue\R7A2A1_control'
$PbcOut = Join-Path $ProjectRoot '3_results\05_tissue\R7A1C1'
$Audit = Join-Path $ProjectRoot '3_results\00_audit\R7A2A1'
$Work = Join-Path $ProjectRoot '3_results\05_tissue\R7A2A1_work'
$Aria = Join-Path $ProjectRoot '1_data\software\aria2\aria2-1.37.0\aria2-1.37.0-win-64bit-build1\aria2c.exe'
New-Item -ItemType Directory -Force -Path $Data,$Out,$Audit,$Work | Out-Null

foreach($required in @(
  $ManifestPath,
  $Aria,
  (Join-Path $Code '01_validate_HRA008003_control_manifest.py'),
  (Join-Path $Code '02_compare_PBC_control_target_panel.py'),
  (Join-Path $FrozenCode '00_hash_file_dual.py'),
  (Join-Path $FrozenCode '02_hra_bam_target_panel_v2.py'),
  (Join-Path $FrozenCode '08_check_HRA008003_bam_schema_v1_2.py'),
  (Join-Path $FrozenCode '11_validate_HRA008003_resume_state.py')
)) {
  if(!(Test-Path -LiteralPath $required)) { throw "Missing required file: $required" }
}

if($AriaConnections -lt 1 -or $AriaConnections -gt 16) { throw 'AriaConnections must be 1-16' }
if($AriaOuterAttempts -lt 1 -or $AriaOuterAttempts -gt 500) { throw 'AriaOuterAttempts must be 1-500' }
if($AriaOuterRetryWaitSeconds -lt 1 -or $AriaOuterRetryWaitSeconds -gt 3600) { throw 'AriaOuterRetryWaitSeconds must be 1-3600' }
if($SamtoolsThreads -lt 1 -or $SamtoolsThreads -gt 16) { throw 'SamtoolsThreads must be 1-16' }

$ManifestAudit = Join-Path $Audit 'R7A2A0_control_manifest_preflight.json'
python (Join-Path $Code '01_validate_HRA008003_control_manifest.py') --manifest $ManifestPath --out $ManifestAudit
if($LASTEXITCODE -ne 0) { throw 'Control-liver manifest preflight failed' }

& wsl.exe -d Ubuntu-22.04 -- bash -lc "command -v samtools >/dev/null && python3 -c 'import pysam; print(pysam.__version__)'"
if($LASTEXITCODE -ne 0) { throw 'WSL Ubuntu-22.04 requires samtools and pysam.' }

function Convert-ToWslPath([string]$WindowsPath) {
  $full = [IO.Path]::GetFullPath($WindowsPath)
  if($full -notmatch '^[A-Za-z]:\\') { throw "Expected an absolute Windows drive path: $full" }
  $driveLetter = $full.Substring(0,1).ToLowerInvariant()
  $relative = $full.Substring(3).Replace('\','/')
  return "/mnt/$driveLetter/$relative"
}

$manifest = @(Import-Csv -LiteralPath $ManifestPath -Delimiter "`t")
$expectedRuns = @('HRR1849454','HRR1849455','HRR1849456','HRR1849457','HRR1849458')
if($manifest.Count -ne 5 -or (Compare-Object $expectedRuns ($manifest.run_accession | Sort-Object))) {
  throw 'Manifest must contain the exact five frozen control-liver runs.'
}

if($PreflightOnly) {
  $targetWsl = Convert-ToWslPath (Join-Path $FrozenCode '02_hra_bam_target_panel_v2.py')
  $schemaWsl = Convert-ToWslPath (Join-Path $FrozenCode '08_check_HRA008003_bam_schema_v1_2.py')
  & wsl.exe -d Ubuntu-22.04 -- bash -lc "test -f '$targetWsl' && test -f '$schemaWsl'"
  if($LASTEXITCODE -ne 0) { throw 'WSL script visibility preflight failed' }
  [pscustomobject]@{
    status='PASS_R7A2A0_PREFLIGHT_ONLY'
    manifest_runs=$manifest.Count
    total_expected_bytes=($manifest | Measure-Object -Property expected_bytes -Sum).Sum
    planned_analysis='EXACT_5_PBC_VS_5_CONTROL_MARKER_PANEL'
    biological_threshold_changed=$false
  } | ConvertTo-Json -Depth 3
  exit 0
}

$receiptPath = Join-Path $Audit 'R7A2A1_HRA008003_control_receipts.tsv'
$receipts = @()
if(Test-Path -LiteralPath $receiptPath) {
  $receipts = @(Import-Csv -LiteralPath $receiptPath -Delimiter "`t")
}

foreach($item in $manifest) {
  $run = $item.run_accession
  $summaryPath = Join-Path $Out "$run`_target_panel_summary.json"
  if(Test-Path -LiteralPath $summaryPath) {
    if(!(Test-Path -LiteralPath $receiptPath)) { throw "Existing summary has no receipt table: $summaryPath" }
    $resumeOut = Join-Path $Audit "$run.resume_validation.json"
    & python (Join-Path $FrozenCode '11_validate_HRA008003_resume_state.py') `
      --summary $summaryPath --receipts $receiptPath --run $run `
      --expected-bytes $item.expected_bytes --official-md5 $item.official_md5 --out $resumeOut
    if($LASTEXITCODE -eq 0) {
      Write-Host "VERIFIED_CONTROL_SUMMARY_AND_RECEIPT_EXIST $run"
      continue
    }
    throw "Existing summary lacks a matching validated receipt: $summaryPath"
  }

  $bam = Join-Path $Data "$run.bam"
  $part = "$bam.part"
  $expectedBytes = [int64]$item.expected_bytes
  $driveName = [IO.Path]::GetPathRoot($ProjectRoot).TrimEnd(':','\')
  $drive = Get-PSDrive -Name $driveName
  if($drive.Free -lt ($expectedBytes + 15GB)) {
    throw "Insufficient free space for $run; require BAM size plus 15 GiB work margin."
  }

  if(!(Test-Path -LiteralPath $bam)) {
    Write-Host "DOWNLOAD_CONTROL $run expected_bytes=$expectedBytes"
    $downloadComplete = $false
    for($outerAttempt = 1; $outerAttempt -le $AriaOuterAttempts; $outerAttempt++) {
      # Preserve the same .part target on every restart. aria2 --continue=true resumes it.
      # After repeated process-level failures, reduce connection pressure on CNCB.
      $effectiveConnections = $AriaConnections
      if($outerAttempt -ge 4) { $effectiveConnections = [Math]::Min($effectiveConnections, 1) }

      $existingBytes = 0
      if(Test-Path -LiteralPath $part) { $existingBytes = (Get-Item -LiteralPath $part).Length }
      $pct = if($expectedBytes -gt 0) { [Math]::Round(100.0 * $existingBytes / $expectedBytes, 2) } else { 0 }
      Write-Host "ARIA2_OUTER_ATTEMPT $outerAttempt/$AriaOuterAttempts run=$run connections=$effectiveConnections existing_bytes=$existingBytes pct=$pct"

      & $Aria `
        --continue=true `
        --max-connection-per-server=$effectiveConnections `
        --split=$effectiveConnections `
        --min-split-size=16M `
        --piece-length=4M `
        --file-allocation=none `
        --auto-file-renaming=false `
        --allow-overwrite=false `
        --max-tries=0 `
        --retry-wait=10 `
        --connect-timeout=60 `
        --timeout=120 `
        --summary-interval=30 `
        --dir=$Data `
        --out="$run.bam.part" `
        $item.direct_url

      $ariaExit = $LASTEXITCODE
      $observedBytes = 0
      if(Test-Path -LiteralPath $part) { $observedBytes = (Get-Item -LiteralPath $part).Length }

      if($ariaExit -eq 0 -and $observedBytes -eq $expectedBytes) {
        $downloadComplete = $true
        Write-Host "ARIA2_DOWNLOAD_COMPLETE $run bytes=$observedBytes outer_attempt=$outerAttempt"
        break
      }

      if($observedBytes -gt $expectedBytes) {
        throw "Downloaded .part exceeds expected byte count for ${run}: observed=$observedBytes expected=$expectedBytes"
      }

      if($outerAttempt -lt $AriaOuterAttempts) {
        Write-Warning "aria2 process ended before byte gate for $run (exit=$ariaExit observed=$observedBytes expected=$expectedBytes). Retaining .part; restart in $AriaOuterRetryWaitSeconds sec."
        Start-Sleep -Seconds $AriaOuterRetryWaitSeconds
      }
    }

    if(!$downloadComplete) {
      $finalBytes = if(Test-Path -LiteralPath $part) { (Get-Item -LiteralPath $part).Length } else { 0 }
      throw "aria2 download did not reach byte gate after $AriaOuterAttempts outer attempts: $run observed=$finalBytes expected=$expectedBytes"
    }
    if((Get-Item -LiteralPath $part).Length -ne $expectedBytes) { throw "Downloaded byte mismatch for $run" }
    Move-Item -LiteralPath $part -Destination $bam -Force
  }
  if((Get-Item -LiteralPath $bam).Length -ne $expectedBytes) { throw "Existing BAM byte mismatch for $run" }

  $hashPath = Join-Path $Audit "$run.hashes.json"
  python (Join-Path $FrozenCode '00_hash_file_dual.py') $bam --out $hashPath
  if($LASTEXITCODE -ne 0) { throw "hashing failed: $run" }
  $hashes = Get-Content -LiteralPath $hashPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if($hashes.bytes -ne $expectedBytes -or $hashes.md5 -ne $item.official_md5) { throw "Official byte/MD5 gate failed for $run" }

  $bamWsl = Convert-ToWslPath $bam
  & wsl.exe -d Ubuntu-22.04 -- samtools quickcheck -v $bamWsl
  if($LASTEXITCODE -ne 0) { throw "samtools quickcheck failed: $run" }

  $schemaScriptWsl = Convert-ToWslPath (Join-Path $FrozenCode '08_check_HRA008003_bam_schema_v1_2.py')
  $schemaOut = Join-Path $Audit "$run.bam_schema_preflight_v1_2.json"
  $schemaOutWsl = Convert-ToWslPath $schemaOut
  & wsl.exe -d Ubuntu-22.04 -- python3 $schemaScriptWsl --bam $bamWsl --run $run --out $schemaOutWsl
  if($LASTEXITCODE -ne 0) { throw "BAM schema preflight failed: $run" }

  $targetWsl = Convert-ToWslPath (Join-Path $FrozenCode '02_hra_bam_target_panel_v2.py')
  $outWsl = Convert-ToWslPath $Out
  $workWsl = Convert-ToWslPath $Work
  Write-Host "ANALYZE_CONTROL $run sha256=$($hashes.sha256)"
  & wsl.exe -d Ubuntu-22.04 -- python3 $targetWsl `
    --bam $bamWsl --run $run --outdir $outWsl --workdir $workWsl `
    --samtools-threads $SamtoolsThreads --expected-cells 6000
  if($LASTEXITCODE -ne 0) { throw "target panel v2 failed: $run" }
  $summary = Get-Content -LiteralPath $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if(
    $summary.schema_version -ne 'CMM_R7A1C1_TARGET_PANEL_2.0' -or
    $summary.technical_QC -ne 'PASS' -or
    $summary.run -ne $run -or
    [int64]$summary.bam_bytes -ne $expectedBytes -or
    $summary.bam_sha256 -ne $hashes.sha256
  ) { throw "Control summary gate failed: $run" }

  $receipts = @($receipts | Where-Object {$_.run -ne $run})
  $receipts += [pscustomobject]@{
    run=$run; url=$item.direct_url; bytes=$hashes.bytes; official_md5=$item.official_md5
    observed_md5=$hashes.md5; sha256=$hashes.sha256
    status='PASS_TARGET_PANEL_V2_CONTROL'; bam_deleted=$false
  }
  $receipts | Sort-Object run | Export-Csv -LiteralPath $receiptPath -Delimiter "`t" -NoTypeInformation -Encoding utf8

  $resumeOut = Join-Path $Audit "$run.resume_validation.json"
  & python (Join-Path $FrozenCode '11_validate_HRA008003_resume_state.py') `
    --summary $summaryPath --receipts $receiptPath --run $run `
    --expected-bytes $item.expected_bytes --official-md5 $item.official_md5 --out $resumeOut
  if($LASTEXITCODE -ne 0) { throw "Control summary/receipt validation failed; BAM retained: $run" }

  if($DeleteBamAfterSuccessfulPanel) {
    $resolvedBam = [IO.Path]::GetFullPath($bam)
    $resolvedData = [IO.Path]::GetFullPath($Data).TrimEnd('\') + '\'
    if(!$resolvedBam.StartsWith($resolvedData,[StringComparison]::OrdinalIgnoreCase)) {
      throw "Refusing to delete BAM outside intended control data directory: $resolvedBam"
    }
    Remove-Item -LiteralPath $resolvedBam -Force
    $receipts = @($receipts | ForEach-Object {
      if($_.run -eq $run) { $_.bam_deleted = $true }
      $_
    })
    $receipts | Sort-Object run | Export-Csv -LiteralPath $receiptPath -Delimiter "`t" -NoTypeInformation -Encoding utf8
    Write-Host "DELETED_CONTROL_BAM_AFTER_VALIDATED_PANEL $run"
  }
}

$comparisonPrefix = Join-Path $Out 'PBC_vs_control_target_panel'
python (Join-Path $Code '02_compare_PBC_control_target_panel.py') `
  --pbc-dir $PbcOut --control-dir $Out --out-prefix $comparisonPrefix
if($LASTEXITCODE -ne 0) { throw 'Exact 5-vs-5 target-panel comparison failed' }
Get-Content -LiteralPath "$comparisonPrefix.json" -Raw -Encoding UTF8
