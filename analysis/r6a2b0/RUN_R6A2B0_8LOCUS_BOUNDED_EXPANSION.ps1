$ErrorActionPreference="Stop"
$ProjectRoot = if($env:IGAN_PROJECT_ROOT){$env:IGAN_PROJECT_ROOT}else{(Get-Location).Path}
Set-Location $ProjectRoot
$Code=Join-Path $ProjectRoot 'analysis\r6a2b0'
Write-Host "[1/6] Full OneK archive identity + selective 43-member extraction"
python "$Code\01_extract_onek_8locus_members.py"
if($LASTEXITCODE-ne 0){throw "OneK extraction failed"}
Write-Host "[2/6] Build exact 183-combination OneK regional QTL"
python "$Code\02_build_onek_8locus_qtl.py"
if($LASTEXITCODE-ne 0){throw "OneK bounded QTL build failed"}
Write-Host "[3/6] Harmonize combined/EUR/Asian IgAN GWAS across frozen 8 loci"
python "$Code\03_harmonize_igan_8locus_gwas.py"
if($LASTEXITCODE-ne 0){throw "GWAS harmonization failed"}
Write-Host "[4/6] Run <=549 frozen coloc smoke tests"
python "$Code\04_run_r6a2b0_coloc_smoke.py"
if($LASTEXITCODE-ne 0){throw "Python coloc smoke failed"}
Write-Host "[5/6] Official R coloc validation"
$R=(Get-Command Rscript -ErrorAction SilentlyContinue).Source
if(-not $R){ throw "Rscript not found" }
& $R "$Code\05_validate_r6a2b0_with_coloc_R.R"
if($LASTEXITCODE-ne 0){throw "R coloc validation failed"}
Write-Host "[6/6] Machine adjudication"
python "$Code\06_adjudicate_r6a2b0.py"
if($LASTEXITCODE-ne 0){throw "R6A2B0 adjudication failed"}
Write-Host "STOP HERE. Do not batch-build LD or query TenK before reviewing triggers."
Get-Content '.\3_results\04_integration\R6A2B0\R6A2B0_final_machine_adjudication.json'
