#!/usr/bin/env python3
"""Publish the lightweight, auditable R7B1D assets to the public repository."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
REPO = ROOT / "github/igan-open-regulatory-evidence"
CODE = ROOT / "2_code/06_intake/r7b1d"
RAW = ROOT / "3_results/01_intake/R7B1D/finngen_cascade_20261009"
RESULT = ROOT / "3_results/04_integration/R7B1D"
AUDIT = ROOT / "3_results/00_audit/R7B1D"
FIGURE = ROOT / "5_analysis/figures/R7B1D"
REPORT = ROOT / "7.Report/rounds/R7B1D"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(args, cwd=REPO, capture_output=True)
    if check and proc.returncode:
        raise RuntimeError(
            f"command failed: {args}\n"
            f"{proc.stdout.decode('utf-8', 'replace')}\n"
            f"{proc.stderr.decode('utf-8', 'replace')}"
        )
    return proc


def text(*args: str) -> str:
    return run(*args).stdout.decode("utf-8", "replace").strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_file(source: Path, relative: str | Path) -> None:
    destination = REPO / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree(source: Path, relative: str | Path) -> None:
    destination = REPO / relative
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def update_readme() -> None:
    path = REPO / "README.md"
    content = path.read_text(encoding="utf-8")
    marker = "## R7B1D external multiome and direction gate"
    section = f"""{marker}

R7B1D retained four prespecified R7B1B anchors and queried current public FinnGen CASCADE bytes without reopening candidate selection. Three `CHIRBIL_PRIM–IL12RB2` records support PBC–eQTL sharing in `l1.NK`, `l2.NK` and `l1.PBMC` (PP.H4.abf 0.9698–0.9706; credible-set overlap 5–9 variants). The linked IL12RB2 peak is a positional chromatin layer; the eQTL anchor is not in the peak caQTL credible set, so a complete disease→caQTL→expression cascade is not claimed.

Current public FinnGen queries did not return a `CHIRBIL_PRIM–FCRL3` coloc pair. This is recorded as public-output non-return rather than a powered biological negative. FCRL3–B therefore retains OneK source-matched support and TenK cross-resource molecular-QTL replication only. Exact allele harmonization shows the PBC risk allele is associated with higher IL12RB2 expression across OneK, TenK and FinnGen contexts, and with lower FCRL3 expression in OneK and TenK B-cell contexts. These are directional associations, not mediation estimates.

The external gate is `PASS_BOUNDED`. R7B1C did not establish general method superiority; the next stage is a single integrated claim–evidence ledger and Figure 1–6 source-data freeze before manuscript rewriting.

