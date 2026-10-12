#!/usr/bin/env python3
"""Validate R5A1 reports, structured outputs, code syntax, and release ZIP."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import pathlib
import zipfile
from datetime import datetime, timezone


ROOT = pathlib.Path(r"H:\SCI2\YR1")
REPORT_CURRENT = ROOT / "7.Report" / "current" / "R5A1"
REPORT_ROUND = ROOT / "7.Report" / "rounds" / "R5A1"
AUDIT_DIR = ROOT / "3_results" / "00_audit" / "R5A1"
ZIP_PATH = ROOT / "6_release" / "current" / "R5A1" / "CMM_R5A1_MG_ByteLevelPreflight_2026-09-13.zip"

REQUIRED_REPORTS = {
    "00_CMM_R5A1_执行摘要_MG字节级预检与项目GO判定.md",
    "01_CMM_R5A1_三套GWAS字节级接入与来源校验.md",
    "02_CMM_R5A1_EOMG_LOMG非MHC异质性结果.md",
    "03_CMM_R5A1_OneK1K_TenK10K可测性与候选排序.md",
    "04_CMM_R5A1_MG单细胞组织资源验收.md",
    "05_CMM_R5A1_R5A2下一阶段冻结目标.md",
    "99_CMM_R5A1_详细行动记录_2026-09-13.md",
    "SOURCES_CHECKED_2026-09-13.md",
    "README.md",
}


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def preflight() -> dict[str, object]:
    current_names = {path.name for path in REPORT_CURRENT.glob("*.md")}
    missing_reports = sorted(REQUIRED_REPORTS - current_names)
    encoding_failures = []
    mirror_mismatches = []
    for name in sorted(REQUIRED_REPORTS):
        current = REPORT_CURRENT / name
        if not current.exists():
            continue
        text = current.read_text(encoding="utf-8")
        if "\ufffd" in text:
            encoding_failures.append(name)
        mirror = REPORT_ROUND / name
        if not mirror.exists() or hash_file(current) != hash_file(mirror):
            mirror_mismatches.append(name)

    json_failures = []
    json_count = 0
    for path in sorted(AUDIT_DIR.glob("*.json")):
        json_count += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            json_failures.append(f"{path.name}: {exc}")

    tsv_failures = []
    tsv_rows: dict[str, int] = {}
    for base in [ROOT / "3_results" / folder / "R5A1" for folder in ("00_audit", "01_gwas", "03_qtl", "05_scrna")]:
        for path in sorted(base.glob("*.tsv")):
            with path.open("r", encoding="utf-8", newline="") as stream:
                reader = csv.reader(stream, delimiter="\t")
                header = next(reader, [])
                rows = 0
                for line_number, row in enumerate(reader, start=2):
                    rows += 1
                    if len(row) != len(header):
                        tsv_failures.append(f"{path}: line {line_number}: {len(row)} != {len(header)}")
                        break
                tsv_rows[path.relative_to(ROOT).as_posix()] = rows

    python_failures = []
    python_count = 0
    for base in [ROOT / "2_code" / "06_intake" / "mg_r5a1", ROOT / "2_code" / "06_intake" / "mg_r5a2", ROOT / "2_code" / "09_release"]:
        for path in sorted(base.glob("*.py")):
            python_count += 1
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                python_failures.append(f"{path}: {exc}")

    passed = not any([missing_reports, encoding_failures, mirror_mismatches, json_failures, tsv_failures, python_failures])
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "required_report_count": len(REQUIRED_REPORTS),
        "missing_reports": missing_reports,
        "encoding_failures": encoding_failures,
        "round_mirror_mismatches": mirror_mismatches,
        "json_files_parsed": json_count,
        "json_failures": json_failures,
        "tsv_rows_checked": tsv_rows,
        "tsv_failures": tsv_failures,
        "python_files_parsed": python_count,
        "python_failures": python_failures,
        "pre_release_qa_pass": passed,
    }


def verify_zip() -> dict[str, object]:
    with zipfile.ZipFile(ZIP_PATH) as archive:
        bad_member = archive.testzip()
        names = archive.namelist()
        checksum_names = [name for name in names if name.endswith("/checksums.sha256")]
        checksum_failures = []
        checked = 0
        if len(checksum_names) != 1:
            checksum_failures.append(f"Expected one checksums.sha256, found {len(checksum_names)}")
        else:
            root_prefix = checksum_names[0].removesuffix("checksums.sha256")
            lines = archive.read(checksum_names[0]).decode("utf-8").splitlines()
            for line in lines:
                expected, relative = line.split("  ", 1)
                member = root_prefix + relative
                actual = hash_bytes(archive.read(member))
                checked += 1
                if actual != expected:
                    checksum_failures.append(relative)
    sidecar = pathlib.Path(str(ZIP_PATH) + ".sha256")
    declared = sidecar.read_text(encoding="ascii").split()[0]
    actual_zip_sha = hash_file(ZIP_PATH)
    passed = bad_member is None and not checksum_failures and declared == actual_zip_sha
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "zip_path": str(ZIP_PATH),
        "zip_bytes": ZIP_PATH.stat().st_size,
        "zip_sha256": actual_zip_sha,
        "zip_crc_bad_member": bad_member,
        "internal_checksums_checked": checked,
        "internal_checksum_failures": checksum_failures,
        "sidecar_sha256_pass": declared == actual_zip_sha,
        "release_qa_pass": passed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", action="store_true")
    args = parser.parse_args()
    output = verify_zip() if args.zip else preflight()
    name = "R5A1_release_verification.json" if args.zip else "R5A1_pre_release_QA.json"
    (AUDIT_DIR / name).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False))
    if not output["release_qa_pass" if args.zip else "pre_release_qa_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
