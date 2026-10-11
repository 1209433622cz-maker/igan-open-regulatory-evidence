#!/usr/bin/env Rscript

.libPaths(c(normalizePath("H:/SCI2/YR1/0_admin/tooling/R-library", winslash = "/"), .libPaths()))
suppressPackageStartupMessages({
  library(coloc)
  library(data.table)
  library(jsonlite)
})

root <- "H:/SCI2/YR1"
qtl <- fread(file.path(root, "3_results/03_qtl/R5A2A2/OneK1K_chr18_fixed_1Mb_region_pairs.tsv.gz"))
qtl <- qtl[cell_type == "NK_R" & phenotype_id == "ZCCHC2"]
gwas_files <- list(
  MG_overall = list(path = "GCST90432156_MG_overall_chr18_GRCh37_fixed_1Mb.tsv.gz", cases = 5708, controls = 432028),
  LOMG = list(path = "GCST90432158_LOMG_chr18_GRCh37_fixed_1Mb.tsv.gz", cases = 2404, controls = 64103)
)
out <- list()
for (trait in names(gwas_files)) {
  info <- gwas_files[[trait]]
  gwas <- fread(file.path(root, "3_results/01_gwas/R5A2A2", info$path))
  gwas <- gwas[inference_eligible == TRUE]
  merged <- merge(qtl, gwas, by = "variant_id")
  merged <- merged[is.finite(slope_A1) & is.finite(slope_se) & slope_se > 0 &
                     is.finite(beta_logOR_A1) & is.finite(standard_error) & standard_error > 0]
  setorder(merged, variant_id)
  d1 <- list(
    beta = merged$beta_logOR_A1,
    varbeta = merged$standard_error^2,
    snp = merged$variant_id,
    MAF = pmin(merged$EAF_A1, 1 - merged$EAF_A1),
    N = info$cases + info$controls,
    s = info$cases / (info$cases + info$controls),
    type = "cc"
  )
  d2 <- list(
    beta = merged$slope_A1,
    varbeta = merged$slope_se^2,
    snp = merged$variant_id,
    MAF = pmin(merged$af_A1, 1 - merged$af_A1),
    N = 750,
    type = "quant"
  )
  runs <- list()
  for (p12 in c(1e-6, 1e-5, 1e-4)) {
    fit <- coloc.abf(d1, d2, p1 = 1e-4, p2 = 1e-4, p12 = p12)
    summary <- as.list(fit$summary)
    runs[[format(p12, scientific = TRUE)]] <- list(
      nsnps = as.integer(summary$nsnps),
      PP_H0 = unname(summary$PP.H0.abf),
      PP_H1 = unname(summary$PP.H1.abf),
      PP_H2 = unname(summary$PP.H2.abf),
      PP_H3 = unname(summary$PP.H3.abf),
      PP_H4 = unname(summary$PP.H4.abf),
      H4_over_H3H4 = unname(summary$PP.H4.abf / (summary$PP.H3.abf + summary$PP.H4.abf)),
      top_SNP = fit$results$snp[which.max(fit$results$SNP.PP.H4)],
      top_SNP_PP_H4 = max(fit$results$SNP.PP.H4)
    )
  }
  out[[trait]] <- runs
}
result <- list(
  generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  R_version = R.version.string,
  coloc_version = as.character(packageVersion("coloc")),
  results = out
)
path <- file.path(root, "3_results/04_integration/R5A2A4/NK_R_ZCCHC2_multisignal/R_coloc_validation.json")
write_json(result, path, pretty = TRUE, auto_unbox = TRUE, digits = 16)
cat(toJSON(result, pretty = TRUE, auto_unbox = TRUE, digits = 10), "\n")
