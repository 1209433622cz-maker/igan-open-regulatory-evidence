$ErrorActionPreference="Stop"
Set-Location 'H:\SCI2\YR1'
python '.\2_code\06_intake\mg_r5a2a4\build_onek_nkr_zcchc2_source_ld.py'
if ($LASTEXITCODE -ne 0) { throw "source-LD build failed" }
Get-Content '.\3_results\04_integration\R5A2A4\NK_R_ZCCHC2_sourceLD\NK_R_ZCCHC2_sourceLD_QC.json'
