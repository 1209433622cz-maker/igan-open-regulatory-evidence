#!/usr/bin/env python3
"""Audit the OneK1K raw eQTL tar.gz and extract only chr5 plus metadata.

The compressed archive is read once in streaming mode. MD5 and SHA-256 are
calculated over the same byte stream used for tar inspection, so no second
10.34-GB pass is required. AppleDouble members remain in the inventory but are
never treated as scientific data.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import tarfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


ROOT = Path(r"H:\SCI2\YR1")
ARCHIVE = ROOT / "1_data/qtl/OneK1K/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz"
OUTPUT = ROOT / "1_data/qtl/OneK1K/R5A2B_chr5_members"
AUDIT = ROOT / "3_results/00_audit/R5A2B"
EXPECTED_BYTES = 10_344_009_571
EXPECTED_MD5 = "e42239480f40abd21f221c0d77c82cc3"
PARQUET_PATTERN = re.compile(r"OneK1K_(.+?)\.cis_qtl_pairs\.chr(\d+)\.parquet$")


class HashingReader:
    def __init__(self, raw):
        self.raw = raw
        self.md5 = hashlib.md5()
        self.sha256 = hashlib.sha256()
        self.bytes_read = 0

    def read(self, size: int = -1) -> bytes:
        block = self.raw.read(size)
        if block:
            self.md5.update(block)
            self.sha256.update(block)
            self.bytes_read += len(block)
        return block

    def readable(self) -> bool:
        return True


def scientific_member(name: str) -> bool:
    path = PurePosixPath(name.removeprefix("./"))
    return "__MACOSX" not in path.parts and not path.name.startswith("._")


def safe_basename(name: str) -> str:
    path = PurePosixPath(name.removeprefix("./"))
    if path.is_absolute() or ".." in path.parts:
        raise RuntimeError(f"Unsafe archive member: {name}")
    return path.name


def main() -> int:
    if ARCHIVE.stat().st_size != EXPECTED_BYTES:
        raise RuntimeError(f"Archive byte mismatch: {ARCHIVE.stat().st_size} != {EXPECTED_BYTES}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)

    member_rows: list[dict[str, object]] = []
    extracted_rows: list[dict[str, object]] = []
    extensions: Counter[str] = Counter()
    cell_chromosomes: defaultdict[str, set[int]] = defaultdict(set)
    counts: Counter[str] = Counter()

    with ARCHIVE.open("rb") as raw:
        reader = HashingReader(raw)
        with tarfile.open(fileobj=reader, mode="r|gz") as archive:
            for member in archive:
                counts["all_members"] += 1
                is_scientific = scientific_member(member.name)
                if is_scientific:
                    counts["scientific_members"] += 1
                else:
                    counts["metadata_members"] += 1
                basename = safe_basename(member.name)
                extension = PurePosixPath(basename).suffix.lower()
                if is_scientific:
                    extensions[extension or "NO_EXTENSION"] += 1
                match = PARQUET_PATTERN.fullmatch(basename) if is_scientific else None
                cell = match.group(1) if match else ""
                chromosome = int(match.group(2)) if match else None
                if match:
                    counts["scientific_parquet"] += 1
                    cell_chromosomes[cell].add(chromosome)
                selected_reason = ""
                if match and chromosome == 5:
                    selected_reason = "CHR5_PARQUET"
                elif is_scientific and basename == "README":
                    selected_reason = "README"
                elif is_scientific and basename == "plink_merged.bim":
                    selected_reason = "ARCHIVE_BIM"

                member_rows.append(
                    {
                        "member": member.name,
                        "bytes_uncompressed": member.size,
                        "member_type": "file" if member.isfile() else "directory" if member.isdir() else "other",
                        "scientific_member": is_scientific,
                        "cell_type": cell,
                        "chromosome": chromosome if chromosome is not None else "",
                        "selected_reason": selected_reason,
                    }
                )
                if selected_reason:
                    source = archive.extractfile(member)
                    if source is None:
                        raise RuntimeError(f"Cannot read selected member: {member.name}")
                    destination = OUTPUT / basename
                    digest = hashlib.sha256()
                    written = 0
                    with destination.open("wb") as output:
                        while block := source.read(8 * 1024 * 1024):
                            output.write(block)
                            digest.update(block)
                            written += len(block)
                    if written != member.size:
                        raise RuntimeError(f"Extracted size mismatch for {member.name}: {written} != {member.size}")
                    extracted_rows.append(
                        {
                            "member": member.name,
                            "output": str(destination),
                            "selected_reason": selected_reason,
                            "bytes": written,
                            "sha256": digest.hexdigest(),
                        }
                    )
        while block := reader.read(8 * 1024 * 1024):
            pass
        archive_md5 = reader.md5.hexdigest()
        archive_sha256 = reader.sha256.hexdigest()
        compressed_bytes_read = reader.bytes_read

    expected_cells = {
        "B_IN", "B_MEM", "CD4_ET", "CD4_NC", "CD4_SOX4", "CD8_ET", "CD8_NC",
        "CD8_S100B", "DC", "Mono_C", "Mono_NC", "NK", "NK_R", "Plasma",
    }
    scientific_parquet_complete = (
        set(cell_chromosomes) == expected_cells
        and all(chromosomes == set(range(1, 23)) for chromosomes in cell_chromosomes.values())
    )
    chr5_cells = sorted(row["member"].split("OneK1K_")[-1].split(".cis_qtl_pairs")[0]
                         for row in extracted_rows if row["selected_reason"] == "CHR5_PARQUET")
    checks = {
        "archive_byte_size_pass": ARCHIVE.stat().st_size == EXPECTED_BYTES,
        "compressed_stream_fully_read": compressed_bytes_read == EXPECTED_BYTES,
        "archive_md5_pass": archive_md5 == EXPECTED_MD5,
        "member_count_pass": counts["all_members"] == 622,
        "scientific_member_count_pass": counts["scientific_members"] == 311,
        "appledouble_pair_count_pass": counts["metadata_members"] == 311,
        "scientific_parquet_count_pass": counts["scientific_parquet"] == 308,
        "cell_chromosome_grid_pass": scientific_parquet_complete,
        "chr5_cell_count_pass": len(chr5_cells) == 14 and set(chr5_cells) == expected_cells,
        "metadata_files_extracted": {row["selected_reason"] for row in extracted_rows} >= {"README", "ARCHIVE_BIM"},
    }

    with (AUDIT / "OneK1K_archive_member_manifest.tsv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["member", "bytes_uncompressed", "member_type", "scientific_member", "cell_type", "chromosome", "selected_reason"]
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(member_rows)
    with (AUDIT / "OneK1K_chr5_extracted_manifest.tsv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["member", "output", "selected_reason", "bytes", "sha256"]
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(extracted_rows)

    result = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "archive": str(ARCHIVE),
        "archive_bytes": ARCHIVE.stat().st_size,
        "expected_bytes": EXPECTED_BYTES,
        "archive_md5": archive_md5,
        "expected_md5": EXPECTED_MD5,
        "archive_sha256": archive_sha256,
        "compressed_bytes_read": compressed_bytes_read,
        "counts": dict(counts),
        "scientific_extension_counts": dict(extensions),
        "cell_chromosome_counts": {cell: len(chroms) for cell, chroms in sorted(cell_chromosomes.items())},
        "chr5_cells": chr5_cells,
        "extracted_member_count": len(extracted_rows),
        "extracted_total_bytes": sum(int(row["bytes"]) for row in extracted_rows),
        "checks": checks,
        "archive_and_member_gate_pass": all(checks.values()),
    }
    (AUDIT / "OneK1K_archive_intake_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "archive_and_member_gate_pass": result["archive_and_member_gate_pass"],
        "archive_sha256": archive_sha256,
        "counts": result["counts"],
        "chr5_cells": len(chr5_cells),
        "extracted_total_bytes": result["extracted_total_bytes"],
    }, ensure_ascii=False))
    return 0 if result["archive_and_member_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
