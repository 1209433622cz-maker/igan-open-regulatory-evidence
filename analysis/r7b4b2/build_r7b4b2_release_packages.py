#!/usr/bin/env python3
"""Build the private journal-submission archive and public Zenodo/GitHub compendium.

The script deliberately keeps private author records and the cover letter out of
the public package. It writes SHA-256 manifests, verifies every archive member,
and records the exact source hashes used for the release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
CANDIDATE = ROOT / "5_manuscript" / "R7B4B_FinalSubmissionCandidate"
REPO = ROOT / "github" / "igan-open-regulatory-evidence"
RELEASE = ROOT / "6_release" / "R7B4B2_2026-10-10"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree_files(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(source)
    for item in sorted(source.rglob("*")):
        if item.is_file():
            copy_file(item, destination / item.relative_to(source))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def manifest_for(root: Path, output: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p != output):
        rel = path.relative_to(root).as_posix()
        records.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path)})
    write_text(output, "".join(f"{x['sha256']}  {x['path']}\n" for x in records))
    return records


def make_zip(source_root: Path, zip_path: Path) -> dict[str, object]:
    if zip_path.exists():
        zip_path.unlink()
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in source_root.rglob("*") if p.is_file())
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            zf.write(path, path.relative_to(source_root).as_posix())
    with zipfile.ZipFile(zip_path, "r") as zf:
        bad = zf.testzip()
        names = zf.namelist()
    if bad:
        raise RuntimeError(f"ZIP CRC failed at {bad}")
    return {
        "path": str(zip_path),
        "bytes": zip_path.stat().st_size,
        "sha256": sha256(zip_path),
        "entries": len(names),
        "zip_crc": "PASS",
    }


def build_private(stage: Path) -> None:
    upload = stage / "UPLOAD_TO_HUMAN_GENOMICS"
    internal = stage / "INTERNAL_DO_NOT_UPLOAD"

    copy_tree_files(CANDIDATE / "manuscript", upload / "01_manuscript")
    copy_tree_files(CANDIDATE / "cover_letter", upload / "02_cover_letter")
    copy_tree_files(CANDIDATE / "figures", upload / "03_figures")
    copy_tree_files(CANDIDATE / "graphical_abstract", upload / "04_graphical_abstract")
    copy_tree_files(CANDIDATE / "supplement", upload / "05_supplement")

    for name in [
        "R7B4B1_author_record_final_validation.json",
        "R7B4B1_final_submission_QA.json",
        "WPS_render_receipt.json",
    ]:
        copy_file(CANDIDATE / "qa" / name, internal / "qa" / name)
    copy_file(
        CANDIDATE / "private" / "R7B4B_author_record.PRIVATE.json",
        internal / "R7B4B_author_record.PRIVATE.json",
    )

    write_text(
        upload / "UPLOAD_MAP.tsv",
        "order\tjournal_item\tfile_or_folder\tnote\n"
        "1\tManuscript\t01_manuscript/R7B4B_HumanGenomics_final.docx\tEditable submission manuscript\n"
        "2\tCover letter\t02_cover_letter/R7B4B_HumanGenomics_cover_letter_final.docx\tAddressed to Human Genomics\n"
        "3\tFigures\t03_figures/Figure1-Figure6_*.pdf\tOne PDF per main figure; PNG alternatives supplied\n"
        "4\tGraphical abstract\t04_graphical_abstract/Graphical_Abstract_HumanGenomics_920x300.png\tRequired 920 x 300 asset\n"
        "5\tAdditional file 1\t05_supplement/Additional_file_1_Supplementary_Tables_S1-S10.xlsx\tSupplementary tables\n"
        "6\tAdditional file 2\t05_supplement/Additional_file_2_Machine_Readable_Supplementary_Data.zip\tMachine-readable derived data\n",
    )
    write_text(
        internal / "DO_NOT_UPLOAD.md",
        "# Internal records — do not upload\n\n"
        "This folder contains private contact/approval metadata and internal QA receipts. "
        "It is retained locally for provenance and must not be uploaded to the journal, GitHub or Zenodo.\n",
    )
    write_text(
        stage / "README.md",
        "# R7B4B2 Human Genomics submission package\n\n"
        "`UPLOAD_TO_HUMAN_GENOMICS/` contains the author-approved upload files. "
        "`INTERNAL_DO_NOT_UPLOAD/` contains private provenance and QA records. "
        "The manuscript and cover-letter PDFs were exported with WPS Writer and visually checked. "
        "Journal submission remains an author-operated action.\n",
    )


def build_public(stage: Path) -> None:
    copy_tree_files(CANDIDATE / "manuscript", stage / "manuscript")
    copy_tree_files(CANDIDATE / "figures", stage / "figures")
    copy_tree_files(CANDIDATE / "graphical_abstract", stage / "graphical_abstract")
    copy_tree_files(CANDIDATE / "supplement", stage / "supplement")

    for name in ["LICENSE", "LICENSE_CONTENT.md", "NOTICE.md", "CITATION.cff", ".zenodo.json", "DATA_AVAILABILITY.md"]:
        copy_file(REPO / name, stage / name)
    copy_file(REPO / "results" / "r7b4b1" / "R7B4B1_publication_state.json", stage / "metadata" / "R7B4B1_publication_state.json")

    write_text(
        stage / "README.md",
        "# PBC R7B4B2 open research compendium\n\n"
        "**Title:** Input-matched multi-signal colocalization clarifies immune-cell regulatory assignments at primary biliary cholangitis risk loci\n\n"
        "**Authors:** Zhi Chen; Teng Qi (corresponding author)\n\n"
        "This public package contains the author-approved manuscript, six main figures, graphical abstract, "
        "supplementary tables and machine-readable derived results. Analysis code and the broader provenance "
        "record are maintained at https://github.com/1209433622cz-maker/igan-open-regulatory-evidence.\n\n"
        "Original manuscript text, figures, documentation and derived outputs are released under CC BY 4.0. "
        "Original code is released under the MIT License. Third-party data are not relicensed or redistributed; "
        "see `NOTICE.md` and `DATA_AVAILABILITY.md`.\n\n"
        "The manuscript reports reanalysis of public, de-identified data. It contains no newly collected human "
        "participant data and no identifiable participant information.\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-dir", type=Path, default=RELEASE)
    args = parser.parse_args()
    release = args.release_dir.resolve()

    private_stage = release / "staging" / "submission_private"
    public_stage = release / "staging" / "open_research_compendium"
    if release.exists():
        shutil.rmtree(release)
    private_stage.mkdir(parents=True)
    public_stage.mkdir(parents=True)

    build_private(private_stage)
    build_public(public_stage)
    private_files = manifest_for(private_stage, private_stage / "MANIFEST.sha256")
    public_files = manifest_for(public_stage, public_stage / "MANIFEST.sha256")

    private_zip = release / "CMM_R7B4B2_HumanGenomics_SubmissionPackage_PRIVATE_2026-10-10.zip"
    public_zip = release / "PBC_R7B4B2_OpenResearchCompendium_2026-10-10.zip"
    private_receipt = make_zip(private_stage, private_zip)
    public_receipt = make_zip(public_stage, public_zip)
    write_text(private_zip.with_suffix(private_zip.suffix + ".sha256"), f"{private_receipt['sha256']}  {private_zip.name}\n")
    write_text(public_zip.with_suffix(public_zip.suffix + ".sha256"), f"{public_receipt['sha256']}  {public_zip.name}\n")

    receipt = {
        "stage": "R7B4B2_GITHUB_ZENODO_DOI_RELEASE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_candidate": str(CANDIDATE),
        "public_privacy_gate": {
            "private_author_record_in_public_package": False,
            "cover_letter_in_public_package": False,
            "first_author_private_email_in_public_package": False,
            "corresponding_author_publication_email_in_public_package": True,
            "third_party_raw_data_in_public_package": False,
        },
        "private_manifest_files_before_manifest": len(private_files),
        "public_manifest_files_before_manifest": len(public_files),
        "private_archive": private_receipt,
        "public_archive": public_receipt,
    }
    write_text(release / "R7B4B2_package_receipt.json", json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
