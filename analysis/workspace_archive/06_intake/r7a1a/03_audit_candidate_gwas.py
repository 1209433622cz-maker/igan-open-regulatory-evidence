#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,json,math,re
from pathlib import Path
import pandas as pd, numpy as np

SYN={
 "chr":["CHR","chr","chromosome","chromosome_name"],
 "pos":["BP","POS","bp","pos","base_pair_location","BP_hg19"],
 "ea":["A1","effect_allele","EA","ALT","alt"],
 "oa":["A2","other_allele","NEA","REF","ref"],
 "beta":["BETA","beta"],
 "or":["OR","odds_ratio","odds_ratio_value"],
 "se":["SE","standard_error","se"],
 "p":["P","p","p_value","pvalue","PVALUE"],
 "rsid":["SNP","rsid","variant_id","hm_rsid"],
}
def find(cols,key):
    for x in SYN[key]:
        if x in cols:return x
    return None

ap=argparse.ArgumentParser()
ap.add_argument("--candidate",required=True,choices=["PBC","CeD"])
ap.add_argument("--file",required=True)
ap.add_argument("--outdir",required=True)
a=ap.parse_args()
p=Path(a.file); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
comp="gzip" if p.suffix==".gz" else None
header=pd.read_csv(p,sep="\t",compression=comp,nrows=3,dtype=str)
cols=list(header.columns)
m={k:find(cols,k) for k in SYN}
required=["chr","pos","ea","oa","se","p"]
missing=[k for k in required if not m[k]]
if not m["beta"] and not m["or"]: missing.append("beta_or_or")
if missing:
    raise SystemExit(f"Required schema fields missing: {missing}; columns={cols}")

rows=0; valid=0; gws=[]
for ch in pd.read_csv(p,sep="\t",compression=comp,dtype=str,chunksize=500000):
    rows+=len(ch)
    c=pd.to_numeric(ch[m["chr"]].astype(str).str.replace("chr","",regex=False),errors="coerce")
    pos=pd.to_numeric(ch[m["pos"]],errors="coerce")
    se=pd.to_numeric(ch[m["se"]],errors="coerce")
    pv=pd.to_numeric(ch[m["p"]],errors="coerce")
    if m["beta"]: beta=pd.to_numeric(ch[m["beta"]],errors="coerce")
    else:
        orv=pd.to_numeric(ch[m["or"]],errors="coerce")
        beta=np.log(orv.where(orv>0))
    ea=ch[m["ea"]].astype(str).str.strip()
    oa=ch[m["oa"]].astype(str).str.strip()
    allele_ok=(~ea.str.lower().isin(["", "na", "nan", "none"])) & (~oa.str.lower().isin(["", "na", "nan", "none"]))
    finite=np.isfinite(pos)&np.isfinite(se)&np.isfinite(pv)&np.isfinite(beta)
    good=c.between(1,22)&finite&se.gt(0)&pv.between(0,1)&allele_ok
    valid+=int(good.sum())
    nonmhc=good & ~((c==6)&pos.between(25_000_000,35_000_000))
    hit=nonmhc & (pv<=5e-8)
    if hit.any():
        x=pd.DataFrame({
          "chr":c[hit].astype(int),"pos":pos[hit].astype(int),
          "p":pv[hit].astype(float),"beta":beta[hit].astype(float),
          "effect_allele":ch.loc[hit,m["ea"]].astype(str),
          "other_allele":ch.loc[hit,m["oa"]].astype(str),
          "rsid":ch.loc[hit,m["rsid"]].astype(str) if m["rsid"] else ""
        })
        gws.append(x)
G=pd.concat(gws,ignore_index=True) if gws else pd.DataFrame(columns=["chr","pos","p","beta","effect_allele","other_allele","rsid"])
G=G.sort_values("p")
# Provisional distance-pruned lead count ONLY, not LD-independent inference.
kept=[]
for r in G.itertuples(index=False):
    if all(not (k["chr"]==r.chr and abs(k["pos"]-r.pos)<=1_000_000) for k in kept):
        kept.append(r._asdict())
K=pd.DataFrame(kept)
G.head(10000).to_csv(out/f"R7A1A_{a.candidate}_nonMHC_GWS_variants.tsv.gz",sep="\t",index=False,compression="gzip")
K.to_csv(out/f"R7A1A_{a.candidate}_provisional_distance_pruned_leads.tsv",sep="\t",index=False)
state={
 "candidate":a.candidate,"file":str(p),"bytes":p.stat().st_size,"columns":cols,"resolved_schema":m,
 "rows":rows,"valid_numeric_rows":valid,"nonMHC_GWS_variant_rows":len(G),
 "provisional_1Mb_distance_pruned_GWS_leads":len(K),
 "interpretation_limit":"1Mb distance-pruned lead count is intake QC only; do not call LD-independent signals without study/public LD.",
 "gate_schema":"PASS","gate_at_least_5_GWS_regions":"PASS" if len(K)>=5 else "FAIL"
}
(out/f"R7A1A_{a.candidate}_GWAS_byte_schema_audit.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
