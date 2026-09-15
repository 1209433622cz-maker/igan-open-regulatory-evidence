#!/usr/bin/env Rscript
root<-Sys.getenv("R7_PROJECT_ROOT",unset="H:/SCI2/YR1")
.libPaths(c(file.path(root,"tools","R-library"),.libPaths()))
suppressPackageStartupMessages({library(susieR);library(coloc);library(data.table);library(jsonlite)})
out<-file.path(root,"3_results","04_integration","R7A1B","multisignal");dir.create(out,recursive=TRUE,showWarnings=FALSE)
qall<-fread(file.path(root,"3_results","03_qtl","R7A1B","R7A1B_OneK_frozen_QTL.tsv.gz"))
tr<-fread(file.path(root,"3_results","04_integration","R7A1B","R7A1B_multisignal_triggers.tsv"))
gjbase<-file.path(root,"1_data","study_inputs","PBC_GJOKA","R7A1B")
ldbase<-file.path(root,"3_results","04_integration","R7A1B","sourceLD")

read_npy_float32<-function(path){
  # Matrices are additionally exported to TSV by the Python runner before this script.
  fread(path,header=FALSE) |> as.matrix()
}
read_gjoka<-function(idx){
  s<-fread(file.path(gjbase,paste0("sumstats_",idx,".assoc.logistic")))
  if("TEST"%in%names(s)) s<-s[TEST=="ADD"]
  R<-fread(file.path(gjbase,paste0("covmat_",idx,".ld")),header=FALSE) |> as.matrix()
  if(nrow(R)!=nrow(s)||ncol(R)!=nrow(s)) stop("GJOKA matrix dimension mismatch locus ",idx)
  required<-c("SNP","BP","A1","BETA","SE","STAT")
  missing<-setdiff(required,names(s))
  if(length(missing)) stop("GJOKA summary missing required columns: ",paste(missing,collapse=","))
  # GJOKA PLINK2 logistic files already contain additive log-odds BETA and SE.
  # Preserve their original row indices because the supplied LD matrix uses this order.
  s[,row_idx:=.I]
  s[,`:=`(beta=as.numeric(BETA),se=as.numeric(SE),z=as.numeric(STAT))]
  ok<-s[is.finite(beta)&is.finite(se)&se>0&is.finite(z)]
  if(!nrow(ok)) stop("GJOKA summary has no finite additive effects at locus ",idx)
  max_z_delta<-max(abs(ok$beta/ok$se-ok$z))
  # BETA and SE are published at roughly four significant digits. Across the
  # two frozen loci the empirical maximum rounding delta is 0.00611 and the
  # BETA/SE-versus-STAT correlation exceeds 0.99999996, so 0.01 is a bounded
  # rounding tolerance rather than an analytical substitution for STAT.
  if(!is.finite(max_z_delta)||max_z_delta>1e-2)
    stop("GJOKA BETA/SE/STAT inconsistency at locus ",idx,": max delta=",max_z_delta)
  list(s=s,R=R)
}
configs<-data.table(config=c("PF10_L5","PF10_L10","PF10_L20","PF50_L10"),
                    mode=c("PF10","PF10","PF10","PF50"),L=c(5L,10L,20L,10L))
