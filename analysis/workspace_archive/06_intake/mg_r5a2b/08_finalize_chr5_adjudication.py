#!/usr/bin/env python3
"""Freeze the R5A2B bounded chr5 adjudication and source-LD trigger table."""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(r"H:\SCI2\YR1")
INTEGRATION = ROOT / "3_results/04_integration/R5A2B"
QTL_PATH = ROOT / "3_results/03_qtl/R5A2B/OneK1K_chr5_bounded_region_pairs.tsv.gz"
TARGET_PATH = ROOT / "2_code/06_intake/mg_r5a2b/chr5_source_significant_smoke_targets.tsv"
AUDIT = ROOT / "3_results/00_audit/R5A2B"

smoke = pd.read_csv(INTEGRATION / "chr5_coloc_abf_smoke.tsv", sep="\t")
targets = pd.read_csv(TARGET_PATH, sep="\t")
qtl = pd.read_csv(QTL_PATH, sep="\t")
r_audit = json.loads((AUDIT / "chr5_python_vs_official_R_coloc_audit.json").read_text(encoding="utf-8"))
gwas_audit = json.loads((AUDIT / "MG_GRCh37_chr5_harmonization_audit.json").read_text(encoding="utf-8"))

trigger = smoke.merge(
    targets[["cell_type", "gene_symbol", "qval", "pval_beta", "smoke_role"]],
    left_on=["cell_type", "phenotype_id"],
    right_on=["cell_type", "gene_symbol"],
    validate="many_to_one",
)
trigger["robust_H4"] = (
    (trigger["PP_H4_p12_1e-5"] >= 0.80)
    & (trigger["H4_over_H3H4_p12_1e-5"] >= 0.80)
    & (trigger["H4ratio_p12_1e-6"] >= 0.50)
)
trigger["resolvable_H3H4_ambiguity"] = trigger["classification"].eq("HOLD_LD_REQUIRED")
trigger["source_LD_trigger"] = trigger["robust_H4"] | trigger["resolvable_H3H4_ambiguity"]
trigger["final_interpretation"] = "NO_TRIGGER"
trigger.loc[
    trigger["trait"].eq("EOMG") & (trigger["PP_H3_p12_1e-5"] > trigger["PP_H4_p12_1e-5"]),
    "final_interpretation",
] = "FAIL_EOMG_DISTINCT_SIGNAL_FAVORED"
trigger.loc[trigger["trait"].eq("LOMG"), "final_interpretation"] = "UNINFORMATIVE_NO_LOMG_DISEASE_SIGNAL"
trigger.loc[trigger["trait"].eq("MG_overall"), "final_interpretation"] = "NO_ROBUST_OVERALL_SHARED_SIGNAL"
trigger.to_csv(INTEGRATION / "chr5_sourceLD_trigger_matrix.tsv", sep="\t", index=False)

def row_dict(row: pd.Series) -> dict:
    fields = [
        "trait", "cell_type", "phenotype_id", "n_snps", "gwas_min_p", "gwas_top_variant",
        "qtl_min_p", "qtl_top_variant", "PP_H3_p12_1e-5", "PP_H4_p12_1e-5",
        "H4_over_H3H4_p12_1e-5", "H4_p12_1e-6", "H4ratio_p12_1e-6",
        "H4_p12_1e-4", "H4ratio_p12_1e-4", "shared_top_variant",
        "shared_top_SNP_PP_H4_conditional", "classification",
    ]
    return {field: row[field].item() if hasattr(row[field], "item") else row[field] for field in fields}

eomg = smoke[smoke["trait"].eq("EOMG")]
overall = smoke[smoke["trait"].eq("MG_overall")]
lomg = smoke[smoke["trait"].eq("LOMG")]
nk_tnip1 = qtl[(qtl["cell_type"].eq("NK")) & (qtl["phenotype_id"].eq("TNIP1"))]
cd4_tnip1 = qtl[(qtl["cell_type"].eq("CD4_NC")) & (qtl["phenotype_id"].eq("TNIP1"))]

lead_qtl = {}
for label, frame in [("NK_TNIP1", nk_tnip1), ("CD4_NC_TNIP1", cd4_tnip1)]:
    row = frame[frame["variant_id"].eq("5:150447128")].iloc[0]
    lead_qtl[label] = {
        "N": int(row["n_expression_donors"]),
        "slope_A1": float(row["slope_A1"]),
        "slope_se": float(row["slope_se"]),
        "pval_nominal": float(row["pval_nominal"]),
    }

robust_count = int(trigger["robust_H4"].sum())
hold_count = int(trigger["resolvable_H3H4_ambiguity"].sum())
adjudication = {
    "schema_version": "1.0",
    "stage": "R5A2B",
    "target": "chr5_rs6861227_bounded_8_gene_competition",
    "inputs": {
        "OneK1K_chr5_QTL_rows": int(len(qtl)),
        "actual_cell_gene_pairs_in_bounded_table": int(qtl.groupby(["cell_type", "phenotype_id"]).ngroups),
        "frozen_source_significant_cell_gene_pairs": int(len(targets)),
        "traits": 3,
        "smoke_tests": int(len(smoke)),
        "n_snps_range": [int(smoke["n_snps"].min()), int(smoke["n_snps"].max())],
        "GRCh37_GWAS_gate_pass": bool(gwas_audit["GRCh37_disease_input_gate_pass"]),
    },
    "classification_counts": smoke["classification"].value_counts().to_dict(),
    "trait_classification_counts": {
        trait: group["classification"].value_counts().to_dict() for trait, group in smoke.groupby("trait")
    },
    "top_results": {
        "EOMG": row_dict(eomg.loc[eomg["PP_H4_p12_1e-5"].idxmax()]),
        "MG_overall": row_dict(overall.loc[overall["PP_H4_p12_1e-5"].idxmax()]),
        "LOMG": row_dict(lomg.loc[lomg["PP_H4_p12_1e-5"].idxmax()]),
    },
    "exact_disease_lead_QTL": lead_qtl,
    "official_R_validation": r_audit,
    "gates": {
        "robust_shared_signal_count": robust_count,
        "resolvable_H3H4_ambiguity_count": hold_count,
        "source_LD_trigger_count": int(trigger["source_LD_trigger"].sum()),
        "TENK10K_trigger": False,
    },
    "frozen_decision": "FAIL_CHR5_EXPRESSION_MEDIATION",
    "MG_REGULATORY_MAIN": "NO_GO",
    "further_MG_locus_rescue": "STOP",
    "next_stage": "IGAN_OPEN_DATA_BYTE_LEVEL_PREFLIGHT",
}
(INTEGRATION / "chr5_bounded_final_adjudication.json").write_text(json.dumps(adjudication, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(adjudication, ensure_ascii=False, indent=2))
