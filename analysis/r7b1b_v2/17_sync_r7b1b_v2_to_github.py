#!/usr/bin/env python3
"""Publish lightweight R7B1B v2 code, protocols, aggregates and provenance."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
REPO = ROOT / "github/igan-open-regulatory-evidence"
CODE = ROOT / "2_code/06_intake/r7b1"
AUDIT = ROOT / "3_results/00_audit/R7B1B_v2"
ADJ = ROOT / "3_results/04_integration/R7B1B_v2/adjudication"
FIG = ROOT / "4_figures/R7B1B_v2"
REPORT = ROOT / "7.Report/rounds/R7B1B_v2"
PROTOCOL = ROOT / "0_admin/protocols/R7B1B"
MULTI = ROOT / "3_results/04_integration/R7B1B_v2/multisignal"


def run(*args: str) -> str:
    # Git can emit UTF-8 paths even when the Windows Python locale is GBK.
    # Decode explicitly so Chinese report names cannot break the publication gate.
    proc = subprocess.run(
        args, cwd=REPO, text=True, capture_output=True,
        encoding="utf-8", errors="replace",
    )
    if proc.returncode:
        raise RuntimeError(f"command failed {args}:\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout.strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy(src: Path, rel: str | Path) -> None:
    dst = REPO / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def finish_push(previous_head: str, changed: int | None = None) -> dict:
    run("git", "push", "origin", "main")
    new_head = run("git", "rev-parse", "HEAD")
    remote_head = run("git", "ls-remote", "origin", "refs/heads/main").split()[0]
    if new_head != remote_head:
        raise RuntimeError("remote HEAD does not match pushed commit")
    sync_state = {
        "schema": "R7B1B_V2_GITHUB_SYNC_1.0",
        "status": "PASS",
        "repository": run("git", "remote", "get-url", "origin"),
        "previous_head": previous_head,
        "content_commit": new_head,
        "remote_head": remote_head,
        "files_changed": changed,
        "large_binary_assets_committed": False,
        "large_assets_represented_by": "data/R7B1B_v2_LARGE_DERIVED_ASSETS.tsv",
    }
    state_path = AUDIT / "R7B1B_v2_GitHub_sync_state.json"
    state_path.write_text(json.dumps(sync_state, indent=2) + "\n", encoding="utf-8")
    return sync_state


def main() -> None:
    if run("git", "status", "--porcelain"):
        raise RuntimeError("repository must be clean before R7B1B v2 sync")
    run("git", "fetch", "origin", "main")
    head = run("git", "rev-parse", "HEAD")
    remote = run("git", "rev-parse", "origin/main")
    if head != remote:
        left, right = [int(x) for x in run("git", "rev-list", "--left-right", "--count", "origin/main...HEAD").split()]
        subject = run("git", "log", "-1", "--pretty=%s")
        if left == 0 and right == 1 and subject == "Complete R7B1B v2 bidirectional multi-signal benchmark":
            # Resume an already validated local commit after a transient network failure.
            print(json.dumps(finish_push(remote, None), indent=2))
            return
        raise RuntimeError(f"local HEAD {head} differs from origin/main {remote}")

    code_names = [
        "08_freeze_r7b1b_v2_high_information_workload.py",
        "09_fetch_r7b1b_v2_gjoka_members.py",
        "10_build_r7b1b_v2_dualmodel_qtl_ld.py",
        "11_run_r7b1b_v2_multisignal_locus.R",
        "12_orchestrate_r7b1b_v2_multisignal.py",
        "13_adjudicate_r7b1b_v2.py",
        "14_independent_qa_r7b1b_v2.py",
        "15_build_r7b1b_v2_figures.py",
        "16_build_r7b1b_v2_reports_release.py",
        "17_sync_r7b1b_v2_to_github.py",
        "RUN_R7B1B_V2_HIGH_INFORMATION_MULTISIGNAL.ps1",
    ]
    for name in code_names:
        copy(CODE / name, Path("analysis/r7b1b_v2") / name)
    for name in ["R7B1B_v2_high_information_multisignal_addendum.md", "R7B1B_v2_adjudication_freeze_2026-10-03.md"]:
        copy(PROTOCOL / name, Path("protocols") / name)
    for path in REPORT.glob("*.md"):
        copy(path, Path("reports/R7B1B_v2") / path.name)
    for path in FIG.rglob("*"):
        if path.is_file():
            copy(path, Path("figures/R7B1B_v2") / path.relative_to(FIG))

    audit_names = [
        "R7B1B_v2_exact_642_high_information_comparisons.tsv",
        "R7B1B_v2_exact_286_cell_locus_blocks.tsv",
        "R7B1B_v2_required_94_GJOKA_members.tsv",
        "R7B1B_v2_exact_3_borderline_calibration.tsv",
        "R7B1B_v2_freeze_state.json",
        "R7B1B_v2_GJOKA_member_receipts.tsv",
        "R7B1B_v2_GJOKA_intake_state.json",
        "R7B1B_v2_dualmodel_QTL_receipts.tsv",
        "R7B1B_v2_sourceLD_block_receipts.tsv",
        "R7B1B_v2_cell_model_receipts.tsv",
        "R7B1B_v2_original184_PF10_regression_QA.tsv",
        "R7B1B_v2_dualmodel_sourceLD_state.json",
        "R7B1B_v2_GJOKA_BETA_SE_STAT_rounding_audit.tsv",
    ]
    for name in audit_names:
        copy(AUDIT / name, Path("results/r7b1b_v2/audit") / name)
    for path in (AUDIT / "independent_QA").glob("*"):
        if path.is_file(): copy(path, Path("results/r7b1b_v2/independent_QA") / path.name)
    for path in ADJ.glob("*"):
        if path.is_file(): copy(path, Path("results/r7b1b_v2/adjudication") / path.name)
    copy(MULTI / "orchestrator_state.json", "results/r7b1b_v2/orchestrator_state.json")

    intake = json.loads((AUDIT / "R7B1B_v2_GJOKA_intake_state.json").read_text(encoding="utf-8"))
    inputs = json.loads((AUDIT / "R7B1B_v2_dualmodel_sourceLD_state.json").read_text(encoding="utf-8"))
    derived = REPO / "data/R7B1B_v2_LARGE_DERIVED_ASSETS.tsv"
    derived.write_text(
        "asset\tfiles\tbytes_or_NA\tlocal_relative_path\tidentity_receipt\tpublic_repository_copy\n"
        f"GJOKA_extracted_members\t94\t{intake['local_uncompressed_bytes']}\t1_data/study_inputs/PBC_GJOKA/R7B1B_v2\t{intake['receipt_sha256']}\tNO\n"
        f"OneK_dualmodel_QTL_summaries\t1284\tNA\t3_results/03_qtl/R7B1B_v2/dualmodel_qtl\t{inputs['outputs']['qtl_receipts_sha256']}\tNO\n"
        f"OneK_sourceLD_binary_matrices\t572\t2061405128\t3_results/04_integration/R7B1B_v2/sourceLD_blocks\t{inputs['outputs']['block_receipts_sha256']}\tNO\n"
        "comparison_checkpoints\t642\tNA\t3_results/04_integration/R7B1B_v2/multisignal\tresults/r7b1b_v2/orchestrator_state.json\tNO\n",
        encoding="utf-8",
    )

    readme = REPO / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "## R7B1B v2 high-information multi-signal reclassification"
    section = f"""{marker}

