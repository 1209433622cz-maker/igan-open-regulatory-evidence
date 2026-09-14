#!/usr/bin/env python3
from pathlib import Path
import os
import pandas as pd, json, re

ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
CODE=Path(__file__).resolve().parent
U=pd.read_csv(CODE/"R6A2B0_frozen_183_combination_universe.tsv",sep="\t")
L=pd.read_csv(CODE/"R6A2B0_frozen_8_locus_leads.tsv",sep="\t")
PARQ=ROOT/"1_data/qtl/OneK1K/R6A2B0_members"
BIM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
SAMPLE_DIR=ROOT/"3_results/03_qtl/R5A2A2/cell_sample_lists"
OUT=ROOT/"3_results/03_qtl/R6A2B0"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R6A2B0"; AUD.mkdir(parents=True,exist_ok=True)

bim=pd.read_csv(BIM,sep=r"\s+",header=None,names=["chromosome","variant_id","cm","position_GRCh37","A1","A2"],
                dtype={"chromosome":int,"variant_id":str,"A1":str,"A2":str})
lead=L.set_index("locus").to_dict("index")
rows=[]; status=[]
for (chrom,cell),sub in U.groupby(["chromosome","cell_type_OneK1K"],sort=True):
    p=PARQ/f"OneK1K_{cell}.cis_qtl_pairs.chr{int(chrom)}.parquet"
    sf=SAMPLE_DIR/f"{cell}.samples.txt"
    if not p.exists(): raise RuntimeError(f"missing parquet {p}")
    if not sf.exists(): raise RuntimeError(f"missing frozen sample list {sf}")
    n=sum(1 for x in sf.read_text(encoding="utf-8").splitlines() if x.strip())
    genes=set(sub.gene_symbol.astype(str))
    q=pd.read_parquet(p,columns=["phenotype_id","variant_id","af","ma_samples","ma_count","pval_nominal","slope","slope_se"])
    q=q[q.phenotype_id.astype(str).isin(genes)].copy()
    pos=pd.to_numeric(q.variant_id.str.split(":").str[1],errors="coerce")
    q["_pos"]=pos
    bchr=bim[bim.chromosome==int(chrom)]
    for r in sub.itertuples(index=False):
        meta=lead[r.locus]; start=int(meta["region_start_GRCh37"]); end=int(meta["region_end_GRCh37"])
        x=q[(q.phenotype_id.astype(str)==str(r.gene_symbol)) & q["_pos"].between(start,end)].copy()
        b=bchr[bchr.position_GRCh37.between(start,end)]
        x=x.merge(b[["variant_id","position_GRCh37","A1","A2"]],on="variant_id",how="inner",validate="one_to_one")
        if x.empty:
            status.append({"locus":r.locus,"cell_type":cell,"gene":r.gene_symbol,"testable":False,"reason":"NO_BIM_QTL_ROWS","n_rows":0}); continue
        if (~x.af.between(0,1)).any() or (x.slope_se<=0).any():
            raise RuntimeError(f"invalid QTL values {r.locus} {cell} {r.gene_symbol}")
        x=x.rename(columns={"af":"af_A1","slope":"slope_A1","A1":"A1_effect_allele","A2":"A2_other_allele"})
        x["locus"]=r.locus; x["gene"]=r.gene_symbol; x["cell_type"]=cell; x["n_expression_donors"]=n
        x["lead_rsid"]=meta["rsid"]; x["lead_position_GRCh37"]=int(meta["position_GRCh37"]); x["risk_allele"]=meta["risk_allele"]
        rows.append(x.drop(columns=["_pos"],errors="ignore"))
        status.append({"locus":r.locus,"cell_type":cell,"gene":r.gene_symbol,"testable":True,"reason":"PASS","n_rows":len(x),
                       "qtl_min_p":float(x.pval_nominal.min()),"n_expression_donors":n})
if not rows: raise RuntimeError("no QTL rows extracted")
allq=pd.concat(rows,ignore_index=True)
if allq.duplicated(["locus","cell_type","gene","variant_id"]).any():
    raise RuntimeError("duplicate locus-cell-gene-variant keys")
allq.to_csv(OUT/"R6A2B0_OneK1K_8locus_QTL.tsv.gz",sep="\t",index=False,compression="gzip")
st=pd.DataFrame(status)
st.to_csv(OUT/"R6A2B0_OneK1K_183combo_testability.tsv",sep="\t",index=False)
audit={
 "frozen_combinations":int(len(U)),
 "testable_combinations":int(st.testable.sum()),
 "qtl_rows":int(len(allq)),
 "loci_testable":int(st[st.testable].locus.nunique()),
 "gate":"PASS" if int(st.testable.sum())==len(U) else "HOLD"
}
(AUD/"R6A2B0_OneK_QTL_gate.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print(json.dumps(audit,indent=2))
