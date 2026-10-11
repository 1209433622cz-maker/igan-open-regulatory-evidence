#!/usr/bin/env python3
"""Fail-closed audit of the public GitHub worktree."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
REPO = ROOT / "0_admin" / "repositories" / "igan-open-regulatory-evidence"
OUT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11" / "github"
OUT.mkdir(parents=True, exist_ok=True)

TEXT_EXT = {".md", ".txt", ".tsv", ".csv", ".json", ".yaml", ".yml", ".cff", ".py", ".r", ".ps1", ".sh", ".toml", ".ini"}
SECRET_PATTERNS = {
    "github_pat": re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "zenodo_token_assignment": re.compile(r"(?i)(?:ZENODO|ACCESS)[_ -]?TOKEN\s*[:=]\s*['\"]?[A-Za-z0-9._-]{20,}"),
}


def run(*args: str) -> str:
    return subprocess.run(args, cwd=REPO, check=True, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.strip()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


tracked = [x for x in run("git", "ls-files", "-z").split("\0") if x]
manifest_expected = {}
for line in (REPO / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
    if not line.strip(): continue
    digest, rel = line.split("  ", 1)
    manifest_expected[rel] = digest

manifest_failures = []
for rel, expected in manifest_expected.items():
    p = REPO / rel
    if not p.is_file(): manifest_failures.append({"path": rel, "reason": "MISSING"})
    elif sha256(p) != expected: manifest_failures.append({"path": rel, "reason": "HASH_MISMATCH"})

manifest_scope = sorted(x for x in tracked if x != "MANIFEST.sha256")
manifest_missing_entries = sorted(set(manifest_scope) - set(manifest_expected))
manifest_extra_entries = sorted(set(manifest_expected) - set(manifest_scope))

large = []
secret_hits = []
for rel in tracked:
    p = REPO / rel
    if not p.is_file(): continue
    size = p.stat().st_size
    if size > 10 * 1024 * 1024:
        large.append({"path": rel, "size_bytes": size})
    if p.suffix.lower() in TEXT_EXT and size <= 8 * 1024 * 1024:
        text = p.read_text(encoding="utf-8", errors="replace")
        for name, pat in SECRET_PATTERNS.items():
            if pat.search(text): secret_hits.append({"path": rel, "pattern": name})

state = {
    "stage": "R7C3_GITHUB_PRE_SYNC_AUDIT",
    "timestamp": datetime.now().astimezone().isoformat(),
    "repo": str(REPO),
    "branch": run("git", "branch", "--show-current"),
    "head": run("git", "rev-parse", "HEAD"),
    "origin_main": run("git", "rev-parse", "origin/main"),
    "status_porcelain": run("git", "status", "--porcelain"),
    "tracked_files": len(tracked),
    "manifest_entries": len(manifest_expected),
    "manifest_failures": manifest_failures,
    "manifest_missing_entries": manifest_missing_entries,
    "manifest_extra_entries": manifest_extra_entries,
    "files_over_10MiB": large,
    "secret_pattern_hits": secret_hits,
    "git_fsck": run("git", "fsck", "--full", "--no-dangling"),
    "license_code": (REPO / "LICENSE").is_file(),
    "license_content": (REPO / "LICENSE_CONTENT.md").is_file(),
    "citation_cff": (REPO / "CITATION.cff").is_file(),
    "zenodo_metadata": (REPO / ".zenodo.json").is_file(),
}
(OUT / "R7C3_github_pre_sync_audit.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(state, ensure_ascii=False, indent=2))
