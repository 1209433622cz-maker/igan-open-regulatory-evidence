#!/usr/bin/env python3
"""Independent mechanical QA for the R7B1E0 closure."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT=Path(r"H:\SCI2\YR1")
BASE=ROOT/"3_results/04_integration/R7B1E0"
OUT=ROOT/"3_results/00_audit/R7B1E0"

def main()->None:
    OUT.mkdir(parents=True,exist_ok=True)
    diag=json.loads((BASE/"diagnostic_adjudication/R7B1E0_diagnostic_adjudication_state.json").read_text(encoding="utf-8"))
    sem=json.loads((BASE/"signal_semantics/R7B1E0_signal_semantics_state.json").read_text(encoding="utf-8"))
    S=pd.read_csv(BASE/"diagnostic_adjudication/R7B1E0_all_diagnostic_units.tsv.gz",sep="\t")
    R=pd.read_csv(BASE/"diagnostic_adjudication/R7B1E0_official_kriging_flags_review.tsv",sep="\t")
    M=pd.read_csv(BASE/"signal_semantics/R7B1E0_signal_semantics_642.tsv",sep="\t")
    checks=[]
    def add(name,ok,observed,expected): checks.append({"name":name,"pass":bool(ok),"observed":observed,"expected":expected})
    add("diagnostic_units_2568",len(S)==2568,len(S),2568)
    add("diagnostic_comparisons_642",S.comparison_id.nunique()==642,S.comparison_id.nunique(),642)
    add("diagnostic_loci_47",S.locus_index.nunique()==47,S.locus_index.nunique(),47)
    add("all_diagnostics_pass",(S.status=="PASS").all(),S.status.value_counts().to_dict(),{"PASS":2568})
    add("variant_rows_complete",(S.variants_expected==S.variants_returned).all(),int((S.variants_expected==S.variants_returned).sum()),2568)
    add("finite_rows_complete",(S.variants_expected==S.finite_rows).all(),int((S.variants_expected==S.finite_rows).sum()),2568)
    add("historical_count_preserved",int(S.historical_logLR_gt2_n.sum())==3333,int(S.historical_logLR_gt2_n.sum()),3333)
    add("official_raw_flags_two",int(S.official_logLR_gt2_absz_gt2_n.sum())==2,int(S.official_logLR_gt2_absz_gt2_n.sum()),2)
    add("official_unique_event_one",R.event_id.nunique()==1,R.event_id.nunique(),1)
    add("official_event_reviewed",set(R.review_status)=={"REVIEWED_RETAIN_INPUT_NO_REFIT"},sorted(R.review_status.unique()),["REVIEWED_RETAIN_INPUT_NO_REFIT"])
    add("official_event_not_in_CS",not R.in_any_credible_set.astype(bool).any(),bool(R.in_any_credible_set.astype(bool).any()),False)
    add("no_posterior_refit",diag["posterior_refit_required"] is False,diag["posterior_refit_required"],False)
    add("historical_labels_unchanged",diag["historical_classifications_changed"] is False,diag["historical_classifications_changed"],False)
    add("semantics_642",len(M)==642,len(M),642)
    add("historical_H4_92",(M.historical_PF10_multisignal_state=="H4_SUPPORTED_STABLE").sum()==92,int((M.historical_PF10_multisignal_state=="H4_SUPPORTED_STABLE").sum()),92)
    add("H4_same_signal_92",sem["stable_h4_same_signal_confirmed"]==92,sem["stable_h4_same_signal_confirmed"],92)
    add("historical_H3_428",(M.historical_PF10_multisignal_state=="H3_SUPPORTED_STABLE").sum()==428,int((M.historical_PF10_multisignal_state=="H3_SUPPORTED_STABLE").sum()),428)
    add("H3_same_pair_428",sem["stable_h3_same_pair_confirmed"]==428,sem["stable_h3_same_pair_confirmed"],428)
    add("mixed_pairs_32",sem["mixed_shared_and_distinct"]==32,sem["mixed_shared_and_distinct"],32)
    add("labels_not_overwritten",sem["historical_labels_overwritten"] is False,sem["historical_labels_overwritten"],False)
    add("protocol_exists",(ROOT/"0_admin/protocols/R7B1E0/R7B1E0_diagnostic_replay_signal_semantics_freeze_2026-10-09.md").exists(),True,True)
    status="PASS" if all(x["pass"] for x in checks) else "FAIL"
    pd.DataFrame(checks).to_csv(OUT/"R7B1E0_independent_QA.tsv",sep="\t",index=False)
    state={"schema":"R7B1E0_QA_1.0","status":status,"passed":sum(x["pass"] for x in checks),"total":len(checks),"checks":checks,
      "gate":"PASS_TO_R7B1E" if status=="PASS" else "HOLD"}
    (OUT/"R7B1E0_independent_QA.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state,indent=2))
    if status!="PASS": raise SystemExit(2)

if __name__=="__main__": main()
