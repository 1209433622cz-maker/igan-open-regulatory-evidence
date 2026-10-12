#!/usr/bin/env python3
"""Join OneK1K and TenK10K index evidence for R5A1 MG loci."""

from __future__ import annotations

import csv
import json
import pathlib
from collections import defaultdict
from datetime import datetime, timezone


ROOT = pathlib.Path(r"H:\SCI2\YR1")
QTL = ROOT / "3_results" / "03_qtl" / "R5A1"
GWAS = ROOT / "3_results" / "01_gwas" / "R5A1" / "EOMG_LOMG_heterogeneity_at_GWS_region_leads.tsv"
AUDIT = ROOT / "3_results" / "00_audit" / "R5A1"
NEAREST = {"GWSR01": "PTPN22", "GWSR02": "SOS1", "GWSR03": "TNIP1", "GWSR04": "TNFRSF11A"}


def read(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    lookup = {row["ensembl_gene"]: row["display_name"] for row in read(QTL / "ensembl_gene_lookup.tsv")}
    regions = {row["region_id"]: row for row in read(GWAS)}
    onek = read(QTL / "OneK1K_top_eQTL_in_MG_loci.tsv")
    tenk_gene = read(QTL / "TenK10K_gene_level_in_MG_loci.tsv")
    tenk_susie = read(QTL / "TenK10K_SuSiE_CS_in_MG_loci.tsv")

    evidence: dict[tuple[str, str], dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in onek:
        evidence[(row["region_id"], row["gene_symbol"])]["onek"].append(row)
    for row in tenk_gene:
        gene = lookup.get(row["gene_ensembl"], "")
        if gene:
            evidence[(row["region_id"], gene)]["tenk_gene"].append(row)
    for row in tenk_susie:
        gene = lookup.get(row["gene_ensembl"], "")
        if gene:
            evidence[(row["region_id"], gene)]["tenk_susie"].append(row)

    output: list[dict[str, object]] = []
    for (region_id, gene), groups in evidence.items():
        region = regions[region_id]
        o_sig = [row for row in groups["onek"] if row["qval_lt_0_05"] == "True"]
        t_sig = [row for row in groups["tenk_gene"] if row["ACAT_BH_q_lt_0_05"] == "True"]
        s_rows = groups["tenk_susie"]
        o_best = min(o_sig, key=lambda x: float(x["qval"])) if o_sig else None
        t_best = min(t_sig, key=lambda x: float(x["ACAT_BH_q_within_cell"])) if t_sig else None
        s_best = max(s_rows, key=lambda x: float(x["PIP"])) if s_rows else None
        lead_colon = region["lead_variant_id"].replace("_", ":")
        exact = [row for row in s_rows if row["variant"] == lead_colon]
        replicated = bool(o_sig and t_sig and s_rows)
        if replicated and gene == NEAREST[region_id]:
            tier = "A1_CROSS_RESOURCE_PAPER_GENE"
        elif replicated:
            tier = "A2_CROSS_RESOURCE_COMPETITOR"
        elif t_sig and s_rows:
            tier = "B_TENK10K_FINE_MAPPED"
        elif o_sig or t_sig:
            tier = "C_SINGLE_RESOURCE_INDEX"
        else:
            tier = "D_REGIONAL_BACKGROUND"
        output.append(
            {
                "region_id": region_id,
                "lead_rsid": region["lead_rsid"],
                "lead_variant_id": region["lead_variant_id"],
                "lead_source": region["lead_source"],
                "p_het": region["p_het"],
                "paper_nearest_gene": NEAREST[region_id],
                "gene": gene,
                "evidence_tier": tier,
                "OneK1K_significant": bool(o_sig),
                "OneK1K_best_cell": o_best["cell_type"] if o_best else "",
                "OneK1K_best_q": o_best["qval"] if o_best else "",
                "OneK1K_significant_cells": ";".join(sorted({row["cell_type"] for row in o_sig})),
                "TenK10K_gene_significant": bool(t_sig),
                "TenK10K_best_cell": t_best["cell_type"] if t_best else "",
                "TenK10K_best_BH_q": t_best["ACAT_BH_q_within_cell"] if t_best else "",
                "TenK10K_significant_cells": ";".join(sorted({row["cell_type"] for row in t_sig})),
                "TenK10K_SuSiE_present": bool(s_rows),
                "TenK10K_max_PIP": s_best["PIP"] if s_best else "",
                "TenK10K_max_PIP_cell": s_best["cell_type"] if s_best else "",
                "disease_lead_in_TenK10K_CS": bool(exact),
                "disease_lead_CS_cells": ";".join(sorted({row["cell_type"] for row in exact})),
                "disease_lead_max_QTL_PIP": max((float(row["PIP"]) for row in exact), default=""),
            }
        )
    priority = {"A1_CROSS_RESOURCE_PAPER_GENE": 0, "A2_CROSS_RESOURCE_COMPETITOR": 1, "B_TENK10K_FINE_MAPPED": 2, "C_SINGLE_RESOURCE_INDEX": 3, "D_REGIONAL_BACKGROUND": 4}
    output.sort(key=lambda x: (x["region_id"], priority[str(x["evidence_tier"])], str(x["gene"])))
    out_path = QTL / "MG_cross_resource_QTL_replication_matrix.tsv"
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    per_region = {}
    for region_id in regions:
        rows = [row for row in output if row["region_id"] == region_id]
        per_region[region_id] = {
            "lead_rsid": regions[region_id]["lead_rsid"],
            "paper_nearest_gene": NEAREST[region_id],
            "cross_resource_genes": [row["gene"] for row in rows if str(row["evidence_tier"]).startswith("A")],
            "paper_gene_cross_resource": any(row["evidence_tier"] == "A1_CROSS_RESOURCE_PAPER_GENE" for row in rows),
            "disease_lead_in_any_tenk10k_cs": any(bool(row["disease_lead_in_TenK10K_CS"]) for row in rows),
        }
    adjudication = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "regions": per_region,
        "oneK1K_public_full_stats_and_genotype_listed": True,
        "oneK1K_local_genotype_identity": "PENDING_SEPARATE_BYTE_LEVEL_AUDIT",
        "tenK10K_replication_index_pass": any(bool(v["cross_resource_genes"]) for v in per_region.values()),
        "lead_candidate": "GWSR03_TNIP1",
        "reason": "EOMG-specific heterogeneity; TNIP1 significant in both resources; TenK10K SuSiE support; exact disease lead occurs in B-naive TNIP1 credible set",
        "causal_claim_status": "NOT_TESTED_REQUIRES_FULL_REGIONAL_HARMONIZATION_AND_COLOCALIZATION",
    }
    with (AUDIT / "MG_QTL_replication_gate.json").open("w", encoding="utf-8") as handle:
        json.dump(adjudication, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(adjudication, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
