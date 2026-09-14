#!/usr/bin/env python3
"""Build OneK1K PF10/PF50 covariate-residual LD for frozen triggers only."""

from pathlib import Path
import os
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
BASE = ROOT / "3_results/04_integration/R6A2B0/sourceLD"
COV = ROOT / "1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        while b := f.read(8 * 1024 * 1024):
            h.update(b)
    return h.hexdigest()


def residual_correlation(genotype, covariates):
    zc = covariates.astype(float)
    zc = (zc - zc.mean(axis=0)) / zc.std(axis=0, ddof=1)
    design = np.column_stack([np.ones(len(zc)), zc])
    q, r = np.linalg.qr(design, mode="reduced")
    rank = int(np.linalg.matrix_rank(r))
    if rank != design.shape[1]:
        raise RuntimeError(f"covariate design rank deficient: {rank}/{design.shape[1]}")
    residual = genotype.astype(float) - q @ (q.T @ genotype.astype(float))
    sd = residual.std(axis=0, ddof=1)
    if not np.isfinite(sd).all() or (sd <= 0).any():
        raise RuntimeError("non-variable genotype after residualization")
    z = (residual - residual.mean(axis=0)) / sd
    corr = (z.T @ z) / (len(z) - 1)
    corr = (corr + corr.T) / 2
    np.fill_diagonal(corr, 1)
    dual = (z @ z.T) / (len(z) - 1)
    dual = (dual + dual.T) / 2
    eig = np.linalg.eigvalsh(dual)
    return corr, {
        "design_columns": int(design.shape[1]),
        "design_rank": rank,
        "residual_degrees_of_freedom": int(len(z) - rank),
        "dual_min_eigenvalue": float(eig.min()),
        "dual_negative_eigenvalues_below_minus_1e_8": int((eig < -1e-8).sum()),
        "max_asymmetry": float(np.max(np.abs(corr - corr.T))),
        "max_diagonal_deviation": float(np.max(np.abs(np.diag(corr) - 1))),
    }


def main():
    rows = []
    for out in sorted(p for p in BASE.iterdir() if p.is_dir()):
        qc_path = out / "sourceLD_QC.json"
        if not qc_path.exists():
            continue
        source = json.loads(qc_path.read_text(encoding="utf-8"))
        samples = [x for x in (out / "active_donors.txt").read_text(encoding="utf-8").splitlines() if x]
        genotype = np.load(out / "standardized_A1_dosage.npy").astype(float)
        if genotype.shape[0] != len(samples):
            raise RuntimeError(f"sample dimension mismatch: {out.name}")
        cov = pd.read_csv(COV / f"{source['cell']}_mx_pf50.txt", sep=r"\s+", dtype={"sampleid": str}).set_index("sampleid")
        missing = sorted(set(samples) - set(cov.index))
        if missing:
            raise RuntimeError(f"covariates missing {len(missing)} donors for {out.name}")
        cov = cov.loc[samples]
        base = ["sex"] + [f"pc{i}" for i in range(1, 7)] + ["age"]
        modes = {
            "PF10": base + [f"pf{i}" for i in range(1, 11)],
            "PF50": base + [f"pf{i}" for i in range(1, 51)],
        }
        mode_qc = {}
        matrices = {}
        for mode, columns in modes.items():
            values = cov[columns].apply(pd.to_numeric, errors="raise").to_numpy(float)
            corr, detail = residual_correlation(genotype, values)
            corr32 = corr.astype(np.float32)
            npy = out / f"{mode}_residualized_A1_correlation.npy"
            binary = out / f"{mode}_residualized_A1_correlation.float32.bin"
            np.save(npy, corr32)
            corr32.astype("<f4", copy=False).tofile(binary)
            detail.update({
                "covariate_columns": columns,
                "npy_bytes": npy.stat().st_size,
                "npy_sha256": sha256(npy),
                "binary_bytes": binary.stat().st_size,
                "binary_sha256": sha256(binary),
            })
            detail["gate_pass"] = bool(
                detail["design_rank"] == detail["design_columns"]
                and detail["dual_negative_eigenvalues_below_minus_1e_8"] == 0
                and detail["max_asymmetry"] <= 1e-12
                and detail["max_diagonal_deviation"] <= 1e-12
                and np.isfinite(corr).all()
            )
            mode_qc[mode] = detail
            matrices[mode] = corr
        delta = np.abs(matrices["PF10"] - matrices["PF50"])
        audit = {
            "locus": source["locus"], "gene": source["gene"], "cell": source["cell"],
            "active_donors": len(samples), "variants": genotype.shape[1],
            "primary_LD": "PF10 residualized, matching public OneK1K TensorQTL covariate design",
            "sensitivity_LD": "PF50 residualized",
            "results": mode_qc,
            "PF10_vs_PF50_max_absolute_change": float(delta.max()),
            "PF10_vs_PF50_median_absolute_change": float(np.median(delta)),
            "gate_pass": all(x["gate_pass"] for x in mode_qc.values()),
        }
        (out / "covariate_residual_LD_QC.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        rows.append({k: audit[k] for k in ["locus", "gene", "cell", "active_donors", "variants", "gate_pass"]})
        print(json.dumps(rows[-1], ensure_ascii=False))
    summary = pd.DataFrame(rows)
    summary.to_csv(BASE / "R6A2B0_covariate_residual_LD_summary.tsv", sep="\t", index=False)
    if len(summary) != 3 or not summary.gate_pass.all():
        raise SystemExit(2)


if __name__ == "__main__":
    main()
