#!/usr/bin/env python3
from pathlib import Path
import re, json
import pandas as pd
import pyarrow.parquet as pq

ROOT=Path(r"H:\SCI2\YR1")
QTL_DIR=ROOT/"1_data/qtl/OneK1K/R5A2B_chr5_members"
BIM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
SAMPLE_DIR=ROOT/"3_results/03_qtl/R5A2A2/cell_sample_lists"
OUT=ROOT/"3_results/03_qtl/R5A2B"; OUT.mkdir(parents=True,exist_ok=True)
AUDIT=ROOT/"3_results/00_audit/R5A2B"; AUDIT.mkdir(parents=True,exist_ok=True)
LEAD_POS=150447128; START=149447128; END=151447128
BOUNDED=['TNIP1', 'ANXA6', 'ATOX1', 'CCDC69', 'GM2A', 'RPS14', 'SLC36A1', 'TCOF1']
PAT=re.compile(r"OneK1K_(.+?)\.cis_qtl_pairs\.chr5\.parquet$")

bim=[]
with BIM.open(encoding="utf-8") as f:
    for idx,line in enumerate(f):
        chrom,vid,cm,pos,a1,a2=line.split()
        if chrom=="5" and START<=int(pos)<=END:
            bim.append((vid,int(pos),a1,a2,idx))
bimdf=pd.DataFrame(bim,columns=["variant_id","position_GRCh37","A1_effect_allele","A2_other_allele","global_bim_index_zero_based"])
bim_map=set(bimdf.variant_id)

rows=[]; summaries=[]
files=sorted(QTL_DIR.glob("OneK1K_*.cis_qtl_pairs.chr5.parquet"))
if len(files)!=14:
    raise RuntimeError(f"Expected 14 chr5 parquet files, found {len(files)}")
for p in files:
    m=PAT.fullmatch(p.name)
    if not m: continue
    cell=m.group(1)
    sample_file=SAMPLE_DIR/f"{cell}.samples.txt"
    if not sample_file.exists(): raise RuntimeError(f"Missing frozen sample list {sample_file}")
    n=sum(1 for x in sample_file.read_text(encoding="utf-8").splitlines() if x.strip())
    df=pd.read_parquet(p,columns=["phenotype_id","variant_id","af","pval_nominal","slope","slope_se"])
    pos=pd.to_numeric(df["variant_id"].str.split(":").str[1],errors="coerce")
    x=df[(pos>=START)&(pos<=END)&df["phenotype_id"].isin(BOUNDED)].copy()
    if x.empty: continue
    x["cell_type"]=cell; x["n_expression_donors"]=n
    x=x.merge(bimdf,on="variant_id",how="inner",validate="many_to_one")
    if x.empty: continue
    if (~x["af"].between(0,1)).any() or (x["slope_se"]<=0).any():
        raise RuntimeError(f"Invalid QTL statistics in {cell}")
    x=x.rename(columns={"af":"af_A1","slope":"slope_A1"})
    rows.append(x)
    for gene,g in x.groupby("phenotype_id"):
        top=g.loc[g.pval_nominal.idxmin()]
        summaries.append({
            "cell_type":cell,"phenotype_id":gene,"n_expression_donors":n,"n_variants":len(g),
            "lead_present":bool((g.variant_id=="5:150447128").any()),
            "qtl_top_variant":top.variant_id,"qtl_top_p":float(top.pval_nominal)
        })
if not rows: raise RuntimeError("No bounded chr5 QTL rows extracted")
allq=pd.concat(rows,ignore_index=True)
if allq.duplicated(["cell_type","phenotype_id","variant_id"]).any():
    raise RuntimeError("Duplicate cell-gene-variant rows")
allq.to_csv(OUT/"OneK1K_chr5_bounded_region_pairs.tsv.gz",sep="\t",index=False,compression="gzip")
pd.DataFrame(summaries).sort_values(["phenotype_id","cell_type"]).to_csv(OUT/"OneK1K_chr5_bounded_cell_gene_summary.tsv",sep="\t",index=False)
state={
 "status":"PASS","region":"GRCh37 chr5:149447128-151447128","lead":"5:150447128",
 "bounded_genes":BOUNDED,"n_rows":int(len(allq)),"n_cells":int(allq.cell_type.nunique()),
 "n_genes":int(allq.phenotype_id.nunique()),"n_cell_gene":int(allq.groupby(["cell_type","phenotype_id"]).ngroups)
}
(AUDIT/"OneK1K_chr5_bounded_qtl_audit.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
