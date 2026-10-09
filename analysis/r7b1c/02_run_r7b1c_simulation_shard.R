#!/usr/bin/env Rscript
## R7B1C truth-known simulation worker. Each grid row is checkpointed.

root <- Sys.getenv("R7_PROJECT_ROOT", unset="H:/SCI2/YR1")
.libPaths(c(file.path(root,"tools","R-library"),.libPaths()))
suppressPackageStartupMessages({library(data.table);library(susieR);library(coloc);library(jsonlite)})

grid_path <- file.path(root,"3_results","00_audit","R7B1C","R7B1C_implementation_grid_486.tsv")
causal_path <- file.path(root,"3_results","00_audit","R7B1C","templates","R7B1C_causal_index_map.tsv")
template_base <- file.path(root,"3_results","00_audit","R7B1C","templates")
outdir <- Sys.getenv("R7B1C_OUTDIR",unset=file.path(root,"3_results","05_simulation","R7B1C","full"))
grid_ids_text <- Sys.getenv("R7B1C_GRID_IDS",unset="")
override_text <- Sys.getenv("R7B1C_REPS_OVERRIDE",unset="")
if (!nzchar(grid_ids_text)) stop("R7B1C_GRID_IDS is required")
dir.create(outdir,recursive=TRUE,showWarnings=FALSE)

grid <- fread(grid_path)
causal <- fread(causal_path)
requested <- strsplit(grid_ids_text,",",fixed=TRUE)[[1]]
work <- grid[grid_id %in% requested]
if (nrow(work)!=length(unique(requested))) stop("requested grid IDs were not uniquely resolved")
setorder(work,grid_id)
override <- if (nzchar(override_text)) as.integer(override_text) else NA_integer_

read_matrix <- function(path,n=128L) {
  con <- file(path,"rb"); on.exit(close(con))
  x <- readBin(con,what="numeric",n=n*n,size=8,endian="little")
  if (length(x)!=n*n) stop("matrix length mismatch: ",path)
  R <- t(matrix(x,nrow=n,ncol=n))
  R <- (R+t(R))/2; diag(R) <- 1
  R
}

template_ids <- c("T_L02_NK_PF10","T_L04_B_IN_PF10")
templates <- list()
for (tid in template_ids) {
  td <- file.path(template_base,tid)
  D <- read_matrix(file.path(td,"disease_ld.float64.bin"))
  Q <- read_matrix(file.path(td,"qtl_ld.float64.bin"))
  Qm <- read_matrix(file.path(td,"qtl_ld_mismatch_PF50.float64.bin"))
  variant_names <- sprintf("v%03d",seq_len(nrow(D)))
  dimnames(D) <- list(variant_names,variant_names)
  dimnames(Q) <- list(variant_names,variant_names)
  dimnames(Qm) <- list(variant_names,variant_names)
  templates[[tid]] <- list(D=D,Q=Q,Qm=Qm,cholD=chol(D),cholQ=chol(Q))
}

logsumexp <- function(x) {
  m <- max(x)
  if (!is.finite(m)) return(m)
  m + log(sum(exp(x-m)))
}
logdiff <- function(a,b) {
  if (!is.finite(a) || b>=a) return(-Inf)
  a + log1p(-exp(b-a))
}
log_abf_z <- function(z,se,prior_sd) {
  variance <- se^2
  r <- prior_sd^2/(prior_sd^2+variance)
  0.5*(log1p(-r)+r*z^2)
}
abf_post <- function(z1,z2,se1,se2,p12) {
  l1 <- log_abf_z(z1,se1,0.2)
  l2 <- log_abf_z(z2,se2,0.15)
  a1 <- logsumexp(l1); a2 <- logsumexp(l2); a12 <- logsumexp(l1+l2)
  lh <- c(0,log(1e-4)+a1,log(1e-4)+a2,
          log(1e-4)+log(1e-4)+logdiff(a1+a2,a12),log(p12)+a12)
  pp <- exp(lh-logsumexp(lh))
  ratio <- if ((pp[4]+pp[5])>0) pp[5]/(pp[4]+pp[5]) else NA_real_
  state <- if (is.finite(pp[5]) && pp[5]>=.8 && ratio>=.8) "H4" else
    if (is.finite(pp[4]) && pp[4]>=.8 && ratio<=.2) "H3" else "UNINFORMATIVE"
  list(h3=pp[4],h4=pp[5],ratio=ratio,state=state)
}

