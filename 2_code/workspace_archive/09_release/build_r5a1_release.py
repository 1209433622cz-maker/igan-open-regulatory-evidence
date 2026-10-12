#!/usr/bin/env python3
"""Build the compact, checksum-verified R5A1 release without raw large inputs."""

from __future__ import annotations

import csv
import hashlib
import pathlib
import shutil
import zipfile


ROOT = pathlib.Path(r"H:\SCI2\YR1")
RELEASE_NAME = "CMM_R5A1_MG_ByteLevelPreflight_2026-09-13"
CURRENT = ROOT / "6_release" / "current" / "R5A1"
PACKAGE = CURRENT / RELEASE_NAME
ZIP_PATH = CURRENT / f"{RELEASE_NAME}.zip"
HISTORY = ROOT / "6_release" / "history" / "R5A1_2026-09-13"

SOURCES = [
    (ROOT / "7.Report" / "current" / "R5A1", "reports"),
    (ROOT / "0_admin" / "protocol" / "current" / "project_portfolio_state_R5A0.json", "protocol"),
    (ROOT / "0_admin" / "protocol" / "current" / "R5A1_MG_byte_level_preflight_protocol.md", "protocol"),
    (ROOT / "0_admin" / "protocol" / "current" / "R5A1_MG_preflight_state.json", "protocol"),
    (ROOT / "0_admin" / "protocol" / "current" / "R5A2_MG_bounded_pilot_protocol.md", "protocol"),
    (ROOT / "2_code" / "06_intake" / "mg_r5a1", "code/mg_r5a1"),
    (ROOT / "2_code" / "06_intake" / "mg_r5a2", "code/mg_r5a2"),
    (ROOT / "3_results" / "00_audit" / "R5A1", "results/audit"),
    (ROOT / "3_results" / "01_gwas" / "R5A1", "results/gwas"),
    (ROOT / "3_results" / "03_qtl" / "R5A1", "results/qtl"),
    (ROOT / "3_results" / "05_scrna" / "R5A1", "results/scrna"),
]

EXCLUDE_SUFFIXES = {".pyc"}
EXCLUDE_NAMES = {
    "OneK1K_genotype_intake_audit.json",
    "OneK1K_MG_lead_variant_coverage.tsv",
    "R5A1_release_verification.json",
}


def file_hash(path: pathlib.Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def copy_source(source: pathlib.Path, destination: pathlib.Path) -> list[tuple[pathlib.Path, pathlib.Path]]:
    copied = []
    if source.is_file():
        target = destination / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        return [(source, target)]
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.suffix in EXCLUDE_SUFFIXES or path.name in EXCLUDE_NAMES:
            continue
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied.append((path, target))
    return copied


def main() -> None:
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir(parents=True)
    copied: list[tuple[pathlib.Path, pathlib.Path]] = []
    for source, relative_destination in SOURCES:
        if not source.exists():
            raise FileNotFoundError(source)
        copied.extend(copy_source(source, PACKAGE / relative_destination))

    manifest = PACKAGE / "release_manifest.tsv"
    with manifest.open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, delimiter="\t", lineterminator="\n")
        writer.writerow(["source_relative", "package_relative", "bytes", "sha256"])
        for source, target in copied:
            writer.writerow([
                source.relative_to(ROOT).as_posix(),
                target.relative_to(PACKAGE).as_posix(),
                target.stat().st_size,
                file_hash(target),
            ])

    checksum = PACKAGE / "checksums.sha256"
    package_files = sorted(path for path in PACKAGE.rglob("*") if path.is_file() and path != checksum)
    checksum.write_text(
        "".join(f"{file_hash(path)}  {path.relative_to(PACKAGE).as_posix()}\n" for path in package_files),
        encoding="utf-8",
    )

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file():
                archive.write(path, f"{RELEASE_NAME}/{path.relative_to(PACKAGE).as_posix()}")

    zip_sha = file_hash(ZIP_PATH)
    sha_path = pathlib.Path(str(ZIP_PATH) + ".sha256")
    sha_path.write_text(f"{zip_sha}  {ZIP_PATH.name}\n", encoding="ascii")
    HISTORY.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ZIP_PATH, HISTORY / ZIP_PATH.name)
    shutil.copy2(sha_path, HISTORY / sha_path.name)
    print(f"ZIP\t{ZIP_PATH}\t{ZIP_PATH.stat().st_size}\t{zip_sha}")


if __name__ == "__main__":
    main()
