#!/usr/bin/env python3
"""Deterministic QA for the R7A2A3 manuscript draft.

This checks structural and numeric invariants. It is not a substitute for the
semantic hostile-review pass frozen for R7A2A4.
"""

from __future__ import annotations

import csv
import json
import re
import os
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPO_CANDIDATE = SCRIPT.parents[2]
if (REPO_CANDIDATE / "manuscript" / "R7A2A3_manuscript_v1.md").exists():
    ROOT = REPO_CANDIDATE
    MANUSCRIPT = ROOT / "manuscript" / "R7A2A3_manuscript_v1.md"
    OUT = ROOT / "results" / "r7a2a3" / "R7A2A3_QiTeng_QA.json"
    UPSTREAM = ROOT / "results"
    MIRROR = ROOT / "results" / "r7a2a3" / "R7A2A3_methods_results_mirror.tsv"
else:
    ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
    MANUSCRIPT = ROOT / "5_manuscript" / "R7A2A3" / "R7A2A3_manuscript_v1.md"
    OUT = ROOT / "3_results" / "04_integration" / "R7A2A3" / "R7A2A3_QiTeng_QA.json"
    UPSTREAM = ROOT / "github" / "igan-open-regulatory-evidence" / "results"
    MIRROR = ROOT / "3_results" / "04_integration" / "R7A2A3" / "R7A2A3_methods_results_mirror.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


text = MANUSCRIPT.read_text(encoding="utf-8")
body, _, refs_and_after = text.partition("## References")

checks: list[dict[str, object]] = []


def add(name: str, passed: bool, observed: object, expected: object) -> None:
    checks.append({"name": name, "pass": bool(passed), "observed": observed, "expected": expected})


required_headings = [
    "## Abstract",
    "## Introduction",
    "## Results",
    "## Discussion",
    "## Methods",
    "## Data availability",
    "## Code availability",
    "## Ethics statement",
    "## Author contributions",
    "## Funding",
    "## Competing interests",
    "## References",
    "## Figure legends",
    "## Supplementary table and figure legends",
]
missing_headings = [h for h in required_headings if h not in text]
add("required_headings", not missing_headings, missing_headings, [])

required_sentences = [
    "Both prespecified target–lineage pairs were detectable in all five PBC and all five control donors. FCRL3–B showed a lower direction in PBC, whereas IL12RB2–NK showed a higher direction; neither target passed the prespecified two-target corrected case–control enrichment threshold.",
    "Because FCRL3 and IL12RB2 have previously been implicated by PBC genetics and molecular-QTL studies, the contribution of this study lies in source-matched, cell-context-resolved multi-signal inference and independent single-cell eQTL replication rather than gene discovery.",
]
missing_required = [s for s in required_sentences if s not in text]
add("required_frozen_sentences", not missing_required, len(required_sentences) - len(missing_required), len(required_sentences))

ref_lines = re.findall(r"(?m)^(\d+)\.\s", refs_and_after)
ref_numbers = [int(x) for x in ref_lines]
expected_refs = list(range(1, max(ref_numbers, default=0) + 1))
add("reference_list_continuity", ref_numbers == expected_refs, ref_numbers, expected_refs)

citation_numbers: list[int] = []
for group in re.findall(r"\[([0-9,;\-– ]+)\]", body):
    for part in re.split(r"[,;]", group):
        part = part.strip()
        m = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", part)
        if m:
            citation_numbers.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            citation_numbers.append(int(part))
cited = sorted(set(citation_numbers))
add("citation_range", cited == expected_refs, cited, expected_refs)

first_seen: list[int] = []
for n in citation_numbers:
    if n not in first_seen:
        first_seen.append(n)
add("citation_first_appearance", first_seen == expected_refs, first_seen, expected_refs)

forbidden_assertions = [
    "is a proven causal mediator",
    "PBC-specific upregulation",
    "newly discovered PBC gene",
    "validated therapeutic target",
    "confirmed therapeutic target",
    "significantly upregulated in PBC liver",
    "is downregulated in PBC liver",
    "causes PBC",
    "mediates PBC risk",
    "This study proves",
]
found_forbidden = [p for p in forbidden_assertions if p.lower() in body.lower()]
add("forbidden_positive_assertions", not found_forbidden, found_forbidden, [])

