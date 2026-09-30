#!/usr/bin/env python3
"""Freeze the R7A2A1 result and the R7A2A2 manuscript claim ladder."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else r"H:\SCI2\YR1")
    out_dir = root / "3_results/04_integration/R7A2A1"
    out_dir.mkdir(parents=True, exist_ok=True)
    one_k = json.loads((root / "3_results/04_integration/R7A1B/R7A1B_final_adjudication.json").read_text(encoding="utf-8-sig"))
    tissue_pbc = json.loads((root / "3_results/05_tissue/R7A1C1/R7A1C1_liver_final_adjudication_v2.json").read_text(encoding="utf-8-sig"))
    tissue_comparison = json.loads((root / "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel.json").read_text(encoding="utf-8-sig"))
    qa = json.loads((root / "3_results/00_audit/R7A2A1/R7A2A1_independent_QA.json").read_text(encoding="utf-8-sig"))
    fcrl3_tenk = json.loads((root / "3_results/04_integration/R7A1C/R7A1C_FCRL3_TenK_Bintermediate_result.json").read_text(encoding="utf-8-sig"))
    with (root / "3_results/04_integration/R7A1C/R7A1C_IL12RB2_TenK_NK_fullPBC_coloc.tsv").open("r", encoding="utf-8-sig", newline="") as handle:
        il12_rows = list(csv.DictReader(handle, delimiter="\t"))
    il12_default = next(row for row in il12_rows if float(row["p12"]) == 1e-5)
    fcrl3_default = next(row for row in fcrl3_tenk["posterior"] if float(row["p12"]) == 1e-5)
    one_k_by_gene = {row["gene"]: row for row in one_k["gene_results"]}

    tissue_targets = tissue_comparison["comparisons"]
    tissue_significant = [target for target, values in tissue_targets.items() if values["BH_q_two_prespecified_targets"] < 0.05]
    upstream_pass = (
        one_k["signal_specific_pass_genes"] == 2
        and fcrl3_tenk["status"].startswith("PASS")
        and float(il12_default["PP_H4"]) >= 0.8
        and tissue_pbc["promotion_gate"] == "PASS"
        and qa["status"] == "PASS"
    )
    result = {
        "schema": "R7A2A1_FINAL_ADJUDICATION_1.0",
        "date": "2026-09-30",
        "R7A2A1_execution": "COMPLETE",
        "technical_closeout": {
            "control_donors": 5,
            "control_total_bytes": 134657112757,
            "control_QC": "PASS_5_OF_5",
            "independent_QA": f"PASS_{qa['checks_passed']}_OF_{qa['checks_total']}",
            "control_bam_cache": "EMPTY_AFTER_VALIDATED_COMPACT_OUTPUT",
        },
        "tissue_result": {
            "FCRL3_B": tissue_targets["FCRL3_B"],
            "IL12RB2_NK": tissue_targets["IL12RB2_NK"],
            "targets_with_BH_q_below_0_05": tissue_significant,
            "target_detectability": "BOTH_TARGETS_DETECTED_IN_5_OF_5_PBC_AND_5_OF_5_CONTROLS",
            "disease_specific_enrichment": "NOT_SUPPORTED",
            "interpretation": "FCRL3 is directionally lower in PBC; IL12RB2 is directionally higher but does not pass correction. The bounded marker panel supports lineage localization, not PBC-specific upregulation.",
        },
        "upstream_chain": {
            "OneK_signal_specific_shared_genes": 2,
            "FCRL3_OneK_best_PP_H4": one_k_by_gene["FCRL3"]["best_signal_PP_H4"],
            "IL12RB2_OneK_best_PP_H4": one_k_by_gene["IL12RB2"]["best_signal_PP_H4"],
            "FCRL3_TenK_B_intermediate_default_PP_H4": fcrl3_default["PP_H4"],
            "IL12RB2_TenK_NK_default_PP_H4": float(il12_default["PP_H4"]),
            "PBC_liver_detectability": "PASS_5_OF_5_BOTH_TARGETS",
        },
        "project_decision": "GO_R7A2A2_MANUSCRIPT_EVIDENCE_FREEZE" if upstream_pass else "HOLD",
        "claim_ceiling": "Replicated disease-eQTL signal sharing for FCRL3 and IL12RB2, with detection in their prespecified PBC liver immune-lineage gates.",
        "prohibited_claims": [
            "PBC-specific upregulation of FCRL3 or IL12RB2",
            "causal liver-tissue mediation",
            "cell-state differential expression from the bounded marker panel",
        ],
        "full_ten_donor_reclustering": "DEFERRED_OPTIONAL_NOT_REQUIRED_FOR_CORE_CLAIM",
        "next_stage": "R7A2A2_MANUSCRIPT_EVIDENCE_FREEZE_AND_FIGURE_ASSEMBLY",
    }
    (out_dir / "R7A2A1_final_adjudication.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    rows = [
        {
            "evidence_layer": "OneK1K_source_LD_signal_specific",
            "gene_axis": "FCRL3",
            "result": f"PP.H4={one_k_by_gene['FCRL3']['best_signal_PP_H4']:.6f}; stable cells={one_k_by_gene['FCRL3']['stable_pass_cells']}",
            "status": "PASS",
            "allowed_use": "primary genetic-regulatory result",
        },
        {
            "evidence_layer": "OneK1K_source_LD_signal_specific",
            "gene_axis": "IL12RB2",
            "result": f"PP.H4={one_k_by_gene['IL12RB2']['best_signal_PP_H4']:.6f}; stable cell=NK",
            "status": "PASS",
            "allowed_use": "primary genetic-regulatory result",
        },
        {
            "evidence_layer": "TenK10K_independent_replication",
            "gene_axis": "FCRL3_B_intermediate",
            "result": f"n={fcrl3_tenk['exact_overlap_n']}; default PP.H4={fcrl3_default['PP_H4']:.6f}; low-prior H4/(H3+H4)={fcrl3_tenk['posterior'][0]['H4_over_H3H4']:.6f}",
            "status": "PASS",
            "allowed_use": "cross-resource replication",
        },
        {
            "evidence_layer": "TenK10K_independent_replication",
            "gene_axis": "IL12RB2_NK",
            "result": f"n={il12_default['n']}; default PP.H4={float(il12_default['PP_H4']):.6f}; low-prior H4/(H3+H4)={float(il12_rows[0]['H4_over_H3H4']):.6f}",
            "status": "PASS",
            "allowed_use": "cross-resource replication",
        },
        {
            "evidence_layer": "HRA008003_PBC_liver_detectability",
            "gene_axis": "FCRL3_B + IL12RB2_NK",
            "result": "both target-lineage pairs promotion-eligible in 5/5 PBC donors",
            "status": "PASS",
            "allowed_use": "disease-tissue lineage localization",
        },
        {
            "evidence_layer": "HRA008003_exact_5_vs_5",
            "gene_axis": "FCRL3_B",
            "result": f"PBC-control log1p CPM difference={tissue_targets['FCRL3_B']['mean_log1p_CPM_difference_PBC_minus_control']:.6f}; P={tissue_targets['FCRL3_B']['exact_label_permutation_p']:.6f}; q={tissue_targets['FCRL3_B']['BH_q_two_prespecified_targets']:.6f}",
            "status": "NO_ENRICHMENT",
            "allowed_use": "report null case-control support and direction",
        },
        {
            "evidence_layer": "HRA008003_exact_5_vs_5",
            "gene_axis": "IL12RB2_NK",
            "result": f"PBC-control log1p CPM difference={tissue_targets['IL12RB2_NK']['mean_log1p_CPM_difference_PBC_minus_control']:.6f}; P={tissue_targets['IL12RB2_NK']['exact_label_permutation_p']:.6f}; q={tissue_targets['IL12RB2_NK']['BH_q_two_prespecified_targets']:.6f}",
            "status": "SUGGESTIVE_DIRECTION_ONLY",
            "allowed_use": "report null corrected result and direction",
        },
    ]
    columns = ["evidence_layer", "gene_axis", "result", "status", "allowed_use"]
    with (out_dir / "R7A2A2_claim_evidence_matrix.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if upstream_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
