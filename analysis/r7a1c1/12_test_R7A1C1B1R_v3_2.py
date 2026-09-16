#!/usr/bin/env python3
"""Regression tests for the R7A1C1B1R v3.2 hotfix."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import pysam


CODE = Path(__file__).resolve().parent
SCHEMA = CODE / "08_check_HRA008003_bam_schema_v1_2.py"
RESUME = CODE / "11_validate_HRA008003_resume_state.py"


def write_bam(path: Path, records: int, xf8_records: int, missing: dict[int, str] | None = None) -> None:
    header = {
        "HD": {"VN": "1.6", "SO": "coordinate"},
        "SQ": [{"SN": "chr1", "LN": 2_000_000}],
        "PG": [{"ID": "STAR", "PN": "STAR"}, {"ID": "annotate_reads"}],
    }
    missing = missing or {}
    with pysam.AlignmentFile(str(path), "wb", header=header) as handle:
        for index in range(records):
            record = pysam.AlignedSegment()
            record.query_name = f"READ{index:07d}"
            record.query_sequence = "A" * 50
            record.flag = 0
            record.reference_id = 0
            record.reference_start = index
            record.mapping_quality = 60
            record.cigar = ((0, 50),)
            record.query_qualities = pysam.qualitystring_to_array("I" * 50)
            record.set_tag("xf", 25 if index < xf8_records else 1)
            tags = {"CB": f"CELL{index:05d}-1", "GN": "GENE1", "UB": f"UMI{index:05d}"}
            tags.pop(missing.get(index, ""), None)
            for tag, value in tags.items():
                record.set_tag(tag, value)
            handle.write(record)


def run_schema(bam: Path, out: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [
            sys.executable,
            str(SCHEMA),
            "--bam",
            str(bam),
            "--run",
            bam.stem,
            "--out",
            str(out),
            "--min-records",
            "1000",
            "--max-records",
            "1000",
            "--target-xf8",
            "1000",
        ],
        text=True,
        capture_output=True,
    )
    value = json.loads(out.read_text(encoding="utf-8"))
    return result.returncode, value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    checks: list[dict] = []

    def record(name: str, passed: bool, evidence: object) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "evidence": evidence})

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        high = root / "high.bam"
        write_bam(high, 1_200, 1_000)
        code, value = run_schema(high, root / "high.json")
        record("prefix_at_least_1000_xf8", code == 0 and value["status"] == "PASS", value)

        low = root / "low.bam"
        write_bam(low, 1_000, 25)
        code, value = run_schema(low, root / "low.json")
        record(
            "low_prefix_xf8_valid_schema",
            code == 0
            and value["status"] == "PASS_WITH_WARNING"
            and value["counts"]["xf8"] == 25
            and value["schema_valid"],
            value,
        )

        zero = root / "zero.bam"
        write_bam(zero, 1_000, 0)
        code, value = run_schema(zero, root / "zero.json")
        record("zero_xf8_fails", code != 0 and value["status"] == "FAIL", value)

        missing = root / "missing.bam"
        write_bam(missing, 1_000, 25, {0: "CB", 1: "GN", 2: "UB"})
        code, value = run_schema(missing, root / "missing.json")
        record(
            "missing_required_tags_fail",
            code != 0
            and value["status"] == "FAIL"
            and any("CB" in x for x in value["errors"])
            and any("GN" in x for x in value["errors"])
            and any("UB" in x for x in value["errors"]),
            value,
        )

        corrupt = root / "corrupt.bam"
        write_bam(corrupt, 1_000, 1_000)
        payload = corrupt.read_bytes()
        corrupt.write_bytes(payload[: max(1, len(payload) // 2)])
        code, value = run_schema(corrupt, root / "corrupt.json")
        record(
            "corrupt_or_incomplete_bam_fails",
            code != 0
            and value["status"] == "FAIL"
            and any(x.startswith("input_read_error:") for x in value["errors"]),
            value,
        )

        summary = root / "resume_summary.json"
        receipts = root / "receipts.tsv"
        resume_out = root / "resume.json"
        sha = "a" * 64
        md5 = "b" * 32
        summary.write_text(
            json.dumps(
                {
                    "schema_version": "CMM_R7A1C1_TARGET_PANEL_2.0",
                    "run": "HRRTEST",
                    "bam_bytes": 12345,
                    "bam_sha256": sha,
                    "technical_QC": "PASS",
                }
            ),
            encoding="utf-8",
        )
        with receipts.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "run",
                    "url",
                    "bytes",
                    "official_md5",
                    "observed_md5",
                    "sha256",
                    "status",
                    "bam_deleted",
                ],
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerow(
                {
                    "run": "HRRTEST",
                    "url": "https://example.invalid/HRRTEST.bam",
                    "bytes": 12345,
                    "official_md5": md5,
                    "observed_md5": md5,
                    "sha256": sha,
                    "status": "PASS_TARGET_PANEL_V2",
                    "bam_deleted": "True",
                }
            )
        result = subprocess.run(
            [
                sys.executable,
                str(RESUME),
                "--summary",
                str(summary),
                "--receipts",
                str(receipts),
                "--run",
                "HRRTEST",
                "--expected-bytes",
                "12345",
                "--official-md5",
                md5,
                "--out",
                str(resume_out),
            ],
            text=True,
            capture_output=True,
        )
        value = json.loads(resume_out.read_text(encoding="utf-8"))
        record(
            "rerun_valid_summary_and_receipt",
            result.returncode == 0 and value["status"] == "PASS_VALID_SUMMARY_AND_RECEIPT",
            value,
        )

    output = {
        "schema": "R7A1C1B1R_V3_2_REGRESSION_1.0",
        "checks": checks,
        "passed": sum(x["status"] == "PASS" for x in checks),
        "total": len(checks),
        "status": "PASS" if all(x["status"] == "PASS" for x in checks) else "FAIL",
    }
    encoded = json.dumps(output, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if output["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