stability = read_tsv(UPSTREAM / "r7a1b" / "integration" / "R7A1B_signal_stability_by_cell.tsv")
stab = {(r["gene"], r["cell_type"]): r for r in stability}
smoke = read_tsv(UPSTREAM / "r7a1b" / "integration" / "R7A1B_coloc_smoke.tsv")
smk = {(r["gene"], r["cell_type"]): r for r in smoke}
tenk_il = read_tsv(UPSTREAM / "r7a1c" / "R7A1C_IL12RB2_TenK_NK_fullPBC_coloc.tsv")
tenk_fc = read_tsv(UPSTREAM / "r7a1c" / "R7A1C_FCRL3_TenK_Bintermediate_coloc.tsv")
tissue = read_tsv(UPSTREAM / "r7a2a1" / "PBC_vs_control_target_panel_sensitivity.tsv")

expected_tokens = {
    "OneK_IL12RB2_default": f"{float(stab[('IL12RB2', 'NK')]['min_default_PP_H4']):.4f}",
    "OneK_IL12RB2_low_prior": f"{float(stab[('IL12RB2', 'NK')]['min_low_prior_H4_ratio']):.4f}",
    "OneK_FCRL3_CD8ET_smoke": f"{float(smk[('FCRL3', 'CD8_ET')]['PP_H4']):.4f}",
    "OneK_FCRL3_CD8ET_multi": f"{float(stab[('FCRL3', 'CD8_ET')]['min_default_PP_H4']):.4f}",
    "TenK_IL12RB2_default": f"{float(next(r for r in tenk_il if r['p12'] == '1e-05')['PP_H4']):.4f}",
    "TenK_IL12RB2_low": f"{float(next(r for r in tenk_il if r['p12'] == '1e-06')['H4_over_H3H4']):.4f}",
    "TenK_FCRL3_default": f"{float(next(r for r in tenk_fc if r['p12'] == '1e-05')['PP_H4']):.4f}",
    "TenK_FCRL3_low": f"{float(next(r for r in tenk_fc if r['p12'] == '1e-06')['H4_over_H3H4']):.4f}",
    "Tissue_FCRL3_diff": f"{float(next(r for r in tissue if r['target_lineage'] == 'FCRL3_B')['mean_transformed_difference_PBC_minus_control']):.4f}",
    "Tissue_IL12RB2_diff": f"{float(next(r for r in tissue if r['target_lineage'] == 'IL12RB2_NK')['mean_transformed_difference_PBC_minus_control']):.4f}",
}
normalized_text = text.replace("−", "-")
for name, token in expected_tokens.items():
    add(f"numeric_token_{name}", token in normalized_text, token if token in normalized_text else None, token)

add("frozen_universe_visible", "three established non-HLA PBC loci and nine gene–cell combinations" in text, True, True)
add("negative_controls_propagated", all(term in body for term in ["CD8_ET", "CD8_NC", "INAVA"]), True, True)
add("tenk_caveat_visible", "donor-level TenK10K LD was not reconstructed" in text, True, True)
add("author_metadata_placeholders", all(term in text for term in ["[AUTHOR NAMES TO BE COMPLETED]", "[AFFILIATIONS TO BE COMPLETED]", "[FUNDING INFORMATION TO BE COMPLETED AND VERIFIED.]", "[COMPETING-INTEREST DECLARATION TO BE COMPLETED AND VERIFIED.]"]), True, True)

mirror = read_tsv(MIRROR)
mirror_pass = sum(r["mirror_status"] == "PASS" for r in mirror)
add("methods_results_mirror", mirror_pass == len(mirror) == 11, mirror_pass, 11)

word_count = len(re.findall(r"\b[\w–-]+\b", text))
add("manuscript_word_count_floor", word_count >= 4500, word_count, ">=4500")

payload = {
    "stage": "R7A2A3",
    "qa_scope": "deterministic_structure_numeric_reference_and_wording_invariants",
    "semantic_review_required_next": "R7A2A4_HOSTILE_MANUSCRIPT_AUDIT",
    "checks": checks,
    "passed": sum(c["pass"] for c in checks),
    "total": len(checks),
    "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
raise SystemExit(0 if payload["status"] == "PASS" else 1)
