#!/usr/bin/env python3
from pathlib import Path
import os,json,math
import pandas as pd,numpy as np
from scipy.special import logsumexp

ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
CODE=ROOT/"2_code/06_intake/r7a1b"
Q=pd.read_csv(ROOT/"3_results/03_qtl/R7A1B/R7A1B_OneK_frozen_QTL.tsv.gz",sep="\t")
F=pd.read_csv(CODE/"R7A1B_frozen_9_combinations.tsv",sep="\t")
GW=ROOT/"3_results/01_gwas/R7A1B"
OUT=ROOT/"3_results/04_integration/R7A1B";OUT.mkdir(parents=True,exist_ok=True)

def logdiff(a,b):
    if b>=a:return -np.inf
    return a+np.log1p(-np.exp(b-a))
def sdY(vbeta,maf,n):
    one=1/vbeta;nvx=2*n*maf*(1-maf);cf=np.sum(one*nvx)/np.sum(one*one)
    if not np.isfinite(cf) or cf<=0:raise ValueError("bad sdY")
    return math.sqrt(cf)
def labf(beta,se,typ,sy=1):
    V=np.asarray(se,float)**2;z=np.asarray(beta,float)/np.asarray(se,float)
    sp=0.15*sy if typ=="quant" else 0.2;r=sp**2/(sp**2+V)
    return .5*(np.log1p(-r)+r*z*z)
def coloc(l1,l2,p12):
    a1=logsumexp(l1);a2=logsumexp(l2);a12=logsumexp(l1+l2)
    lh=np.array([0,math.log(1e-4)+a1,math.log(1e-4)+a2,
                 math.log(1e-4)+math.log(1e-4)+logdiff(a1+a2,a12),math.log(p12)+a12])
    return np.exp(lh-logsumexp(lh)),l1+l2

rows=[]
for r in F.itertuples(index=False):
    q=Q[(Q.gene==r.gene)&(Q.cell_type==r.cell_type)].drop_duplicates("variant_id").set_index("variant_id")
    g=pd.read_csv(GW/f"PBC_{r.gene}_GRCh37_BIM_A1.tsv.gz",sep="\t").drop_duplicates("variant_id").set_index("variant_id")
    ids=pd.Index(sorted(set(q.index)&set(g.index)))
    if len(ids)<500:
        rows.append({"gene":r.gene,"cell_type":r.cell_type,"gjoka_locus_index":r.gjoka_locus_index,
                     "n_snps":len(ids),"classification":"INSUFFICIENT_OVERLAP","force_multisignal":r.force_multisignal});continue
    m=q.loc[ids].join(g.loc[ids].add_prefix("g_"))
    m=m[np.isfinite(m.slope_A1)&np.isfinite(m.slope_se)&(m.slope_se>0)&np.isfinite(m.g_beta_A1)&np.isfinite(m.g_standard_error)&(m.g_standard_error>0)]
    maf=np.minimum(m.af_A1.to_numpy(float),1-m.af_A1.to_numpy(float));sy=sdY(m.slope_se.to_numpy(float)**2,maf,int(m.n_expression_donors.iloc[0]))
    lq=labf(m.slope_A1,m.slope_se,"quant",sy);lg=labf(m.g_beta_A1,m.g_standard_error,"cc")
    pp={};rat={}
    for p12 in [1e-6,1e-5,1e-4]:
        x,ls=coloc(lg,lq,p12);pp[p12]=x;rat[p12]=x[4]/(x[3]+x[4]) if x[3]+x[4]>0 else np.nan
        if p12==1e-5: lsum=ls
    d=pp[1e-5];h34=d[3]+d[4]
    robust=d[4]>=.8 and rat[1e-5]>=.8 and rat[1e-6]>=.5
    ambiguity=(not robust) and h34>=.5 and rat[1e-5]>=.2
    gmin=float(m.g_p_value.min());qmin=float(m.pval_nominal.min())
    if robust:cls="PASS_SINGLE_CAUSAL_SMOKE"
    elif ambiguity:cls="HOLD_H3H4_AMBIGUITY"
    elif gmin<=5e-8 and qmin<=1e-6 and max(pp[x][4] for x in pp)<.2:cls="DISTINCT_SIGNAL_SMOKE"
    else:cls="UNINFORMATIVE_OR_WEAK_QTL"
    snpp=np.exp(lsum-logsumexp(lsum));imax=int(np.argmax(snpp))
    rows.append({"gene":r.gene,"cell_type":r.cell_type,"gjoka_locus_index":int(r.gjoka_locus_index),
                 "force_multisignal":bool(r.force_multisignal),"n_snps":len(m),"qtl_N":int(m.n_expression_donors.iloc[0]),
                 "gwas_min_p":gmin,"qtl_min_p":qmin,"PP_H0":d[0],"PP_H1":d[1],"PP_H2":d[2],"PP_H3":d[3],"PP_H4":d[4],
                 "H4_over_H3H4":rat[1e-5],"H4_p12_1e-6":pp[1e-6][4],"H4ratio_p12_1e-6":rat[1e-6],
                 "H4_p12_1e-4":pp[1e-4][4],"classification":cls,
                 "shared_top_variant":m.index[imax],"shared_top_SNP_PP_H4_conditional":float(snpp[imax])})
R=pd.DataFrame(rows);R.to_csv(OUT/"R7A1B_coloc_smoke.tsv",sep="\t",index=False)
trigger=R[(R.force_multisignal==True)|R.classification.isin(["PASS_SINGLE_CAUSAL_SMOKE","HOLD_H3H4_AMBIGUITY"])].copy()
trigger["trigger_reason"]=np.where(trigger.force_multisignal,"PUBLISHED_DISEASE_MULTISIGNAL_FORCE",trigger.classification)
trigger.to_csv(OUT/"R7A1B_multisignal_triggers.tsv",sep="\t",index=False)
state={"smoke_tests":len(R),"robust_smoke":int((R.classification=="PASS_SINGLE_CAUSAL_SMOKE").sum()),
       "ambiguities":int((R.classification=="HOLD_H3H4_AMBIGUITY").sum()),"forced_multisignal":int(R.force_multisignal.sum()),
       "trigger_combinations":len(trigger),"trigger_genes":sorted(trigger.gene.unique().tolist())}
(OUT/"R7A1B_coloc_smoke_summary.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
