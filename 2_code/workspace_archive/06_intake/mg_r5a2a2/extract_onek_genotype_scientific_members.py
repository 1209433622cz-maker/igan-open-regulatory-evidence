#!/usr/bin/env python3
"""Extract and hash the scientific BED/BIM/FAM members from OneK1K ZIP."""

from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


ROOT = Path(r"H:\SCI2\YR1")
ARCHIVE = ROOT / "1_data/qtl/OneK1K/plink_genotype_merged_980_donors.zip"
OUTPUT = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors"
AUDIT = ROOT / "3_results/00_audit/R5A2A2"


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        crc_pass = archive.testzip() is None
        selected = [
            info for info in archive.infolist()
            if not info.is_dir()
            and not info.filename.startswith("__MACOSX/")
            and not PurePosixPath(info.filename).name.startswith("._")
            and PurePosixPath(info.filename).suffix.lower() in {".bed", ".bim", ".fam"}
        ]
        if len(selected) != 3 or {PurePosixPath(x.filename).suffix.lower() for x in selected} != {".bed", ".bim", ".fam"}:
            raise RuntimeError(f"Expected one BED/BIM/FAM set, found {[x.filename for x in selected]}")
        for info in selected:
            destination = OUTPUT / PurePosixPath(info.filename).name
            digest = hashlib.sha256()
            written = 0
            with archive.open(info) as source, destination.open("wb") as output:
                while block := source.read(8 * 1024 * 1024):
                    output.write(block)
                    digest.update(block)
                    written += len(block)
            if written != info.file_size:
                raise RuntimeError(f"Size mismatch extracting {info.filename}")
            rows.append({
                "member": info.filename,
                "output": str(destination),
                "bytes": written,
                "sha256": digest.hexdigest(),
            })

    with (AUDIT / "OneK1K_genotype_extracted_manifest.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["member", "output", "bytes", "sha256"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "archive": str(ARCHIVE),
        "zip_crc_pass": crc_pass,
        "scientific_members": rows,
        "extraction_pass": crc_pass and len(rows) == 3,
    }
    (AUDIT / "OneK1K_genotype_extraction_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"extraction_pass": result["extraction_pass"], "total_bytes": sum(int(r["bytes"]) for r in rows)}, ensure_ascii=False))
    return 0 if result["extraction_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
