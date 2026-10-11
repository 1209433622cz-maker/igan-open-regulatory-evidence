#!/usr/bin/env python3
"""Build PF10/PF50 covariate-residualized LD sensitivity matrices."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "3_results/04_integration/R5A2A4/NK_R_ZCCHC2_sourceLD"
COVARIATES = ROOT / "1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors/NK_R_mx_pf50.txt"
LEAD = "18:60005046"
QTL_TOP = "18:60243208"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def residualized_correlation(x: np.ndarray, design: np.ndarray) -> tuple[np.ndarray, dict[str, float | int]]:
    centered = design[:, 1:].astype(np.float64)
    centered = (centered - centered.mean(axis=0)) / centered.std(axis=0, ddof=1)
    design_scaled = np.column_stack([np.ones(len(design)), centered])
    q, r = np.linalg.qr(design_scaled, mode="reduced")
    rank = int(np.linalg.matrix_rank(r))
    if rank != design_scaled.shape[1]:
        raise RuntimeError(f"Covariate design is rank deficient: {rank}/{design_scaled.shape[1]}")
    residual = x.astype(np.float64) - q @ (q.T @ x.astype(np.float64))
    residual_sd = residual.std(axis=0, ddof=1)
    if not np.isfinite(residual_sd).all() or (residual_sd <= 0).any():
        raise RuntimeError("Non-variable genotype after covariate residualization")
    z = (residual - residual.mean(axis=0)) / residual_sd
    corr = (z.T @ z) / (len(z) - 1)
    corr = (corr + corr.T) / 2
    np.fill_diagonal(corr, 1.0)
    dual = (z @ z.T) / (len(z) - 1)
    dual = (dual + dual.T) / 2
    eig = np.linalg.eigvalsh(dual)
    return corr, {
        "design_columns": int(design_scaled.shape[1]),
        "design_rank": rank,
        "residual_degrees_of_freedom": int(len(z) - rank),
        "dual_min_eigenvalue": float(eig.min()),
        "dual_negative_eigenvalues_below_minus_1e_8": int((eig < -1e-8).sum()),
        "max_asymmetry": float(np.max(np.abs(corr - corr.T))),
        "max_diagonal_deviation": float(np.max(np.abs(np.diag(corr) - 1))),
    }


def main() -> int:
    samples = [line.strip() for line in (OUT / "NK_R_750_active_donors.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
    variants = pd.read_csv(OUT / "NK_R_ZCCHC2_LD_variants.tsv", sep="\t")
    x = np.load(OUT / "NK_R_ZCCHC2_standardized_A1_dosage.npy").astype(np.float64)
    raw = np.load(OUT / "NK_R_ZCCHC2_signed_A1_correlation.npy").astype(np.float64)
    if x.shape != (750, 3827) or raw.shape != (3827, 3827) or len(variants) != 3827:
        raise RuntimeError(f"Unexpected source-LD dimensions: X={x.shape}, R={raw.shape}, variants={len(variants)}")

    cov = pd.read_csv(COVARIATES, sep=r"\s+", dtype={"sampleid": str}).set_index("sampleid")
    missing = sorted(set(samples) - set(cov.index))
    if missing:
        raise RuntimeError(f"Active donors missing from covariates: {missing[:5]}")
    cov = cov.loc[samples]
    base = ["sex"] + [f"pc{i}" for i in range(1, 7)] + ["age"]
    designs = {
        "PF10": base + [f"pf{i}" for i in range(1, 11)],
        "PF50": base + [f"pf{i}" for i in range(1, 51)],
    }
    index = {variant: i for i, variant in enumerate(variants["variant_id"])}
    results = {}
    correlations = {}
    for label, columns in designs.items():
        if not set(columns).issubset(cov.columns):
            raise RuntimeError(f"Missing {label} covariate columns")
        values = cov[columns].apply(pd.to_numeric, errors="raise").to_numpy(float)
        corr, qc = residualized_correlation(x, np.column_stack([np.ones(len(values)), values]))
        corr32 = corr.astype(np.float32)
        npy = OUT / f"NK_R_ZCCHC2_{label}_residualized_A1_correlation.npy"
        binary = OUT / f"NK_R_ZCCHC2_{label}_residualized_A1_correlation.float32.bin"
        np.save(npy, corr32)
        corr32.astype("<f4", copy=False).tofile(binary)
        delta = np.abs(corr - raw)
        lead_top_r = float(corr[index[LEAD], index[QTL_TOP]])
        qc.update({
            "covariate_columns": columns,
            "lead_to_QTL_top_signed_r_A1": lead_top_r,
            "lead_to_QTL_top_r_squared": lead_top_r**2,
            "maximum_absolute_change_vs_raw_LD": float(delta.max()),
            "median_absolute_change_vs_raw_LD": float(np.median(delta)),
            "npy_bytes": npy.stat().st_size,
            "npy_sha256": sha256(npy),
            "binary_bytes": binary.stat().st_size,
            "binary_sha256": sha256(binary),
        })
        qc["gate_pass"] = all([
            qc["design_rank"] == qc["design_columns"],
            qc["dual_negative_eigenvalues_below_minus_1e_8"] == 0,
            qc["max_asymmetry"] <= 1e-12,
            qc["max_diagonal_deviation"] <= 1e-12,
            np.isfinite(corr).all(),
        ])
        results[label] = qc
        correlations[label] = corr

    cross_delta = np.abs(correlations["PF10"] - correlations["PF50"])
    audit = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "active_donors": len(samples),
        "variants": len(variants),
        "primary_LD": "PF10 residualized, matching the public OneK1K TensorQTL script",
        "sensitivity_LD": ["raw genotype", "PF50 residualized using updated public covariates"],
        "results": results,
        "PF10_vs_PF50_max_absolute_change": float(cross_delta.max()),
        "PF10_vs_PF50_median_absolute_change": float(np.median(cross_delta)),
        "covariate_residual_LD_gate_pass": all(item["gate_pass"] for item in results.values()),
    }
    path = OUT / "NK_R_ZCCHC2_covariate_residual_LD_QC.json"
    path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0 if audit["covariate_residual_LD_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
