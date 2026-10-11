#!/usr/bin/env python3
"""Build and verify the final R7C2 release archive."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_manuscript/R7C2_Q1_JournalRealityCheck_DualTrackSubmission"
RELEASE_DIR = ROOT / "6_release/R7C2_2026-10-11"
STEM = "CMM_R7C2_Q1_JournalRealityCheck_DualTrackSubmission_2026-10-11"
STAGE = RELEASE_DIR / STEM
ZIP_PATH = RELEASE_DIR / f"{STEM}.zip"
SHA_PATH = RELEASE_DIR / f"{STEM}.zip.sha256"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy_selected():
    if STAGE.exists():
        stage_resolved = STAGE.resolve()
        release_resolved = RELEASE_DIR.resolve()
        if not stage_resolved.is_relative_to(release_resolved) or stage_resolved == release_resolved:
            raise RuntimeError(f"unsafe staging path for recursive cleanup: {stage_resolved}")
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True, exist_ok=True)
    include = {
        "manuscript": ["*.md", "*.docx", "*.pdf"],
        "cover_letter": ["*.md", "*.docx", "*.pdf"],
        "figures": ["*.pdf", "*.png", "*.svg", "*.json"],
        "supplement": ["*.md", "*.docx", "*.pdf", "*.xlsx", "*.zip"],
        "reports": ["*.md"],
        "results": ["*.json", "*.tsv"],
        "protocols": ["*.md", "*.json"],
        "code": ["*.py", "*.ps1"],
        "qa": ["*.json", "*.tsv"],
    }
    for directory, patterns in include.items():
        destination = STAGE / directory
        destination.mkdir(parents=True, exist_ok=True)
        for pattern in patterns:
            for source in (WORK / directory).glob(pattern):
                if source.is_file():
                    shutil.copy2(source, destination / source.name)

    repo = ROOT / "github/igan-open-regulatory-evidence"
    receipt = {
        "stage": "R7C2",
        "r7c1_release_zip_sha256": sha256(ROOT / "6_release/R7C1_2026-10-11/CMM_R7C1_IL12RB2_ExternalValidation_ManuscriptFork_2026-10-11.zip"),
        "r7c1_manuscript_docx_sha256": sha256(ROOT / "5_manuscript/R7C1_IL12RB2_ExternalValidation_ManuscriptFork/manuscript/R7C1_HumanGenomics_IL12RB2_external_validation_fork.docx"),
        "human_genomics_fallback_docx_sha256": sha256(ROOT / "5_manuscript/R7B4B_FinalSubmissionCandidate/manuscript/R7B4B_HumanGenomics_final.docx"),
        "github_baseline_commit": "dd25931352fab5238da7ea08d1ce4a9e0e3f2e55",
        "source_workspace": str(WORK),
    }
    (STAGE / "provenance").mkdir(exist_ok=True)
    (STAGE / "provenance/R7C2_baseline_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")


def build():
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    copy_selected()
    files = sorted(p for p in STAGE.rglob("*") if p.is_file())
    manifest_lines = [f"{sha256(path)}  {path.relative_to(STAGE).as_posix()}" for path in files]
    manifest = STAGE / "checksums.sha256"
    manifest.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in STAGE.rglob("*") if p.is_file()):
            zf.write(path, f"{STEM}/{path.relative_to(STAGE).as_posix()}")
    digest = sha256(ZIP_PATH)
    SHA_PATH.write_text(f"{digest}  {ZIP_PATH.name}\n", encoding="utf-8")
    return digest, len(files)


def verify(expected_digest: str):
    if sha256(ZIP_PATH) != expected_digest:
        raise RuntimeError("external ZIP SHA-256 mismatch")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        if zf.testzip() is not None:
            raise RuntimeError("ZIP CRC failure")
        names = zf.namelist()
        manifest_name = f"{STEM}/checksums.sha256"
        lines = zf.read(manifest_name).decode("utf-8").splitlines()
        passed = 0
        for line in lines:
            digest, rel = line.split("  ", 1)
            member = f"{STEM}/{rel}"
            if hashlib.sha256(zf.read(member)).hexdigest() != digest:
                raise RuntimeError(f"internal checksum mismatch: {rel}")
            passed += 1
    qa = json.loads((WORK / "qa/R7C2_machine_hostile_QA.json").read_text(encoding="utf-8"))
    if qa["status"] != "PASS":
        raise RuntimeError("R7C2 machine QA is not PASS")
    state = {
        "stage": "R7C2_Q1_REALITY_CHECK_DUAL_TRACK",
        "release_zip": str(ZIP_PATH),
        "release_zip_sha256": expected_digest,
        "zip_crc": "PASS",
        "internal_checksums": f"{passed}/{passed} PASS",
        "zip_entries": len(names),
        "machine_qa": f"{qa['checks_passed']}/{qa['checks_total']} PASS",
        "wps_visual_qa": qa["visual_review"]["status"],
        "decision": "NPJ_GENOMIC_MEDICINE_CONDITIONAL_GO_ONE_ATTEMPT",
        "fallback": "HUMAN_GENOMICS_FROZEN_SUBMISSION_READY",
        "next": "R7C3_AUTHOR_FINAL_REVIEW_AND_NPJ_SUBMISSION_GATE",
    }
    (RELEASE_DIR / "R7C2_release_state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(state, indent=2, ensure_ascii=False))


def main():
    digest, _ = build()
    verify(digest)


if __name__ == "__main__":
    main()
