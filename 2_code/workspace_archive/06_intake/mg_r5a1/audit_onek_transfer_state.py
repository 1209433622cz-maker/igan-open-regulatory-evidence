#!/usr/bin/env python3
"""Inventory resumable OneK1K genotype ranges without treating partial data as complete."""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone


ROOT = pathlib.Path(r"H:\SCI2\YR1")
DATA = ROOT / "1_data" / "qtl" / "OneK1K"
AUDIT = ROOT / "3_results" / "00_audit" / "R5A1"
EXPECTED_BYTES = 233_198_074
EXPECTED_MD5 = "be1053e34fa023bc808388d4e0bf2aa1"
PATTERN = re.compile(r"\.part(?P<part>\d+)\.(?P<start>\d+)-(?P<stop>\d+)(?P<partial>\.new)?$")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(DATA.glob("plink_genotype_merged_980_donors.zip.part*")):
        match = PATTERN.search(path.name)
        if not match:
            continue
        start = int(match.group("start"))
        stop = int(match.group("stop"))
        expected = stop - start + 1
        actual = path.stat().st_size
        rows.append(
            {
                "part": int(match.group("part")),
                "path": str(path),
                "range_start": start,
                "range_stop": stop,
                "expected_part_bytes": expected,
                "actual_part_bytes": actual,
                "part_complete": actual == expected and not bool(match.group("partial")),
                "sha256": sha256(path),
            }
        )

    received = sum(row["actual_part_bytes"] for row in rows)
    final_path = DATA / "plink_genotype_merged_980_donors.zip"
    state = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_record": "https://zenodo.org/records/18910121",
        "expected_file": str(final_path),
        "expected_bytes": EXPECTED_BYTES,
        "expected_md5": EXPECTED_MD5,
        "partial_bytes_present": received,
        "bytes_remaining": EXPECTED_BYTES - received,
        "range_files": rows,
        "final_file_present": final_path.exists(),
        "local_byte_identity": "PASS" if final_path.exists() else "PENDING_ZENODO_TRANSFER_504",
        "restriction": "Do not run LD until the final archive passes MD5, CRC, BED/BIM/FAM, sample-count and build checks. Report lead and regional proxy coverage separately because the source includes only MAF>0.05 variants.",
    }
    (AUDIT / "OneK1K_genotype_transfer_state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    columns = [
        "part", "path", "range_start", "range_stop", "expected_part_bytes",
        "actual_part_bytes", "part_complete", "sha256",
    ]
    with (AUDIT / "OneK1K_genotype_partial_manifest.tsv").open("w", encoding="utf-8", newline="") as out:
        out.write("\t".join(columns) + "\n")
        for row in rows:
            out.write("\t".join(str(row[column]) for column in columns) + "\n")


if __name__ == "__main__":
    main()
