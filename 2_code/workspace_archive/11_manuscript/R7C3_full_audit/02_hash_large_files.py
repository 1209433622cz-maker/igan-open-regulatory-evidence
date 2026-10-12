#!/usr/bin/env python3
"""Complete SHA-256 hashing for size-gated research files and refresh duplicates."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
INV_DIR = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11" / "inventory"
INVENTORY = INV_DIR / "R7C3_all_local_files_inventory.tsv"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    with INVENTORY.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    targets = [r for r in rows if r["hash_state"] == "NOT_HASHED_SIZE_GATE"]
    receipts = []
    for index, row in enumerate(targets, 1):
        path = Path(row["absolute_path"])
        started = datetime.now().astimezone()
        value = digest(path)
        completed = datetime.now().astimezone()
        row["sha256"] = value
        row["hash_state"] = "SHA256_COMPLETE_LARGE"
        receipts.append(
            {
                "index": index,
                "relative_path": row["relative_path"],
                "size_bytes": int(row["size_bytes"]),
                "sha256": value,
                "started": started.isoformat(),
                "completed": completed.isoformat(),
                "seconds": (completed - started).total_seconds(),
            }
        )
        print(json.dumps(receipts[-1], ensure_ascii=False), flush=True)
    with INVENTORY.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with (INV_DIR / "R7C3_large_file_hash_receipts.tsv").open("w", encoding="utf-8", newline="") as fh:
        fields2 = ["index", "relative_path", "size_bytes", "sha256", "started", "completed", "seconds"]
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=fields2)
        writer.writeheader()
        writer.writerows(receipts)
    (INV_DIR / "R7C3_unhashed_large_files.tsv").write_text(
        "relative_path\tabsolute_path\ttop_level\tcategory\tfile_kind\textension\tsize_bytes\tsize_mib\tmodified_local\tsha256\thash_state\tpublic_class\tpublic_reason\tlikely_sensitive_name\tcontent_title\tstage_tokens\tstatus_tokens\tcontent_note\ttext_lines_scanned\ttext_scan_complete\tarchive_entries\tarchive_uncompressed_bytes\tpdf_pages\n",
        encoding="utf-8",
    )

    by_hash: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["sha256"]:
            by_hash[row["sha256"]].append(row)
    duplicates = []
    for value, members in by_hash.items():
        if len(members) < 2:
            continue
        each = int(members[0]["size_bytes"])
        for member in members:
            duplicates.append(
                {
                    "sha256": value,
                    "copies": len(members),
                    "size_each": each,
                    "potential_redundant_bytes": each * (len(members) - 1),
                    "relative_path": member["relative_path"],
                    "category": member["category"],
                }
            )
    duplicates.sort(key=lambda x: (-int(x["potential_redundant_bytes"]), x["sha256"], x["relative_path"]))
    dup_path = INV_DIR / "R7C3_exact_duplicate_files_all_hashed_research.tsv"
    with dup_path.open("w", encoding="utf-8", newline="") as fh:
        fields3 = ["sha256", "copies", "size_each", "potential_redundant_bytes", "relative_path", "category"]
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=fields3)
        writer.writeheader()
        writer.writerows(duplicates)
    state_path = INV_DIR / "R7C3_inventory_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state.update(
        {
            "large_hash_completed": len(receipts),
            "unhashed_large_files": 0,
            "research_non_git_sha256_complete": sum(bool(r["sha256"]) and r["category"] != "git_internal" for r in rows),
            "duplicate_rows_all_hashed_research": len(duplicates),
            "large_hash_completed_at": datetime.now().astimezone().isoformat(),
        }
    )
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
