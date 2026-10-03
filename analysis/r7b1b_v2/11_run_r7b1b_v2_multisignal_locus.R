#!/usr/bin/env Rscript
## Run one R7B1B v2 locus.  The Python orchestrator launches independent
## loci, while every comparison is checkpointed for deterministic resume.

root <- Sys.getenv("R7_PROJECT_ROOT", unset="H:/SCI2/YR1")
.libPaths(c(file.path(root,"tools","R-library"), .libPaths()))
suppressPackageStartupMessages({
  library(susieR); library(coloc); library(data.table); library(jsonlite)
})

locus_env <- Sys.getenv("R7B1B_LOCUS", unset="")
if (!nzchar(locus_env)) stop("R7B1B_LOCUS is required")
locus <- as.integer(locus_env)
if (!is.finite(locus)) stop("R7B1B_LOCUS is not an integer")

work_path <- file.path(root,"3_results","00_audit","R7B1B_v2","R7B1B_v2_exact_642_high_information_comparisons.tsv")
qbase <- file.path(root,"3_results","03_qtl","R7B1B_v2","dualmodel_qtl")
ldbase <- file.path(root,"3_results","04_integration","R7B1B_v2","sourceLD_blocks")
gjbase <- file.path(root,"1_data","study_inputs","PBC_GJOKA","R7B1B_v2")
bridge_path <- file.path(root,"3_results","01_gwas","R7B1","R7B1_PBC56_GRCh37_BIM_A1.tsv.gz")
outbase <- file.path(root,"3_results","04_integration","R7B1B_v2","multisignal")
out <- file.path(outbase,sprintf("locus_%02d",locus))
dir.create(out,recursive=TRUE,showWarnings=FALSE)

work <- fread(work_path)[locus_index==locus]
if (!nrow(work)) stop("no workload rows for locus ",locus)
setorder(work,comparison_id)

read_gjoka <- function(idx) {
  sf <- file.path(gjbase,paste0("sumstats_",idx,".assoc.logistic"))
  lf <- file.path(gjbase,paste0("covmat_",idx,".ld"))
  if (!file.exists(sf) || !file.exists(lf)) stop("missing GJOKA member pair for locus ",idx)
  s <- fread(sf)
  if ("TEST" %in% names(s)) s <- s[TEST=="ADD"]
  required <- c("SNP","BP","A1","BETA","SE","STAT")
  missing <- setdiff(required,names(s))
  if (length(missing)) stop("GJOKA summary missing: ",paste(missing,collapse=","))
  R <- fread(lf,header=FALSE,showProgress=FALSE) |> as.matrix()
  if (nrow(R)!=nrow(s) || ncol(R)!=nrow(s)) stop("GJOKA matrix dimension mismatch")
  s[,row_idx:=.I]
  s[,`:=`(BP=as.integer(BP),z=as.numeric(STAT),beta=as.numeric(BETA),se=as.numeric(SE))]
  ok <- s[is.finite(beta)&is.finite(se)&se>0&is.finite(z)]
  if (!nrow(ok)) stop("GJOKA has no finite additive rows")
  delta <- max(abs(ok$beta/ok$se-ok$z))
  zcor <- cor(ok$beta/ok$se,ok$z)
  ## The 47-locus pre-posterior audit found one maximum rounding delta of
  ## 0.0105516, while the minimum correlation was 0.999999883. Apply one
  ## uniform text-rounding bound to every locus; no locus-specific exception.
  if (!is.finite(delta) || delta>2e-2 || !is.finite(zcor) || zcor<0.99999)
    stop("GJOKA BETA/SE/STAT identity check failed: max_delta=",delta," correlation=",zcor)
  R <- (R+t(R))/2
  diag(R) <- 1
  list(s=s,R=R,z_rounding_max_delta=delta,z_rounding_correlation=zcor)
}

read_binary_ld <- function(path,n) {
  con <- file(path,"rb")
  on.exit(close(con))
  x <- readBin(con,what="numeric",n=n*n,size=4,endian="little")
  if (length(x)!=n*n) stop("binary LD length mismatch: ",path)
  ## Python writes row-major. R fills column-major; the transpose is identical
  ## for a symmetric correlation matrix, but transpose explicitly for clarity.
  R <- t(matrix(x,nrow=n,ncol=n))
  R <- (R+t(R))/2
  diag(R) <- 1
  R
}

safe_s_rss <- function(z,R,n) {
  tryCatch(as.numeric(estimate_s_rss(z,R,n)),error=function(e) NA_real_)
}

