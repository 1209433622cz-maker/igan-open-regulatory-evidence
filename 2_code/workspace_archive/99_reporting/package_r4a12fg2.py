#!/usr/bin/env python3
"""Create and independently validate the compact R4A12FG2 release package."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


PACKAGE = "CMM_R4A12FG2_FinnGen区域接入_IL12RB2描述性SmokeGate_2026-09-13"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(destination)
    shutil.copy2(source, destination)


def add_tree(source: Path, destination: Path, excludes: set[str]) -> list[Path]:
    added = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(source)
        if any(part in excludes for part in rel.parts):
            continue
        if path.suffix in {".pyc", ".part"}:
            continue
        target = destination / rel
        copy_file(path, target)
        added.append(target)
    return added


def validate_text_file(path: Path) -> list[str]:
    errors = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [f"utf8:{path.name}:{exc}"]
    if "\x00" in text or "\ufffd" in text:
        errors.append(f"invalid_text_character:{path.name}")
    if path.suffix.lower() == ".json":
        try:
            json.loads(text)
        except Exception as exc:
            errors.append(f"json:{path.name}:{exc}")
    if path.suffix.lower() == ".tsv":
        rows = list(csv.reader(text.splitlines(), delimiter="\t"))
        widths = {len(row) for row in rows if row}
        if len(widths) > 1:
            errors.append(f"tsv_rectangular:{path.name}:{sorted(widths)}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    release_dir = root / "6_release/current/R4A12FG2"
    expanded = release_dir / "expanded" / PACKAGE
    if expanded.exists():
        raise SystemExit(f"refusing to overwrite existing expanded release: {expanded}")
    expanded.mkdir(parents=True)

    mappings: list[tuple[Path, Path]] = []
    report_dir = root / "7.Report/current/R4A12FG2"
    for path in sorted(report_dir.glob("*.md")):
        mappings.append((path, expanded / "reports" / path.name))

    protocol_files = [
        "analysis_manifest_v11.json",
        "analysis_manifest_v11.md",
        "candidate_registry_v11.tsv",
        "R4A11_state.json",
        "analysis_manifest_v11_amendment_A1_R4A12FG2.json",
        "analysis_manifest_v11_amendment_A1_R4A12FG2.md",
        "R4A12FG2_state.json",
    ]
    for name in protocol_files:
        mappings.append((root / "0_admin/protocol/current" / name, expanded / "protocol" / name))

    evidence_files = [
        root / "0_admin/validation/R4A11E_preflight/R4A11CD_PACKAGE_INTEGRITY_AND_STATE_PREFLIGHT.json",
        root / "0_admin/validation/R4A11E_preflight/R4A11CD_PACKAGE_INTEGRITY_AND_STATE_PREFLIGHT.md",
        root / "0_admin/validation/R4A11E_preflight/audit_r4a11cd_packages.py",
        root / "0_admin/validation/R4A12FG2/R4A11CD_historical_import_manifest.json",
        root / "0_admin/protocol/history/R4A11C/imported_2026-09-12/R4A11C_import_overlay.json",
        root / "0_admin/protocol/history/R4A11D/imported_2026-09-12/R4A11D_import_overlay.json",
    ]
    for path in evidence_files:
        mappings.append((path, expanded / "input_audit" / path.name))

    data_root = root / "1_data/gwas/outcome/ssc_finngen_r12_r13"
    for subdir in ("manifests", "metadata", "regional/R12", "regional/R13", "regional/receipts"):
        for path in sorted((data_root / subdir).glob("*")):
            if path.is_file():
                mappings.append((path, expanded / "data" / subdir / path.name))
    qtl_derived = root / "1_data/qtl/eqtl/tenk10k/derived/IL12RB2"
    for path in sorted(qtl_derived.glob("*.tsv")):
        mappings.append((path, expanded / "data/qtl_derived" / path.name))

    result_files = [
        root / "3_results/00_audit/R4A12FG2/R4A12FG2_manifest_object_receipt.json",
        root / "3_results/00_audit/R4A12FG2/R4A12FG2_manifest_object_receipt.md",
        root / "3_results/00_audit/R4A12FG2/R12_IL12RB2_P0.json",
        root / "3_results/00_audit/R4A12FG2/R13_IL12RB2_P0.json",
        root / "3_results/00_audit/R4A12FG2/R4A12FG2_IL12RB2_TenK10K_FinnGen_descriptive_audit.json",
        root / "3_results/00_audit/R4A12FG2/R4A12FG2_IL12RB2_TenK10K_FinnGen_descriptive_audit.md",
        root / "3_results/00_audit/R4A12FG2/repro/R12_requery.receipt.json",
        root / "3_results/00_audit/R4A12FG2/repro/R13_requery.receipt.json",
        root / "3_results/01_smoke/R4A12FG2_IL12RB2/FinnGen_R12_R13_x_TenK10K_IL12RB2_exact_CS_overlap.tsv",
    ]
    for path in result_files:
        mappings.append((path, expanded / "results" / path.name))

    for source, destination in mappings:
        copy_file(source, destination)

    code_root = expanded / "code"
    add_tree(root / "2_code/06_intake/finngen_r12_r13", code_root / "finngen_r12_r13", {"__pycache__", "node_modules"})
    add_tree(root / "2_code/06_intake/finngen_fg2_remote", code_root / "finngen_fg2_remote", {"__pycache__", "node_modules"})
    add_tree(root / "2_code/06_intake/tenk10k_il12rb2", code_root / "tenk10k_il12rb2", {"__pycache__", "node_modules"})
    for name in ("build_r4a12fg2_state.py", "package_r4a12fg2.py", "catalog_r4a12fg2.py"):
        copy_file(root / "2_code/99_reporting" / name, code_root / "reporting" / name)

    readme = f"""# {PACKAGE}

