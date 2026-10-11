#!/usr/bin/env python3
"""
R7A1C1A full-PBC-region sensitivity for IL12RB2 × TenK10K NK.

Uses:
  1) canonical GCST90061440 GRCh37 full GWAS;
  2) UCSC hg19ToHg38 chain;
  3) TenK10K NK full ±100kb IL12RB2 QTL rows already present in the historical public-data release.

This removes the R7A1C0 restricted 292-rsID bridge limitation.
"""
from pathlib import Path
import os, math, json
import numpy as np, pandas as pd
from scipy.special import logsumexp
from pyliftover import LiftOver

ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
GWAS=ROOT/"1_data/gwas/R7A1A/PBC/GCST90061440_buildGRCh37.tsv"
CHAIN=ROOT/"1_data/reference/liftover/hg19ToHg38.over.chain"
TENK=ROOT/"6_release/current/R4A12FG4/CMM_R4A12FG4_TenK10K_NK接入与信号门_2026-09-13/data/NK_IL12RB2_full_variant_eqtl.tsv"
OUT=ROOT/"3_results/04_integration/R7A1C"; OUT.mkdir(parents=True,exist_ok=True)

if not all(p.exists() for p in [GWAS,CHAIN,TENK]):
    missing=[str(p) for p in [GWAS,CHAIN,TENK] if not p.exists()]
    raise FileNotFoundError(missing)

q=pd.read_csv(TENK,sep="\t")
q=q.rename(columns={"p.value":"p_value"})
required_qtl={"CHR","POS","MarkerID","Allele1","Allele2","AF_Allele2","BETA","SE","p_value","N"}
missing_qtl=sorted(required_qtl-set(q.columns))
if missing_qtl:
    raise ValueError(f"TenK QTL missing required columns: {missing_qtl}")
q=q[(q.CHR==1)&(q.POS.between(67200000,67420000))].copy()
q["ref"]=q.Allele1.astype(str).str.upper()
q["alt"]=q.Allele2.astype(str).str.upper()
q["key38"]=q.CHR.astype(str)+":"+q.POS.astype(str)+":"+q.ref+":"+q.alt
q=q.drop_duplicates("key38")

# Read only a broad GRCh37 window around IL12RB2.
parts=[]
for ch in pd.read_csv(GWAS,sep="\t",dtype=str,chunksize=500000):
    c=pd.to_numeric(ch["chromosome"],errors="coerce")
    p=pd.to_numeric(ch["base_pair_location"],errors="coerce")
    m=(c==1)&p.between(67650000,68050000)
    if m.any(): parts.append(ch.loc[m].copy())
g=pd.concat(parts,ignore_index=True)
lo=LiftOver(str(CHAIN))
comp=str.maketrans("ACGT","TGCA")
def rc(x): return str(x).upper().translate(comp)[::-1]
rows=[]
for r in g.itertuples(index=False):
    try:
        pos37=int(r.base_pair_location); ea=str(r.effect_allele).upper(); oa=str(r.other_allele).upper()
        beta=float(r.beta); se=float(r.standard_error); pv=float(r.p_value)
    except Exception:
        continue
    hits=lo.convert_coordinate("chr1",pos37-1)
    hits=[x for x in hits if x[0] in ("chr1","1")]
    if len(hits)!=1: continue
    _,p0,strand,_=hits[0]
    pos38=int(p0)+1
    if strand=="-": ea,oa=rc(ea),rc(oa)
    cand=q[q.POS==pos38]
    for qr in cand.itertuples(index=False):
        ref=str(qr.ref).upper(); alt=str(qr.alt).upper()
        if ea==alt and oa==ref: db=beta
        elif ea==ref and oa==alt: db=-beta
        else: continue
        rows.append({
            "variant_id":qr.MarkerID,"pos37":pos37,"pos38":pos38,
            "disease_beta_ALT":db,"disease_se":se,"disease_p":pv,
            "qtl_beta_ALT":float(qr.BETA),"qtl_se":float(qr.SE),
            "qtl_p":float(qr.p_value),"qtl_af_alt":float(qr.AF_Allele2),
            "qtl_n":int(qr.N)
        })
m=pd.DataFrame(rows).drop_duplicates("variant_id")
if len(m)<200: raise RuntimeError(f"insufficient overlap: {len(m)}")
if m.variant_id.duplicated().any():
    raise RuntimeError("duplicate TenK variant_id remained after harmonization")
if not np.isfinite(m[["disease_beta_ALT","disease_se","qtl_beta_ALT","qtl_se","qtl_af_alt"]].to_numpy()).all():
    raise RuntimeError("non-finite values remained in ABF inputs")
if not ((m.disease_se>0).all() and (m.qtl_se>0).all()):
    raise RuntimeError("non-positive standard error in ABF inputs")
if not m.qtl_af_alt.between(0,1,inclusive="neither").all():
    raise RuntimeError("QTL ALT frequency outside (0,1)")

def sdY(varbeta,maf,n):
    one=1/np.asarray(varbeta); nvx=2*n*maf*(1-maf)
    return math.sqrt(np.sum(one*nvx)/np.sum(one*one))
def labf(beta,se,typ,sy=1):
    V=np.asarray(se,float)**2; z=np.asarray(beta,float)/np.asarray(se,float)
    sp=.2 if typ=="cc" else .15*sy
    r=sp*sp/(sp*sp+V)
    return .5*(np.log1p(-r)+r*z*z)
def logdiff(a,b):
    if b>=a:return -np.inf
    return a+np.log1p(-np.exp(b-a))
from scipy.special import logsumexp
ld=labf(m.disease_beta_ALT,m.disease_se,"cc")
maf=np.minimum(m.qtl_af_alt.to_numpy(float),1-m.qtl_af_alt.to_numpy(float))
sy=sdY(m.qtl_se.to_numpy(float)**2,maf,int(m.qtl_n.iloc[0]))
lq=labf(m.qtl_beta_ALT,m.qtl_se,"quant",sy)
a1=logsumexp(ld);a2=logsumexp(lq);a12=logsumexp(ld+lq)
res=[]
for p12 in (1e-6,1e-5,1e-4):
    lh=np.array([0,np.log(1e-4)+a1,np.log(1e-4)+a2,
                 np.log(1e-8)+logdiff(a1+a2,a12),np.log(p12)+a12])
    pp=np.exp(lh-logsumexp(lh))
    res.append({"p12":p12,"n":len(m),"PP_H3":pp[3],"PP_H4":pp[4],
                "H4_over_H3H4":pp[4]/(pp[3]+pp[4])})
pd.DataFrame(res).to_csv(OUT/"R7A1C_IL12RB2_TenK_NK_fullPBC_coloc.tsv",sep="\t",index=False)
m.to_csv(OUT/"R7A1C_IL12RB2_TenK_NK_fullPBC_overlap.tsv.gz",sep="\t",index=False,compression="gzip")
if not (res[0]["H4_over_H3H4"]>=0.80 and res[1]["PP_H4"]>=0.80):
    raise RuntimeError(f"full-window TenK replication gate failed: {res}")
print(json.dumps(res,indent=2))
