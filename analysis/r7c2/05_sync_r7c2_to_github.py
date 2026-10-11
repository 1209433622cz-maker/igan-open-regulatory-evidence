#!/usr/bin/env python3
"""Copy public R7C2 assets to the GitHub worktree and rebuild release metadata."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_manuscript/R7C2_Q1_JournalRealityCheck_DualTrackSubmission"
REPO = ROOT / "github/igan-open-regulatory-evidence"


def copy_file(source: Path, target: Path):
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
    for i, line in enumerate(lines):
        if line.startswith(prefix):
            lines[i] = new_line
            return "\n".join(lines) + "\n"
    raise RuntimeError(f"metadata line missing: {prefix}")


def main():
    if not (REPO / ".git").exists():
        raise RuntimeError(f"not a git worktree: {REPO}")

    for path in sorted((WORK / "code").glob("*.py")):
        copy_file(path, REPO / "analysis/r7c2" / path.name)
    for path in sorted((WORK / "reports").glob("*.md")):
        copy_file(path, REPO / "reports/R7C2" / path.name)
    for path in sorted((WORK / "protocols").glob("*")):
        if path.is_file():
            copy_file(path, REPO / "protocols/R7C2" / path.name)
    for path in sorted((WORK / "results").glob("*")):
        if path.is_file():
            copy_file(path, REPO / "results/R7C2" / path.name)
    for path in (
        WORK / "qa/R7C2_machine_hostile_QA.json",
        WORK / "qa/R7C2_machine_hostile_QA.tsv",
        WORK / "qa/R7C2_WPS_visual_receipt.json",
    ):
        copy_file(path, REPO / "results/R7C2/qa" / path.name)

    for path in sorted((WORK / "manuscript").glob("*")):
        if path.is_file():
            copy_file(path, REPO / "manuscript/r7c2" / path.name)
    for path in sorted((WORK / "cover_letter").glob("*")):
        if path.is_file():
            copy_file(path, REPO / "manuscript/r7c2/cover_letter" / path.name)
    for path in sorted((WORK / "supplement").glob("*")):
        if path.is_file():
            copy_file(path, REPO / "manuscript/r7c2/supplement" / path.name)
    for path in sorted((WORK / "figures").glob("*")):
        if path.is_file():
            copy_file(path, REPO / "figures/R7C2" / path.name)

    readme = REPO / "README.md"
    marker = "## R7C2 Q1 journal reality check and dual-track package"
    block = f"""

{marker}

R7C2 completed a current official-guideline audit of npj Genomic Medicine,
Communications Biology, Genome Medicine and Human Genomics without reopening any
disease, locus, gene, cell or omics layer. The only supported Q1-target attempt is
`npj Genomic Medicine / Article`, because its scope directly includes integrative
disease genomics, immunogenomics and computational analysis of genomic variation.
The decision remains conditional: current evidence does not establish a broadly
superior algorithm, direct eQTL-caQTL sharing, chromatin mediation, functional
mechanism or clinical utility.

The npj candidate uses a 12-word punctuation-free title and a 137-word
unstructured abstract. The separate Conclusions section was integrated into the
Discussion, and Nature Portfolio data, code, authorship, funding and competing-
interest statements were added. WPS Writer exported a 31-page manuscript, a
one-page cover letter and a two-page supplementary guide; all 34 pages passed
visual review. Machine and hostile QA passed 68/68 checks.

The author-approved Human Genomics package remains frozen and submission-ready.
If npj Genomic Medicine declines the paper editorially, the project will move
directly to that baseline rather than add unbounded rescue analyses. The next
stage is `R7C3_AUTHOR_FINAL_REVIEW_AND_NPJ_SUBMISSION_GATE`; journal submission
must be completed by an author.

![R7C2 external validation figure](figures/R7C2/Figure4_IL12RB2_external_evidence.png)
"""
    current = readme.read_text(encoding="utf-8")
    if marker not in current:
        readme.write_text(current.rstrip() + block + "\n", encoding="utf-8")

    availability = REPO / "DATA_AVAILABILITY.md"
    availability_marker = "## R7C2 journal package and source data"
    availability_block = f"""

{availability_marker}

R7C2 republishes no new third-party source bytes. The public package includes the
npj-formatted manuscript, six figures, the editable S1-S10 workbook, compact
machine-readable derived tables and the R7C1 external-validation derived-data
archive. Individual-level genotypes, BAM files, pseudobulk matrices and provider-
licensed archives remain excluded. Official journal-rule snapshots are recorded
as URLs and dated audit statements rather than mirrored web content.
"""
    current = availability.read_text(encoding="utf-8")
    if availability_marker not in current:
        availability.write_text(current.rstrip() + availability_block + "\n", encoding="utf-8")

    cff = REPO / "CITATION.cff"
    cff_text = cff.read_text(encoding="utf-8")
    cff_text = replace_line(cff_text, "title:", 'title: "Input matched multisignal colocalization clarifies regulatory assignments at primary biliary cholangitis loci"')
    cff_text = replace_line(cff_text, "version:", "version: 1.2.0")
    cff_text = replace_line(cff_text, "date-released:", "date-released: 2026-10-11")
    cff.write_text(cff_text, encoding="utf-8")

    zenodo = REPO / ".zenodo.json"
    metadata = json.loads(zenodo.read_text(encoding="utf-8"))
    metadata["title"] = "Input matched multisignal colocalization clarifies regulatory assignments at primary biliary cholangitis loci"
    metadata["publication_date"] = "2026-10-11"
    metadata["version"] = "1.2.0"
    metadata["description"] = (
        "Open research compendium and npj Genomic Medicine submission candidate for PBC-wide screening followed "
        "by source-matched multi-signal reclassification of a prespecified high-information subset. The release "
        "separates variant-support and disease-statistic effects from residual reclassification, reports discovery "
        "and pair-conditional simulation channels, and adds bounded IL12RB2-NK evidence from a different FinnGen "
        "disease study system and a disease-eQTL/disease-caQTL/peak-gene chromatin triangle. It does not claim "
        "participant-level independence, direct eQTL-caQTL colocalization, causal mediation or general method superiority."
    )
    zenodo.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest = REPO / "MANIFEST.sha256"
    files = [p for p in REPO.rglob("*") if p.is_file() and ".git" not in p.parts and p != manifest]
    manifest.write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(REPO).as_posix()}" for path in sorted(files)) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "repo": str(REPO),
        "analysis_files": len(list((REPO / "analysis/r7c2").glob("*"))),
        "report_files": len(list((REPO / "reports/R7C2").glob("*"))),
        "manuscript_files": len(list((REPO / "manuscript/r7c2").rglob("*"))),
        "figure_files": len(list((REPO / "figures/R7C2").glob("*"))),
        "manifest_rows": len(files),
    }, indent=2))


if __name__ == "__main__":
    main()
