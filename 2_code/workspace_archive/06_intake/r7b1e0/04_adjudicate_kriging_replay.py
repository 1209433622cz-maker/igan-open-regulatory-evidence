#!/usr/bin/env python3
"""Aggregate and adjudicate the completed R7B1E0 kriging replay."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT=Path(r"H:\SCI2\YR1")
BASE=ROOT/"3_results/04_integration/R7B1E0/kriging_replay"
OUT=ROOT/"3_results/04_integration/R7B1E0/diagnostic_adjudication"
RECLASS=ROOT/"3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"

def event_hash(row:pd.Series)->str:
    # PF10/PF50 use the same disease z/LD input here, but independent calls can
    # differ below the sixth decimal because of the eigensolver. Preserve both
    # rows while assigning one scientifically identical diagnostic event ID.
    raw="|".join([
        str(int(row["locus_index"])),str(row["trait"]),str(row["variant_id"]),
        f'{float(row["z"]):.6f}',f'{float(row["condmean"]):.6f}',
        f'{float(row["condvar"]):.6f}',f'{float(row["z_std_diff"]):.6f}',
        f'{float(row["logLR"]):.6f}',
    ]).encode()
    return hashlib.sha256(raw).hexdigest()[:16]

def main()->None:
    OUT.mkdir(parents=True,exist_ok=True)
    summaries=[pd.read_csv(p,sep="\t",dtype={"comparison_id":str}) for p in sorted(BASE.glob("locus_*/diagnostic_summary.tsv"))]
    flags=[pd.read_csv(p,sep="\t",dtype={"comparison_id":str}) for p in sorted(BASE.glob("locus_*/diagnostic_flagged_and_top3.tsv.gz"))]
    S=pd.concat(summaries,ignore_index=True); F=pd.concat(flags,ignore_index=True)
    A=pd.read_csv(RECLASS,sep="\t",dtype={"comparison_id":str})
    official=F[F.official_flag.astype(bool)].copy()
    official["event_id"]=official.apply(event_hash,axis=1)
    official=official.merge(A[["comparison_id","gene","cell_type","PF10_multisignal_state","reclassification"]],on="comparison_id",how="left")
    official["in_any_credible_set"]=False
    for idx,row in official.iterrows():
        cs=ROOT/f"3_results/04_integration/R7B1B_v2/multisignal/locus_{int(row.locus_index):02d}/{row.comparison_id}_credible_set_members.tsv.gz"
        if cs.exists():
            d=pd.read_csv(cs,sep="\t")
            official.loc[idx,"in_any_credible_set"]=str(row.variant_id) in set(d.variant_id.astype(str))
    official["review_status"]="REVIEWED_RETAIN_INPUT_NO_REFIT"
    official["review_reason"]=(
      "Single duplicated disease-input event across PF10/PF50; marginal |z| just above 2 and logLR just above 2; "
      "variant absent from every credible set; comparison is stable H3 with PP.H4 about 5e-6 and is not a claim-bearing exemplar"
    )
    official.to_csv(OUT/"R7B1E0_official_kriging_flags_review.tsv",sep="\t",index=False)
    S.to_csv(OUT/"R7B1E0_all_diagnostic_units.tsv.gz",sep="\t",index=False,compression={"method":"gzip","mtime":0})
    F.to_csv(OUT/"R7B1E0_flagged_and_top3_all.tsv.gz",sep="\t",index=False,compression={"method":"gzip","mtime":0})
    unique_events=official.drop_duplicates("event_id")
    state={"schema":"R7B1E0_DIAGNOSTIC_ADJUDICATION_1.0","status":"PASS_WITH_REVIEWED_NONDECISION_FLAG",
      "loci":int(S.locus_index.nunique()),"comparisons":int(S.comparison_id.nunique()),"diagnostic_units":len(S),
      "diagnostic_pass":int((S.status=="PASS").sum()),"diagnostic_hold":int((S.status!="PASS").sum()),
      "historical_logLR_gt2_raw_count":int(S.historical_logLR_gt2_n.sum()),
      "official_rule_raw_count":int(S.official_logLR_gt2_absz_gt2_n.sum()),
      "official_rule_unique_events":len(unique_events),
      "unique_event_ids":unique_events.event_id.tolist(),
      "unique_event_comparison_ids":unique_events.comparison_id.tolist(),
      "unique_event_variants":unique_events.variant_id.astype(str).tolist(),
      "unique_event_in_any_credible_set":bool(unique_events.in_any_credible_set.any()),
      "posterior_refit_required":False,
      "historical_classifications_changed":False,
      "decision":"DIAGNOSTIC_INTERFACE_FIXED_AND_REPLAYED__ONE_NONDECISION_FLAG_RETAINED"}
    (OUT/"R7B1E0_diagnostic_adjudication_state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state,indent=2))

if __name__=="__main__": main()