cs_metrics <- function(fit,truth) {
  cs <- fit$sets$cs
  if (is.null(cs) || !length(cs))
    return(list(count=0L,size=0L,any=FALSE,all=FALSE,per_causal=0))
  members <- unique(unlist(cs,use.names=FALSE))
  hit <- truth %in% members
  list(count=length(cs),size=length(members),any=any(hit),all=all(hit),per_causal=mean(hit))
}

multi_fit <- function(zD,zQ,RD,RQ,nD,nQ,L,p12,truthD,truthQ) {
  ans <- list(ok=FALSE,converged=FALSE,state="QC_FAILURE",best_h4=NA_real_,best_ratio=NA_real_,
              best_h3=NA_real_,pairs=0L,d_cs=NA_integer_,q_cs=NA_integer_,
              d_cs_size=NA_integer_,q_cs_size=NA_integer_,d_cover_any=NA,q_cover_any=NA,
              d_cover_all=NA,q_cover_all=NA,d_cover_per=NA_real_,q_cover_per=NA_real_,error=NA_character_)
  tryCatch({
    names(zD) <- colnames(RD); names(zQ) <- colnames(RQ)
    fitD <- suppressWarnings(susie_rss(z=zD,R=RD,n=nD,L=L,
      estimate_residual_variance=FALSE,estimate_prior_variance=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE))
    fitQ <- suppressWarnings(susie_rss(z=zQ,R=RQ,n=nQ,L=L,
      estimate_residual_variance=FALSE,estimate_prior_variance=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE))
    dm <- cs_metrics(fitD,truthD); qm <- cs_metrics(fitQ,truthQ)
    co <- tryCatch(suppressWarnings(coloc.susie(fitD,fitQ,p1=1e-4,p2=1e-4,p12=p12)),error=function(e) NULL)
    ss <- if (is.null(co)) data.table() else as.data.table(co$summary)
    if (nrow(ss)) {
      ss[,ratio:=PP.H4.abf/(PP.H3.abf+PP.H4.abf)]
      h4pass <- ss$PP.H4.abf>=.8 & ss$ratio>=.8
      h3pass <- ss$PP.H3.abf>=.8 & ss$ratio<=.2
      state <- if (any(h4pass,na.rm=TRUE)) "H4" else if (any(h3pass,na.rm=TRUE)) "H3" else "UNINFORMATIVE"
      best_i <- which.max(ss$PP.H4.abf)
      ans$best_h4 <- ss$PP.H4.abf[best_i]
      ans$best_ratio <- ss$ratio[best_i]
      ans$best_h3 <- max(ss$PP.H3.abf,na.rm=TRUE)
      ans$pairs <- nrow(ss); ans$state <- state
    } else ans$state <- "UNINFORMATIVE"
    ans$ok <- TRUE; ans$converged <- isTRUE(fitD$converged) && isTRUE(fitQ$converged)
    ans$d_cs <- dm$count; ans$q_cs <- qm$count; ans$d_cs_size <- dm$size; ans$q_cs_size <- qm$size
    ans$d_cover_any <- dm$any; ans$q_cover_any <- qm$any; ans$d_cover_all <- dm$all; ans$q_cover_all <- qm$all
    ans$d_cover_per <- dm$per_causal; ans$q_cover_per <- qm$per_causal
  },error=function(e) ans$error <<- conditionMessage(e))
  ans
}

