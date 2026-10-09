#!/usr/bin/env python3
"""Package the R7B4B0 pre-author final-submission gate."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
BASE = ROOT / "5_manuscript" / "R7B4B_PreauthorFinalSubmissionGate"
CODE = ROOT / "2_code" / "11_manuscript" / "R7B4B"
OUT = ROOT / "6_release"
NAME = "CMM_R7B4B0_PreauthorFinalSubmissionGate_2026-10-10"
ZIP = OUT / f"{NAME}.zip"
SHA = OUT / f"{NAME}.zip.sha256"
RECEIPT = OUT / f"{NAME}_release_receipt.json"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_tree(entries: dict[str, Path], source: Path, arc_root: str) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            entries[f"{NAME}/{arc_root}/{path.relative_to(source).as_posix()}"] = path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    entries: dict[str, Path] = {}
    for folder in ["results", "qa", "submission", "reports"]:
        add_tree(entries, BASE / folder, folder)
    add_tree(entries, CODE, "code")
    readme = """# R7B4B0 Pre-author Final-submission Gate

This release independently verifies the frozen R7B4A archive and repository identity, audits reference first-appearance order, separates AUTHOR_REVIEW from FINAL_SUBMISSION QA, and provides a privacy-preserving author-record schema plus fail-closed final QA.

Pre-author QA: 10 PASS / 8 HOLD / 0 FAIL.

The HOLD items require verified author or institutional input. No biological analysis was reopened. This package does not authorize or perform external submission.

Public release tag: r7b4b0-preauthor-final-submission-gate-2026-10-10
Release commit: cc8e7cdf177d574615fefa7d9fa12c73c5f3add7
""".encode("utf-8")
    lines = [f"{sha_file(path)}  {arc.removeprefix(NAME + '/')}" for arc, path in sorted(entries.items())]
    lines.append(f"{sha_bytes(readme)}  README.md")
    checksum_data = ("\n".join(lines) + "\n").encode("utf-8")
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for arc, path in sorted(entries.items()):
            archive.write(path, arc)
        archive.writestr(f"{NAME}/README.md", readme)
        archive.writestr(f"{NAME}/checksums.sha256", checksum_data)
    with zipfile.ZipFile(ZIP) as archive:
        bad = archive.testzip()
        manifest = archive.read(f"{NAME}/checksums.sha256").decode("utf-8").splitlines()
        for line in manifest:
            expected, relative = line.split("  ", 1)
            actual = sha_bytes(archive.read(f"{NAME}/{relative}"))
            if expected != actual:
                raise RuntimeError(f"Checksum mismatch: {relative}")
        members = len(archive.infolist())
    if bad is not None:
        raise RuntimeError(f"CRC failure: {bad}")
    outer = sha_file(ZIP)
    SHA.write_text(f"{outer}  {ZIP.name}\n", encoding="utf-8")
    receipt = {
        "release": ZIP.name,
        "bytes": ZIP.stat().st_size,
        "sha256": outer,
        "zip_crc": "PASS",
        "zip_entries": members,
        "internal_checksums": f"{len(manifest)}/{len(manifest)} PASS",
        "preauthor_gate": "10 PASS / 8 HOLD / 0 FAIL",
        "release_commit": "cc8e7cdf177d574615fefa7d9fa12c73c5f3add7",
        "github_sync": "CHECK_SEPARATE_RECEIPT",
        "status": "PASS_PREAUTHOR_GATE_HUMAN_INPUT_REQUIRED"
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
