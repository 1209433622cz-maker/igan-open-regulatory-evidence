$ErrorActionPreference="Stop"
$ProjectRoot=if($env:IGAN_PROJECT_ROOT){$env:IGAN_PROJECT_ROOT}else{(Get-Location).Path}
Set-Location $ProjectRoot
$Code='.\2_code\06_intake\igan_r6a2c'
$Need=@(
 '.\3_results\03_qtl\R6A2B0\R6A2B0_OneK1K_8locus_QTL.tsv.gz',
 '.\3_results\01_gwas\R6A2B0\asian_REEP3_GRCh37_1Mb_A1.tsv.gz',
 '.\3_results\01_gwas\R6A2B0\combined_REEP3_GRCh37_1Mb_A1.tsv.gz',
 '.\3_results\01_gwas\R6A2B0\european_REEP3_GRCh37_1Mb_A1.tsv.gz',
 '.\1_data\qtl\OneK1K\plink_merged_980_donors\plink_merged_980_donors.bed',
 '.\1_data\qtl\OneK1K\plink_merged_980_donors\plink_merged_980_donors.bim',
 '.\1_data\qtl\OneK1K\plink_merged_980_donors\plink_merged_980_donors.fam',
 '.\1_data\qtl\OneK1K\updated_covariates_OneK1K_980_donors\CD4_NC_mx_pf50.txt',
 '.\3_results\03_qtl\R5A2A2\cell_sample_lists\CD4_NC.samples.txt'
)
$missing=$Need|Where-Object{!(Test-Path -LiteralPath $_)}
if($missing){$missing|ForEach-Object{Write-Error "MISSING $_"}; throw "R6A2C prerequisites missing"}
Write-Host '[1/4] Exact CD4_NC source LD for REEP3'
python "$Code\01_build_reep3_cd4nc_source_ld.py"; if($LASTEXITCODE-ne 0){throw 'source LD failed'}
Write-Host '[2/4] PF10/PF50 residualized source LD'
python "$Code\02_build_reep3_residual_ld.py"; if($LASTEXITCODE-ne 0){throw 'residual LD failed'}
Write-Host '[3/4] SuSiE + Asian/combined/European signal-specific coloc'
$R=Join-Path $ProjectRoot 'tools\R\R-4.6.1\bin\Rscript.exe'; if(!(Test-Path $R)){$R=Join-Path $ProjectRoot 'tools\R-4.6.1\bin\Rscript.exe'}; if(!(Test-Path $R)){ $cmd=Get-Command Rscript -ErrorAction SilentlyContinue; if($cmd){$R=$cmd.Source}else{throw 'Rscript not found'} }
& $R "$Code\03_run_reep3_multisignal.R"; if($LASTEXITCODE-ne 0){throw 'multisignal R failed'}
Write-Host '[4/4] Frozen adjudication'
python "$Code\04_adjudicate_reep3.py"; if($LASTEXITCODE-ne 0){throw 'adjudication failed'}
Write-Host 'STOP. TenK10K is NOT queried automatically.'
Get-Content '.\3_results\04_integration\R6A2C\R6A2C_final_adjudication.json'
