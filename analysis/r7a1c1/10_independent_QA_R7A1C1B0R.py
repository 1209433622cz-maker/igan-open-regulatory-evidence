#!/usr/bin/env python3
"""Fail-closed QA for the repaired R7A1C1B0 pre-execution package."""
from __future__ import annotations

import csv
import hashlib
import json
import py_compile
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
ZIP = Path(r"C:\Users\Administrator\Downloads\CMM_R7A1C1B0_FiveDonor_PreExecutionAudit_2026-09-15.zip")
SIDECAR = ZIP.with_suffix(ZIP.suffix + ".sha256")
INPUT = ROOT / "9.Version/staging_downloads/R7A1C1B0_input_20260915/CMM_R7A1C1B0_FiveDonor_PreExecutionAudit_2026-09-15"
CODE = ROOT / "2_code/06_intake/r7a1c1"
AUDIT = ROOT / "3_results/00_audit"
SUPP = ROOT / "3_results/00_audit/R7A1C1B0_paper_supplement"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 << 20), b""):
            h.update(block)
    return h.hexdigest()


checks: list[dict] = []


def require(name: str, condition: bool, evidence) -> None:
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "evidence": evidence})
    if not condition:
        raise RuntimeError(f"{name}: {evidence}")


observed = sha(ZIP)
require("input_sidecar_sha256", observed == SIDECAR.read_text(encoding="utf-8-sig").split()[0], observed)
with zipfile.ZipFile(ZIP) as archive:
    require("input_zip_crc", archive.testzip() is None, len(archive.infolist()))
rows = []
for line in (INPUT / "checksums.sha256").read_text(encoding="utf-8-sig").splitlines():
    if line.strip():
        expected, relative = line.split(None, 1)
        rows.append((expected, relative.strip().lstrip("*")))
matched = sum(sha(INPUT / relative) == expected for expected, relative in rows)
require("input_internal_checksums", matched == len(rows), f"{matched}/{len(rows)}")

original = (CODE / "RUN_R7A1C1_HRA008003_TARGET_PANEL_v3_R7A1C1B0_original.ps1").read_text(encoding="utf-8-sig")
fixed = (CODE / "RUN_R7A1C1_HRA008003_TARGET_PANEL_v3_1.ps1").read_text(encoding="utf-8-sig")
require(
    "original_final_adjudicator_runtime_defect_reproduced",
    "$adjudicateWsl = Convert-ToWslPath (Join-Path $Code '03_adjudicate_HRA008003_liver_gate_v2.py')," in original,
    "unexpected three-path assignment present in input v3",
)
require(
    "v3_1_final_adjudicator_assignment_fixed",
    "$adjudicateWsl = Convert-ToWslPath (Join-Path $Code '03_adjudicate_HRA008003_liver_gate_v2.py')" in fixed
    and "$adjudicateWsl = Convert-ToWslPath (Join-Path $Code '03_adjudicate_HRA008003_liver_gate_v2.py')," not in fixed,
    "single adjudicator path",
)
require(
    "v3_1_resume_requires_receipt_identity",
    all(token in fixed for token in ("validReceipt", "observed_md5", "official_md5", "sha256 -eq $summarySha")),
    "summary reuse requires bytes, provider MD5 and matching SHA-256 receipt",
)
require("v3_1_runtime_preflight", "PASS_R7A1C1B1_PREFLIGHT_ONLY" in (AUDIT / "R7A1C1B0R_v3_1_preflight_console.txt").read_text(encoding="utf-8-sig"), "PASS")

light_original = (CODE / "RUN_R7A1C1B0_LIGHTWEIGHT_SUPPLEMENT_PREFLIGHT_original.ps1").read_text(encoding="utf-8-sig")
light_fixed = (CODE / "RUN_R7A1C1B0_LIGHTWEIGHT_SUPPLEMENT_PREFLIGHT_v2.ps1").read_text(encoding="utf-8-sig")
require(
    "lightweight_download_endpoint_fixed",
    "pmc.ncbi.nlm.nih.gov/articles/instance" in light_original
    and "static-content.springer.com" in light_fixed
    and "fc42c213d4a3b6a029fbb51c7f4806a6ae9101f764510a20df3633d81140bd8d" in light_fixed
    and "23ca09f165508f92fde22c52e3f0561d02852247a60a0e820c51f8ea56fb00a1" in light_fixed,
    "binary XLSX endpoints plus exact byte/SHA-256 gates",
)

schema = json.loads((AUDIT / "R7A1C1B1_HRR1849459_partial_schema_test.json").read_text(encoding="utf-8"))
require(
    "adaptive_schema_gate_real_BAM_prefix",
    schema["status"] == "PASS" and schema["records_inspected"] == 649_995 and schema["counts"]["xf8"] == 1_000,
    {"status": schema["status"], "records": schema["records_inspected"], "xf8": schema["counts"]["xf8"]},
)
require(
    "adaptive_schema_tag_fractions",
    all(schema["fractions"][key] == 1.0 for key in ("CB_among_xf8", "GN_among_xf8", "UB_among_xf8", "unambiguous_GN_among_xf8")),
    schema["fractions"],
)

supp3 = json.loads((SUPP / "41467_2024_53104_MOESM3_ESM_audit.json").read_text(encoding="utf-8"))
supp5 = json.loads((SUPP / "41467_2024_53104_MOESM5_ESM_audit.json").read_text(encoding="utf-8"))
require(
    "supplement_marker_evidence_classified",
    supp3["human_target_hits"] == 2 and supp3["mouse_target_hits"] == 1 and supp3["donor_id_hits"] == 0,
    {"human": supp3["human_target_hits"], "mouse": supp3["mouse_target_hits"], "donor": supp3["donor_id_hits"]},
)
require(
    "source_data_no_target_donor_matrix",
    supp5["target_hits"] == 0 and supp5["donor_id_hits"] == 0 and not supp5["frozen_donor_target_matrix_reconstructable"],
    supp5["gate_status"],
)
require(
    "lightweight_bypass_fails_closed",
    supp3["gate_status"] == "NO_DONOR_TARGET_MATRIX" and supp5["gate_status"] == "NO_DONOR_TARGET_MATRIX",
    "BAM execution remains required",
)

manifest = json.loads((AUDIT / "R7A1C1B1_manifest_preflight.json").read_text(encoding="utf-8"))
require("five_donor_manifest", manifest["status"] == "PASS" and manifest["total_expected_bytes"] == 152_488_497_199, manifest)
final = ROOT / "3_results/05_tissue/R7A1C1/R7A1C1_liver_final_adjudication_v2.json"
require("real_five_donor_outcome_absent", not final.exists(), "NOT_TESTED")

python_files = [CODE / x for x in (
    "07_validate_HRA008003_manifest.py", "08_check_HRA008003_bam_schema.py",
    "09_audit_public_PBC_supplement_xlsx.py", "10_independent_QA_R7A1C1B0R.py",
)]
for path in python_files:
    py_compile.compile(str(path), doraise=True)
require("python_compile", True, f"{len(python_files)}/{len(python_files)}")

result = {
    "schema_version": "CMM_R7A1C1B0R_QA_1.0",
    "status": "PASS",
    "checks": checks,
    "biological_threshold_changed": False,
    "lightweight_bypass": "FAIL_NO_DONOR_TARGET_MATRIX",
    "real_five_donor_result": "NOT_TESTED",
    "next_stage": "R7A1C1B_FIVE_DONOR_BYTE_EXECUTION_V3_1",
}
(AUDIT / "R7A1C1B0R_independent_QA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
