#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


RUNS = {"HRR1849459", "HRR1849460", "HRR1849461", "HRR1849462", "HRR1849463"}


parser = argparse.ArgumentParser()
parser.add_argument("--summary-dir", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()

rows = []
for path in sorted(args.summary_dir.glob("HRR18494*_target_panel_summary.json")):
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("run") in RUNS:
        rows.append(value)
if len(rows) != 5 or {x["run"] for x in rows} != RUNS:
    raise RuntimeError(f"expected the exact five PBC liver donor summaries; found {[x.get('run') for x in rows]}")
if any(x.get("schema_version") != "CMM_R7A1C1_TARGET_PANEL_2.0" for x in rows):
    raise RuntimeError("legacy target-panel output detected; v2 called-cell outputs are required")
if any(x.get("technical_QC") != "PASS" for x in rows):
    raise RuntimeError("one or more donors failed technical QC")

f_primary = sum(bool(x["primary_FCRL3_B_detectable"]) for x in rows)
i_primary = sum(bool(x["primary_IL12RB2_NK_detectable"]) for x in rows)
f_robust = sum(bool(x["promotion_eligible_FCRL3_B"]) for x in rows)
i_robust = sum(bool(x["promotion_eligible_IL12RB2_NK"]) for x in rows)

# Project promotion requires the original >=3/5 primary rule and the v2
# pre-outcome sensitivity hardening (>=3 UMIs across >=2 lineage cells) in the
# same >=3/5 donor set for at least one target.
passed = f_robust >= 3 or i_robust >= 3
state = {
    "schema_version": "CMM_R7A1C1_LIVER_ADJUDICATION_2.0",
    "PBC_donors": 5,
    "technical_QC_donors": sum(x["technical_QC"] == "PASS" for x in rows),
    "FCRL3_B_primary_positive_donors": f_primary,
    "IL12RB2_NK_primary_positive_donors": i_primary,
    "FCRL3_B_promotion_eligible_donors": f_robust,
    "IL12RB2_NK_promotion_eligible_donors": i_robust,
    "primary_gate": "PASS" if (f_primary >= 3 or i_primary >= 3) else "FAIL",
    "promotion_gate": "PASS" if passed else "FAIL",
    "rule": "At least one target passes lineage adequacy and >=3 UMIs across >=2 target-positive called cells in >=3/5 PBC donors.",
    "next_stage": "GO_R7A2_PBC_MANUSCRIPT_SCALE" if passed else "FREEZE_PBC_REGULATORY_MAIN_NO_CED_AUTO_RESUME",
}
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
columns = [
    "run", "technical_QC", "B_gate_cells", "NK_gate_cells",
    "FCRL3_B_positive_cells", "FCRL3_B_UMI",
    "IL12RB2_NK_positive_cells", "IL12RB2_NK_UMI",
    "primary_FCRL3_B_detectable", "primary_IL12RB2_NK_detectable",
    "promotion_eligible_FCRL3_B", "promotion_eligible_IL12RB2_NK",
]
with args.out.with_suffix(".tsv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(sorted(rows, key=lambda x: x["run"]))
print(json.dumps(state, ensure_ascii=False, indent=2))
