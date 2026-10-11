#!/usr/bin/env python3
"""Build a non-recursive manifest for public R7B3A supplement deliverables."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1\5_manuscript\R7B3A_ManuscriptV2\supplements")
OUTPUT = ROOT / "SUPPLEMENT_FINAL_MANIFEST.tsv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def eligible(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if path == OUTPUT:
        return False
    if relative.parts[0] in {f"S{i}" for i in range(1, 11)}:
        return "workbook_view" not in path.name
    return path.name in {
        "R7B3A_Supplementary_Tables_S1-S10.xlsx",
        "SUPPLEMENT_STATE.json",
    }


rows = []
for path in sorted(p for p in ROOT.rglob("*") if p.is_file() and eligible(p)):
    rows.append(
        {
            "relative_path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "release_role": "editable_workbook" if path.suffix.lower() == ".xlsx" else "source_or_derived_table",
            "public_release": "YES",
        }
    )

with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

print(f"WROTE {OUTPUT}")
print(f"FILES {len(rows)}")
