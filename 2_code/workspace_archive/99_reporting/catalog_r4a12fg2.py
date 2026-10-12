#!/usr/bin/env python3
"""Register R4A12FG2 artifacts in the canonical workspace catalogs."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def files_under(root: Path, relative: str, *, exclude: set[str] | None = None) -> list[Path]:
    base = root / relative
    result = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if exclude and any(part in exclude for part in path.relative_to(base).parts):
            continue
        if path.suffix == ".pyc" or path.name.endswith(".part"):
            continue
        result.append(path)
    return result


def update_catalog(root: Path, catalog_rel: str, paths: list[Path], role: str, status: str) -> None:
    catalog = root / catalog_rel
    with catalog.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames
        rows = list(reader)
    assert fields == ["source_rel", "destination_rel", "role", "bytes", "sha256", "status", "provenance_round"]
    by_dest = {row["destination_rel"]: row for row in rows}
    for path in paths:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        by_dest[rel] = {
            "source_rel": "generated_or_imported:R4A12FG2",
            "destination_rel": rel,
            "role": role,
            "bytes": str(path.stat().st_size),
            "sha256": sha256(path),
            "status": status,
            "provenance_round": "R4A12FG2",
        }
    with catalog.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(by_dest.values())


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    data = files_under(root, "1_data/gwas/outcome/ssc_finngen_r12_r13") + files_under(root, "1_data/qtl/eqtl/tenk10k/derived/IL12RB2")
    code = (
        files_under(root, "2_code/06_intake/finngen_r12_r13", exclude={"__pycache__", "node_modules"})
        + files_under(root, "2_code/06_intake/finngen_fg2_remote", exclude={"__pycache__", "node_modules"})
        + files_under(root, "2_code/06_intake/tenk10k_il12rb2", exclude={"__pycache__", "node_modules"})
        + [
            root / "2_code/99_reporting/build_r4a12fg2_state.py",
            root / "2_code/99_reporting/package_r4a12fg2.py",
            root / "2_code/99_reporting/validate_r4a12fg2_final.py",
            Path(__file__).resolve(),
        ]
    )
    results = files_under(root, "3_results/00_audit/R4A12FG2") + files_under(root, "3_results/01_smoke/R4A12FG2_IL12RB2")
    reports = files_under(root, "7.Report/current/R4A12FG2") + files_under(root, "7.Report/rounds/R4A11C/imported_2026-09-12") + files_under(root, "7.Report/rounds/R4A11D/imported_2026-09-12")
    releases = files_under(root, "6_release/current/R4A12FG2", exclude={"expanded"})
    update_catalog(root, "1_data/catalogs/DATA_CATALOG.tsv", data, "R4A12FG2_DATA_INPUT_OR_DERIVED", "GENERATED_OR_ACQUIRED_VALIDATED")
    update_catalog(root, "2_code/CODE_CATALOG.tsv", code, "R4A12FG2_ACTIVE_CODE", "COMPILE_OR_TEST_PASS")
    update_catalog(root, "3_results/RESULT_CATALOG.tsv", results, "R4A12FG2_AUDIT_OR_SMOKE_RESULT", "VALIDATED_DESCRIPTIVE_ONLY")
    update_catalog(root, "7.Report/REPORT_CATALOG.tsv", reports, "R4A12FG2_CURRENT_OR_IMPORTED_REPORT", "CURRENT_OR_HISTORICAL_VALIDATED")
    update_catalog(root, "6_release/RELEASE_CATALOG.tsv", releases, "R4A12FG2_CURRENT_RELEASE", "ZIP_VALIDATION_PASS")

    stage_catalog = root / "9.Version/STAGE_CATALOG.tsv"
    with stage_catalog.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames
        rows = list(reader)
    rows = [row for row in rows if row["stage"] != "R4A12FG2"]
    stage_files = set(data + code + results + reports + releases)
    rows.append({
        "stage": "R4A12FG2",
        "current_path": "7.Report/current/R4A12FG2",
        "files": str(len(stage_files)),
        "bytes": str(sum(path.stat().st_size for path in stage_files)),
        "action": "REGISTERED_CURRENT_BOUNDED_BRANCH",
        "current_role": "FINNGEN_ALL_SEX_IL12RB2_ENGINEERING_AND_SENSITIVITY",
    })
    with stage_catalog.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print({"data": len(data), "code": len(code), "results": len(results), "reports": len(reports), "releases": len(releases)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
