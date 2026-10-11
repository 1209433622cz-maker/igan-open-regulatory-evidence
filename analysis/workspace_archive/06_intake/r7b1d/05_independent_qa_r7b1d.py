#!/usr/bin/env python3
"""Independent deterministic QA for the R7B1D external gate."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "3_results/04_integration/R7B1D"
RAW = ROOT / "3_results/01_intake/R7B1D/finngen_cascade_20261009"
FIG = ROOT / "5_analysis/figures/R7B1D"
OUT = ROOT / "3_results/00_audit/R7B1D"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(name: str, ok: bool, observed, expected) -> None:
        checks.append({"name": name, "pass": bool(ok), "observed": observed, "expected": expected})

    receipt = pd.read_csv(RAW / "R7B1D_finngen_api_receipts.tsv", sep="\t")
    targets = pd.read_csv(RES / "R7B1D_external_target_registry.tsv", sep="\t")
    coloc = pd.read_csv(RES / "R7B1D_FinnGen_PBC_molQTL_coloc.tsv", sep="\t")
    coverage = pd.read_csv(RES / "R7B1D_FinnGen_coloc_coverage.tsv", sep="\t")
    cascade = pd.read_csv(RES / "R7B1D_IL12RB2_FinnGen_positional_cascade.tsv", sep="\t")
    directions = pd.read_csv(RES / "R7B1D_risk_allele_expression_direction.tsv", sep="\t")
    final = pd.read_csv(RES / "R7B1D_external_axis_adjudication.tsv", sep="\t")
    state = json.loads((RES / "R7B1D_external_gate_state.json").read_text(encoding="utf-8"))

    check("api_receipts_18", len(receipt) == 18, len(receipt), 18)
    check("api_all_http_200", (receipt.status_code == 200).all(), receipt.status_code.value_counts().to_dict(), {200: 18})
    check("api_all_valid_json", receipt.valid_json.astype(bool).all(), int(receipt.valid_json.astype(bool).sum()), 18)
    check("current_pbc_search_index_empty_logged", state["current_phenotype_search_rows"] == 0, state["current_phenotype_search_rows"], 0)
    check("current_pbc_direct_endpoints_live", state["current_autocomplete_identity"] == "CHIRBIL_PRIM", state["current_autocomplete_identity"], "CHIRBIL_PRIM")
    check("target_registry_exact_4", len(targets) == 4, len(targets), 4)
    check("target_ids_unique", targets.comparison_id.nunique() == 4, targets.comparison_id.nunique(), 4)
    check("no_new_target_selection", set(targets.comparison_id) == {"R7B1_000258", "R7B1_000410", "R7B1_000411", "R7B1_000414"}, sorted(targets.comparison_id.tolist()), "exact frozen IDs")
    il = coloc[coloc.trait2_symbol == "IL12RB2"]
    fc = coloc[coloc.trait2_symbol == "FCRL3"]
    check("FinnGen_IL12RB2_PBC_rows_3", len(il) == 3, len(il), 3)
    check("FinnGen_IL12RB2_cells", set(il.cell_type2) == {"l1.NK", "l1.PBMC", "l2.NK"}, sorted(il.cell_type2.tolist()), ["l1.NK", "l1.PBMC", "l2.NK"])
    check("FinnGen_IL12RB2_H4_min_gt_0_96", il["PP.H4.abf"].min() > 0.96, float(il["PP.H4.abf"].min()), ">0.96")
    check("FinnGen_FCRL3_PBC_rows_0", len(fc) == 0, len(fc), 0)
    check("FCRL3_nonreturn_boundary_present", "not proof" in coverage.loc[coverage.gene == "FCRL3", "interpretation_boundary"].iloc[0], coverage.loc[coverage.gene == "FCRL3", "interpretation_boundary"].iloc[0], "contains not proof")
    check("IL12RB2_peak_NK_caqtl_q", float(cascade.peak_caqtl_q_l1_NK.iloc[0]) < 0.05 and float(cascade.peak_caqtl_q_l2_NK.iloc[0]) < 0.05, cascade[["peak_caqtl_q_l1_NK", "peak_caqtl_q_l2_NK"]].iloc[0].to_dict(), "both <0.05")
    check("positional_not_full_cascade", not bool(cascade.complete_variant_level_cascade_supported.iloc[0]), bool(cascade.complete_variant_level_cascade_supported.iloc[0]), False)
    il_dir = directions[(directions.axis == "IL12RB2–NK") & directions.eligible_for_shared_signal_direction.astype(bool)]
    check("IL12_direction_all_higher", set(il_dir.risk_allele_expression_direction) == {"HIGHER"}, sorted(il_dir.risk_allele_expression_direction.unique()), ["HIGHER"])
    check("IL12_direction_three_resource_families", il_dir.resource.nunique() == 3, il_dir.resource.nunique(), 3)
    f_dir = directions[directions.axis.isin(["FCRL3–B_IN", "FCRL3–B_MEM", "FCRL3–B"]) & directions.eligible_for_shared_signal_direction.astype(bool)]
    check("FCRL3_B_direction_all_lower", set(f_dir.risk_allele_expression_direction) == {"LOWER"}, sorted(f_dir.risk_allele_expression_direction.unique()), ["LOWER"])
    cd8 = directions[directions.axis == "FCRL3–CD8_ET"]
    check("CD8_direction_not_eligible", len(cd8) == 1 and not bool(cd8.eligible_for_shared_signal_direction.iloc[0]), cd8.eligible_for_shared_signal_direction.tolist(), [False])
    check("axis_adjudication_exact_3", len(final) == 3, len(final), 3)
    check("G6_pass_bounded", state["G6_EXTERNAL_REPLICATION"] == "PASS_BOUNDED", state["G6_EXTERNAL_REPLICATION"], "PASS_BOUNDED")
    check("next_stage_frozen", state["next"] == "R7B1E_INTEGRATED_CLAIM_EVIDENCE_FREEZE_AND_FIGURE_SOURCE_ASSEMBLY", state["next"], "R7B1E...")
    figure_ok = all((FIG / f"R7B1D_external_evidence_overview.{x}").exists() for x in ["png", "pdf", "svg"])
    check("figure_three_formats", figure_ok, figure_ok, True)

    passed = sum(x["pass"] for x in checks)
    result = {
        "schema": "R7B1D_QA_1.0",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }
    (OUT / "R7B1D_independent_QA.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(checks).to_csv(OUT / "R7B1D_independent_QA.tsv", sep="\t", index=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
