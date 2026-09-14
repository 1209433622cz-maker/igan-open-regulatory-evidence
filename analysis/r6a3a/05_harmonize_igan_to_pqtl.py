from __future__ import annotations
import os, json, gzip
from pathlib import Path
import numpy as np, pandas as pd
try:
    from pyliftover import LiftOver
except ImportError as e:
    raise SystemExit("Install pyliftover first: python -m pip install pyliftover") from e

ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
CODE=ROOT/"analysis/r6a3a"
OUT=ROOT/"3_results/04_integration/R6A3A"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R6A3A"; AUD.mkdir(parents=True,exist_ok=True)
GWAS=ROOT/"1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis.txt"
CHAIN=ROOT/"1_data/reference/liftover/hg19ToHg38.over.chain"
T=pd.read_csv(CODE/"00_frozen_pqtl_targets.tsv",sep="\t")
P=pd.read_csv(OUT/"R6A3A_Sun2018_target_pqtl_sumstats.tsv.gz",sep="\t",dtype=str)

required={"variant","molecular_trait_id","beta","se","pvalue","ref","alt","chromosome","position"}
missing=required-set(P.columns)
if missing: raise RuntimeError(f"Unexpected eQTL Catalogue columns, missing: {sorted(missing)}")

# Map each target molecular trait back to frozen gene/locus.
C=pd.read_csv(OUT/"R6A3A_pqtl_candidate_molecular_traits.tsv",sep="\t",dtype=str)
trait_meta=C.drop_duplicates("molecular_trait_id").set_index("molecular_trait_id")[["locus","gene_symbol"]]
P=P[P.molecular_trait_id.isin(trait_meta.index)].copy()
P["locus"]=P.molecular_trait_id.map(trait_meta.locus)
P["gene_symbol"]=P.molecular_trait_id.map(trait_meta.gene_symbol)
P["position"]=pd.to_numeric(P.position,errors="coerce").astype("Int64")
P["pvalue"]=pd.to_numeric(P.pvalue,errors="coerce")
P["beta"]=pd.to_numeric(P.beta,errors="coerce")
P["se"]=pd.to_numeric(P.se,errors="coerce")
P=P.dropna(subset=["position","beta","se","pvalue"])
P=P[P.se>0]

# Scan disease GWAS only around frozen GRCh37 leads (+/-2 Mb).
windows={r.locus:(int(r.lead_chr_GRCh37),int(r.lead_pos_GRCh37)-2_000_000,int(r.lead_pos_GRCh37)+2_000_000) for r in T.drop_duplicates("locus").itertuples()}
gw=[]
for ch in pd.read_csv(GWAS,sep="\t",dtype=str,chunksize=600_000):
    c=pd.to_numeric(ch.CHR,errors="coerce"); b=pd.to_numeric(ch.BP_hg19,errors="coerce")
    keep=np.zeros(len(ch),dtype=bool)
    loc_arr=np.array([""]*len(ch),dtype=object)
    for locus,(chrom,s,e) in windows.items():
        m=(c==chrom)&b.between(s,e)
        keep |= m.to_numpy()
        loc_arr[m.to_numpy()]=locus
    if keep.any():
        x=ch.loc[keep].copy()
        x["locus"]=loc_arr[keep]
        gw.append(x)
D=pd.concat(gw,ignore_index=True)
lo=LiftOver(str(CHAIN))
comp=str.maketrans("ACGT","TGCA")
def cbase(a): return str(a).upper().translate(comp)[::-1]
def pal(a,b): return len(a)==1 and len(b)==1 and cbase(a)==b

mapped=[]
for r in D.itertuples(index=False):
    chrom=f"chr{r.CHR}"; pos37=int(r.BP_hg19)
    hits=lo.convert_coordinate(chrom,pos37-1)
    hits=[h for h in hits if h[0].removeprefix("chr")==str(r.CHR)]
    if len(hits)!=1: continue
    _,p0,strand,_=hits[0]
    a1=str(r.A1).upper(); a2=str(r.A2).upper()
    if strand=="-": a1,a2=cbase(a1),cbase(a2)
    mapped.append({"locus":r.locus,"chr38":str(r.CHR),"pos38":int(p0)+1,"D_A1":a1,"D_A2":a2,
                   "D_beta":float(r.BETA),"D_se":float(r.SE),"D_p":float(r.P),
                   "source_chr37":int(r.CHR),"source_pos37":pos37})
M=pd.DataFrame(mapped)
rows=[]
for pr in P.itertuples(index=False):
    cand=M[(M.locus==pr.locus)&(M.chr38.astype(str)==str(pr.chromosome))&(M.pos38==int(pr.position))]
    if cand.empty: continue
    ref=str(pr.ref).upper(); alt=str(pr.alt).upper()
    if pal(ref,alt): continue
    for dr in cand.itertuples(index=False):
        if dr.D_A1==alt and dr.D_A2==ref: db=dr.D_beta
        elif dr.D_A1==ref and dr.D_A2==alt: db=-dr.D_beta
        else: continue
        rows.append({"locus":pr.locus,"gene_symbol":pr.gene_symbol,"molecular_trait_id":pr.molecular_trait_id,
                     "variant":pr.variant,"rsid":getattr(pr,"rsid",""),"chromosome_GRCh38":pr.chromosome,"position_GRCh38":int(pr.position),
                     "ref":ref,"alt_effect":alt,"pqtl_beta_ALT":float(pr.beta),"pqtl_se":float(pr.se),"pqtl_p":float(pr.pvalue),
                     "disease_beta_ALT":db,"disease_se":dr.D_se,"disease_p":dr.D_p,
                     "disease_source_chr37":dr.source_chr37,"disease_source_pos37":dr.source_pos37})
H=pd.DataFrame(rows)
if len(H):
    H=H.drop_duplicates(["molecular_trait_id","variant"])
else:
    H=pd.DataFrame(columns=["locus","gene_symbol","molecular_trait_id","variant","rsid",
                            "chromosome_GRCh38","position_GRCh38","ref","alt_effect",
                            "pqtl_beta_ALT","pqtl_se","pqtl_p","disease_beta_ALT",
                            "disease_se","disease_p","disease_source_chr37","disease_source_pos37"])
H.to_csv(OUT/"R6A3A_IgAN_Sun2018_pqtl_harmonized.tsv.gz",sep="\t",index=False,compression="gzip")
q=H.groupby(["locus","gene_symbol","molecular_trait_id"]).agg(n_overlap=("variant","size"),disease_min_p=("disease_p","min"),pqtl_min_p=("pqtl_p","min")).reset_index()
q.to_csv(OUT/"R6A3A_pqtl_overlap_QC.tsv",sep="\t",index=False)
audit={"lifted_disease_rows":len(M),"harmonized_rows":len(H),"traits":H.molecular_trait_id.nunique() if len(H) else 0,
       "traits_ge_500_overlap":int((q.n_overlap>=500).sum()) if len(q) else 0,
       "status":"PASS" if len(H)>0 else "FAIL"}
(AUD/"R6A3A_IgAN_pqtl_harmonization_gate.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print(json.dumps(audit,indent=2))
