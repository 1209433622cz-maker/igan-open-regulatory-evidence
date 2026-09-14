#!/usr/bin/env python3
from pathlib import Path
import os
import pandas as pd, numpy as np, math, json
from scipy.special import logsumexp

ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
QTL=ROOT/"3_results/03_qtl/R6A2B0/R6A2B0_OneK1K_8locus_QTL.tsv.gz"
GW=ROOT/"3_results/01_gwas/R6A2B0"
OUT=ROOT/"3_results/04_integration/R6A2B0"; OUT.mkdir(parents=True,exist_ok=True)

def logdiff(a,b):
    if b>=a: return -np.inf
    return a+np.log1p(-np.exp(b-a))
def sdY_est(vbeta,maf,n):
    one=1.0/vbeta; nvx=2.0*n*maf*(1-maf); cf=np.sum(one*nvx)/np.sum(one*one)
    if not np.isfinite(cf) or cf<=0: raise ValueError("bad sdY")
    return math.sqrt(cf)
def labf(beta,se,typ,sdY=1.0):
    V=np.asarray(se,float)**2; z=np.asarray(beta,float)/np.asarray(se,float)
    sp=(0.15*sdY) if typ=="quant" else 0.2
    r=sp**2/(sp**2+V)
    return 0.5*(np.log1p(-r)+r*z*z)
def combine(l1,l2,p12):
    a1=logsumexp(l1); a2=logsumexp(l2); a12=logsumexp(l1+l2)
    lh=np.array([0,math.log(1e-4)+a1,math.log(1e-4)+a2,math.log(1e-4)+math.log(1e-4)+logdiff(a1+a2,a12),math.log(p12)+a12])
    return np.exp(lh-logsumexp(lh)), l1+l2

q=pd.read_csv(QTL,sep="\t")
rows=[]
for (locus,gene,cell),qd in q.groupby(["locus","gene","cell_type"],sort=True):
    qd=qd.drop_duplicates("variant_id").set_index("variant_id")
    n=int(qd.n_expression_donors.iloc[0])
    for trait in ["combined","european","asian"]:
        gp=GW/f"{trait}_{locus.replace('/','_')}_GRCh37_1Mb_A1.tsv.gz"
        if not gp.exists(): continue
        gd=pd.read_csv(gp,sep="\t").drop_duplicates("variant_id").set_index("variant_id")
        ids=pd.Index(sorted(set(qd.index).intersection(gd.index)))
        if len(ids)<500:
            rows.append({"dataset":trait,"locus":locus,"gene":gene,"cell_type":cell,"n_snps":len(ids),"classification":"INSUFFICIENT_OVERLAP"}); continue
        m=qd.loc[ids].join(gd.loc[ids].add_prefix("g_"))
        m=m[np.isfinite(m.slope_A1)&np.isfinite(m.slope_se)&(m.slope_se>0)&np.isfinite(m.g_beta_A1)&np.isfinite(m.g_standard_error)&(m.g_standard_error>0)]
        if len(m)<500:
            rows.append({"dataset":trait,"locus":locus,"gene":gene,"cell_type":cell,"n_snps":len(m),"classification":"INSUFFICIENT_OVERLAP"}); continue
        maf=np.minimum(m.af_A1.to_numpy(float),1-m.af_A1.to_numpy(float))
        sy=sdY_est(m.slope_se.to_numpy(float)**2,maf,n)
        lq=labf(m.slope_A1,m.slope_se,"quant",sy); lg=labf(m.g_beta_A1,m.g_standard_error,"cc")
        pp={}; ratio={}
        for p12 in [1e-6,1e-5,1e-4]:
            x,ls=combine(lg,lq,p12); pp[p12]=x; ratio[p12]=x[4]/(x[3]+x[4]) if x[3]+x[4]>0 else np.nan
            if p12==1e-5: lsum=ls
        d=pp[1e-5]; h34=d[3]+d[4]
        robust=d[4]>=0.80 and ratio[1e-5]>=0.80 and ratio[1e-6]>=0.50
        ambiguity=(not robust) and h34>=0.50 and ratio[1e-5]>=0.20
        gmin=float(m.g_p_value.min()); qmin=float(m.pval_nominal.min())
        if robust: cls="PASS_ROBUST_SHARED_SIGNAL"
        elif ambiguity: cls="HOLD_TARGETED_LD"
        elif gmin<=5e-8 and qmin<=1e-6 and max(pp[x][4] for x in pp)<0.20: cls="FAIL_SUFFICIENT_COVERAGE"
        else: cls="UNINFORMATIVE_OR_WEAK_QTL"
        snpp=np.exp(lsum-logsumexp(lsum)); imax=int(np.argmax(snpp))
        rows.append({"dataset":trait,"locus":locus,"gene":gene,"cell_type":cell,"n_snps":len(m),"qtl_N":n,
                     "gwas_min_p":gmin,"qtl_min_p":qmin,"PP_H0":d[0],"PP_H1":d[1],"PP_H2":d[2],"PP_H3":d[3],"PP_H4":d[4],
                     "H4_over_H3H4":ratio[1e-5],"H4_p12_1e-6":pp[1e-6][4],"H4ratio_p12_1e-6":ratio[1e-6],
                     "H4_p12_1e-4":pp[1e-4][4],"H4ratio_p12_1e-4":ratio[1e-4],"classification":cls,
                     "shared_top_variant":m.index[imax],"shared_top_SNP_PP_H4_conditional":float(snpp[imax])})
