#!/usr/bin/env Rscript
root<-Sys.getenv("IGAN_PROJECT_ROOT",unset=getwd())
local_lib<-file.path(root,"tools/R-library")
if(dir.exists(local_lib)) .libPaths(c(normalizePath(local_lib,winslash="/"),.libPaths()))
suppressPackageStartupMessages({library(susieR);library(coloc);library(data.table);library(jsonlite)})
idir<-file.path(root,"3_results/04_integration/R6A2C/sourceLD/REEP3_REEP3_CD4_NC"); out<-file.path(root,"3_results/04_integration/R6A2C/multisignal"); dir.create(out,recursive=TRUE,showWarnings=FALSE)
q<-fread(file.path(root,"3_results/03_qtl/R6A2B0/R6A2B0_OneK1K_8locus_QTL.tsv.gz"))[locus=="REEP3" & gene=="REEP3" & cell_type=="CD4_NC"]
v<-fread(file.path(idir,"LD_variants.tsv")); setorder(v,LD_order_zero_based); q<-q[match(v$variant_id,q$variant_id)]
if(anyNA(q$variant_id)||!all(q$variant_id==v$variant_id)) stop("QTL/LD order mismatch")
N<-unique(q$n_expression_donors); if(length(N)!=1L||N!=980L) stop("unexpected QTL N")
z<-q$slope_A1/q$slope_se
readR<-function(mode){
 p<-nrow(v); con<-file(file.path(idir,paste0(mode,"_residualized_A1_correlation.float32.bin")),"rb"); on.exit(close(con)); x<-readBin(con,what=numeric(),n=p*p,size=4L,endian="little"); if(length(x)!=p*p)stop("LD length mismatch")
 R<-matrix(x,nrow=p,ncol=p,byrow=TRUE); R<-(R+t(R))/2; diag(R)<-1; ridge<-1e-4; (R+diag(ridge,p))/(1+ridge)
}
configs<-data.table(config=c("PF10_L5","PF10_L10","PF10_L20","PF50_L10"),ld_mode=c("PF10","PF10","PF10","PF50"),L=c(5L,10L,20L,10L))
diseases<-c("asian","combined","european")
summary_rows<-list(); cs_rows<-list(); coloc_rows<-list(); comp_rows<-list()
for(ii in seq_len(nrow(configs))){
 cfg<-configs[ii]; R<-readR(cfg$ld_mode); warns<-character(); fit<-withCallingHandlers(susie_rss(z=z,R=R,n=980,L=cfg$L,estimate_residual_variance=FALSE,estimate_prior_variance=TRUE,check_prior=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE),warning=function(w){warns<<-c(warns,conditionMessage(w));invokeRestart("muffleWarning")})
 saveRDS(fit,file.path(out,paste0("REEP3_CD4_NC_",cfg$config,".susie_fit.rds")),compress="xz")
 pip<-susie_get_pip(fit,prune_by_cs=FALSE); cs<-susie_get_cs(fit,Xcorr=R,coverage=0.95,min_abs_corr=0.5,check_symmetric=TRUE); cslist<-if(is.null(cs$cs))list()else cs$cs; csidx<-if(is.null(cs$cs_index))integer()else cs$cs_index
 lead_idx<-match("10:65363048",v$variant_id); smoke_idx<-match("10:65376395",v$variant_id)
 summary_rows[[length(summary_rows)+1L]]<-data.table(config=cfg$config,ld_mode=cfg$ld_mode,L=cfg$L,n=980,variants=nrow(v),converged=isTRUE(fit$converged),niter=fit$niter,credible_sets_95=length(cslist),max_PIP_variant=v$variant_id[which.max(pip)],max_PIP=max(pip),disease_lead_PIP=ifelse(is.na(lead_idx),NA_real_,pip[lead_idx]),smoke_shared_top_PIP=ifelse(is.na(smoke_idx),NA_real_,pip[smoke_idx]),warning_count=length(unique(warns)))
 for(l in seq_len(nrow(fit$alpha))){j<-which.max(fit$alpha[l,]);comp_rows[[length(comp_rows)+1L]]<-data.table(config=cfg$config,component=l,prior_variance=fit$V[l],top_variant=v$variant_id[j],top_alpha=fit$alpha[l,j],is_credible_component=l%in%csidx)}
 if(length(cslist)) for(csname in names(cslist)){
   members<-cslist[[csname]]; component<-as.integer(sub("L","",csname)); purity<-if(!is.null(cs$purity)&&csname%in%rownames(cs$purity))cs$purity[csname,] else rep(NA_real_,3)
   for(j in members) cs_rows[[length(cs_rows)+1L]]<-data.table(config=cfg$config,credible_set=csname,component=component,variant_id=v$variant_id[j],alpha=fit$alpha[component,j],PIP=pip[j],marginal_p=q$pval_nominal[j],min_abs_corr=purity[[1]],mean_abs_corr=purity[[2]],median_abs_corr=purity[[3]],is_disease_lead=v$variant_id[j]=="10:65363048",is_smoke_shared_top=v$variant_id[j]=="10:65376395")
   for(ds in diseases){
     gp<-file.path(root,"3_results/01_gwas/R6A2B0",paste0(ds,"_REEP3_GRCh37_1Mb_A1.tsv.gz")); g<-fread(gp); common<-intersect(v$variant_id,g$variant_id); gg<-g[match(common,variant_id)]
     gd<-coloc:::approx.bf.estimates(gg$beta_A1/gg$standard_error,gg$standard_error^2,"cc")$lABF; names(gd)<-common; qbf<-fit$lbf_variable[component,match(common,v$variant_id)]; names(qbf)<-common
     topv<-v$variant_id[which.max(fit$alpha[component,])]; qi<-match(topv,q$variant_id); gi<-match(topv,gg$variant_id)
     for(p12 in c(1e-6,1e-5,1e-4)){
       cc<-coloc:::coloc.bf_bf(c(gd,null=0),c(qbf,null=0),p1=1e-4,p2=1e-4,p12=p12,overlap.min=0,trim_by_posterior=FALSE)$summary[1]
       coloc_rows[[length(coloc_rows)+1L]]<-data.table(dataset=ds,config=cfg$config,credible_set=csname,component=component,p12=p12,nsnps=cc$nsnps,PP_H0=cc$PP.H0.abf,PP_H1=cc$PP.H1.abf,PP_H2=cc$PP.H2.abf,PP_H3=cc$PP.H3.abf,PP_H4=cc$PP.H4.abf,H4_over_H3H4=cc$PP.H4.abf/(cc$PP.H3.abf+cc$PP.H4.abf),qtl_component_top=topv,qtl_top_beta=ifelse(is.na(qi),NA_real_,q$slope_A1[qi]),disease_top_beta_A1=ifelse(is.na(gi),NA_real_,gg$beta_A1[gi]))
     }
   }
 }
 rm(R,fit,pip,cs);gc()
}
summ<-rbindlist(summary_rows,fill=TRUE); comps<-rbindlist(comp_rows,fill=TRUE); css<-if(length(cs_rows))rbindlist(cs_rows,fill=TRUE)else data.table(); cols<-if(length(coloc_rows))rbindlist(coloc_rows,fill=TRUE)else data.table()
fwrite(summ,file.path(out,"R6A2C_susie_summary.tsv"),sep="\t");fwrite(comps,file.path(out,"R6A2C_susie_components.tsv"),sep="\t");fwrite(css,file.path(out,"R6A2C_susie_credible_sets.tsv"),sep="\t");fwrite(cols,file.path(out,"R6A2C_signal_coloc.tsv"),sep="\t")
write_json(list(R=R.version.string,susieR=as.character(packageVersion("susieR")),coloc=as.character(packageVersion("coloc")),fits=nrow(summ),credible_set_rows=nrow(css),signal_coloc_rows=nrow(cols)),file.path(out,"R6A2C_multisignal_run.json"),pretty=TRUE,auto_unbox=TRUE)
cat(toJSON(list(fits=nrow(summ),credible_set_rows=nrow(css),signal_coloc_rows=nrow(cols)),auto_unbox=TRUE),"\n")
