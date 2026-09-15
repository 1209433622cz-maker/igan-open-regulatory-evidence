$ErrorActionPreference='Stop'
$Root=if($env:R7_PROJECT_ROOT){$env:R7_PROJECT_ROOT}else{'H:\SCI2\YR1'}
$env:R7_PROJECT_ROOT=$Root
Set-Location $Root
$Code='.\2_code\06_intake\r7a1b'
Write-Host '[1/10] Full OneK archive identity + frozen chr1 member extraction'
python "$Code\01_extract_onek_chr1_frozen_members.py";if($LASTEXITCODE-ne 0){throw 'OneK extraction failed'}
Write-Host '[2/10] Build nine frozen QTL inputs'
python "$Code\02_build_pbc_control_qtl.py";if($LASTEXITCODE-ne 0){throw 'QTL build failed'}
Write-Host '[3/10] Harmonize PBC GWAS to OneK BIM A1'
python "$Code\03_harmonize_pbc_gwas_to_onek.py";if($LASTEXITCODE-ne 0){throw 'GWAS harmonization failed'}
Write-Host '[4/10] Run <=9 ABF smoke tests'
python "$Code\04_run_pbc_coloc_smoke.py";if($LASTEXITCODE-ne 0){throw 'ABF smoke failed'}
Write-Host '[5/10] Official R coloc validation'
$R=if($env:R7_RSCRIPT){$env:R7_RSCRIPT}else{Join-Path $Root 'tools\R\R-4.6.1\bin\Rscript.exe'}
if(!(Test-Path $R)){$R=(Get-Command Rscript -ErrorAction SilentlyContinue).Source}
if(-not $R){throw 'Rscript not found'}
& $R "$Code\05_validate_pbc_coloc_R.R";if($LASTEXITCODE-ne 0){throw 'R validation failed'}
python "$Code\05b_compare_python_R_coloc.py";if($LASTEXITCODE-ne 0){throw 'Python/R coloc posterior mismatch'}

Write-Host '[6/10] Fetch ONLY triggered GJOKA disease summary/LD members'
python "$Code\06_fetch_trigger_gjoka_members.py";if($LASTEXITCODE-ne 0){throw 'GJOKA target fetch failed'}

$tr=Import-Csv '.\3_results\04_integration\R7A1B\R7A1B_multisignal_triggers.tsv' -Delimiter "`t"
if($tr.Count -eq 0){throw 'No multisignal triggers; adjudicate as gate failure rather than expanding targets'}
Write-Host '[7/10] OneK source LD for triggered combinations only'
foreach($x in $tr){
  python "$Code\07_build_onek_trigger_source_ld.py" --gene $x.gene --cell $x.cell_type
  if($LASTEXITCODE-ne 0){throw "source LD failed $($x.gene) $($x.cell_type)"}
}
Write-Host '[8/10] PF10/PF50 covariate-residual source LD'
python "$Code\08_build_onek_residual_ld.py";if($LASTEXITCODE-ne 0){throw 'residual LD failed'}
python "$Code\08b_export_residual_ld_for_R.py";if($LASTEXITCODE-ne 0){throw 'LD export failed'}
Write-Host '[9/10] Two-sided disease + QTL SuSiE / coloc.susie'
& $R "$Code\09_run_pbc_multisignal_coloc.R";if($LASTEXITCODE-ne 0){throw 'multisignal failed'}
Write-Host '[10/10] Gene-level frozen adjudication'
python "$Code\10_adjudicate_r7a1b.py";if($LASTEXITCODE-ne 0){throw 'adjudication failed'}
Get-Content '.\3_results\04_integration\R7A1B\R7A1B_final_adjudication.json'