This compact release contains the R4A12FG2 reports, frozen protocol amendment,
official FinnGen manifests/receipts, exact IL12RB2 regional extracts, derived
TenK10K IL12RB2 records, descriptive overlap results, and reproducible intake
code. It intentionally excludes `node_modules`, the two original TenK10K ZIPs,
the attached R4A11C/D ZIPs, and full 0.79 GB FinnGen objects.

Scientific state: `CONDITIONAL_GO`; `R4B=HOLD`; `C1_count=null`.
No formal disease-QTL colocalization, SMR, or RSS result is claimed.
"""
    (expanded / "README.md").write_text(readme, encoding="utf-8")

    files_before_validation = sorted(p for p in expanded.rglob("*") if p.is_file())
    internal = {
        "schema_version": "CMM_R4A12FG2_STAGING_VALIDATION_1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_STAGING_REQUIRED_FILES_AND_STATES",
        "file_count_before_checksum": len(files_before_validation),
        "checks": {
            "R12_P0": json.loads((expanded / "results/R12_IL12RB2_P0.json").read_text(encoding="utf-8"))["status"],
            "R13_P0": json.loads((expanded / "results/R13_IL12RB2_P0.json").read_text(encoding="utf-8"))["status"],
            "descriptive_audit": json.loads((expanded / "results/R4A12FG2_IL12RB2_TenK10K_FinnGen_descriptive_audit.json").read_text(encoding="utf-8"))["status"],
            "project": json.loads((expanded / "protocol/R4A12FG2_state.json").read_text(encoding="utf-8"))["project"],
            "R4B": json.loads((expanded / "protocol/R4A12FG2_state.json").read_text(encoding="utf-8"))["R4B"],
            "C1_count": json.loads((expanded / "protocol/R4A12FG2_state.json").read_text(encoding="utf-8"))["C1_count"],
        },
    }
    (expanded / "release_validation.json").write_text(json.dumps(internal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checksum_lines = []
    for path in sorted(p for p in expanded.rglob("*") if p.is_file() and p.name != "checksums.sha256"):
        checksum_lines.append(f"{sha256(path)}  {safe_rel(path, expanded)}")
    (expanded / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    zip_path = release_dir / f"{PACKAGE}.zip"
    if zip_path.exists():
        raise SystemExit(f"refusing to overwrite existing zip: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in expanded.rglob("*") if p.is_file()):
            arcname = PurePosixPath(PACKAGE) / PurePosixPath(safe_rel(path, expanded))
            zf.write(path, arcname.as_posix())

    errors: list[str] = []
    text_suffixes = {".md", ".json", ".tsv", ".py", ".ps1", ".mjs", ".yaml", ".txt", ".sha256"}
    with zipfile.ZipFile(zip_path) as zf:
        bad_crc = zf.testzip()
        if bad_crc:
            errors.append(f"crc:{bad_crc}")
        names = [i.filename for i in zf.infolist() if not i.is_dir()]
        if len(names) != len(set(n.casefold() for n in names)):
            errors.append("duplicate_paths")
        if any(".." in PurePosixPath(n).parts or PurePosixPath(n).is_absolute() for n in names):
            errors.append("unsafe_paths")
        if any("node_modules" in PurePosixPath(n).parts or "__pycache__" in PurePosixPath(n).parts for n in names):
            errors.append("excluded_runtime_content_present")
        prefix = PACKAGE + "/"
        if any(not n.startswith(prefix) for n in names):
            errors.append("unexpected_top_level_root")
        members = {n[len(prefix):]: zf.read(n) for n in names}
        try:
            checks = members["checksums.sha256"].decode("utf-8").splitlines()
            declared = {}
            for line in checks:
                digest, rel = line.split("  ", 1)
                declared[rel] = digest
            expected_members = set(members) - {"checksums.sha256"}
            if set(declared) != expected_members:
                errors.append("checksum_coverage")
            for rel, digest in declared.items():
                if hashlib.sha256(members[rel]).hexdigest() != digest:
                    errors.append(f"checksum:{rel}")
        except Exception as exc:
            errors.append(f"checksum_manifest:{exc}")
        for rel, data in members.items():
            suffix = Path(rel).suffix.lower()
            if suffix in text_suffixes or Path(rel).name in {"package.json", "pnpm-lock.yaml"}:
                try:
                    text = data.decode("utf-8")
                    if "\ufffd" in text or "\x00" in text:
                        errors.append(f"text:{rel}")
                    if suffix == ".json":
                        json.loads(text)
                    if suffix == ".tsv":
                        widths = {len(row) for row in csv.reader(text.splitlines(), delimiter="\t") if row}
                        if len(widths) > 1:
                            errors.append(f"tsv:{rel}:{sorted(widths)}")
                except Exception as exc:
                    errors.append(f"parse:{rel}:{exc}")

    validation = {
        "schema_version": "CMM_R4A12FG2_ZIP_VALIDATION_1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "zip": str(zip_path),
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256(zip_path),
        "file_count": len(names),
        "checks_total": 9,
        "checks_passed": 9 if not errors else 9 - min(9, len(errors)),
        "errors": errors,
        "status": "PASS_9_OF_9" if not errors else "FAIL",
    }
    validation_path = zip_path.with_suffix(".zip.validation.json")
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    zip_path.with_suffix(".zip.validation.md").write_text(
        f"# R4A12FG2 release validation\n\nStatus: **{validation['status']}**  \n"
        f"Files: {validation['file_count']}  \nZIP bytes: {validation['zip_bytes']}  \n"
        f"SHA-256: `{validation['zip_sha256']}`\n",
        encoding="utf-8",
    )
    zip_path.with_suffix(".zip.sha256").write_text(f"{validation['zip_sha256']}  {zip_path.name}\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
