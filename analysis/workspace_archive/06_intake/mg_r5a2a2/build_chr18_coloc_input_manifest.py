#!/usr/bin/env python3
"""Build cell-gene-specific MG/OneK1K overlap counts for the chr18 pilot."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
QTL_PATH = ROOT / "3_results/03_qtl/R5A2A2/OneK1K_chr18_fixed_1Mb_region_pairs.tsv.gz"
GWAS_DIR = ROOT / "3_results/01_gwas/R5A2A2"
OUT_DIR = ROOT / "3_results/04_integration/R5A2A2"
AUDIT_DIR = ROOT / "3_results/00_audit/R5A2A2"
LEAD = "18:60005046"
GWAS_FILES = {
    "MG_overall": "GCST90432156_MG_overall_chr18_GRCh37_fixed_1Mb.tsv.gz",
    "EOMG": "GCST90432157_EOMG_chr18_GRCh37_fixed_1Mb.tsv.gz",
    "LOMG": "GCST90432158_LOMG_chr18_GRCh37_fixed_1Mb.tsv.gz",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    qtl = pd.read_csv(QTL_PATH, sep="\t")
    required_qtl = {
        "cell_type", "n_expression_donors", "phenotype_id", "variant_id", "pval_nominal",
        "slope_A1", "slope_se", "af_A1",
    }
    if not required_qtl.issubset(qtl.columns):
        raise RuntimeError(f"Missing QTL columns: {sorted(required_qtl - set(qtl.columns))}")
    if qtl.duplicated(["cell_type", "phenotype_id", "variant_id"]).any():
        raise RuntimeError("Duplicate cell-gene-variant QTL rows")

    gwas: dict[str, pd.DataFrame] = {}
    eligible_sets: dict[str, set[str]] = {}
    for trait, filename in GWAS_FILES.items():
        frame = pd.read_csv(GWAS_DIR / filename, sep="\t")
        eligible = frame[frame["inference_eligible"].astype(str).str.lower().eq("true")].copy()
        if eligible["variant_id"].duplicated().any():
            raise RuntimeError(f"Duplicate eligible GWAS variants for {trait}")
        gwas[trait] = eligible.set_index("variant_id", drop=False)
        eligible_sets[trait] = set(eligible["variant_id"])

    all_three = set.intersection(*eligible_sets.values())
    e_l = eligible_sets["EOMG"] & eligible_sets["LOMG"]
    rows: list[dict[str, object]] = []
    for (cell, gene), frame in qtl.groupby(["cell_type", "phenotype_id"], sort=True):
        qtl_variants = set(frame["variant_id"])
        top = frame.loc[frame["pval_nominal"].idxmin()]
        row: dict[str, object] = {
            "cell_type": cell,
            "phenotype_id": gene,
            "n_expression_donors": int(frame["n_expression_donors"].iloc[0]),
            "qtl_variants": len(qtl_variants),
            "EOMG_LOMG_shared_with_qtl": len(qtl_variants & e_l),
            "all_three_GWAS_shared_with_qtl": len(qtl_variants & all_three),
            "qtl_top_variant": top["variant_id"],
            "qtl_top_pval_nominal": float(top["pval_nominal"]),
            "qtl_top_slope_A1": float(top["slope_A1"]),
            "qtl_lead_present": LEAD in qtl_variants,
        }
        for trait in GWAS_FILES:
            common = qtl_variants & eligible_sets[trait]
            row[f"{trait}_shared_with_qtl"] = len(common)
            if common:
                disease_rows = gwas[trait].loc[list(common)]
                disease_top = disease_rows.loc[disease_rows["p_value"].idxmin()]
                row[f"{trait}_top_variant_in_overlap"] = disease_top["variant_id"]
                row[f"{trait}_top_p_in_overlap"] = float(disease_top["p_value"])
            else:
                row[f"{trait}_top_variant_in_overlap"] = ""
                row[f"{trait}_top_p_in_overlap"] = float("nan")
        row["lead_present_all_required_inputs"] = bool(
            row["qtl_lead_present"] and all(LEAD in eligible_sets[t] for t in GWAS_FILES)
        )
        row["ABF_input_gate_pass"] = bool(
            row["EOMG_LOMG_shared_with_qtl"] >= 500 and row["lead_present_all_required_inputs"]
        )
        rows.append(row)

    manifest = pd.DataFrame(rows).sort_values(["phenotype_id", "cell_type"])
    manifest_path = OUT_DIR / "OneK1K_chr18_coloc_input_manifest.tsv"
    manifest.to_csv(manifest_path, sep="\t", index=False, lineterminator="\n")

    summary = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "region": "GRCh37 chr18:59005046-61005046",
        "lead": LEAD,
        "QTL_pairs": int(len(qtl)),
        "cell_gene_pairs": int(len(manifest)),
        "unique_cells": int(manifest["cell_type"].nunique()),
        "unique_genes": int(manifest["phenotype_id"].nunique()),
        "eligible_GWAS_variants": {trait: len(values) for trait, values in eligible_sets.items()},
        "EOMG_LOMG_shared_variants": len(e_l),
        "all_three_GWAS_shared_variants": len(all_three),
        "cell_gene_pairs_passing_ABF_input_gate": int(manifest["ABF_input_gate_pass"].sum()),
        "minimum_EOMG_LOMG_shared_with_qtl": int(manifest["EOMG_LOMG_shared_with_qtl"].min()),
        "maximum_EOMG_LOMG_shared_with_qtl": int(manifest["EOMG_LOMG_shared_with_qtl"].max()),
        "TNFRSF11A_cells": sorted(manifest.loc[manifest["phenotype_id"].eq("TNFRSF11A"), "cell_type"].tolist()),
        "checks": {
            "qtl_pairs_nonempty": len(qtl) > 0,
            "all_71_cell_gene_pairs_pass_ABF_input_gate": len(manifest) == 71 and bool(manifest["ABF_input_gate_pass"].all()),
            "all_three_GWAS_share_at_least_1000_variants": len(all_three) >= 1000,
            "TNFRSF11A_testable_in_at_least_one_cell": bool(
                manifest.loc[manifest["phenotype_id"].eq("TNFRSF11A"), "ABF_input_gate_pass"].any()
            ),
        },
    }
    summary["chr18_coloc_input_gate_pass"] = all(summary["checks"].values())
    summary_path = AUDIT_DIR / "OneK1K_chr18_coloc_input_readiness.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["chr18_coloc_input_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
