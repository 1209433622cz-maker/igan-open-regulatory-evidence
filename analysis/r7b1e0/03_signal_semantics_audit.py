#!/usr/bin/env python3
"""Audit comparison-level versus same-signal-pair stability across PF10 L."""
from __future__ import annotations

import gzip
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(r"H:\SCI2\YR1")
BASE=ROOT/"3_results/04_integration/R7B1B_v2"
FINAL=pd.read_csv(BASE/"adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv",sep="\t",dtype={"comparison_id":str})
POST=pd.read_csv(BASE/"adjudication/R7B1B_v2_all_signal_pair_posteriors.tsv.gz",sep="\t",dtype={"comparison_id":str})
OUT=ROOT/"3_results/04_integration/R7B1E0/signal_semantics"
CONFIGS=("PF10_L5","PF10_L10","PF10_L20")

def qualifying(frame:pd.DataFrame,kind:str)->pd.DataFrame:
    d=frame[np.isclose(frame.p12,1e-5)].copy()
    if kind=="H4":
        low=frame[np.isclose(frame.p12,1e-6)].copy()
        low["pair"]=low.idx1.astype(str)+"|"+low.idx2.astype(str)
        ratios=low.groupby("pair").H4_over_H3H4.max().to_dict()
        d["pair"]=d.idx1.astype(str)+"|"+d.idx2.astype(str)
        return d[(d["PP.H4.abf"]>=.8)&(d.H4_over_H3H4>=.8)&d.pair.map(ratios).fillna(-np.inf).ge(.5)]
    return d[(d["PP.H3.abf"]>=.8)&(d.H4_over_H3H4<=.2)].copy()

def jaccard(a:set[str],b:set[str])->float:
    return len(a&b)/len(a|b) if a|b else 0.0

def main()->None:
    OUT.mkdir(parents=True,exist_ok=True)
    cs_by_id:dict[str,pd.DataFrame]={}
    for row in FINAL.itertuples(index=False):
        p=BASE/"multisignal"/f"locus_{int(row.locus_index):02d}"/f"{row.comparison_id}_credible_set_members.tsv.gz"
        cs_by_id[row.comparison_id]=pd.read_csv(p,sep="\t",dtype={"comparison_id":str}) if p.exists() else pd.DataFrame()
    details=[]; summary=[]
    for row in FINAL.itertuples(index=False):
        cid=row.comparison_id; p=POST[POST.comparison_id==cid]; cs=cs_by_id[cid]
        state=row.PF10_multisignal_state
        kind="H4" if state=="H4_SUPPORTED_STABLE" else "H3" if state=="H3_SUPPORTED_STABLE" else "NA"
        q={cfg:qualifying(p[p.config==cfg],"H4") for cfg in CONFIGS}
        h3={cfg:qualifying(p[p.config==cfg],"H3") for cfg in CONFIGS}
        mixed=any(len(q[cfg])>0 and len(h3[cfg])>0 for cfg in CONFIGS)
        matches=[]
        if kind!="NA":
            source=q if kind=="H4" else h3
            anchor=source["PF10_L10"]
            for cfg in ("PF10_L5","PF10_L20"):
                for a in anchor.itertuples(index=False):
                    for b in source[cfg].itertuples(index=False):
                        exact=(str(a.hit1)==str(b.hit1) and str(a.hit2)==str(b.hit2))
                        vals={}
                        for trait,idxa,idxb in [("PBC",a.idx1,b.idx1),("OneK_QTL",a.idx2,b.idx2)]:
                            sa=set(cs[(cs.config=="PF10_L10")&(cs.trait==trait)&(cs.credible_set==f"L{int(idxa)}")].variant_id.astype(str))
                            sb=set(cs[(cs.config==cfg)&(cs.trait==trait)&(cs.credible_set==f"L{int(idxb)}")].variant_id.astype(str))
                            vals[trait]=jaccard(sa,sb)
                        cs_match=vals["PBC"]>=.5 and vals["OneK_QTL"]>=.5
                        matches.append((cfg,exact,cs_match,vals["PBC"],vals["OneK_QTL"],a,b))
                        details.append({"comparison_id":cid,"kind":kind,"other_config":cfg,
                          "anchor_idx1":a.idx1,"anchor_idx2":a.idx2,"other_idx1":b.idx1,"other_idx2":b.idx2,
                          "anchor_hit1":a.hit1,"anchor_hit2":a.hit2,"other_hit1":b.hit1,"other_hit2":b.hit2,
                          "exact_lead_pair":exact,"disease_cs_jaccard":vals["PBC"],"qtl_cs_jaccard":vals["OneK_QTL"],"cs_pair_match":cs_match})
        supporting=sorted({m[0] for m in matches if m[1] or m[2]})
        confirmed=(kind!="NA" and len(supporting)>=1)
        if kind=="H4": semantic="H4_SAME_SIGNAL_PAIR_STABLE" if confirmed else "H4_COMPARISON_STABLE_SIGNAL_IDENTITY_UNCONFIRMED"
        elif kind=="H3": semantic="H3_DISTINCT_PAIR_STABLE_NOT_GLOBAL_ABSENCE" if confirmed else "H3_COMPARISON_STABLE_SIGNAL_IDENTITY_UNCONFIRMED"
        else: semantic="NOT_APPLICABLE"
        if mixed: semantic += "__MIXED_SHARED_AND_DISTINCT_PAIRS"
        summary.append({"comparison_id":cid,"locus_index":row.locus_index,"gene":row.gene,"cell_type":row.cell_type,
          "historical_PF10_multisignal_state":state,"semantic_state":semantic,"anchor_kind":kind,
          "same_signal_pair_confirmed":confirmed,"supporting_other_configs":";".join(supporting),
          "mixed_h4_h3_within_any_config":mixed})
    S=pd.DataFrame(summary); D=pd.DataFrame(details)
    S.to_csv(OUT/"R7B1E0_signal_semantics_642.tsv",sep="\t",index=False)
    D.to_csv(OUT/"R7B1E0_signal_pair_match_details.tsv.gz",sep="\t",index=False,compression={"method":"gzip","mtime":0})
    counts=Counter(S.semantic_state)
    state={"schema":"R7B1E0_SIGNAL_SEMANTICS_1.0","status":"PASS","comparisons":len(S),
      "historical_state_counts":dict(sorted(Counter(S.historical_PF10_multisignal_state).items())),
      "semantic_state_counts":dict(sorted(counts.items())),
      "stable_h4_same_signal_confirmed":int(((S.historical_PF10_multisignal_state=="H4_SUPPORTED_STABLE")&S.same_signal_pair_confirmed).sum()),
      "stable_h3_same_pair_confirmed":int(((S.historical_PF10_multisignal_state=="H3_SUPPORTED_STABLE")&S.same_signal_pair_confirmed).sum()),
      "mixed_shared_and_distinct":int(S.mixed_h4_h3_within_any_config.sum()),
      "historical_labels_overwritten":False,
      "interpretation":"comparison stability and signal-pair identity are reported separately; H3 pair support is not global proof of no shared pair"}
    (OUT/"R7B1E0_signal_semantics_state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state,indent=2))

if __name__=="__main__": main()