R7B1B v2 preserves the original 184 screen-positive/ambiguous comparisons as the primary verification cohort and adds a pre-result-frozen symmetric layer of 455 H3 comparisons plus three borderline high-information calibration cases. All 642 comparisons were run with GJOKA study-matched disease LD and current-release OneK1K PF10/PF50 cell-specific LD; 2,568 SuSiE fits completed with no QC failures.

The PF10 adjudication retained 78 stable H4 and 409 stable H3 comparisons. Eight ABF H3 comparisons were reclassified to stable H4, while four ABF H4 comparisons were reclassified to stable H3. FCRL3 × CD8_ET reproduces the key H4-to-H3 counterexample; IL12RB2 × NK and the FCRL3 B-cell comparisons remain stable shared-signal exemplars. Independent mechanical QA passes 19/19 checks.

The evidence ceiling is **PBC-wide ABF screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset**. It is not a multi-signal analysis of every one of the 6,923 screened comparisons. The next frozen stage is simulation/calibration under known truth; manuscript rewriting remains on hold.

![R7B1B v2 bidirectional reclassification](figures/R7B1B_v2/Figure_R7B1B_1_bidirectional_reclassification.png)
"""
    if marker in text:
        start = text.index(marker)
        next_heading = text.find("\n## ", start + len(marker))
        text = text[:start] + section.rstrip() + "\n" + (text[next_heading:] if next_heading != -1 else "")
    else:
        insert = text.find("\n## Repository layout")
        if insert == -1:
            text = text.rstrip() + "\n\n" + section
        else:
            text = text[:insert] + "\n\n" + section.rstrip() + "\n" + text[insert:]
    text = text.replace(
        "These 184 screen triggers are not treated as biological positives. They define the exact R7B1B source-matched multi-signal workload: 25 disease loci, 49 genes, 14 cells and 120 unique cell–locus LD blocks. All 184 must be adjudicated as stable, weakened, reversed, uninformative or QC-failed before the PBC-wide benchmark is interpreted.",
        "The original 184 screen triggers remain a nested primary verification cohort. R7B1B v2 expands the pre-result-frozen multi-signal workload to 642 high-information comparisons so H4-to-H3 and H3-to-H4 reclassification can be measured symmetrically."
    )
    text = text.replace(
        "analysis/r7b1/     PBC-wide eligibility, harmonization, PF10 ABF screen and R7B1B intake",
        "analysis/r7b1/     PBC-wide eligibility, harmonization and PF10 ABF screen\nanalysis/r7b1b_v2/ R7B1B v2 source-LD, SuSiE, adjudication, QA and release"
    )
    text = text.replace(
        "results/r7b1a/     6,923-test ABF registry, exact 184-trigger set and independent QA",
        "results/r7b1a/     6,923-test ABF registry, exact 184-trigger set and independent QA\nresults/r7b1b_v2/  642-comparison bidirectional reclassification and 19-check QA"
    )
    readme.write_text(text, encoding="utf-8")

    # Reject large accidental copies and obvious credential material before staging.
    new_root_files = [p for p in REPO.rglob("*") if p.is_file() and ".git" not in p.parts]
    too_large = [str(p.relative_to(REPO)) for p in new_root_files if p.stat().st_size > 10 * 1024 * 1024]
    if too_large:
        raise RuntimeError(f"files over 10 MiB: {too_large}")
    secret_re = re.compile(r"(?i)(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
    secret_hits = []
    for path in new_root_files:
        if path.suffix.lower() in {".png", ".pdf", ".zip", ".gz", ".xlsx", ".docx", ".pyc"}:
            continue
        try: content = path.read_text(encoding="utf-8")
        except Exception: continue
        if secret_re.search(content): secret_hits.append(str(path.relative_to(REPO)))
    if secret_hits:
        raise RuntimeError(f"secret-pattern hits: {secret_hits}")

    manifest = REPO / "MANIFEST.sha256"
    manifest_lines = []
    for path in sorted(p for p in REPO.rglob("*") if p.is_file() and ".git" not in p.parts and p != manifest):
        manifest_lines.append(f"{sha256(path)}  {path.relative_to(REPO).as_posix()}")
    manifest.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    run("git", "add", "analysis/r7b1b_v2", "protocols", "reports/R7B1B_v2", "results/r7b1b_v2", "figures/R7B1B_v2", "data/R7B1B_v2_LARGE_DERIVED_ASSETS.tsv", "README.md", "MANIFEST.sha256")
    run("git", "diff", "--cached", "--check")
    changed = run("git", "diff", "--cached", "--name-only").splitlines()
    if not changed:
        print(json.dumps({"status": "NO_CHANGES", "head": head}, indent=2))
        return
    run("git", "commit", "-m", "Complete R7B1B v2 bidirectional multi-signal benchmark")
    print(json.dumps(finish_push(head, len(changed)), indent=2))


if __name__ == "__main__":
    main()
