#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, json

ROOT=Path(r"H:\SCI2\YR1")
CODE=ROOT/"2_code/06_intake/igan_r6a2a"
MANIFEST=CODE/"R6A2A_positive_control_benchmark_v2.tsv"
PARQ=ROOT/"1_data/qtl/OneK1K/R6A2A_benchmark_members"
BIM=ROOT/"1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
SAMPLES=ROOT/"3_results/03_qtl/R5A2A2/cell_sample_lists"
OUT=ROOT/"3_results/03_qtl/R6A2A"; OUT.mkdir(parents=True,exist_ok=True)
AUD=ROOT/"3_results/00_audit/R6A2A"; AUD.mkdir(parents=True,exist_ok=True)

m=pd.read_csv(MANIFEST,sep="\t")
bim=pd.read_csv(BIM,sep=r"\s+",header=None,names=["chromosome","variant_id","cm","position_GRCh37","A1","A2"],dtype={"chromosome":int,"variant_id":str,"A1":str,"A2":str})
parts=[]; status=[]
for r in m.itertuples(index=False):
    p=PARQ/f"OneK1K_{r.cell_type}.cis_qtl_pairs.chr{r.chromosome}.parquet"
    sf=SAMPLES/f"{r.cell_type}.samples.txt"
    if not p.exists():
        status.append({**r._asdict(),"testable":False,"reason":"PARQUET_MISSING","n_rows":0}); continue
    if not sf.exists():
        status.append({**r._asdict(),"testable":False,"reason":"SAMPLE_LIST_MISSING","n_rows":0}); continue
    n=sum(1 for x in sf.read_text(encoding="utf-8").splitlines() if x.strip())
    q=pd.read_parquet(p,columns=["phenotype_id","variant_id","af","pval_nominal","slope","slope_se"])
    q=q[q.phenotype_id.astype(str)==str(r.gene)].copy()
    if q.empty:
        status.append({**r._asdict(),"testable":False,"reason":"PHENOTYPE_ABSENT","n_rows":0}); continue
    pos=pd.to_numeric(q.variant_id.str.split(":").str[1],errors="coerce")
    start=max(1,int(r.lead_position_GRCh37)-1_000_000); end=int(r.lead_position_GRCh37)+1_000_000
    q=q[pos.between(start,end)].copy()
    b=bim[(bim.chromosome==int(r.chromosome)) & bim.position_GRCh37.between(start,end)]
    q=q.merge(b[["variant_id","position_GRCh37","A1","A2"]],on="variant_id",how="inner",validate="one_to_one")
    if q.empty:
        status.append({**r._asdict(),"testable":False,"reason":"NO_BIM_OVERLAP","n_rows":0}); continue
    q=q.rename(columns={"af":"af_A1","slope":"slope_A1","A1":"A1_effect_allele","A2":"A2_other_allele"})
    q["locus"]=r.locus; q["gene"]=r.gene; q["cell_type"]=r.cell_type; q["benchmark_role"]=r.benchmark_role
    q["lead_rsid"]=r.lead_rsid; q["lead_position_GRCh37"]=int(r.lead_position_GRCh37); q["risk_allele"]=r.risk_allele
    q["n_expression_donors"]=n
    parts.append(q)
    status.append({**r._asdict(),"testable":True,"reason":"PASS","n_rows":len(q),"n_expression_donors":n,"qtl_min_p":float(q.pval_nominal.min())})
if parts:
    allq=pd.concat(parts,ignore_index=True)
    if allq.duplicated(["locus","gene","cell_type","variant_id"]).any(): raise RuntimeError("duplicate QTL keys")
    allq.to_csv(OUT/"R6A2A_OneK1K_benchmark_QTL.tsv.gz",sep="\t",index=False,compression="gzip")
st=pd.DataFrame(status)
st.to_csv(OUT/"R6A2A_OneK1K_benchmark_testability.tsv",sep="\t",index=False)
audit={"benchmarks":len(m),"testable":int(st.testable.sum()),"published_cell_primary_testable":int(st[(st.benchmark_role=="PUBLISHED_CELL_CLASS_PRIMARY") & st.testable].shape[0]),"gate":"PASS" if st.testable.sum()>=5 else "HOLD"}
(AUD/"R6A2A_OneK1K_benchmark_QTL_gate.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print(json.dumps(audit,indent=2))
