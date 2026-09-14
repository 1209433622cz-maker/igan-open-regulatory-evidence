from __future__ import annotations
import os,json
from pathlib import Path
ROOT=Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
INT=ROOT/"3_results/04_integration/R6A3A"
AUD=ROOT/"3_results/00_audit/R6A3A"
PQ=INT/"R6A3A_pqtl_track_state.json"
KD=AUD/"R6A3A_ZMIZ1_kidney_primary_gate.json"
if not PQ.exists() or not KD.exists(): raise RuntimeError("Track A/B state files missing")
pq=json.loads(PQ.read_text()); kd=json.loads(KD.read_text())
receipts=[AUD/"R6A3A_Sun2018_small_byte_receipt.tsv",AUD/"R6A3A_GSE127136_byte_receipt.tsv"]
provenance=all(path.exists() for path in receipts)
trackA=pq.get("status")=="PASS"
trackB=kd.get("status") in {"PASS_SUPPORTIVE_CASE_LOWER","INTERPRETABLE_DONOR_LEVEL"}
if provenance and trackA and trackB:
    final="GO_R6A4_MANUSCRIPT_SCALE_COMPLETION"
    project="GO_COMPLETION_FIRST"
else:
    final="FREEZE_IGAN_REGULATORY_MAIN__NEW_TOPIC_PREFLIGHT"
    project="FROZEN_ARCHIVE"
state={"R6A3A":"COMPLETE","PUBLIC_BYTE_LEVEL_PROVENANCE":"PASS" if provenance else "FAIL_MISSING_RECEIPT",
       "AT_LEAST_ONE_ADDITIONAL_LOCUS_PQTL_SHARED_SIGNAL":"PASS" if trackA else "FAIL",
       "ZMIZ1_KIDNEY_DONOR_LEVEL_LOCALIZATION":"PASS_OR_INTERPRETABLE" if trackB else "FAIL",
       "CORE_CLAIM_REQUIRES_PERMISSION_DATA":False,"TARGET_SELECTION_WAS_PRE_FROZEN":True,
       "IGAN_REGULATORY_MAIN":project,"NEXT_STAGE":final}
(INT/"R6A3A_final_adjudication.json").write_text(json.dumps(state,indent=2),encoding="utf-8")
print(json.dumps(state,indent=2))
