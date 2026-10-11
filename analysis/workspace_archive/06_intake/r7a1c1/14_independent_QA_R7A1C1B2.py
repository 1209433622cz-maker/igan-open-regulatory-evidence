#!/usr/bin/env python3
"""Independent closeout QA for the completed five-donor PBC liver gate."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
CODE = ROOT / "2_code/06_intake/r7a1c1"
RESULT = ROOT / "3_results/05_tissue/R7A1C1"
AUDIT = ROOT / "3_results/00_audit/R7A1C1"
MANIFEST = ROOT / "1_data/scrna/PBC/HRA008003/manifests/HRA008003_PBC_liver_primary_run_manifest_v2.tsv"
OFFICIAL_FINAL = RESULT / "R7A1C1_liver_final_adjudication_v2.json"
INDEPENDENT_FINAL = ROOT / "3_results/00_audit/R7A1C1B2_independent_final_adjudication.json"
OUT = ROOT / "3_results/00_audit/R7A1C1B2_independent_QA.json"
BAM_DIR = ROOT / "1_data/scrna/PBC/HRA008003/bam"
RUNS = [f"HRR18494{i}" for i in range(59, 64)]

FROZEN_HASHES = {
    "02_hra_bam_target_panel_v2.py": "a88a8d061332322e3182dc259bf4a47b5bb507a30047d278a370932654d9a7a2",
    "03_adjudicate_HRA008003_liver_gate_v2.py": "9a7bc06111e945296911b44cbd6d10e065a83ca475b6456a4c425eaad5b04eae",
    "08_check_HRA008003_bam_schema_v1_2.py": "495f699e6d457f22bd406787b046917962349208e831de4c56e65acea02f0418",
    "RUN_R7A1C1_HRA008003_TARGET_PANEL_v3_2.ps1": "1b072dc93ca9354211eee155809e33edd36766c0366d5353113c386d03a6b071",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


checks: list[dict] = []


def check(name: str, passed: bool, evidence: object) -> None:
    checks.append({"name": name, "status": "PASS" if passed else "FAIL", "evidence": evidence})


with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
    manifest = {row["run_accession"]: row for row in csv.DictReader(handle, delimiter="\t")}
check("manifest_exact_five", set(manifest) == set(RUNS), sorted(manifest))

observed_code_hashes = {name: sha256(CODE / name) for name in FROZEN_HASHES}
check("frozen_biological_and_runner_code", observed_code_hashes == FROZEN_HASHES, observed_code_hashes)

with (AUDIT / "R7A1C1_HRA008003_receipts_v2.tsv").open(encoding="utf-8-sig", newline="") as handle:
    receipt_rows = list(csv.DictReader(handle, delimiter="\t"))
receipts = {row["run"]: row for row in receipt_rows}
check("receipt_exact_five_unique", len(receipt_rows) == 5 and set(receipts) == set(RUNS), sorted(receipts))

donor_evidence: dict[str, dict] = {}
for run in RUNS:
    summary_path = RESULT / f"{run}_target_panel_summary.json"
    called_path = RESULT / f"{run}_target_panel_called_cells.tsv.gz"
    hash_path = AUDIT / f"{run}.hashes.json"
    resume_path = AUDIT / f"{run}.resume_validation_v3_2.json"
    required_exist = all(path.exists() for path in (summary_path, called_path, hash_path, resume_path))
    if not required_exist:
        donor_evidence[run] = {"pass": False, "error": "missing compact artifact"}
        continue
    summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
    hashes = json.loads(hash_path.read_text(encoding="utf-8-sig"))
    resume = json.loads(resume_path.read_text(encoding="utf-8-sig"))
    receipt = receipts.get(run, {})
    expected = manifest[run]
    with gzip.open(called_path, "rt", encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        first_data_row = handle.readline()
    donor_pass = (
        summary.get("schema_version") == "CMM_R7A1C1_TARGET_PANEL_2.0"
        and summary.get("run") == run
        and summary.get("technical_QC") == "PASS"
        and summary.get("promotion_eligible_FCRL3_B") is True
        and summary.get("promotion_eligible_IL12RB2_NK") is True
        and int(summary.get("bam_bytes", -1)) == int(expected["expected_bytes"])
        and hashes.get("bytes") == int(expected["expected_bytes"])
        and hashes.get("md5", "").lower() == expected["official_md5"].lower()
        and hashes.get("sha256", "").lower() == summary.get("bam_sha256", "").lower()
        and receipt.get("observed_md5", "").lower() == expected["official_md5"].lower()
        and receipt.get("sha256", "").lower() == summary.get("bam_sha256", "").lower()
        and receipt.get("bam_deleted", "").lower() == "true"
        and receipt.get("status", "").startswith("PASS_TARGET_PANEL_V2")
        and resume.get("status") == "PASS_VALID_SUMMARY_AND_RECEIPT"
        and header[:3] == ["run", "cell_barcode", "total_gene_UMI"]
        and bool(first_data_row)
    )
    donor_evidence[run] = {
        "pass": donor_pass,
        "called_cells": summary.get("scan_qc", {}).get("cell_call", {}).get("called_cells"),
        "B_gate_cells": summary.get("B_gate_cells"),
        "NK_gate_cells": summary.get("NK_gate_cells"),
        "FCRL3_B_positive_cells": summary.get("FCRL3_B_positive_cells"),
        "FCRL3_B_UMI": summary.get("FCRL3_B_UMI"),
        "IL12RB2_NK_positive_cells": summary.get("IL12RB2_NK_positive_cells"),
        "IL12RB2_NK_UMI": summary.get("IL12RB2_NK_UMI"),
        "sha256": summary.get("bam_sha256"),
        "resume": resume.get("status"),
        "bam_deleted": receipt.get("bam_deleted"),
    }
check("five_donor_compact_artifact_identity", all(x.get("pass") for x in donor_evidence.values()), donor_evidence)

schema_evidence = {}
for run in RUNS[-2:]:
    schema = json.loads((AUDIT / f"{run}.bam_schema_preflight_v1_2.json").read_text(encoding="utf-8-sig"))
    schema_evidence[run] = {
        "status": schema.get("status"),
        "schema_valid": schema.get("schema_valid"),
        "records": schema.get("counts", {}).get("records"),
        "xf8": schema.get("counts", {}).get("xf8"),
        "tag_fractions": schema.get("fractions"),
    }
check(
    "v3_2_schema_gate_donor4_and_5",
    all(x["schema_valid"] is True and x["status"] in {"PASS", "PASS_WITH_WARNING"} for x in schema_evidence.values()),
    schema_evidence,
)

official = json.loads(OFFICIAL_FINAL.read_text(encoding="utf-8-sig"))
independent = json.loads(INDEPENDENT_FINAL.read_text(encoding="utf-8-sig"))
check("independent_adjudication_exact_match", official == independent, {"official": official, "independent": independent})
check(
    "five_of_five_dual_target_gate",
    official.get("technical_QC_donors") == 5
    and official.get("FCRL3_B_promotion_eligible_donors") == 5
    and official.get("IL12RB2_NK_promotion_eligible_donors") == 5
    and official.get("primary_gate") == "PASS"
    and official.get("promotion_gate") == "PASS"
    and official.get("next_stage") == "GO_R7A2_PBC_MANUSCRIPT_SCALE",
    official,
)

residual_large_files = []
if BAM_DIR.exists():
    residual_large_files = [str(path.relative_to(BAM_DIR)) for path in BAM_DIR.rglob("*") if path.is_file()]
check("bam_cache_empty_after_validated_deletion", not residual_large_files, residual_large_files)

status = "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL"
output = {
    "schema": "R7A1C1B2_INDEPENDENT_QA_1.0",
    "status": status,
    "passed": sum(row["status"] == "PASS" for row in checks),
    "total": len(checks),
    "checks": checks,
    "conclusion": "PBC five-donor liver gate closed at 5/5 for both prespecified target-lineage pairs.",
    "claim_boundary": "Target detectability in marker-defined lineages; not case-control differential expression or causal mediation.",
    "next_stage": "R7A2A1_HRA008003_EXACT_5_VS_5_CONTROL_TARGET_PANEL",
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(output, ensure_ascii=False, indent=2))
raise SystemExit(0 if status == "PASS" else 2)
