#!/usr/bin/env Rscript
## Replay the R7B1B kriging diagnostics for one frozen locus without refitting SuSiE.

root <- Sys.getenv("R7_PROJECT_ROOT", unset="H:/SCI2/YR1")
.libPaths(c(file.path(root,"tools","R-library"), .libPaths()))
suppressPackageStartupMessages({ library(susieR); library(data.table); library(jsonlite); library(digest) })

locus <- as.integer(Sys.getenv("R7B1E0_LOCUS", unset=""))
if (!is.finite(locus)) stop("R7B1E0_LOCUS is required")

work_path <- file.path(root,"3_results","00_audit","R7B1B_v2","R7B1B_v2_exact_642_high_information_comparisons.tsv")
qbase <- file.path(root,"3_results","03_qtl","R7B1B_v2","dualmodel_qtl")
ldbase <- file.path(root,"3_results","04_integration","R7B1B_v2","sourceLD_blocks")
gjbase <- file.path(root,"1_data","study_inputs","PBC_GJOKA","R7B1B_v2")
bridge_path <- file.path(root,"3_results","01_gwas","R7B1","R7B1_PBC56_GRCh37_BIM_A1.tsv.gz")
fitbase <- file.path(root,"3_results","04_integration","R7B1B_v2","multisignal")
outbase <- file.path(root,"3_results","04_integration","R7B1E0","kriging_replay")
out <- file.path(outbase,sprintf("locus_%02d",locus))
dir.create(out,recursive=TRUE,showWarnings=FALSE)

work <- fread(work_path)[locus_index==locus]
if (!nrow(work)) stop("no frozen rows for locus ",locus)
setorder(work,comparison_id)

read_gjoka <- function(idx) {
  s <- fread(file.path(gjbase,paste0("sumstats_",idx,".assoc.logistic")))
  if ("TEST" %in% names(s)) s <- s[TEST=="ADD"]
  R <- fread(file.path(gjbase,paste0("covmat_",idx,".ld")),header=FALSE,showProgress=FALSE) |> as.matrix()
  if (nrow(R)!=nrow(s) || ncol(R)!=nrow(s)) stop("GJOKA dimension mismatch")
  s[,row_idx:=.I]
  s[,`:=`(BP=as.integer(BP),z=as.numeric(STAT))]
  R <- (R+t(R))/2; diag(R) <- 1
  list(s=s,R=R)
}

read_binary_ld <- function(path,n) {
  con <- file(path,"rb"); on.exit(close(con))
  x <- readBin(con,what="numeric",n=n*n,size=4,endian="little")
  if (length(x)!=n*n) stop("binary LD length mismatch")
  R <- t(matrix(x,nrow=n,ncol=n)); R <- (R+t(R))/2; diag(R) <- 1; R
}

replay_one <- function(z,R,n,s,variants,comparison_id,mode,trait) {
  started <- Sys.time()
  raw <- tryCatch(susieR::kriging_rss(z,R,n,s=s),error=function(e)e)
  ans <- list(comparison_id=comparison_id,locus_index=locus,mode=mode,trait=trait,
              n=as.integer(n),s_rss=as.numeric(s),variants_expected=length(variants),
              status="DIAGNOSTIC_NOT_EVALUATED",error="",variants_returned=NA_integer_,
              finite_rows=NA_integer_,historical_logLR_gt2_n=NA_integer_,
              official_logLR_gt2_absz_gt2_n=NA_integer_,max_logLR=NA_real_,
              max_abs_z=NA_real_,max_abs_z_std_diff=NA_real_,runtime_seconds=NA_real_)
  flags <- NULL
  if (inherits(raw,"error")) {
    ans$error <- conditionMessage(raw)
  } else {
    d <- if (is.list(raw) && is.data.frame(raw$conditional_dist)) raw$conditional_dist else
         if (is.data.frame(raw)) raw else NULL
    required <- c("z","condmean","condvar","z_std_diff","logLR")
    if (is.null(d)) ans$error <- "NO_CONDITIONAL_DIST_DATA_FRAME"
    else if (!all(required %in% names(d))) ans$error <- paste0("MISSING_FIELDS:",paste(setdiff(required,names(d)),collapse=","))
    else if (nrow(d)!=length(variants)) ans$error <- paste0("ROW_COUNT_MISMATCH:",nrow(d),"!=",length(variants))
    else {
      d <- as.data.table(d); d[,variant_id:=variants]
      finite <- apply(as.matrix(d[,..required]),1,function(x) all(is.finite(x)))
      ans$variants_returned <- nrow(d); ans$finite_rows <- sum(finite)
      if (!all(finite)) ans$error <- paste0("NONFINITE_ROWS:",sum(!finite))
      else {
        historical <- d$logLR>2
        official <- historical & abs(d$z)>2
        ans$status <- "PASS"
        ans$historical_logLR_gt2_n <- sum(historical)
        ans$official_logLR_gt2_absz_gt2_n <- sum(official)
        ans$max_logLR <- max(d$logLR)
        ans$max_abs_z <- max(abs(d$z))
        ans$max_abs_z_std_diff <- max(abs(d$z_std_diff))
        keep <- historical | frank(-d$logLR,ties.method="first")<=3L
        flags <- d[keep,.(comparison_id=comparison_id,locus_index=locus,mode=mode,trait=trait,
                          variant_id,z,condmean,condvar,z_std_diff,logLR,
                          historical_flag=logLR>2,official_flag=logLR>2&abs(z)>2)]
      }
    }
  }
  ans$runtime_seconds <- as.numeric(difftime(Sys.time(),started,units="secs"))
  list(summary=as.data.table(ans),flags=flags)
}

