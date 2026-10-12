#!/usr/bin/env python3
from pathlib import Path
import argparse,json
import pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--summary-dir",required=True)
ap.add_argument("--out",required=True)
a=ap.parse_args()
d=Path(a.summary_dir)
files=sorted(d.glob("HRR18494*_target_panel_summary.json"))
rows=[]
for p in files:
    x=json.loads(p.read_text())
    if x["run"] not in {"HRR1849459","HRR1849460","HRR1849461","HRR1849462","HRR1849463"}:
        continue
    rows.append(x)
if len(rows)!=5:
    raise RuntimeError(f"Expected 5 PBC liver donor summaries, found {len(rows)}")
T=pd.DataFrame(rows)
f=int(T.primary_FCRL3_B_detectable.sum())
i=int(T.primary_IL12RB2_NK_detectable.sum())
fs=int(T.sensitivity_FCRL3_B.sum())
is_=int(T.sensitivity_IL12RB2_NK.sum())
passed=(f>=3 or i>=3)
state={
  "PBC_donors":5,
  "FCRL3_B_primary_positive_donors":f,
  "IL12RB2_NK_primary_positive_donors":i,
  "FCRL3_B_sensitivity_positive_donors":fs,
  "IL12RB2_NK_sensitivity_positive_donors":is_,
  "primary_gate":"PASS" if passed else "FAIL",
  "rule":"At least one eligible target nonzero in its predeclared liver immune lineage in >=3/5 PBC donors.",
  "next_stage":"GO_R7A2_PBC_MANUSCRIPT_SCALE" if passed else "FREEZE_PBC_REGULATORY_MAIN_NO_CED_AUTO_RESUME"
}
Path(a.out).write_text(json.dumps(state,indent=2),encoding="utf-8")
T.to_csv(Path(a.out).with_suffix(".tsv"),sep="\t",index=False)
print(json.dumps(state,indent=2))
