#!/usr/bin/env Rscript

.libPaths(c(normalizePath(file.path(Sys.getenv("IGAN_PROJECT_ROOT", unset=getwd()),"tools/R-library"),winslash="/",mustWork=FALSE),.libPaths()))
suppressPackageStartupMessages({library(susieR); library(coloc); library(data.table); library(jsonlite)})

root <- Sys.getenv("IGAN_PROJECT_ROOT", unset=getwd())
base <- file.path(root, "3_results/04_integration/R6A2B0/sourceLD")
out <- file.path(root, "3_results/04_integration/R6A2B0/multisignal")
dir.create(out, recursive=TRUE, showWarnings=FALSE)
qtl <- fread(file.path(root, "3_results/03_qtl/R6A2B0/R6A2B0_OneK1K_8locus_QTL.tsv.gz"))
triggers <- fread(file.path(root, "3_results/04_integration/R6A2B0/R6A2B0_sourceLD_triggers.tsv"))
leads <- fread(file.path(root, "2_code/06_intake/igan_r6a2b0/R6A2B0_frozen_8_locus_leads.tsv"))

read_float32 <- function(path, p) {
  con <- file(path, "rb"); on.exit(close(con))
  values <- readBin(con, what=numeric(), n=p*p, size=4L, endian="little")
  if (length(values) != p*p) stop("LD binary length mismatch: ", path)
  R <- matrix(values, nrow=p, ncol=p, byrow=TRUE)
  R <- (R+t(R))/2
  diag(R) <- 1
  # Float32 serialization introduces small negative eigenvalues. This fixed,
  # predeclared ridge preserves unit diagonal and is recorded in every row.
  ridge <- 1e-4
  R <- (R + diag(ridge, p))/(1+ridge)
  R
}

summary_rows <- list(); cs_rows <- list(); component_rows <- list(); coloc_rows <- list()
trigger_keys <- unique(triggers[,.(locus,gene,cell_type,qtl_N,shared_top_variant)])
configs <- data.table(config=c("PF10_L5","PF10_L10","PF10_L20","PF50_L10"),
                      ld_mode=c("PF10","PF10","PF10","PF50"), L=c(5L,10L,20L,10L))

