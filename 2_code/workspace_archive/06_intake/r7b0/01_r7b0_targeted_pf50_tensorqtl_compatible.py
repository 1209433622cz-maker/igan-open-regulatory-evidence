#!/usr/bin/env python3
"""R7B0 targeted PF10 reproduction and corrected PF50 nominal QTL rerun.

This is a NumPy implementation of TensorQTL 1.0.10's published nominal
association formula. It is deliberately labelled formula-compatible: it does
not claim that the TensorQTL binary was executed. PF10 is compared with the
frozen OneK1K summary before PF50 output is allowed into adjudication.
"""
from __future__ import annotations

import argparse, hashlib, json, math, os, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\\SCI2\\YR1"))
PHENO_ZIP = ROOT / "1_data/qtl/OneK1K/OneK1K_pseudobulk_mean_mx.zip"
GENE_ZIP = ROOT / "1_data/qtl/OneK1K/OneK1K_pseudobulk_mx_gene_list.zip"
COV_DIR = ROOT / "1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors"
FAM = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.fam"
BIM = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
QTL = ROOT / "3_results/03_qtl/R7A1B/R7A1B_OneK_frozen_QTL.tsv.gz"
TRIGGERS = ROOT / "3_results/04_integration/R7A1B/R7A1B_multisignal_triggers.tsv"
OUT = ROOT / "3_results/03_qtl/R7B0/pf50_targeted"

