#!/usr/bin/env python3
"""Run compact consistency checks before packaging R5A2A2."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
AUDIT = ROOT / "3_results/00_audit/R5A2A2"
REPORT = ROOT / "7.Report/current/R5A2A2"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def count_rows(path: Path) -> int:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as stream:
        return sum(1 for _ in stream) - 1


def main() -> int:
    archive = load(AUDIT / "OneK1K_archive_intake_audit.json")
    genotype = load(AUDIT / "OneK1K_genotype_extraction_audit.json")
    usability = load(AUDIT / "OneK1K_chr18_schema_usability_audit.json")
    harmonization = load(AUDIT / "MG_GRCh37_chr18_harmonization_audit.json")
    readiness = load(AUDIT / "OneK1K_chr18_coloc_input_readiness.json")
    state = load(ROOT / "0_admin/protocol/current/R5A2A2_MG_chr18_usability_state.json")

    report_names = sorted(path.name for path in REPORT.glob("*.md"))
    required_reports = {
        "00_CMM_R5A2A2_执行摘要_OneK1K_chr18输入闭环.md",
        "01_CMM_R5A2A2_OneK1K_10GB归档与基因型字节审计.md",
        "02_CMM_R5A2A2_样本接口_ParquetSchema与等位基因审计.md",
        "03_CMM_R5A2A2_chr18区域基因与QTL可测性.md",
        "04_CMM_R5A2A2_MG_GRCh37协调与共定位准备度.md",
        "05_CMM_R5A2A2_R5A2A3下一阶段冻结目标.md",
        "99_CMM_R5A2A2_详细行动记录_2026-09-14.md",
        "README.md",
        "SOURCES_CHECKED_2026-09-14.md",
    }
    utf8_pass = True
    for path in REPORT.glob("*.md"):
        try:
            path.read_text(encoding="utf-8")
        except UnicodeError:
            utf8_pass = False

    region_qtl = ROOT / "3_results/03_qtl/R5A2A2/OneK1K_chr18_fixed_1Mb_region_pairs.tsv.gz"
    overlap = ROOT / "3_results/04_integration/R5A2A2/OneK1K_chr18_coloc_input_manifest.tsv"
    gwas_outputs = [ROOT / result["output_path"] for result in harmonization["traits"]]
    checks = {
        "archive_gate_pass": bool(archive.get("archive_and_member_gate_pass")),
        "genotype_extraction_gate_pass": bool(genotype.get("extraction_pass")),
        "schema_usability_gate_pass": bool(usability.get("schema_and_usability_gate_pass")),
        "GRCh37_disease_input_gate_pass": bool(harmonization.get("GRCh37_disease_input_gate_pass")),
        "coloc_input_readiness_gate_pass": bool(readiness.get("chr18_coloc_input_gate_pass")),
        "state_is_complete_pass": state.get("status") == "COMPLETE_INPUT_GATE_PASS",
        "state_does_not_claim_coloc": state.get("gates", {}).get("disease_eQTL_colocalization") == "NOT_RUN",
        "required_reports_exact": set(report_names) == required_reports,
        "reports_utf8_pass": utf8_pass,
        "regional_qtl_row_count_241650": count_rows(region_qtl) == 241_650,
        "overlap_manifest_row_count_71": count_rows(overlap) == 71,
        "all_three_gwas_outputs_exist": all(path.is_file() for path in gwas_outputs),
        "all_three_gwas_outputs_nonempty": all(count_rows(path) > 1_000 for path in gwas_outputs),
    }
    assets = []
    asset_paths = (
        list(REPORT.glob("*.md"))
        + list((ROOT / "2_code/06_intake/mg_r5a2a2").glob("*.py"))
        + list(AUDIT.glob("*.json"))
        + list(AUDIT.glob("*.tsv"))
        + list((ROOT / "3_results/01_gwas/R5A2A2").glob("*"))
        + list((ROOT / "3_results/03_qtl/R5A2A2").glob("*.tsv"))
        + list((ROOT / "3_results/03_qtl/R5A2A2").glob("*.tsv.gz"))
        + list((ROOT / "3_results/03_qtl/R5A2A2/cell_sample_lists").glob("*.txt"))
        + list((ROOT / "3_results/04_integration/R5A2A2").glob("*"))
        + [
            ROOT / "0_admin/protocol/current/R5A2A2_MG_chr18_usability_state.json",
            ROOT / "0_admin/protocol/current/R5A2A3_MG_chr18_coloc_smoke_protocol.md",
            ROOT / "README_WORKSPACE.md",
        ]
    )
    excluded_audit_names = {
        "R5A2A2_asset_manifest.tsv",
        "R5A2A2_pre_release_QA.json",
        "R5A2A2_release_verification.json",
    }
    for path in sorted({p.resolve() for p in asset_paths if p.is_file() and p.name not in excluded_audit_names}):
        assets.append({
            "relative_path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest_path = AUDIT / "R5A2A2_asset_manifest.tsv"
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["relative_path", "bytes", "sha256"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(assets)

    result = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "asset_manifest": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
        "asset_count": len(assets),
    }
    out = AUDIT / "R5A2A2_pre_release_QA.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
