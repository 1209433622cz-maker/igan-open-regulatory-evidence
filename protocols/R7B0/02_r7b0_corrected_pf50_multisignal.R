#!/usr/bin/env Rscript
## R7B0: re-run frozen 7 comparisons with corrected PF50 QTL z paired to PF50 LD.
## PF10 configs intentionally retain the frozen source summary; PF50 reads the
## targeted TensorQTL-formula-compatible output and is labelled accordingly.
root <- Sys.getenv("R7_PROJECT_ROOT", unset="H:/SCI2/YR1")
.libPaths(c(file.path(root,"tools","R-library"), .libPaths()))
suppressPackageStartupMessages({library(susieR); library(coloc); library(data.table); library(jsonlite)})
out <- file.path(root,"3_results","04_integration","R7B0","multisignal")
dir.create(out, recursive=TRUE, showWarnings=FALSE)
qall <- fread(file.path(root,"3_results","03_qtl","R7A1B","R7A1B_OneK_frozen_QTL.tsv.gz"))
tr <- fread(file.path(root,"3_results","04_integration","R7A1B","R7A1B_multisignal_triggers.tsv"))
gjbase <- file.path(root,"1_data","study_inputs","PBC_GJOKA","R7A1B")
ldbase <- file.path(root,"3_results","04_integration","R7A1B","sourceLD")
pf50base <- file.path(root,"3_results","03_qtl","R7B0","pf50_targeted")

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

cs_count <- function(fit, R) {
  cs <- tryCatch(susie_get_cs(fit, Xcorr=R, coverage=.95, min_abs_corr=.5), error=function(e) NULL)
  if (is.null(cs) || is.null(cs$cs)) return(0L)
  length(cs$cs)
}
diag_rss <- function(z,R,n) {
  s <- tryCatch(estimate_s_rss(z,R,n), error=function(e) NA_real_)
  k <- tryCatch(kriging_rss(z,R,n,s=s), error=function(e) NULL)
  out <- list(s_rss=as.numeric(s), kriging_n=0L, kriging_max_logLR=NA_real_)
  if (!is.null(k)) {
    if (is.data.frame(k)) {
      nm <- names(k); lr <- k[[nm[grepl("log|LR",nm,ignore.case=TRUE)[1]]]]
      if (!is.null(lr)) out$kriging_max_logLR <- max(as.numeric(lr),na.rm=TRUE)
      out$kriging_n <- sum(is.finite(as.numeric(lr)) & as.numeric(lr)>2,na.rm=TRUE)
    } else if (is.numeric(k)) {
      out$kriging_max_logLR <- max(k,na.rm=TRUE); out$kriging_n <- sum(k>2,na.rm=TRUE)
    }
  }
  out
}

configs <- data.table(config=c("PF10_L5","PF10_L10","PF10_L20","PF50_L10"),
                      mode=c("PF10","PF10","PF10","PF50"),L=c(5L,10L,20L,10L))