safe_kriging <- function(z,R,n,s) {
  k <- tryCatch(kriging_rss(z,R,n,s=s),error=function(e) NULL)
  ans <- list(flag_n=NA_integer_,max_logLR=NA_real_)
  if (is.null(k) || !is.data.frame(k)) return(ans)
  cand <- which(grepl("log|LR",names(k),ignore.case=TRUE))
  if (!length(cand)) return(ans)
  lr <- suppressWarnings(as.numeric(k[[cand[1]]]))
  if (length(lr) && any(is.finite(lr))) {
    ans$flag_n <- sum(is.finite(lr)&lr>2,na.rm=TRUE)
    ans$max_logLR <- max(lr,na.rm=TRUE)
  }
  ans
}

cs_diag <- function(fit,R) {
  cs <- tryCatch(susie_get_cs(fit,Xcorr=R,coverage=.95,min_abs_corr=.5),error=function(e) NULL)
  ans <- list(count=0L,min_min_abs_corr=NA_real_,min_median_abs_corr=NA_real_)
  if (is.null(cs) || is.null(cs$cs)) return(ans)
  ans$count <- length(cs$cs)
  if (!is.null(cs$purity) && nrow(cs$purity)) {
    p <- as.data.frame(cs$purity)
    min_col <- names(p)[grepl("min.*abs.*corr|min.abs.corr",names(p),ignore.case=TRUE)][1]
    med_col <- names(p)[grepl("median.*abs.*corr|median.abs.corr",names(p),ignore.case=TRUE)][1]
    if (!is.na(min_col)) ans$min_min_abs_corr <- suppressWarnings(min(as.numeric(p[[min_col]]),na.rm=TRUE))
    if (!is.na(med_col)) ans$min_median_abs_corr <- suppressWarnings(min(as.numeric(p[[med_col]]),na.rm=TRUE))
  }
  ans
}

cs_members <- function(fit,trait,comparison_id,config,variants) {
  if (is.null(fit$sets$cs) || !length(fit$sets$cs)) return(NULL)
  rows <- lapply(seq_along(fit$sets$cs),function(i) {
    ix <- unname(fit$sets$cs[[i]])
    if (!length(ix)) return(NULL)
    data.table(comparison_id=comparison_id,config=config,trait=trait,
               credible_set=names(fit$sets$cs)[i],variant_id=variants[ix],PIP=as.numeric(fit$pip[ix]))
  })
  rbindlist(rows,fill=TRUE)
}

configs <- data.table(
  config=c("PF10_L5","PF10_L10","PF10_L20","PF50_L10"),
  mode=c("PF10","PF10","PF10","PF50"),
  L=c(5L,10L,20L,10L)
)

gj <- read_gjoka(locus)
bridge <- fread(bridge_path)[locus_index==locus,
  .(variant_id,rsid,position_GRCh37=as.integer(position_GRCh37),BIM_A1=toupper(BIM_A1),BIM_A2=toupper(BIM_A2))]
if (bridge[,anyDuplicated(variant_id)]) stop("duplicate bridge variant IDs")

ld_cache <- new.env(parent=emptyenv())
disease_fit_cache <- new.env(parent=emptyenv())
diagnostic_cache <- new.env(parent=emptyenv())
completed <- 0L
failed <- 0L
started <- Sys.time()

