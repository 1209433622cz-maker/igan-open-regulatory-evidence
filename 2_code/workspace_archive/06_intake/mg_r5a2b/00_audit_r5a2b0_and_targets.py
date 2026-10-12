#!/usr/bin/env python3
"""Audit the received R5A2B0 package and independently rebuild its target set."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import zipfile

import pandas as pd

ROOT = Path(r"H:\SCI2\YR1")
PACKAGE = Path(r"C:\Users\Administrator\Downloads\CMM_R5A2B0_chr5_BoundedPilot_Preflight_2026-09-14.zip")
STANDALONE = Path(r"C:\Users\Administrator\Downloads\99_CMM_R5A2B0_详细行动记录_2026-09-14.md")
TOP_ARCHIVE = ROOT / "1_data/qtl/OneK1K/OneK1K_TensorQTL_top_eQTL_summary.zip"
TARGETS = ROOT / "2_code/06_intake/mg_r5a2b/chr5_source_significant_smoke_targets.tsv"
OUT = ROOT / "3_results/00_audit/R5A2B"
OUT.mkdir(parents=True, exist_ok=True)
GENES = {"TNIP1", "ANXA6", "ATOX1", "CCDC69", "GM2A", "RPS14", "SLC36A1", "TCOF1"}
CELL_RE = re.compile(r"OneK1K_(.+?)\.sig_cis_qtl_pairs\.chr5\.csv$")
REGION_START = 149_447_128
REGION_END = 151_447_128


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


with zipfile.ZipFile(PACKAGE) as zf:
    crc_pass = zf.testzip() is None
    checksum_member = next(n for n in zf.namelist() if n.endswith("checksums.sha256"))
    prefix = checksum_member[: -len("checksums.sha256")]
    checksum_rows = []
    for line in zf.read(checksum_member).decode("utf-8").splitlines():
        expected, rel = line.split("  ", 1)
        actual = hashlib.sha256(zf.read(prefix + rel)).hexdigest()
        checksum_rows.append({"path": rel, "expected": expected, "actual": actual, "pass": expected == actual})
    action_member = next(n for n in zf.namelist() if "/reports/99_CMM_R5A2B0_" in n)
    packaged_action_sha = hashlib.sha256(zf.read(action_member)).hexdigest()

recalculated = []
with zipfile.ZipFile(TOP_ARCHIVE) as zf:
    top_crc_pass = zf.testzip() is None
    for member in zf.namelist():
        if "__MACOSX" in member:
            continue
        match = CELL_RE.fullmatch(Path(member).name)
        if not match:
            continue
        cell = match.group(1)
        # The archive uses a .csv suffix but the source files are tab-delimited.
        df = pd.read_csv(zf.open(member), sep="\t")
        top_position = pd.to_numeric(df["variant_id"].str.split(":").str[1], errors="coerce")
        sub = df[
            df["phenotype_id"].isin(GENES)
            & (df["qval"] < 0.05)
            & top_position.between(REGION_START, REGION_END)
        ].copy()
        for row in sub.itertuples(index=False):
            recalculated.append({
                "cell_type": cell,
                "gene_symbol": row.phenotype_id,
                "top_variant": row.variant_id,
                "pval_nominal": float(row.pval_nominal),
                "pval_beta": float(row.pval_beta),
                "qval": float(row.qval),
            })

calc = pd.DataFrame(recalculated).sort_values(["gene_symbol", "cell_type"]).reset_index(drop=True)
received = pd.read_csv(TARGETS, sep="\t").sort_values(["gene_symbol", "cell_type"]).reset_index(drop=True)
keys = ["cell_type", "gene_symbol", "top_variant"]
key_match = set(map(tuple, calc[keys].to_numpy())) == set(map(tuple, received[keys].to_numpy()))
merged = calc.merge(received, on=keys, suffixes=("_calc", "_received"), validate="one_to_one")
numeric_max_diff = max(
    float((merged[f"{column}_calc"] - merged[f"{column}_received"]).abs().max())
    for column in ["pval_nominal", "pval_beta", "qval"]
)

target_pass = len(received) == len(calc) == 32 and key_match and numeric_max_diff < 1e-12
audit = {
    "schema_version": "1.0",
    "package": {
        "path": str(PACKAGE),
        "bytes": PACKAGE.stat().st_size,
        "sha256": sha256_file(PACKAGE),
        "zip_crc_pass": crc_pass,
        "declared_checksums": len(checksum_rows),
        "checksums_passed": sum(r["pass"] for r in checksum_rows),
        "all_checksums_pass": all(r["pass"] for r in checksum_rows),
        "standalone_action_sha256": sha256_file(STANDALONE),
        "packaged_action_sha256": packaged_action_sha,
        "standalone_action_byte_identical": sha256_file(STANDALONE) == packaged_action_sha,
    },
    "OneK1K_top_archive": {
        "bytes": TOP_ARCHIVE.stat().st_size,
        "sha256": sha256_file(TOP_ARCHIVE),
        "zip_crc_pass": top_crc_pass,
    },
    "target_recalculation": {
        "bounded_genes": sorted(GENES),
        "received_targets": len(received),
        "recalculated_targets": len(calc),
        "cell_gene_top_variant_keys_exact": key_match,
        "max_absolute_numeric_difference": numeric_max_diff,
        "gene_counts": calc["gene_symbol"].value_counts().sort_index().to_dict(),
        "eligibility_rule": "bounded gene, source q<0.05, and source top variant within the frozen GRCh37 interval 5:149447128-151447128",
        "pass": target_pass,
    },
    "delivery_code_audit": {
        "original_issue": "03_extract_harmonize_mg_grch37_chr5.py retained chr18/rs7239261 labels although numeric chr5 window and rs6861227 coordinate were correct.",
        "canonical_fix": "Changed output/audit labels to chromosome 5 and rs6861227 before execution; original imported package remains unchanged.",
        "top_snp_tie_fix": "04_run_chr5_coloc_smoke.py now uses the post-filter m.index for deterministic tie ordering.",
    },
    "overall_preflight_gate": "PASS_AFTER_DELIVERY_LABEL_FIX" if target_pass else "FAIL_TARGET_RECALCULATION",
}
(OUT / "R5A2B0_package_and_target_recalculation_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "R5A2B0_internal_checksum_detail.json").write_text(json.dumps(checksum_rows, ensure_ascii=False, indent=2), encoding="utf-8")
calc.to_csv(OUT / "chr5_source_significant_targets_recalculated.tsv", sep="\t", index=False)
print(json.dumps(audit, ensure_ascii=False, indent=2))
