#!/usr/bin/env python3
"""Publish lightweight R7B1E0/R7B1E closure assets to the public repository."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
REPO = ROOT / "github/igan-open-regulatory-evidence"
AUDIT0 = ROOT / "3_results/00_audit/R7B1E0"
AUDITE = ROOT / "3_results/00_audit/R7B1E"
REPLAY = ROOT / "3_results/04_integration/R7B1E0/kriging_replay"


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


def write_replay_manifest() -> None:
    output = REPO / "data/R7B1E0_LOCAL_REPLAY_MANIFEST.tsv"
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["relative_path\tbytes\tsha256\tpublic_copy\treason"]
    for path in sorted(REPLAY.rglob("*")):
        if not path.is_file() or path.parent == REPLAY:
            continue
        rel = path.relative_to(ROOT).as_posix()
        lines.append(f"{rel}\t{path.stat().st_size}\t{sha256(path)}\tNO\tper-locus replay intermediate or log; aggregate result is public")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_readme() -> None:
    path = REPO / "README.md"
    content = path.read_text(encoding="utf-8")
    marker = "## R7B1E0 diagnostic closure and R7B1E evidence freeze"
    section = f"""{marker}

R7B1E0 repaired a post-result diagnostic interface defect without refitting SuSiE or coloc. The historical runner expected `kriging_rss()` to return a data frame, whereas `susieR 0.14.2` returns a list containing `conditional_dist`. Exact replay of the frozen z, LD, sample size, variant order and fitted `s_rss` completed 2,568/2,568 disease/QTL × PF10/PF50 diagnostic units across 642 comparisons and 47 loci. The official plotting rule (`logLR > 2` and `|z| > 2`) yielded one unique reviewed event, rs1800378; it entered no credible set and required no posterior refit. Historical classifications were preserved.

Signal-level semantic review confirmed the same pair identity for all 92 stable-H4 and all 428 stable-H3 comparisons across L10 and at least one other PF10 L setting. Thirty-two stable-H4 comparisons also contained an H3-qualifying pair, so shared and distinct pairs can coexist within a comparison. Stable H3 is therefore reported as support for a distinct pair, not global proof that no shared pair exists.

R7B1E freezes 22 claim–evidence records, nine hashed figure-source assets and a Figure 1–6 panel manifest. The evidence ceiling is **PBC-wide screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset, with scenario-dependent calibration and bounded external/tissue support**. General method superiority, a complete regulatory cascade and PBC-specific tissue enrichment are not established. Independent QA passes 21/21 checks for R7B1E0 and 21/21 for R7B1E. The next stage is R7B2 manuscript v1, with no reopening of locus, gene or cell selection.

![R7B1E figure-source architecture](figures/R7B1E/R7B1E_figure_source_architecture.png)
"""
    if marker in content:
        start = content.index(marker)
        end = content.find("\n## ", start + len(marker))
        content = content[:start] + section.rstrip() + "\n" + (content[end:] if end != -1 else "")
    else:
        content = content.rstrip() + "\n\n" + section
    path.write_text(content, encoding="utf-8")


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
        raise RuntimeError("repository must be clean before R7B1E sync")
    local_before = text("git", "rev-parse", "HEAD")
    remote_before = text("git", "ls-remote", "origin", "refs/heads/main").split()[0]
    if local_before != remote_before:
        raise RuntimeError(f"local HEAD {local_before} differs from remote main {remote_before}")

    copy_tree(ROOT / "2_code/06_intake/r7b1e0", "analysis/r7b1e0")
    copy_tree(ROOT / "2_code/06_intake/r7b1e", "analysis/r7b1e")
    copy_file(ROOT / "0_admin/protocols/R7B1E0/R7B1E0_diagnostic_replay_signal_semantics_freeze_2026-10-09.md", "protocols/R7B1E0/R7B1E0_diagnostic_replay_signal_semantics_freeze_2026-10-09.md")
    copy_file(ROOT / "0_admin/protocols/R7B1E/R7B1E_claim_evidence_figure_freeze_2026-10-09.md", "protocols/R7B1E/R7B1E_claim_evidence_figure_freeze_2026-10-09.md")

    copy_tree(ROOT / "3_results/04_integration/R7B1E0/diagnostic_adjudication", "results/r7b1e0/diagnostic_adjudication")
    copy_tree(ROOT / "3_results/04_integration/R7B1E0/signal_semantics", "results/r7b1e0/signal_semantics")
    copy_file(REPLAY / "orchestrator_state.json", "results/r7b1e0/kriging_replay/orchestrator_state.json")
    copy_file(REPLAY / "orchestrator_loci.tsv", "results/r7b1e0/kriging_replay/orchestrator_loci.tsv")
    copy_tree(AUDIT0, "results/r7b1e0/audit")

    copy_tree(ROOT / "3_results/04_integration/R7B1E", "results/r7b1e")
    copy_tree(AUDITE, "results/r7b1e/audit")
    copy_tree(ROOT / "5_analysis/figures/R7B1E", "figures/R7B1E")
    copy_tree(ROOT / "7.Report/rounds/R7B1E", "reports/R7B1E")
    write_replay_manifest()
    update_readme()
    rebuild_manifest()
    safety_checks()

    paths = [
        "analysis/r7b1e0", "analysis/r7b1e", "protocols/R7B1E0", "protocols/R7B1E",
        "results/r7b1e0", "results/r7b1e", "figures/R7B1E", "reports/R7B1E",
        "data/R7B1E0_LOCAL_REPLAY_MANIFEST.tsv", "README.md", "MANIFEST.sha256",
    ]
    run("git", "add", *paths)
    run(
        "git", "diff", "--cached", "--check", "--", ".",
        ":(exclude)figures/R7B1E/*.svg",
        ":(exclude)results/r7b1e/**/*.tsv",
        ":(exclude)results/r7b1e0/**/*.tsv",
        ":(exclude)data/*.tsv",
    )
    changed = [line for line in text("git", "diff", "--cached", "--name-only").splitlines() if line]
    if changed:
        run("git", "commit", "-m", "Freeze R7B1E diagnostic closure and evidence ledger")
        run("git", "push", "origin", "main")
        status = "PASS"
    else:
        status = "NO_CHANGES"
    local_after = text("git", "rev-parse", "HEAD")
    remote_after = text("git", "ls-remote", "origin", "refs/heads/main").split()[0]
    if local_after != remote_after:
        raise RuntimeError(f"remote verification failed: local={local_after} remote={remote_after}")
    if text("git", "status", "--porcelain"):
        raise RuntimeError("repository is not clean after push")

    state = {
        "schema": "R7B1E_GITHUB_SYNC_1.0",
        "status": status,
        "previous_head": local_before,
        "remote_head": remote_after,
        "files_changed": len(changed),
        "large_assets_committed": False,
        "per_locus_replay_intermediates": "LOCAL_ONLY_HASH_MANIFEST_PUBLIC",
        "secret_scan": "PASS",
        "oversize_gate": "PASS_LE_10_MIB",
    }
    output = AUDITE / "R7B1E_github_sync_receipt.json"
    output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
