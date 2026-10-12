#!/usr/bin/env Rscript
## R7B0A current-release dual-model targeted signal-level analysis.
## Both PF10 and PF50 QTL z-scores are de novo and paired with LD generated
## from the same 2026 public OneK donor/covariate release.

root <- Sys.getenv("R7_PROJECT_ROOT", unset="H:/SCI2/YR1")
.libPaths(c(file.path(root,"0_admin","tooling","R-library"), .libPaths()))
suppressPackageStartupMessages({
  library(susieR); library(coloc); library(data.table); library(jsonlite)
})

out <- file.path(root,"3_results","04_integration","R7B0A","current_release_dualmodel")
dir.create(out, recursive=TRUE, showWarnings=FALSE)

tr <- fread(file.path(root,"3_results","04_integration","R7A1B","R7A1B_multisignal_triggers.tsv"))
gjbase <- file.path(root,"1_data","study_inputs","PBC_GJOKA","R7A1B")
ldbase <- file.path(root,"3_results","04_integration","R7A1B","sourceLD")
qbase <- file.path(root,"3_results","03_qtl","R7B0","pf50_targeted")

read_gjoka <- function(idx) {
  s <- fread(file.path(gjbase,paste0("sumstats_",idx,".assoc.logistic")))
  if ("TEST" %in% names(s)) s <- s[TEST=="ADD"]
  R <- fread(file.path(gjbase,paste0("covmat_",idx,".ld")),header=FALSE) |> as.matrix()
  if (nrow(R)!=nrow(s) || ncol(R)!=nrow(s)) stop("GJOKA matrix dimension mismatch")
  s[,row_idx:=.I]
  s[,`:=`(beta=as.numeric(BETA),se=as.numeric(SE),z=as.numeric(STAT))]
  if (max(abs(s$beta/s$se-s$z),na.rm=TRUE)>1e-2) stop("GJOKA rounded z check failed")
  list(s=s,R=R)
}

cs_diag <- function(fit, R) {
  cs <- tryCatch(susie_get_cs(fit, Xcorr=R, coverage=.95, min_abs_corr=.5), error=function(e) NULL)
  out <- list(count=0L, min_min_abs_corr=NA_real_, min_median_abs_corr=NA_real_)
  if (is.null(cs) || is.null(cs$cs)) return(out)
  out$count <- length(cs$cs)
  if (!is.null(cs$purity) && nrow(cs$purity)) {
    p <- as.data.frame(cs$purity)
    nms <- names(p)
    min_col <- nms[grepl("min.*abs.*corr|min.abs.corr", nms, ignore.case=TRUE)][1]
    med_col <- nms[grepl("median.*abs.*corr|median.abs.corr", nms, ignore.case=TRUE)][1]
    if (!is.na(min_col)) out$min_min_abs_corr <- min(as.numeric(p[[min_col]]), na.rm=TRUE)
    if (!is.na(med_col)) out$min_median_abs_corr <- min(as.numeric(p[[med_col]]), na.rm=TRUE)
  }
  out
}

diag_rss <- function(z,R,n) {
  s <- tryCatch(estimate_s_rss(z,R,n), error=function(e) NA_real_)
  k <- tryCatch(kriging_rss(z,R,n,s=s), error=function(e) NULL)
  out <- list(s_rss=as.numeric(s), kriging_n=0L, kriging_max_logLR=NA_real_)
  if (!is.null(k) && is.data.frame(k)) {
    nm <- names(k)
    cand <- which(grepl("log|LR",nm,ignore.case=TRUE))
    if (length(cand)) {
      lr <- suppressWarnings(as.numeric(k[[cand[1]]]))
      if (length(lr) && any(is.finite(lr))) {
        out$kriging_max_logLR <- max(lr,na.rm=TRUE)
        out$kriging_n <- sum(is.finite(lr) & lr>2,na.rm=TRUE)
      }
    }
  }
  out
}

configs <- data.table(
  config=c("CURPF10_L5","CURPF10_L10","CURPF10_L20","CURPF50_L10"),
  mode=c("PF10","PF10","PF10","PF50"),
  L=c(5L,10L,20L,10L)
)

rows <- list(); fitrows <- list(); k <- 1L; fk <- 1L
keys <- unique(tr[,.(gene,cell_type,gjoka_locus_index)])

