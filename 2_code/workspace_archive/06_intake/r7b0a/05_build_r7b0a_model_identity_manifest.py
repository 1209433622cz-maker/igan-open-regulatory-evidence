#!/usr/bin/env python3
"""Build the fail-closed current-release PF10/PF50 identity manifest.

This gate verifies that each de novo QTL summary is paired with LD generated
from the same public OneK release, active donors, covariate matrix, alleles and
variant order. It records hashes but does not use posterior results.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
TRIGGERS = ROOT / "3_results/04_integration/R7A1B/R7A1B_multisignal_triggers.tsv"
SOURCE_LD = ROOT / "3_results/04_integration/R7A1B/sourceLD"
QTL_BASE = ROOT / "3_results/03_qtl/R7B0/pf50_targeted"
COV_BASE = ROOT / "1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors"
SAMPLE_BASE = ROOT / "3_results/03_qtl/R5A2A2/cell_sample_lists"
OUT = ROOT / "3_results/04_integration/R7B0A/current_release_dualmodel"

BASE_COV = ["sex"] + [f"pc{i}" for i in range(1, 7)] + ["age"]
MODE_COV = {
    "PF10": BASE_COV + [f"pf{i}" for i in range(1, 11)],
    "PF50": BASE_COV + [f"pf{i}" for i in range(1, 51)],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def bool_value(value: object) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    triggers = pd.read_csv(TRIGGERS, sep="\t")
    jobs = list(dict.fromkeys((str(x.gene), str(x.cell_type)) for x in triggers.itertuples()))
    if len(jobs) != 7:
        raise RuntimeError(f"expected 7 frozen comparisons, found {len(jobs)}")

    rows: list[dict[str, object]] = []
    for gene, cell in jobs:
        slug = f"{gene}_{cell}"
        ld_dir = SOURCE_LD / slug
        donor_path = SAMPLE_BASE / f"{cell}.samples.txt"
        active_path = ld_dir / "active_donors.txt"
        cov_path = COV_BASE / f"{cell}_mx_pf50.txt"
        variants_path = ld_dir / "LD_variants.tsv"
        ld_qc_path = ld_dir / "covariate_residual_LD_QC.json"

        required = [donor_path, active_path, cov_path, variants_path, ld_qc_path]
        missing = [str(x) for x in required if not x.is_file()]
        if missing:
            raise FileNotFoundError("missing identity inputs: " + "; ".join(missing))

        donors = [x for x in donor_path.read_text(encoding="utf-8").splitlines() if x]
        active = [x for x in active_path.read_text(encoding="utf-8").splitlines() if x]
        donors_exact = donors == active
        cov = pd.read_csv(cov_path, sep=r"\s+", dtype={"sampleid": str}).set_index("sampleid")
        donors_in_cov = all(x in cov.index for x in donors)
        cov_order_exact = donors_in_cov and cov.loc[donors].index.tolist() == donors
        variants = pd.read_csv(variants_path, sep="\t").sort_values("LD_order_zero_based")
        if variants["variant_id"].duplicated().any():
            raise RuntimeError(f"duplicate LD variants: {slug}")
        ld_qc = json.loads(ld_qc_path.read_text(encoding="utf-8"))

        for mode, covariates in MODE_COV.items():
            qtl_path = QTL_BASE / f"{slug}_{mode}.tsv.gz"
            ld_npy_path = ld_dir / f"{mode}_residualized_A1_correlation.npy"
            ld_tsv_path = ld_dir / f"{mode}_residualized_A1_correlation.tsv.gz"
            files_present = all(x.is_file() for x in [qtl_path, ld_npy_path, ld_tsv_path])
            if not files_present:
                missing_mode = [str(x) for x in [qtl_path, ld_npy_path, ld_tsv_path] if not x.is_file()]
                raise FileNotFoundError("missing current-model artifacts: " + "; ".join(missing_mode))

            qtl = pd.read_csv(qtl_path, sep="\t")
            qtl_order_exact = qtl["variant_id"].astype(str).tolist() == variants["variant_id"].astype(str).tolist()
            allele_exact = (
                qtl["A1_effect_allele"].astype(str).str.upper().tolist()
                == variants["A1"].astype(str).str.upper().tolist()
                and qtl["A2_other_allele"].astype(str).str.upper().tolist()
                == variants["A2"].astype(str).str.upper().tolist()
            )
            qtl_mode_exact = set(qtl["mode"].astype(str)) == {mode}
            implementation_exact = set(qtl["implementation"].astype(str)) == {
                "TensorQTL_1.0.10_formula_compatible_numpy"
            }
            qtl_n_exact = set(pd.to_numeric(qtl["n_expression_donors"]).astype(int)) == {len(donors)}
            covariates_present = all(x in cov.columns for x in covariates)

            matrix = np.load(ld_npy_path, mmap_mode="r")
            shape_exact = matrix.shape == (len(variants), len(variants))
            max_asymmetry = float(np.max(np.abs(matrix - matrix.T))) if shape_exact else float("inf")
            max_diag_dev = float(np.max(np.abs(np.diag(matrix) - 1.0))) if shape_exact else float("inf")
            mode_qc = ld_qc.get("results", {}).get(mode, {})
            ld_generation_qc = bool_value(mode_qc.get("gate_pass", False))
            model_identity_pass = all(
                [
                    donors_exact,
                    donors_in_cov,
                    cov_order_exact,
                    covariates_present,
                    qtl_order_exact,
                    allele_exact,
                    qtl_mode_exact,
                    implementation_exact,
                    qtl_n_exact,
                    shape_exact,
                    max_asymmetry <= 1e-6,
                    max_diag_dev <= 1e-6,
                    ld_generation_qc,
                ]
            )

            rows.append(
                {
                    "gene": gene,
                    "cell_type": cell,
                    "mode": mode,
                    "n_donors": len(donors),
                    "n_variants": len(variants),
                    "donors_exact": donors_exact,
                    "donors_in_covariates": donors_in_cov,
                    "covariate_order_exact": cov_order_exact,
                    "covariates_present": covariates_present,
                    "summary_variant_order_exact": qtl_order_exact,
                    "summary_alleles_exact": allele_exact,
                    "summary_mode_exact": qtl_mode_exact,
                    "summary_implementation_exact": implementation_exact,
                    "summary_n_exact": qtl_n_exact,
                    "ld_shape_exact": shape_exact,
                    "ld_max_asymmetry": max_asymmetry,
                    "ld_max_diag_deviation": max_diag_dev,
                    "ld_generation_qc_pass": ld_generation_qc,
                    "ld_design_columns": mode_qc.get("design_columns"),
                    "ld_design_rank": mode_qc.get("design_rank"),
                    "ld_residual_df": mode_qc.get("residual_df"),
                    "ld_dual_min_eigenvalue": mode_qc.get("dual_min_eigenvalue"),
                    "model_identity_pass": model_identity_pass,
                    "donor_manifest_sha256": sha256(donor_path),
                    "active_donor_sha256": sha256(active_path),
                    "covariate_file_sha256": sha256(cov_path),
                    "variant_manifest_sha256": sha256(variants_path),
                    "qtl_summary_sha256": sha256(qtl_path),
                    "ld_npy_sha256": sha256(ld_npy_path),
                    "ld_tsv_sha256": sha256(ld_tsv_path),
                    "ld_qc_sha256": sha256(ld_qc_path),
                }
            )

    frame = pd.DataFrame(rows).sort_values(["gene", "cell_type", "mode"])
    frame.to_csv(OUT / "R7B0A_current_release_identity_manifest.tsv", sep="\t", index=False)
    overall = bool(len(frame) == 14 and frame["model_identity_pass"].all())
    state = {
        "schema": "R7B0A_CURRENT_RELEASE_IDENTITY_MANIFEST_1.0",
        "comparisons": len(jobs),
        "expected_mode_rows": 14,
        "observed_mode_rows": int(len(frame)),
        "identity_pass_rows": int(frame["model_identity_pass"].sum()),
        "identity_status": "PASS" if overall else "HOLD",
        "gate_is_independent_of_posterior": True,
        "trigger_manifest_sha256": sha256(TRIGGERS),
    }
    (OUT / "R7B0A_current_release_identity_manifest.json").write_text(
        json.dumps(state, indent=2), encoding="utf-8"
    )
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
