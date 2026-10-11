#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np, math, json
from scipy.special import logsumexp

ROOT=Path(r"H:\SCI2\YR1")
QTL=ROOT/"3_results/03_qtl/R6A2A/R6A2A_OneK1K_benchmark_QTL.tsv.gz"
GWAS_ROOT=ROOT/"3_results/01_gwas/R6A2A"
OUT=ROOT/"3_results/04_integration/R6A2A"; OUT.mkdir(parents=True,exist_ok=True)

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
rows=[]; tops=[]
for (locus,gene,cell,role),qd in q.groupby(["locus","gene","cell_type","benchmark_role"],sort=True):
    qd=qd.drop_duplicates("variant_id").set_index("variant_id")
    n=int(qd.n_expression_donors.iloc[0])
    for trait in ["combined","european","asian"]:
        gp=GWAS_ROOT/f"{trait}_{locus.replace('/','_')}_GRCh37_1Mb_A1.tsv.gz"
        if not gp.exists(): continue
        gd=pd.read_csv(gp,sep="\t").drop_duplicates("variant_id").set_index("variant_id")
        ids=pd.Index(sorted(set(qd.index).intersection(gd.index)))
        if len(ids)<500: continue
        m=qd.loc[ids].join(gd.loc[ids].add_prefix("g_"))
        m=m[np.isfinite(m.slope_A1)&np.isfinite(m.slope_se)&(m.slope_se>0)&np.isfinite(m.g_beta_A1)&np.isfinite(m.g_standard_error)&(m.g_standard_error>0)]
        if len(m)<500: continue
        maf=np.minimum(m.af_A1.to_numpy(float),1-m.af_A1.to_numpy(float))
        sy=sdY_est(m.slope_se.to_numpy(float)**2,maf,n)
        lq=labf(m.slope_A1,m.slope_se,"quant",sy); lg=labf(m.g_beta_A1,m.g_standard_error,"cc")
        pp={}; ratios={}
        for p12 in [1e-6,1e-5,1e-4]:
            x,ls=combine(lg,lq,p12); pp[p12]=x; ratios[p12]=x[4]/(x[3]+x[4]) if x[3]+x[4]>0 else np.nan
            if p12==1e-5: lsum=ls
        d=pp[1e-5]; ratio=ratios[1e-5]; h34=d[3]+d[4]
        robust=d[4]>=0.8 and ratio>=0.8 and all(ratios[p]>=0.5 for p in ratios)
        ambiguity=(not robust) and h34>=0.5 and ratio>=0.2
        gmin=float(m.g_p_value.min()); qmin=float(m.pval_nominal.min())
        if robust: cls="PASS_ROBUST_SHARED_SIGNAL"
        elif ambiguity: cls="HOLD_TARGETED_LD"
        elif gmin<=5e-8 and qmin<=1e-6 and max(pp[p][4] for p in pp)<0.2: cls="FAIL_SUFFICIENT_COVERAGE"
        else: cls="UNINFORMATIVE_OR_WEAK_QTL"
        snpp=np.exp(lsum-logsumexp(lsum)); imax=int(np.argmax(snpp))
        rows.append({"dataset":trait,"locus":locus,"gene":gene,"cell_type":cell,"benchmark_role":role,"n_snps":len(m),"qtl_N":n,
                     "gwas_min_p":gmin,"qtl_min_p":qmin,"PP_H0":d[0],"PP_H1":d[1],"PP_H2":d[2],"PP_H3":d[3],"PP_H4":d[4],
                     "H4_over_H3H4":ratio,"H4_p12_1e-6":pp[1e-6][4],"H4ratio_p12_1e-6":ratios[1e-6],
                     "H4_p12_1e-4":pp[1e-4][4],"H4ratio_p12_1e-4":ratios[1e-4],"classification":cls,
                     "shared_top_variant":m.index[imax],"shared_top_SNP_PP_H4_conditional":float(snpp[imax])})
res=pd.DataFrame(rows)
res.to_csv(OUT/"R6A2A_coloc_smoke.tsv",sep="\t",index=False)
primary=res[(res.dataset=="combined")&(res.benchmark_role=="PUBLISHED_CELL_CLASS_PRIMARY")]
locus=[]
for loc,g in primary.groupby("locus"):
    best=g.sort_values(["PP_H4","H4_over_H3H4"],ascending=False).iloc[0]
    if (g.classification=="PASS_ROBUST_SHARED_SIGNAL").any(): status="PASS_SINGLE_SIGNAL"
    elif (g.classification=="HOLD_TARGETED_LD").any(): status="HOLD_TARGETED_LD"
    elif (g.classification=="FAIL_SUFFICIENT_COVERAGE").any(): status="FAIL_OR_DISTINCT"
    else: status="UNINFORMATIVE"
    locus.append({"locus":loc,"status":status,"best_gene":best.gene,"best_cell":best.cell_type,"best_PP_H4":best.PP_H4,"best_H4_ratio":best.H4_over_H3H4,"best_qtl_min_p":best.qtl_min_p})
ldf=pd.DataFrame(locus)
ldf.to_csv(OUT/"R6A2A_locus_benchmark_adjudication.tsv",sep="\t",index=False)
trig=res[(res.dataset=="combined")&(res.classification=="HOLD_TARGETED_LD")].copy()
trig.to_csv(OUT/"R6A2A_sourceLD_triggers.tsv",sep="\t",index=False)
summary={"tests":len(res),"combined_tests":int((res.dataset=="combined").sum()),"robust_combined":int(((res.dataset=="combined")&(res.classification=="PASS_ROBUST_SHARED_SIGNAL")).sum()),
         "targeted_LD_triggers_combined":int(((res.dataset=="combined")&(res.classification=="HOLD_TARGETED_LD")).sum()),
         "published_cell_locus_status":ldf.to_dict("records"),
         "next":"RUN_TARGETED_LD" if len(trig) else "ADJUDICATE_BENCHMARK_GATE"}
(OUT/"R6A2A_coloc_smoke_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,indent=2))
