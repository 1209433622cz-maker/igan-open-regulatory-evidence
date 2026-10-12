#!/usr/bin/env python3
"""Build a minimal, checksum-bound npj Genomic Medicine submission bundle."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
SRC = ROOT / "5_manuscript" / "R7C2_Q1_JournalRealityCheck_DualTrackSubmission"
OUT = ROOT / "5_manuscript" / "R7C3_npj_FinalSubmissionPackage_2026-10-11"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

copies = [
    ("01_Cover_Letter.docx", "cover_letter/R7C2_npj_Genomic_Medicine_cover_letter.docx", "Cover letter", "UPLOAD"),
    ("01_Cover_Letter_WPS_Review.pdf", "cover_letter/R7C2_npj_Genomic_Medicine_cover_letter_WPS.pdf", "Cover letter review copy", "REVIEW_ONLY"),
    ("02_Main_Manuscript.docx", "manuscript/R7C2_npj_Genomic_Medicine_manuscript.docx", "Main manuscript", "UPLOAD"),
    ("02_Main_Manuscript_WPS_Review.pdf", "manuscript/R7C2_npj_Genomic_Medicine_manuscript_WPS.pdf", "Main manuscript review copy", "REVIEW_ONLY"),
    ("03_Figure_1.pdf", "figures/Figure1_study_scope_and_model_integrity.pdf", "Figure 1", "UPLOAD"),
    ("04_Figure_2.pdf", "figures/Figure2_input_matched_reclassification.pdf", "Figure 2", "UPLOAD"),
    ("05_Figure_3.pdf", "figures/Figure3_simulation_discovery_and_inference.pdf", "Figure 3", "UPLOAD"),
    ("06_Figure_4.pdf", "figures/Figure4_IL12RB2_external_evidence.pdf", "Figure 4", "UPLOAD"),
    ("07_Figure_5.pdf", "figures/Figure5_FCRL3_support_and_counterexample.pdf", "Figure 5", "UPLOAD"),
    ("08_Figure_6.pdf", "figures/Figure6_liver_tissue_boundary.pdf", "Figure 6", "UPLOAD"),
    ("09_Supplementary_Information.pdf", "supplement/R7C2_npj_Supplementary_Information.pdf", "Supplementary information", "UPLOAD"),
    ("09_Supplementary_Information_Source.docx", "supplement/R7C2_npj_Supplementary_Information.docx", "Editable supplementary source", "REVIEW_ONLY"),
    ("10_Supplementary_Data_1_Tables_S1-S10.xlsx", "supplement/Supplementary_Data_1_Tables_S1-S10.xlsx", "Supplementary Data 1", "UPLOAD"),
    ("11_Source_Data_1_Primary_Machine_Readable_Data.zip", "supplement/Source_Data_1_Primary_Machine_Readable_Data.zip", "Source Data 1", "UPLOAD"),
    ("12_Source_Data_2_External_Validation_Data.zip", "supplement/Source_Data_2_External_Validation_Data.zip", "Source Data 2", "UPLOAD"),
]

rows = []
for out_name, src_rel, label, action in copies:
    src = SRC / src_rel
    if not src.is_file(): raise FileNotFoundError(src)
    dst = OUT / out_name
    shutil.copy2(src, dst)
    s1, s2 = sha256(src), sha256(dst)
    if s1 != s2: raise RuntimeError(f"copy mismatch: {out_name}")
    rows.append({"order": out_name.split("_", 1)[0], "submission_item": label, "file": out_name, "action": action, "bytes": dst.stat().st_size, "sha256": s2, "copy_identity": "PASS"})

metadata = """# Submission metadata and declarations

- Target: npj Genomic Medicine
- Article type: Article
- Title: Input matched multisignal colocalization clarifies regulatory assignments at primary biliary cholangitis loci
- First author: Zhi Chen; zhichen1@link.cuhk.edu.cn; ORCID 0009-0001-0072-5576
- Corresponding author: Teng Qi; tengqi@link.cuhk.edu.cn; ORCID 0009-0007-7648-4776
- Affiliation: School of Medicine, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Boulevard, Longgang District, Shenzhen, Guangdong 518172, China
- Funding: none
- Competing interests: none
- Acknowledgements: none
- Ethics: not required for secondary analysis of public, de-identified data; source-study approvals are cited
- Originality: original work; not under review elsewhere
- Public version: disclose the author-approved GitHub open research release
- Generative AI: disclose author-supervised OpenAI Codex use as stated in manuscript and cover letter
- Code/content licences: MIT for original code; CC BY 4.0 for original text, figures, documentation and derived outputs
- Zenodo DOI: not yet minted; do not enter a DOI until an authenticated Zenodo deposit exists
"""
(OUT / "00_Submission_Metadata_and_Declarations.md").write_text(metadata, encoding="utf-8")

readme = """# R7C3 npj Genomic Medicine final submission package

Upload files marked `UPLOAD` in `00_Upload_Checklist.tsv` in numeric order. Files marked `REVIEW_ONLY` are WPS-rendered or editable review copies and are not additional manuscript files unless the submission system asks for them.

The scientific content is byte-identical to the R7C2 package that passed 68/68 machine/hostile QA checks. WPS Writer review covered 31 manuscript pages, one cover-letter page and two supplementary-guide pages; clipping, overlap and missing figures were zero. Verify the submission-system-generated PDF before clicking Submit.

Submission must be completed in an author account. Save the manuscript ID, generated proof, timestamp and confirmation email as the R7C4 receipt.
"""
(OUT / "00_README_FIRST.md").write_text(readme, encoding="utf-8")

with (OUT / "00_Upload_Checklist.tsv").open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)

shutil.copy2(SRC / "qa" / "R7C2_WPS_visual_receipt.json", OUT / "00_WPS_Visual_Receipt.json")
shutil.copy2(SRC / "qa" / "R7C2_machine_hostile_QA.json", OUT / "00_Machine_Hostile_QA.json")

files_for_manifest = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "checksums.sha256")
with (OUT / "checksums.sha256").open("w", encoding="utf-8", newline="\n") as f:
    for p in files_for_manifest: f.write(f"{sha256(p)}  {p.name}\n")

state = {
    "stage": "R7C3_NPJ_FINAL_SUBMISSION_PACKAGE",
    "built": datetime.now().astimezone().isoformat(),
    "source": str(SRC),
    "output": str(OUT),
    "items": len(copies),
    "upload_items": sum(r["action"] == "UPLOAD" for r in rows),
    "review_only_items": sum(r["action"] == "REVIEW_ONLY" for r in rows),
    "copy_identity_pass": sum(r["copy_identity"] == "PASS" for r in rows),
    "wps_pages_reviewed": 34,
    "scientific_changes": 0,
    "status": "READY_AUTHOR_OPERATED_SUBMISSION",
}
(OUT / "00_Submission_Package_State.json").write_text(json.dumps(state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(state, ensure_ascii=False, indent=2))
