from __future__ import annotations
import os, json
from pathlib import Path
import pandas as pd

ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
DATA=ROOT/"1_data/qtl/eQTLCatalogue/Sun_2018_QTD000584"
OUT=ROOT/"3_results/04_integration/R6A3A"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R6A3A"; AUD.mkdir(parents=True,exist_ok=True)
C=pd.read_csv(OUT/"R6A3A_pqtl_candidate_molecular_traits.tsv",sep="\t",dtype=str)
traits=set(C.molecular_trait_id.astype(str))
genes=set(C.gene_id.astype(str).str.split(".").str[0])
if not traits: raise RuntimeError("No frozen pQTL candidates")

all_path=DATA/"QTD000584.all.tsv.gz"
lbf_path=DATA/"QTD000584.lbf_variable.txt.gz"
parts=[]
for chunk in pd.read_csv(all_path,sep="\t",compression="gzip",dtype=str,chunksize=600_000):
    mid=chunk["molecular_trait_id"].astype(str) if "molecular_trait_id" in chunk else pd.Series("",index=chunk.index)
    gid=chunk["gene_id"].astype(str).str.split(".").str[0] if "gene_id" in chunk else pd.Series("",index=chunk.index)
    x=chunk[mid.isin(traits) | gid.isin(genes)].copy()
    if len(x): parts.append(x)
if not parts: raise RuntimeError("No target rows found in QTD000584.all.tsv.gz")
P=pd.concat(parts,ignore_index=True)
# Keep all molecular probes but remove duplicated variant records caused by duplicate rsIDs.
keycols=[c for c in ["molecular_trait_id","variant"] if c in P.columns]
before=len(P)
P=P.drop_duplicates(keycols,keep="first")
P.to_csv(OUT/"R6A3A_Sun2018_target_pqtl_sumstats.tsv.gz",sep="\t",index=False,compression="gzip")

lp=[]
for chunk in pd.read_csv(lbf_path,sep="\t",compression="gzip",dtype=str,chunksize=500_000):
    mid=chunk["molecular_trait_id"].astype(str)
    x=chunk[mid.isin(traits)].copy()
    if len(x): lp.append(x)
L=pd.concat(lp,ignore_index=True) if lp else pd.DataFrame()
if L.empty: raise RuntimeError("No target rows found in source SuSiE LBF file")
L.to_csv(OUT/"R6A3A_Sun2018_target_lbf.tsv.gz",sep="\t",index=False,compression="gzip")

audit={"candidate_traits":len(traits),"sumstat_rows_before_dedup":before,"sumstat_rows_after_dedup":len(P),
       "lbf_rows":len(L),"lbf_components":[c for c in L.columns if c.startswith("lbf_variable")],
       "status":"PASS" if len(P)>0 and len(L)>0 else "FAIL"}
(AUD/"R6A3A_Sun2018_dense_extraction_gate.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print(json.dumps(audit,indent=2))
