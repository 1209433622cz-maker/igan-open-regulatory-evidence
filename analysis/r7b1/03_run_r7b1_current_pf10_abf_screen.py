#!/usr/bin/env python3
"""Run the frozen R7B1 PBC-wide current-release PF10 ABF screen.

The comparison universe is frozen upstream.  This script regenerates OneK1K
nominal QTL statistics from the public pseudobulk, PLINK genotype and PF10
covariates, keeps every frozen comparison, and writes a trigger set without
using posterior results to change gene/cell eligibility.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logsumexp
from scipy.stats import t as student_t


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
COMPARE = ROOT / "3_results/03_qtl/R7B1/R7B1_frozen_comparison_universe.tsv"
DISEASE = ROOT / "3_results/01_gwas/R7B1/R7B1_PBC56_GRCh37_BIM_A1.tsv.gz"
PHENO_ZIP = ROOT / "1_data/qtl/OneK1K/OneK1K_pseudobulk_mean_mx.zip"
GENE_ZIP = ROOT / "1_data/qtl/OneK1K/OneK1K_pseudobulk_mx_gene_list.zip"
PLINK = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors"
BED = PLINK / "plink_merged_980_donors.bed"
FAM = PLINK / "plink_merged_980_donors.fam"
COV_DIR = ROOT / "1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors"
SAMPLE_DIR = ROOT / "3_results/03_qtl/R5A2A2/cell_sample_lists"
OUT = ROOT / "3_results/04_integration/R7B1"
QTL_OUT = ROOT / "3_results/03_qtl/R7B1/pf10_trigger_qtl"

BASE_COV = ["sex"] + [f"pc{i}" for i in range(1, 7)] + ["age"]
PF10_COV = BASE_COV + [f"pf{i}" for i in range(1, 11)]
P12_GRID = (1e-6, 1e-5, 1e-4)
MIN_VARIANTS = 200


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def hash_variant_set(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(values) + "\n").encode("utf-8")).hexdigest()


def logdiff(a: float, b: float) -> float:
    if b >= a:
        return -np.inf
    return float(a + np.log1p(-np.exp(b - a)))


def log_abf(beta: np.ndarray, se: np.ndarray, prior_sd: float) -> np.ndarray:
    variance = np.square(np.asarray(se, dtype=np.float64))
    z = np.asarray(beta, dtype=np.float64) / np.asarray(se, dtype=np.float64)
    r = prior_sd**2 / (prior_sd**2 + variance)
    return 0.5 * (np.log1p(-r) + r * np.square(z))


def coloc_posteriors(l1: np.ndarray, l2: np.ndarray, p12: float) -> tuple[np.ndarray, np.ndarray]:
    a1 = float(logsumexp(l1))
    a2 = float(logsumexp(l2))
    a12 = float(logsumexp(l1 + l2))
    log_h = np.array(
        [
            0.0,
            math.log(1e-4) + a1,
            math.log(1e-4) + a2,
            math.log(1e-4) + math.log(1e-4) + logdiff(a1 + a2, a12),
            math.log(p12) + a12,
        ]
    )
    return np.exp(log_h - logsumexp(log_h)), l1 + l2


def estimate_sdy(vbeta: np.ndarray, maf: np.ndarray, n: int) -> float:
    one_over = 1.0 / np.asarray(vbeta, dtype=np.float64)
    nvx = 2.0 * float(n) * np.asarray(maf, dtype=np.float64) * (1.0 - np.asarray(maf, dtype=np.float64))
    cf = float(np.sum(one_over * nvx) / np.sum(np.square(one_over)))
    if not np.isfinite(cf) or cf <= 0:
        raise ValueError("invalid sdY estimate")
    return math.sqrt(cf)


def read_fam() -> tuple[list[str], dict[str, int]]:
    fam = pd.read_csv(FAM, sep=r"\s+", header=None, dtype=str)
    ids = fam.iloc[:, 1].tolist()
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate FAM sample IDs")
    return ids, {sample: i for i, sample in enumerate(ids)}


def decode_bed_union(variant_gi: np.ndarray, n_samples: int) -> np.ndarray:
    """Decode requested BIM rows once; missing values remain NaN for cell-wise imputation."""
    bytes_per_snp = (n_samples + 3) // 4
    out = np.empty((len(variant_gi), n_samples), dtype=np.float32)
    with BED.open("rb") as handle:
        if handle.read(3) != bytes.fromhex("6c1b01"):
            raise RuntimeError("BED is not SNP-major PLINK v1")
        for row_i, gi in enumerate(variant_gi.astype(np.int64)):
            handle.seek(3 + int(gi) * bytes_per_snp)
            raw = handle.read(bytes_per_snp)
            if len(raw) != bytes_per_snp:
                raise RuntimeError(f"truncated BED at gi={gi}")
            codes = np.fromiter(
                ((byte >> shift) & 3 for byte in raw for shift in (0, 2, 4, 6)),
                dtype=np.int8,
                count=bytes_per_snp * 4,
            )[:n_samples]
            out[row_i] = np.where(codes == 0, 2.0, np.where(codes == 2, 1.0, np.where(codes == 3, 0.0, np.nan)))
    return out


def read_cell_expression(cell: str, wanted: set[str]) -> tuple[list[str], dict[str, np.ndarray], dict[str, int]]:
    with zipfile.ZipFile(GENE_ZIP) as gene_zip:
        member = f"{cell}_cells_gene_list.txt"
        with gene_zip.open(member) as handle:
            genes = [line.decode("utf-8", "replace").strip() for line in handle]
    genes = [gene for gene in genes[1:] if gene]
    row_to_gene = {i: gene for i, gene in enumerate(genes) if gene in wanted}
    if set(row_to_gene.values()) != wanted:
        missing = sorted(wanted - set(row_to_gene.values()))
        raise RuntimeError(f"{cell}: requested genes absent from gene list: {missing[:10]}")

    selected: dict[str, np.ndarray] = {}
    selected_rows: dict[str, int] = {}
    with zipfile.ZipFile(PHENO_ZIP) as pheno_zip:
        member = f"{cell}_cells_mean_mx.txt"
        with pheno_zip.open(member) as handle:
            header = handle.readline().decode("utf-8", "replace").strip().split()
            first_line = handle.readline()
            first = np.fromstring(first_line.decode("utf-8", "replace").replace("NA", "nan"), sep=" ")
            if first.size != len(header):
                raise RuntimeError(f"{cell}: expression first-row width mismatch")
            active = np.isfinite(first)
            if 0 in row_to_gene:
                selected[row_to_gene[0]] = first[active]
                selected_rows[row_to_gene[0]] = 0
            for row_i, raw in enumerate(handle, start=1):
                gene = row_to_gene.get(row_i)
                if gene is None:
                    continue
                values = np.fromstring(raw.decode("utf-8", "replace").replace("NA", "nan"), sep=" ")
                if values.size != len(header):
                    raise RuntimeError(f"{cell}/{gene}: expression row width mismatch")
                values = values[active]
                if not np.isfinite(values).all():
                    raise RuntimeError(f"{cell}/{gene}: missing value after source active-donor filter")
                selected[gene] = values
                selected_rows[gene] = row_i
    if set(selected) != wanted:
        raise RuntimeError(f"{cell}: failed to recover all requested expression rows")
    active_ids = [sample for sample, keep in zip(header, active) if keep]
    for gene, values in selected.items():
        y = np.log1p(values.astype(np.float64))
        sd = float(y.std(ddof=1))
        if not np.isfinite(sd) or sd <= 0:
            raise RuntimeError(f"{cell}/{gene}: expression has zero variance")
        selected[gene] = (y - y.mean()) / sd
    return active_ids, selected, selected_rows


def build_q(covariates: np.ndarray) -> np.ndarray:
    centered = covariates - covariates.mean(axis=0)
    q, r = np.linalg.qr(centered, mode="reduced")
    if np.linalg.matrix_rank(r) != covariates.shape[1]:
        raise RuntimeError("PF10 covariates are rank deficient")
    return q


def residualize_y(y: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, float]:
    centered = y - y.mean()
    residual = centered - (centered @ q) @ q.T
    variance = float(residual.var(ddof=1))
    if not np.isfinite(variance) or variance <= 0:
        raise RuntimeError("non-variable residual phenotype")
    return residual, variance


def residualize_g(genotypes: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    g = np.asarray(genotypes, dtype=np.float64)
    if np.isnan(g).any():
        means = np.nanmean(g, axis=1)
        if np.isnan(means).any():
            raise RuntimeError("all-missing genotype in active donors")
        missing = np.where(np.isnan(g))
        g[missing] = means[missing[0]]
    af = g.sum(axis=1) / (2.0 * g.shape[1])
    centered = g - g.mean(axis=1, keepdims=True)
    residual = centered - (centered @ q) @ q.T
    variance = residual.var(axis=1, ddof=1)
    return residual, variance, af


def main() -> None:
    started = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    QTL_OUT.mkdir(parents=True, exist_ok=True)
    comparisons = pd.read_csv(COMPARE, sep="\t")
    disease = pd.read_csv(DISEASE, sep="\t").sort_values(["locus_index", "position_GRCh37"])
    if len(comparisons) != 6923 or comparisons["comparison_id"].duplicated().any():
        raise RuntimeError("frozen comparison universe is not exact 6923 unique rows")
    if disease.duplicated(["locus_index", "variant_id"]).any():
        raise RuntimeError("duplicate disease locus-variant keys")

    fam_ids, fam_index = read_fam()
    union = disease[["variant_id", "gi"]].drop_duplicates("variant_id").sort_values("gi")
    if union["gi"].duplicated().any():
        raise RuntimeError("different variant IDs share a BIM index")
    print(f"Decoding {len(union):,} unique disease-aligned variants from BED", flush=True)
    g_union = decode_bed_union(union["gi"].to_numpy(), len(fam_ids))
    union_row = {variant: i for i, variant in enumerate(union["variant_id"].astype(str))}
    locus_data: dict[int, tuple[pd.DataFrame, np.ndarray]] = {}
    for locus, frame in disease.groupby("locus_index", sort=True):
        rows = np.array([union_row[value] for value in frame["variant_id"].astype(str)], dtype=int)
        locus_data[int(locus)] = (frame.reset_index(drop=True), rows)

    results: list[dict[str, object]] = []
    qtl_cache: dict[str, pd.DataFrame] = {}
    cell_receipts: list[dict[str, object]] = []
    cells = sorted(comparisons["cell_type"].unique())
    for cell_i, cell in enumerate(cells, start=1):
        cell_frame = comparisons[comparisons["cell_type"] == cell].copy()
        wanted = set(cell_frame["gene"].astype(str))
        active_ids, expression, expression_rows = read_cell_expression(cell, wanted)
        frozen_samples = [line for line in (SAMPLE_DIR / f"{cell}.samples.txt").read_text(encoding="utf-8").splitlines() if line]
        if active_ids != frozen_samples:
            raise RuntimeError(f"{cell}: expression active donors differ from frozen donor list")
        if any(sample not in fam_index for sample in active_ids):
            raise RuntimeError(f"{cell}: active donor absent from FAM")
        keep = np.array([fam_index[sample] for sample in active_ids], dtype=int)
        cov_path = COV_DIR / f"{cell}_mx_pf50.txt"
        cov = pd.read_csv(cov_path, sep=r"\s+", dtype={"sampleid": str}).set_index("sampleid")
        cov = cov.loc[active_ids, PF10_COV]
        if cov.index.tolist() != active_ids or not np.isfinite(cov.to_numpy(dtype=float)).all():
            raise RuntimeError(f"{cell}: covariate donor order or values invalid")
        q = build_q(cov.to_numpy(dtype=np.float64))
        y_residual = {gene: residualize_y(values, q) for gene, values in expression.items()}
        cell_receipts.append(
            {
                "cell_type": cell,
                "active_donor_N": len(active_ids),
                "frozen_comparisons": len(cell_frame),
                "target_genes": len(wanted),
                "covariate_columns": ",".join(PF10_COV),
                "covariate_sha256": sha256(cov_path),
                "active_donor_sha256": sha256(SAMPLE_DIR / f"{cell}.samples.txt"),
            }
        )
        for locus, jobs in cell_frame.groupby("locus_index", sort=True):
            d, union_rows = locus_data[int(locus)]
            g_residual, g_variance, af = residualize_g(g_union[union_rows][:, keep], q)
            valid_g = np.isfinite(g_variance) & (g_variance > 0) & np.isfinite(af) & (af > 0) & (af < 1)
            for job in jobs.itertuples(index=False):
                tss = int(job.gene_tss_GRCh37)
                position = d["position_GRCh37"].to_numpy(dtype=int)
                mask = valid_g & (position >= tss - 1_000_000) & (position <= tss + 1_000_000)
                n_variants = int(mask.sum())
                ids = d.loc[mask, "variant_id"].astype(str).tolist()
                base = {
                    "comparison_id": str(job.comparison_id),
                    "locus_index": int(locus),
                    "chromosome": int(job.chromosome),
                    "gene": str(job.gene),
                    "cell_type": cell,
                    "gene_tss_GRCh37": tss,
                    "gene_min_source_qval": float(job.gene_min_source_qval),
                    "cell_source_qval": float(job.source_qval),
                    "source_cell_q_lt_0_05": bool(job.source_cell_q_lt_0_05),
                    "qtl_N": len(active_ids),
                    "expression_gene_row_zero_based": int(expression_rows[str(job.gene)]),
                    "n_variants": n_variants,
                    "variant_set_sha256": hash_variant_set(ids),
                    "model": "CURRENT_RELEASE_PF10",
                    "implementation": "TensorQTL_1.0.10_formula_compatible_numpy",
                }
                if n_variants < MIN_VARIANTS:
                    results.append({**base, "classification": "INSUFFICIENT_VARIANT_OVERLAP"})
                    continue
                yres, yvar = y_residual[str(job.gene)]
                gres = g_residual[mask]
                gv = g_variance[mask]
                denom = np.sqrt(np.sum(np.square(gres), axis=1) * np.sum(np.square(yres)))
                r = np.clip((gres @ yres) / denom, -1 + 1e-15, 1 - 1e-15)
                dof = len(active_ids) - 2 - len(PF10_COV)
                tstat = r * np.sqrt(dof / (1.0 - np.square(r)))
                slope = r * np.sqrt(yvar / gv)
                slope_se = np.divide(slope, tstat, out=np.sqrt(yvar / gv) / np.sqrt(dof) * np.ones_like(slope), where=tstat != 0)
                pvalue = 2.0 * student_t.sf(np.abs(tstat), dof)
                dsub = d.loc[mask].reset_index(drop=True)
                maf = np.minimum(af[mask], 1.0 - af[mask])
                sdy = estimate_sdy(np.square(slope_se), maf, len(active_ids))
                l_disease = log_abf(dsub["beta_A1"].to_numpy(float), dsub["standard_error"].to_numpy(float), 0.2)
                l_qtl = log_abf(slope, slope_se, 0.15 * sdy)
                posteriors: dict[float, np.ndarray] = {}
                ratios: dict[float, float] = {}
                combined = None
                for p12 in P12_GRID:
                    posterior, signal = coloc_posteriors(l_disease, l_qtl, p12)
                    posteriors[p12] = posterior
                    ratios[p12] = float(posterior[4] / (posterior[3] + posterior[4])) if posterior[3] + posterior[4] > 0 else np.nan
                    if p12 == 1e-5:
                        combined = signal
                default = posteriors[1e-5]
                h34 = float(default[3] + default[4])
                robust = bool(default[4] >= 0.80 and ratios[1e-5] >= 0.80)
                ambiguous = bool((not robust) and h34 >= 0.80 and 0.20 <= ratios[1e-5] <= 0.80)
                if robust:
                    classification = "ROBUST_H4_TRIGGER"
                elif ambiguous:
                    classification = "H3_H4_AMBIGUITY_TRIGGER"
                elif h34 >= 0.80 and ratios[1e-5] < 0.20:
                    classification = "H3_DISTINCT_SIGNAL"
                else:
                    classification = "NO_TRIGGER_OR_UNINFORMATIVE"
                shared_probability = np.exp(combined - logsumexp(combined))
                shared_i = int(np.argmax(shared_probability))
                result = {
                    **base,
                    "sdY_estimate": sdy,
                    "disease_min_p": float(dsub["p_value"].min()),
                    "qtl_min_p": float(np.min(pvalue)),
                    "qtl_top_variant": str(dsub.loc[int(np.argmin(pvalue)), "variant_id"]),
                    "PP_H0": float(default[0]),
                    "PP_H1": float(default[1]),
                    "PP_H2": float(default[2]),
                    "PP_H3": float(default[3]),
                    "PP_H4": float(default[4]),
                    "H3_plus_H4": h34,
                    "H4_over_H3H4": ratios[1e-5],
                    "H4_p12_1e_6": float(posteriors[1e-6][4]),
                    "H4ratio_p12_1e_6": ratios[1e-6],
                    "H4_p12_1e_4": float(posteriors[1e-4][4]),
                    "H4ratio_p12_1e_4": ratios[1e-4],
                    "shared_top_variant": str(dsub.loc[shared_i, "variant_id"]),
                    "shared_top_SNP_PP_H4_conditional": float(shared_probability[shared_i]),
                    "classification": classification,
                }
                results.append(result)
                if robust or ambiguous:
                    qtl = dsub[["locus_index", "chromosome", "variant_id", "position_GRCh37", "BIM_A1", "BIM_A2", "gi"]].copy()
                    qtl["gene"] = str(job.gene)
                    qtl["cell_type"] = cell
                    qtl["n_expression_donors"] = len(active_ids)
                    qtl["af_A1"] = af[mask]
                    qtl["slope_A1"] = slope
                    qtl["slope_se"] = slope_se
                    qtl["z"] = tstat
                    qtl["pval_nominal"] = pvalue
                    qtl["mode"] = "PF10"
                    qtl["implementation"] = "TensorQTL_1.0.10_formula_compatible_numpy"
                    qtl_cache[str(job.comparison_id)] = qtl
        print(f"CELL_DONE {cell_i}/{len(cells)} {cell} comparisons={len(cell_frame)}", flush=True)

    result_frame = pd.DataFrame(results).sort_values("comparison_id")
    if len(result_frame) != len(comparisons) or result_frame["comparison_id"].duplicated().any():
        raise RuntimeError("result key set does not exactly match frozen comparison universe")
    if set(result_frame["comparison_id"]) != set(comparisons["comparison_id"]):
        raise RuntimeError("result comparison IDs differ from frozen universe")
    result_path = OUT / "R7B1_current_PF10_ABF_all_comparisons.tsv.gz"
    result_frame.to_csv(result_path, sep="\t", index=False, compression="gzip")
    triggers = result_frame[result_frame["classification"].isin(["ROBUST_H4_TRIGGER", "H3_H4_AMBIGUITY_TRIGGER"])].copy()
    trigger_path = OUT / "R7B1_multisignal_trigger_set.tsv"
    triggers.to_csv(trigger_path, sep="\t", index=False)
    for comparison_id in triggers["comparison_id"].astype(str):
        qtl_cache[comparison_id].to_csv(QTL_OUT / f"{comparison_id}_PF10_QTL.tsv.gz", sep="\t", index=False, compression="gzip")
    pd.DataFrame(cell_receipts).to_csv(OUT / "R7B1_current_PF10_cell_model_receipts.tsv", sep="\t", index=False)
    counts = Counter(result_frame["classification"])
    state = {
        "schema": "R7B1_CURRENT_PF10_ABF_1.0",
        "status": "COMPLETE_TRIGGER_SET_FROZEN",
        "frozen_comparisons": int(len(comparisons)),
        "observed_results": int(len(result_frame)),
        "cells": len(cells),
        "loci": int(comparisons["locus_index"].nunique()),
        "genes": int(comparisons["gene"].nunique()),
        "class_counts": dict(sorted(counts.items())),
        "trigger_comparisons": int(len(triggers)),
        "trigger_loci": int(triggers["locus_index"].nunique()),
        "trigger_genes": int(triggers["gene"].nunique()),
        "trigger_cells": int(triggers["cell_type"].nunique()),
        "runtime_seconds": round(time.time() - started, 3),
        "inputs": {
            "comparison_universe_sha256": sha256(COMPARE),
            "disease_harmonized_sha256": sha256(DISEASE),
            "pseudobulk_zip_sha256": sha256(PHENO_ZIP),
            "gene_list_zip_sha256": sha256(GENE_ZIP),
            "bed_sha256": sha256(BED),
            "fam_sha256": sha256(FAM),
        },
        "outputs": {
            "all_comparisons_sha256": sha256(result_path),
            "trigger_set_sha256": sha256(trigger_path),
        },
        "posterior_read_before_universe_freeze": False,
        "primary_model": "current-release PF10",
        "next": "R7B1B_CURRENT_PF50_AND_SOURCE_MATCHED_MULTISIGNAL_FOR_EXACT_TRIGGER_SET" if len(triggers) else "R7B1_EXIT_NO_SIGNAL_LEVEL_TRIGGERS",
    }
    (OUT / "R7B1_current_PF10_ABF_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2), flush=True)


if __name__ == "__main__":
    main()
