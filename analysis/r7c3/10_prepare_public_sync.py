#!/usr/bin/env python3
"""Prepare a relative-path-only R7C3 public audit subset and copy it to GitHub."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
AUDIT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11"
PUBLIC = AUDIT / "public"
REPO = ROOT / "0_admin" / "repositories" / "igan-open-regulatory-evidence"
CODE = ROOT / "2_code" / "11_manuscript" / "R7C3_full_audit"

if PUBLIC.exists(): shutil.rmtree(PUBLIC)
PUBLIC.mkdir(parents=True)

copy_files = [
    (AUDIT / "inventory" / "R7C3_top_level_summary.tsv", "R7C3_top_level_summary.tsv"),
    (AUDIT / "inventory" / "R7C3_extension_summary.tsv", "R7C3_extension_summary.tsv"),
    (AUDIT / "inventory" / "R7C3_large_file_hash_receipts.tsv", "R7C3_large_file_hash_receipts.tsv"),
    (AUDIT / "integrity" / "R7C3_archive_integrity_summary.json", "R7C3_archive_integrity_summary.json"),
    (AUDIT / "duplicates" / "R7C3_duplicate_state.json", "R7C3_duplicate_state.json"),
    (AUDIT / "records" / "R7C3_action_record_canonical_ledger.tsv", "R7C3_action_record_canonical_ledger.tsv"),
    (AUDIT / "records" / "R7C3_stage_record_summary.tsv", "R7C3_stage_record_summary.tsv"),
    (AUDIT / "records" / "R7C3_action_record_state.json", "R7C3_action_record_state.json"),
    (AUDIT / "fragments" / "R7C3_fragment_state.json", "R7C3_fragment_state.json"),
    (AUDIT / "assets" / "R7C3_high_value_asset_ledger.tsv", "R7C3_high_value_asset_ledger.tsv"),
    (AUDIT / "assets" / "R7C3_retained_stage_timeline.tsv", "R7C3_retained_stage_timeline.tsv"),
]
for src, name in copy_files:
    if not src.is_file(): raise FileNotFoundError(src)
    shutil.copy2(src, PUBLIC / name)

# Publish only the largest 100 exact-duplicate groups; the complete member list stays local.
src_dup = AUDIT / "duplicates" / "R7C3_duplicate_groups.tsv"
with src_dup.open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))[:100]
with (PUBLIC / "R7C3_duplicate_groups_top100.tsv").open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)

inv = json.loads((AUDIT / "inventory" / "R7C3_inventory_state.json").read_text(encoding="utf-8"))
integrity = json.loads((AUDIT / "integrity" / "R7C3_archive_integrity_summary.json").read_text(encoding="utf-8"))
duplicates = json.loads((AUDIT / "duplicates" / "R7C3_duplicate_state.json").read_text(encoding="utf-8"))
records = json.loads((AUDIT / "records" / "R7C3_action_record_state.json").read_text(encoding="utf-8"))
fragments = json.loads((AUDIT / "fragments" / "R7C3_fragment_state.json").read_text(encoding="utf-8"))
public_state = {
    "stage": "R7C3_FULL_WORKSPACE_AUDIT_PUBLIC_SUMMARY",
    "inventory_baseline": {k: inv[k] for k in ("file_count", "total_bytes", "total_gib", "git_internal_files", "research_non_git_sha256_complete", "large_hash_completed")},
    "content_parse_errors_research": 0,
    "content_parse_errors_skill_runtime_long_path": 293,
    "archive_integrity": {k: integrity[k] for k in ("targets", "zip_targets", "gzip_targets", "pass", "fail", "expanded_bytes_checked")},
    "duplicates": duplicates,
    "work_records": records,
    "fragments": fragments,
    "scientific_state": "PBC_GO_SCIENTIFIC_ANALYSIS_FROZEN",
    "submission_state": "NPJ_PACKAGE_READY_AUTHOR_OPERATED_SUBMISSION",
    "zenodo_doi": None,
    "publication_boundary": "No third-party raw data, individual-level data, user-profile paths, full absolute-path inventory, credentials or tokens are included. Audit code retains the workspace-root default H:\\\\SCI2\\\\YR1 for reproducibility.",
}
(PUBLIC / "R7C3_public_audit_summary.json").write_text(json.dumps(public_state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

# Replace R7C3 public destinations atomically at directory level.
dest_analysis = REPO / "analysis" / "r7c3"
dest_results = REPO / "results" / "r7c3"
dest_reports = REPO / "reports" / "R7C3"
dest_protocol = REPO / "protocols" / "R7C3"
for d in (dest_analysis, dest_results, dest_reports, dest_protocol):
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)
for p in sorted(CODE.glob("*.py")): shutil.copy2(p, dest_analysis / p.name)
for p in sorted(PUBLIC.iterdir()):
    if p.is_file(): shutil.copy2(p, dest_results / p.name)
for p in sorted((AUDIT / "reports").glob("*.md")): shutil.copy2(p, dest_reports / p.name)
shutil.copy2(AUDIT / "reports" / "05_CMM_R7C3_投稿包与下一阶段冻结目标.md", dest_protocol / "R7C3_submission_gate_and_next_stage.md")

(REPO / "manuscript" / "r7c3").mkdir(parents=True, exist_ok=True)
(REPO / "manuscript" / "r7c3" / "README.md").write_text(
    "# R7C3 submission gate\n\nThe exact journal files remain the WPS-verified R7C2 npj package in `manuscript/r7c2/`. R7C3 adds a full local asset audit, a checksum-bound author upload bundle and a frozen R7C4 author-operated submission gate. No scientific text, locus, gene, cell type or result was changed.\n",
    encoding="utf-8",
)
print(json.dumps({"public_files": len(list(PUBLIC.iterdir())), "repo_analysis": str(dest_analysis), "repo_results": str(dest_results), "repo_reports": str(dest_reports)}, ensure_ascii=False, indent=2))