rows<-list();csrows<-list();csdetail<-list();k<-1L
cs_table<-function(obj,trait,gene,cell,config){
  if(is.null(obj$sets$cs)||!length(obj$sets$cs)) return(NULL)
  rbindlist(lapply(seq_along(obj$sets$cs),function(j){
    idx<-unname(obj$sets$cs[[j]])
    ids<-names(obj$sets$cs[[j]])
    if(is.null(ids)) ids<-names(obj$pip)[idx]
    label<-names(obj$sets$cs)[j]
    if(is.null(label)||is.na(label)||!nzchar(label)) label<-paste0("CS",j)
    data.table(gene=gene,cell_type=cell,config=config,trait=trait,
               credible_set=label,variant_id=ids,PIP=as.numeric(obj$pip[idx]))
  }),fill=TRUE)
}
keys<-unique(tr[,.(gene,cell_type,gjoka_locus_index)])
for(i in seq_len(nrow(keys))){
  key<-keys[i];slug<-paste(key$gene,key$cell_type,sep="_");d<-file.path(ldbase,slug)
  vars<-fread(file.path(d,"LD_variants.tsv"));setorder(vars,LD_order_zero_based)
  qq<-qall[gene==key$gene & cell_type==key$cell_type]
  qq<-qq[match(vars$variant_id,qq$variant_id)]
  if(anyNA(qq$variant_id)) stop("QTL/LD mismatch ",slug)
  gj<-read_gjoka(as.integer(key$gjoka_locus_index))
  # Identity bridge: GCST summary has explicit BIM-harmonized alleles and rsID.
  # GJOKA PLINK .assoc.logistic has A1 but no explicit A2, so exact variant identity
  # is established through the GCST rsID/OneK BIM bridge rather than position alone.
  bridge<-fread(file.path(root,"3_results","01_gwas","R7A1B",paste0("PBC_",key$gene,"_GRCh37_BIM_A1.tsv.gz")))
  bridge<-bridge[,.(variant_id,rsid,BIM_A1=toupper(BIM_A1),BIM_A2=toupper(BIM_A2))]
  map<-merge(vars[,.(variant_id,pos=as.integer(position_GRCh37),A1=toupper(A1),A2=toupper(A2))],bridge,by="variant_id")
  map<-map[A1==BIM_A1 & A2==BIM_A2]
  map<-merge(map,gj$s[,.(SNP,BP=as.integer(BP),A1_g=toupper(A1),z,row_idx)],by.x="rsid",by.y="SNP")
  map<-map[pos==BP & is.finite(z)]
  map<-map[!duplicated(variant_id)]
  common<-intersect(vars$variant_id,map$variant_id)
  if(length(common)<200) stop("too few common variants ",slug)
  vi<-match(common,vars$variant_id);mi<-match(common,map$variant_id);si<-map$row_idx[mi]
  DLD<-gj$R[si,si,drop=FALSE];DLD<-(DLD+t(DLD))/2;diag(DLD)<-1
  # Critical: disease z remains in the ORIGINAL GJOKA A1 orientation because the
  # GJOKA LD signs are tied to that orientation. QTL z remains OneK BIM-A1.
  # coloc.susie compares signal Bayes factors and allows separate LD per study.
  zD<-map$z[mi];zQ<-qq$slope_A1[vi]/qq$slope_se[vi]
  snps<-common
  dimnames(DLD)<-list(snps,snps)
  for(cc in seq_len(nrow(configs))){
    cfg<-configs[cc]
    qldfile<-file.path(d,paste0(cfg$mode,"_residualized_A1_correlation.tsv.gz"))
    QLD<-fread(qldfile,header=FALSE) |> as.matrix()
    QLD<-QLD[vi,vi,drop=FALSE];QLD<-(QLD+t(QLD))/2;diag(QLD)<-1
    dimnames(QLD)<-list(snps,snps)
    fitD<-susie_rss(z=zD,R=DLD,n=24510,L=cfg$L,estimate_residual_variance=FALSE,
                    estimate_prior_variance=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE)
    fitQ<-susie_rss(z=zQ,R=QLD,n=as.integer(qq$n_expression_donors[1]),L=cfg$L,
                    estimate_residual_variance=FALSE,estimate_prior_variance=TRUE,max_iter=2000,tol=1e-4,verbose=FALSE)
    SD<-annotate_susie(fitD,snps,DLD);SQ<-annotate_susie(fitQ,snps,QLD)
    csdetail[[length(csdetail)+1L]]<-cs_table(SD,"PBC",key$gene,key$cell_type,cfg$config)
    csdetail[[length(csdetail)+1L]]<-cs_table(SQ,"OneK_QTL",key$gene,key$cell_type,cfg$config)
    for(p12 in c(1e-6,1e-5,1e-4)){
      co<-coloc.susie(SD,SQ,p1=1e-4,p2=1e-4,p12=p12)
      s<-as.data.table(co$summary)
      if(nrow(s)){
        s[,`:=`(gene=key$gene,cell_type=key$cell_type,gjoka_locus_index=key$gjoka_locus_index,
                config=cfg$config,p12=p12)]
        s[,H4_over_H3H4:=PP.H4.abf/(PP.H3.abf+PP.H4.abf)]
        rows[[k]]<-s;k<-k+1L
      }
    }
    # Re-supply the corresponding LD matrix so the reported CS counts apply
    # the same minimum-purity filter used by annotate_susie/coloc.susie.
    csD<-susie_get_cs(fitD,Xcorr=DLD,coverage=.95,min_abs_corr=.5)
    csQ<-susie_get_cs(fitQ,Xcorr=QLD,coverage=.95,min_abs_corr=.5)
    csrows[[length(csrows)+1L]]<-data.table(gene=key$gene,cell_type=key$cell_type,config=cfg$config,
      disease_converged=isTRUE(fitD$converged),qtl_converged=isTRUE(fitQ$converged),
      disease_CS=ifelse(is.null(csD$cs),0,length(csD$cs)),qtl_CS=ifelse(is.null(csQ$cs),0,length(csQ$cs)),
      common_variants=length(common))
  }
}
R<-rbindlist(rows,fill=TRUE);C<-rbindlist(csrows,fill=TRUE)
CD<-rbindlist(csdetail,fill=TRUE)
fwrite(R,file.path(out,"R7A1B_signal_coloc_susie.tsv"),sep="\t")
fwrite(C,file.path(out,"R7A1B_susie_fit_summary.tsv"),sep="\t")
fwrite(CD,file.path(out,"R7A1B_susie_credible_set_members.tsv.gz"),sep="\t")
write_json(list(R=R.version.string,susieR=as.character(packageVersion("susieR")),coloc=as.character(packageVersion("coloc")),
                comparisons=nrow(keys),rows=nrow(R),credible_set_member_rows=nrow(CD)),
           file.path(out,"R7A1B_multisignal_runtime.json"),pretty=TRUE,auto_unbox=TRUE)
