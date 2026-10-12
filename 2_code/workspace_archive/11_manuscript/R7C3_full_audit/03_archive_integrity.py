#!/usr/bin/env python3
"""Validate ZIP CRC and GZIP stream integrity for research assets."""

from __future__ import annotations

import csv
import gzip
import json
import time
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11" / "integrity"
INV = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11" / "inventory" / "R7C3_all_local_files_inventory.tsv"


def validate_zip(path: Path) -> tuple[str, str, int]:
    try:
        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
            return ("PASS" if bad is None else "FAIL", "" if bad is None else f"bad_member={bad}", len(zf.infolist()))
    except Exception as exc:
        return "FAIL", f"{type(exc).__name__}:{exc}", 0


def validate_gzip(path: Path) -> tuple[str, str, int]:
    expanded = 0
    try:
        with gzip.open(path, "rb") as handle:
            for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
                expanded += len(block)
        return "PASS", "", expanded
    except Exception as exc:
        return "FAIL", f"{type(exc).__name__}:{exc}", expanded


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with INV.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    targets = []
    for row in rows:
        rel = row["relative_path"]
        if row["category"] in {"git_internal", "tools", "skill_runtime"}:
            continue
        suffix = Path(rel).suffix.lower()
        if suffix == ".zip":
            targets.append((row, "ZIP_CRC"))
        elif suffix == ".gz" and row["category"] in {
            "source_or_derived_data", "analysis_results", "manuscript", "release", "versioned_plans",
            "workspace_root", "analysis_workspace", "github_worktrees"
        }:
            targets.append((row, "GZIP_STREAM"))
    results = []
    started_all = datetime.now().astimezone()
    for idx, (row, mode) in enumerate(targets, 1):
        path = Path(row["absolute_path"])
        t0 = time.perf_counter()
        if mode == "ZIP_CRC":
            status, detail, units = validate_zip(path)
            expanded = int(row.get("archive_uncompressed_bytes") or 0)
            entries = units
        else:
            status, detail, expanded = validate_gzip(path)
            entries = ""
        result = {
            "index": idx,
            "relative_path": row["relative_path"],
            "mode": mode,
            "size_bytes": int(row["size_bytes"]),
            "status": status,
            "detail": detail,
            "entries": entries,
            "expanded_bytes_checked": expanded,
            "seconds": f"{time.perf_counter() - t0:.6f}",
            "sha256": row["sha256"],
        }
        results.append(result)
        if idx % 100 == 0 or status != "PASS":
            print(json.dumps(result, ensure_ascii=False), flush=True)
    fields = ["index", "relative_path", "mode", "size_bytes", "status", "detail", "entries", "expanded_bytes_checked", "seconds", "sha256"]
    with (OUT / "R7C3_archive_integrity.tsv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    summary = {
        "stage": "R7C3_ARCHIVE_INTEGRITY",
        "started": started_all.isoformat(),
        "completed": datetime.now().astimezone().isoformat(),
        "targets": len(results),
        "zip_targets": sum(r["mode"] == "ZIP_CRC" for r in results),
        "gzip_targets": sum(r["mode"] == "GZIP_STREAM" for r in results),
        "pass": sum(r["status"] == "PASS" for r in results),
        "fail": sum(r["status"] != "PASS" for r in results),
        "expanded_bytes_checked": sum(int(r["expanded_bytes_checked"]) for r in results),
        "failures": [r for r in results if r["status"] != "PASS"],
    }
    (OUT / "R7C3_archive_integrity_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
