#!/usr/bin/env Rscript
suppressPackageStartupMessages(library(coloc))
args <- commandArgs(trailingOnly=TRUE)
if(length(args)!=6) stop("usage: script <harmonized.tsv> <release> <cell> <cases> <controls> <out.tsv>")
d <- read.delim(args[[1]],stringsAsFactors=FALSE,check.names=FALSE); release<-args[[2]]; cell<-args[[3]]
cases<-as.numeric(args[[4]]); controls<-as.numeric(args[[5]]); output<-args[[6]]
req<-c("variant_key","pos","qtl_beta","qtl_se","qtl_p","qtl_af_alt","qtl_n","gwas_beta","gwas_se","gwas_p","gwas_af_alt")
if(length(setdiff(req,names(d)))) stop("required columns absent")
ok<-is.finite(d$qtl_beta)&is.finite(d$qtl_se)&d$qtl_se>0&d$qtl_af_alt>0&d$qtl_af_alt<1&is.finite(d$gwas_beta)&is.finite(d$gwas_se)&d$gwas_se>0&d$gwas_af_alt>0&d$gwas_af_alt<1
d<-d[ok,]; if(nrow(d)<100) stop("fewer than 100 valid variants")
nq<-median(d$qtl_n); ng<-cases+controls; s<-cases/ng; mafq<-pmin(d$qtl_af_alt,1-d$qtl_af_alt)
nvx<-2*nq*mafq*(1-mafq); sdy<-sqrt(coef(lm(nvx~I(1/(d$qtl_se^2))-1))[[1]])
q<-list(beta=d$qtl_beta,varbeta=d$qtl_se^2,snp=d$variant_key,position=d$pos,MAF=mafq,N=nq,sdY=sdy,type="quant")
g<-list(beta=d$gwas_beta,varbeta=d$gwas_se^2,snp=d$variant_key,position=d$pos,MAF=pmin(d$gwas_af_alt,1-d$gwas_af_alt),N=ng,s=s,type="cc")
rows<-list(); for(p12 in c(1e-6,1e-5,1e-4)){
 f<-coloc.abf(g,q,p1=1e-4,p2=1e-4,p12=p12); sm<-f$summary; top<-which.max(f$results$SNP.PP.H4); h3<-unname(sm[["PP.H3.abf"]]);h4<-unname(sm[["PP.H4.abf"]])
 rows[[length(rows)+1]]<-data.frame(release=release,celltype=cell,role="POST_EXACT_GATE_SINGLE_CAUSAL_DIAGNOSTIC_ONLY",p1=1e-4,p2=1e-4,p12=p12,nsnps=unname(sm[["nsnps"]]),PP.H0=unname(sm[["PP.H0.abf"]]),PP.H1=unname(sm[["PP.H1.abf"]]),PP.H2=unname(sm[["PP.H2.abf"]]),PP.H3=h3,PP.H4=h4,H4_over_H3H4=ifelse(h3+h4>0,h4/(h3+h4),NA),top_shared_variant=f$results$snp[[top]],top_shared_variant_PP_H4=f$results$SNP.PP.H4[[top]],qtl_N=nq,qtl_sdY=sdy,gwas_N=ng,gwas_case_fraction=s,qtl_min_p=min(d$qtl_p),gwas_min_p=min(d$gwas_p),coloc_version=as.character(packageVersion("coloc")),R_version=R.version.string)
}
write.table(do.call(rbind,rows),output,sep="\t",row.names=FALSE,quote=FALSE)
