[CmdletBinding()]
param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$Rscript = "C:\Program Files\R\R-4.6.1\bin\Rscript.exe",
    [string]$WorkspaceRoot = "H:\SCI2\YR1",
    [switch]$AllowPostGateDiagnostic
)

$ErrorActionPreference = "Stop"
$analysisDir = Join-Path $WorkspaceRoot "2_code\07_analysis\R4A12FG4"
$qtl = Join-Path $WorkspaceRoot "1_data\qtl\eqtl\tenk10k\derived\IL12RB2_full\remote_NK\NK_IL12RB2_full_variant_eqtl.tsv"
$cs = Join-Path $WorkspaceRoot "1_data\qtl\eqtl\tenk10k\derived\IL12RB2\TenK10K_IL12RB2_susie_credible_members.tsv"
$r12 = Join-Path $WorkspaceRoot "1_data\gwas\outcome\ssc_finngen_r12_r13\regional\R12\finngen_R12_M13_SYSTSLCE_IL12RB2_chr1_66840524_67840524.tsv"
$r13 = Join-Path $WorkspaceRoot "1_data\gwas\outcome\ssc_finngen_r12_r13\regional\R13\finngen_R13_M13_SYSTSLCE_IL12RB2_chr1_66840524_67840524.tsv"
$outdir = Join-Path $WorkspaceRoot "3_results\01_smoke\R4A12FG4_IL12RB2"
New-Item -ItemType Directory -Path $outdir -Force | Out-Null

foreach ($path in @($Python, $Rscript, $qtl, $cs, $r12, $r13)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required input/runtime missing: $path" }
}

& $Python (Join-Path $analysisDir "harmonize_il12rb2_tenk10k_finngen.py") `
    --qtl $qtl --cs $cs --r12 $r12 --r13 $r13 --outdir $outdir
$harmonizationExit = $LASTEXITCODE
if ($harmonizationExit -ne 0 -and -not $AllowPostGateDiagnostic) {
    throw "Exact harmonization/coverage gate did not pass; add -AllowPostGateDiagnostic only to reproduce the explicitly labelled post-gate sensitivity run."
}
if ($harmonizationExit -ne 0) {
    Write-Warning "Exact coverage remains HOLD. Continuing only as a post-gate diagnostic."
}

& $Rscript (Join-Path $analysisDir "run_il12rb2_coloc_abf.R") `
    (Join-Path $outdir "R12_M13_SYSTSLCE_x_TenK10K_NK_IL12RB2_harmonized.tsv") `
    R12 854 484260 (Join-Path $outdir "R12_IL12RB2_coloc_abf_postgate_diagnostic.tsv")
if ($LASTEXITCODE -ne 0) { throw "R12 coloc.abf failed." }

& $Rscript (Join-Path $analysisDir "run_il12rb2_coloc_abf.R") `
    (Join-Path $outdir "R13_M13_SYSTSLCE_x_TenK10K_NK_IL12RB2_harmonized.tsv") `
    R13 883 483310 (Join-Path $outdir "R13_IL12RB2_coloc_abf_postgate_diagnostic.tsv")
if ($LASTEXITCODE -ne 0) { throw "R13 coloc.abf failed." }

& $Python (Join-Path $analysisDir "summarize_il12rb2_coloc.py") `
    --r12 (Join-Path $outdir "R12_IL12RB2_coloc_abf_postgate_diagnostic.tsv") `
    --r13 (Join-Path $outdir "R13_IL12RB2_coloc_abf_postgate_diagnostic.tsv") `
    --out (Join-Path $outdir "R4A12FG4_coloc_abf_postgate_diagnostic_summary.json")
if ($LASTEXITCODE -ne 0) { throw "Coloc sensitivity summarization failed." }

Write-Host "COMPLETE: R4A12FG4 summary-input gate and labelled post-gate diagnostic completed."
