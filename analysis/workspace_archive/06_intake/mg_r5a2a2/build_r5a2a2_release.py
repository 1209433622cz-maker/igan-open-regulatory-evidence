#!/usr/bin/env python3
"""Build and verify the compact R5A2A2 release package."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
RELEASE_ROOT = ROOT / "6_release/current/R5A2A2"
RELEASE_NAME = "CMM_R5A2A2_OneK1K_chr18_Usability_2026-09-14"
RELEASE_DIR = RELEASE_ROOT / RELEASE_NAME
ZIP_PATH = RELEASE_ROOT / f"{RELEASE_NAME}.zip"
SHA_PATH = RELEASE_ROOT / f"{RELEASE_NAME}.zip.sha256"
HISTORY_ROOT = ROOT / "6_release/history/R5A2A2_2026-09-14"
DOWNLOADS = Path(r"C:\Users\Administrator\Downloads")
AUDIT_DIR = ROOT / "3_results/00_audit/R5A2A2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def safe_reset(path: Path, expected_parent: Path) -> None:
    resolved = path.resolve()
    parent = expected_parent.resolve()
    if resolved.parent != parent or resolved == parent:
        raise RuntimeError(f"Refusing unsafe recursive reset: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=True)


def copy_files(source: Path, destination: Path, patterns: tuple[str, ...], recursive: bool = False) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    paths: set[Path] = set()
    for pattern in patterns:
        paths.update(source.rglob(pattern) if recursive else source.glob(pattern))
    for path in sorted(p for p in paths if p.is_file()):
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def main() -> int:
    RELEASE_ROOT.mkdir(parents=True, exist_ok=True)
    safe_reset(RELEASE_DIR, RELEASE_ROOT)

    copy_files(ROOT / "7.Report/current/R5A2A2", RELEASE_DIR / "reports", ("*.md",))
    copy_files(ROOT / "2_code/06_intake/mg_r5a2a2", RELEASE_DIR / "code/mg_r5a2a2", ("*.py",))
    copy_files(ROOT / "3_results/00_audit/R5A2A2", RELEASE_DIR / "results/audit", ("*.json", "*.tsv"))
    # A post-build verification describes the ZIP that contains it and would
    # therefore create a circular checksum dependency. Keep it beside the ZIP.
    (RELEASE_DIR / "results/audit/R5A2A2_release_verification.json").unlink(missing_ok=True)
    copy_files(ROOT / "3_results/01_gwas/R5A2A2", RELEASE_DIR / "results/gwas", ("*.tsv", "*.tsv.gz"))
    copy_files(ROOT / "3_results/03_qtl/R5A2A2", RELEASE_DIR / "results/qtl", ("*.tsv", "*.tsv.gz", "*.txt"), recursive=True)
    copy_files(ROOT / "3_results/04_integration/R5A2A2", RELEASE_DIR / "results/integration", ("*.tsv", "*.json"))

    protocol_dir = RELEASE_DIR / "protocol"
    protocol_dir.mkdir(parents=True, exist_ok=True)
    for name in ["R5A2A2_MG_chr18_usability_state.json", "R5A2A3_MG_chr18_coloc_smoke_protocol.md"]:
        shutil.copy2(ROOT / "0_admin/protocol/current" / name, protocol_dir / name)
    workspace_dir = RELEASE_DIR / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "README_WORKSPACE.md", workspace_dir / "README_WORKSPACE.md")

    payload = sorted(path for path in RELEASE_DIR.rglob("*") if path.is_file())
    manifest_path = RELEASE_DIR / "release_manifest.tsv"
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["relative_path", "bytes", "sha256"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for path in payload:
            writer.writerow({
                "relative_path": str(path.relative_to(RELEASE_DIR)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            })

    checksum_targets = sorted(path for path in RELEASE_DIR.rglob("*") if path.is_file())
    checksum_path = RELEASE_DIR / "checksums.sha256"
    checksum_path.write_text(
        "".join(f"{sha256(path)}  {str(path.relative_to(RELEASE_DIR)).replace(chr(92), '/')}\n" for path in checksum_targets),
        encoding="utf-8",
    )

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(RELEASE_DIR.rglob("*")):
            if path.is_file():
                archive.write(path, f"{RELEASE_NAME}/{str(path.relative_to(RELEASE_DIR)).replace(chr(92), '/')}")
    with zipfile.ZipFile(ZIP_PATH) as archive:
        bad_member = archive.testzip()
        zip_members = len(archive.infolist())
    if bad_member is not None:
        raise RuntimeError(f"ZIP CRC failure: {bad_member}")

    zip_sha = sha256(ZIP_PATH)
    SHA_PATH.write_text(f"{zip_sha}  {ZIP_PATH.name}\n", encoding="utf-8")

    HISTORY_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ZIP_PATH, HISTORY_ROOT / ZIP_PATH.name)
    shutil.copy2(SHA_PATH, HISTORY_ROOT / SHA_PATH.name)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ZIP_PATH, DOWNLOADS / ZIP_PATH.name)
    shutil.copy2(SHA_PATH, DOWNLOADS / SHA_PATH.name)
    shutil.copy2(ROOT / "7.Report/current/R5A2A2/99_CMM_R5A2A2_详细行动记录_2026-09-14.md", DOWNLOADS / "99_CMM_R5A2A2_详细行动记录_2026-09-14.md")

    verification = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "release_name": RELEASE_NAME,
        "release_directory": str(RELEASE_DIR.relative_to(ROOT)).replace("\\", "/"),
        "zip_path": str(ZIP_PATH.relative_to(ROOT)).replace("\\", "/"),
        "zip_bytes": ZIP_PATH.stat().st_size,
        "zip_sha256": zip_sha,
        "zip_crc_pass": True,
        "zip_members": zip_members,
        "payload_files_before_manifest_and_checksums": len(payload),
        "downloads_copy_sha256_match": sha256(DOWNLOADS / ZIP_PATH.name) == zip_sha,
        "history_copy_sha256_match": sha256(HISTORY_ROOT / ZIP_PATH.name) == zip_sha,
    }
    verification["release_gate_pass"] = all([
        verification["zip_crc_pass"],
        verification["downloads_copy_sha256_match"],
        verification["history_copy_sha256_match"],
    ])
    verify_path = AUDIT_DIR / "R5A2A2_release_verification.json"
    verify_path.write_text(json.dumps(verification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(verification, indent=2, ensure_ascii=False))
    return 0 if verification["release_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
