#!/usr/bin/env python3
"""Adjudicate bounded TenK/FinnGen external evidence and allele direction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "3_results/01_intake/R7B1D/finngen_cascade_20261009"
OUT = ROOT / "3_results/04_integration/R7B1D"
QTL = ROOT / "3_results/03_qtl/R7B1B_v2/dualmodel_qtl"
TENK = ROOT / "3_results/04_integration/R7A1C"
R7B0_RAW = ROOT / "3_results/01_intake/R7B0/finngen_cascade"


def load(name: str):
    return json.loads((RAW / f"{name}.json").read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assoc_frame(payload: dict, ensg: str, cell: str) -> pd.DataFrame:
    obj = payload["traits"][ensg]["cts"][cell]["assoc"]
    return pd.DataFrame({k: v for k, v in obj.items() if k != "ann"})


def direction_row(
    *, axis: str, resource: str, cell: str, variant: str, build: str,
    ref: str, alt: str, disease_beta_alt: float, qtl_effect_allele: str,
    qtl_beta: float, eligible: bool, boundary: str,
) -> dict:
    risk = alt if disease_beta_alt > 0 else ref
    if qtl_effect_allele == risk:
        risk_beta = qtl_beta
    elif qtl_effect_allele == (ref if risk == alt else alt):
        risk_beta = -qtl_beta
    else:
        raise RuntimeError(f"Allele mismatch for {resource} {variant}")
    return {
        "axis": axis,
        "resource": resource,
        "cell": cell,
        "variant": variant,
        "build": build,
        "ref": ref,
        "alt": alt,
        "disease_effect_allele": alt,
        "disease_beta_effect_allele": disease_beta_alt,
        "risk_allele": risk,
        "qtl_effect_allele": qtl_effect_allele,
        "qtl_beta_effect_allele": qtl_beta,
        "risk_allele_expression_beta": risk_beta,
        "risk_allele_expression_direction": "HIGHER" if risk_beta > 0 else "LOWER",
        "eligible_for_shared_signal_direction": eligible,
        "boundary": boundary,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    target = pd.read_csv(OUT / "R7B1D_external_target_registry.tsv", sep="\t")

    # Phenotype identity is a hard gate.
    phenos = load("phenos_pbc")["phenos"]
    pbc = [x for x in phenos if x["phenocode"] == "CHIRBIL_PRIM"]
    phenotype_metadata_source = "R7B1D_CURRENT_SEARCH"
    if len(pbc) != 1:
        # The public phenotype search index intermittently returns an empty set while
        # direct autocomplete, Manhattan, regional GWAS and coloc endpoints remain live.
        # Use the previously frozen public metadata only for case/control counts.
        prior = json.loads((R7B0_RAW / "phenos_pbc.response").read_text(encoding="utf-8"))
        pbc = [x for x in prior["phenos"] if x["phenocode"] == "CHIRBIL_PRIM"]
        phenotype_metadata_source = "R7B0_FROZEN_PUBLIC_METADATA__CURRENT_SEARCH_INDEX_EMPTY"
    suggestions = load("autocomplete_pbc_phenotype").get("suggestions", [])
    if not any(x.get("value") == "CHIRBIL_PRIM" for x in suggestions):
        raise RuntimeError("Current autocomplete does not confirm CHIRBIL_PRIM identity")
    if not load("manhattan_pbc").get("variant_bins"):
        raise RuntimeError("Current CHIRBIL_PRIM Manhattan endpoint is empty")

    # Current public disease–eQTL colocalization records.
    coloc_sets = []
    for name, gene in [
        ("coloc_il12rb2_variant1", "IL12RB2"),
        ("coloc_il12rb2_variant2", "IL12RB2"),
        ("coloc_fcrl3_marginal", "FCRL3"),
        ("coloc_fcrl3_anchor", "FCRL3"),
        ("coloc_fcrl3_region", "FCRL3"),
    ]:
        rows = load(name).get("pairs", [])
        if rows:
            frame = pd.DataFrame(rows)
            frame["query_name"] = name
            frame["query_gene"] = gene
            coloc_sets.append(frame)
    coloc_all = pd.concat(coloc_sets, ignore_index=True, sort=False)
    pbc_rows = coloc_all[
        (coloc_all["trait1"].astype(str) == "CHIRBIL_PRIM")
        & (coloc_all["trait2_symbol"].astype(str).isin(["IL12RB2", "FCRL3"]))
    ].copy()
    dedupe = [
        "trait1", "dataset2", "trait2_symbol", "cell_type2", "cs1_id", "cs2_id",
        "hit1", "hit2",
    ]
    pbc_unique = pbc_rows.sort_values("query_name").drop_duplicates(dedupe).reset_index(drop=True)
    pbc_unique.to_csv(OUT / "R7B1D_FinnGen_PBC_molQTL_coloc.tsv", sep="\t", index=False)

    coverage = []
    for gene, names in {
        "IL12RB2": ["coloc_il12rb2_variant1", "coloc_il12rb2_variant2"],
        "FCRL3": ["coloc_fcrl3_marginal", "coloc_fcrl3_anchor", "coloc_fcrl3_region"],
    }.items():
        queried = coloc_all[coloc_all.query_name.isin(names)]
        hits = pbc_unique[pbc_unique.trait2_symbol == gene]
        coverage.append({
            "gene": gene,
            "queried_pair_rows_before_dedup": len(queried),
            "queried_unique_traits": queried.trait1.astype(str).nunique(),
            "PBC_CHIRBIL_PRIM_rows": len(hits),
            "PBC_cell_types": ";".join(sorted(hits.cell_type2.dropna().astype(str).unique())),
            "public_output_adjudication": "PBC_COLOC_RETURNED" if len(hits) else "NO_PBC_COLOC_RETURNED",
            "interpretation_boundary": (
                "Direct public PBC disease–eQTL aggregate support"
                if len(hits) else
                "Public-output non-return; not proof of biological absence or a formally powered negative test"
            ),
        })
    coverage_df = pd.DataFrame(coverage)
    coverage_df.to_csv(OUT / "R7B1D_FinnGen_coloc_coverage.tsv", sep="\t", index=False)

    # Frozen cell-map molecular coverage.
    genes = {"IL12RB2": load("gene_il12rb2"), "FCRL3": load("gene_fcrl3")}
    map_rows = []
    for row in target.itertuples(index=False):
        gene = genes[row.gene]
        primary = row.FinnGen_primary
        compatible = str(row.FinnGen_compatible).split(";") if pd.notna(row.FinnGen_compatible) else []
        for map_role, cells in [("PRIMARY", [primary]), ("COMPATIBLE", compatible)]:
            for cell in cells:
                eq = gene.get("eqtl_q", {}).get(cell)
                ca = gene.get("caqtl_q", {}).get(cell)
                map_rows.append({
                    "comparison_id": row.comparison_id,
                    "axis": row.axis,
                    "gene": row.gene,
                    "OneK_cell": row.cell_type,
                    "mapping_role": map_role,
                    "FinnGen_cell": cell,
                    "eqtl_q": eq,
                    "caqtl_q": ca,
                    "eqtl_available": eq is not None,
                    "caqtl_available": ca is not None,
                    "eqtl_q_lt_0_05": eq is not None and float(eq) < 0.05,
                    "caqtl_q_lt_0_05": ca is not None and float(ca) < 0.05,
                })
    cell_map = pd.DataFrame(map_rows)
    cell_map.to_csv(OUT / "R7B1D_FinnGen_regulatory_cell_map.tsv", sep="\t", index=False)

    # IL12RB2 positional cascade and linked-peak layer.
    il12 = genes["IL12RB2"]
    peak = load("peak_il12rb2_anchor")
    il12_link = [x for x in peak["linked_genes"] if x["gene"] == "IL12RB2"]
    if len(il12_link) != 1:
        raise RuntimeError("IL12RB2 linked-peak identity is not unique")
    cascade_variant = [x for x in il12["top_variants"] if x["variant_id"] == "chr1_67307966_T_C"]
    if len(cascade_variant) != 1:
        raise RuntimeError("Expected IL12RB2 positional-cascade variant not found")
    pv = peak["top_variants"][0]
    cascade = pd.DataFrame([{
        "gene": "IL12RB2",
        "variant": cascade_variant[0]["variant_id"],
        "variant_mechanism": cascade_variant[0]["pattern_label"],
        "variant_eQTL_PIP_max": cascade_variant[0]["pip_max"],
        "peak": peak["peak"]["id"],
        "peak_gene_link_method": peak["peak"]["link_method"],
        "peak_gene_link_beta": il12_link[0]["link_beta"],
        "peak_caqtl_q_l1_NK": peak["ca_q"].get("l1.NK"),
        "peak_caqtl_q_l2_NK": peak["ca_q"].get("l2.NK"),
        "variant_in_peak": bool(pv.get("overlap")),
        "variant_in_peak_caqtl_CS": bool(pv.get("in_cs")),
        "complete_variant_level_cascade_supported": False,
        "boundary": "CASCADE positional overlap/link; the eQTL variant is not in the peak caQTL credible set, and PBC–caQTL colocalization is not established",
    }])
    cascade.to_csv(OUT / "R7B1D_IL12RB2_FinnGen_positional_cascade.tsv", sep="\t", index=False)

    # Exact-allele risk-expression direction map.
    directions = []
    il12_tenk = pd.read_csv(TENK / "R7A1C_IL12RB2_TenK_NK_fullPBC_overlap.tsv.gz", sep="\t")
    il12_anchor = il12_tenk.loc[il12_tenk.pos38 == 67354511].iloc[0]
    one_il12 = pd.read_csv(QTL / "R7B1_000258_PF10_QTL.tsv.gz", sep="\t")
    one_il12_anchor = one_il12.loc[one_il12.position_GRCh37 == 67820194].iloc[0]
    directions.append(direction_row(
        axis="IL12RB2–NK", resource="OneK1K_PF10", cell="NK", variant="rs6679356",
        build="GRCh37", ref="C", alt="T", disease_beta_alt=float(il12_anchor.disease_beta_ALT),
        qtl_effect_allele=str(one_il12_anchor.BIM_A1), qtl_beta=float(one_il12_anchor.slope_A1),
        eligible=True, boundary="GJOKA disease GWAS plus source-matched OneK multi-signal stable H4",
    ))
    directions.append(direction_row(
        axis="IL12RB2–NK", resource="TenK10K", cell="NK", variant="rs6679356",
        build="GRCh38", ref="C", alt="T", disease_beta_alt=float(il12_anchor.disease_beta_ALT),
        qtl_effect_allele="T", qtl_beta=float(il12_anchor.qtl_beta_ALT), eligible=True,
        boundary="Same GJOKA disease GWAS; independent molecular-QTL resource; single-causal analysis",
    ))

    fg_gwas_il12 = pd.DataFrame(load("gwas_pbc_il12rb2_region")["data"])
    fg_eqtl_il12 = load("eqtl_il12rb2_nk")
    for cell in ["l1.NK", "l2.NK"]:
        q = assoc_frame(fg_eqtl_il12, "ENSG00000081985", cell)
        merged = fg_gwas_il12.merge(q, on=["position", "ref", "alt"], suffixes=("_gwas", "_qtl"))
        for pos, label in [(67336688, "rs6659932"), (67354511, "rs6679356")]:
            hit = merged.loc[merged.position == pos]
            if len(hit) != 1:
                raise RuntimeError(f"FinnGen exact direction anchor missing: {cell} {pos}")
            x = hit.iloc[0]
            directions.append(direction_row(
                axis="IL12RB2–NK", resource="FinnGen_R12_multiome", cell=cell, variant=label,
                build="GRCh38", ref=str(x.ref), alt=str(x.alt), disease_beta_alt=float(x.beta_gwas),
                qtl_effect_allele=str(x.alt), qtl_beta=float(x.beta_qtl), eligible=True,
                boundary="Exact-allele FinnGen PBC GWAS–eQTL direction within a public PBC coloc credible-set pair",
            ))

    fcr_tenk = pd.read_csv(TENK / "R7A1C_FCRL3_TenK_Bintermediate_fullPBC_overlap.tsv.gz", sep="\t")
    fcr_anchor = fcr_tenk.loc[fcr_tenk.rsid == "rs3761959"].iloc[0]
    for cid, cell, eligible in [
        ("R7B1_000410", "B_IN", True),
        ("R7B1_000411", "B_MEM", True),
        ("R7B1_000414", "CD8_ET", False),
    ]:
        one = pd.read_csv(QTL / f"{cid}_PF10_QTL.tsv.gz", sep="\t")
        x = one.loc[one.position_GRCh37 == 157669278].iloc[0]
        directions.append(direction_row(
            axis=f"FCRL3–{cell}", resource="OneK1K_PF10", cell=cell, variant="rs3761959",
            build="GRCh37", ref="C", alt="T", disease_beta_alt=float(fcr_anchor.disease_beta_ALT),
            qtl_effect_allele=str(x.BIM_A1), qtl_beta=float(x.slope_A1), eligible=eligible,
            boundary=(
                "GJOKA disease GWAS plus source-matched OneK stable H4"
                if eligible else
                "Direction is descriptive only because PF10 source-matched multi-signal adjudication favors H3"
            ),
        ))
    directions.append(direction_row(
        axis="FCRL3–B", resource="TenK10K", cell="B_intermediate", variant="rs3761959",
        build="GRCh38", ref="C", alt="T", disease_beta_alt=float(fcr_anchor.disease_beta_ALT),
        qtl_effect_allele="T", qtl_beta=float(fcr_anchor.qtl_beta_ALT), eligible=True,
        boundary="Same GJOKA disease GWAS; independent molecular-QTL resource; single-causal analysis",
    ))
    direction_df = pd.DataFrame(directions)
    direction_df.to_csv(OUT / "R7B1D_risk_allele_expression_direction.tsv", sep="\t", index=False)

    direction_summary = pd.DataFrame([
        {
            "axis": "IL12RB2–NK",
            "eligible_resources": 4,
            "resource_families": 3,
            "direction": "PBC risk allele associated with HIGHER IL12RB2 expression",
            "concordance": "CONCORDANT_ONEK_TENK_FINNGEN",
            "boundary": "Association/direction only; not mediation",
        },
        {
            "axis": "FCRL3–B",
            "eligible_resources": 3,
            "resource_families": 2,
            "direction": "PBC risk allele associated with LOWER FCRL3 expression",
            "concordance": "CONCORDANT_ONEK_TENK__FINNGEN_PBC_DIRECTION_UNAVAILABLE",
            "boundary": "FinnGen public PBC–FCRL3 coloc was not returned",
        },
        {
            "axis": "FCRL3–CD8_ET",
            "eligible_resources": 0,
            "resource_families": 0,
            "direction": "NOT_INTERPRETABLE_AS_SHARED_SIGNAL",
            "concordance": "NOT_APPLICABLE_H3_RECLASSIFICATION",
            "boundary": "A QTL effect direction does not rescue a distinct-signal result",
        },
    ])
    direction_summary.to_csv(OUT / "R7B1D_direction_summary.tsv", sep="\t", index=False)

    il12_coloc = pbc_unique[pbc_unique.trait2_symbol == "IL12RB2"]
    fcr_coloc = pbc_unique[pbc_unique.trait2_symbol == "FCRL3"]
    final = pd.DataFrame([
        {
            "axis": "IL12RB2–NK",
            "OneK_multisignal": "STABLE_H4",
            "TenK_molecular": "PASS_SINGLE_CAUSAL_WITH_SOURCE_CS_CAVEAT",
            "FinnGen_PBC_eQTL": f"PASS_{len(il12_coloc)}_CELL_RECORDS",
            "FinnGen_chromatin": "POSITIONAL_CASCADE_LINKED_PEAK__NOT_FULL_VARIANT_CAUSAL_CHAIN",
            "direction": "RISK_ALLELE_HIGHER_EXPRESSION__3_RESOURCE_FAMILIES",
            "final_state": "PASS_EXTERNAL_DISEASE_AND_MULTIOME_SUPPORT_BOUNDED",
            "allowed_claim": "Stable IL12RB2–NK sharing recurs across molecular-QTL resources and in FinnGen PBC–eQTL aggregate output, with a linked positional chromatin layer",
            "forbidden_claim": "IL12RB2 expression mediates PBC or a complete disease→caQTL→expression causal cascade is proven",
        },
        {
            "axis": "FCRL3–B",
            "OneK_multisignal": "STABLE_H4_B_IN_AND_B_MEM",
            "TenK_molecular": "PASS_B_INTERMEDIATE_SINGLE_CAUSAL",
            "FinnGen_PBC_eQTL": f"NO_PBC_COLOC_RETURNED_{len(fcr_coloc)}",
            "FinnGen_chromatin": "NO_GENE_LEVEL_CASCADE_TOP_VARIANT",
            "direction": "RISK_ALLELE_LOWER_EXPRESSION__ONEK_TENK",
            "final_state": "PASS_CROSS_QTL_RESOURCE__FINNGEN_DISEASE_LAYER_UNAVAILABLE",
            "allowed_claim": "FCRL3 B-cell sharing is stable in OneK and reproduced in TenK with concordant allele direction",
            "forbidden_claim": "FinnGen independently confirms PBC–FCRL3 colocalization or mechanism",
        },
        {
            "axis": "FCRL3–CD8_ET",
            "OneK_multisignal": "PF10_H3_SUPPORTED__PF10_PF50_SENSITIVE",
            "TenK_molecular": "NOT_PRESPECIFIED",
            "FinnGen_PBC_eQTL": f"NO_PBC_COLOC_RETURNED_{len(fcr_coloc)}",
            "FinnGen_chromatin": "NO_GENE_LEVEL_CASCADE_TOP_VARIANT",
            "direction": "NOT_INTERPRETABLE_AS_SHARED_SIGNAL",
            "final_state": "NEGATIVE_CONTROL_RETAINS_H3_NO_EXTERNAL_RESCUE",
            "allowed_claim": "The CD8_ET assignment remains a source-model-sensitive falsification exemplar",
            "forbidden_claim": "Strong FCRL3 eQTL alone establishes a shared PBC signal in CD8 effector cells",
        },
    ])
    final.to_csv(OUT / "R7B1D_external_axis_adjudication.tsv", sep="\t", index=False)

    state = {
        "schema": "R7B1D_EXTERNAL_GATE_1.0",
        "status": "COMPLETE",
        "phenotype": pbc[0],
        "phenotype_metadata_source": phenotype_metadata_source,
        "current_phenotype_search_rows": len(phenos),
        "current_autocomplete_identity": "CHIRBIL_PRIM",
        "target_count": len(target),
        "FinnGen_PBC_IL12RB2_coloc_records": len(il12_coloc),
        "FinnGen_PBC_FCRL3_coloc_records": len(fcr_coloc),
        "IL12RB2_PP_H4_range": [float(il12_coloc["PP.H4.abf"].min()), float(il12_coloc["PP.H4.abf"].max())],
        "IL12RB2_CS_overlap_range": [int(il12_coloc.cs_overlap.min()), int(il12_coloc.cs_overlap.max())],
        "G6_EXTERNAL_REPLICATION": "PASS_BOUNDED",
        "G6_basis": [
            "IL12RB2–NK stable OneK multi-signal result",
            "IL12RB2–NK TenK molecular-QTL replication",
            "Three FinnGen R12 CHIRBIL_PRIM–IL12RB2 eQTL coloc records",
            "FinnGen positional linked-peak chromatin layer with explicit non-causal-chain boundary",
            "FCRL3 B-cell OneK–TenK replication with concordant allele direction",
        ],
        "general_method_superiority": "NOT_ESTABLISHED_BY_R7B1C_SIMULATION",
        "project": "RETAIN_PBC__EVIDENCE_INTEGRATION_GO",
        "next": "R7B1E_INTEGRATED_CLAIM_EVIDENCE_FREEZE_AND_FIGURE_SOURCE_ASSEMBLY",
        "outputs": {},
    }
    for path in sorted(OUT.glob("R7B1D_*.tsv")):
        state["outputs"][path.name] = {"rows": len(pd.read_csv(path, sep="\t")), "sha256": sha256(path)}
    (OUT / "R7B1D_external_gate_state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
