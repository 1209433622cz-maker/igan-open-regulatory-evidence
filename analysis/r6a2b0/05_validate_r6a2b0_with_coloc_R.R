#!/usr/bin/env Rscript
.libPaths(c(normalizePath(file.path(Sys.getenv("IGAN_PROJECT_ROOT", unset=getwd()),"tools/R-library"),winslash="/",mustWork=FALSE),.libPaths()))
suppressPackageStartupMessages({library(coloc);library(data.table);library(jsonlite)})
root<-Sys.getenv("IGAN_PROJECT_ROOT", unset=getwd())
q<-fread(file.path(root,"3_results/03_qtl/R6A2B0/R6A2B0_OneK1K_8locus_QTL.tsv.gz"))
rows<-list(); k<-1L
keys<-unique(q[,.(locus,gene,cell_type)])
for(ii in seq_len(nrow(keys))){
  locus_id<-keys$locus[ii]; gene_id<-keys$gene[ii]; cell_id<-keys$cell_type[ii]
  qq<-q[locus==locus_id & gene==gene_id & cell_type==cell_id]
  for(trait in c("combined","european","asian")){
    gp<-file.path(root,"3_results/01_gwas/R6A2B0",paste0(trait,"_",gsub("/","_",locus_id),"_GRCh37_1Mb_A1.tsv.gz"))
    if(!file.exists(gp)) next
    gg<-fread(gp)
    m<-merge(qq,gg,by="variant_id")
    m<-m[is.finite(slope_A1)&is.finite(slope_se)&slope_se>0&is.finite(beta_A1)&is.finite(standard_error)&standard_error>0]
    if(nrow(m)<500) next
    d1<-list(beta=m$beta_A1,varbeta=m$standard_error^2,snp=m$variant_id,type="cc")
    d2<-list(beta=m$slope_A1,varbeta=m$slope_se^2,snp=m$variant_id,MAF=pmin(m$af_A1,1-m$af_A1),
             N=unique(m$n_expression_donors),type="quant")
    for(p12 in c(1e-6,1e-5,1e-4)){
      # coloc.abf prints one posterior table per run. Capture that routine output
      # so the 1,647-run validation remains observable without flooding the log.
      invisible(capture.output(
        fit<-suppressWarnings(coloc.abf(d1,d2,p1=1e-4,p2=1e-4,p12=p12))
      ))
      s<-fit$summary
      rows[[k]]<-data.table(dataset=trait,locus=locus_id,gene=gene_id,cell_type=cell_id,p12=p12,
        nsnps=as.integer(s[["nsnps"]]),PP_H0=unname(s[["PP.H0.abf"]]),PP_H1=unname(s[["PP.H1.abf"]]),
        PP_H2=unname(s[["PP.H2.abf"]]),PP_H3=unname(s[["PP.H3.abf"]]),PP_H4=unname(s[["PP.H4.abf"]]))
      k<-k+1L
    }
  }
}
x<-rbindlist(rows); x[,H4_over_H3H4:=PP_H4/(PP_H3+PP_H4)]
out<-file.path(root,"3_results/04_integration/R6A2B0")
fwrite(x,file.path(out,"R6A2B0_official_R_coloc_validation.tsv"),sep="\t")
write_json(list(R=R.version.string,coloc=as.character(packageVersion("coloc")),runs=nrow(x),
                comparisons=length(unique(paste(x$dataset,x$locus,x$gene,x$cell_type)))),
           file.path(out,"R6A2B0_official_R_coloc_validation.json"),pretty=TRUE,auto_unbox=TRUE)
