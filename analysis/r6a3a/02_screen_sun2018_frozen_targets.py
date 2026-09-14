from __future__ import annotations
import gzip, os, re, json
from pathlib import Path
import pandas as pd

ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
CODE=ROOT/"analysis/r6a3a"
DATA=ROOT/"1_data/qtl/eQTLCatalogue/Sun_2018_QTD000584"
GTF=ROOT/"1_data/reference/gene_annotation/gencode.v50.annotation.gtf.gz"
OUT=ROOT/"3_results/04_integration/R6A3A"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R6A3A"; AUD.mkdir(parents=True,exist_ok=True)

T=pd.read_csv(CODE/"00_frozen_pqtl_targets.tsv",sep="\t")
if not GTF.exists(): raise FileNotFoundError(f"Required GENCODE mapping missing: {GTF}")

def attrs(s):
    out={}
    for x in s.split(";"):
        x=x.strip()
        if not x: continue
        m=re.match(r'(\S+)\s+"(.*)"',x)
        if m: out[m.group(1)]=m.group(2)
    return out

genes=[]
with gzip.open(GTF,"rt",encoding="utf-8",errors="replace") as h:
    for line in h:
        if line.startswith("#"): continue
        f=line.rstrip("\n").split("\t")
        if len(f)<9 or f[2]!="gene": continue
        a=attrs(f[8])
        if a.get("gene_name") in set(T.gene_symbol):
            genes.append({"gene_symbol":a.get("gene_name"),"gene_id":a.get("gene_id","").split(".")[0],
                          "chromosome":f[0].removeprefix("chr"),"gene_start_GRCh38":int(f[3]),"gene_end_GRCh38":int(f[4]),"strand":f[6]})
G=pd.DataFrame(genes).drop_duplicates(["gene_symbol","gene_id"])
if G.gene_symbol.nunique()!=T.gene_symbol.nunique():
    missing=sorted(set(T.gene_symbol)-set(G.gene_symbol))
    raise RuntimeError(f"GENCODE mapping incomplete: {missing}")
T=T.merge(G,on="gene_symbol",how="left",validate="many_to_one")

perm=pd.read_csv(DATA/"QTD000584.permuted.tsv.gz",sep="\t",compression="gzip",dtype=str)
cs=pd.read_csv(DATA/"QTD000584.credible_sets.tsv.gz",sep="\t",compression="gzip",dtype=str)

def normalize_gene_col(df):
    if "gene_id" in df.columns:
        return df["gene_id"].astype(str).str.split(".").str[0]
    if "molecular_trait_object_id" in df.columns:
        # eQTL Catalogue's Sun 2018 permutation table stores the
        # protein-encoding Ensembl ID in this column.
        return df["molecular_trait_object_id"].astype(str).str.split(".").str[0]
    if "phenotype_id" in df.columns:
        return df["phenotype_id"].astype(str).str.split(".").str[0]
    if "molecular_trait_id" in df.columns:
        # Protein traits can be aptamer IDs, so this is only a fallback.
        return df["molecular_trait_id"].astype(str)
    raise RuntimeError(f"Cannot identify gene/molecular trait column from {list(df.columns)}")

perm["_gene_key"]=normalize_gene_col(perm)
cs["_gene_key"]=normalize_gene_col(cs)
if "molecular_trait_id" not in perm.columns:
    perm["molecular_trait_id"]=perm.get("phenotype_id",perm["_gene_key"]).astype(str)
if "molecular_trait_id" not in cs.columns:
    cs["molecular_trait_id"]=cs.get("phenotype_id",cs["_gene_key"]).astype(str)

# If gene_id exists in CS it is authoritative for protein->encoding gene mapping.
if "gene_id" in cs.columns:
    cs["_gene_key"]=cs["gene_id"].astype(str).str.split(".").str[0]
if "gene_id" in perm.columns:
    perm["_gene_key"]=perm["gene_id"].astype(str).str.split(".").str[0]

adjusted_col = next((c for c in ["qval", "p_beta", "pval_beta", "p_perm"] if c in perm.columns), None)
if adjusted_col is None:
    raise RuntimeError(f"No permutation-adjusted significance column in {list(perm.columns)}")

rows=[]
traits=[]
for r in T.itertuples(index=False):
    gp=perm[perm["_gene_key"]==r.gene_id].copy()
    gc=cs[cs["_gene_key"]==r.gene_id].copy()
    measured=not gp.empty
    adjusted_min=pd.to_numeric(gp[adjusted_col],errors="coerce").min() if measured else float("nan")
    source_sig=bool(pd.notna(adjusted_min) and adjusted_min<0.05)
    has_cs=not gc.empty
    measured_traits=set(gp.molecular_trait_id.astype(str))
    cs_traits=set(gc.molecular_trait_id.astype(str))
    sig_traits=set(gp.loc[pd.to_numeric(gp[adjusted_col],errors="coerce")<0.05,"molecular_trait_id"].astype(str))
    candidate_traits=sorted(sig_traits | cs_traits)
    status=("SOURCE_SIG_OR_CS" if measured and (source_sig or has_cs)
            else "MEASURED_NO_SOURCE_SIGNAL" if measured
            else "NOT_MEASURED")
    rows.append({**r._asdict(),"measured_in_permutation":measured,
                 "adjusted_significance_column":adjusted_col,"min_adjusted_p":adjusted_min,
                 "source_qval_lt_0_05":source_sig,"has_source_susie_cs":has_cs,
                 "n_measured_molecular_traits":len(measured_traits),
                 "n_candidate_molecular_traits":len(candidate_traits),
                 "candidate_molecular_trait_ids":";".join(candidate_traits),"screen_status":status})
    for tid in candidate_traits:
        trait_perm=gp[gp.molecular_trait_id.astype(str)==tid]
        trait_adj=pd.to_numeric(trait_perm[adjusted_col],errors="coerce").min() if len(trait_perm) else float("nan")
        traits.append({"locus":r.locus,"gene_symbol":r.gene_symbol,"gene_id":r.gene_id,"molecular_trait_id":tid,
                       "chromosome":r.chromosome,"gene_start_GRCh38":r.gene_start_GRCh38,"gene_end_GRCh38":r.gene_end_GRCh38,
                       "adjusted_significance_column":adjusted_col,"trait_min_adjusted_p":trait_adj,
                       "source_significant_trait":bool(pd.notna(trait_adj) and trait_adj<0.05),
                       "has_source_susie_cs":tid in cs_traits})
S=pd.DataFrame(rows)
C=pd.DataFrame(traits)
S.to_csv(OUT/"R6A3A_Sun2018_frozen_target_screen.tsv",sep="\t",index=False)
C.to_csv(OUT/"R6A3A_pqtl_candidate_molecular_traits.tsv",sep="\t",index=False)
gate={"dataset":"QTD000584","study":"Sun_2018","donors":3301,"assay":"aptamer","build":"GRCh38",
      "effect_allele":"ALT","frozen_gene_count":len(T),"measured_genes":int(S.measured_in_permutation.sum()),
      "source_signal_or_cs_genes":int((S.screen_status=="SOURCE_SIG_OR_CS").sum()),
      "candidate_molecular_traits":int(len(C)),"status":"PASS_TO_DENSE_REGIONAL" if len(C)>0 else "NO_TARGET_SIGNAL"}
(AUD/"R6A3A_Sun2018_target_screen_gate.json").write_text(json.dumps(gate,indent=2),encoding="utf-8")
print(json.dumps(gate,indent=2))
