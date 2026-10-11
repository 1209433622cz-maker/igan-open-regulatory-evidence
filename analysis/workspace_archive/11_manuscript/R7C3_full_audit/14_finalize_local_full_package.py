#!/usr/bin/env python3
"""Refresh the local-full archive with final GitHub release receipts."""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
AUDIT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11"
CODE = ROOT / "2_code" / "11_manuscript" / "R7C3_full_audit"
REL = ROOT / "6_release" / "R7C3_2026-10-11"
NAME = "CMM_R7C3_FullWorkspaceAudit_SubmissionGate_LOCAL_2026-10-11"
STAGE = REL / NAME
ZIP = REL / f"{NAME}.zip"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


for dst, src in ((STAGE / "code", CODE), (STAGE / "audit" / "reports", AUDIT / "reports"), (STAGE / "audit" / "github", AUDIT / "github"), (STAGE / "audit" / "qa", AUDIT / "qa")):
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
manifest = STAGE / "checksums.sha256"
files = sorted(p for p in STAGE.rglob("*") if p.is_file() and p != manifest)
with manifest.open("w", encoding="utf-8", newline="\n") as f:
    for p in files: f.write(f"{sha256(p)}  {p.relative_to(STAGE).as_posix()}\n")
if ZIP.exists(): ZIP.unlink()
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as z:
    for p in sorted(STAGE.rglob("*")):
        if p.is_file(): z.write(p, p.relative_to(STAGE.parent).as_posix())
with zipfile.ZipFile(ZIP) as z:
    bad, entries = z.testzip(), len(z.infolist())
if bad is not None: raise RuntimeError(bad)
digest = sha256(ZIP)
Path(str(ZIP)+".sha256").write_text(f"{digest}  {ZIP.name}\n", encoding="utf-8")
print(f"entries={entries}\nbytes={ZIP.stat().st_size}\nsha256={digest}\ncrc=PASS")