for (i in seq_len(nrow(keys))) {
  key <- keys[i]
  slug <- paste(key$gene,key$cell_type,sep="_")
  d <- file.path(ldbase,slug)
  vars <- fread(file.path(d,"LD_variants.tsv"))
  setorder(vars,LD_order_zero_based)

  gj <- read_gjoka(as.integer(key$gjoka_locus_index))
  bridge <- fread(file.path(root,"3_results","01_gwas","R7A1B",
                            paste0("PBC_",key$gene,"_GRCh37_BIM_A1.tsv.gz")))
  bridge <- bridge[,.(variant_id,rsid,BIM_A1=toupper(BIM_A1),BIM_A2=toupper(BIM_A2))]
  map <- merge(vars[,.(variant_id,pos=as.integer(position_GRCh37),A1=toupper(A1),A2=toupper(A2))],
               bridge,by="variant_id")
  map <- map[A1==BIM_A1 & A2==BIM_A2]
  map <- merge(map,gj$s[,.(SNP,BP=as.integer(BP),z,row_idx)],by.x="rsid",by.y="SNP")
  map <- map[pos==BP & is.finite(z)]
  map <- map[!duplicated(variant_id)]

  common <- intersect(vars$variant_id,map$variant_id)
  if (length(common)<200) stop("too few common variants ",slug)
  vi <- match(common,vars$variant_id)
  mi <- match(common,map$variant_id)
  si <- map$row_idx[mi]
  DLD <- gj$R[si,si,drop=FALSE]
  DLD <- (DLD+t(DLD))/2; diag(DLD) <- 1
  dimnames(DLD) <- list(common,common)
  zD <- map$z[mi]

  for (cc in seq_len(nrow(configs))) {
    cfg <- configs[cc]
    qfile <- file.path(qbase,paste0(slug,"_",cfg$mode,".tsv.gz"))
    if (!file.exists(qfile)) {
      stop("missing current-release de novo summary: ",qfile,
           " ; rerun 01_r7b0_targeted_pf50_tensorqtl_compatible.py first")
    }
    qdat <- fread(qfile)
    qdat <- qdat[match(common,variant_id)]
    if (anyNA(qdat$variant_id)) stop("current summary missing variants ",slug," ",cfg$mode)
    zQ <- qdat$slope_A1/qdat$slope_se

    qldfile <- file.path(d,paste0(cfg$mode,"_residualized_A1_correlation.tsv.gz"))
    if (!file.exists(qldfile)) stop("missing matched LD ",qldfile)
    QLD <- fread(qldfile,header=FALSE) |> as.matrix()
    QLD <- QLD[vi,vi,drop=FALSE]
    QLD <- (QLD+t(QLD))/2; diag(QLD) <- 1
    dimnames(QLD) <- list(common,common)

    nQ <- as.integer(qdat$n_expression_donors[1])
    fitD <- susie_rss(z=zD,R=DLD,n=24510,L=cfg$L,
                      estimate_residual_variance=FALSE,
                      estimate_prior_variance=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE)
    fitQ <- susie_rss(z=zQ,R=QLD,n=nQ,L=cfg$L,
                      estimate_residual_variance=FALSE,
                      estimate_prior_variance=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE)

    dd <- diag_rss(zD,DLD,24510)
    qd <- diag_rss(zQ,QLD,nQ)
    dcs <- cs_diag(fitD,DLD)
    qcs <- cs_diag(fitQ,QLD)

    fitrows[[fk]] <- data.table(
      gene=key$gene,cell_type=key$cell_type,config=cfg$config,
      qtl_model=paste0("CURRENT_RELEASE_",cfg$mode),
      qtl_n=nQ,common_variants=length(common),
      disease_converged=isTRUE(fitD$converged),
      qtl_converged=isTRUE(fitQ$converged),
      disease_cs=dcs$count,qtl_cs=qcs$count,
      disease_cs_min_min_abs_corr=dcs$min_min_abs_corr,
      qtl_cs_min_min_abs_corr=qcs$min_min_abs_corr,
      disease_cs_min_median_abs_corr=dcs$min_median_abs_corr,
      qtl_cs_min_median_abs_corr=qcs$min_median_abs_corr,
      disease_s_rss=dd$s_rss,qtl_s_rss=qd$s_rss,
      disease_kriging_n=dd$kriging_n,qtl_kriging_n=qd$kriging_n,
      disease_kriging_max_logLR=dd$kriging_max_logLR,
      qtl_kriging_max_logLR=qd$kriging_max_logLR
    )
    fk <- fk+1L

    for (p12 in c(1e-6,1e-5,1e-4)) {
      x <- coloc.susie(fitD,fitQ,p1=1e-4,p2=1e-4,p12=p12)
      s <- as.data.table(x$summary)
      if (nrow(s)) {
        s[,`:=`(
          gene=key$gene,cell_type=key$cell_type,
          gjoka_locus_index=key$gjoka_locus_index,
          config=cfg$config,qtl_model=paste0("CURRENT_RELEASE_",cfg$mode),
          p12=p12,qtl_n=nQ,common_variants=length(common),
          disease_converged=isTRUE(fitD$converged),
          qtl_converged=isTRUE(fitQ$converged),
          disease_cs=dcs$count,qtl_cs=qcs$count,
          disease_cs_min_min_abs_corr=dcs$min_min_abs_corr,
          qtl_cs_min_min_abs_corr=qcs$min_min_abs_corr,
          disease_cs_min_median_abs_corr=dcs$min_median_abs_corr,
          qtl_cs_min_median_abs_corr=qcs$min_median_abs_corr,
          disease_s_rss=dd$s_rss,qtl_s_rss=qd$s_rss,
          disease_kriging_n=dd$kriging_n,qtl_kriging_n=qd$kriging_n
        )]
        s[,H4_over_H3H4:=PP.H4.abf/(PP.H3.abf+PP.H4.abf)]
        rows[[k]] <- s
        k <- k+1L
      }
    }
  }
}

R <- if (length(rows)) rbindlist(rows,fill=TRUE) else data.table()
F <- rbindlist(fitrows,fill=TRUE)
fwrite(R,file.path(out,"R7B0A_current_release_dualmodel_coloc_susie.tsv"),sep="\t")
fwrite(F,file.path(out,"R7B0A_current_release_dualmodel_fit_QC.tsv"),sep="\t")
runtime <- list(
  R=R.version.string,
  susieR=as.character(packageVersion("susieR")),
  coloc=as.character(packageVersion("coloc")),
  comparisons=nrow(keys),
  configs=nrow(configs),
  coloc_rows=nrow(R),
  design="2026 current-release de novo QTL summary paired with same-release matched LD"
)
write_json(runtime,file.path(out,"R7B0A_runtime.json"),pretty=TRUE,auto_unbox=TRUE)
print(runtime)
