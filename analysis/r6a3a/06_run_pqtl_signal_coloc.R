#!/usr/bin/env Rscript
root<-Sys.getenv("IGAN_PROJECT_ROOT",unset=getwd())
.libPaths(c(file.path(root,"tools","R-library"),.libPaths()))
suppressPackageStartupMessages({library(data.table);library(coloc);library(jsonlite)})
out<-file.path(root,"3_results","04_integration","R6A3A")
h<-fread(file.path(out,"R6A3A_IgAN_Sun2018_pqtl_harmonized.tsv.gz"))
lbf<-fread(file.path(out,"R6A3A_Sun2018_target_lbf.tsv.gz"))
if(nrow(h)==0) stop("No harmonized rows")
lcols<-grep("^lbf_variable",names(lbf),value=TRUE)
if(length(lcols)==0) stop("No lbf_variable columns")
wakefield<-function(beta,se,W=0.2^2){
  V<-se^2; z<-beta/se; r<-W/(W+V)
  0.5*(log(1-r)+r*z^2)
}
rows<-list(); k<-1L
keys<-unique(h[,.(locus,gene_symbol,molecular_trait_id)])
for(i in seq_len(nrow(keys))){
  loc<-keys$locus[i]; gene<-keys$gene_symbol[i]; mt<-keys$molecular_trait_id[i]
  x<-h[locus==loc & gene_symbol==gene & molecular_trait_id==mt]
  y<-lbf[molecular_trait_id==mt]
  common<-intersect(x$variant,y$variant)
  if(length(common)<200) next
  x<-x[match(common,x$variant)]
  y<-y[match(common,y$variant)]
  dmat<-matrix(wakefield(x$disease_beta_ALT,x$disease_se),nrow=1)
  colnames(dmat)<-common; rownames(dmat)<-"IgAN_marginal"
  pmat<-t(as.matrix(y[,..lcols])); colnames(pmat)<-common
  rownames(pmat)<-sub("lbf_variable","L",lcols)
  for(p12 in c(1e-6,1e-5,1e-4)){
    fit<-coloc::coloc.bf_bf(dmat,pmat,p1=1e-4,p2=1e-4,p12=p12)
    s<-as.data.table(fit$summary)
    if(nrow(s)==0) next
    s[,`:=`(locus=loc,gene_symbol=gene,molecular_trait_id=mt,p12=p12)]
    rows[[k]]<-s; k<-k+1L
  }
}
res<-rbindlist(rows,fill=TRUE)
if(nrow(res)==0) stop("No coloc.bf_bf results")
res[,H4_over_H3H4:=PP.H4.abf/(PP.H3.abf+PP.H4.abf)]
fwrite(res,file.path(out,"R6A3A_pqtl_signal_coloc.tsv"),sep="\t")
write_json(list(R=R.version.string,coloc=as.character(packageVersion("coloc")),rows=nrow(res)),
           file.path(out,"R6A3A_pqtl_signal_coloc_runtime.json"),pretty=TRUE,auto_unbox=TRUE)
