#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(coloc))

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 5) {
  stop("usage: run_il12rb2_coloc_abf.R <harmonized.tsv> <release> <cases> <controls> <out.tsv>")
}

input_path <- args[[1]]
release <- args[[2]]
cases <- as.numeric(args[[3]])
controls <- as.numeric(args[[4]])
output_path <- args[[5]]

d <- read.delim(input_path, stringsAsFactors = FALSE, check.names = FALSE)
required <- c("variant_key", "qtl_beta", "qtl_se", "qtl_af_alt", "qtl_n",
              "gwas_beta", "gwas_se", "gwas_af_alt")
missing <- setdiff(required, names(d))
if (length(missing) > 0) stop(paste("missing columns:", paste(missing, collapse = ",")))
if (nrow(d) < 100) stop("fewer than 100 harmonized variants")

valid <- is.finite(d$qtl_beta) & is.finite(d$qtl_se) & d$qtl_se > 0 &
         is.finite(d$qtl_af_alt) & d$qtl_af_alt > 0 & d$qtl_af_alt < 1 &
         is.finite(d$gwas_beta) & is.finite(d$gwas_se) & d$gwas_se > 0 &
         is.finite(d$gwas_af_alt) & d$gwas_af_alt > 0 & d$gwas_af_alt < 1
d <- d[valid, ]
if (nrow(d) < 100) stop("fewer than 100 valid harmonized variants")

n_qtl_values <- unique(d$qtl_n)
if (length(n_qtl_values) != 1) {
  warning("qtl N varies; using median N")
}
n_qtl <- median(d$qtl_n)
n_gwas <- cases + controls
s_gwas <- cases / n_gwas
qtl_maf <- pmin(d$qtl_af_alt, 1 - d$qtl_af_alt)
# Same estimator used internally by coloc::sdY.est, made explicit so the
# estimated phenotype SD and its provenance are present in every result row.
qtl_nvx <- 2 * n_qtl * qtl_maf * (1 - qtl_maf)
qtl_sdY <- sqrt(coef(lm(qtl_nvx ~ I(1 / (d$qtl_se ^ 2)) - 1))[[1]])

dataset_qtl <- list(
  beta = d$qtl_beta,
  varbeta = d$qtl_se ^ 2,
  snp = d$variant_key,
  position = d$pos,
  MAF = qtl_maf,
  N = n_qtl,
  sdY = qtl_sdY,
  type = "quant"
)
dataset_gwas <- list(
  beta = d$gwas_beta,
  varbeta = d$gwas_se ^ 2,
  snp = d$variant_key,
  position = d$pos,
  MAF = pmin(d$gwas_af_alt, 1 - d$gwas_af_alt),
  N = n_gwas,
  s = s_gwas,
  type = "cc"
)

p12_values <- c(1e-6, 1e-5, 1e-4)
rows <- list()
for (p12 in p12_values) {
  fit <- coloc.abf(dataset1 = dataset_gwas, dataset2 = dataset_qtl,
                   p1 = 1e-4, p2 = 1e-4, p12 = p12)
  summary <- fit$summary
  top_index <- which.max(fit$results$SNP.PP.H4)
  h3 <- unname(summary[["PP.H3.abf"]])
  h4 <- unname(summary[["PP.H4.abf"]])
  rows[[length(rows) + 1]] <- data.frame(
    release = release,
    role = "POST_EXACT_COVERAGE_GATE_SINGLE_CAUSAL_DIAGNOSTIC_ONLY",
    p1 = 1e-4,
    p2 = 1e-4,
    p12 = p12,
    nsnps = unname(summary[["nsnps"]]),
    PP.H0 = unname(summary[["PP.H0.abf"]]),
    PP.H1 = unname(summary[["PP.H1.abf"]]),
    PP.H2 = unname(summary[["PP.H2.abf"]]),
    PP.H3 = h3,
    PP.H4 = h4,
    H4_over_H3H4 = ifelse(h3 + h4 > 0, h4 / (h3 + h4), NA_real_),
    top_shared_variant = fit$results$snp[[top_index]],
    top_shared_variant_PP_H4 = fit$results$SNP.PP.H4[[top_index]],
    qtl_N = n_qtl,
    qtl_sdY = qtl_sdY,
    qtl_sdY_source = "coloc_sdY_est_formula_from_varbeta_MAF_N",
    gwas_N = n_gwas,
    gwas_case_fraction = s_gwas,
    qtl_min_p = min(d$qtl_p),
    gwas_min_p = min(d$gwas_p),
    coloc_version = as.character(packageVersion("coloc")),
    R_version = R.version.string,
    stringsAsFactors = FALSE
  )
}
result <- do.call(rbind, rows)
write.table(result, file = output_path, sep = "\t", row.names = FALSE, quote = FALSE)
cat(output_path, "\n")
