#!/usr/bin/env python3
from pathlib import Path
import os,json
import pandas as pd,numpy as np

ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
CODE=ROOT/"2_code/06_intake/r7a1b"
F=pd.read_csv(CODE/"R7A1B_frozen_9_combinations.tsv",sep="\t").drop_duplicates("gene")
GWAS=ROOT/"1_data/gwas/R7A1A/PBC/GCST90061440_buildGRCh37.tsv"
BIM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
OUT=ROOT/"3_results/01_gwas/R7A1B";OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R7A1B";AUD.mkdir(parents=True,exist_ok=True)
bim=pd.read_csv(BIM,sep=r"\s+",header=None,names=["chr","variant_id","cm","pos","BIM_A1","BIM_A2"],dtype=str)
bim["chr"]=pd.to_numeric(bim.chr);bim["pos"]=pd.to_numeric(bim.pos)
comp=str.maketrans("ACGT","TGCA")
def rc(x): return str(x).upper().translate(comp)[::-1]
def pal(a,b): return len(a)==1 and len(b)==1 and rc(a)==b
windows={r.gene:(int(r.region_start_GRCh37),int(r.region_end_GRCh37),int(r.gjoka_locus_index)) for r in F.itertuples(index=False)}
coll={g:[] for g in windows}
for ch in pd.read_csv(GWAS,sep="\t",dtype=str,chunksize=600000):
    c=pd.to_numeric(ch.chromosome,errors="coerce");p=pd.to_numeric(ch.base_pair_location,errors="coerce")
    for g,(s,e,idx) in windows.items():
        m=(c==1)&p.between(s,e)
        if m.any(): coll[g].append(ch.loc[m].copy())
rows=[]
for g,(s,e,idx) in windows.items():
    x=pd.concat(coll[g],ignore_index=True) if coll[g] else pd.DataFrame()
    x["base_pair_location"]=pd.to_numeric(x.base_pair_location)
    b=bim[(bim.chr==1)&bim.pos.between(s,e)].copy()
    x=x.merge(b[["variant_id","pos","BIM_A1","BIM_A2"]],left_on="base_pair_location",right_on="pos",how="inner")
    out=[]
    for r in x.itertuples(index=False):
        ea=str(r.effect_allele).upper();oa=str(r.other_allele).upper();a1=str(r.BIM_A1).upper();a2=str(r.BIM_A2).upper()
        if pal(a1,a2): continue
        sign=None;kind=""
        if ea==a1 and oa==a2: sign=1;kind="DIRECT"
        elif ea==a2 and oa==a1: sign=-1;kind="SWAP"
        elif rc(ea)==a1 and rc(oa)==a2: sign=1;kind="STRAND_DIRECT"
        elif rc(ea)==a2 and rc(oa)==a1: sign=-1;kind="STRAND_SWAP"
        if sign is None: continue
        try: beta=float(r.beta)*sign;se=float(r.standard_error);pv=float(r.p_value)
        except: continue
        if not(np.isfinite(beta) and np.isfinite(se) and se>0 and np.isfinite(pv) and 0<=pv<=1): continue
        out.append({"gene":g,"gjoka_locus_index":idx,"variant_id":r.variant_id_y,"position_GRCh37":int(r.pos),
                    "BIM_A1":a1,"BIM_A2":a2,"beta_A1":beta,"standard_error":se,"p_value":pv,
                    "GWAS_effect_allele":ea,"GWAS_other_allele":oa,"match_type":kind,"rsid":r.variant_id_x})
    o=pd.DataFrame(out)
    dup=pd.DataFrame()
    if len(o):
        # inference-eligible uniqueness: conflicting multiple rows per BIM variant are excluded rather than fatal.
        dup=o[o.duplicated("variant_id",keep=False)]
        if len(dup):
            bad=set(dup.variant_id);o=o[~o.variant_id.isin(bad)].copy()
        o=o.drop_duplicates("variant_id")
    fn=OUT/f"PBC_{g}_GRCh37_BIM_A1.tsv.gz";o.to_csv(fn,sep="\t",index=False,compression="gzip")
    rows.append({"gene":g,"gjoka_locus_index":idx,"eligible_rows":len(o),"gwas_min_p":float(o.p_value.min()) if len(o) else None,
                 "duplicate_conflict_variants_excluded":int(dup.variant_id.nunique()) if len(dup) else 0})
man=pd.DataFrame(rows);man.to_csv(OUT/"R7A1B_PBC_harmonization_manifest.tsv",sep="\t",index=False)
state={"genes":len(man),"all_regions_ge_500":bool((man.eligible_rows>=500).all()),
       "gate":"PASS" if (man.eligible_rows>=500).all() else "HOLD"}
(AUD/"R7A1B_PBC_harmonization_gate.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
