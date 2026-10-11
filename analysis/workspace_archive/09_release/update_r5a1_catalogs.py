#!/usr/bin/env python3
"""Upsert final R5A1 reports and release artifacts into workspace catalogs."""

from __future__ import annotations

import csv
import hashlib
import pathlib


ROOT = pathlib.Path(r"H:\SCI2\YR1")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def upsert(catalog: pathlib.Path, paths: list[pathlib.Path], role: str) -> None:
    with catalog.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = reader.fieldnames
        rows = list(reader)
    if fields is None:
        raise RuntimeError(f"Missing header: {catalog}")
    new_by_destination = {path.relative_to(ROOT).as_posix(): path for path in paths}
    rows = [row for row in rows if row["destination_rel"] not in new_by_destination]
    for destination, path in sorted(new_by_destination.items()):
        rows.append(
            {
                "source_rel": "generated:R5A1",
                "destination_rel": destination,
                "role": role,
                "bytes": str(path.stat().st_size),
                "sha256": sha256(path),
                "status": "GENERATED_VERIFIED",
                "provenance_round": "R5A1",
            }
        )
    with catalog.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    reports = sorted((ROOT / "7.Report" / "current" / "R5A1").glob("*.md"))
    release_dir = ROOT / "6_release" / "current" / "R5A1"
    release = [
        release_dir / "CMM_R5A1_MG_ByteLevelPreflight_2026-09-13.zip",
        release_dir / "CMM_R5A1_MG_ByteLevelPreflight_2026-09-13.zip.sha256",
        ROOT / "3_results" / "00_audit" / "R5A1" / "R5A1_release_verification.json",
    ]
    if not reports or not all(path.exists() for path in release):
        raise FileNotFoundError("R5A1 report or final release artifact is missing")
    upsert(ROOT / "7.Report" / "REPORT_CATALOG.tsv", reports, "R5A1_CURRENT_REPORT")
    upsert(ROOT / "6_release" / "RELEASE_CATALOG.tsv", release, "R5A1_CURRENT_RELEASE")
    print(f"CATALOGS_UPDATED\treports={len(reports)}\trelease_artifacts={len(release)}")


if __name__ == "__main__":
    main()
