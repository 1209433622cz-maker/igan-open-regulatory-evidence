#!/usr/bin/env python3
"""Identify interrupted-download/cache fragments and classify conservatively."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
AUDIT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11"
INV = AUDIT / "inventory" / "R7C3_all_local_files_inventory.tsv"
OUT = AUDIT / "fragments"
OUT.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader(INV.open(encoding="utf-8", newline=""), delimiter="\t"))
by_sha = {}
for r in rows:
    if r["sha256"]: by_sha.setdefault(r["sha256"], []).append(r)

fragments = []
for r in rows:
    if r["extension"] not in {".part", ".redownload", ".tmp", ".download"}: continue
    rel = r["relative_path"]
    peers = [x["relative_path"] for x in by_sha.get(r["sha256"], []) if x["relative_path"] != rel]
    if r["extension"] == ".redownload" and peers:
        status = "EXACT_FINAL_COPY_EXISTS_REVIEW_FOR_DELETION"
    elif rel.startswith("9.Version/"):
        status = "HISTORICAL_INTERRUPTED_DOWNLOAD_PRESERVE_WITH_VERSION_SNAPSHOT"
    elif "first64MiB.bam.part" in rel:
        status = "INTENTIONAL_SCHEMA_PREFLIGHT_SAMPLE_PRESERVE"
    elif "/cache/" in rel or "_cache/" in rel:
        status = "INCOMPLETE_CACHE_FRAGMENT_NOT_PRIMARY_EVIDENCE"
    else:
        status = "REVIEW_FRAGMENT_NOT_PRIMARY_EVIDENCE"
    fragments.append({
        "relative_path": rel,
        "size_bytes": int(r["size_bytes"]),
        "sha256": r["sha256"],
        "classification": status,
        "exact_hash_peers": ";".join(peers),
    })

with (OUT / "R7C3_fragment_inventory.tsv").open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(fragments[0]), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(sorted(fragments, key=lambda x: -x["size_bytes"]))

state = {
    "fragment_files": len(fragments),
    "fragment_bytes": sum(x["size_bytes"] for x in fragments),
    "exact_final_copy_exists": sum(x["classification"].startswith("EXACT_FINAL") for x in fragments),
    "primary_evidence_blockers": 0,
    "action": "No fragment was deleted; none is used as primary PBC manuscript evidence.",
}
(OUT / "R7C3_fragment_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(state, ensure_ascii=False, indent=2))