for (ii in seq_len(nrow(trigger_keys))) {
  key <- trigger_keys[ii]
  slug <- paste(gsub("/","_",key$locus), key$gene, key$cell_type, sep="_")
  idir <- file.path(base, slug)
  variants <- fread(file.path(idir,"LD_variants.tsv"))
  setorder(variants, LD_order_zero_based)
  qq <- qtl[locus==key$locus & gene==key$gene & cell_type==key$cell_type]
  qq <- qq[match(variants$variant_id, qq$variant_id)]
  if (anyNA(qq$variant_id) || !all(qq$variant_id==variants$variant_id)) stop("QTL/LD order mismatch: ",slug)
  z <- qq$slope_A1/qq$slope_se
  lead <- leads[locus==key$locus]
  disease_lead <- paste0(lead$chromosome,":",lead$position_GRCh37)
  gp <- file.path(root,"3_results/01_gwas/R6A2B0",paste0("combined_",gsub("/","_",key$locus),"_GRCh37_1Mb_A1.tsv.gz"))
  gg <- fread(gp)
  common <- intersect(variants$variant_id, gg$variant_id)
  g <- gg[match(common, variant_id)]
  gd_lbf <- coloc:::approx.bf.estimates(g$beta_A1/g$standard_error, g$standard_error^2, "cc")$lABF
  names(gd_lbf) <- common
  for (jj in seq_len(nrow(configs))) {
    cfg <- configs[jj]
    R <- read_float32(file.path(idir,paste0(cfg$ld_mode,"_residualized_A1_correlation.float32.bin")),nrow(variants))
    warnings <- character()
    fit <- withCallingHandlers(
      susie_rss(z=z,R=R,n=as.integer(key$qtl_N),L=cfg$L,
                estimate_residual_variance=FALSE,estimate_prior_variance=TRUE,
                check_prior=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE),
      warning=function(w){warnings <<- c(warnings,conditionMessage(w)); invokeRestart("muffleWarning")}
    )
    saveRDS(fit,file.path(out,paste0(slug,"_",cfg$config,".susie_fit.rds")),compress="xz")
    pip <- susie_get_pip(fit,prune_by_cs=FALSE)
    cs <- susie_get_cs(fit,Xcorr=R,coverage=0.95,min_abs_corr=0.5,check_symmetric=TRUE)
    cs_list <- if(is.null(cs$cs)) list() else cs$cs
    cs_index <- if(is.null(cs$cs_index)) integer() else cs$cs_index
    idx_lead <- match(disease_lead,variants$variant_id)
    idx_shared <- match(key$shared_top_variant,variants$variant_id)
    idx_top <- which.min(qq$pval_nominal)
    summary_rows[[length(summary_rows)+1L]] <- data.table(
      locus=key$locus,gene=key$gene,cell_type=key$cell_type,config=cfg$config,
      ld_mode=cfg$ld_mode,L=cfg$L,n=as.integer(key$qtl_N),variants=nrow(variants),
      ridge_delta=1e-4,converged=isTRUE(fit$converged),niter=fit$niter,
      credible_sets_95=length(cs_list),active_components=sum(fit$V>1e-9),
      max_PIP_variant=variants$variant_id[which.max(pip)],max_PIP=max(pip),
      disease_lead_variant=disease_lead,disease_lead_PIP=ifelse(is.na(idx_lead),NA_real_,pip[idx_lead]),
      shared_top_variant=key$shared_top_variant,shared_top_PIP=ifelse(is.na(idx_shared),NA_real_,pip[idx_shared]),
      marginal_QTL_top=variants$variant_id[idx_top],marginal_QTL_top_PIP=pip[idx_top],
      warning_count=length(unique(warnings)))
    for (l in seq_len(nrow(fit$alpha))) {
      j <- which.max(fit$alpha[l,])
      component_rows[[length(component_rows)+1L]] <- data.table(
        locus=key$locus,gene=key$gene,cell_type=key$cell_type,config=cfg$config,
        component=l,prior_variance=fit$V[l],top_variant=variants$variant_id[j],
        top_alpha=fit$alpha[l,j],is_credible_component=l %in% cs_index)
    }
    if(length(cs_list)>0) {
      for(cs_name in names(cs_list)) {
        members <- cs_list[[cs_name]]
        component <- as.integer(sub("L","",cs_name))
        purity <- if(!is.null(cs$purity) && cs_name %in% rownames(cs$purity)) cs$purity[cs_name,] else rep(NA_real_,3)
        for(j in members) cs_rows[[length(cs_rows)+1L]] <- data.table(
          locus=key$locus,gene=key$gene,cell_type=key$cell_type,config=cfg$config,
          credible_set=cs_name,component=component,variant_id=variants$variant_id[j],
          alpha=fit$alpha[component,j],PIP=pip[j],marginal_p=qq$pval_nominal[j],
          min_abs_corr=purity[[1]],mean_abs_corr=purity[[2]],median_abs_corr=purity[[3]],
          is_disease_lead=variants$variant_id[j]==disease_lead,
          is_shared_top=variants$variant_id[j]==key$shared_top_variant)
        qbf <- fit$lbf_variable[component,match(common,variants$variant_id)]
        names(qbf) <- common
        for(p12 in c(1e-6,1e-5,1e-4)) {
          bf1 <- c(gd_lbf,null=0); bf2 <- c(qbf,null=0)
          cc <- coloc:::coloc.bf_bf(bf1,bf2,p1=1e-4,p2=1e-4,p12=p12,
                                    overlap.min=0,trim_by_posterior=FALSE)$summary[1]
          coloc_rows[[length(coloc_rows)+1L]] <- data.table(
            locus=key$locus,gene=key$gene,cell_type=key$cell_type,config=cfg$config,
            credible_set=cs_name,component=component,p12=p12,nsnps=cc$nsnps,
            disease_hit=cc$hit1,qtl_signal_hit=cc$hit2,
            PP_H0=cc$PP.H0.abf,PP_H1=cc$PP.H1.abf,PP_H2=cc$PP.H2.abf,
            PP_H3=cc$PP.H3.abf,PP_H4=cc$PP.H4.abf,
            H4_over_H3H4=cc$PP.H4.abf/(cc$PP.H3.abf+cc$PP.H4.abf))
        }
      }
    }
    rm(R,fit,pip,cs); gc()
  }
}

summ <- rbindlist(summary_rows,fill=TRUE)
comps <- rbindlist(component_rows,fill=TRUE)
css <- if(length(cs_rows)) rbindlist(cs_rows,fill=TRUE) else data.table()
cols <- if(length(coloc_rows)) rbindlist(coloc_rows,fill=TRUE) else data.table()
fwrite(summ,file.path(out,"R6A2B0_targeted_susie_summary.tsv"),sep="\t")
fwrite(comps,file.path(out,"R6A2B0_targeted_susie_components.tsv"),sep="\t")
fwrite(css,file.path(out,"R6A2B0_targeted_susie_credible_sets.tsv"),sep="\t")
fwrite(cols,file.path(out,"R6A2B0_targeted_signal_coloc.tsv"),sep="\t")
write_json(list(R=R.version.string,susieR=as.character(packageVersion("susieR")),
                coloc=as.character(packageVersion("coloc")),triggers=nrow(trigger_keys),
                fits=nrow(summ),signal_coloc_rows=nrow(cols)),
           file.path(out,"R6A2B0_targeted_multisignal_run.json"),pretty=TRUE,auto_unbox=TRUE)
cat(toJSON(list(triggers=nrow(trigger_keys),fits=nrow(summ),credible_set_rows=nrow(css),
                 signal_coloc_rows=nrow(cols)),auto_unbox=TRUE),"\n")