![R7B1D external evidence overview](figures/R7B1D/R7B1D_external_evidence_overview.png)
"""
    if marker in content:
        start = content.index(marker)
        next_section = content.find("\n## ", start + len(marker))
        content = content[:start] + section.rstrip() + "\n" + (
            content[next_section:] if next_section != -1 else ""
        )
    else:
        content = content.rstrip() + "\n\n" + section
    path.write_text(content, encoding="utf-8")


def write_large_asset_manifest() -> None:
    manifest = REPO / "data/R7B1D_LARGE_ASSET_MANIFEST.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ["asset", "role", "source", "bytes", "checksum", "public_copy", "reason"],
        ["OneK1K_full_cis_eQTL", "primary cell-QTL summaries", "Zenodo 18910121", "10344009571", "md5:e42239480f40abd21f221c0d77c82cc3", "NO", "third-party 10.34 GB archive"],
        ["OneK1K_genotype_980", "source-matched QTL LD", "Zenodo 18910121", "233198074", "md5:be1053e34fa023bc808388d4e0bf2aa1", "NO", "third-party donor genotype"],
        ["TenK10K_coloc_100kb", "independent molecular-QTL replication", "Zenodo 18221260", "626505208", "md5:c627f1c4bc47706e331039d1e9e6e7d1", "NO", "third-party large archive"],
        ["GJOKA_SUMSTATS", "PBC locus summaries and disease LD", "Newcastle GJOKA public archive", "1184054519", "112 member CRCs present", "NO", "third-party large archive"],
        ["FinnGen_CASCADE_R7B1D", "external disease/eQTL/chromatin layer", "https://cascade.finngen.fi/", "SMALL_AGGREGATE_JSON", "per-object SHA-256 in receipts", "YES", "current public aggregate output retained for audit"],
    ]
    manifest.write_text("\n".join("\t".join(row) for row in rows) + "\n", encoding="utf-8")


def rebuild_manifest() -> None:
    manifest = REPO / "MANIFEST.sha256"
    files = sorted(
        path for path in REPO.rglob("*")
        if path.is_file() and ".git" not in path.parts and path != manifest
    )
    manifest.write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(REPO).as_posix()}" for path in files) + "\n",
        encoding="utf-8",
    )


def safety_checks() -> None:
    files = [path for path in REPO.rglob("*") if path.is_file() and ".git" not in path.parts]
    oversized = [str(path.relative_to(REPO)) for path in files if path.stat().st_size > 10 * 1024 * 1024]
    if oversized:
        raise RuntimeError(f"files over 10 MiB: {oversized}")
    secret = re.compile(
        r"(?i)(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|"
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"
    )
    hits: list[str] = []
    for path in files:
        if path.suffix.lower() in {".png", ".pdf", ".gz", ".zip", ".bin"}:
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if secret.search(body):
            hits.append(str(path.relative_to(REPO)))
    if hits:
        raise RuntimeError(f"secret-pattern hits: {hits}")


def main() -> None:
    if text("git", "status", "--porcelain"):
        raise RuntimeError("repository must be clean before R7B1D sync")
    local_before = text("git", "rev-parse", "HEAD")
    remote_before = text("git", "ls-remote", "origin", "refs/heads/main").split()[0]
    if local_before != remote_before:
        raise RuntimeError(f"local HEAD {local_before} differs from remote main {remote_before}")

    copy_tree(CODE, "analysis/r7b1d")
    copy_tree(RAW, "environment/R7B1D/finngen_cascade_20261009")
    copy_tree(RESULT, "results/r7b1d")
    copy_tree(AUDIT, "results/r7b1d/audit")
    copy_tree(FIGURE, "figures/R7B1D")
    copy_tree(REPORT, "reports/R7B1D")
    copy_file(REPORT / "04_CMM_R7B1D_G6判定与R7B1E冻结目标.md", "protocols/R7B1D/R7B1E_frozen_scope.md")
    write_large_asset_manifest()
    update_readme()
    rebuild_manifest()
    safety_checks()

    run("git", "add", "analysis/r7b1d", "environment/R7B1D", "results/r7b1d", "figures/R7B1D", "reports/R7B1D", "protocols/R7B1D", "data/R7B1D_LARGE_ASSET_MANIFEST.tsv", "README.md", "MANIFEST.sha256")
    # Matplotlib SVG path records and rectangular TSVs can contain meaningful
    # trailing spaces/tabs. Keep their bytes unchanged and apply the whitespace
    # gate to all human-authored/code files.
    run(
        "git", "diff", "--cached", "--check", "--", ".",
        ":(exclude)figures/R7B1D/*.svg",
        ":(exclude)results/r7b1d/*.tsv",
    )
    changed = [line for line in text("git", "diff", "--cached", "--name-only").splitlines() if line]
    if not changed:
        remote_after = remote_before
        status = "NO_CHANGES"
    else:
        run("git", "commit", "-m", "Complete R7B1D external multiome direction gate")
        run("git", "push", "origin", "main")
        remote_after = text("git", "ls-remote", "origin", "refs/heads/main").split()[0]
        local_after = text("git", "rev-parse", "HEAD")
        if remote_after != local_after:
            raise RuntimeError(f"remote verification failed: local={local_after} remote={remote_after}")
        status = "PASS"

    state = {
        "schema": "R7B1D_GITHUB_SYNC_1.0",
        "status": status,
        "previous_head": local_before,
        "remote_head": remote_after,
        "files_changed": len(changed),
        "large_assets_committed": False,
        "max_committed_file_bytes": max(
            path.stat().st_size for path in REPO.rglob("*")
            if path.is_file() and ".git" not in path.parts
        ),
        "secret_scan": "PASS",
        "oversize_gate": "PASS_LE_10_MIB",
    }
    state_path = AUDIT / "R7B1D_github_sync_receipt.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
