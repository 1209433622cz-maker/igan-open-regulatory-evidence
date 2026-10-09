#!/usr/bin/env python3
"""Final machine QA for the R7B4A Human Genomics submission interface."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import pandas as pd
from PIL import Image
from docx import Document
from pypdf import PdfReader


ROOT = Path(r"H:\SCI2\YR1")
BASE = ROOT / "5_manuscript" / "R7B4A_HumanGenomics_SubmissionInterface"
MD = BASE / "manuscript" / "R7B4A_HumanGenomics_manuscript.md"
DOCX = BASE / "manuscript" / "R7B4A_HumanGenomics_manuscript.docx"
PDF = BASE / "manuscript" / "R7B4A_HumanGenomics_manuscript_WPS.pdf"
COVER_MD = BASE / "cover_letter" / "R7B4A_HumanGenomics_cover_letter_DRAFT.md"
COVER_DOCX = BASE / "cover_letter" / "R7B4A_HumanGenomics_cover_letter_DRAFT.docx"
COVER_PDF = BASE / "cover_letter" / "R7B4A_HumanGenomics_cover_letter_DRAFT_WPS.pdf"
FIG = BASE / "figures"
GA = BASE / "graphical_abstract" / "Graphical_Abstract_HumanGenomics_920x300.png"
SUP1 = BASE / "supplement" / "Additional_file_1_Supplementary_Tables_S1-S10.xlsx"
SUP2 = BASE / "supplement" / "Additional_file_2_Machine_Readable_Supplementary_Data.zip"
UPSTREAM_SUP1 = ROOT / "5_manuscript" / "R7B3A_ManuscriptV2" / "supplements" / "R7B3A_Supplementary_Tables_S1-S10.xlsx"
STATE = BASE / "results" / "R7B4A_state.json"
ROUTES = BASE / "results" / "R7B4A_journal_route_matrix.tsv"
GUIDELINES = BASE / "results" / "R7B4A_official_guideline_audit.tsv"
UPLOAD = BASE / "submission" / "R7B4A_HumanGenomics_upload_map.tsv"
AUTHOR_FORM = BASE / "submission" / "R7B4A_author_metadata_completion_form.md"
CHECKLIST = BASE / "submission" / "R7B4A_HumanGenomics_submission_checklist.md"
FIGURE_CODE = ROOT / "2_code" / "11_manuscript" / "R7B4A" / "build_r7b4a_figures.py"
OUT = BASE / "qa"
OUT.mkdir(parents=True, exist_ok=True)

TITLE = "Input-matched multi-signal colocalization clarifies immune-cell regulatory assignments at primary biliary cholangitis risk loci"
TAG = "r7b4a-human-genomics-interface-2026-10-10"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def word_count(value: str) -> int:
    return len(re.findall(r"\b[A-Za-z0-9][A-Za-z0-9'/-]*\b", value))


def main() -> int:
    text = MD.read_text(encoding="utf-8")
    checks: list[dict[str, str]] = []

    def check(name: str, passed: bool, detail) -> None:
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": str(detail)})

    check("exact_title", text.startswith(f"# {TITLE}\n"), text.splitlines()[0])
    check("article_type", "**Article type:** Research" in text, "Research")
    abstract_start = text.index("## Abstract") + len("## Abstract")
    abstract_end = text.index("\n## Background\n", abstract_start)
    abstract = text[abstract_start:abstract_end]
    abstract_words = word_count(abstract)
    abstract_heads = re.findall(r"(?m)^### (.+)$", abstract)
    check("abstract_structure", abstract_heads == ["Background", "Results", "Conclusions"], abstract_heads)
    check("abstract_word_limit", abstract_words <= 350, abstract_words)
    check("abstract_no_citations", not re.search(r"\[\d+(?:[-,]\d+)*\]", abstract), "no numeric citations")
    keyword_match = re.search(r"\*\*Keywords:\*\* (.+)", text)
    keywords = [item.strip() for item in keyword_match.group(1).split(";")] if keyword_match else []
    check("keyword_count", 3 <= len(keywords) <= 10, len(keywords))

    required_sections = ["## Background", "## Methods", "## Results", "## Discussion", "## Conclusions", "## List of abbreviations", "## Declarations", "## References", "## Figure legends", "## Additional files"]
    check("required_sections", all(section in text for section in required_sections), required_sections)
    declarations = ["Ethics approval and consent to participate", "Consent for publication", "Availability of data and materials", "Competing interests", "Funding", "Authors' contributions", "Acknowledgements", "Authors' information"]
    check("declaration_headings", all(f"### {heading}" in text for heading in declarations), declarations)
    check("llm_disclosure", "OpenAI Codex" in text and "QiTeng Academic Writing Skill" in text and "not treated as an author" in text, "supervised use disclosed")
    check("immutable_repository_tag", TAG in text, TAG)

    anchors = ["6,923", "5,460", "642", "79 of 113", "ten of 452", "92 H4-supported", "428 H3-supported", "59 model-sensitive", "63 uninformative", "32 H4-supported", "491 of 520", "486,000", "160,782", "33.08%", "12.41%", "8.56%", "32.99%", "26.66%", "0.9698", "0.9706", "0.9916", "q=0.111"]
    missing = [value for value in anchors if value.lower() not in text.lower()]
    check("numeric_anchor_coverage", not missing, f"missing={missing}")
    prohibited = ["proved that multi-signal", "proves that multi-signal", "universal method superiority", "established a complete causal cascade", "tissue mediation was established", "PBC-specific upregulation", "all 6,923 received multi-signal"]
    found = [phrase for phrase in prohibited if phrase.lower() in text.lower()]
    check("prohibited_claims_absent", not found, found)
    check("replication_language_bounded", "cross-qtl-resource support rather than independent disease replication" in text.lower(), "explicit disease-replication boundary")
    check("screening_scope_bounded", "PBC-wide screening followed by bounded reclassification" in text, "claim ceiling explicit")

    refs = [int(number) for number in re.findall(r"(?m)^(\d+)\. ", text)]
    check("reference_count_and_continuity", refs == list(range(1, 23)), refs)
    legends = re.findall(r"(?m)^\*\*Figure (\d+)\.", text)
    check("figure_legends", legends == ["1", "2", "3", "4", "5", "6"], legends)
    check("figure2_semantic_legend", "60 stable-H4 comparisons had no qualifying H3 pair" in text and "32 contained qualifying shared and distinct pairs" in text, "60/32 wording")
    figure_code = FIGURE_CODE.read_text(encoding="utf-8")
    check("figure2_semantic_label", "Stable H4;\\nno qualifying H3 pair" in figure_code and "Stable H4 / shared only" not in figure_code, "label corrected without count change")
    figure_files = [path for path in FIG.glob("Figure[1-6]_*") if path.suffix.lower() in {".png", ".pdf", ".svg"}]
    check("figure_triplets", len(figure_files) == 18, len(figure_files))
    hashes = json.loads((FIG / "FIGURE_HASHES.json").read_text(encoding="utf-8"))
    check("figure_hash_manifest", len(hashes) == 18 and all(sha256(FIG / name) == digest for name, digest in hashes.items()), len(hashes))

    check("graphical_abstract", GA.exists() and Image.open(GA).size == (920, 300), Image.open(GA).size if GA.exists() else None)
    check("additional_file_1", SUP1.exists() and SUP1.stat().st_size > 100000, SUP1.stat().st_size if SUP1.exists() else 0)
    check("supplement_workbook_identity", SUP1.exists() and UPSTREAM_SUP1.exists() and sha256(SUP1) == sha256(UPSTREAM_SUP1), sha256(SUP1) if SUP1.exists() else "missing")
    zip_names: list[str] = []
    zip_error = None
    if SUP2.exists():
        with zipfile.ZipFile(SUP2) as archive:
            zip_error = archive.testzip()
            zip_names = archive.namelist()
    check("additional_file_2_crc", SUP2.exists() and zip_error is None and len(zip_names) >= 10, f"members={len(zip_names)} bad={zip_error}")
    forbidden = [name for name in zip_names if Path(name).suffix.lower() in {".bed", ".bim", ".fam", ".bam", ".bai", ".cram", ".vcf", ".bcf", ".mtx", ".h5", ".h5ad"}]
    check("no_restricted_raw_files", not forbidden, forbidden)

    guidelines = pd.read_csv(GUIDELINES, sep="\t")
    routes = pd.read_csv(ROUTES, sep="\t")
    upload = pd.read_csv(UPLOAD, sep="\t")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    check("official_guideline_inventory", len(guidelines) >= 12 and (guidelines.source_type == "official journal").all(), len(guidelines))
    check("journal_route_lock", routes.iloc[0].journal == "Human Genomics" and routes.iloc[0].decision == "GO_AFTER_HUMAN_METADATA", routes.iloc[0].to_dict())
    check("quartile_caveat", "INSTITUTIONAL_RECHECK" in state.get("Q2_eligibility", "") and routes.iloc[0].quartile_source_caveat != "", state.get("Q2_eligibility"))
    check("upload_map", len(upload) == 12 and set(upload.status).issuperset({"READY", "HUMAN_CONFIRMATION_PENDING", "TECHNICALLY_READY_HUMAN_FIELDS_PENDING", "READY_AFTER_WPS_EXPORT"}), len(upload))
    check("human_gate_files", AUTHOR_FORM.exists() and CHECKLIST.exists() and "HUMAN_COMPLETION_GATE" in json.dumps(state), state.get("author_metadata"))
    check("next_stage", state.get("next") == "R7B4B_AUTHOR_COMPLETION_AND_FINAL_SUBMISSION_QA", state.get("next"))

    check("docx_exists", DOCX.exists() and DOCX.stat().st_size > 10000, DOCX.stat().st_size if DOCX.exists() else 0)
    if DOCX.exists():
        document = Document(DOCX)
        check("docx_title_metadata", document.core_properties.title == TITLE, document.core_properties.title)
        check("docx_figure_objects", len(document.inline_shapes) == 6, len(document.inline_shapes))
        check("docx_human_gate", any(paragraph.text == "Author metadata completion gate" for paragraph in document.paragraphs), "gate retained in author-review draft")

    check("cover_letter_files", COVER_MD.exists() and COVER_DOCX.exists(), f"md={COVER_MD.exists()} docx={COVER_DOCX.exists()}")
    cover_text = COVER_MD.read_text(encoding="utf-8") if COVER_MD.exists() else ""
    confirmation_lines = [line for line in cover_text.splitlines() if line.startswith("- [")]
    check("cover_human_confirmations", len(confirmation_lines) == 5 and "[CORRESPONDING AUTHOR NAME AND SIGNATURE BLOCK]" in cover_text, f"confirmation_lines={len(confirmation_lines)}")

    manuscript_reader = PdfReader(str(PDF))
    manuscript_meta = dict(manuscript_reader.metadata or {})
    manuscript_creator = f"{manuscript_meta.get('/Creator', '')} {manuscript_meta.get('/Producer', '')}"
    check("wps_manuscript_pdf", "wps" in manuscript_creator.lower() and len(manuscript_reader.pages) == 31, f"pages={len(manuscript_reader.pages)} creator={manuscript_creator}")
    check("wps_pdf_title", manuscript_meta.get("/Title") == TITLE, manuscript_meta.get("/Title"))
    cover_reader = PdfReader(str(COVER_PDF))
    cover_meta = dict(cover_reader.metadata or {})
    cover_creator = f"{cover_meta.get('/Creator', '')} {cover_meta.get('/Producer', '')}"
    check("one_page_wps_cover", "wps" in cover_creator.lower() and len(cover_reader.pages) == 1, f"pages={len(cover_reader.pages)} creator={cover_creator}")
    rendered = list((OUT / "manuscript_pages_final").glob("*.png"))
    check("wps_render_page_parity", len(rendered) == len(manuscript_reader.pages), f"rendered={len(rendered)} pdf={len(manuscript_reader.pages)}")
    check("visual_contact_sheets", (OUT / "manuscript_contact_final.png").exists() and (OUT / "cover_final_page.png").exists(), "manual visual inspection assets present")

    all_paths = [MD, DOCX, PDF, COVER_MD, COVER_DOCX, COVER_PDF, GA, SUP1, SUP2]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    result = {
        "stage": "R7B4A_HUMAN_GENOMICS_SUBMISSION_INTERFACE",
        "status": status,
        "summary": {"pass": sum(item["status"] == "PASS" for item in checks), "total": len(checks)},
        "checks": checks,
        "artifacts": {path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in all_paths if path.exists()},
        "human_gate": ["authors", "affiliations", "correspondence", "CRediT", "funding", "competing interests", "ethics wording", "acknowledgements", "APC route", "licence", "final approval"],
    }
    (OUT / "R7B4A_final_QA.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(checks).to_csv(OUT / "R7B4A_final_QA.tsv", sep="\t", index=False)
    print(json.dumps({**result["summary"], "status": status}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
