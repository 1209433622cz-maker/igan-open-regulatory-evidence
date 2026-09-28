#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlparse


EXPECTED = [f"HRR18494{i}" for i in range(54, 59)]
EXPECTED_TOTAL_BYTES = 134_657_112_757
MD5_RE = re.compile(r"^[0-9a-f]{32}$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    with args.manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    errors: list[str] = []
    runs = [row.get("run_accession", "") for row in rows]
    if len(rows) != 5 or sorted(runs) != EXPECTED or len(set(runs)) != 5:
        errors.append(f"expected exact five control-liver runs; found {runs}")
    total = 0
    for row in rows:
        run = row.get("run_accession", "")
        try:
            size = int(row.get("expected_bytes", ""))
            if size <= 0:
                raise ValueError
            total += size
        except ValueError:
            errors.append(f"{run}: invalid expected_bytes")
        if not MD5_RE.fullmatch(row.get("official_md5", "").lower()):
            errors.append(f"{run}: invalid official_md5")
        if row.get("group") != "CONTROL_HEMANGIOMA_NONLESION" or row.get("tissue") != "liver":
            errors.append(f"{run}: invalid group/tissue")
        if row.get("archived_file_name") != f"{run}.bam":
            errors.append(f"{run}: archived_file_name mismatch")
        parsed = urlparse(row.get("direct_url", ""))
        if (
            parsed.scheme != "https"
            or parsed.netloc != "download.cncb.ac.cn"
            or parsed.path != f"/gsa-human/HRA008003/{run}/{run}.bam"
        ):
            errors.append(f"{run}: unexpected direct_url")
    if total != EXPECTED_TOTAL_BYTES:
        errors.append(f"total bytes {total} != {EXPECTED_TOTAL_BYTES}")

    output = {
        "schema": "R7A2A0_CONTROL_LIVER_MANIFEST_PREFLIGHT_1.0",
        "rows": len(rows),
        "runs": runs,
        "total_expected_bytes": total,
        "total_expected_GiB": total / (1024**3),
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
