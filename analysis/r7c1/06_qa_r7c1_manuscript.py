#!/usr/bin/env python3
"""Machine and hostile-claim QA for the R7C1 manuscript fork."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import pandas as pd
from docx import Document
from pypdf import PdfReader


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_manuscript/R7C1_IL12RB2_ExternalValidation_ManuscriptFork"
R7C0 = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011/results"
MD = WORK / "manuscript/R7C1_HumanGenomics_IL12RB2_external_validation_fork.md"
DOCX = WORK / "manuscript/R7C1_HumanGenomics_IL12RB2_external_validation_fork.docx"
PDF = WORK / "manuscript/R7C1_HumanGenomics_IL12RB2_external_validation_fork_WPS.pdf"
BASELINE = ROOT / "5_manuscript/R7B4B_FinalSubmissionCandidate"
ADD3 = WORK / "supplement/Additional_file_3_R7C1_External_Validation_Data.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def add(rows, gate, passed, evidence):
    rows.append({"gate": gate, "pass": bool(passed), "evidence": str(evidence)})


def main() -> None:
    text = MD.read_text(encoding="utf-8")
    rows = []

    expected_baseline = {
        BASELINE / "manuscript/R7B4B_HumanGenomics_final.md": "39c3164e572d7957859de71815856cd7b61cb7865caea00ffeb3078ede7a3638",
        BASELINE / "manuscript/R7B4B_HumanGenomics_final.docx": "8dec3207ec695aded22a50ad0646c0b016df27fb28eb333fbd70ca7c35039ff7",
        BASELINE / "manuscript/R7B4B_HumanGenomics_final_WPS.pdf": "c7f55e24936b29add40621ff2b4dd57c28664fb0663ff9a049a810d2e9ab4786",
    }
    for path, expected in expected_baseline.items():
        observed = sha256(path)
        add(rows, f"baseline_immutable_{path.suffix.lstrip('.')}", observed == expected, observed)

    coloc = pd.read_csv(R7C0 / "R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv", sep="\t")
    triangle = json.loads((R7C0 / "R7C0_IL12RB2_chromatin_triangle_adjudication.json").read_text(encoding="utf-8"))
    coverage = pd.read_csv(R7C0 / "R7C0_CASCADE_27gene_coverage.tsv", sep="\t")
    cs = pd.read_csv(R7C0 / "R7C0_FinnGen_R12_R13_IL12RB2_CS_members.tsv", sep="\t")
    cs_identity = json.loads((R7C0 / "R7C0_FinnGen_R12_R13_IL12RB2_signal_identity.json").read_text(encoding="utf-8"))
    omix = pd.read_csv(R7C0 / "R7C0_OMIX001122_spatial_sample_QC.tsv", sep="\t")

    checks = {
        "external_variant_count_1175": "1,175" in text,
        "default_h4_09977": "0.9977" in text and abs(float(coloc.loc[coloc.p12 == 1e-5, "PP_H4"].iloc[0]) - 0.9976766621271316) < 1e-12,
        "skeptical_h4_09772": "0.9772" in text and abs(float(coloc.loc[coloc.p12 == 1e-6, "PP_H4"].iloc[0]) - 0.9772424819044834) < 1e-12,
        "high_prior_h4_09998": "0.9998" in text and float(coloc.loc[coloc.p12 == 1e-4, "PP_H4"].iloc[0]) > 0.9997,
        "source_cs_2_of_2": "both members of the OneK QTL credible set" in text,
        "r13_cs_17": "R13 set contained 17" in text and len(cs) == 17 and cs_identity["r12_cs_size"] == 19 and cs_identity["r13_cs_size"] == 17,
        "cs_jaccard": "Jaccard=0.895" in text,
        "cs_correlation": "r=0.833" in text,
        "cascade_27": "Of 27 fixed genes" in text and coverage.shape[0] == 27,
        "cascade_22": "22 had relevant broad-cell eQTL coverage" in text and int((coverage["relevant_l1_eqtl_q_lt_0_05"] > 0).sum()) == 22,
        "disease_eqtl_h4": "PP.H4=0.9703" in text and abs(triangle["disease_eQTL"]["PP_H4_abf"] - 0.9703068) < 1e-6,
        "disease_caqtl_h4": "PP.H4=0.9695" in text and abs(triangle["disease_caQTL"]["PP_H4_abf"] - 0.9695295) < 1e-6,
        "peak_distance": "239 bp" in text and triangle["peak_gene_link"]["distance_to_tss"] == 239,
        "peak_link_beta": "coefficient 0.141" in text and abs(triangle["peak_gene_link"]["link_beta"] - 0.140574) < 1e-6,
        "omix_two_matrices": "single PBC and single control spatial matrices" in text and omix.shape[0] == 2,
    }
    for gate, passed in checks.items():
        add(rows, gate, passed, "manuscript token + frozen source")

    add(rows, "no_person_level_independence_claim", "person-level non-overlap could not be demonstrated" in text and "person-level zero overlap" in text, "explicit boundary")
    add(rows, "no_second_source_ld_claim", "not as a second source-LD multi-signal fit" in text and "remained single-causal rather than source-LD multi-signal" in text, "explicit boundary")
    add(rows, "no_direct_mediation_claim", "direct eQTL-caQTL posterior was unavailable" in text and "did not supply the unavailable direct eQTL-caQTL posterior" in text, "explicit boundary")
    add(rows, "omix_descriptive_only", "restricted this observation to descriptive detectability" in text, "explicit boundary")
    add(rows, "old_chromatin_claim_removed", "PBC-caQTL signal sharing was not established" not in text, "stale claim absent")
    add(rows, "novelty_calibrated", "the contribution is not first nomination of the gene" in text, "claim governor")
    add(rows, "new_gene_fishing_absent", "it was not used to select new genes" in text and "new candidate discovery" not in text.lower(), "bounded module")

    ref_numbers = [int(x) for x in re.findall(r"(?m)^(\d+)\. ", text)]
    add(rows, "references_continuous_1_25", ref_numbers == list(range(1, 26)), ref_numbers)
    citation_numbers = [int(n) for group in re.findall(r"\[([0-9,]+)\]", text[:text.index("## References")]) for n in group.split(",")]
    add(rows, "citations_in_range", citation_numbers and min(citation_numbers) >= 1 and max(citation_numbers) <= 25, f"min={min(citation_numbers)} max={max(citation_numbers)}")
    add(rows, "every_reference_cited", set(ref_numbers).issubset(set(citation_numbers)), sorted(set(ref_numbers) - set(citation_numbers)))

    doc = Document(DOCX)
    drawing_count = sum(len(p._p.xpath(".//w:drawing")) for p in doc.paragraphs)
    add(rows, "docx_six_figures", drawing_count == 6, drawing_count)
    add(rows, "docx_line_numbering", bool(doc.sections[0]._sectPr.xpath("./w:lnNumType")), "w:lnNumType present")
    with zipfile.ZipFile(DOCX) as docx_zip:
        footer_xml = "\n".join(
            docx_zip.read(name).decode("utf-8", errors="ignore")
            for name in docx_zip.namelist()
            if name.startswith("word/footer") and name.endswith(".xml")
        )
    add(rows, "docx_page_number_field", "PAGE" in footer_xml, "PAGE field in DOCX footer XML")

    pdf = PdfReader(str(PDF))
    meta = pdf.metadata or {}
    producer = f"{meta.get('/Producer', '')} {meta.get('/Creator', '')}".lower()
    add(rows, "wps_pdf_32_pages", len(pdf.pages) == 32, len(pdf.pages))
    add(rows, "wps_pdf_metadata", "wps" in producer, producer)
    rendered_pages = sorted((WORK / "qa/wps_pages").glob("page-*.png"))
    add(rows, "all_pdf_pages_rendered", len(rendered_pages) == len(pdf.pages), len(rendered_pages))

    with zipfile.ZipFile(ADD3) as archive:
        bad = archive.testzip()
        names = archive.namelist()
    add(rows, "additional_file_3_crc", bad is None, bad)
    add(rows, "additional_file_3_manifest", "checksums.sha256.tsv" in names, len(names))
    add(rows, "figure4_png_exists", (WORK / "figures/Figure4_IL12RB2_external_evidence.png").stat().st_size > 100_000, "journal figure")
    add(rows, "additional_file_3_declared", "**Additional file 3.**" in text and "**Supplementary Table S11.**" in text, "reader-facing inventory")

    failures = [row for row in rows if not row["pass"]]
    result = {
        "stage": "R7C1_HOSTILE_MANUSCRIPT_QA",
        "pass": len(rows) - len(failures),
        "fail": len(failures),
        "total": len(rows),
        "status": "PASS" if not failures else "FAIL",
        "checks": rows,
    }
    (WORK / "qa/R7C1_machine_hostile_QA.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(rows).to_csv(WORK / "qa/R7C1_machine_hostile_QA.tsv", sep="\t", index=False)
    print(json.dumps({k: result[k] for k in ("status", "pass", "fail", "total")}, indent=2))
    if failures:
        print(json.dumps(failures, indent=2, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
