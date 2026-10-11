#!/usr/bin/env python3
"""Summarize exact duplicates without deleting or relinking any file."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
AUDIT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11"
INV = AUDIT / "inventory" / "R7C3_all_local_files_inventory.tsv"
OUT = AUDIT / "duplicates"
OUT.mkdir(parents=True, exist_ok=True)


def bucket(path: str) -> str:
    p = path.replace("\\", "/").lower()
    if p.startswith("6_release/") or "/6_release/" in p:
        return "release_or_stage_snapshot"
    if p.startswith("9.version/"):
        return "version_snapshot"
    if p.startswith("github/"):
        return "public_repository_copy"
    if p.startswith("5_manuscript/"):
        return "manuscript_working_copy"
    if p.startswith("7.report/"):
        return "report_canonical_or_overlay"
    if p.startswith("1_data/"):
        return "data_asset"
    if p.startswith("3_results/") or p.startswith("4_figures/"):
        return "result_or_figure"
    if p.startswith("2_code/"):
        return "code_or_environment"
    return "other"


rows = []
with INV.open(encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["sha256"] and r["hash_state"].startswith("SHA256_COMPLETE"):
            rows.append(r)

groups: dict[str, list[dict[str, str]]] = defaultdict(list)
for r in rows:
    groups[r["sha256"]].append(r)

dups = {h: v for h, v in groups.items() if len(v) > 1}
group_rows = []
member_rows = []
for h, members in sorted(dups.items(), key=lambda kv: -(len(kv[1]) - 1) * int(kv[1][0]["size_bytes"])):
    size = int(members[0]["size_bytes"])
    buckets = sorted({bucket(m["relative_path"]) for m in members})
    protected = any(x in buckets for x in ("release_or_stage_snapshot", "version_snapshot", "public_repository_copy"))
    group_rows.append({
        "sha256": h,
        "copies": len(members),
        "size_each": size,
        "total_bytes": size * len(members),
        "potential_redundant_bytes": size * (len(members) - 1),
        "storage_contexts": ";".join(buckets),
        "disposition": "REVIEW_ONLY_PRESERVE_PROVENANCE" if protected else "REVIEW_FOR_CANONICALIZATION",
        "example_path": members[0]["relative_path"],
    })
    for m in sorted(members, key=lambda x: x["relative_path"].lower()):
        member_rows.append({
            "sha256": h,
            "copies": len(members),
            "size_each": size,
            "storage_context": bucket(m["relative_path"]),
            "relative_path": m["relative_path"],
        })

def write_tsv(path: Path, data: list[dict]):
    if not data:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(data)

write_tsv(OUT / "R7C3_duplicate_groups.tsv", group_rows)
write_tsv(OUT / "R7C3_duplicate_members.tsv", member_rows)

by_context = defaultdict(lambda: {"groups": 0, "members": 0, "potential_redundant_bytes": 0})
for g in group_rows:
    key = g["storage_contexts"]
    by_context[key]["groups"] += 1
    by_context[key]["members"] += int(g["copies"])
    by_context[key]["potential_redundant_bytes"] += int(g["potential_redundant_bytes"])
context_rows = [{"storage_contexts": k, **v} for k, v in sorted(by_context.items(), key=lambda kv: -kv[1]["potential_redundant_bytes"])]
write_tsv(OUT / "R7C3_duplicate_context_summary.tsv", context_rows)

state = {
    "hashed_research_files": len(rows),
    "unique_hashes": len(groups),
    "duplicate_groups": len(dups),
    "duplicate_member_rows": len(member_rows),
    "potential_redundant_bytes": sum(int(g["potential_redundant_bytes"]) for g in group_rows),
    "potential_redundant_gib": sum(int(g["potential_redundant_bytes"]) for g in group_rows) / 1024**3,
    "action": "No file deleted; release/version/repository duplicates are provenance-bearing by default.",
}
(OUT / "R7C3_duplicate_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(state, ensure_ascii=False, indent=2))
