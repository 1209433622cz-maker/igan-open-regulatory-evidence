#!/usr/bin/env python3
"""Validate that a compact donor summary has one exact persisted receipt."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--expected-bytes", type=int, required=True)
    parser.add_argument("--official-md5", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        summary = {}
        errors.append(f"summary_read_error:{type(exc).__name__}:{exc}")
    try:
        with args.receipts.open(encoding="utf-8-sig", newline="") as handle:
            receipts = list(csv.DictReader(handle, delimiter="\t"))
    except Exception as exc:
        receipts = []
        errors.append(f"receipt_read_error:{type(exc).__name__}:{exc}")

    matching = [row for row in receipts if row.get("run") == args.run]
    if len(matching) != 1:
        errors.append(f"expected exactly one receipt for {args.run}; found {len(matching)}")
    receipt = matching[0] if len(matching) == 1 else {}
    summary_sha = str(summary.get("bam_sha256", "")).lower()
    official_md5 = args.official_md5.lower()

    checks = {
        "summary_schema": summary.get("schema_version") == "CMM_R7A1C1_TARGET_PANEL_2.0",
        "summary_technical_QC": summary.get("technical_QC") == "PASS",
        "summary_run": summary.get("run") == args.run,
        "summary_bytes": summary.get("bam_bytes") == args.expected_bytes,
        "summary_sha256": bool(re.fullmatch(r"[0-9a-f]{64}", summary_sha)),
        "receipt_status": str(receipt.get("status", "")).startswith("PASS_TARGET_PANEL_V2"),
        "receipt_bytes": str(receipt.get("bytes", "")) == str(args.expected_bytes),
        "receipt_official_md5": str(receipt.get("official_md5", "")).lower() == official_md5,
        "receipt_observed_md5": str(receipt.get("observed_md5", "")).lower() == official_md5,
        "receipt_sha256": str(receipt.get("sha256", "")).lower() == summary_sha,
    }
    errors.extend(name for name, passed in checks.items() if not passed)
    output = {
        "schema": "R7A1C1B1R_RESUME_VALIDATOR_1.0",
        "run": args.run,
        "checks": checks,
        "errors": errors,
        "status": "PASS_VALID_SUMMARY_AND_RECEIPT" if not errors else "FAIL",
    }
    encoded = json.dumps(output, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
