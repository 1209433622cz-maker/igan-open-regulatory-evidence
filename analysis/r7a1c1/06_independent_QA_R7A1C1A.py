#!/usr/bin/env python3
"""Independent, fail-closed QA for the R7A1C1A deliverable."""
from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
INPUT_ZIP = Path(r"C:\Users\Administrator\Downloads\CMM_R7A1C0_PBC_TenK_Replication_LiverSourceGate_2026-09-15.zip")
INPUT_SIDECAR = INPUT_ZIP.with_suffix(INPUT_ZIP.suffix + ".sha256")
INPUT_ROOT = ROOT / "9.Version/staging_downloads/R7A1C0_input_20260915/CMM_R7A1C0_PBC_TenK_Replication_LiverSourceGate_2026-09-15"
RESULTS = ROOT / "3_results/04_integration/R7A1C"
AUDIT = ROOT / "3_results/00_audit"
MANIFEST = ROOT / "1_data/scrna/PBC/HRA008003/manifests/HRA008003_PBC_liver_primary_run_manifest_v2.tsv"
OFFICIAL_MD5 = ROOT / "3_results/00_audit/R7A1C1_preflight/HRA008003_md5sum.txt"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 << 20), b""):
            h.update(block)
    return h.hexdigest()


checks: list[dict] = []


def check(name: str, passed: bool, evidence) -> None:
    checks.append({"name": name, "status": "PASS" if passed else "FAIL", "evidence": evidence})
    if not passed:
        raise RuntimeError(f"QA failed: {name}: {evidence}")


observed_zip_sha = digest(INPUT_ZIP)
sidecar_sha = INPUT_SIDECAR.read_text(encoding="utf-8-sig").split()[0].lower()
check("input_sidecar_sha256", observed_zip_sha == sidecar_sha, observed_zip_sha)
with zipfile.ZipFile(INPUT_ZIP) as archive:
    check("input_zip_crc", archive.testzip() is None, len(archive.infolist()))
checksum_rows = []
for line in (INPUT_ROOT / "checksums.sha256").read_text(encoding="utf-8-sig").splitlines():
    if not line.strip():
        continue
    expected, relative = line.split(None, 1)
    relative = relative.strip().lstrip("*")
    checksum_rows.append((expected.lower(), relative))
internal_pass = sum(digest(INPUT_ROOT / relative) == expected for expected, relative in checksum_rows)
check("input_internal_checksums", internal_pass == len(checksum_rows), f"{internal_pass}/{len(checksum_rows)}")

il12 = pd.read_csv(RESULTS / "R7A1C_IL12RB2_TenK_NK_fullPBC_coloc.tsv", sep="\t")
il12_low = il12.loc[il12.p12.eq(1e-6)].iloc[0]
il12_default = il12.loc[il12.p12.eq(1e-5)].iloc[0]
check("IL12RB2_full_PBC_exact_overlap", int(il12_default["n"]) == 396, int(il12_default["n"]))
check(
    "IL12RB2_TenK_robust_replication",
    il12_default.PP_H4 >= 0.8 and il12_default.H4_over_H3H4 >= 0.8 and il12_low.H4_over_H3H4 >= 0.8,
    {"default_H4": il12_default.PP_H4, "low_prior_ratio": il12_low.H4_over_H3H4},
)

fcrl = json.loads((RESULTS / "R7A1C_FCRL3_TenK_Bintermediate_result.json").read_text(encoding="utf-8"))
check("FCRL3_selective_intake", fcrl["exact_overlap_n"] == 343, fcrl["exact_overlap_n"])
check("FCRL3_TenK_robust_ABF", fcrl["status"] == "PASS_ROBUST_SINGLE_CAUSAL_ABF_SMOKE", fcrl["status"])
check(
    "FCRL3_exact_source_signal_identity",
    fcrl["frozen_shared_variant_in_source_cs"] and fcrl["frozen_shared_variant_in_exact_overlap"],
    "1:157699488:C:T",
)
intake = json.loads(
    (ROOT / "1_data/qtl/eqtl/tenk10k/derived/FCRL3_full/B_intermediate/TenK10K_B_intermediate_FCRL3_selective_intake_receipt.json").read_text(encoding="utf-8")
)
extract = intake["members"][0]["extract"]
check(
    "FCRL3_TenK_member_byte_integrity",
    intake["status"] == "PASS_FCRL3_B_INTERMEDIATE_MEMBER_INTAKE"
    and extract["uncompressed_bytes"] == 2_392_868_507
    and extract["crc32"] == "3c73842b"
    and extract["target_rows"] == 843,
    {"status": intake["status"], "bytes": extract["uncompressed_bytes"], "crc32": extract["crc32"], "rows": extract["target_rows"]},
)

official = {}
for line in OFFICIAL_MD5.read_text(encoding="utf-8").splitlines():
    md5, path = line.split("\t")
    official[Path(path).stem] = md5
with MANIFEST.open(encoding="utf-8", newline="") as handle:
    manifest_rows = list(csv.DictReader(handle, delimiter="\t"))
expected_runs = {f"HRR18494{x}" for x in range(59, 64)}
manifest_runs = {x["run_accession"] for x in manifest_rows}
check("HRA_exact_five_PBC_runs", manifest_runs == expected_runs and len(manifest_rows) == 5, sorted(manifest_runs))
check(
    "HRA_official_MD5_manifest_match",
    all(official.get(x["run_accession"]) == x["official_md5"] for x in manifest_rows),
    "5/5",
)

final_hra = ROOT / "3_results/05_tissue/R7A1C1/R7A1C1_liver_final_adjudication_v2.json"
check("HRA_outcome_blind_protocol_state", not final_hra.exists(), "NOT_TESTED; no final adjudication present")

result = {
    "schema_version": "CMM_R7A1C1A_QA_1.0",
    "status": "PASS" if all(x["status"] == "PASS" for x in checks) else "FAIL",
    "checks": checks,
    "project_decision": "HOLD_PENDING_FIVE_DONOR_HRA_V2",
}
AUDIT.mkdir(parents=True, exist_ok=True)
(AUDIT / "R7A1C1A_independent_QA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