res=pd.DataFrame(rows)
res.to_csv(OUT/"R6A2B0_coloc_smoke_549max.tsv",sep="\t",index=False)

combined=res[res.dataset=="combined"].copy()
locus_rows=[]
for loc,g in combined.groupby("locus"):
    usable=g[~g.classification.isin(["INSUFFICIENT_OVERLAP"])]
    if len(usable)==0:
        status="INSUFFICIENT"
        best_gene=best_cell=None; best_h4=best_ratio=np.nan
    else:
        best=usable.sort_values(["PP_H4","H4_over_H3H4"],ascending=False).iloc[0]
        best_gene,best_cell,best_h4,best_ratio=best.gene,best.cell_type,best.PP_H4,best.H4_over_H3H4
        if (usable.classification=="PASS_ROBUST_SHARED_SIGNAL").any(): status="PASS_ROBUST_SINGLE_SIGNAL"
        elif (usable.classification=="HOLD_TARGETED_LD").any(): status="HOLD_TARGETED_LD"
        elif (usable.classification=="FAIL_SUFFICIENT_COVERAGE").any(): status="DISTINCT_SIGNAL_PRESENT"
        else: status="UNINFORMATIVE"
    locus_rows.append({"locus":loc,"status":status,"best_gene":best_gene,"best_cell":best_cell,"best_PP_H4":best_h4,"best_H4_ratio":best_ratio,
                       "n_robust":int((g.classification=="PASS_ROBUST_SHARED_SIGNAL").sum()),
                       "n_LD_triggers":int((g.classification=="HOLD_TARGETED_LD").sum())})
ldf=pd.DataFrame(locus_rows).sort_values("locus")
ldf.to_csv(OUT/"R6A2B0_locus_adjudication.tsv",sep="\t",index=False)
trig=combined[combined.classification=="HOLD_TARGETED_LD"].copy()
trig.to_csv(OUT/"R6A2B0_sourceLD_triggers.tsv",sep="\t",index=False)
summary={
 "frozen_combinations":int(q.groupby(["locus","gene","cell_type"]).ngroups),
 "tests_total":int(len(res)),
 "combined_tests":int(len(combined)),
 "robust_combined_combinations":int((combined.classification=="PASS_ROBUST_SHARED_SIGNAL").sum()),
 "targeted_LD_combined_combinations":int((combined.classification=="HOLD_TARGETED_LD").sum()),
 "robust_loci":int((ldf.status=="PASS_ROBUST_SINGLE_SIGNAL").sum()),
 "LD_trigger_loci":int((ldf.status=="HOLD_TARGETED_LD").sum()),
 "locus_status":ldf.to_dict("records")
}
(OUT/"R6A2B0_coloc_smoke_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,indent=2))
