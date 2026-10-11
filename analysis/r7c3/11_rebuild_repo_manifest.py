#!/usr/bin/env python3
"""Rebuild MANIFEST.sha256 from the exact Git tracked-file set."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

REPO = Path(r"H:\SCI2\YR1\0_admin\repositories\igan-open-regulatory-evidence")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


tracked = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, check=True, stdout=subprocess.PIPE).stdout.decode("utf-8").split("\0")
tracked = sorted(x for x in tracked if x and x != "MANIFEST.sha256")
missing = [x for x in tracked if not (REPO / x).is_file()]
if missing: raise RuntimeError(f"tracked files missing: {missing[:10]}")
with (REPO / "MANIFEST.sha256").open("w", encoding="utf-8", newline="\n") as f:
    for rel in tracked:
        f.write(f"{sha256(REPO / rel)}  {rel}\n")
print(f"tracked_without_manifest={len(tracked)}")
