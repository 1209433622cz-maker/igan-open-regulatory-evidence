$ErrorActionPreference="Stop"
Set-Location 'H:\SCI2\YR1'
$Code='.\2_code\06_intake\igan_r6a2a'
$Rscript='H:\SCI2\YR1\0_admin\tooling\R\R-4.6.1\bin\Rscript.exe'
Write-Host "[1/5] Extract frozen OneK1K benchmark chromosome/cell members"
python "$Code\01_extract_onek_benchmark_members.py"
if($LASTEXITCODE-ne 0){throw "extract failed"}
Write-Host "[2/5] Build frozen OneK1K benchmark QTL"
python "$Code\02_build_onek_benchmark_qtl.py"
if($LASTEXITCODE-ne 0){throw "QTL build failed"}
Write-Host "[3/5] Harmonize combined/EUR/Asian IgAN GWAS to OneK A1"
python "$Code\03_harmonize_igan_benchmark_gwas.py"
if($LASTEXITCODE-ne 0){throw "GWAS harmonization failed"}
Write-Host "[4/5] Run Python ABF smoke"
python "$Code\04_run_r6a2a_coloc_smoke.py"
if($LASTEXITCODE-ne 0){throw "coloc smoke failed"}
Write-Host "[5/5] Official R coloc validation"
& $Rscript "$Code\05_validate_r6a2a_with_coloc_R.R"
if($LASTEXITCODE-ne 0){throw "R validation failed"}
Write-Host "STOP: inspect R6A2A_sourceLD_triggers.tsv. Do not build LD for non-trigger combinations."
Get-Content '.\3_results\04_integration\R6A2A\R6A2A_coloc_smoke_summary.json'
