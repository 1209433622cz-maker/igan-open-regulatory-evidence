#!/usr/bin/env python3
"""Audit public paper XLSX supplements for donor-level target evidence.
A hit is evidence discovery only; it never auto-passes the frozen 3/5 donor gate.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import pandas as pd

p=argparse.ArgumentParser()
p.add_argument("--xlsx",type=Path,required=True)
p.add_argument("--outdir",type=Path,required=True)
a=p.parse_args()
a.outdir.mkdir(parents=True,exist_ok=True)

terms=[
 "FCRL3","IL12RB2","HRR1849459","HRR1849460","HRR1849461","HRR1849462","HRR1849463",
 "PBC_liver1","PBC_liver2","PBC_liver3","PBC_liver4","PBC_liver5",
 "Naive B","Memory B","B cell","CD16- NK","CD16+ NK","NK"
]
xl=pd.ExcelFile(a.xlsx)
hits=[]
for sheet in xl.sheet_names:
    df=pd.read_excel(a.xlsx,sheet_name=sheet,header=None,dtype=str)
    context_probe=" | ".join("" if pd.isna(v) else str(v) for v in df.head(3).to_numpy().ravel())
    context=("mouse" if "mouse" in context_probe.lower() else
             "human" if "human" in context_probe.lower() else "unspecified")
    for ridx,row in df.iterrows():
        vals=[("" if pd.isna(v) else str(v)) for v in row.tolist()]
        joined=" | ".join(vals)
        for term in terms:
            if term.lower() in joined.lower():
                hits.append({"sheet":sheet,"context":context,"row_1based":int(ridx)+1,"term":term,"excerpt":joined[:1500]})
target_terms={"FCRL3","IL12RB2"}
human_target_hits=sum(x["term"] in target_terms and x["context"]=="human" for x in hits)
mouse_target_hits=sum(x["term"] in target_terms and x["context"]=="mouse" for x in hits)
donor_hits=sum(x["term"].startswith("HRR18494") or x["term"].startswith("PBC_liver") for x in hits)
summary={
 "file":str(a.xlsx),
 "bytes":a.xlsx.stat().st_size,
 "sheets":xl.sheet_names,
 "hit_count":len(hits),
 "target_hits":sum(x["term"] in target_terms for x in hits),
 "human_target_hits":human_target_hits,
 "mouse_target_hits":mouse_target_hits,
 "donor_id_hits":donor_hits,
 "frozen_donor_target_matrix_reconstructable":bool(human_target_hits and donor_hits),
 "gate_status":"CANDIDATE_ONLY_REQUIRES_MANUAL_MATRIX_AUDIT" if human_target_hits and donor_hits else "NO_DONOR_TARGET_MATRIX",
 "boundary":"Search-only. PASS requires donor × lineage × target evidence satisfying frozen >=3/5 rule."
}
pd.DataFrame(hits).to_csv(a.outdir/(a.xlsx.stem+"_hits.tsv"),sep="\t",index=False)
(a.outdir/(a.xlsx.stem+"_audit.json")).write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,indent=2))
