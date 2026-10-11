#!/usr/bin/env Rscript

.libPaths(c(normalizePath("H:/SCI2/YR1/0_admin/tooling/R-library", winslash = "/"), .libPaths()))
suppressPackageStartupMessages({
  library(coloc)
  library(data.table)
  library(jsonlite)
})

root <- "H:/SCI2/YR1"
qtl <- fread(file.path(root, "3_results/03_qtl/R5A2B/OneK1K_chr5_bounded_region_pairs.tsv.gz"))
targets <- fread(file.path(root, "2_code/06_intake/mg_r5a2b/chr5_source_significant_smoke_targets.tsv"))
targets[, key := paste(cell_type, gene_symbol, sep = "\t")]
qtl[, key := paste(cell_type, phenotype_id, sep = "\t")]
qtl <- qtl[key %in% targets$key]

gwas_files <- list(
  MG_overall = list(path = "GCST90432156_MG_overall_chr5_GRCh37_fixed_1Mb.tsv.gz", cases = 5708, controls = 432028),
  EOMG = list(path = "GCST90432157_EOMG_chr5_GRCh37_fixed_1Mb.tsv.gz", cases = 1391, controls = 22407),
  LOMG = list(path = "GCST90432158_LOMG_chr5_GRCh37_fixed_1Mb.tsv.gz", cases = 2404, controls = 64103)
)

rows <- list()
index <- 1L
combos <- unique(qtl[, .(cell_type, phenotype_id)])
setorder(combos, cell_type, phenotype_id)
for (trait in names(gwas_files)) {
  info <- gwas_files[[trait]]
  gwas <- fread(file.path(root, "3_results/01_gwas/R5A2B", info$path))
  gwas <- gwas[inference_eligible == TRUE]
  for (i in seq_len(nrow(combos))) {
    cell <- combos$cell_type[i]
    gene <- combos$phenotype_id[i]
    q <- qtl[cell_type == cell & phenotype_id == gene]
    merged <- merge(q, gwas, by = "variant_id")
    merged <- merged[
      is.finite(slope_A1) & is.finite(slope_se) & slope_se > 0 &
      is.finite(beta_logOR_A1) & is.finite(standard_error) & standard_error > 0
    ]
    setorder(merged, variant_id)
    if (nrow(merged) < 500) next
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
      N = unique(merged$n_expression_donors),
      type = "quant"
    )
    for (p12 in c(1e-6, 1e-5, 1e-4)) {
      fit <- suppressWarnings(suppressMessages(coloc.abf(d1, d2, p1 = 1e-4, p2 = 1e-4, p12 = p12)))
      s <- fit$summary
      rows[[index]] <- data.table(
        trait = trait,
        cell_type = cell,
        phenotype_id = gene,
        p12 = p12,
        nsnps = as.integer(s[["nsnps"]]),
        PP_H0 = unname(s[["PP.H0.abf"]]),
        PP_H1 = unname(s[["PP.H1.abf"]]),
        PP_H2 = unname(s[["PP.H2.abf"]]),
        PP_H3 = unname(s[["PP.H3.abf"]]),
        PP_H4 = unname(s[["PP.H4.abf"]]),
        H4_over_H3H4 = unname(s[["PP.H4.abf"]] / (s[["PP.H3.abf"]] + s[["PP.H4.abf"]])),
        top_SNP = fit$results$snp[which.max(fit$results$SNP.PP.H4)],
        top_SNP_PP_H4 = max(fit$results$SNP.PP.H4)
      )
      index <- index + 1L
    }
  }
}

result <- rbindlist(rows)
setorder(result, trait, cell_type, phenotype_id, p12)
out_dir <- file.path(root, "3_results/04_integration/R5A2B")
fwrite(result, file.path(out_dir, "chr5_coloc_official_R_validation.tsv"), sep = "\t")
summary <- list(
  generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  R_version = R.version.string,
  coloc_version = as.character(packageVersion("coloc")),
  comparisons = as.integer(length(unique(paste(result$trait, result$cell_type, result$phenotype_id)))),
  runs = nrow(result),
  max_default_H4 = max(result[p12 == 1e-5]$PP_H4),
  max_default_H4_row = as.list(result[p12 == 1e-5][which.max(PP_H4)]),
  robust_default_H4_count = nrow(result[p12 == 1e-5 & PP_H4 >= 0.8 & H4_over_H3H4 >= 0.8])
)
write_json(summary, file.path(out_dir, "chr5_coloc_official_R_validation.json"), pretty = TRUE, auto_unbox = TRUE, digits = 16)
cat(toJSON(summary, pretty = TRUE, auto_unbox = TRUE, digits = 10), "\n")
