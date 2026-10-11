param(
  [string]$Root = 'H:\SCI2\YR1',
  [int]$Workers = 8,
  [int]$ChunkMiB = 8
)
$ErrorActionPreference = 'Stop'
$Python = 'python'
$Rscript = 'C:\Program Files\R\R-4.6.1\bin\Rscript.exe'
$Intake = Join-Path $Root '2_code\06_intake\tenk10k_il12rb2\download_extract_tenk10k_three_cells_resume.py'
$Analysis = Join-Path $Root '2_code\07_analysis\R4A12FG6'
$QtlOut = Join-Path $Root '1_data\qtl\eqtl\tenk10k\derived\IL12RB2_full\three_cells'
$Cache = Join-Path $Root '1_data\qtl\eqtl\tenk10k\derived\IL12RB2_full\three_cells_cache'
$Smoke = Join-Path $Root '3_results\01_smoke\R4A12FG6_IL12RB2_three_cells'
$LdOut = Join-Path $Root '3_results\02_coloc\ld_finemap\R4A12FG6_external_EUR503_full'
$SourceCs = Join-Path $Root '1_data\qtl\eqtl\tenk10k\derived\IL12RB2\TenK10K_IL12RB2_susie_credible_members.tsv'
$Bfile = Join-Path $Root '1_data\reference\ld\1000G_Phase3_v5a_EUR503\legacy_chr1_IL12RB2\1000G_Phase3_v5a_EUR503_IL12RB2_GRCh37'

& $Python $Intake --out-dir $QtlOut --cache-dir $Cache --workers $Workers --chunk-mib $ChunkMiB --retries 6
if ($LASTEXITCODE -ne 0) { throw 'Three-cell intake failed closed.' }

New-Item -ItemType Directory -Force -Path $Smoke,$LdOut | Out-Null
$NkHarmonized = Join-Path $Root '3_results\01_smoke\R4A12FG4_IL12RB2\R13_M13_SYSTSLCE_x_TenK10K_NK_IL12RB2_harmonized.tsv'
& $Python (Join-Path $Analysis 'build_full_EUR503_LD_for_current_891.py') --harmonized $NkHarmonized --bfile-prefix $Bfile --source-cs $SourceCs --out-dir $LdOut
if ($LASTEXITCODE -ne 0) { throw 'Full EUR503 gate computation failed.' }

foreach ($Cell in @('CD8_TEM','CD4_CTL','CD4_TCM')) {
  $Qtl = Join-Path $QtlOut "${Cell}_IL12RB2_full_variant_eqtl.tsv"
  foreach ($Release in @('R12','R13')) {
    $Gwas = Join-Path $Root "1_data\gwas\outcome\ssc_finngen_r12_r13\regional\${Release}\finngen_${Release}_M13_SYSTSLCE_IL12RB2_chr1_66840524_67840524.tsv"
    $H = Join-Path $Smoke "${Release}_${Cell}_IL12RB2_harmonized.tsv"
    $J = Join-Path $Smoke "${Release}_${Cell}_harmonization_gate.json"
    & $Python (Join-Path $Analysis 'harmonize_three_cell_il12rb2.py') --qtl $Qtl --gwas $Gwas --source-cs $SourceCs --cell $Cell --release $Release --out-tsv $H --out-json $J
    if ($LASTEXITCODE -ne 0) { throw "Harmonization failed: $Release $Cell" }
    if ($Release -eq 'R12') { $Cases=854; $Controls=484260 } else { $Cases=883; $Controls=483310 }
    & $Rscript (Join-Path $Analysis 'run_three_cell_coloc_abf.R') $H $Release $Cell $Cases $Controls (Join-Path $Smoke "${Release}_${Cell}_coloc_abf.tsv")
    if ($LASTEXITCODE -ne 0) { throw "Single-causal diagnostic failed: $Release $Cell" }
  }
}

$Gate = Get-Content -LiteralPath (Join-Path $LdOut 'R4A12FG6_full_EUR503_LD_gate.json') -Raw | ConvertFrom-Json
if (-not $Gate.pass) {
  Write-Host 'R4A12FG6 complete: external-LD multi-signal gate failed by frozen rules; formal multi-signal analysis was not run.'
} else {
  Write-Host 'External-LD gate passed. A separately frozen multi-signal protocol is required before running formal analysis.'
}
