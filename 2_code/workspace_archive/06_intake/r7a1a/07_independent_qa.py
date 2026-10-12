#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, os, zipfile
from pathlib import Path

HERE=Path(__file__).resolve()
DEFAULT_ROOT=HERE.parents[2] if (HERE.parents[2]/".git").exists() else HERE.parents[3]
ROOT=Path(os.environ.get("R7_PROJECT_ROOT",DEFAULT_ROOT))
I=ROOT/"3_results/01_intake/R7A1A"; Q=ROOT/"3_results/03_qtl/R7A1A"
OUT=ROOT/"3_results/00_audit/R7A1A"; OUT.mkdir(parents=True,exist_ok=True)
checks=[]
def check(name,ok,observed):
    checks.append({"check":name,"status":"PASS" if ok else "FAIL","observed":observed})

pbc=ROOT/"1_data/gwas/R7A1A/PBC/GCST90061440_buildGRCh37.tsv"
h=hashlib.md5()
with pbc.open("rb") as f:
    for b in iter(lambda:f.read(8*1024*1024),b""): h.update(b)
check("PBC_official_MD5",h.hexdigest()=="c48ede08359f6fc919810591cc0daad7",h.hexdigest())
ps=json.loads((I/"R7A1A_PBC_GWAS_byte_schema_audit.json").read_text())
cs=json.loads((I/"R7A1A_CeD_GWAS_byte_schema_audit.json").read_text())
check("PBC_rows",ps["rows"]==5_054_572,ps["rows"])
check("PBC_valid_rows",ps["valid_numeric_rows"]==ps["rows"],ps["valid_numeric_rows"])
check("PBC_nonMHC_gate",ps["provisional_1Mb_distance_pruned_GWS_leads"]>=5,ps["provisional_1Mb_distance_pruned_GWS_leads"])
check("CeD_schema",cs["gate_schema"]=="PASS",cs["gate_schema"])
check("CeD_nonMHC_gate",cs["provisional_1Mb_distance_pruned_GWS_leads"]>=5,cs["provisional_1Mb_distance_pruned_GWS_leads"])
gj=json.loads((I/"R7A1A_PBC_GJOKA_remote_inventory_state.json").read_text())
check("GJOKA_pairs",gj["sumstats_members"]==gj["ld_members"]==gj["matched_locus_pairs"]==56,gj)
qs=json.loads((Q/"R7A1A_QTL_control_testability_state.json").read_text())
check("PBC_3of3_testable",qs["PBC"]["cross_resource_byte_testable"]==3,qs["PBC"])
check("PBC_2of3_positive",qs["PBC"]["cross_resource_source_positive"]==2,qs["PBC"])
check("CeD_3of3_testable",qs["CeD"]["cross_resource_byte_testable"]==3,qs["CeD"])
check("CeD_1of3_positive",qs["CeD"]["cross_resource_source_positive"]==1,qs["CeD"])
st=json.loads((I/"R7A1A_final_state.json").read_text())
check("decision",st["pbc"].startswith("GO_R7A1B") and st["ced"]=="HOLD_NOT_SELECTED",st)
result={"status":"PASS" if all(x["status"]=="PASS" for x in checks) else "FAIL","checks":checks}
(OUT/"R7A1A_independent_QA.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(result,indent=2,ensure_ascii=False))
raise SystemExit(0 if result["status"]=="PASS" else 1)
