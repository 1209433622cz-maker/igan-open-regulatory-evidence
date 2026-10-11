#!/usr/bin/env python3
"""Freeze R6A1 manifests, locus strata, and GO/NO-GO state.

This script only adjudicates byte/schema/testability/detectability evidence.
It does not perform or claim new disease-QTL colocalization.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "3_results" / "00_audit" / "R6A1"
RESULT = ROOT / "3_results" / "04_integration" / "R6A1"
ADMIN = ROOT / "0_admin" / "protocol" / "current"
AUDIT.mkdir(parents=True, exist_ok=True)
RESULT.mkdir(parents=True, exist_ok=True)
ADMIN.mkdir(parents=True, exist_ok=True)


def digest(path: Path) -> dict:
    md5 = hashlib.md5()
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            md5.update(block)
            sha.update(block)
    return {"bytes": path.stat().st_size, "md5": md5.hexdigest(), "sha256": sha.hexdigest()}


sources = [
    {
        "id": "igan_combined",
        "url": "https://www.columbiamedicine.org/divisions/kiryluk/gwas/IgA_Summary/IgAN_Combined_metaanalysis.txt",
        "transfer": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis.txt",
        "canonical": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis.txt",
        "content_encoding": "identity",
        "reported_transfer_bytes": 492016732,
    },
    {
        "id": "igan_european",
        "url": "https://www.columbiamedicine.org/divisions/kiryluk/gwas/IgA_Summary/IgAN_Combined_metaanalysis_European_only.txt",
        "transfer": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_European_only.txt.br",
        "canonical": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_European_only.txt",
        "content_encoding": "br",
        "reported_transfer_bytes": 164526659,
    },
    {
        "id": "igan_asian",
        "url": "https://www.columbiamedicine.org/divisions/kiryluk/gwas/IgA_Summary/IgAN_Combined_metaanalysis_Asian_only.txt",
        "transfer": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_Asian_only.txt",
        "canonical": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_Asian_only.txt",
        "content_encoding": "identity",
        "reported_transfer_bytes": 376485006,
    },
    {
        "id": "serum_iga_combined",
        "url": "https://www.columbiamedicine.org/divisions/kiryluk/gwas/IgA/META.IGA.LEVELS.ALL.COMBINED.txt",
        "transfer": ROOT / "1_data/gwas/serum_IgA/Kiryluk2022/META.IGA.LEVELS.ALL.COMBINED.txt.br",
        "canonical": ROOT / "1_data/gwas/serum_IgA/Kiryluk2022/META.IGA.LEVELS.ALL.COMBINED.txt",
        "content_encoding": "br",
        "reported_transfer_bytes": 168662774,
    },
]

byte_manifest = []
for source in sources:
    transfer = source["transfer"]
    canonical = source["canonical"]
    if not transfer.exists() or not canonical.exists():
        raise FileNotFoundError(f"missing source layer: {source['id']}")
    transfer_hash = digest(transfer)
    canonical_hash = transfer_hash if transfer.resolve() == canonical.resolve() else digest(canonical)
    byte_manifest.append(
        {
            "id": source["id"],
            "url": source["url"],
            "official_checksum_available": False,
            "content_encoding": source["content_encoding"],
            "transfer_layer": {
                "path": str(transfer),
                **transfer_hash,
                "reported_transfer_bytes": source["reported_transfer_bytes"],
                "byte_gate": "PASS" if transfer_hash["bytes"] == source["reported_transfer_bytes"] else "FAIL",
            },
            "canonical_analysis_layer": {"path": str(canonical), **canonical_hash},
        }
    )

(AUDIT / "R6A1_download_byte_manifest_v2.json").write_text(
    json.dumps(byte_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
)

gwas = json.loads((AUDIT / "IgAN_GWAS_schema_loci_serumIgA_audit.json").read_text(encoding="utf-8"))
qtl = json.loads((AUDIT / "IgAN_QTL_testability_positive_control_audit.json").read_text(encoding="utf-8"))
kidney = json.loads((AUDIT / "IgAN_kidney_tissue_byte_metadata_detectability_audit.json").read_text(encoding="utf-8"))
loci = pd.read_csv(RESULT / "IgAN_24_locus_positive_evidence_preflight_matrix.tsv", sep="\t")
signals = pd.read_csv(RESULT / "IgAN_25_non_HLA_signal_ancestry_serumIgA_matrix.tsv", sep="\t")
controls = pd.read_csv(RESULT / "IgAN_published_positive_control_screening_recovery.tsv", sep="\t")
kidney_loci = pd.read_csv(RESULT / "GSE127136_locus_candidate_detectability.tsv", sep="\t")

controls["cross_ok"] = controls["cross_resource_compatible_cell_recovered"].astype(str).str.lower().eq("true")
control_loci = sorted(controls.loc[controls.cross_ok, "locus"].unique())
control_genes = sorted(controls.loc[controls.cross_ok, "gene_symbol"].unique())
signals["serum_ok"] = signals["serum_iga_nominal_concordant"].astype(str).str.lower().eq("true")
serum_loci = sorted(signals.loc[signals.serum_ok, "locus"].unique())
kidney_detect = dict(zip(kidney_loci["locus"], kidney_loci["detectable_cross_resource_genes"]))

loci["serum_IgA_nominal_concordant_signal"] = loci["locus"].isin(serum_loci)
loci["published_DICE_control_cross_resource_recovered"] = loci["locus"].isin(control_loci)
loci["GSE127136_detected_cross_resource_genes"] = loci["locus"].map(kidney_detect).fillna(0).astype(int)
loci["kidney_target_detectable"] = loci["GSE127136_detected_cross_resource_genes"] > 0

def stratum(row: pd.Series) -> str:
    if row["published_DICE_control_cross_resource_recovered"]:
        return "A_BENCHMARK_POSITIVE_CONTROL"
    if row["serum_IgA_nominal_concordant_signal"] and row["cross_resource_candidate"] and row["kidney_target_detectable"]:
        return "B_TRAIT_CONCORDANT_CROSS_RESOURCE"
    if row["cross_resource_candidate"] and row["kidney_target_detectable"]:
        return "C_LANDSCAPE_TESTABLE"
    return "D_RESOURCE_ASYMMETRIC"

loci["R6A2_entry_stratum"] = loci.apply(stratum, axis=1)
loci.to_csv(RESULT / "IgAN_24_locus_R6A2_entry_matrix.tsv", sep="\t", index=False)

cross_loci = int(qtl["cross_resource"]["loci"])
testable_onek = int(qtl["OneK1K"]["testable_loci"])
positive_control_loci = len(control_loci)
expected_tier_eligible = positive_control_loci

gates = {
    "ALL_4_GWAS_BYTES": all(x["transfer_layer"]["byte_gate"] == "PASS" for x in byte_manifest),
    "GWAS_SCHEMA_AND_LOCUS_RECOVERY": gwas["overall_gate"] == "PASS",
    "NON_HLA_LOCUS_COUNT_GE_20": int(gwas["published_signal_universe"]["non_HLA_loci"]) >= 20,
    "ONEK1K_TESTABLE_LOCI_GE_8": testable_onek >= 8,
    "CROSS_RESOURCE_QTL_CANDIDATE_LOCI_GE_4": cross_loci >= 4,
    "KNOWN_POSITIVE_CONTROL_LOCUS_RECOVERY_GE_2": positive_control_loci >= 2,
    "KIDNEY_TARGET_DETECTABILITY": kidney["kidney_detectability_gate"] == "PASS",
    "EXPECTED_TIER_A_OR_B_ELIGIBLE_LOCI_GE_3": expected_tier_eligible >= 3,
}
overall = "GO_R6A2" if all(gates.values()) else "NO_GO"

state = {
    "schema_version": "1.0",
    "project": "IgAN open-data regulatory landscape",
    "stage": "R6A1",
    "adjudication": overall,
    "gates": gates,
    "metrics": {
        "published_non_HLA_loci": int(gwas["published_signal_universe"]["non_HLA_loci"]),
        "published_non_HLA_independent_signals": int(gwas["published_signal_universe"]["non_HLA_independent_signals"]),
        "OneK1K_testable_loci": testable_onek,
        "TenK10K_testable_loci": int(qtl["TenK10K"]["testable_loci"]),
        "cross_resource_candidate_loci": cross_loci,
        "cross_resource_candidate_genes": int(qtl["cross_resource"]["genes"]),
        "serum_IgA_nominal_concordant_signals": int(gwas["serum_IgA_overlap"]["nominal_and_risk_direction_concordant"]),
        "published_control_genes_cross_resource_recovered": len(control_genes),
        "published_control_loci_cross_resource_recovered": positive_control_loci,
        "GSE127136_target_gene_detection_fraction": kidney["GSE127136"]["target_gene_detection_fraction"],
    },
    "R6A2_frozen_scope": {
        "full_universe": "24 published non-HLA loci; CFH has two independent signals",
        "first_wave_benchmark_loci": control_loci,
        "first_wave_benchmark_genes": control_genes,
        "trait_concordant_loci": serum_loci,
        "source_LD_rule": "build LD only for a prespecified cell-gene signal that triggers robust H4 or resolvable H3/H4 ambiguity",
        "claim_boundary": "R6A1 establishes access, testability and positive-control eligibility only; all new disease-QTL shared-signal claims require R6A2 signal-level analysis",
    },
    "holds": [
        "no new colocalization-positive claim",
        "no causal gene claim from QTL significance alone",
        "no cell-level differential inference treating cells as biological replicates",
        "GSE286184 is spatial localization support, not a four-case disease-control study",
    ],
}
(AUDIT / "R6A1_final_gate_adjudication.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
(ADMIN / "R6A1_IgAN_preflight_final_state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

portfolio = {
    "schema_version": "1.0",
    "frozen_at": "2026-09-14",
    "decision_id": "R6A1",
    "ssc": {"role": "ARCHIVED_PROJECT_AND_METHOD_ENGINEERING_ASSET_LIBRARY", "status": "FROZEN_ARCHIVE"},
    "mg": {"role": "ARCHIVED_PROJECT_AND_METHOD_ENGINEERING_ASSET", "regulatory_main_status": "NO_GO", "default_resume": False},
    "primary_project": {
        "project": "IGA_NEPHROPATHY",
        "status": "GO",
        "completed_stage": "R6A1_BYTE_LEVEL_POSITIVE_EVIDENCE_PREFLIGHT",
        "next_stage": "R6A2A_POSITIVE_CONTROL_SIGNAL_RECOVERY",
        "axis": "BLOOD_IMMUNE_REGULATORY_SIGNAL_TO_KIDNEY_DISEASE_STATE_CONVERGENCE",
    },
    "data_policy": {
        "open_data_only": "HARD_CONSTRAINT",
        "permission_required_data": "EXCLUDED",
        "author_request_data": "EXCLUDED",
        "ega_dbgap_ukb_green_library": "EXCLUDED",
    },
}
(ADMIN / "project_portfolio_state_R6A1.json").write_text(json.dumps(portfolio, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(state, indent=2, ensure_ascii=False))
