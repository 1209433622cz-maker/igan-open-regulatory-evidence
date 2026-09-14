#!/usr/bin/env python3
from pathlib import Path
import os
import pandas as pd, numpy as np, json

ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
CODE=Path(__file__).resolve().parent
L=pd.read_csv(CODE/"R6A2B0_frozen_8_locus_leads.tsv",sep="\t")
BIM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
GWAS={
 "combined":ROOT/"1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis.txt",
 "european":ROOT/"1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_European_only.txt",
 "asian":ROOT/"1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_Asian_only.txt",
}
OUT=ROOT/"3_results/01_gwas/R6A2B0"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R6A2B0"; AUD.mkdir(parents=True,exist_ok=True)

bim=pd.read_csv(BIM,sep=r"\s+",header=None,names=["CHR","variant_id","cm","BP_hg19","BIM_A1","BIM_A2"],
                dtype={"CHR":int,"variant_id":str,"BIM_A1":str,"BIM_A2":str})
comp=str.maketrans("ACGT","TGCA")
def rc(x): return str(x).upper().translate(comp)[::-1]
def pal(a,b): return len(a)==1 and len(b)==1 and rc(a)==b

windows={r.locus:(int(r.chromosome),int(r.region_start_GRCh37),int(r.region_end_GRCh37),int(r.position_GRCh37),r.rsid,r.risk_allele)
         for r in L.itertuples(index=False)}
summary=[]
for label,path in GWAS.items():
    collected={k:[] for k in windows}
    for chunk in pd.read_csv(path,sep="\t",dtype=str,chunksize=650000):
        ch=pd.to_numeric(chunk.CHR,errors="coerce"); bp=pd.to_numeric(chunk.BP_hg19,errors="coerce")
        for locus,(c,s,e,lead,rsid,risk) in windows.items():
            mask=(ch==c)&bp.between(s,e)
            if mask.any(): collected[locus].append(chunk.loc[mask].copy())
    for locus,(c,s,e,lead,rsid,risk) in windows.items():
        x=pd.concat(collected[locus],ignore_index=True) if collected[locus] else pd.DataFrame(columns=["CHR","BP_hg19","A1","A2","BETA","SE","P"])
        if len(x):
            x["CHR"]=pd.to_numeric(x.CHR,errors="coerce"); x["BP_hg19"]=pd.to_numeric(x.BP_hg19,errors="coerce")
        b=bim[(bim.CHR==c)&bim.BP_hg19.between(s,e)].copy()
        x=x.merge(b[["variant_id","BP_hg19","BIM_A1","BIM_A2"]],on="BP_hg19",how="inner")
        outrows=[]
        for r in x.itertuples(index=False):
            a1=str(r.A1).upper(); a2=str(r.A2).upper(); b1=str(r.BIM_A1).upper(); b2=str(r.BIM_A2).upper()
            if pal(b1,b2): continue
            sign=None; rel=""
            if a1==b1 and a2==b2: sign=1; rel="DIRECT"
            elif a1==b2 and a2==b1: sign=-1; rel="SWAP"
            elif rc(a1)==b1 and rc(a2)==b2: sign=1; rel="STRAND_DIRECT"
            elif rc(a1)==b2 and rc(a2)==b1: sign=-1; rel="STRAND_SWAP"
            if sign is None: continue
            try:
                beta=float(r.BETA)*sign; se=float(r.SE); p=float(r.P)
            except: continue
            if not(np.isfinite(beta) and np.isfinite(se) and se>0 and np.isfinite(p) and 0<=p<=1): continue
            outrows.append({"dataset":label,"locus":locus,"chromosome":c,"position_GRCh37":int(r.BP_hg19),"variant_id":r.variant_id,
                            "BIM_A1":b1,"BIM_A2":b2,"GWAS_A1":a1,"GWAS_A2":a2,"beta_A1":beta,"standard_error":se,"p_value":p,"match_type":rel})
        o=pd.DataFrame(outrows).drop_duplicates("variant_id") if outrows else pd.DataFrame(columns=["variant_id","position_GRCh37","beta_A1","standard_error","p_value"])
        fn=OUT/f"{label}_{locus.replace('/','_')}_GRCh37_1Mb_A1.tsv.gz"
        o.to_csv(fn,sep="\t",index=False,compression="gzip")
        summary.append({"dataset":label,"locus":locus,"raw_BIM_join_rows":len(x),"eligible_rows":len(o),
                        "lead_position_present":bool((o.position_GRCh37==lead).any()) if len(o) else False,
                        "gwas_min_p":float(o.p_value.min()) if len(o) else None,"output":str(fn.relative_to(ROOT)).replace("\\","/")})
sdf=pd.DataFrame(summary)
sdf.to_csv(OUT/"R6A2B0_GWAS_harmonization_manifest.tsv",sep="\t",index=False)
primary=sdf[sdf.dataset=="combined"]
audit={"comparisons":len(sdf),"combined_all_regions_ge_500":bool((primary.eligible_rows>=500).all()),
       "combined_all_loci_have_data":bool((primary.eligible_rows>0).all()),
       "gate":"PASS" if (primary.eligible_rows>=500).all() else "HOLD"}
(AUD/"R6A2B0_GWAS_harmonization_gate.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print(json.dumps(audit,indent=2))
