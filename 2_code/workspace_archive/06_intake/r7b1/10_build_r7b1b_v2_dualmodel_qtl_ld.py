#!/usr/bin/env python3
"""Build source-matched PF10/PF50 QTL summaries and reusable LD blocks.

This is the de-novo execution layer for the pre-result-frozen R7B1B v2
high-information cohort.  Genotypes are decoded once, expression and
covariates are read from the public 2026 OneK1K release, and LD is shared at
the cell-locus level instead of duplicated for every gene.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
WORKLOAD = ROOT / "3_results/00_audit/R7B1B_v2/R7B1B_v2_exact_642_high_information_comparisons.tsv"
BLOCKS = ROOT / "3_results/00_audit/R7B1B_v2/R7B1B_v2_exact_286_cell_locus_blocks.tsv"
DISEASE = ROOT / "3_results/01_gwas/R7B1/R7B1_PBC56_GRCh37_BIM_A1.tsv.gz"
PHENO_ZIP = ROOT / "1_data/qtl/OneK1K/OneK1K_pseudobulk_mean_mx.zip"
GENE_ZIP = ROOT / "1_data/qtl/OneK1K/OneK1K_pseudobulk_mx_gene_list.zip"
PLINK = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors"
BED = PLINK / "plink_merged_980_donors.bed"
FAM = PLINK / "plink_merged_980_donors.fam"
COV_DIR = ROOT / "1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors"
SAMPLE_DIR = ROOT / "3_results/03_qtl/R5A2A2/cell_sample_lists"
OLD_QTL_DIR = ROOT / "3_results/03_qtl/R7B1/pf10_trigger_qtl"
OUT_QTL = ROOT / "3_results/03_qtl/R7B1B_v2/dualmodel_qtl"
OUT_LD = ROOT / "3_results/04_integration/R7B1B_v2/sourceLD_blocks"
OUT_AUDIT = ROOT / "3_results/00_audit/R7B1B_v2"

BASE_COV = ["sex"] + [f"pc{i}" for i in range(1, 7)] + ["age"]
COVARIATE_SETS = {
    "PF10": BASE_COV + [f"pf{i}" for i in range(1, 11)],
    "PF50": BASE_COV + [f"pf{i}" for i in range(1, 51)],
}
MIN_VARIANTS = 200


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def hash_variant_set(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(values) + "\n").encode("utf-8")).hexdigest()


def read_fam() -> tuple[list[str], dict[str, int]]:
    fam = pd.read_csv(FAM, sep=r"\s+", header=None, dtype=str)
    ids = fam.iloc[:, 1].tolist()
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate FAM sample IDs")
    return ids, {sample: i for i, sample in enumerate(ids)}


def decode_bed_union(variant_gi: np.ndarray, n_samples: int) -> np.ndarray:
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
        with gene_zip.open(f"{cell}_cells_gene_list.txt") as handle:
            genes = [line.decode("utf-8", "replace").strip() for line in handle]
    genes = [gene for gene in genes[1:] if gene]
    row_to_gene = {i: gene for i, gene in enumerate(genes) if gene in wanted}
    if set(row_to_gene.values()) != wanted:
        raise RuntimeError(f"{cell}: missing expression genes {sorted(wanted-set(row_to_gene.values()))[:10]}")
    selected: dict[str, np.ndarray] = {}
    selected_rows: dict[str, int] = {}
    with zipfile.ZipFile(PHENO_ZIP) as pheno_zip:
        with pheno_zip.open(f"{cell}_cells_mean_mx.txt") as handle:
            header = handle.readline().decode("utf-8", "replace").strip().split()
            first = np.fromstring(handle.readline().decode("utf-8", "replace").replace("NA", "nan"), sep=" ")
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
                    raise RuntimeError(f"{cell}/{gene}: missing value after active-donor filter")
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


def build_q(covariates: np.ndarray, label: str) -> tuple[np.ndarray, int]:
    centered = covariates - covariates.mean(axis=0)
    q, r = np.linalg.qr(centered, mode="reduced")
    rank = int(np.linalg.matrix_rank(r))
    if rank != covariates.shape[1]:
        raise RuntimeError(f"{label}: covariates are rank deficient ({rank}/{covariates.shape[1]})")
    return q, rank


def residualize_y(y: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, float]:
    centered = y - y.mean()
    residual = centered - (centered @ q) @ q.T
    variance = float(residual.var(ddof=1))
    if not np.isfinite(variance) or variance <= 0:
        raise RuntimeError("non-variable residual phenotype")
    return residual, variance


def impute_and_af(genotypes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    g = np.asarray(genotypes, dtype=np.float64).copy()
    if np.isnan(g).any():
        means = np.nanmean(g, axis=1)
        if np.isnan(means).any():
            raise RuntimeError("all-missing genotype in active donors")
        missing = np.where(np.isnan(g))
        g[missing] = means[missing[0]]
    return g, g.sum(axis=1) / (2.0 * g.shape[1])


def residualize_g(g: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    centered = g - g.mean(axis=1, keepdims=True)
    residual = centered - (centered @ q) @ q.T
    return residual, residual.var(axis=1, ddof=1)


def association(gres: np.ndarray, gv: np.ndarray, yres: np.ndarray, yvar: float, n: int, cov_n: int) -> tuple[np.ndarray, ...]:
    denom = np.sqrt(np.sum(np.square(gres), axis=1) * np.sum(np.square(yres)))
    r = np.clip((gres @ yres) / denom, -1 + 1e-15, 1 - 1e-15)
    dof = n - 2 - cov_n
    if dof <= 0:
        raise RuntimeError(f"non-positive association degrees of freedom: {dof}")
    tstat = r * np.sqrt(dof / (1.0 - np.square(r)))
    slope = r * np.sqrt(yvar / gv)
    default_se = np.sqrt(yvar / gv) / np.sqrt(dof)
    slope_se = np.divide(slope, tstat, out=default_se.copy(), where=tstat != 0)
    pvalue = 2.0 * student_t.sf(np.abs(tstat), dof)
    return slope, slope_se, tstat, pvalue


def write_binary_ld(path: Path, matrix: np.ndarray) -> None:
    matrix = np.asarray(matrix, dtype=np.float32, order="C")
    matrix.tofile(path)


def main() -> None:
    started = time.time()
    for directory in (OUT_QTL, OUT_LD, OUT_AUDIT):
        directory.mkdir(parents=True, exist_ok=True)
    work = pd.read_csv(WORKLOAD, sep="\t", dtype={"comparison_id": str})
    blocks = pd.read_csv(BLOCKS, sep="\t")
    disease = pd.read_csv(DISEASE, sep="\t").sort_values(["locus_index", "position_GRCh37"])
    if len(work) != 642 or work["comparison_id"].duplicated().any():
        raise RuntimeError("workload is not exact 642 unique comparisons")
    if len(blocks) != 286 or blocks.duplicated(["cell_type", "locus_index"]).any():
        raise RuntimeError("block table is not exact 286 unique cell-locus blocks")
    if disease.duplicated(["locus_index", "variant_id"]).any():
        raise RuntimeError("duplicate disease locus-variant keys")

    fam_ids, fam_index = read_fam()
    needed_loci = set(work["locus_index"].astype(int))
    disease = disease[disease["locus_index"].isin(needed_loci)].copy()
    union = disease[["variant_id", "gi"]].drop_duplicates("variant_id").sort_values("gi")
    if union["gi"].duplicated().any():
        raise RuntimeError("different variant IDs share a BIM index")
    print(f"Decoding {len(union):,} unique variants", flush=True)
    g_union = decode_bed_union(union["gi"].to_numpy(), len(fam_ids))
    union_row = {variant: i for i, variant in enumerate(union["variant_id"].astype(str))}
    locus_data: dict[int, tuple[pd.DataFrame, np.ndarray]] = {}
    for locus, frame in disease.groupby("locus_index", sort=True):
        rows = np.array([union_row[value] for value in frame["variant_id"].astype(str)], dtype=int)
        locus_data[int(locus)] = (frame.reset_index(drop=True), rows)

    comparison_receipts: list[dict[str, object]] = []
    block_receipts: list[dict[str, object]] = []
    regression_receipts: list[dict[str, object]] = []
    cell_receipts: list[dict[str, object]] = []
    cells = sorted(work["cell_type"].unique())
    for cell_i, cell in enumerate(cells, start=1):
        cell_work = work[work["cell_type"] == cell].copy()
        wanted = set(cell_work["gene"].astype(str))
        active_ids, expression, expression_rows = read_cell_expression(cell, wanted)
        frozen_samples = [x for x in (SAMPLE_DIR / f"{cell}.samples.txt").read_text(encoding="utf-8").splitlines() if x]
        if active_ids != frozen_samples:
            raise RuntimeError(f"{cell}: active donors differ from frozen list")
        if any(sample not in fam_index for sample in active_ids):
            raise RuntimeError(f"{cell}: active donor absent from FAM")
        keep = np.array([fam_index[sample] for sample in active_ids], dtype=int)
        cov_path = COV_DIR / f"{cell}_mx_pf50.txt"
        cov = pd.read_csv(cov_path, sep=r"\s+", dtype={"sampleid": str}).set_index("sampleid")
        cov = cov.loc[active_ids]
        q_by_mode: dict[str, np.ndarray] = {}
        rank_by_mode: dict[str, int] = {}
        y_by_mode: dict[str, dict[str, tuple[np.ndarray, float]]] = {}
        for mode, cols in COVARIATE_SETS.items():
            cm = cov[cols].apply(pd.to_numeric).to_numpy(dtype=np.float64)
            if not np.isfinite(cm).all():
                raise RuntimeError(f"{cell}/{mode}: non-finite covariate")
            q_by_mode[mode], rank_by_mode[mode] = build_q(cm, f"{cell}/{mode}")
            y_by_mode[mode] = {gene: residualize_y(values, q_by_mode[mode]) for gene, values in expression.items()}
        cell_receipts.append({
            "cell_type": cell,
            "active_donor_N": len(active_ids),
            "comparisons": len(cell_work),
            "blocks": int(cell_work["locus_index"].nunique()),
            "genes": len(wanted),
            "PF10_rank": rank_by_mode["PF10"],
            "PF50_rank": rank_by_mode["PF50"],
            "covariate_sha256": sha256(cov_path),
            "donor_sha256": sha256(SAMPLE_DIR / f"{cell}.samples.txt"),
        })
        for locus, jobs in cell_work.groupby("locus_index", sort=True):
            locus = int(locus)
            d, union_rows = locus_data[locus]
            g, af = impute_and_af(g_union[union_rows][:, keep])
            mode_g: dict[str, tuple[np.ndarray, np.ndarray]] = {
                mode: residualize_g(g, q) for mode, q in q_by_mode.items()
            }
            valid = np.isfinite(af) & (af > 0) & (af < 1)
            for _, gv in mode_g.values():
                valid &= np.isfinite(gv) & (gv > 0)
            positions = d["position_GRCh37"].to_numpy(dtype=int)
            masks: dict[str, np.ndarray] = {}
            union_mask = np.zeros(len(d), dtype=bool)
            for job in jobs.itertuples(index=False):
                mask = valid & (positions >= int(job.gene_tss_GRCh37) - 1_000_000) & (positions <= int(job.gene_tss_GRCh37) + 1_000_000)
                ids = d.loc[mask, "variant_id"].astype(str).tolist()
                if int(mask.sum()) != int(job.n_variants):
                    raise RuntimeError(f"{job.comparison_id}: variant count drift {mask.sum()} != {job.n_variants}")
                if hash_variant_set(ids) != str(job.variant_set_sha256):
                    raise RuntimeError(f"{job.comparison_id}: variant identity drift")
                masks[str(job.comparison_id)] = mask
                union_mask |= mask
            block_dir = OUT_LD / f"L{locus:02d}_{cell}"
            block_dir.mkdir(parents=True, exist_ok=True)
            block_meta = d.loc[union_mask, [
                "locus_index", "chromosome", "variant_id", "position_GRCh37", "BIM_A1", "BIM_A2", "gi", "rsid"
            ]].copy()
            block_meta.insert(0, "block_order_zero_based", np.arange(len(block_meta), dtype=int))
            block_meta_path = block_dir / "variants.tsv.gz"
            block_meta.to_csv(block_meta_path, sep="\t", index=False, compression="gzip")
            mode_qc: dict[str, object] = {}
            for mode, (gres_all, gv_all) in mode_g.items():
                gres = gres_all[union_mask]
                sd = np.sqrt(gv_all[union_mask])
                z = gres / sd[:, None]
                corr = (z @ z.T) / (len(active_ids) - 1)
                corr = (corr + corr.T) / 2.0
                np.fill_diagonal(corr, 1.0)
                ld_path = block_dir / f"{mode}_residualized_A1_correlation.float32.bin"
                write_binary_ld(ld_path, corr)
                mode_qc[mode] = {
                    "covariates": len(COVARIATE_SETS[mode]),
                    "design_rank": rank_by_mode[mode],
                    "residual_df": len(active_ids) - rank_by_mode[mode],
                    "max_asymmetry": float(np.max(np.abs(corr - corr.T))),
                    "max_diagonal_deviation": float(np.max(np.abs(np.diag(corr) - 1.0))),
                    "ld_bytes": ld_path.stat().st_size,
                    "ld_sha256": sha256(ld_path),
                }
                if ld_path.stat().st_size != len(block_meta) * len(block_meta) * 4:
                    raise RuntimeError(f"{locus}/{cell}/{mode}: binary LD byte size mismatch")
            block_state = {
                "schema": "R7B1B_V2_SOURCE_LD_BLOCK_1.0",
                "locus_index": locus,
                "cell_type": cell,
                "qtl_N": len(active_ids),
                "comparisons": len(jobs),
                "genes": int(jobs["gene"].nunique()),
                "block_variants": len(block_meta),
                "variant_metadata_sha256": sha256(block_meta_path),
                "variant_set_sha256": hash_variant_set(block_meta["variant_id"].astype(str).tolist()),
                "modes": mode_qc,
                "gate_pass": all(
                    q["design_rank"] == q["covariates"]
                    and q["max_asymmetry"] <= 1e-6
                    and q["max_diagonal_deviation"] <= 1e-6
                    for q in mode_qc.values()
                ),
            }
            (block_dir / "block_QC.json").write_text(json.dumps(block_state, indent=2), encoding="utf-8")
            if not block_state["gate_pass"]:
                raise RuntimeError(f"{locus}/{cell}: source-LD block QC failed")
            block_receipts.append({
                "cell_locus_block_id": f"L{locus:02d}_{cell}",
                "locus_index": locus,
                "cell_type": cell,
                "qtl_N": len(active_ids),
                "comparisons": len(jobs),
                "genes": int(jobs["gene"].nunique()),
                "block_variants": len(block_meta),
                "block_state_sha256": sha256(block_dir / "block_QC.json"),
                "gate_pass": True,
            })

            for job in jobs.itertuples(index=False):
                comparison_id = str(job.comparison_id)
                mask = masks[comparison_id]
                dsub = d.loc[mask].reset_index(drop=True)
                maf = np.minimum(af[mask], 1.0 - af[mask])
                for mode, (gres_all, gv_all) in mode_g.items():
                    yres, yvar = y_by_mode[mode][str(job.gene)]
                    slope, slope_se, tstat, pvalue = association(
                        gres_all[mask], gv_all[mask], yres, yvar, len(active_ids), len(COVARIATE_SETS[mode])
                    )
                    qtl = dsub[[
                        "locus_index", "chromosome", "variant_id", "position_GRCh37", "BIM_A1", "BIM_A2", "gi", "rsid"
                    ]].copy()
                    qtl["comparison_id"] = comparison_id
                    qtl["gene"] = str(job.gene)
                    qtl["cell_type"] = cell
                    qtl["n_expression_donors"] = len(active_ids)
                    qtl["af_A1"] = af[mask]
                    qtl["maf"] = maf
                    qtl["slope_A1"] = slope
                    qtl["slope_se"] = slope_se
                    qtl["z"] = tstat
                    qtl["pval_nominal"] = pvalue
                    qtl["mode"] = mode
                    qtl["implementation"] = "TensorQTL_1.0.10_formula_compatible_numpy"
                    qtl_path = OUT_QTL / f"{comparison_id}_{mode}_QTL.tsv.gz"
                    qtl.to_csv(qtl_path, sep="\t", index=False, compression="gzip")
                    comparison_receipts.append({
                        "comparison_id": comparison_id,
                        "locus_index": locus,
                        "gene": str(job.gene),
                        "cell_type": cell,
                        "mode": mode,
                        "qtl_N": len(active_ids),
                        "n_variants": len(qtl),
                        "variant_set_sha256": hash_variant_set(qtl["variant_id"].astype(str).tolist()),
                        "qtl_sha256": sha256(qtl_path),
                        "min_p": float(np.min(pvalue)),
                    })
                    old = OLD_QTL_DIR / f"{comparison_id}_PF10_QTL.tsv.gz"
                    if mode == "PF10" and old.exists():
                        oldq = pd.read_csv(old, sep="\t")
                        merged = qtl.merge(oldq[["variant_id", "slope_A1", "slope_se", "z", "pval_nominal"]], on="variant_id", suffixes=("_new", "_old"))
                        if len(merged) != len(qtl) or len(oldq) != len(qtl):
                            raise RuntimeError(f"{comparison_id}: old/new PF10 variant identity mismatch")
                        diffs = {
                            col: float(np.max(np.abs(merged[f"{col}_new"] - merged[f"{col}_old"])))
                            for col in ("slope_A1", "slope_se", "z", "pval_nominal")
                        }
                        if diffs["slope_A1"] > 1e-10 or diffs["slope_se"] > 1e-10 or diffs["z"] > 1e-9 or diffs["pval_nominal"] > 1e-10:
                            raise RuntimeError(f"{comparison_id}: PF10 regression mismatch {diffs}")
                        regression_receipts.append({"comparison_id": comparison_id, **diffs, "pass": True})
        print(f"CELL_DONE {cell_i}/{len(cells)} {cell} comparisons={len(cell_work)}", flush=True)

    comp = pd.DataFrame(comparison_receipts).sort_values(["comparison_id", "mode"])
    block = pd.DataFrame(block_receipts).sort_values(["locus_index", "cell_type"])
    cell = pd.DataFrame(cell_receipts).sort_values("cell_type")
    regression = pd.DataFrame(regression_receipts).sort_values("comparison_id")
    if len(comp) != 1284 or comp.duplicated(["comparison_id", "mode"]).any():
        raise RuntimeError("QTL receipts are not exact 642 x 2")
    if len(block) != 286 or block.duplicated(["locus_index", "cell_type"]).any():
        raise RuntimeError("LD receipts are not exact 286 blocks")
    if set(map(tuple, block[["locus_index", "cell_type"]].to_numpy())) != set(map(tuple, blocks[["locus_index", "cell_type"]].to_numpy())):
        raise RuntimeError("realized block key set differs from frozen 286")
    comp_path = OUT_AUDIT / "R7B1B_v2_dualmodel_QTL_receipts.tsv"
    block_path = OUT_AUDIT / "R7B1B_v2_sourceLD_block_receipts.tsv"
    cell_path = OUT_AUDIT / "R7B1B_v2_cell_model_receipts.tsv"
    regression_path = OUT_AUDIT / "R7B1B_v2_original184_PF10_regression_QA.tsv"
    comp.to_csv(comp_path, sep="\t", index=False)
    block.to_csv(block_path, sep="\t", index=False)
    cell.to_csv(cell_path, sep="\t", index=False)
    regression.to_csv(regression_path, sep="\t", index=False)
    state = {
        "schema": "R7B1B_V2_DUALMODEL_SOURCE_LD_1.0",
        "status": "PASS",
        "comparisons": 642,
        "qtl_summaries": 1284,
        "cell_locus_blocks": 286,
        "cells": len(cells),
        "loci": int(work["locus_index"].nunique()),
        "original184_pf10_regression_checks": len(regression),
        "runtime_seconds": round(time.time() - started, 3),
        "inputs": {
            "workload_sha256": sha256(WORKLOAD),
            "blocks_sha256": sha256(BLOCKS),
            "disease_sha256": sha256(DISEASE),
            "pseudobulk_sha256": sha256(PHENO_ZIP),
            "gene_list_sha256": sha256(GENE_ZIP),
            "bed_sha256": sha256(BED),
            "fam_sha256": sha256(FAM),
        },
        "outputs": {
            "qtl_receipts_sha256": sha256(comp_path),
            "block_receipts_sha256": sha256(block_path),
            "cell_receipts_sha256": sha256(cell_path),
            "regression_QA_sha256": sha256(regression_path),
        },
        "posterior_multisignal_read_before_input_build": False,
        "next": "R7B1B_V2_642_SOURCE_MATCHED_SUSIE_COLOC",
    }
    state_path = OUT_AUDIT / "R7B1B_v2_dualmodel_sourceLD_state.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2), flush=True)


if __name__ == "__main__":
    main()