for (ii in seq_len(nrow(work))) {
  job <- work[ii]
  cid <- as.character(job$comparison_id)
  state_path <- file.path(out,paste0(cid,"_state.json"))
  if (file.exists(state_path)) {
    old <- tryCatch(fromJSON(state_path),error=function(e) NULL)
    if (!is.null(old) && identical(old$status,"COMPLETE")) {
      completed <- completed+1L
      message("RESUME_SKIP ",ii,"/",nrow(work)," ",cid)
      next
    }
  }
  message("START ",ii,"/",nrow(work)," ",cid," ",job$gene,"/",job$cell_type)
  comparison_started <- Sys.time()
  tryCatch({
    block_dir <- file.path(ldbase,sprintf("L%02d_%s",locus,job$cell_type))
    vars <- fread(file.path(block_dir,"variants.tsv.gz"))
    setorder(vars,block_order_zero_based)
    if (vars[,anyDuplicated(variant_id)]) stop("duplicate source-LD variant IDs")
    map <- merge(vars[,.(variant_id,pos=as.integer(position_GRCh37),A1=toupper(BIM_A1),A2=toupper(BIM_A2))],
                 bridge,by="variant_id")
    map <- map[A1==BIM_A1 & A2==BIM_A2 & pos==position_GRCh37]
    map <- merge(map,gj$s[,.(rsid=SNP,BP,z,row_idx)],by="rsid")
    map <- map[pos==BP & is.finite(z)]
    map <- map[!duplicated(variant_id)]

    coloc_rows <- list()
    fit_rows <- list()
    cs_rows <- list()
    rr <- 1L; ff <- 1L; ccounter <- 1L
    for (ci in seq_len(nrow(configs))) {
      cfg <- configs[ci]
      qfile <- file.path(qbase,paste0(cid,"_",cfg$mode,"_QTL.tsv.gz"))
      if (!file.exists(qfile)) stop("missing QTL summary: ",qfile)
      qdat <- fread(qfile)
      qdat <- qdat[match(vars$variant_id,variant_id),nomatch=NULL]
      if (!nrow(qdat)) stop("QTL and block have no common variants")
      common <- intersect(qdat$variant_id,map$variant_id)
      if (length(common)<200) stop("GJOKA/QTL common variants below 200: ",length(common))
      qi <- match(common,qdat$variant_id)
      vi <- match(common,vars$variant_id)
      mi <- match(common,map$variant_id)
      si <- map$row_idx[mi]
      if (anyNA(qi)||anyNA(vi)||anyNA(mi)||anyNA(si)) stop("variant mapping produced NA")

      dld <- gj$R[si,si,drop=FALSE]
      dld <- (dld+t(dld))/2; diag(dld) <- 1
      ldkey <- paste(job$cell_type,cfg$mode,sep="|")
      if (!exists(ldkey,envir=ld_cache,inherits=FALSE)) {
        full <- read_binary_ld(file.path(block_dir,paste0(cfg$mode,"_residualized_A1_correlation.float32.bin")),nrow(vars))
        assign(ldkey,full,envir=ld_cache)
      }
      qld <- get(ldkey,envir=ld_cache,inherits=FALSE)[vi,vi,drop=FALSE]
      qld <- (qld+t(qld))/2; diag(qld) <- 1
      dimnames(dld) <- list(common,common)
      dimnames(qld) <- list(common,common)
      zD <- map$z[mi]; names(zD) <- common
      zQ <- qdat$z[qi]; names(zQ) <- common
      if (any(!is.finite(zD))||any(!is.finite(zQ))) stop("non-finite z score")
      nQ <- as.integer(qdat$n_expression_donors[qi[1]])

      dcachekey <- paste(cfg$L,paste(si,collapse=","),sep="|")
      if (exists(dcachekey,envir=disease_fit_cache,inherits=FALSE)) {
        fitD <- get(dcachekey,envir=disease_fit_cache,inherits=FALSE)
      } else {
        fitD <- susie_rss(z=zD,R=dld,n=24510,L=cfg$L,
                          estimate_residual_variance=FALSE,estimate_prior_variance=TRUE,
                          max_iter=2000,tol=1e-4,verbose=FALSE)
        assign(dcachekey,fitD,envir=disease_fit_cache)
      }
      fitQ <- susie_rss(z=zQ,R=qld,n=nQ,L=cfg$L,
                        estimate_residual_variance=FALSE,estimate_prior_variance=TRUE,
                        max_iter=2000,tol=1e-4,verbose=FALSE)
      dcs <- cs_diag(fitD,dld); qcs <- cs_diag(fitQ,qld)
      ddiagkey <- paste0("D|",paste(si,collapse=","))
      if (exists(ddiagkey,envir=diagnostic_cache,inherits=FALSE)) {
        ddiag <- get(ddiagkey,envir=diagnostic_cache,inherits=FALSE)
      } else {
        ds0 <- safe_s_rss(zD,dld,24510)
        ddiag <- list(s=ds0,k=safe_kriging(zD,dld,24510,ds0))
        assign(ddiagkey,ddiag,envir=diagnostic_cache)
      }
      qdiagkey <- paste0("Q|",cid,"|",cfg$mode)
      if (exists(qdiagkey,envir=diagnostic_cache,inherits=FALSE)) {
        qdiag <- get(qdiagkey,envir=diagnostic_cache,inherits=FALSE)
      } else {
        qs0 <- safe_s_rss(zQ,qld,nQ)
        qdiag <- list(s=qs0,k=safe_kriging(zQ,qld,nQ,qs0))
        assign(qdiagkey,qdiag,envir=diagnostic_cache)
      }
      ds <- ddiag$s; dk <- ddiag$k; qs <- qdiag$s; qk <- qdiag$k
      fit_rows[[ff]] <- data.table(
        comparison_id=cid,locus_index=locus,gene=job$gene,cell_type=job$cell_type,
        R7B1B_v2_role=job$R7B1B_v2_role,config=cfg$config,mode=cfg$mode,L=cfg$L,
        qtl_N=nQ,common_variants=length(common),
        disease_converged=isTRUE(fitD$converged),qtl_converged=isTRUE(fitQ$converged),
        disease_cs=dcs$count,qtl_cs=qcs$count,
        disease_cs_min_min_abs_corr=dcs$min_min_abs_corr,qtl_cs_min_min_abs_corr=qcs$min_min_abs_corr,
        disease_cs_min_median_abs_corr=dcs$min_median_abs_corr,qtl_cs_min_median_abs_corr=qcs$min_median_abs_corr,
        disease_s_rss=ds,qtl_s_rss=qs,disease_kriging_n=dk$flag_n,qtl_kriging_n=qk$flag_n,
        disease_kriging_max_logLR=dk$max_logLR,qtl_kriging_max_logLR=qk$max_logLR
      )
      ff <- ff+1L
      cs_rows[[ccounter]] <- cs_members(fitD,"PBC",cid,cfg$config,common); ccounter <- ccounter+1L
      cs_rows[[ccounter]] <- cs_members(fitQ,"OneK_QTL",cid,cfg$config,common); ccounter <- ccounter+1L

      for (p12 in c(1e-6,1e-5,1e-4)) {
        co <- coloc.susie(fitD,fitQ,p1=1e-4,p2=1e-4,p12=p12)
        s <- as.data.table(co$summary)
        if (nrow(s)) {
          s[,`:=`(comparison_id=cid,locus_index=locus,gene=job$gene,cell_type=job$cell_type,
                  R7B1B_v2_role=job$R7B1B_v2_role,config=cfg$config,mode=cfg$mode,L=cfg$L,
                  p12=p12,qtl_N=nQ,common_variants=length(common))]
          s[,H3_plus_H4:=PP.H3.abf+PP.H4.abf]
          s[,H4_over_H3H4:=PP.H4.abf/(PP.H3.abf+PP.H4.abf)]
          coloc_rows[[rr]] <- s; rr <- rr+1L
        }
      }
    }
    CR <- if (length(coloc_rows)) rbindlist(coloc_rows,fill=TRUE) else data.table()
    FR <- rbindlist(fit_rows,fill=TRUE)
    CSR <- rbindlist(cs_rows,fill=TRUE)
    coloc_path <- file.path(out,paste0(cid,"_coloc_susie.tsv.gz"))
    fit_path <- file.path(out,paste0(cid,"_fit_QC.tsv"))
    cs_path <- file.path(out,paste0(cid,"_credible_set_members.tsv.gz"))
    fwrite(CR,coloc_path,sep="\t")
    fwrite(FR,fit_path,sep="\t")
    fwrite(CSR,cs_path,sep="\t")
    state <- list(
      schema="R7B1B_V2_COMPARISON_1.0",status="COMPLETE",comparison_id=cid,
      locus_index=locus,gene=as.character(job$gene),cell_type=as.character(job$cell_type),
      role=as.character(job$R7B1B_v2_role),configs=nrow(configs),coloc_rows=nrow(CR),
      common_variants_min=min(FR$common_variants),common_variants_max=max(FR$common_variants),
      all_fits_converged=all(FR$disease_converged&FR$qtl_converged),
      output_bytes=list(coloc=file.info(coloc_path)$size,fit=file.info(fit_path)$size,credible_sets=file.info(cs_path)$size),
      runtime_seconds=as.numeric(difftime(Sys.time(),comparison_started,units="secs"))
    )
    write_json(state,state_path,pretty=TRUE,auto_unbox=TRUE)
    completed <- completed+1L
  },error=function(e) {
    failed <<- failed+1L
    state <- list(schema="R7B1B_V2_COMPARISON_1.0",status="QC_FAILURE",comparison_id=cid,
                  locus_index=locus,gene=as.character(job$gene),cell_type=as.character(job$cell_type),
                  role=as.character(job$R7B1B_v2_role),error=conditionMessage(e),
                  runtime_seconds=as.numeric(difftime(Sys.time(),comparison_started,units="secs")))
    write_json(state,state_path,pretty=TRUE,auto_unbox=TRUE)
    message("QC_FAILURE ",cid," ",conditionMessage(e))
  })
  gc(verbose=FALSE)
}

locus_state <- list(
  schema="R7B1B_V2_LOCUS_1.0",
  status=if (failed==0L) "COMPLETE" else "COMPLETE_WITH_QC_FAILURES",
  locus_index=locus,expected_comparisons=nrow(work),complete=completed,qc_failures=failed,
  R=R.version.string,susieR=as.character(packageVersion("susieR")),coloc=as.character(packageVersion("coloc")),
  gjoka_z_rounding_max_delta=gj$z_rounding_max_delta,
  gjoka_z_rounding_correlation=gj$z_rounding_correlation,
  runtime_seconds=as.numeric(difftime(Sys.time(),started,units="secs"))
)
write_json(locus_state,file.path(out,"locus_state.json"),pretty=TRUE,auto_unbox=TRUE)
print(locus_state)
