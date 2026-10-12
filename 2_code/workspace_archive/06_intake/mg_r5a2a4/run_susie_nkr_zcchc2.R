#!/usr/bin/env Rscript

.libPaths(c(normalizePath("H:/SCI2/YR1/0_admin/tooling/R-library", winslash = "/"), .libPaths()))
suppressPackageStartupMessages({
  library(susieR)
  library(data.table)
  library(jsonlite)
})

root <- "H:/SCI2/YR1"
input_dir <- file.path(root, "3_results/04_integration/R5A2A4/NK_R_ZCCHC2_sourceLD")
out_dir <- file.path(root, "3_results/04_integration/R5A2A4/NK_R_ZCCHC2_multisignal")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

variants <- fread(file.path(input_dir, "NK_R_ZCCHC2_LD_variants.tsv"))
p <- nrow(variants)
stopifnot(p == 3827L, identical(variants$LD_order_zero_based, 0:(p - 1L)))
z <- variants$QTL_slope_A1 / variants$QTL_slope_se
stopifnot(all(is.finite(z)), all(variants$variant_id == as.character(variants$variant_id)))

read_float32_matrix <- function(path, p) {
  con <- file(path, "rb")
  on.exit(close(con))
  values <- readBin(con, what = numeric(), n = p * p, size = 4L, endian = "little")
  if (length(values) != p * p) stop("LD binary length mismatch")
  R <- matrix(values, nrow = p, ncol = p)
  R <- (R + t(R)) / 2
  diag(R) <- 1
  R
}

configs <- list(
  list(name = "PF10_L10_primary", file = "NK_R_ZCCHC2_PF10_residualized_A1_correlation.float32.bin", L = 10L, estimate_residual = FALSE),
  list(name = "PF10_L5", file = "NK_R_ZCCHC2_PF10_residualized_A1_correlation.float32.bin", L = 5L, estimate_residual = FALSE),
  list(name = "PF10_L20", file = "NK_R_ZCCHC2_PF10_residualized_A1_correlation.float32.bin", L = 20L, estimate_residual = FALSE),
  list(name = "PF10_L10_estimate_residual", file = "NK_R_ZCCHC2_PF10_residualized_A1_correlation.float32.bin", L = 10L, estimate_residual = TRUE),
  list(name = "RAW_L10", file = "NK_R_ZCCHC2_signed_A1_correlation.float32.bin", L = 10L, estimate_residual = FALSE),
  list(name = "PF50_L10", file = "NK_R_ZCCHC2_PF50_residualized_A1_correlation.float32.bin", L = 10L, estimate_residual = FALSE)
)

summary_rows <- list()
component_rows <- list()
cs_rows <- list()
pip_rows <- list()
warnings_by_config <- list()

for (cfg in configs) {
  R <- read_float32_matrix(file.path(input_dir, cfg$file), p)
  captured_warnings <- character()
  fit <- withCallingHandlers(
    susie_rss(
      z = z,
      R = R,
      n = 750,
      L = cfg$L,
      estimate_residual_variance = cfg$estimate_residual,
      estimate_prior_variance = TRUE,
      check_prior = TRUE,
      max_iter = 2000,
      tol = 1e-4,
      verbose = FALSE
    ),
    warning = function(w) {
      captured_warnings <<- c(captured_warnings, conditionMessage(w))
      invokeRestart("muffleWarning")
    }
  )
  warnings_by_config[[cfg$name]] <- unique(captured_warnings)
  saveRDS(fit, file.path(out_dir, paste0(cfg$name, ".susie_fit.rds")), compress = "xz")
  pip <- susie_get_pip(fit, prune_by_cs = FALSE)
  cs <- susie_get_cs(fit, Xcorr = R, coverage = 0.95, min_abs_corr = 0.5, check_symmetric = TRUE)
  cs_list <- if (is.null(cs$cs)) list() else cs$cs
  max_pip_index <- which.max(pip)
  lead_index <- match("18:60005046", variants$variant_id)
  top_index <- match("18:60243208", variants$variant_id)
  active_components <- which(fit$V > 1e-9)
  summary_rows[[length(summary_rows) + 1L]] <- data.table(
    config = cfg$name,
    LD_mode = sub("_L.*$", "", cfg$name),
    L = cfg$L,
    estimate_residual_variance = cfg$estimate_residual,
    converged = isTRUE(fit$converged),
    niter = fit$niter,
    residual_variance = fit$sigma2,
    nonzero_prior_variance_components = length(active_components),
    credible_sets_95 = length(cs_list),
    max_PIP_variant = variants$variant_id[max_pip_index],
    max_PIP = pip[max_pip_index],
    rs7239261_PIP = pip[lead_index],
    QTL_top_60243208_PIP = pip[top_index],
    final_ELBO = tail(fit$elbo, 1),
    warning_count = length(unique(captured_warnings))
  )
  pip_rows[[length(pip_rows) + 1L]] <- data.table(
    config = cfg$name,
    variant_id = variants$variant_id,
    position_GRCh37 = variants$position_GRCh37,
    PIP = pip,
    marginal_p = variants$QTL_pval_nominal,
    is_rs7239261 = variants$variant_id == "18:60005046",
    is_marginal_QTL_top = variants$variant_id == "18:60243208"
  )
  for (l in seq_len(nrow(fit$alpha))) {
    j <- which.max(fit$alpha[l, ])
    component_rows[[length(component_rows) + 1L]] <- data.table(
      config = cfg$name,
      component = l,
      prior_variance = fit$V[l],
      top_variant = variants$variant_id[j],
      top_position_GRCh37 = variants$position_GRCh37[j],
      top_alpha = fit$alpha[l, j],
      top_variant_marginal_p = variants$QTL_pval_nominal[j],
      rs7239261_alpha = fit$alpha[l, lead_index],
      QTL_top_60243208_alpha = fit$alpha[l, top_index]
    )
  }
  if (length(cs_list) > 0) {
    for (cs_name in names(cs_list)) {
      members <- cs_list[[cs_name]]
      component <- as.integer(sub("L", "", cs_name))
      purity <- if (!is.null(cs$purity) && cs_name %in% rownames(cs$purity)) cs$purity[cs_name, ] else rep(NA_real_, 3)
      for (j in members) {
        cs_rows[[length(cs_rows) + 1L]] <- data.table(
          config = cfg$name,
          credible_set = cs_name,
          component = component,
          variant_id = variants$variant_id[j],
          position_GRCh37 = variants$position_GRCh37[j],
          alpha = fit$alpha[component, j],
          PIP = pip[j],
          marginal_p = variants$QTL_pval_nominal[j],
          min_abs_corr = purity[[1]],
          mean_abs_corr = purity[[2]],
          median_abs_corr = purity[[3]],
          is_rs7239261 = variants$variant_id[j] == "18:60005046",
          is_marginal_QTL_top = variants$variant_id[j] == "18:60243208"
        )
      }
    }
  }
  rm(R, fit, pip, cs)
  gc()
}

