$ErrorActionPreference = "Stop"
Set-Location 'H:\SCI2\YR1'
$Code = '.\2_code\06_intake\mg_r5a2b'
New-Item -ItemType Directory -Force -Path $Code | Out-Null

Write-Host "[1/4] Extract chr5 members from already-downloaded OneK1K 10.34GB archive"
python "$Code\01_extract_onek_chr5_archive.py"
if ($LASTEXITCODE -ne 0) { throw "chr5 archive extraction failed" }

Write-Host "[2/4] Build bounded chr5 QTL table"
python "$Code\02_build_chr5_bounded_qtl.py"
if ($LASTEXITCODE -ne 0) { throw "chr5 bounded QTL build failed" }

Write-Host "[3/4] Extract and harmonize the three existing GRCh37 MG GWAS files"
python "$Code\03_extract_harmonize_mg_grch37_chr5.py"
if ($LASTEXITCODE -ne 0) { throw "chr5 GWAS harmonization failed" }

Write-Host "[4/4] Run only the frozen source-significant cell-gene smoke matrix"
python "$Code\04_run_chr5_coloc_smoke.py"
if ($LASTEXITCODE -ne 0) { throw "chr5 coloc smoke failed" }

Write-Host "Completed R5A2B first-layer bounded smoke. Do NOT build LD for all targets."
Write-Host "Inspect: H:\SCI2\YR1\3_results\04_integration\R5A2B\chr5_coloc_abf_smoke_summary.json"
