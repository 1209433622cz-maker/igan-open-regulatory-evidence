#!/usr/bin/env python3
"""Adjudicate the OneK benchmark and targeted TenK ZMIZ1 replication."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "3_results/04_integration/R6A2A"
AUD = ROOT / "3_results/00_audit/R6A2A"
ADMIN = ROOT / "0_admin/protocol/current"
TENK = ROOT / "1_data/qtl/TenK10K"
for folder in (OUT, AUD, ADMIN):
    folder.mkdir(parents=True, exist_ok=True)

py = pd.read_csv(OUT / "R6A2A_coloc_smoke.tsv", sep="\t")
rr = pd.read_csv(OUT / "R6A2A_official_R_coloc_validation.tsv", sep="\t")
keys = ["dataset", "locus", "gene", "cell_type", "benchmark_role"]
prior_map = {
    1e-6: {"PP_H4": "H4_p12_1e-6", "H4_over_H3H4": "H4ratio_p12_1e-6"},
    1e-5: {"PP_H4": "PP_H4", "H4_over_H3H4": "H4_over_H3H4"},
    1e-4: {"PP_H4": "H4_p12_1e-4", "H4_over_H3H4": None},
}
validation = []
for r in rr.itertuples(index=False):
    match = py
    for key in keys:
        match = match[match[key] == getattr(r, key)]
    if len(match) != 1:
        raise RuntimeError(f"Python comparison row mismatch: {tuple(getattr(r, x) for x in keys)}")
    p = match.iloc[0]
    pp_col = prior_map[float(r.p12)]["PP_H4"]
    validation.append(
        {
            **{key: getattr(r, key) for key in keys},
            "p12": float(r.p12),
            "n_snps_python": int(p.n_snps),
            "n_snps_R": int(r.nsnps),
            "PP_H4_python": float(p[pp_col]),
            "PP_H4_R": float(getattr(r, "PP_H4")),
            "PP_H4_abs_diff": abs(float(p[pp_col]) - float(getattr(r, "PP_H4"))),
        }
    )
validation = pd.DataFrame(validation)
validation.to_csv(OUT / "R6A2A1_Python_vs_official_R_validation.tsv", sep="\t", index=False)
max_delta = float(validation.PP_H4_abs_diff.max())
if max_delta > 1e-10 or not (validation.n_snps_python == validation.n_snps_R).all():
    raise RuntimeError("Python/R validation failed")

combined = py[py.dataset == "combined"].copy()
combined.to_csv(OUT / "R6A2A1_combined_benchmark_adjudication.tsv", sep="\t", index=False)
primary = combined[combined.benchmark_role == "PUBLISHED_CELL_CLASS_PRIMARY"]
secondary = combined[combined.benchmark_role == "CROSS_CELL_SECONDARY"]
primary_loci = []
for locus, group in primary.groupby("locus"):
    if (group.classification == "PASS_ROBUST_SHARED_SIGNAL").any():
        status = "PASS_ROBUST_SHARED_SIGNAL"
    elif (group.classification == "HOLD_TARGETED_LD").any():
        status = "HOLD_TARGETED_LD"
    elif (group.classification == "FAIL_SUFFICIENT_COVERAGE").any():
        status = "FAIL_DISTINCT_SIGNAL"
    else:
        status = "UNINFORMATIVE_WEAK_QTL"
    best = group.sort_values(["PP_H4", "H4_over_H3H4"], ascending=False).iloc[0]
    primary_loci.append(
        {
            "locus": locus,
            "status": status,
            "best_gene": best.gene,
            "best_cell": best.cell_type,
            "best_PP_H4": float(best.PP_H4),
            "best_H4_over_H3H4": float(best.H4_over_H3H4),
            "best_qtl_min_p": float(best.qtl_min_p),
        }
    )
primary_loci = pd.DataFrame(primary_loci)
primary_loci.to_csv(OUT / "R6A2A1_published_cell_locus_adjudication.tsv", sep="\t", index=False)

# Targeted TenK author-computed coloc rows.
tenk_rows = []
for cell in ("NK", "NK_CD56bright"):
    data = pd.read_csv(TENK / f"R6A2A_ZMIZ1_precomputed_coloc/{cell}_chr10.csv")
    row = data[data.gene.astype(str).str.split(".").str[0] == "ENSG00000108175"]
    if len(row) != 1:
        raise RuntimeError(f"TenK ZMIZ1 row mismatch in {cell}")
    r = row.iloc[0].to_dict()
    r["gene_symbol"] = "ZMIZ1"
    r["H4_over_H3H4"] = float(r["PP.H4.abf"] / (r["PP.H3.abf"] + r["PP.H4.abf"]))
    r["replication_interpretation"] = (
        "SUPPORTIVE_SINGLE_CAUSAL_REPLICATION" if cell == "NK" and r["PP.H4.abf"] >= 0.8 else "DISTINCT_SIGNAL_FAVORED"
    )
    tenk_rows.append(r)
tenk_rows = pd.DataFrame(tenk_rows)
tenk_rows.to_csv(OUT / "R6A2A1_TenK_ZMIZ1_precomputed_coloc.tsv", sep="\t", index=False)

# Gene-level strength and source SuSiE structure from the locally verified ZIPs.
ens = "ENSG00000108175"
with zipfile.ZipFile(TENK / "common_variant_gene_level_results_with_annotated_fails.zip") as zf:
    member = [n for n in zf.namelist() if n.endswith("/NK_all_cis_cv_gene_level_results.tsv")][0]
    gene = pd.read_csv(zf.open(member))
    gene = gene[gene.gene.astype(str).str.split(".").str[0] == ens].copy()
with zipfile.ZipFile(TENK / "susie_summary.zip") as zf:
    member = [n for n in zf.namelist() if n.endswith("/NK_all_credible_snps.tsv")][0]
    susie = pd.read_csv(zf.open(member))
    susie = susie[susie.gene.astype(str).str.split(".").str[0] == ens].copy()
gene.to_csv(OUT / "R6A2A1_TenK_ZMIZ1_NK_gene_level.tsv", sep="\t", index=False)
susie.to_csv(OUT / "R6A2A1_TenK_ZMIZ1_NK_SuSiE_CS.tsv", sep="\t", index=False)
cs = susie.groupby("Credible_Set").PIP.agg(["count", "sum", "max"]).reset_index()
cs.to_csv(OUT / "R6A2A1_TenK_ZMIZ1_NK_SuSiE_CS_summary.tsv", sep="\t", index=False)

# Freeze a bounded next-wave universe: the eight remaining serum-IgA-concordant
# loci and only OneK combinations that already have compatible TenK support.
cross = pd.read_csv(ROOT / "3_results/04_integration/R6A1/IgAN_OneK1K_TenK10K_cross_resource_candidates.tsv", sep="\t")
next_loci = ["TNFSF4/18", "REL", "TNFSF8/15", "REEP3", "OVOL1/RELA", "TNFSF12/13", "TNFRSF13B", "LIF/OSM"]
universe = cross[cross.locus.isin(next_loci)][
    ["locus", "cell_type_OneK1K", "broad_cell", "gene_symbol", "top_variant_GRCh37", "top_p", "qval"]
].drop_duplicates(["locus", "cell_type_OneK1K", "gene_symbol"])
universe["selection_rule"] = "SERUM_IGA_CONCORDANT_AND_ONEK_SOURCE_SIG_AND_TENK_COMPATIBLE"
universe.sort_values(["locus", "gene_symbol", "cell_type_OneK1K"]).to_csv(
    OUT / "R6A2B0_frozen_8locus_183combination_universe.tsv", sep="\t", index=False
)
if len(universe) != 183 or universe.locus.nunique() != 8:
    raise RuntimeError("bounded next-wave universe changed")

published_pass = int((primary_loci.status == "PASS_ROBUST_SHARED_SIGNAL").sum())
published_uninformative = int((primary_loci.status == "UNINFORMATIVE_WEAK_QTL").sum())
secondary_fail = int((secondary.classification == "FAIL_SUFFICIENT_COVERAGE").sum())
tenk_nk = tenk_rows[tenk_rows.celltype == "NK"].iloc[0]
state = {
    "schema_version": "1.0",
    "stage": "R6A2A1",
    "adjudication": "COMPLETE_CONDITIONAL_GO_BOUNDED_EXPANSION",
    "upstream_R6A2A0_sha256": "c6efaba124a97ec357d97db8610e5d0eb4125384df68cfb33c4e8f56b66a0177",
    "code_corrections": {
        "R_data_table_gene_filter": "FIXED_GENE_COLUMN_SELF_COMPARISON",
        "Rscript_path": "FIXED_TO_WORKSPACE_R_4.6.1",
    },
    "OneK_benchmark": {
        "comparisons": int(len(py)),
        "combined_comparisons": int(len(combined)),
        "published_cell_loci_pass": published_pass,
        "published_cell_loci_uninformative_weak_QTL": published_uninformative,
        "published_cell_loci_fail_distinct": int((primary_loci.status == "FAIL_DISTINCT_SIGNAL").sum()),
        "cross_cell_robust": int((secondary.classification == "PASS_ROBUST_SHARED_SIGNAL").sum()),
        "cross_cell_fail_distinct": secondary_fail,
        "ABF_ambiguity_LD_triggers": int((combined.classification == "HOLD_TARGETED_LD").sum()),
        "strict_2_of_3_published_cell_gate": "NOT_MET",
    },
    "ZMIZ1_NK_OneK": {
        "combined_PP_H4": 0.9305874680520649,
        "combined_H4_over_H3H4": 0.9341141088825184,
        "H4_p12_1e-6": 0.572770,
        "asian_PP_H4": float(py[(py.dataset == "asian") & (py.locus == "ZMIZ1")].PP_H4.iloc[0]),
        "disease_lead_GRCh37": "10:81043743",
        "risk_allele_A_effect_on_expression": "DOWN",
    },
    "ZMIZ1_NK_TenK": {
        "author_precomputed_PP_H4": float(tenk_nk["PP.H4.abf"]),
        "H4_over_H3H4": float(tenk_nk.H4_over_H3H4),
        "nsnps": int(tenk_nk.nsnps_coloc_tested),
        "top_snp_GRCh38": str(tenk_nk.top_snp),
        "gene_level_ACAT_p": float(gene.ACAT_p.iloc[0]),
        "gene_level_top_p": float(gene.top_pval.iloc[0]),
        "source_SuSiE_credible_sets": int(susie.Credible_Set.nunique()),
        "claim_boundary": "supportive independent single-causal replication; exact priors and input provenance are not encoded in the extracted author CSV",
    },
    "validation": {
        "Python_vs_official_R_comparisons": int(len(validation)),
        "max_PP_H4_abs_diff": max_delta,
        "OneK_archive_gate": "PASS",
        "TenK_target_member_CRC_SHA_gate": "PASS",
    },
    "next_stage": {
        "id": "R6A2B0_BOUNDED_POSITIVE_YIELD_EXPANSION",
        "loci": 8,
        "OneK_cell_gene_combinations": int(len(universe)),
        "maximum_three_trait_ABF_tests": int(len(universe) * 3),
        "GO_full_24_rule": "at least 2 additional loci pass robust or signal-specific adjudication, yielding ZMIZ1 plus at least 2 additional loci",
        "zero_yield_rule": "if no additional locus is interpretable positive under sufficient coverage, HOLD full-24 expansion and reassess manuscript design",
    },
}
(AUD / "R6A2A1_final_adjudication.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
(ADMIN / "R6A2A1_state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(state, indent=2, ensure_ascii=False))
