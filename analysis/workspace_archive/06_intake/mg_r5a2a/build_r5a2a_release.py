#!/usr/bin/env python3
"""Build the immutable R5A2A compact release and verify its checksums."""

from __future__ import annotations

import csv
import hashlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
NAME = "CMM_R5A2A_MG_GeneticGate_2026-09-14"
CURRENT = ROOT / "6_release" / "current" / "R5A2A"
PACKAGE = CURRENT / NAME
HISTORY = ROOT / "6_release" / "history" / "R5A2A_2026-09-14"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def add_file(rows: list[dict[str, object]], source: Path, relative: Path, category: str) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination = PACKAGE / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    rows.append(
        {
            "relative_path": relative.as_posix(),
            "category": category,
            "source_path": str(source),
            "bytes": destination.stat().st_size,
            "sha256": sha256(destination),
        }
    )


def main() -> int:
    for path in (CURRENT, HISTORY):
        if path.exists():
            raise RuntimeError(f"Refusing to overwrite existing release path: {path}")
    PACKAGE.mkdir(parents=True)
    rows: list[dict[str, object]] = []

    for source in sorted((ROOT / "7.Report" / "current" / "R5A2A").glob("*")):
        if source.is_file():
            add_file(rows, source, Path("reports") / source.name, "report")

    for source in sorted((ROOT / "2_code" / "06_intake" / "mg_r5a2a").glob("*")):
        if source.is_file() and source.suffix.lower() in {".py", ".ps1"}:
            add_file(rows, source, Path("code") / "mg_r5a2a" / source.name, "code")
    for name in ("audit_onek_genotype.py", "multirange_download.py"):
        source = ROOT / "2_code" / "06_intake" / "mg_r5a1" / name
        add_file(rows, source, Path("code") / "mg_r5a1" / name, "code_dependency")

    for name in (
        "project_portfolio_state_R5A0.json",
        "R5A2_MG_bounded_pilot_protocol.md",
        "R5A2A_MG_replication_aware_state.json",
        "R5A2A1_MG_chr18_input_closure_protocol.md",
    ):
        source = ROOT / "0_admin" / "protocol" / "current" / name
        add_file(rows, source, Path("protocol") / name, "protocol")

    for source in sorted((ROOT / "3_results" / "01_gwas" / "R5A2A").glob("*")):
        if source.is_file():
            add_file(rows, source, Path("results") / "gwas" / source.name, "result")
    for name in ("EOMG_LOMG_heterogeneity_at_GWS_region_leads.tsv", "MG_lead_dual_build_NCBI.tsv"):
        source = ROOT / "3_results" / "01_gwas" / "R5A1" / name
        add_file(rows, source, Path("results") / "gwas" / name, "result_dependency")

    source = ROOT / "3_results" / "00_audit" / "R5A1" / "OneK1K_genotype_intake_audit.json"
    add_file(rows, source, Path("results") / "audit" / source.name, "audit")
    for source in sorted((ROOT / "3_results" / "00_audit" / "R5A2A").glob("*")):
        if source.is_file():
            add_file(rows, source, Path("results") / "audit" / source.name, "audit")
    for name in (
        "OneK1K_MG_lead_variant_coverage.tsv",
        "MG_cross_resource_QTL_replication_matrix.tsv",
        "OneK1K_top_eQTL_in_MG_loci.tsv",
        "TenK10K_gene_level_in_MG_loci.tsv",
        "TenK10K_SuSiE_CS_in_MG_loci.tsv",
    ):
        source = ROOT / "3_results" / "03_qtl" / "R5A1" / name
        add_file(rows, source, Path("results") / "qtl" / name, "result_dependency")

    manifest = PACKAGE / "release_manifest.tsv"
    with manifest.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["relative_path", "category", "source_path", "bytes", "sha256"],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    checksum_targets = sorted(path for path in PACKAGE.rglob("*") if path.is_file())
    checksums = PACKAGE / "checksums.sha256"
    with checksums.open("w", encoding="utf-8", newline="\n") as stream:
        for path in checksum_targets:
            stream.write(f"{sha256(path)}  {path.relative_to(PACKAGE).as_posix()}\n")

    zip_path = CURRENT / f"{NAME}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file():
                archive.write(path, (Path(NAME) / path.relative_to(PACKAGE)).as_posix())
    with zipfile.ZipFile(zip_path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Release ZIP CRC validation failed")

    zip_sha = sha256(zip_path)
    sha_path = CURRENT / f"{NAME}.zip.sha256"
    sha_path.write_text(f"{zip_sha}  {zip_path.name}\n", encoding="utf-8")

    HISTORY.mkdir(parents=True)
    shutil.copytree(PACKAGE, HISTORY / NAME)
    shutil.copy2(zip_path, HISTORY / zip_path.name)
    shutil.copy2(sha_path, HISTORY / sha_path.name)

    round_reports = ROOT / "7.Report" / "rounds" / "R5A2A"
    shutil.copytree(ROOT / "7.Report" / "current" / "R5A2A", round_reports)
    print(f"payload_files={len(checksum_targets)}")
    print(f"zip={zip_path}")
    print(f"zip_sha256={zip_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
