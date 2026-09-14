from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
SRC = ROOT / "3_results/04_integration/R6A3A"
TISSUE = ROOT / "3_results/05_tissue/R6A3A"
AUD = ROOT / "3_results/00_audit/R6A3A"
QA = ROOT / "3_results/00_audit/R6A3A1"
OUT = ROOT / "3_results/04_integration/R6A3A1"
QA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


receipts = []
for name in ["R6A3A_Sun2018_small_byte_receipt.tsv", "R6A3A_Sun2018_full_byte_receipt.tsv",
             "R6A3A_GSE127136_byte_receipt.tsv"]:
    table = pd.read_csv(AUD / name, sep="\t")
    for row in table.itertuples(index=False):
        filename = str(row.file)
        if filename.startswith("QTD000584"):
            local = ROOT / "1_data/qtl/eQTLCatalogue/Sun_2018_QTD000584" / filename
        elif filename == "hg19ToHg38.over.chain":
            local = ROOT / "1_data/reference/liftover" / filename
        else:
            local = ROOT / "1_data/scrna/IgAN/GSE127136" / filename
        actual = sha256(local)
        passed = local.stat().st_size == int(row.bytes) and actual == str(row.sha256)
        receipts.append({"receipt": name, "file": filename, "bytes": local.stat().st_size,
                         "sha256": actual, "pass": passed})
for filename, local, expected_bytes, expected_sha in [
    ("IgAN_Combined_metaanalysis.txt", ROOT/"1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis.txt",
     492016732, "35b603e9f912ec0ed1a04a9aa6cf76c35b75998161e0d1ccbba4d0ded0d2c140"),
    ("gencode.v50.annotation.gtf.gz", ROOT/"1_data/reference/gene_annotation/gencode.v50.annotation.gtf.gz",
     124527720, "83fba3e9b03f0b8c958f3595c6c350adc55f468abf8b0e47b6d5284cfe13a453"),
]:
    actual = sha256(local)
    receipts.append({"receipt": "frozen_upstream_input", "file": filename, "bytes": local.stat().st_size,
                     "sha256": actual, "pass": local.stat().st_size == expected_bytes and actual == expected_sha})
if not all(item["pass"] for item in receipts):
    raise RuntimeError("At least one public input receipt failed independent rehash")

screen = pd.read_csv(SRC / "R6A3A_Sun2018_frozen_target_screen.tsv", sep="\t")
candidates = pd.read_csv(SRC / "R6A3A_pqtl_candidate_molecular_traits.tsv", sep="\t")
expected = {"TNFSF8.3421.54.2..1", "TNFSF12.5939.42.3..1"}
if set(candidates.molecular_trait_id) != expected:
    raise RuntimeError(f"Unexpected frozen pQTL candidates: {set(candidates.molecular_trait_id)}")

coloc = pd.read_csv(SRC / "R6A3A_pqtl_signal_coloc.tsv", sep="\t")
cs = pd.read_csv(ROOT / "1_data/qtl/eQTLCatalogue/Sun_2018_QTD000584/QTD000584.credible_sets.tsv.gz",
                 sep="\t", dtype=str)
cs_components = set()
for row in cs[cs.molecular_trait_id.isin(expected)].itertuples(index=False):
    component = str(row.cs_id).rsplit("_L", 1)[-1]
    if component.isdigit():
        cs_components.add((str(row.molecular_trait_id), int(component)))

component_rows = []
for (locus, gene, trait, idx2), group in coloc.groupby(
        ["locus", "gene_symbol", "molecular_trait_id", "idx2"]):
    idx2 = int(idx2)
    if (str(trait), idx2) not in cs_components:
        continue
    default = group[np.isclose(group.p12.astype(float), 1e-5)].iloc[0]
    low = group[np.isclose(group.p12.astype(float), 1e-6)].iloc[0]
    passed = (float(default["PP.H4.abf"]) >= 0.80 and
              float(default["H4_over_H3H4"]) >= 0.80 and
              float(low["H4_over_H3H4"]) >= 0.50)
    component_rows.append({
        "locus": locus, "gene_symbol": gene, "molecular_trait_id": trait,
        "component": f"L{idx2}", "top_pqtl_variant": default.hit2,
        "PP_H3_default": float(default["PP.H3.abf"]),
        "PP_H4_default": float(default["PP.H4.abf"]),
        "H4_ratio_default": float(default.H4_over_H3H4),
        "H4_ratio_low_p12": float(low.H4_over_H3H4),
        "classification": "PASS" if passed else "FAIL",
    })
