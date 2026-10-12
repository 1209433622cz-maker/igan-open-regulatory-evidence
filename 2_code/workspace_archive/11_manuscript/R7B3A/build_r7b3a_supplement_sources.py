#!/usr/bin/env python3
"""Assemble the ten R7B3A supplementary datasets and provenance manifest.

The package contains only compact project-generated outputs and manifests.
Individual-level genotypes, BAMs, pseudobulk matrices and licensed source
archives are deliberately excluded.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
BASE = ROOT / "5_manuscript" / "R7B3A_ManuscriptV2" / "supplements"
BASE.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", low_memory=False)


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False)


def copy_exact(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def union_view(parts: list[tuple[str, pd.DataFrame]], keep: dict[str, list[str]] | None = None) -> pd.DataFrame:
    rows = []
    for name, frame in parts:
        cur = frame.copy()
        if keep and name in keep:
            missing = [c for c in keep[name] if c not in cur.columns]
            if missing:
                raise ValueError(f"{name}: missing columns {missing}")
            cur = cur[keep[name]].copy()
        cur.insert(0, "record_type", name)
        rows.append(cur)
    return pd.concat(rows, ignore_index=True, sort=False)


def main() -> None:
    for n in range(1, 11):
        (BASE / f"S{n}").mkdir(parents=True, exist_ok=True)

    # S1: accession, access, and source-term ledger.
    sources = pd.DataFrame([
        ["PBC_GWAS", "GCST90061440", "NHGRI-EBI GWAS Catalog", "https://www.ebi.ac.uk/gwas/studies/GCST90061440", "public", "Catalog/source-study terms", "Disease summary statistics; same GWAS reused across QTL resources"],
        ["PBC_FINE_MAP_LD", "GjokaPaper", "Newcastle University", "https://www.staff.ncl.ac.uk/heather.cordell/GjokaPaper.html", "public", "Source-page terms", "Study-derived PBC regional statistics and LD"],
        ["ONEK1K_EQTL", "Zenodo 18910121", "Zenodo", "https://doi.org/10.5281/zenodo.18910121", "public", "Zenodo-record terms", "Cell-specific cis-eQTL, genotype and covariate release"],
        ["TENK10K_EQTL", "Zenodo 18221260", "Zenodo", "https://doi.org/10.5281/zenodo.18221260", "public", "Zenodo-record terms", "Independent molecular-QTL resource; same PBC GWAS"],
        ["FINNGEN_MULTIOME", "Nature 2026", "FinnGen", "https://doi.org/10.1038/s41586-026-11078-2", "public aggregate", "Publisher/resource terms", "Molecular-QTL colocalization records and chromatin evidence"],
        ["PBC_LIVER", "HRA008003", "GSA-Human", "https://ngdc.cncb.ac.cn/gsa-human/browse/HRA008003", "open access", "GSA-Human source terms", "Five PBC and five surgical non-lesion control donors"],
        ["PROJECT_REPOSITORY", "GitHub", "Open Regulatory Evidence Project", "https://github.com/1209433622cz-maker/igan-open-regulatory-evidence", "public", "Repository license/source-file terms", "Code, protocols and compact aggregate results"],
    ], columns=["dataset_id", "accession", "provider", "url", "access_class", "license_or_terms", "role_and_boundary"])
    write_tsv(sources, BASE / "S1" / "S1_data_sources_accession_license.tsv")

    # S2: complete screening registry.
    s2_src = ROOT / "3_results/04_integration/R7B1/R7B1_current_PF10_ABF_all_comparisons.tsv.gz"
    s2 = read_tsv(s2_src)
    if len(s2) != 6923:
        raise ValueError(f"S2 expected 6,923 rows, found {len(s2)}")
    eligible_cols = [c for c in s2.columns if "eligible" in c.lower() or "classification" in c.lower() or "status" in c.lower()]
    if not eligible_cols:
        raise ValueError("S2 lacks eligibility/classification fields")
    copy_exact(s2_src, BASE / "S2" / "S2_PBCwide_6923_screening_registry.tsv.gz")
    s2_state = json.loads((ROOT / "3_results/04_integration/R7B1/R7B1_current_PF10_ABF_state.json").read_text(encoding="utf-8"))
    (BASE / "S2" / "S2_screening_state.json").write_text(json.dumps(s2_state, indent=2, ensure_ascii=False), encoding="utf-8")
    write_tsv(s2, BASE / "S2" / "S2_workbook_view.tsv")

    # S3: exact A0/A1/A2/M trajectories for all 642 high-information comparisons.
    s3_src = ROOT / "3_results/04_integration/R7B2A/adjudication/R7B2A_642_four_arm_trajectories.tsv"
    s3 = read_tsv(s3_src)
    if len(s3) != 642 or s3.comparison_id.nunique() != 642:
        raise ValueError("S3 comparison identity failed")
    copy_exact(s3_src, BASE / "S3" / "S3_642_A0_A1_A2_M_trajectories.tsv")
    write_tsv(s3, BASE / "S3" / "S3_workbook_view.tsv")

    # S4: exact support-set identity and removal audit.
    s4_cols = [
        "comparison_id", "locus_index", "gene", "cell_type", "R7B1B_v2_role",
        "S_A_n", "S_A_sha256", "S_M_n", "S_M_sha256", "removed_n",
        "removed_fraction", "qtl_N", "qtl_file_sha256", "source_ld_variant_sha256",
        "source_ld_PF10_sha256", "input_status",
    ]
    if any(c not in s3.columns for c in s4_cols):
        raise ValueError("S4 support identity columns missing")
    s4 = s3[s4_cols].copy()
    if not (s4.removed_n.min() == 19 and s4.removed_n.max() == 114 and float(s4.removed_n.median()) == 65):
        raise ValueError("S4 frozen removal audit changed")
    write_tsv(s4, BASE / "S4" / "S4_support_member_identity_and_removal_audit.tsv")
    write_tsv(s4, BASE / "S4" / "S4_workbook_view.tsv")

    # S5: all 2,568 model/trait fit-QC units and PF10/PF50 comparison-level states.
    s5_qc_src = ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_all_fit_QC.tsv.gz"
    s5_qc = read_tsv(s5_qc_src)
    s5_state_src = ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"
    s5_state = read_tsv(s5_state_src)
    if len(s5_qc) != 2568 or len(s5_state) != 642:
        raise ValueError("S5 expected 2,568 fit-QC rows and 642 states")
    copy_exact(s5_qc_src, BASE / "S5" / "S5_2568_PF10_PF50_SuSiE_fit_QC.tsv.gz")
    copy_exact(s5_state_src, BASE / "S5" / "S5_642_PF10_PF50_classifications.tsv")
    s5_view = union_view([
        ("FIT_QC", s5_qc),
        ("CLASSIFICATION", s5_state),
    ], keep={
        "FIT_QC": ["comparison_id", "locus_index", "gene", "cell_type", "config", "mode", "L", "qtl_N", "common_variants", "disease_converged", "qtl_converged", "disease_cs", "qtl_cs", "disease_s_rss", "qtl_s_rss"],
        "CLASSIFICATION": ["comparison_id", "locus_index", "gene", "cell_type", "PF10_multisignal_state", "PF10_PF50_sensitivity", "common_variants_min", "pf10_l10_best_h4", "pf50_l10_best_h4"],
    })
    write_tsv(s5_view, BASE / "S5" / "S5_workbook_view.tsv")

    # S6: complete signal-pair posteriors plus comparison-level pair semantics.
    s6_pairs_src = ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_all_signal_pair_posteriors.tsv.gz"
    s6_sem_src = ROOT / "3_results/04_integration/R7B1E0/signal_semantics/R7B1E0_signal_semantics_642.tsv"
    s6_pairs = read_tsv(s6_pairs_src); s6_sem = read_tsv(s6_sem_src)
    if len(s6_pairs) != 10542 or len(s6_sem) != 642:
        raise ValueError("S6 pair or semantics count changed")
    copy_exact(s6_pairs_src, BASE / "S6" / "S6_all_signal_pair_posteriors.tsv.gz")
    copy_exact(s6_sem_src, BASE / "S6" / "S6_signal_semantics_642.tsv")
    s6_view = union_view([
        ("PAIR_POSTERIOR", s6_pairs),
        ("COMPARISON_SEMANTICS", s6_sem),
    ], keep={
        "PAIR_POSTERIOR": ["comparison_id", "locus_index", "gene", "cell_type", "config", "mode", "L", "p12", "hit1", "hit2", "PP.H3.abf", "PP.H4.abf", "H3_plus_H4", "H4_over_H3H4"],
        "COMPARISON_SEMANTICS": ["comparison_id", "locus_index", "gene", "cell_type", "historical_PF10_multisignal_state", "semantic_state", "anchor_kind", "same_signal_pair_confirmed", "supporting_other_configs", "mixed_h4_h3_within_any_config"],
    })
    write_tsv(s6_view, BASE / "S6" / "S6_workbook_view.tsv")

    # S7: full grid-level summaries and the complete outcome-channel audit as compressed data.
    s7_files = {
        "S7_simulation_grid_486_summary.tsv": ROOT / "3_results/05_simulation/R7B1C/aggregate/R7B1C_grid_486_summary.tsv",
        "S7_scenario_summary.tsv": ROOT / "3_results/05_simulation/R7B1C/aggregate/R7B1C_scenario_summary.tsv",
        "S7_factor_stratified_summary.tsv": ROOT / "3_results/05_simulation/R7B1C/aggregate/R7B1C_factor_stratified_summary.tsv",
        "S7_discovery_vs_estimator.tsv": ROOT / "3_results/05_simulation/R7B2A_audit/R7B2A_R7B1C_discovery_vs_estimator_performance.tsv",
        "S7_channel_summary.tsv": ROOT / "3_results/05_simulation/R7B2A_audit/R7B2A_R7B1C_channel_summary.tsv",
        "S7_iteration_channels_486000.tsv.gz": ROOT / "3_results/05_simulation/R7B2A_audit/R7B2A_R7B1C_iteration_channel_audit.tsv.gz",
    }
    for dst_name, src in s7_files.items(): copy_exact(src, BASE / "S7" / dst_name)
    s7_parts = []
    for name in ["S7_simulation_grid_486_summary.tsv", "S7_scenario_summary.tsv", "S7_discovery_vs_estimator.tsv", "S7_channel_summary.tsv"]:
        s7_parts.append((name.replace("S7_", "").replace(".tsv", "").upper(), read_tsv(BASE / "S7" / name)))
    s7_view = union_view(s7_parts)
    write_tsv(s7_view, BASE / "S7" / "S7_workbook_view.tsv")

    # S8: external molecular-QTL, allele direction and chromatin-boundary records.
    s8_sources = {
        "S8_external_target_registry.tsv": ROOT / "3_results/04_integration/R7B1D/R7B1D_external_target_registry.tsv",
        "S8_external_axis_adjudication.tsv": ROOT / "3_results/04_integration/R7B1D/R7B1D_external_axis_adjudication.tsv",
        "S8_risk_allele_expression_direction.tsv": ROOT / "3_results/04_integration/R7B1D/R7B1D_risk_allele_expression_direction.tsv",
        "S8_FinnGen_PBC_molQTL_coloc.tsv": ROOT / "3_results/04_integration/R7B1D/R7B1D_FinnGen_PBC_molQTL_coloc.tsv",
        "S8_IL12RB2_positional_chromatin.tsv": ROOT / "3_results/04_integration/R7B1D/R7B1D_IL12RB2_FinnGen_positional_cascade.tsv",
    }
    s8_parts = []
    for dst_name, src in s8_sources.items():
        copy_exact(src, BASE / "S8" / dst_name)
        s8_parts.append((dst_name.replace("S8_", "").replace(".tsv", "").upper(), read_tsv(src)))
    write_tsv(union_view(s8_parts), BASE / "S8" / "S8_workbook_view.tsv")

    # S9: donor-level target-panel and exact/sensitivity results.
    s9_sources = {
        "S9_donor_target_panel.tsv": ROOT / "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel.tsv",
        "S9_exact_5vs5_tissue.tsv": ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure6_exact_5vs5_tissue.tsv",
        "S9_target_panel_sensitivity.tsv": ROOT / "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel_sensitivity.tsv",
    }
    s9_parts = []
    for dst_name, src in s9_sources.items():
        copy_exact(src, BASE / "S9" / dst_name)
        s9_parts.append((dst_name.replace("S9_", "").replace(".tsv", "").upper(), read_tsv(src)))
    s9_view = union_view(s9_parts)
    write_tsv(s9_view, BASE / "S9" / "S9_workbook_view.tsv")

    # S10: claim-evidence ledger and Methods/Results mirror.
    s10_claim_src = ROOT / "3_results/04_integration/R7B2A/manuscript_lock/R7B2A_updated_claim_evidence_ledger.tsv"
    s10_mirror_src = ROOT / "3_results/04_integration/R7B2A/manuscript_lock/R7B2A_methods_results_mirror.tsv"
    claims = read_tsv(s10_claim_src); mirror = read_tsv(s10_mirror_src)
    if len(claims) != 27 or len(mirror) != 10:
        raise ValueError("S10 ledger counts changed")
    copy_exact(s10_claim_src, BASE / "S10" / "S10_claim_evidence_ledger.tsv")
    copy_exact(s10_mirror_src, BASE / "S10" / "S10_methods_results_mirror.tsv")
    s10_view = union_view([("CLAIM_LEDGER", claims), ("METHODS_RESULTS_MIRROR", mirror)])
    write_tsv(s10_view, BASE / "S10" / "S10_workbook_view.tsv")

    # Build a file-level provenance, schema and release-boundary manifest.
    records = []
    for p in sorted(BASE.rglob("*")):
        if not p.is_file() or p.name in {"SUPPLEMENT_FILE_MANIFEST.tsv", "SUPPLEMENT_STATE.json"}:
            continue
        rel = p.relative_to(BASE).as_posix()
        rows = None; columns = None
        if p.suffix == ".tsv" or p.name.endswith(".tsv.gz"):
            frame = read_tsv(p)
            rows = len(frame); columns = "|".join(frame.columns)
        records.append({
            "supplement": rel.split("/")[0], "file": rel, "bytes": p.stat().st_size,
            "sha256": sha256(p), "rows": rows, "schema": columns,
            "content_class": "compact_project_generated_output",
            "license_boundary": "Project-generated derivative; underlying source terms remain applicable",
            "public_release": "YES",
        })
    manifest = pd.DataFrame(records)
    write_tsv(manifest, BASE / "SUPPLEMENT_FILE_MANIFEST.tsv")
    state = {
        "stage": "R7B3A_SUPPLEMENT_ASSEMBLY",
        "status": "PASS",
        "supplements": 10,
        "files_before_workbook": len(manifest),
        "excluded": ["individual-level genotype", "BAM", "pseudobulk matrices", "licensed source archives"],
        "row_controls": {"S2": 6923, "S3": 642, "S5_fit_QC": 2568, "S6_pairs": 10542, "S7_iterations": 486000, "S9_donor_rows": 20, "S10_claims": 27},
    }
    (BASE / "SUPPLEMENT_STATE.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False))


if __name__ == "__main__":
    main()
