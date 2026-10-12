#!/usr/bin/env python3
"""Independent local-state QA for the R7A1C1B1R v3.2 hotfix."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
CODE = ROOT / "2_code/06_intake/r7a1c1"
RESULT = ROOT / "3_results/05_tissue/R7A1C1"
AUDIT = ROOT / "3_results/00_audit/R7A1C1"
MANIFEST = ROOT / "1_data/scrna/PBC/HRA008003/manifests/HRA008003_PBC_liver_primary_run_manifest_v2.tsv"
OUT = ROOT / "3_results/00_audit/R7A1C1B1R_independent_QA.json"

FROZEN_HASHES = {
    "02_hra_bam_target_panel_v2.py": "a88a8d061332322e3182dc259bf4a47b5bb507a30047d278a370932654d9a7a2",
    "03_adjudicate_HRA008003_liver_gate_v2.py": "9a7bc06111e945296911b44cbd6d10e065a83ca475b6456a4c425eaad5b04eae",
    "08_check_HRA008003_bam_schema.py": "11002e6de9624a606a8907abe44acb2110c7d2a07e17b9e9f47a94cd7ba73bbe",
    "RUN_R7A1C1_HRA008003_TARGET_PANEL_v3_1.ps1": "5906a2750b3603ed9e84d3c69ab9a0371afa21c02c5a51b0ff45ee498462f454",
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
check("manifest_exact_five", set(manifest) == {f"HRR184946{i}" for i in range(4)} | {"HRR1849459"}, sorted(manifest))

frozen_observed = {name: sha256(CODE / name) for name in FROZEN_HASHES}
check("v3_1_and_biological_code_unchanged", frozen_observed == FROZEN_HASHES, frozen_observed)

regression = json.loads((ROOT / "3_results/00_audit/R7A1C1B1R_v3_2_regression.json").read_text(encoding="utf-8"))
check("v3_2_regression_suite", regression.get("status") == "PASS" and regression.get("passed") == 6, {"passed": regression.get("passed"), "total": regression.get("total")})

with (AUDIT / "R7A1C1_HRA008003_receipts_v2.tsv").open(encoding="utf-8-sig", newline="") as handle:
    receipts = list(csv.DictReader(handle, delimiter="\t"))
receipt_by_run = {row["run"]: row for row in receipts}
completed = ["HRR1849459", "HRR1849460", "HRR1849461"]
completed_evidence: dict[str, dict] = {}
for run in completed:
    summary = json.loads((RESULT / f"{run}_target_panel_summary.json").read_text(encoding="utf-8"))
    receipt = receipt_by_run.get(run, {})
    resume = json.loads((AUDIT / f"{run}.resume_validation_v3_2.json").read_text(encoding="utf-8"))
    passed = (
        summary.get("technical_QC") == "PASS"
        and summary.get("promotion_eligible_FCRL3_B") is True
        and summary.get("promotion_eligible_IL12RB2_NK") is True
        and receipt.get("sha256") == summary.get("bam_sha256")
        and receipt.get("observed_md5") == manifest[run]["official_md5"]
        and resume.get("status") == "PASS_VALID_SUMMARY_AND_RECEIPT"
    )
    completed_evidence[run] = {
        "pass": passed,
        "FCRL3_B_positive_cells": summary.get("FCRL3_B_positive_cells"),
        "IL12RB2_NK_positive_cells": summary.get("IL12RB2_NK_positive_cells"),
        "receipt_status": receipt.get("status"),
        "resume": resume.get("status"),
    }
check("completed_three_donors_reusable", all(x["pass"] for x in completed_evidence.values()), completed_evidence)
check("receipt_table_has_only_completed_three", set(receipt_by_run) == set(completed), sorted(receipt_by_run))

run4 = "HRR1849462"
run4_bam = ROOT / f"1_data/scrna/PBC/HRA008003/bam/{run4}.bam"
run4_hash = json.loads((AUDIT / f"{run4}.hashes.json").read_text(encoding="utf-8"))
run4_manifest = manifest[run4]
run4_identity = (
    run4_bam.exists()
    and run4_bam.stat().st_size == int(run4_manifest["expected_bytes"])
    and run4_hash.get("bytes") == int(run4_manifest["expected_bytes"])
    and run4_hash.get("md5") == run4_manifest["official_md5"]
    and run4_hash.get("sha256") == "42ab19a8fc22ae0d4ce180f08ebc6361989c60ce9227ce601e21718d48cdb3ce"
)
check("HRR1849462_cached_byte_identity", run4_identity, run4_hash)

old_schema = json.loads((AUDIT / f"{run4}.bam_schema_preflight.json").read_text(encoding="utf-8"))
new_schema = json.loads((AUDIT / f"{run4}.bam_schema_preflight_v1_2.json").read_text(encoding="utf-8"))
check(
    "v1_1_false_failure_reproduced",
    old_schema.get("status") == "FAIL"
    and old_schema.get("counts", {}).get("xf8") == 25
    and old_schema.get("fractions", {}).get("UB_among_xf8") == 1.0,
    {"status": old_schema.get("status"), "counts": old_schema.get("counts"), "fractions": old_schema.get("fractions")},
)
check(
    "v1_2_real_HRR1849462_schema",
    new_schema.get("status") == "PASS_WITH_WARNING"
    and new_schema.get("schema_valid") is True
    and new_schema.get("counts", {}).get("xf8") == 25
    and all(new_schema.get("fractions", {}).get(key) == 1.0 for key in ("CB_among_xf8", "GN_among_xf8", "UB_among_xf8", "unambiguous_GN_among_xf8")),
    {"status": new_schema.get("status"), "counts": new_schema.get("counts"), "fractions": new_schema.get("fractions"), "warnings": new_schema.get("warnings")},
)

runner = (CODE / "RUN_R7A1C1_HRA008003_TARGET_PANEL_v3_2.ps1").read_text(encoding="utf-8")
runner_checks = {
    "uses_schema_v1_2": "08_check_HRA008003_bam_schema_v1_2.py" in runner,
    "uses_resume_validator": "11_validate_HRA008003_resume_state.py" in runner,
    "uses_frozen_full_scan": "02_hra_bam_target_panel_v2.py" in runner,
    "uses_frozen_final_adjudicator": "03_adjudicate_HRA008003_liver_gate_v2.py" in runner,
    "new_schema_output_is_versioned": "bam_schema_preflight_v1_2.json" in runner,
    "receipt_validated_before_delete": runner.index("New summary/receipt identity validation failed") < runner.index("Remove-Item -LiteralPath $resolvedBam"),
}
check("v3_2_runner_static_contract", all(runner_checks.values()), runner_checks)

preflight_text = (ROOT / "3_results/00_audit/R7A1C1B1R_v3_2_preflight_console.txt").read_text(encoding="utf-8")
check("v3_2_runtime_preflight", "PASS_R7A1C1B1R_PREFLIGHT_ONLY" in preflight_text and '"runner": "v3.2"' in preflight_text, "PASS")

final_path = RESULT / "R7A1C1_liver_final_adjudication_v2.json"
check("five_donor_final_not_yet_claimed", not final_path.exists(), "NOT_TESTED")
check("HRR1849463_not_yet_tested", not (RESULT / "HRR1849463_target_panel_summary.json").exists(), "NOT_TESTED")

status = "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL"
output = {
    "schema": "R7A1C1B1R_INDEPENDENT_QA_1.0",
    "status": status,
    "checks": checks,
    "passed": sum(row["status"] == "PASS" for row in checks),
    "total": len(checks),
    "biological_threshold_changed": False,
    "completed_donors": 3,
    "HRR1849462_schema": "PASS_WITH_WARNING_FULL_SCAN_REQUIRED",
    "five_donor_final_result": "NOT_TESTED",
    "next_stage": "R7A1C1B2_FIVE_DONOR_COMPLETION_AND_FINAL_ADJUDICATION",
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
print(json.dumps(output, indent=2))
raise SystemExit(0 if status == "PASS" else 1)
