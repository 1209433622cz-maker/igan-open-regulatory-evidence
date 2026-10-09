#!/usr/bin/env python3
"""Build and verify the R7B1E diagnostic-closure/evidence-freeze release."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
RELEASE = ROOT / "6_release/R7B1E"
STAGE = RELEASE / "stage"
ZIP_PATH = RELEASE / "CMM_R7B1E_DiagnosticClosure_ClaimEvidenceFreeze_2026-10-09.zip"
DOWNLOADS = Path(r"C:\Users\Administrator\Downloads")
REPO = ROOT / "github/igan-open-regulatory-evidence"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_tree(source: Path, relative: str | Path) -> None:
    destination = STAGE / relative
    shutil.copytree(source, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def copy_file(source: Path, relative: str | Path) -> None:
    destination = STAGE / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


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


def git_text(*args: str) -> str:
    proc = subprocess.run(args, cwd=REPO, capture_output=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    return proc.stdout.decode("utf-8", "replace").strip()


def main() -> None:
    qa0_path = ROOT / "3_results/00_audit/R7B1E0/R7B1E0_independent_QA.json"
    qae_path = ROOT / "3_results/00_audit/R7B1E/R7B1E_independent_QA.json"
    sync_path = ROOT / "3_results/00_audit/R7B1E/R7B1E_github_sync_receipt.json"
    qa0 = json.loads(qa0_path.read_text(encoding="utf-8"))
    qae = json.loads(qae_path.read_text(encoding="utf-8"))
    sync = json.loads(sync_path.read_text(encoding="utf-8"))
    if qa0.get("status") != "PASS" or qa0.get("passed") != qa0.get("total"):
        raise RuntimeError("R7B1E0 QA is not fully PASS")
    if qae.get("status") != "PASS" or qae.get("passed") != qae.get("total"):
        raise RuntimeError("R7B1E QA is not fully PASS")
    if sync.get("status") not in {"PASS", "NO_CHANGES"}:
        raise RuntimeError("GitHub sync is not verified")

    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    copy_tree(ROOT / "2_code/06_intake/r7b1e0", "code/r7b1e0")
    copy_tree(ROOT / "2_code/06_intake/r7b1e", "code/r7b1e")
    copy_tree(ROOT / "0_admin/protocols/R7B1E0", "protocols/R7B1E0")
    copy_tree(ROOT / "0_admin/protocols/R7B1E", "protocols/R7B1E")
    copy_tree(ROOT / "3_results/04_integration/R7B1E0/diagnostic_adjudication", "results/R7B1E0/diagnostic_adjudication")
    copy_tree(ROOT / "3_results/04_integration/R7B1E0/signal_semantics", "results/R7B1E0/signal_semantics")
    copy_file(ROOT / "3_results/04_integration/R7B1E0/kriging_replay/orchestrator_state.json", "results/R7B1E0/kriging_replay/orchestrator_state.json")
    copy_file(ROOT / "3_results/04_integration/R7B1E0/kriging_replay/orchestrator_loci.tsv", "results/R7B1E0/kriging_replay/orchestrator_loci.tsv")
    copy_tree(ROOT / "3_results/00_audit/R7B1E0", "audit/R7B1E0")
    copy_tree(ROOT / "3_results/04_integration/R7B1E", "results/R7B1E")
    copy_tree(ROOT / "3_results/00_audit/R7B1E", "audit/R7B1E")
    copy_tree(ROOT / "5_analysis/figures/R7B1E", "figures/R7B1E")
    copy_tree(ROOT / "7.Report/rounds/R7B1E", "reports")
    copy_file(REPO / "data/R7B1E0_LOCAL_REPLAY_MANIFEST.tsv", "data/R7B1E0_LOCAL_REPLAY_MANIFEST.tsv")

    readme = f"""# CMM R7B1E release

This release closes the R7B1E0 diagnostic/semantic audit and the R7B1E integrated claim–evidence and Figure 1–6 source freeze defined by doctoral research plan v2.

```text
R7B1E0_KRIGING_REPLAY = 2568/2568 PASS
R7B1E0_SIGNAL_SEMANTICS = PASS
R7B1E0_INDEPENDENT_QA = {qa0['passed']}/{qa0['total']} PASS
R7B1E_CLAIM_EVIDENCE_FREEZE = PASS
R7B1E_INDEPENDENT_QA = {qae['passed']}/{qae['total']} PASS
HISTORICAL_CLASSIFICATIONS_CHANGED = NO
POSTERIOR_REFIT_REQUIRED = NO
PUBLIC_GITHUB_SYNC = {sync['status']} @ {sync['remote_head']}
NEXT = R7B2_MANUSCRIPT_V1
```

Per-locus replay intermediates and logs remain local and are represented by a path/size/SHA-256 manifest. Aggregate diagnostic outputs, signal semantics, claim ledger, figure source data, code, protocols, reports, figures and independent QA are included.
"""
    (STAGE / "README.md").write_text(readme, encoding="utf-8")

    files = sorted(path for path in STAGE.rglob("*") if path.is_file() and path.name != "checksums.sha256")
    (STAGE / "checksums.sha256").write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(STAGE).as_posix()}" for path in files) + "\n",
        encoding="utf-8",
    )

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
    action = ROOT / "7.Report/rounds/R7B1E/99_CMM_R7B1E_详细行动记录_2026-10-09.md"
    shutil.copy2(action, DOWNLOADS / action.name)
    shutil.copy2(action, ROOT / action.name)

    local_head = git_text("git", "rev-parse", "HEAD")
    remote_head = git_text("git", "ls-remote", "origin", "refs/heads/main").split()[0]
    clean = git_text("git", "status", "--porcelain") == ""
    download_zip = DOWNLOADS / ZIP_PATH.name
    download_hash = sha256(download_zip)
    python_files = list((ROOT / "2_code/06_intake/r7b1e0").glob("*.py")) + list((ROOT / "2_code/06_intake/r7b1e").glob("*.py"))
    report_count = len(list((ROOT / "7.Report/rounds/R7B1E").glob("*.md")))
    verification = {
        "schema": "R7B1E_FINAL_VERIFICATION_1.0",
        "status": "PASS" if all([
            download_hash == digest,
            local_head == remote_head,
            clean,
            report_count == 6,
            qa0["passed"] == qa0["total"] == 21,
            qae["passed"] == qae["total"] == 21,
        ]) else "FAIL",
        "release_sha256": digest,
        "downloads_sha256_match": download_hash == digest,
        "zip_crc": "PASS",
        "zip_entries": entries,
        "internal_checksums_passed": internal_passed,
        "reports": report_count,
        "python_scripts": len(python_files),
        "R7B1E0_QA": f"{qa0['passed']}/{qa0['total']} PASS",
        "R7B1E_QA": f"{qae['passed']}/{qae['total']} PASS",
        "github_local_head": local_head,
        "github_remote_head": remote_head,
        "github_clean": clean,
        "next": "R7B2_MANUSCRIPT_V1",
    }
    if verification["status"] != "PASS":
        raise RuntimeError(json.dumps(verification, ensure_ascii=False, indent=2))
    (RELEASE / "final_verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    state = {
        "schema": "R7B1E_RELEASE_1.0",
        "status": "PASS",
        "zip": str(ZIP_PATH),
        "downloads_copy": str(download_zip),
        "sha256": digest,
        "zip_crc": "PASS",
        "entries": entries,
        "internal_checksums_passed": internal_passed,
        "github_head": remote_head,
        "next": "R7B2_MANUSCRIPT_V1",
    }
    (RELEASE / "release_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"release": state, "verification": verification}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
