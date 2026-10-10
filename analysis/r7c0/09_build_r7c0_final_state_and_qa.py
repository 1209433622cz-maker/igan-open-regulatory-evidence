#!/usr/bin/env python3
"""Independent QA and final machine state for R7C0."""

from __future__ import annotations

import json
import os
import py_compile
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011"
RESULTS = WORK / "results"
INTAKE = WORK / "intake/R7C0_RPv4_intake_receipt.json"
REPO = ROOT / "github/igan-open-regulatory-evidence"
EXPECTED_BASELINE = "db20068e700b9c1ded8fb9171dab7e8da6aa33b7"


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def main() -> None:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail) -> None:
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})

    intake = json.loads(INTAKE.read_text(encoding="utf-8"))
    check("rpv4_zip_crc", intake["zip_crc"] == "PASS", intake["zip_crc"])
    check("rpv4_internal_checksums", intake["internal_checksums"] == {"pass": 12, "fail": 0, "total": 12}, intake["internal_checksums"])
    check("rpv4_docx_identity", intake["docx_identity"] == "PASS", intake["workspace_docx"]["sha256"])

    g1 = load("R7C0_G1_GJOKA_sample_size_adjudication.json")
    check("g1_source_matched_n", g1["adjudication"] == "PASS_SOURCE_MATCHED_N_TOTAL", g1["action"])

    cs = load("R7C0_FinnGen_R12_R13_IL12RB2_signal_identity.json")
    check("r12_r13_cs_identity", cs["intersection_size"] == 17 and cs["r13_is_subset_of_r12"] and cs["shared_lead_variant"], {k: cs[k] for k in ["r12_cs_size", "r13_cs_size", "intersection_size", "jaccard"]})
    check("r12_r13_direction", cs["shared_variant_beta_direction_concordance"] == 1.0, cs["shared_variant_beta_direction_concordance"])

    rep = load("R7C0_GJOKA_FinnGenR13_independent_replication_adjudication.json")
    check("independent_disease_signal", rep["signal_replication"] == "PASS", rep["adjudication"])
    check("independence_boundary_present", "WITHOUT_PERSON_LEVEL_PROOF" in rep["study_independence"], rep["study_independence"])

    ext = load("R7C0_FinnGenR13_x_OneK_IL12RB2_external_coloc_state.json")
    posterior = pd.read_csv(RESULTS / "R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv", sep="\t")
    posterior_sums = posterior[["PP_H0", "PP_H1", "PP_H2", "PP_H3", "PP_H4"]].sum(axis=1)
    check("external_coloc_posterior_sums", bool(((posterior_sums - 1).abs() < 1e-10).all()), posterior_sums.tolist())
    check("external_coloc_coverage", ext["n_variants"] >= 1000, ext["n_variants"])
    check("external_coloc_frozen_gate", ext["robust_single_causal_gate"] and ext["default_PP_H4"] >= 0.8 and ext["low_prior_H4_over_H3H4"] >= 0.5, {"default_H4": ext["default_PP_H4"], "low_ratio": ext["low_prior_H4_over_H3H4"]})
    check("external_source_cs_2_of_2", ext["onek_primary_qtl_cs_members"] == 2 and ext["onek_primary_qtl_cs_members_in_finngen_r13_disease_cs"] == 2, ext["onek_primary_qtl_cs_pip_mass_in_finngen_r13_disease_cs"])
    check("external_top_direction", ext["shared_top_variant"]["aligned_direction"] == "CONCORDANT", ext["shared_top_variant"])

    freeze = pd.read_csv(RESULTS / "R7C0_frozen_92_stableH4_comparisons.tsv", sep="\t")
    check("stable_h4_freeze", len(freeze) == 92 and freeze["gene"].nunique() == 27 and freeze["locus_index"].nunique() == 19, {"rows": len(freeze), "genes": freeze["gene"].nunique(), "loci": freeze["locus_index"].nunique()})

    cov = load("R7C0_CASCADE_27gene_coverage_summary.json")
    coloc = pd.read_csv(RESULTS / "R7C0_CASCADE_PBC_coloc_in_fixed_27genes.tsv", sep="\t")
    check("cascade_all_gene_endpoints", cov["gene_endpoint_pass"] == 27, cov["gene_endpoint_pass"])
    check("cascade_disease_specificity", cov["fixed_genes_with_PBC_eQTL_coloc_records"] == 1 and set(coloc["gene"]) == {"IL12RB2"}, sorted(coloc["gene"].unique()))
    check("cascade_il12rb2_h4", bool((coloc["PP_H4_abf"] >= 0.8).all()), coloc["PP_H4_abf"].tolist())

    tri = load("R7C0_IL12RB2_chromatin_triangle_adjudication.json")
    check("chromatin_triangle", tri["adjudication"] == "PASS_TRIANGULAR_SIGNAL_COHERENCE_WITHOUT_DIRECT_MEDIATION_PROOF" and tri["disease_eQTL"]["PP_H4_abf"] >= 0.8 and tri["disease_caQTL"]["PP_H4_abf"] >= 0.8, tri["adjudication"])
    check("chromatin_boundary", "does not provide a direct" in tri["remaining_gap"], tri["remaining_gap"])

    omix = load("R7C0_OMIX001122_spatial_adjudication.json")
    check("omix_byte_identity", omix["archive_file_count"] == 6 and omix["biological_matrices"] == 2, {"files": omix["archive_file_count"], "matrices": omix["biological_matrices"]})
    check("omix_fail_independent_validation", omix["adjudication"] == "PASS_OPEN_BYTES_FAIL_INDEPENDENT_SPATIAL_VALIDATION_GATE", omix["action"])

    figure_exts = {p.suffix for p in (WORK / "figures").glob("R7C0_external_evidence_preflight.*")}
    check("figure_formats", figure_exts == {".png", ".pdf", ".svg"}, sorted(figure_exts))

    code_files = sorted((WORK / "code").glob("*.py"))
    compile_fail = []
    for path in code_files:
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            compile_fail.append({"path": str(path), "error": repr(exc)})
    check("python_compile", not compile_fail and len(code_files) == 9, {"files": len(code_files), "failures": compile_fail})

    head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    origin = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "origin/main"], text=True).strip()
    status = subprocess.check_output(["git", "-C", str(REPO), "status", "--short"], text=True).strip()
    check("baseline_commit_unchanged", head == EXPECTED_BASELINE and origin == EXPECTED_BASELINE, {"head": head, "origin": origin})
    check("baseline_repo_clean", status == "", status or "clean")

    failed = [c for c in checks if c["status"] != "PASS"]
    qa = {
        "stage": "R7C0_QA", "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks, "pass": len(checks) - len(failed), "fail": len(failed), "total": len(checks),
        "overall": "PASS" if not failed else "FAIL",
    }
    (RESULTS / "R7C0_independent_QA.json").write_text(json.dumps(qa, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(checks).to_csv(RESULTS / "R7C0_independent_QA.tsv", sep="\t", index=False)
    if failed:
        raise RuntimeError(f"R7C0 QA failed: {failed}")

    state = {
        "stage": "R7C0_SOURCE_IDENTITY_EXTERNAL_EVIDENCE_UPGRADE_PREFLIGHT",
        "date": "2026-10-11",
        "R7C0": "COMPLETE",
        "PBC_PRIMARY_PROJECT": "GO",
        "R7B4B2_Q2_BASELINE": "FROZEN_SUBMISSION_READY_UNCHANGED",
        "G1_GJOKA_N": "PASS_SOURCE_MATCHED_N_TOTAL_NO_RERUN",
        "G2_EXTERNAL_DISEASE": "PASS_FINNGEN_R13_X_ONEK_IL12RB2",
        "G2_DEFAULT_PP_H4": ext["default_PP_H4"],
        "G2_LOW_PRIOR_PP_H4": ext["low_prior_PP_H4"],
        "G2_SOURCE_CS": "2_OF_2_ONEK_QTL_CS_MEMBERS_IN_FINNGEN_R13_DISEASE_CS",
        "G3_FIXED_92_CASCADE": "ONLY_IL12RB2_HAS_PBC_EQTL_COLOC",
        "G3_CHROMATIN": "PASS_TRIANGULAR_SIGNAL_COHERENCE_WITHOUT_MEDIATION_PROOF",
        "G4_OMIX": "FAIL_AS_INDEPENDENT_SPATIAL_VALIDATION_DESCRIPTIVE_ONLY",
        "FCRL3_EXTERNAL_DISEASE_SUPPORT": "NO",
        "NEW_GENE_LOCUS_SEARCH": "NO",
        "FULL_642_RERUN": "NO",
        "Q1_UPGRADE_TRACK": "GO_BOUNDED_MANUSCRIPT_FORK",
        "NEXT": "R7C1_IL12RB2_EXTERNAL_VALIDATION_MODULE_AND_MANUSCRIPT_FORK",
        "NEXT_HARD_BOUNDARIES": [
            "Preserve R7B4B2 byte-identical baseline and submission package.",
            "Add only the prespecified IL12RB2 external-disease and chromatin evidence module.",
            "Describe FinnGen R13 x OneK as single-causal external validation with a source-CS audit, not a second source-LD multi-signal fit.",
            "Do not claim direct eQTL-to-caQTL mediation; retain the missing direct posterior as a limitation.",
            "Do not use OMIX001122 as independent spatial replication.",
            "Hostile-audit the fork before any journal retargeting; retain the Q2 baseline if the upgrade does not survive review.",
        ],
        "GITHUB_BASELINE_COMMIT": EXPECTED_BASELINE,
        "ZENODO_DOI": None,
        "ZENODO_STATUS": "AUTHENTICATION_REQUIRED" if not os.getenv("ZENODO_TOKEN") else "TOKEN_PRESENT_NOT_USED_BY_QA",
        "qa": {"pass": qa["pass"], "fail": qa["fail"], "total": qa["total"]},
    }
    (RESULTS / "R7C0_final_state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