gj <- read_gjoka(locus)
bridge <- fread(bridge_path)[locus_index==locus,
  .(variant_id,rsid,position_GRCh37=as.integer(position_GRCh37),BIM_A1=toupper(BIM_A1),BIM_A2=toupper(BIM_A2))]
if (bridge[,anyDuplicated(variant_id)]) stop("duplicate bridge IDs")

ld_cache <- new.env(parent=emptyenv())
disease_cache <- new.env(parent=emptyenv())
summaries <- list(); flag_rows <- list(); ss <- 1L; ff <- 1L

for (ii in seq_len(nrow(work))) {
  job <- work[ii]; cid <- as.character(job$comparison_id)
  block_dir <- file.path(ldbase,sprintf("L%02d_%s",locus,job$cell_type))
  vars <- fread(file.path(block_dir,"variants.tsv.gz")); setorder(vars,block_order_zero_based)
  map <- merge(vars[,.(variant_id,pos=as.integer(position_GRCh37),A1=toupper(BIM_A1),A2=toupper(BIM_A2))],bridge,by="variant_id")
  map <- map[A1==BIM_A1&A2==BIM_A2&pos==position_GRCh37]
  map <- merge(map,gj$s[,.(rsid=SNP,BP,z,row_idx)],by="rsid")
  map <- map[pos==BP&is.finite(z)]; map <- map[!duplicated(variant_id)]
  fit_path <- file.path(fitbase,sprintf("locus_%02d",locus),paste0(cid,"_fit_QC.tsv"))
  frozen_fit <- fread(fit_path)

  for (mode in c("PF10","PF50")) {
    cfg <- if (mode=="PF10") "PF10_L10" else "PF50_L10"
    qdat <- fread(file.path(qbase,paste0(cid,"_",mode,"_QTL.tsv.gz")))
    qdat <- qdat[match(vars$variant_id,variant_id),nomatch=NULL]
    common <- intersect(qdat$variant_id,map$variant_id)
    qi <- match(common,qdat$variant_id); vi <- match(common,vars$variant_id); mi <- match(common,map$variant_id); si <- map$row_idx[mi]
    if (anyNA(qi)||anyNA(vi)||anyNA(mi)||anyNA(si)||length(common)<200) stop("mapping failure: ",cid,"/",mode)
    nQ <- as.integer(qdat$n_expression_donors[qi[1]])
    zD <- map$z[mi]; names(zD) <- common; zQ <- qdat$z[qi]; names(zQ) <- common
    dld <- gj$R[si,si,drop=FALSE]; dld <- (dld+t(dld))/2; diag(dld)<-1
    ldkey <- paste(job$cell_type,mode,sep="|")
    if (!exists(ldkey,envir=ld_cache,inherits=FALSE))
      assign(ldkey,read_binary_ld(file.path(block_dir,paste0(mode,"_residualized_A1_correlation.float32.bin")),nrow(vars)),envir=ld_cache)
    qld <- get(ldkey,envir=ld_cache,inherits=FALSE)[vi,vi,drop=FALSE]; qld <- (qld+t(qld))/2; diag(qld)<-1
    frozen <- frozen_fit[config==cfg]
    if (nrow(frozen)!=1 || frozen$common_variants!=length(common)) stop("frozen fit identity mismatch: ",cid,"/",mode)

    dkey <- digest(list(mode=mode,variants=common,s=as.numeric(frozen$disease_s_rss)),algo="sha256")
    if (exists(dkey,envir=disease_cache,inherits=FALSE)) {
      dr <- get(dkey,envir=disease_cache,inherits=FALSE)
      dr$summary <- copy(dr$summary); dr$summary[,comparison_id:=cid]
      if (!is.null(dr$flags)) { dr$flags <- copy(dr$flags); dr$flags[,comparison_id:=cid] }
    } else {
      dr <- replay_one(zD,dld,24510,frozen$disease_s_rss,common,cid,mode,"PBC")
      assign(dkey,dr,envir=disease_cache)
    }
    qr <- replay_one(zQ,qld,nQ,frozen$qtl_s_rss,common,cid,mode,"OneK_QTL")
    for (res in list(dr,qr)) {
      summaries[[ss]] <- res$summary; ss <- ss+1L
      if (!is.null(res$flags)) { flag_rows[[ff]] <- res$flags; ff <- ff+1L }
    }
  }
  message("R7B1E0 ",ii,"/",nrow(work)," ",cid)
}

summary <- rbindlist(summaries,fill=TRUE)
flags <- rbindlist(flag_rows,fill=TRUE)
fwrite(summary,file.path(out,"diagnostic_summary.tsv"),sep="\t")
fwrite(flags,file.path(out,"diagnostic_flagged_and_top3.tsv.gz"),sep="\t")
state <- list(schema="R7B1E0_KRIGING_LOCUS_1.0",status=if(all(summary$status=="PASS"))"PASS" else "HOLD",
              locus_index=locus,comparisons=nrow(work),diagnostic_units=nrow(summary),
              diagnostic_pass=sum(summary$status=="PASS"),diagnostic_hold=sum(summary$status!="PASS"),
              historical_flags=sum(summary$historical_logLR_gt2_n,na.rm=TRUE),
              official_flags=sum(summary$official_logLR_gt2_absz_gt2_n,na.rm=TRUE),
              R=R.version.string,susieR=as.character(packageVersion("susieR")))
write_json(state,file.path(out,"locus_state.json"),pretty=TRUE,auto_unbox=TRUE)
print(state)
