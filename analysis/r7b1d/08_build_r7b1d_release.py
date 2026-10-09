#!/usr/bin/env python3
"""Build and independently verify the lightweight R7B1D release package."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
CODE = ROOT / "2_code/06_intake/r7b1d"
RAW = ROOT / "3_results/01_intake/R7B1D/finngen_cascade_20261009"
RESULT = ROOT / "3_results/04_integration/R7B1D"
AUDIT = ROOT / "3_results/00_audit/R7B1D"
FIGURE = ROOT / "5_analysis/figures/R7B1D"
REPORT = ROOT / "7.Report/rounds/R7B1D"
RELEASE = ROOT / "6_release/R7B1D"
STAGE = RELEASE / "stage"
ZIP_PATH = RELEASE / "CMM_R7B1D_ExternalMultiome_DirectionGate_2026-10-09.zip"
DOWNLOADS = Path(r"C:\Users\Administrator\Downloads")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_tree(source: Path, relative: str | Path) -> None:
    destination = STAGE / relative
    shutil.copytree(source, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def verify_internal(zip_path: Path) -> tuple[int, int]:
    with zipfile.ZipFile(zip_path) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failed at {bad}")
        checks = archive.read("checksums.sha256").decode("utf-8").strip().splitlines()
        passed = 0
        for line in checks:
            expected, name = line.split("  ", 1)
            observed = hashlib.sha256(archive.read(name)).hexdigest()
            if observed != expected:
                raise RuntimeError(f"internal checksum failed: {name}")
            passed += 1
        return len(archive.infolist()), passed


def main() -> None:
    qa = json.loads((AUDIT / "R7B1D_independent_QA.json").read_text(encoding="utf-8"))
    sync = json.loads((AUDIT / "R7B1D_github_sync_receipt.json").read_text(encoding="utf-8"))
    if qa.get("status") != "PASS" or qa.get("passed") != qa.get("total"):
        raise RuntimeError("R7B1D independent QA is not fully PASS")
    if sync.get("status") not in {"PASS", "NO_CHANGES"}:
        raise RuntimeError("public GitHub sync is not verified")

    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    copy_tree(CODE, "code")
    copy_tree(RAW, "raw_public_bytes/finngen_cascade_20261009")
    copy_tree(RESULT, "results")
    copy_tree(AUDIT, "audit")
    copy_tree(FIGURE, "figures")
    copy_tree(REPORT, "reports")

    readme = f"""# CMM R7B1D release

This package closes the external molecular/chromatin replication and risk-allele direction gate defined by the doctoral research plan v2.

Status:

```text
R7B1D = COMPLETE
INDEPENDENT_QA = {qa['passed']}/{qa['total']} PASS
G6_EXTERNAL_REPLICATION = PASS_BOUNDED
PUBLIC_GITHUB_SYNC = {sync['status']} @ {sync['remote_head']}
NEXT = R7B1E_INTEGRATED_CLAIM_EVIDENCE_FREEZE_AND_FIGURE_SOURCE_ASSEMBLY
```

The package contains current public FinnGen aggregate JSON bytes, URL/time/hash receipts, frozen targets, derived tables, code, three figure formats, reports, QA and the GitHub sync receipt. Donor-level genotype/LD and large third-party archives are not redistributed.
"""
    (STAGE / "README.md").write_text(readme, encoding="utf-8")

    files = sorted(path for path in STAGE.rglob("*") if path.is_file() and path.name != "checksums.sha256")
    checksum_lines = [f"{sha256(path)}  {path.relative_to(STAGE).as_posix()}" for path in files]
    (STAGE / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in STAGE.rglob("*") if item.is_file()):
            archive.write(path, path.relative_to(STAGE).as_posix())

    entries, internal_passed = verify_internal(ZIP_PATH)
    digest = sha256(ZIP_PATH)
    hash_path = Path(str(ZIP_PATH) + ".sha256")
    hash_path.write_text(f"{digest}  {ZIP_PATH.name}\n", encoding="utf-8")

    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    for path in [ZIP_PATH, hash_path]:
        shutil.copy2(path, DOWNLOADS / path.name)
    action = REPORT / "99_CMM_R7B1D_详细行动记录_2026-10-09.md"
    shutil.copy2(action, DOWNLOADS / action.name)
    shutil.copy2(action, ROOT / action.name)

    state = {
        "schema": "R7B1D_RELEASE_1.0",
        "status": "PASS",
        "zip": str(ZIP_PATH),
        "downloads_copy": str(DOWNLOADS / ZIP_PATH.name),
        "sha256": digest,
        "zip_crc": "PASS",
        "entries": entries,
        "internal_checksums_passed": internal_passed,
        "github_head": sync["remote_head"],
    }
    (RELEASE / "release_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
