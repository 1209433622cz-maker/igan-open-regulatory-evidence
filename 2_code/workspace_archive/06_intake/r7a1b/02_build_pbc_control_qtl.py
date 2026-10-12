#!/usr/bin/env python3
from pathlib import Path
import os,json
import pandas as pd

ROOT=Path(os.environ.get("R7_PROJECT_ROOT",r"H:\SCI2\YR1"))
CODE=ROOT/"2_code/06_intake/r7a1b"
F=pd.read_csv(CODE/"R7A1B_frozen_9_combinations.tsv",sep="\t")
PARQ=ROOT/"1_data/qtl/OneK1K/R7A1B_chr1_members"
BIM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
SAMPLES=ROOT/"3_results/03_qtl/R5A2A2/cell_sample_lists"
OUT=ROOT/"3_results/03_qtl/R7A1B"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R7A1B"; AUD.mkdir(parents=True,exist_ok=True)

bim=pd.read_csv(BIM,sep=r"\s+",header=None,names=["chromosome","variant_id","cm","position_GRCh37","A1","A2"],
                dtype={"chromosome":int,"variant_id":str,"A1":str,"A2":str})
parts=[]; status=[]
for (cell,),sub in F.groupby(["cell_type"],sort=True):
    p=PARQ/f"OneK1K_{cell}.cis_qtl_pairs.chr1.parquet"
    sf=SAMPLES/f"{cell}.samples.txt"
    if not p.exists(): raise FileNotFoundError(p)
    if not sf.exists(): raise FileNotFoundError(sf)
    n=sum(1 for x in sf.read_text(encoding="utf-8").splitlines() if x.strip())
    source_genes=set(sub.source_gene_symbol.astype(str))
    q=pd.read_parquet(p,columns=["phenotype_id","variant_id","af","pval_nominal","slope","slope_se"])
    q=q[q.phenotype_id.astype(str).isin(source_genes)].copy()
    pos=pd.to_numeric(q.variant_id.str.split(":").str[1],errors="coerce")
    q["_pos"]=pos
    for r in sub.itertuples(index=False):
        x=q[(q.phenotype_id.astype(str)==str(r.source_gene_symbol)) &
            q["_pos"].between(int(r.region_start_GRCh37),int(r.region_end_GRCh37))].copy()
        b=bim[(bim.chromosome==1)&bim.position_GRCh37.between(int(r.region_start_GRCh37),int(r.region_end_GRCh37))]
        x=x.merge(b[["variant_id","position_GRCh37","A1","A2"]],on="variant_id",how="inner",validate="one_to_one")
        if x.empty:
            status.append({"gene":r.gene,"source_gene_symbol":r.source_gene_symbol,"cell_type":cell,"testable":False,"n_rows":0})
            continue
        if (~x.af.between(0,1)).any() or (x.slope_se<=0).any(): raise RuntimeError("invalid QTL values")
        x=x.rename(columns={"af":"af_A1","slope":"slope_A1","A1":"A1_effect_allele","A2":"A2_other_allele"})
        x["gene"]=r.gene;x["source_gene_symbol"]=r.source_gene_symbol;x["cell_type"]=cell
        x["cytoband"]=r.cytoband;x["gjoka_locus_index"]=int(r.gjoka_locus_index)
        x["force_multisignal"]=bool(r.force_multisignal);x["n_expression_donors"]=n
        parts.append(x.drop(columns=["_pos"],errors="ignore"))
        status.append({"gene":r.gene,"source_gene_symbol":r.source_gene_symbol,"cell_type":cell,"testable":True,
                       "n_rows":len(x),"n_expression_donors":n,"qtl_min_p":float(x.pval_nominal.min())})
if not parts: raise RuntimeError("no QTL rows")
allq=pd.concat(parts,ignore_index=True)
if allq.duplicated(["gene","cell_type","variant_id"]).any(): raise RuntimeError("duplicate QTL keys")
allq.to_csv(OUT/"R7A1B_OneK_frozen_QTL.tsv.gz",sep="\t",index=False,compression="gzip")
st=pd.DataFrame(status); st.to_csv(OUT/"R7A1B_OneK_frozen_testability.tsv",sep="\t",index=False)
state={"frozen_combinations":len(F),"testable_combinations":int(st.testable.sum()),
       "qtl_rows":len(allq),"gate":"PASS" if int(st.testable.sum())==len(F) else "HOLD"}
(AUD/"R7A1B_OneK_QTL_gate.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