rows <- list(); fits <- list(); k <- 1L; f <- 1L
keys <- unique(tr[,.(gene,cell_type,gjoka_locus_index)])
for (i in seq_len(nrow(keys))) {
  key <- keys[i]; slug <- paste(key$gene,key$cell_type,sep="_"); d <- file.path(ldbase,slug)
  vars <- fread(file.path(d,"LD_variants.tsv")); setorder(vars,LD_order_zero_based)
  qq <- qall[gene==key$gene & cell_type==key$cell_type]
  qq <- qq[match(vars$variant_id,qq$variant_id)]
  if (anyNA(qq$variant_id)) stop("QTL/LD mismatch ",slug)
  gj <- read_gjoka(as.integer(key$gjoka_locus_index))
  bridge <- fread(file.path(root,"3_results","01_gwas","R7A1B",paste0("PBC_",key$gene,"_GRCh37_BIM_A1.tsv.gz")))
  bridge <- bridge[,.(variant_id,rsid,BIM_A1=toupper(BIM_A1),BIM_A2=toupper(BIM_A2))]
  map <- merge(vars[,.(variant_id,pos=as.integer(position_GRCh37),A1=toupper(A1),A2=toupper(A2))],bridge,by="variant_id")
  map <- map[A1==BIM_A1 & A2==BIM_A2]
  map <- merge(map,gj$s[,.(SNP,BP=as.integer(BP),z,row_idx)],by.x="rsid",by.y="SNP")
  map <- map[pos==BP & is.finite(z)]
  map <- map[!duplicated(variant_id)]
  common <- intersect(vars$variant_id,map$variant_id)
  if (length(common)<200) stop("too few common variants ",slug)
  vi <- match(common,vars$variant_id); mi <- match(common,map$variant_id); si <- map$row_idx[mi]
  DLD <- gj$R[si,si,drop=FALSE]; DLD <- (DLD+t(DLD))/2; diag(DLD) <- 1; dimnames(DLD)<-list(common,common)
  zD <- map$z[mi]
  for (cc in seq_len(nrow(configs))) {
    cfg <- configs[cc]
    qdat <- NULL
    if (cfg$mode=="PF50") {
      qdat <- fread(file.path(pf50base,paste0(slug,"_PF50.tsv.gz")))
      qdat <- qdat[match(common,variant_id)]
      if (anyNA(qdat$variant_id)) stop("corrected PF50 missing variants ",slug)
      zQ <- qdat$slope_A1/qdat$slope_se
    } else {
      zQ <- qq$slope_A1[vi]/qq$slope_se[vi]
    }
    qldfile <- file.path(d,paste0(cfg$mode,"_residualized_A1_correlation.tsv.gz"))
    QLD <- fread(qldfile,header=FALSE) |> as.matrix(); QLD <- QLD[vi,vi,drop=FALSE]
    QLD <- (QLD+t(QLD))/2; diag(QLD)<-1; dimnames(QLD)<-list(common,common)
    fitD <- susie_rss(z=zD,R=DLD,n=24510,L=cfg$L,estimate_residual_variance=FALSE,
                      estimate_prior_variance=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE)
    nQ <- if (cfg$mode=="PF50") qdat$n_expression_donors[1] else qq$n_expression_donors[1]
    fitQ <- susie_rss(z=zQ,R=QLD,n=as.integer(nQ),L=cfg$L,estimate_residual_variance=FALSE,
                      estimate_prior_variance=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE)
    fits[[f]] <- list(gene=key$gene,cell_type=key$cell_type,config=cfg$config,fitD=fitD,fitQ=fitQ); f<-f+1L
    dd <- diag_rss(zD,DLD,24510); qd <- diag_rss(zQ,QLD,as.integer(nQ))
    co <- NULL
    for (p12 in c(1e-6,1e-5,1e-4)) {
      x <- coloc.susie(fitD,fitQ,p1=1e-4,p2=1e-4,p12=p12)
      s <- as.data.table(x$summary)
      if (nrow(s)) {
        s[,`:=`(gene=key$gene,cell_type=key$cell_type,gjoka_locus_index=key$gjoka_locus_index,
                config=cfg$config,p12=p12,PF50_source=(cfg$mode=="PF50"),
                qtl_n=as.integer(nQ),common_variants=length(common),
                disease_converged=isTRUE(fitD$converged),qtl_converged=isTRUE(fitQ$converged),
                disease_cs=cs_count(fitD,DLD),qtl_cs=cs_count(fitQ,QLD),
                disease_s_rss=dd$s_rss,qtl_s_rss=qd$s_rss,
                disease_kriging_n=dd$kriging_n,qtl_kriging_n=qd$kriging_n)]
        s[,H4_over_H3H4:=PP.H4.abf/(PP.H3.abf+PP.H4.abf)]
        rows[[k]] <- s; k<-k+1L
      }
    }
  }
}
R <- rbindlist(rows,fill=TRUE)
fwrite(R,file.path(out,"R7B0_corrected_multisignal_coloc_susie.tsv"),sep="\t")
fit_summary <- rbindlist(lapply(fits,function(x) data.table(gene=x$gene,cell_type=x$cell_type,config=x$config,
              disease_converged=isTRUE(x$fitD$converged),qtl_converged=isTRUE(x$fitQ$converged))),fill=TRUE)
fwrite(fit_summary,file.path(out,"R7B0_fit_summary.tsv"),sep="\t")
runtime <- list(R=R.version.string,susieR=as.character(packageVersion("susieR")),coloc=as.character(packageVersion("coloc")),
                comparisons=nrow(keys),rows=nrow(R),configs=nrow(configs),implementation="R7A1B workflow; PF50 QTL z replaced by R7B0 targeted output")
write_json(runtime,file.path(out,"R7B0_multisignal_runtime.json"),pretty=TRUE,auto_unbox=TRUE)
print(runtime)
