#!/usr/bin/env python3
"""Archive and CRC-check the standalone R7C3 journal upload bundle."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
SRC = ROOT / "5_manuscript" / "R7C3_npj_FinalSubmissionPackage_2026-10-11"
OUT = ROOT / "6_release" / "R7C3_2026-10-11" / "PBC_R7C3_npj_FinalSubmissionPackage_2026-10-11.zip"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(SRC.rglob("*")):
        if p.is_file(): z.write(p, p.relative_to(SRC.parent).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad, entries = z.testzip(), len(z.infolist())
if bad is not None: raise RuntimeError(bad)
digest = sha256(OUT)
Path(str(OUT)+".sha256").write_text(f"{digest}  {OUT.name}\n", encoding="utf-8")
state = {"path": str(OUT), "bytes": OUT.stat().st_size, "sha256": digest, "entries": entries, "crc": "PASS"}
Path(str(OUT)+".json").write_text(json.dumps(state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(state, ensure_ascii=False, indent=2))