BASE_COV = ["sex"] + [f"pc{i}" for i in range(1, 7)] + ["age"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tensorqtl_formula(genotypes: np.ndarray, phenotype: np.ndarray,
                      covariates: np.ndarray) -> dict[str, np.ndarray]:
    """Replicate TensorQTL Residualizer + calculate_cis_nominal.

    Inputs: variants x samples, phenotype samples, covariates samples x K.
    Residualizer centers covariates, QR-orthogonalizes them, then centers and
    projects both genotype and phenotype. Variance uses sample (N-1) variance,
    matching torch.var's default used by TensorQTL.
    """
    G = np.asarray(genotypes, dtype=np.float64)
    y = np.asarray(phenotype, dtype=np.float64)
    C = np.asarray(covariates, dtype=np.float64)
    if G.ndim != 2 or y.ndim != 1 or C.ndim != 2 or G.shape[1] != y.size or C.shape[0] != y.size:
        raise ValueError("TensorQTL-compatible dimensions are invalid")
    if not np.isfinite(G).all() or not np.isfinite(y).all() or not np.isfinite(C).all():
        raise ValueError("non-finite input after preprocessing")
    # TensorQTL: self.Q_t,_ = torch.linalg.qr(C_t - C_t.mean(0))
    Q, R = np.linalg.qr(C - C.mean(axis=0), mode="reduced")
    rank = int(np.linalg.matrix_rank(R))
    if rank != C.shape[1]:
        raise ValueError(f"rank-deficient covariates rank={rank} k={C.shape[1]}")
    G0 = G - G.mean(axis=1, keepdims=True)
    y0 = y - y.mean()
    Gres = G0 - (G0 @ Q) @ Q.T
    yres = y0 - (y0 @ Q) @ Q.T
    gv = Gres.var(axis=1, ddof=1)
    yv = yres.var(ddof=1)
    if np.any(~np.isfinite(gv)) or np.any(gv <= 0) or not np.isfinite(yv) or yv <= 0:
        raise ValueError("non-variable residual genotype/phenotype")
    r = (Gres @ yres) / np.sqrt((Gres * Gres).sum(axis=1) * (yres * yres).sum())
    r = np.clip(r, -1 + 1e-15, 1 - 1e-15)
    dof = y.size - 2 - C.shape[1]
    tstat = r * np.sqrt(dof / (1 - r * r))
    slope = r * np.sqrt(yv / gv)
    slope_se = slope / tstat
    pval = 2 * student_t.sf(np.abs(tstat), dof)
    af = G.sum(axis=1) / (2 * G.shape[1])
    return {"slope_A1": slope, "slope_se": slope_se, "z": tstat,
            "pval_nominal": pval, "af_A1": af,
            "n": np.array([y.size]), "dof": np.array([dof])}


def read_gene_ids(cell: str) -> list[str]:
    with zipfile.ZipFile(GENE_ZIP) as z:
        name = f"{cell}_cells_gene_list.txt"
        with z.open(name) as f:
            lines = [x.decode("utf-8", "replace").strip() for x in f]
    return [x for x in lines[1:] if x]


def read_target_expression(cell: str, gene: str) -> tuple[list[str], np.ndarray, int]:
    genes = read_gene_ids(cell)
    hits = [i for i, x in enumerate(genes) if x == gene]
    if not hits:
        raise KeyError(f"{gene} absent from {cell} gene list")
    row_i = hits[0]
    with zipfile.ZipFile(PHENO_ZIP) as z:
        name = f"{cell}_cells_mean_mx.txt"
        with z.open(name) as f:
            header = f.readline().decode("utf-8").strip().split()
            first = f.readline().decode("utf-8").strip().split()
            if len(first) != len(header):
                raise ValueError(f"{cell} first row width differs from header")
            first_arr = np.array([float("nan") if x.lower() in {"na", "nan", ""} else float(x) for x in first])
            active_mask = np.isfinite(first_arr)
            target = None
            for i, line in enumerate(f):
                if i == row_i - 1:  # row 0 was read as first data row
                    vals = line.decode("utf-8").strip().split()
                    target = np.array([float("nan") if x.lower() in {"na", "nan", ""} else float(x) for x in vals])
                    break
    if target is None:
        if row_i == 0:
            target = first_arr
        else:
            raise RuntimeError(f"failed to read target row {row_i} for {cell}")
    if target.size != len(header):
        raise ValueError(f"{cell}/{gene}: target width differs from header")
    ids = [x for x, ok in zip(header, active_mask) if ok]
    y = target[active_mask]
    if not np.isfinite(y).all():
        raise ValueError(f"{cell}/{gene}: target has missing values after first-row donor filter")
    # Source R: log(x+1), then t(scale(t(mx))) for each gene across donors.
    y = np.log1p(y)
    ysd = y.std(ddof=1)
    if not np.isfinite(ysd) or ysd <= 0:
        raise ValueError(f"{cell}/{gene}: zero variance after log1p")
    y = (y - y.mean()) / ysd
    return ids, y, row_i


def load_plink_maps() -> tuple[list[str], dict[str, int], pd.DataFrame]:
    fam = pd.read_csv(FAM, sep=r"\s+", header=None, dtype=str)
    ids = fam.iloc[:, 1].tolist()
    idx = {x: i for i, x in enumerate(ids)}
    bim = pd.read_csv(BIM, sep=r"\s+", header=None,
                      names=["chr", "variant_id", "cm", "pos", "A1", "A2"], dtype=str)
    bim["gi"] = np.arange(len(bim), dtype=int)
    return ids, idx, bim


def read_bed_variants(variant_gi: np.ndarray, keep: np.ndarray, n_total: int) -> np.ndarray:
    bed = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bed"
    bps = (n_total + 3) // 4
    G = np.empty((len(keep), len(variant_gi)), dtype=np.float64)
    with bed.open("rb") as f:
        if f.read(3) != bytes.fromhex("6c1b01"):
            raise ValueError("invalid PLINK bed magic")
        for j, gi in enumerate(variant_gi.astype(int)):
            f.seek(3 + gi * bps)
            raw = f.read(bps)
            codes = np.fromiter(((b >> s) & 3 for b in raw for s in (0, 2, 4, 6)),
                                dtype=np.int8, count=bps * 4)[:n_total][keep]
            dos = np.where(codes == 0, 2.0,
                           np.where(codes == 2, 1.0,
                                    np.where(codes == 3, 0.0, np.nan)))
            if np.isnan(dos).any():
                dos = np.where(np.isnan(dos), np.nanmean(dos), dos)
            G[:, j] = dos
    return G.T


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genes", nargs="+", default=None)
    ap.add_argument("--cells", nargs="+", default=None)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    tr = pd.read_csv(TRIGGERS, sep="\t")
    if args.genes and args.cells:
        jobs = [(g, c) for g, c in zip(args.genes, args.cells)]
    else:
        jobs = list(dict.fromkeys((str(r.gene), str(r.cell_type)) for r in tr.itertuples()))
    q = pd.read_csv(QTL, sep="\t")
    fam_ids, fam_idx, bim = load_plink_maps()
    summary = []
    per = []
    for gene, cell in jobs:
        slug = f"{gene}_{cell}"
        sfile = ROOT / f"3_results/03_qtl/R5A2A2/cell_sample_lists/{cell}.samples.txt"
        expected = [x for x in sfile.read_text(encoding="utf-8").splitlines() if x]
        expr_ids, y, row_i = read_target_expression(cell, gene)
        if expr_ids != expected:
            raise RuntimeError(f"{slug}: source first-row donor filter != frozen active donor list")
        d = ROOT / f"3_results/04_integration/R7A1B/sourceLD/{slug}"
        vars = pd.read_csv(d / "LD_variants.tsv", sep="\t")
        if vars.variant_id.duplicated().any():
            raise RuntimeError(f"{slug}: duplicate LD variant IDs")
        if not set(vars.variant_id).issubset(set(bim.variant_id)):
            raise RuntimeError(f"{slug}: LD variant missing from BIM")
        qsub = q[(q.gene == gene) & (q.cell_type == cell)].drop_duplicates("variant_id")
        qsub = vars[["variant_id", "LD_order_zero_based"]].merge(qsub, on="variant_id", how="left", validate="one_to_one")
        if qsub.slope_A1.isna().any():
            raise RuntimeError(f"{slug}: QTL summary missing LD variants")
        gis = bim.set_index("variant_id").loc[qsub.variant_id, "gi"].to_numpy()
        keep = np.array([fam_idx[x] for x in expr_ids], dtype=int)
        G = read_bed_variants(gis, keep, len(fam_ids))
        cov = pd.read_csv(COV_DIR / f"{cell}_mx_pf50.txt", sep=r"\s+", dtype={"sampleid": str}).set_index("sampleid")
        cov = cov.loc[expr_ids]
        if not np.array_equal(cov.index.to_numpy(), np.array(expr_ids)):
            raise RuntimeError(f"{slug}: covariate donor order mismatch")
        modes = {"PF10": BASE_COV + [f"pf{i}" for i in range(1, 11)],
                 "PF50": BASE_COV + [f"pf{i}" for i in range(1, 51)]}
        outputs = {}
        for mode, cols in modes.items():
            res = tensorqtl_formula(G, y, cov[cols].to_numpy(dtype=float))
            out = qsub[["phenotype_id", "variant_id", "position_GRCh37", "A1_effect_allele", "A2_other_allele", "gene", "cell_type", "n_expression_donors"]].copy()
            for key in ["af_A1", "slope_A1", "slope_se", "z", "pval_nominal"]:
                out[key] = res[key]
            out["mode"] = mode
            out["implementation"] = "TensorQTL_1.0.10_formula_compatible_numpy"
            outputs[mode] = out
            out.to_csv(OUT / f"{slug}_{mode}.tsv.gz", sep="\t", index=False, compression="gzip")
        pf10 = outputs["PF10"].set_index("variant_id")
        frozen = qsub.set_index("variant_id")
        slope_err = np.abs(pf10.slope_A1 - frozen.slope_A1)
        se_err = np.abs(pf10.slope_se - frozen.slope_se)
        z_ref = frozen.slope_A1 / frozen.slope_se
        z_corr = float(np.corrcoef(pf10.z, z_ref)[0, 1])
        p_corr = float(np.corrcoef(-np.log10(np.maximum(pf10.pval_nominal, 1e-300)),
                                   -np.log10(np.maximum(frozen.pval_nominal, 1e-300)))[0, 1])
        qc = {"gene": gene, "cell": cell, "n_donors": len(expr_ids), "n_variants": len(qsub),
              "expression_gene_row_zero_based": int(row_i),
              "pf10_slope_max_abs_error": float(slope_err.max()),
              "pf10_slope_median_abs_error": float(slope_err.median()),
              "pf10_se_max_abs_error": float(se_err.max()),
              "pf10_se_median_abs_error": float(se_err.median()),
              "pf10_z_corr_with_frozen_beta_se": z_corr,
              "pf10_logp_corr_with_frozen": p_corr,
              "pass_tight_reproduction": bool(slope_err.max() <= 2e-5 and se_err.max() <= 2e-5 and z_corr >= 0.999999),
              "formula_source": "tensorqtl-1.0.10 wheel tensorqtl/core.py + tensorqtl/cis.py",
              "source_expression_transform": "remove first-row-NA donors; log1p; row standardize sample SD",
              "covariates": {"PF10": BASE_COV + [f"pf{i}" for i in range(1, 11)],
                             "PF50": BASE_COV + [f"pf{i}" for i in range(1, 51)]}}
        (OUT / f"{slug}_QC.json").write_text(json.dumps(qc, indent=2), encoding="utf-8")
        summary.append(qc)
        for mode, out in outputs.items():
            out2 = out.set_index("variant_id")
            per.append({"gene": gene, "cell": cell, "mode": mode,
                        "n_donors": len(expr_ids), "n_variants": len(out),
                        "min_p": float(out2.pval_nominal.min()),
                        "min_p_variant": str(out2.pval_nominal.idxmin())})
    pd.DataFrame(summary).to_json(OUT / "R7B0_pf10_reproduction_and_pf50_QC.json", orient="records", indent=2)
    pd.DataFrame(summary).to_csv(OUT / "R7B0_pf10_reproduction_QC.tsv", sep="\t", index=False)
    pd.DataFrame(per).to_csv(OUT / "R7B0_pf10_pf50_summary.tsv", sep="\t", index=False)
    manifest = {"status": "PASS" if all(x["pass_tight_reproduction"] for x in summary) else "BLOCK",
                "jobs": len(jobs), "jobs_pass": int(sum(x["pass_tight_reproduction"] for x in summary)),
                "inputs": {str(p.relative_to(ROOT)): sha256(p) for p in [PHENO_ZIP, GENE_ZIP, QTL, TRIGGERS]},
                "implementation": "TensorQTL_1.0.10_formula_compatible_numpy"}
    (OUT / "R7B0_pf50_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
