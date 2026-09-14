#!/usr/bin/env python3
from pathlib import Path
import os
import pandas as pd, numpy as np, json, sys
ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
OUT=ROOT/"3_results/04_integration/R6A2B0"
py=pd.read_csv(OUT/"R6A2B0_coloc_smoke_549max.tsv",sep="\t")
r=pd.read_csv(OUT/"R6A2B0_official_R_coloc_validation.tsv",sep="\t")
r0=r[np.isclose(r.p12,1e-5)].copy()
m=py.merge(r0,on=["dataset","locus","gene","cell_type"],suffixes=("_py","_r"))
diffs={}
for h in ["PP_H0","PP_H1","PP_H2","PP_H3","PP_H4"]:
    diffs[h]=float((m[h+"_py"]-m[h+"_r"]).abs().max())
maxdiff=max(diffs.values()) if diffs else None
loci=pd.read_csv(OUT/"R6A2B0_locus_adjudication.tsv",sep="\t")
robust=int((loci.status=="PASS_ROBUST_SINGLE_SIGNAL").sum())
holds=int((loci.status=="HOLD_TARGETED_LD").sum())
if robust>=2:
    decision="GO_FULL24_AFTER_TENK_REPLICATION_OF_ROBUST_LOCI"
elif robust==1:
    decision="CONDITIONAL_GO_ONE_MORE_BOUNDED_BLOCK_AFTER_REPLICATION"
elif robust==0 and holds>0:
    decision="RUN_TARGETED_SOURCE_LD_ONLY"
else:
    decision="HOLD_FULL24_REASSESS_DESIGN"
state={"python_vs_R_rows":len(m),"max_posterior_abs_diff":maxdiff,"posterior_abs_diff_by_H":diffs,
       "robust_loci":robust,"LD_trigger_loci":holds,"decision":decision,
       "locus_status":loci.to_dict("records")}
(OUT/"R6A2B0_final_machine_adjudication.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
if maxdiff is not None and maxdiff>1e-10:
    raise SystemExit("Python/R posterior mismatch exceeds tolerance")
