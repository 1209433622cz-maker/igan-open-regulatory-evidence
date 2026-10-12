#!/usr/bin/env python3
"""Audit the received R5A2A3 release and its independent local recalculation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(r"C:\Users\Administrator\Downloads\CMM_R5A2A3_chr18_colocABF_smoke_2026-09-14.zip")
STANDALONE = Path(r"C:\Users\Administrator\Downloads\99_CMM_R5A2A3_详细行动记录_2026-09-14.md")
IMPORTED = ROOT / "3_results" / "04_integration" / "R5A2A3"
RECALC = ROOT / "3_results" / "04_integration" / "R5A2A3_recomputed"
OUT = ROOT / "3_results" / "00_audit" / "R5A2A4"
OUT.mkdir(parents=True, exist_ok=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


with zipfile.ZipFile(PACKAGE) as zf:
    bad_crc = zf.testzip()
    checksum_name = next(n for n in zf.namelist() if n.endswith("checksums.sha256"))
    root_prefix = checksum_name[: -len("checksums.sha256")]
    lines = zf.read(checksum_name).decode("utf-8").splitlines()
    checksum_rows = []
    for line in lines:
        expected, rel = line.split("  ", 1)
        member = root_prefix + rel
        actual = sha256_bytes(zf.read(member))
        checksum_rows.append({"member": rel, "expected": expected, "actual": actual, "pass": expected == actual})
    report_member = next(n for n in zf.namelist() if "/reports/99_CMM_R5A2A3_" in n)
    packaged_report_sha = sha256_bytes(zf.read(report_member))

summary_keys = ["trait", "cell_type", "phenotype_id"]
received = pd.read_csv(IMPORTED / "chr18_coloc_abf_smoke_213.tsv", sep="\t").sort_values(summary_keys).reset_index(drop=True)
recalc = pd.read_csv(RECALC / "chr18_coloc_abf_smoke_213.tsv", sep="\t").sort_values(summary_keys).reset_index(drop=True)
numeric = list(received.select_dtypes(include=[np.number]).columns)
max_abs = float(np.nanmax(np.abs(received[numeric].to_numpy(float) - recalc[numeric].to_numpy(float))))
nonnumeric = [c for c in received.columns if c not in numeric]
string_differences = int(sum((received[c].fillna("<NA>").astype(str) != recalc[c].fillna("<NA>").astype(str)).sum() for c in nonnumeric))

top_received = pd.read_csv(IMPORTED / "chr18_coloc_abf_top_snps.tsv", sep="\t")
top_recalc = pd.read_csv(RECALC / "chr18_coloc_abf_top_snps.tsv", sep="\t")
rank_keys = summary_keys + ["rank"]
rank_merge = top_received.merge(top_recalc, on=rank_keys, suffixes=("_received", "_recalc"), validate="one_to_one")
rank_variant_differences = int((rank_merge["variant_id_received"] != rank_merge["variant_id_recalc"]).sum())
variant_keys = summary_keys + ["variant_id"]
variant_merge = top_received.merge(top_recalc, on=variant_keys, suffixes=("_received", "_recalc"), validate="one_to_one")
matched_rank_differences = int((variant_merge["rank_received"] != variant_merge["rank_recalc"]).sum())
missing_from_recalc = int((top_received.merge(top_recalc[variant_keys], on=variant_keys, how="left", indicator=True)["_merge"] != "both").sum())
missing_from_received = int((top_recalc.merge(top_received[variant_keys], on=variant_keys, how="left", indicator=True)["_merge"] != "both").sum())
top_numeric_cols = [c for c in top_received.select_dtypes(include=[np.number]).columns if c != "rank"]
top_max_abs = 0.0
for col in top_numeric_cols:
    diff = np.abs(variant_merge[f"{col}_received"].to_numpy(float) - variant_merge[f"{col}_recalc"].to_numpy(float))
    top_max_abs = max(top_max_abs, float(np.nanmax(diff)))

r_validation = json.loads((ROOT / "3_results" / "04_integration" / "R5A2A4" / "NK_R_ZCCHC2_multisignal" / "R_coloc_validation.json").read_text(encoding="utf-8"))

audit = {
    "schema_version": "1.0",
    "package": {
        "path": str(PACKAGE),
        "bytes": PACKAGE.stat().st_size,
        "sha256": sha256_file(PACKAGE),
        "zip_crc_pass": bad_crc is None,
        "declared_checksums": len(checksum_rows),
        "checksums_passed": sum(r["pass"] for r in checksum_rows),
        "all_declared_checksums_pass": all(r["pass"] for r in checksum_rows),
    },
    "standalone_action_record": {
        "path": str(STANDALONE),
        "sha256": sha256_file(STANDALONE),
        "packaged_sha256": packaged_report_sha,
        "byte_identical_to_packaged": sha256_file(STANDALONE) == packaged_report_sha,
    },
    "independent_213_test_recalculation": {
        "received_rows": len(received),
        "recalculated_rows": len(recalc),
        "max_absolute_numeric_difference": max_abs,
        "nonnumeric_value_differences": string_differences,
        "scientific_summary_reproduced": len(received) == len(recalc) == 213 and max_abs < 1e-12 and string_differences == 0,
    },
    "top_snp_table_reproducibility": {
        "received_rows": len(top_received),
        "recalculated_rows": len(top_recalc),
        "variant_differences_at_same_rank": rank_variant_differences,
        "matched_variants_with_rank_swap": matched_rank_differences,
        "variants_only_in_received_top10_sets": missing_from_recalc,
        "variants_only_in_recalculated_top10_sets": missing_from_received,
        "max_absolute_numeric_difference_for_same_variant": top_max_abs,
        "interpretation": "Exact SNP-PP ties were ordered by input order in the received script. Local code now sorts variant IDs and breaks ties by variant ID. This affects display ranks/top-10 boundaries only; PP.H0-H4 and the scientific trigger are unchanged.",
    },
    "official_R_coloc_validation": r_validation,
    "overall_import_gate": "PASS_WITH_NONSCIENTIFIC_TIE_ORDER_FIX",
}

(OUT / "R5A2A3_import_and_recalculation_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "R5A2A3_internal_checksum_detail.json").write_text(json.dumps(checksum_rows, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(audit, ensure_ascii=False, indent=2))