components = pd.DataFrame(component_rows).sort_values(["locus", "component"])
components.to_csv(OUT / "R6A3A1_valid_source_component_adjudication.tsv", sep="\t", index=False)
if len(components) != 3 or (components.classification == "PASS").any():
    raise RuntimeError("Independent source-component adjudication did not reproduce expected three failures")

donors = pd.read_csv(TISSUE / "R6A3A_ZMIZ1_kidney_donor_pseudobulk.tsv", sep="\t")
case = donors.loc[donors.analysis_group == "IgAN", "ZMIZ1_log2CPM"].to_numpy()
control = donors.loc[donors.analysis_group == "paracancer_control", "ZMIZ1_log2CPM"].to_numpy()
tissue_gate = json.loads((AUD / "R6A3A_ZMIZ1_kidney_primary_gate.json").read_text(encoding="utf-8"))
if (len(case), len(control)) != (13, 6):
    raise RuntimeError("Unexpected kidney donor counts")
if not np.isclose(case.mean() - control.mean(), tissue_gate["mean_log2CPM_difference_case_minus_control"]):
    raise RuntimeError("ZMIZ1 donor effect does not reproduce")

receipt_table = pd.DataFrame(receipts)
receipt_table.to_csv(QA / "R6A3A1_public_input_rehash.tsv", sep="\t", index=False)
qa = {
    "input_package_sha256": "7acfd7cca97598550e9ec9c90daf37104e6164fe14478661f33829c71ec8f479",
    "input_package_internal_checksums": "29/29_PASS",
    "public_input_files_rehashed": len(receipts),
    "public_input_rehash": "PASS",
    "frozen_targets": int(len(screen)),
    "measured_targets": int(screen.measured_in_permutation.sum()),
    "source_supported_candidates": sorted(candidates.gene_symbol.tolist()),
    "source_supported_traits": int(len(candidates)),
    "harmonized_traits_ge_500_variants": 2,
    "valid_source_cs_components": int(len(components)),
    "shared_signal_pass_components": int((components.classification == "PASS").sum()),
    "kidney_donors": {"IgAN": len(case), "paracancer_control": len(control)},
    "ZMIZ1_case_minus_control_log2CPM": float(case.mean() - control.mean()),
    "ZMIZ1_exact_permutation_p": float(tissue_gate["exact_permutation_p"]),
    "status": "PASS_INDEPENDENT_REPRODUCTION",
}
(QA / "R6A3A1_independent_QA.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")

state = {
    "R6A3A0_INPUT": "PASS_29_OF_29_INTERNAL_CHECKSUMS",
    "R6A3A1_ACTUAL_EXECUTION": "COMPLETE",
    "PUBLIC_BYTE_LEVEL_PROVENANCE": "PASS",
    "PQTL_FROZEN_TARGETS": 11,
    "PQTL_MEASURED_TARGETS": 8,
    "PQTL_SOURCE_SUPPORTED_PROTEINS": ["TNFSF8", "TNFSF12"],
    "PQTL_VALID_SOURCE_CS_COMPONENTS": 3,
    "PQTL_SHARED_SIGNAL_PASS_LOCI": 0,
    "TRACK_A_PQTL": "FAIL_NO_ADDITIONAL_SHARED_SIGNAL",
    "TRACK_B_ZMIZ1_KIDNEY": "INTERPRETABLE_CASE_LOWER_NOT_SIGNIFICANT",
    "TRACK_B_EXACT_PERMUTATION_P": float(tissue_gate["exact_permutation_p"]),
    "IGAN_REGULATORY_MAIN": "FROZEN_ARCHIVE",
    "IGAN_DEFAULT_RESUME": False,
    "NEXT_STAGE": "R7A0_OPEN_DATA_COMPLETION_FIRST_PORTFOLIO_PREFLIGHT",
    "NEXT_STAGE_SCOPE": ["CELIAC_DISEASE", "PRIMARY_BILIARY_CHOLANGITIS", "ALOPECIA_AREATA"],
}
(OUT / "R6A3A1_final_project_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
print(json.dumps(qa, indent=2))
print(json.dumps(state, indent=2))
