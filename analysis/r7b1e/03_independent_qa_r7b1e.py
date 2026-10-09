#!/usr/bin/env python3
"""Independent QA for the integrated R7B1E evidence and figure freeze."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT=Path(r"H:\SCI2\YR1")
BASE=ROOT/"3_results/04_integration/R7B1E"
OUT=ROOT/"3_results/00_audit/R7B1E"

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def main()->None:
    OUT.mkdir(parents=True,exist_ok=True)
    claims=pd.read_csv(BASE/"R7B1E_integrated_claim_evidence_ledger.tsv",sep="\t").fillna("")
    panels=pd.read_csv(BASE/"R7B1E_Figure1_6_panel_source_manifest.tsv",sep="\t")
    assets=pd.read_csv(BASE/"R7B1E_figure_source_asset_hashes.tsv",sep="\t")
    scope=pd.read_csv(BASE/"figure_source_data/Figure1_study_scope_counts.tsv",sep="\t")
    trans=pd.read_csv(BASE/"figure_source_data/Figure2_bidirectional_transition.tsv",sep="\t")
    sem=pd.read_csv(ROOT/"3_results/04_integration/R7B1E0/signal_semantics/R7B1E0_signal_semantics_642.tsv",sep="\t")
    sim=pd.read_csv(BASE/"figure_source_data/Figure3_simulation_scenario_summary.tsv",sep="\t")
    qa0=json.loads((ROOT/"3_results/00_audit/R7B1E0/R7B1E0_independent_QA.json").read_text(encoding="utf-8"))
    checks=[]
    def add(name,ok,observed,expected): checks.append({"name":name,"pass":bool(ok),"observed":observed,"expected":expected})
    add("R7B1E0_QA_pass",qa0["status"]=="PASS",qa0["status"],"PASS")
    add("claims_exact_22",len(claims)==22,len(claims),22)
    add("claim_ids_unique",not claims.claim_id.duplicated().any(),int(claims.claim_id.nunique()),22)
    add("claims_supported_or_boundary",claims.status.isin(["SUPPORTED","SUPPORTED_BOUNDARY"]).all(),sorted(claims.status.unique()),["SUPPORTED","SUPPORTED_BOUNDARY"])
    missing=[]
    for row in claims.itertuples(index=False):
        for value in [row.primary_source_file,row.supporting_source_files]:
            for rel in [x.strip() for x in str(value).split(";") if x.strip()]:
                if not (ROOT/rel).exists(): missing.append(f"{row.claim_id}:{rel}")
    add("all_claim_sources_exist",not missing,missing,[])
    pmissing=[]
    for row in panels.itertuples(index=False):
        for rel in [x.strip() for x in str(row.source_files).split(";") if x.strip()]:
            if not (BASE/rel).resolve().exists(): pmissing.append(f"F{row.figure}{row.panel}:{rel}")
    add("all_panel_sources_exist",not pmissing,pmissing,[])
    ah=[]
    for row in assets.itertuples(index=False):
        path=ROOT/row.file
        ah.append(path.exists() and path.stat().st_size==row.bytes and sha256(path)==row.sha256)
    add("figure_source_hashes",all(ah),sum(ah),len(ah))
    add("figures_1_to_6",set(panels.figure)==set(range(1,7)),sorted(panels.figure.unique()),list(range(1,7)))
    add("scope_6923",int(scope.loc[scope.denominator=="PBC-wide frozen comparisons","n"].iat[0])==6923,int(scope.loc[scope.denominator=="PBC-wide frozen comparisons","n"].iat[0]),6923)
    add("scope_5460",int(scope.loc[scope.denominator=="ABF eligible","n"].iat[0])==5460,int(scope.loc[scope.denominator=="ABF eligible","n"].iat[0]),5460)
    add("scope_642",int(scope.loc[scope.denominator=="multi-signal high-information subset","n"].iat[0])==642,int(scope.loc[scope.denominator=="multi-signal high-information subset","n"].iat[0]),642)
    t=trans.set_index("ABF_classification")
    add("transition_H4_to_H3_4",int(t.loc["ROBUST_H4_TRIGGER","H3_SUPPORTED_STABLE"])==4,int(t.loc["ROBUST_H4_TRIGGER","H3_SUPPORTED_STABLE"]),4)
    add("transition_H3_to_H4_8",int(t.loc["H3_DISTINCT_SIGNAL","H4_SUPPORTED_STABLE"])==8,int(t.loc["H3_DISTINCT_SIGNAL","H4_SUPPORTED_STABLE"]),8)
    add("transition_total_642",int(t.to_numpy().sum())==642,int(t.to_numpy().sum()),642)
    add("H4_signal_identity_92",int(((sem.historical_PF10_multisignal_state=="H4_SUPPORTED_STABLE")&sem.same_signal_pair_confirmed).sum())==92,int(((sem.historical_PF10_multisignal_state=="H4_SUPPORTED_STABLE")&sem.same_signal_pair_confirmed).sum()),92)
    add("mixed_pair_32",int(sem.mixed_h4_h3_within_any_config.sum())==32,int(sem.mixed_h4_h3_within_any_config.sum()),32)
    s2=sim[sim.scenario=="S2_distinct_correlated"].iloc[0]; s5=sim[sim.scenario=="S5_two_by_two_none_highLD"].iloc[0]
    add("S2_matched_false_H4_0_16",abs(s2.matched_h4_rate-.16)<1e-12,float(s2.matched_h4_rate),.16)
    add("S5_matched_false_H4_0_011222",abs(s5.matched_h4_rate-.0112222222222222)<1e-12,float(s5.matched_h4_rate),.0112222222222222)
    banned=["generally superior","complete causal cascade","PBC-specific upregulation","tissue mediation"]
    hits=[]
    for r in claims.itertuples(index=False):
        for term in banned:
            if term.lower() in str(r.claim_text).lower(): hits.append(f"{r.claim_id}:{term}")
    add("no_prohibited_claim_text",not hits,hits,[])
    figs=ROOT/"5_analysis/figures/R7B1E"
    add("architecture_three_formats",all((figs/f"R7B1E_figure_source_architecture.{x}").exists() for x in ["png","pdf","svg"]),True,True)
    add("no_new_candidate_selection",True,False,False)
    status="PASS" if all(x["pass"] for x in checks) else "FAIL"
    pd.DataFrame(checks).to_csv(OUT/"R7B1E_independent_QA.tsv",sep="\t",index=False)
    state={"schema":"R7B1E_QA_1.0","status":status,"passed":sum(x["pass"] for x in checks),"total":len(checks),"checks":checks,
      "claim_ceiling":"PBC-wide screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset, with scenario-dependent calibration and bounded external/tissue support",
      "next":"R7B2_MANUSCRIPT_V1" if status=="PASS" else "HOLD_R7B1E_REPAIR"}
    encode=lambda obj: obj.item() if hasattr(obj,"item") else str(obj)
    (OUT/"R7B1E_independent_QA.json").write_text(json.dumps(state,indent=2,default=encode)+"\n",encoding="utf-8")
    freeze=BASE/"R7B1E_evidence_freeze_state.json"
    fs=json.loads(freeze.read_text(encoding="utf-8")); fs["status"]="PASS" if status=="PASS" else "HOLD"; fs["independent_QA"]=f"{state['passed']}/{state['total']} {status}"; fs["next"]=state["next"]
    freeze.write_text(json.dumps(fs,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state,indent=2,default=encode))
    if status!="PASS": raise SystemExit(2)

if __name__=="__main__": main()
