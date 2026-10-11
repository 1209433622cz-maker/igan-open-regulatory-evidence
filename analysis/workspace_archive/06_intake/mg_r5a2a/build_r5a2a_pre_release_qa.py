#!/usr/bin/env python3
"""Create the R5A2A asset manifest and machine-readable pre-release QA."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
AUDIT_DIR = ROOT / "3_results" / "00_audit" / "R5A2A"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = ROOT / "3_results/01_gwas/R5A2A/EOMG_LOMG_genomewide_heterogeneity.summary.json"
    japanese_path = ROOT / "3_results/01_gwas/R5A2A/Japanese_MG_GWAS_intake_audit.json"
    genotype_path = ROOT / "3_results/00_audit/R5A1/OneK1K_genotype_intake_audit.json"
    state_path = ROOT / "0_admin/protocol/current/R5A2A_MG_replication_aware_state.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    japanese = json.loads(japanese_path.read_text(encoding="utf-8"))
    genotype = json.loads(genotype_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))

    report_paths = sorted((ROOT / "7.Report/current/R5A2A").glob("*.md"))
    report_utf8_pass = True
    replacement_character_count = 0
    for path in report_paths:
        text = path.read_text(encoding="utf-8")
        replacement_character_count += text.count("\ufffd")

    tsv_paths = sorted((ROOT / "3_results/01_gwas/R5A2A").glob("*.tsv"))
    tsv_results: dict[str, object] = {}
    all_tsv_rectangular = True
    for path in tsv_paths:
        with path.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.reader(stream, delimiter="\t"))
        widths = sorted({len(row) for row in rows})
        rectangular = len(widths) == 1
        all_tsv_rectangular &= rectangular
        tsv_results[path.name] = {
            "data_rows": max(0, len(rows) - 1),
            "column_counts_seen": widths,
            "rectangular": rectangular,
        }

    checks = {
        "state_complete": state["status"] == "COMPLETE_CONDITIONAL_GO_CHR18_PRIMARY",
        "genomewide_scan_pass": summary["status"] == "PASS",
        "exact_shared_expected": summary["exact_shared_testable_variants"] == 5_231_937,
        "no_bonferroni_significant_variant": summary["genomewide_significant_variant_count"] == 0,
        "japanese_content_pass": bool(japanese["content_pass"]),
        "japanese_expected_rows": japanese["variant_rows"] == 9_034_566,
        "onek_genotype_intake_pass": bool(genotype["intake_pass"]),
        "onek_expected_donors": genotype["fam_donors"] == 980,
        "reports_utf8_pass": report_utf8_pass and replacement_character_count == 0,
        "result_tsv_rectangular_pass": all_tsv_rectangular,
    }

    asset_paths = [
        ROOT / "1_data/gwas/MG/R5A1_GWAS_Catalog/GCST90432157/GCST90432157.h.tsv.gz",
        ROOT / "1_data/gwas/MG/R5A1_GWAS_Catalog/GCST90432158/GCST90432158.h.tsv.gz",
        ROOT / "1_data/gwas/MG/NBDC/hum0197.v29.MG-gwas.v1/hum0197.v29.MG-gwas.v1.zip",
        ROOT / "1_data/gwas/MG/NBDC/hum0197.v29.MG-gwas.v1/Dictionary_hum0197_v29.docx",
        ROOT / "1_data/qtl/OneK1K/plink_genotype_merged_980_donors.zip",
    ]
    asset_paths += sorted((ROOT / "3_results/01_gwas/R5A2A").glob("*"))
    asset_paths += report_paths
    asset_paths += sorted((ROOT / "2_code/06_intake/mg_r5a2a").glob("*.py"))
    asset_paths += sorted((ROOT / "2_code/06_intake/mg_r5a2a").glob("*.ps1"))
    asset_paths += [
        state_path,
        ROOT / "0_admin/protocol/current/R5A2A1_MG_chr18_input_closure_protocol.md",
    ]
    manifest_rows = []
    for path in asset_paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        manifest_rows.append(
            {
                "path_relative_to_workspace": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    manifest_path = AUDIT_DIR / "R5A2A_asset_manifest.tsv"
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["path_relative_to_workspace", "bytes", "sha256"],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    output = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "report_count": len(report_paths),
        "replacement_character_count": replacement_character_count,
        "tsv_results": tsv_results,
        "asset_manifest_rows": len(manifest_rows),
        "asset_manifest": str(manifest_path),
    }
    qa_path = AUDIT_DIR / "R5A2A_pre_release_QA.json"
    qa_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_checks_pass": output["all_checks_pass"], "asset_manifest_rows": len(manifest_rows)}, ensure_ascii=False))
    return 0 if output["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