summary_dt <- rbindlist(summary_rows, fill = TRUE)
component_dt <- rbindlist(component_rows, fill = TRUE)
cs_dt <- if (length(cs_rows)) rbindlist(cs_rows, fill = TRUE) else data.table(
  config = character(), credible_set = character(), component = integer(), variant_id = character(),
  position_GRCh37 = integer(), alpha = numeric(), PIP = numeric(), marginal_p = numeric(),
  min_abs_corr = numeric(), mean_abs_corr = numeric(), median_abs_corr = numeric(),
  is_rs7239261 = logical(), is_marginal_QTL_top = logical()
)
pip_dt <- rbindlist(pip_rows, fill = TRUE)

fwrite(summary_dt, file.path(out_dir, "NK_R_ZCCHC2_susie_summary.tsv"), sep = "\t")
fwrite(component_dt, file.path(out_dir, "NK_R_ZCCHC2_susie_components.tsv"), sep = "\t")
fwrite(cs_dt, file.path(out_dir, "NK_R_ZCCHC2_susie_credible_sets.tsv"), sep = "\t")
fwrite(pip_dt, file.path(out_dir, "NK_R_ZCCHC2_susie_PIP.tsv.gz"), sep = "\t", compress = "gzip")

primary <- summary_dt[config == "PF10_L10_primary"]
audit <- list(
  schema_version = "1.0",
  generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  R_version = R.version.string,
  package_versions = list(susieR = as.character(packageVersion("susieR")), data.table = as.character(packageVersion("data.table")), jsonlite = as.character(packageVersion("jsonlite"))),
  input = list(n = 750L, variants = p, z_min_p = min(variants$QTL_pval_nominal), local_bonferroni_threshold = 0.05 / p),
  primary = as.list(primary),
  all_configs = lapply(seq_len(nrow(summary_dt)), function(i) as.list(summary_dt[i])),
  warnings = warnings_by_config,
  adjudication_checks = list(
    primary_converged = isTRUE(primary$converged),
    primary_has_95pct_credible_set = primary$credible_sets_95 > 0,
    primary_rs7239261_PIP_ge_0_1 = primary$rs7239261_PIP >= 0.1,
    primary_max_PIP_ge_0_1 = primary$max_PIP >= 0.1,
    any_sensitivity_has_95pct_credible_set = any(summary_dt$credible_sets_95 > 0),
    all_configs_converged = all(summary_dt$converged)
  )
)
audit$multisignal_support_pass <- isTRUE(audit$adjudication_checks$primary_has_95pct_credible_set) &&
  isTRUE(audit$adjudication_checks$primary_rs7239261_PIP_ge_0_1)
write_json(audit, file.path(out_dir, "NK_R_ZCCHC2_susie_audit.json"), pretty = TRUE, auto_unbox = TRUE, digits = 16, na = "null")
cat(toJSON(audit, pretty = TRUE, auto_unbox = TRUE, digits = 10, na = "null"), "\n")
