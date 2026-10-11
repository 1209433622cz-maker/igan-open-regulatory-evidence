#!/usr/bin/env python3
"""Copy public-safe R7C1 assets into the local GitHub worktree and rebuild its manifest."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_manuscript/R7C1_IL12RB2_ExternalValidation_ManuscriptFork"
REPO = ROOT / "github/igan-open-regulatory-evidence"
R7C0 = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011/results"


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def replace_line(text: str, prefix: str, new_line: str) -> str:
    lines = text.splitlines()
    changed = False
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = new_line
            changed = True
            break
    if not changed:
        raise RuntimeError(f"metadata line not found: {prefix}")
    return "\n".join(lines) + "\n"


def main() -> None:
    if not (REPO / ".git").exists():
        raise RuntimeError(f"Not a Git worktree: {REPO}")

    for path in sorted((WORK / "code").glob("*")):
        if path.is_file():
            copy_file(path, REPO / "analysis/r7c1" / path.name)

    for path in sorted((WORK / "reports").glob("*.md")):
        copy_file(path, REPO / "reports/R7C1" / path.name)
    for path in sorted((WORK / "protocols").glob("*.md")):
        copy_file(path, REPO / "protocols/R7C1" / path.name)
    for path in sorted((WORK / "results").glob("*")):
        if path.is_file():
            copy_file(path, REPO / "results/R7C1" / path.name)
    for path in (WORK / "qa/R7C1_machine_hostile_QA.json", WORK / "qa/R7C1_machine_hostile_QA.tsv"):
        copy_file(path, REPO / "results/R7C1/qa" / path.name)

    data_out = REPO / "results/R7C1/external_evidence"
    data_out.mkdir(parents=True, exist_ok=True)
    for path in sorted(R7C0.glob("R7C0_*")):
        if path.is_file():
            copy_file(path, data_out / path.name)

    for path in sorted((WORK / "figures").glob("Figure4_IL12RB2_external_evidence.*")):
        copy_file(path, REPO / "figures/R7C1" / path.name)
    for path in sorted((WORK / "manuscript").glob("R7C1_HumanGenomics_IL12RB2_external_validation_fork*")):
        copy_file(path, REPO / "manuscript/r7c1" / path.name)
    copy_file(
        WORK / "supplement/Additional_file_3_R7C1_External_Validation_Data.zip",
        REPO / "manuscript/r7c1/supplement/Additional_file_3_R7C1_External_Validation_Data.zip",
    )

    readme = REPO / "README.md"
    marker = "## R7C1 IL12RB2 external-validation manuscript fork"
    block = f"""

{marker}

R7C1 preserves the byte-identical R7B4B2 Human Genomics baseline and adds a
separate, bounded manuscript fork for IL12RB2-NK. FinnGen R13 × OneK used 1,175
harmonized variants and supported H4 across the frozen prior series (PP.H4
0.9772, 0.9977 and 0.9998 at p12 10^-6, 10^-5 and 10^-4); both OneK QTL
credible-set members occur in the FinnGen R13 disease credible set. FinnGen is
treated as a different disease study system because person-level zero overlap
with the discovery GWAS cannot be demonstrated from public metadata.

The prespecified linked peak now has direct PBC-eQTL and PBC-caQTL sharing
records in l1.NK plus a promoter-proximal peak-IL12RB2 link. This supersedes the
historical R7B1D statement that PBC-caQTL sharing had not been established for
the peak. The result is reported as triangular signal coherence: the direct
eQTL-caQTL posterior and a mediation estimate remain unavailable. OMIX001122
contains one PBC and one control processed matrix and is descriptive only.

The R7C1 manuscript DOCX was exported to a 32-page PDF using WPS Writer, and
32/32 pages passed visual inspection. Machine and hostile-claim QA passed 38/38.
No gene, locus or cell type was added, and the 642-comparison analysis was not
rerun. The next stage is a Q1 journal-fit reality check; if that fit fails, the
R7B4B2 Human Genomics baseline remains the submission route.

![R7C1 external validation and chromatin triangle](figures/R7C1/Figure4_IL12RB2_external_evidence.png)
"""
    current = readme.read_text(encoding="utf-8")
    if marker not in current:
        readme.write_text(current.rstrip() + block + "\n", encoding="utf-8")

    availability = REPO / "DATA_AVAILABILITY.md"
    availability_marker = "## R7C1 external-validation derived data"
    availability_block = f"""

{availability_marker}

R7C1 adds only compact derived FinnGen R12/R13 disease-CS, FinnGen R13 × OneK,
source-CS, fixed CASCADE, chromatin-triangle and OMIX descriptive-QC tables under
`results/R7C1/external_evidence/`, plus a self-checking Additional file 3 under
`manuscript/r7c1/supplement/`. Raw FinnGen summary statistics, CASCADE response
objects, OMIX source archives, OneK genotypes/pseudobulk and other third-party
source bytes remain at their original providers and are not redistributed.
"""
    current = availability.read_text(encoding="utf-8")
    if availability_marker not in current:
        availability.write_text(current.rstrip() + availability_block + "\n", encoding="utf-8")

    cff = REPO / "CITATION.cff"
    cff_text = cff.read_text(encoding="utf-8")
    cff_text = replace_line(cff_text, "version:", "version: 1.1.0")
    cff_text = replace_line(cff_text, "date-released:", "date-released: 2026-10-11")
    cff.write_text(cff_text, encoding="utf-8")

    zenodo = REPO / ".zenodo.json"
    metadata = json.loads(zenodo.read_text(encoding="utf-8"))
    metadata["publication_date"] = "2026-10-11"
    metadata["version"] = "1.1.0"
    metadata["description"] = (
        "Preprint and open research compendium for PBC-wide screening followed by source-matched multi-signal "
        "reclassification of a prespecified high-information H3/H4 subset. R7C1 adds a bounded IL12RB2-NK "
        "validation module using a different FinnGen disease study system, source credible sets and a "
        "disease-eQTL/disease-caQTL/peak-gene chromatin triangle. The release distinguishes statistical signal "
        "sharing from participant-level independence, direct eQTL-caQTL colocalization and causal mediation."
    )
    zenodo.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest = REPO / "MANIFEST.sha256"
    files = [
        path for path in REPO.rglob("*")
        if path.is_file() and ".git" not in path.parts and path != manifest
    ]
    manifest.write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(REPO).as_posix()}" for path in sorted(files)) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "repo": str(REPO),
        "r7c1_code": len(list((REPO / "analysis/r7c1").glob("*"))),
        "r7c1_reports": len(list((REPO / "reports/R7C1").glob("*.md"))),
        "r7c1_external_files": len(list(data_out.glob("*"))),
        "manifest_rows": len(files),
    }, indent=2))


if __name__ == "__main__":
    main()