truth_for <- function(scenario,a,b,c4,c5,d5) {
  if (scenario=="S1_one_shared") return(list(D=c(a),Q=c(a),shared=c(a)))
  if (scenario=="S2_distinct_correlated") return(list(D=c(a),Q=c(b),shared=integer()))
  if (scenario=="S3_disease2_qtl1_partial") return(list(D=c(a,b),Q=c(a),shared=c(a)))
  if (scenario=="S4_two_by_two_one_shared") return(list(D=c(a,b),Q=c(a,c4),shared=c(a)))
  if (scenario=="S5_two_by_two_none_highLD") return(list(D=c(a,b),Q=c(c5,d5),shared=integer()))
  if (scenario=="S6_matched_vs_mismatched_LD") return(list(D=c(a,b),Q=c(a,c4),shared=c(a)))
  stop("unknown scenario ",scenario)
}

started <- Sys.time(); completed <- 0L; failures <- 0L
for (gi in seq_len(nrow(work))) {
  g <- work[gi]
  suffix <- if (is.finite(override)) ".tsv" else ".tsv.gz"
  out_path <- file.path(outdir,paste0(g$grid_id,suffix))
  state_path <- file.path(outdir,paste0(g$grid_id,".state.json"))
  if (file.exists(state_path)) {
    old <- tryCatch(fromJSON(state_path),error=function(e) NULL)
    if (!is.null(old) && identical(old$status,"COMPLETE") && file.exists(out_path)) {
      completed <- completed+1L; message("RESUME_SKIP ",g$grid_id); next
    }
  }
  reps <- if (is.finite(override)) override else as.integer(g$replicates)
  set.seed(as.integer(g$seed))
  rows <- vector("list",reps)
  row_started <- Sys.time()
  for (replicate_index in seq_len(reps)) {
    tid <- template_ids[1L+((replicate_index-1L) %% 2L)] # odd=locus2, even=locus4
    tpl <- templates[[tid]]
    cm <- causal[template_id==tid & abs(causal_r2_target-as.numeric(g$causal_r2))<1e-12]
    if (nrow(cm)!=1) stop("causal map lookup failed")
    a <- as.integer(cm$a)+1L; b <- as.integer(cm$b)+1L; c4 <- as.integer(cm$c_s4)+1L
    c5 <- as.integer(cm$c_s5)+1L; d5 <- as.integer(cm$d_s5)+1L
    truth <- truth_for(g$scenario,a,b,c4,c5,d5)
    maf <- as.numeric(g$maf); allele_sd <- sqrt(2*maf*(1-maf))
    bD <- numeric(128); bQ <- numeric(128)
    d_effects <- c(log(1.12),-0.8*log(1.12)); q_effects <- c(.30,-.8*.30)
    bD[truth$D] <- d_effects[seq_along(truth$D)]*allele_sd
    bQ[truth$Q] <- q_effects[seq_along(truth$Q)]*allele_sd
    muD <- sqrt(as.numeric(g$disease_N))*as.vector(tpl$D%*%bD)
    muQ <- sqrt(as.numeric(g$qtl_N))*as.vector(tpl$Q%*%bQ)
    zD <- muD + as.vector(rnorm(128)%*%tpl$cholD)
    zQ <- muQ + as.vector(rnorm(128)%*%tpl$cholQ)
    seD <- 1/sqrt(as.numeric(g$disease_N)*2*maf*(1-maf))
    seQ <- 1/sqrt(as.numeric(g$qtl_N)*2*maf*(1-maf))
    abf <- abf_post(zD,zQ,seD,seQ,as.numeric(g$p12))
    matched <- multi_fit(zD,zQ,tpl$D,tpl$Q,as.integer(g$disease_N),as.integer(g$qtl_N),
                         as.integer(g$susie_L),as.numeric(g$p12),truth$D,truth$Q)
    mismatch <- NULL
    if (g$scenario=="S6_matched_vs_mismatched_LD")
      mismatch <- multi_fit(zD,zQ,tpl$D,tpl$Qm,as.integer(g$disease_N),as.integer(g$qtl_N),
                            as.integer(g$susie_L),as.numeric(g$p12),truth$D,truth$Q)
    rows[[replicate_index]] <- data.table(
      grid_id=g$grid_id,scenario=g$scenario,replicate=replicate_index,seed=g$seed,template_id=tid,
      maf=maf,causal_r2=g$causal_r2,susie_L=g$susie_L,p12=g$p12,disease_N=g$disease_N,qtl_N=g$qtl_N,
      true_shared=length(truth$shared)>0,truth_D=paste(truth$D-1L,collapse=","),
      truth_Q=paste(truth$Q-1L,collapse=","),truth_shared=paste(truth$shared-1L,collapse=","),
      abf_h3=abf$h3,abf_h4=abf$h4,abf_ratio=abf$ratio,abf_state=abf$state,
      matched_ok=matched$ok,matched_converged=matched$converged,matched_state=matched$state,
      matched_best_h3=matched$best_h3,matched_best_h4=matched$best_h4,matched_best_ratio=matched$best_ratio,
      matched_pairs=matched$pairs,matched_d_cs=matched$d_cs,matched_q_cs=matched$q_cs,
      matched_d_cs_size=matched$d_cs_size,matched_q_cs_size=matched$q_cs_size,
      matched_d_cover_any=matched$d_cover_any,matched_q_cover_any=matched$q_cover_any,
      matched_d_cover_all=matched$d_cover_all,matched_q_cover_all=matched$q_cover_all,
      matched_d_cover_per=matched$d_cover_per,matched_q_cover_per=matched$q_cover_per,
      matched_error=matched$error,
      mismatch_ok=if(is.null(mismatch)) NA else mismatch$ok,
      mismatch_converged=if(is.null(mismatch)) NA else mismatch$converged,
      mismatch_state=if(is.null(mismatch)) NA_character_ else mismatch$state,
      mismatch_best_h3=if(is.null(mismatch)) NA_real_ else mismatch$best_h3,
      mismatch_best_h4=if(is.null(mismatch)) NA_real_ else mismatch$best_h4,
      mismatch_best_ratio=if(is.null(mismatch)) NA_real_ else mismatch$best_ratio,
      mismatch_pairs=if(is.null(mismatch)) NA_integer_ else mismatch$pairs,
      mismatch_d_cover_all=if(is.null(mismatch)) NA else mismatch$d_cover_all,
      mismatch_q_cover_all=if(is.null(mismatch)) NA else mismatch$q_cover_all,
      mismatch_error=if(is.null(mismatch)) NA_character_ else mismatch$error
    )
  }
  result <- rbindlist(rows,fill=TRUE)
  fwrite(result,out_path,sep="\t",na="NA",compress=if(grepl("[.]gz$",out_path)) "gzip" else "none")
  failures_row <- sum(!result$matched_ok) + sum(result$scenario=="S6_matched_vs_mismatched_LD" & !result$mismatch_ok,na.rm=TRUE)
  state <- list(schema="R7B1C_GRID_ROW_1.0",status="COMPLETE",grid_id=g$grid_id,scenario=g$scenario,
                replicates=reps,failed_fits=failures_row,output=basename(out_path),
                runtime_seconds=as.numeric(difftime(Sys.time(),row_started,units="secs")))
  write_json(state,state_path,pretty=TRUE,auto_unbox=TRUE)
  completed <- completed+1L; failures <- failures+failures_row
  message("GRID_DONE ",g$grid_id," ",gi,"/",nrow(work)," reps=",reps," failures=",failures_row)
  gc(verbose=FALSE)
}
worker_state <- list(schema="R7B1C_WORKER_1.0",status="COMPLETE",requested=length(requested),
                     completed=completed,fit_failures=failures,R=R.version.string,
                     susieR=as.character(packageVersion("susieR")),coloc=as.character(packageVersion("coloc")),
                     runtime_seconds=as.numeric(difftime(Sys.time(),started,units="secs")))
print(worker_state)
