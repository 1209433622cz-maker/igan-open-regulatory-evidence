#!/usr/bin/env python3
"""Safely execute a previously audited FinnGen object download plan.

Without --execute this command only prints the selected objects and byte total.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def digest_file(path: Path) -> tuple[str, str]:
    sha = hashlib.sha256()
    md5 = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            sha.update(block)
            md5.update(block)
    return sha.hexdigest(), md5.hexdigest()


def within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--incoming-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--selection", choices=("primary", "all"), default="primary")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    with args.plan.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    selected = [row for row in rows if args.selection == "all" or row["endpoint"] == "M13_SYSTSLCE"]
    if not selected:
        raise SystemExit("download plan selected zero objects")
    total = sum(int(row["content_length"]) for row in selected)
    print(f"selection={args.selection} objects={len(selected)} bytes={total}")
    for row in selected:
        print(f"{row['priority']}\t{row['release']}\t{row['object_kind']}\t{row['content_length']}\t{row['url']}")
    if not args.execute:
        print("DRY_RUN_ONLY: add --execute to download the listed objects")
        return 0

    free = shutil.disk_usage(args.incoming_root).free
    if free < int(total * 1.10):
        raise SystemExit(f"insufficient free space: need at least {int(total * 1.10)} bytes, found {free}")

    receipt_rows = []
    for row in selected:
        destination = Path(row["local_path"])
        if not within(destination, args.incoming_root):
            raise SystemExit(f"unsafe destination outside incoming root: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        part = destination.with_name(destination.name + ".part")
        subprocess.run(
            [
                "curl.exe",
                "-fL",
                "--retry",
                "8",
                "--retry-all-errors",
                "--continue-at",
                "-",
                "--output",
                str(part),
                row["url"],
            ],
            check=True,
        )
        if part.stat().st_size != int(row["content_length"]):
            raise SystemExit(f"size mismatch for {part}: {part.stat().st_size} != {row['content_length']}")
        sha256, md5_hex = digest_file(part)
        expected_md5 = row.get("provider_md5_hex", "").lower()
        if expected_md5 and md5_hex != expected_md5:
            raise SystemExit(f"provider MD5 mismatch for {part}: {md5_hex} != {expected_md5}")
        part.replace(destination)
        receipt_rows.append(
            {
                **row,
                "local_path": str(destination),
                "actual_bytes": destination.stat().st_size,
                "actual_sha256": sha256,
                "actual_md5": md5_hex,
                "download_state": "DOWNLOADED_SIZE_AND_PROVIDER_MD5_PASS",
            }
        )

    receipt = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "selection": args.selection,
        "status": "PASS_DOWNLOADED_SIZE_AND_PROVIDER_MD5",
        "objects": receipt_rows,
        "scientific_boundary": "Download integrity only; no analysis status changed.",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"receipt={args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
