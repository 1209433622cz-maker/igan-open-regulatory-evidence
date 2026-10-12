#!/usr/bin/env python3
"""Build local-full and public R7C3 release archives with internal checksums."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
AUDIT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11"
CODE = ROOT / "2_code" / "11_manuscript" / "R7C3_full_audit"
SUB = ROOT / "5_manuscript" / "R7C3_npj_FinalSubmissionPackage_2026-10-11"
REL = ROOT / "6_release" / "R7C3_2026-10-11"
FULL_NAME = "CMM_R7C3_FullWorkspaceAudit_SubmissionGate_LOCAL_2026-10-11"
PUBLIC_NAME = "CMM_R7C3_PublicAudit_SubmissionRelease_2026-10-11"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def copytree_clean(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def manifest(stage: Path) -> int:
    files = sorted(p for p in stage.rglob("*") if p.is_file() and p.name != "checksums.sha256")
    with (stage / "checksums.sha256").open("w", encoding="utf-8", newline="\n") as f:
        for p in files: f.write(f"{sha256(p)}  {p.relative_to(stage).as_posix()}\n")
    return len(files)


def zip_stage(stage: Path, target: Path) -> dict:
    if target.exists(): target.unlink()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file(): z.write(p, p.relative_to(stage.parent).as_posix())
    with zipfile.ZipFile(target) as z:
        bad = z.testzip()
        entries = len(z.infolist())
    if bad is not None: raise RuntimeError(f"ZIP CRC failure: {bad}")
    return {"path": str(target), "bytes": target.stat().st_size, "sha256": sha256(target), "entries": entries, "crc": "PASS"}


REL.mkdir(parents=True, exist_ok=True)
for name in (FULL_NAME, PUBLIC_NAME):
    d = REL / name
    if d.exists(): shutil.rmtree(d)
    d.mkdir()

full = REL / FULL_NAME
public = REL / PUBLIC_NAME

# Local-full package: includes path-level inventory and all audit outputs.
copytree_clean(CODE, full / "code")
for d in ("inventory", "integrity", "duplicates", "records", "fragments", "assets", "github", "reports", "public"):
    copytree_clean(AUDIT / d, full / "audit" / d)
copytree_clean(SUB, full / "submission_package")

# Public package: only relative-path summaries, reports, code and approved journal files.
copytree_clean(CODE, public / "code")
copytree_clean(AUDIT / "reports", public / "reports")
copytree_clean(AUDIT / "public", public / "audit_summary")
copytree_clean(SUB, public / "submission_package")
shutil.copy2(AUDIT / "github" / "R7C3_git_commit_receipt.json", public / "R7C3_git_commit_receipt.json")

notes = """# R7C3 public release notes

R7C3 completes a content-aware audit of the local research workspace and freezes the author-operated npj Genomic Medicine submission gate. The public package contains relative-path-only summaries, a canonical work-record ledger, a high-value asset register, the audit code and the author-approved journal files. It excludes third-party raw data, individual-level data, credentials, tokens and the full absolute-path inventory.

The scientific analysis is unchanged from R7C2. PBC remains GO; the next stage is R7C4 author-operated submission and receipt capture. No Zenodo DOI has been minted.
"""
(public / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
(full / "README_LOCAL_FULL.md").write_text("# Local full R7C3 audit package\n\nThis archive contains the complete local inventory and may expose absolute workspace paths. Keep it local; publish the PUBLIC archive instead.\n", encoding="utf-8")

full_files = manifest(full)
public_files = manifest(public)
full_zip = zip_stage(full, REL / f"{FULL_NAME}.zip")
public_zip = zip_stage(public, REL / f"{PUBLIC_NAME}.zip")
for rec in (full_zip, public_zip):
    Path(rec["path"] + ".sha256").write_text(f"{rec['sha256']}  {Path(rec['path']).name}\n", encoding="utf-8")

state = {
    "stage": "R7C3_RELEASE_BUILD",
    "built": datetime.now().astimezone().isoformat(),
    "local_full_internal_files_before_manifest": full_files,
    "public_internal_files_before_manifest": public_files,
    "local_full": full_zip,
    "public": public_zip,
    "submission_package_status": json.loads((SUB / "00_Submission_Package_State.json").read_text(encoding="utf-8"))["status"],
}
(REL / "R7C3_release_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(state, ensure_ascii=False, indent=2))
