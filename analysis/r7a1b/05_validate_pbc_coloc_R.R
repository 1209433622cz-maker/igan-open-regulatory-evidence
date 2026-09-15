#!/usr/bin/env Rscript
root<-Sys.getenv("R7_PROJECT_ROOT",unset="H:/SCI2/YR1")
.libPaths(c(file.path(root,"tools","R-library"),.libPaths()))
suppressPackageStartupMessages({library(coloc);library(data.table);library(jsonlite)})
code<-file.path(root,"2_code","06_intake","r7a1b")
q<-fread(file.path(root,"3_results","03_qtl","R7A1B","R7A1B_OneK_frozen_QTL.tsv.gz"))
f<-fread(file.path(code,"R7A1B_frozen_9_combinations.tsv"))
rows<-list();k<-1L
for(ii in seq_len(nrow(f))){
  gene_id<-f$gene[ii];cell_id<-f$cell_type[ii]
  qq<-q[gene==gene_id & cell_type==cell_id]
  gg<-fread(file.path(root,"3_results","01_gwas","R7A1B",paste0("PBC_",gene_id,"_GRCh37_BIM_A1.tsv.gz")))
  m<-merge(qq,gg,by="variant_id")
  m<-m[is.finite(slope_A1)&is.finite(slope_se)&slope_se>0&is.finite(beta_A1)&is.finite(standard_error)&standard_error>0]
  if(nrow(m)<500) next
  d1<-list(beta=m$beta_A1,varbeta=m$standard_error^2,snp=m$variant_id,type="cc")
  d2<-list(beta=m$slope_A1,varbeta=m$slope_se^2,snp=m$variant_id,MAF=pmin(m$af_A1,1-m$af_A1),
           N=unique(m$n_expression_donors),type="quant")
  for(p12 in c(1e-6,1e-5,1e-4)){
    fit<-suppressWarnings(coloc.abf(d1,d2,p1=1e-4,p2=1e-4,p12=p12))
    s<-fit$summary
    rows[[k]]<-data.table(gene=gene_id,cell_type=cell_id,p12=p12,nsnps=as.integer(s[["nsnps"]]),
      PP_H0=unname(s[["PP.H0.abf"]]),PP_H1=unname(s[["PP.H1.abf"]]),PP_H2=unname(s[["PP.H2.abf"]]),
      PP_H3=unname(s[["PP.H3.abf"]]),PP_H4=unname(s[["PP.H4.abf"]]))
    k<-k+1L
  }
}
x<-rbindlist(rows);x[,H4_over_H3H4:=PP_H4/(PP_H3+PP_H4)]
out<-file.path(root,"3_results","04_integration","R7A1B")
fwrite(x,file.path(out,"R7A1B_official_R_coloc_validation.tsv"),sep="\t")
write_json(list(R=R.version.string,coloc=as.character(packageVersion("coloc")),runs=nrow(x)),
           file.path(out,"R7A1B_official_R_coloc_validation.json"),pretty=TRUE,auto_unbox=TRUE)
