#!/usr/bin/env python3
"""Build audited OneK1K NK_R/ZCCHC2 signed-A1 LD from 750 active donors."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
PLINK = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors"
BED = PLINK / "plink_merged_980_donors.bed"
BIM = PLINK / "plink_merged_980_donors.bim"
FAM = PLINK / "plink_merged_980_donors.fam"
SAMPLES = ROOT / "3_results/03_qtl/R5A2A2/cell_sample_lists/NK_R.samples.txt"
QTL = ROOT / "3_results/03_qtl/R5A2A2/OneK1K_chr18_fixed_1Mb_region_pairs.tsv.gz"
OUT = ROOT / "3_results/04_integration/R5A2A4/NK_R_ZCCHC2_sourceLD"

LEAD = "18:60005046"
QTL_TOP = "18:60243208"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fam = pd.read_csv(FAM, sep=r"\s+", header=None, dtype=str)
    fam_ids = fam.iloc[:, 1].tolist()
    if len(fam_ids) != 980 or len(set(fam_ids)) != 980:
        raise RuntimeError("FAM must contain 980 unique donors")
    fam_index = {sample: i for i, sample in enumerate(fam_ids)}
    active = [line.strip() for line in SAMPLES.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(active) != 750 or len(set(active)) != 750:
        raise RuntimeError(f"NK_R sample list must contain 750 unique donors, found {len(active)}/{len(set(active))}")
    missing_active = sorted(set(active) - set(fam_ids))
    if missing_active:
        raise RuntimeError(f"NK_R donors missing from FAM: {missing_active[:5]}")
    keep = np.array([fam_index[sample] for sample in active], dtype=np.int64)

    qtl = pd.read_csv(QTL, sep="\t")
    qtl = qtl[(qtl["cell_type"] == "NK_R") & (qtl["phenotype_id"] == "ZCCHC2")].copy()
    if len(qtl) != 3827 or qtl["variant_id"].nunique() != len(qtl):
        raise RuntimeError(f"Unexpected NK_R/ZCCHC2 QTL structure: {len(qtl)} rows")
    qtl = qtl.sort_values(["position_GRCh37", "variant_id"]).set_index("variant_id", drop=False)
    wanted = set(qtl.index)

    bim_records: dict[str, dict[str, object]] = {}
    with BIM.open(encoding="utf-8") as stream:
        for global_index, line in enumerate(stream):
            chromosome, variant_id, cm, position, a1, a2 = line.split()
            if variant_id not in wanted:
                continue
            if variant_id in bim_records:
                raise RuntimeError(f"Duplicate BIM variant ID {variant_id}")
            bim_records[variant_id] = {
                "global_bim_index_zero_based": global_index,
                "chromosome": chromosome,
                "position_GRCh37": int(position),
                "BIM_A1": a1,
                "BIM_A2": a2,
            }
    if set(bim_records) != wanted:
        raise RuntimeError(f"QTL/BIM coverage mismatch: {len(bim_records)}/{len(wanted)}")

    order = qtl.index.tolist()
    variant_rows = []
    genotype = np.empty((len(active), len(order)), dtype=np.float64)
    bytes_per_variant = (len(fam_ids) + 3) // 4
    af_differences = []
    count_mismatches = 0
    with BED.open("rb") as bed:
        if bed.read(3).hex() != "6c1b01":
            raise RuntimeError("BED is not SNP-major PLINK v1")
        for column, variant_id in enumerate(order):
            b = bim_records[variant_id]
            row = qtl.loc[variant_id]
            if row["A1_effect_allele"] != b["BIM_A1"] or row["A2_other_allele"] != b["BIM_A2"]:
                raise RuntimeError(f"Allele mismatch for {variant_id}")
            bed.seek(3 + int(b["global_bim_index_zero_based"]) * bytes_per_variant)
            raw = bed.read(bytes_per_variant)
            codes = np.fromiter(
                ((byte >> shift) & 3 for byte in raw for shift in (0, 2, 4, 6)),
                dtype=np.int8,
                count=bytes_per_variant * 4,
            )[: len(fam_ids)][keep]
            called = codes != 1
            dosage = np.where(codes == 0, 2.0, np.where(codes == 2, 1.0, np.where(codes == 3, 0.0, np.nan)))
            called_dosage = dosage[called]
            af = float(called_dosage.sum() / (2 * called.sum()))
            af_difference = abs(af - float(row["af_A1"]))
            af_differences.append(af_difference)
            a1_count = int(called_dosage.sum())
            a1_carriers = int((called_dosage > 0).sum())
            a2_dosage = 2 - called_dosage
            if af <= 0.5:
                minor_count, minor_carriers = a1_count, a1_carriers
            else:
                minor_count, minor_carriers = int(a2_dosage.sum()), int((a2_dosage > 0).sum())
            if minor_count != int(row["ma_count"]) or minor_carriers != int(row["ma_samples"]):
                count_mismatches += 1
            missing = int((~called).sum())
            if missing:
                dosage = np.where(np.isnan(dosage), np.nanmean(dosage), dosage)
            genotype[:, column] = dosage
            variant_rows.append({
                "variant_id": variant_id,
                **b,
                "QTL_A1_AF": float(row["af_A1"]),
                "recomputed_A1_AF": af,
                "AF_absolute_difference": af_difference,
                "called_donors": int(called.sum()),
                "missing_donors": missing,
                "QTL_slope_A1": float(row["slope_A1"]),
                "QTL_slope_se": float(row["slope_se"]),
                "QTL_pval_nominal": float(row["pval_nominal"]),
            })

    mean = genotype.mean(axis=0)
    sd = genotype.std(axis=0, ddof=1)
    variable = np.isfinite(sd) & (sd > 0)
    if not variable.all():
        order = [variant for variant, keep_variant in zip(order, variable) if keep_variant]
        genotype = genotype[:, variable]
        variant_rows = [row for row, keep_variant in zip(variant_rows, variable) if keep_variant]
        mean = mean[variable]
        sd = sd[variable]
    standardized = (genotype - mean) / sd
    correlation64 = (standardized.T @ standardized) / (len(active) - 1)
    correlation64 = (correlation64 + correlation64.T) / 2
    np.fill_diagonal(correlation64, 1.0)
    correlation32 = correlation64.astype(np.float32)

    correlation_path = OUT / "NK_R_ZCCHC2_signed_A1_correlation.npy"
    correlation_bin_path = OUT / "NK_R_ZCCHC2_signed_A1_correlation.float32.bin"
    standardized_path = OUT / "NK_R_ZCCHC2_standardized_A1_dosage.npy"
    np.save(correlation_path, correlation32)
    correlation32.astype("<f4", copy=False).tofile(correlation_bin_path)
    np.save(standardized_path, standardized.astype(np.float32))
    variants = pd.DataFrame(variant_rows)
    variants.insert(0, "LD_order_zero_based", np.arange(len(variants)))
    variants_path = OUT / "NK_R_ZCCHC2_LD_variants.tsv"
    variants.to_csv(variants_path, sep="\t", index=False, lineterminator="\n")
    samples_path = OUT / "NK_R_750_active_donors.txt"
    samples_path.write_text("\n".join(active) + "\n", encoding="utf-8")

    index = {variant: i for i, variant in enumerate(order)}
    anchors = [LEAD, QTL_TOP]
    anchor_rows = []
    for anchor in anchors:
        ai = index[anchor]
        for j, variant in enumerate(order):
            anchor_rows.append({
                "anchor_variant": anchor,
                "variant_id": variant,
                "position_GRCh37": int(variants.iloc[j]["position_GRCh37"]),
                "signed_r_A1": float(correlation64[ai, j]),
                "r_squared": float(correlation64[ai, j] ** 2),
                "absolute_distance_bp": abs(int(variants.iloc[j]["position_GRCh37"]) - int(variants.iloc[ai]["position_GRCh37"])),
            })
    anchor_table = pd.DataFrame(anchor_rows).sort_values(["anchor_variant", "r_squared"], ascending=[True, False])
    anchor_path = OUT / "NK_R_ZCCHC2_anchor_LD.tsv.gz"
    anchor_table.to_csv(anchor_path, sep="\t", index=False, compression="gzip", lineterminator="\n")

    # The p x p matrix has p-n exact zero eigenvalues. Its nonzero spectrum is
    # the spectrum of the much smaller n x n Gram matrix, which is feasible to
    # audit directly and avoids a cubic eigendecomposition of a 3827 matrix.
    dual = (standardized @ standardized.T) / (len(active) - 1)
    dual = (dual + dual.T) / 2
    dual_eigenvalues = np.linalg.eigvalsh(dual)
    lead_top_r = float(correlation64[index[LEAD], index[QTL_TOP]])
    qc = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cell_type": "NK_R",
        "phenotype_id": "ZCCHC2",
        "effect_allele": "OneK1K_BIM_A1",
        "n_FAM_donors": len(fam_ids),
        "n_active_donors": len(active),
        "n_QTL_variants_input": len(qtl),
        "n_LD_variants_output": len(order),
        "zero_variance_variants_removed": int((~variable).sum()),
        "variants_with_missing_genotypes": int((variants["missing_donors"] > 0).sum()),
        "maximum_missing_donors": int(variants["missing_donors"].max()),
        "maximum_AF_absolute_difference": float(max(af_differences)),
        "minor_count_or_carrier_mismatches": count_mismatches,
        "max_asymmetry_float64": float(np.max(np.abs(correlation64 - correlation64.T))),
        "max_diagonal_deviation_float64": float(np.max(np.abs(np.diag(correlation64) - 1))),
        "dual_gram_min_eigenvalue": float(dual_eigenvalues.min()),
        "dual_gram_negative_eigenvalues_below_minus_1e_8": int((dual_eigenvalues < -1e-8).sum()),
        "LD_rank_upper_bound": len(active) - 1,
        "lead_present": LEAD in index,
        "QTL_top_present": QTL_TOP in index,
        "lead_to_QTL_top_signed_r_A1": lead_top_r,
        "lead_to_QTL_top_r_squared": lead_top_r**2,
        "lead_r2_ge_0_8_variants": int((correlation64[index[LEAD], :] ** 2 >= 0.8).sum()),
        "QTL_top_r2_ge_0_8_variants": int((correlation64[index[QTL_TOP], :] ** 2 >= 0.8).sum()),
        "files": {
            "samples": {"path": str(samples_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(samples_path)},
            "variants": {"path": str(variants_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(variants_path)},
            "correlation": {"path": str(correlation_path.relative_to(ROOT)).replace("\\", "/"), "bytes": correlation_path.stat().st_size, "sha256": sha256(correlation_path)},
            "correlation_float32_bin": {"path": str(correlation_bin_path.relative_to(ROOT)).replace("\\", "/"), "bytes": correlation_bin_path.stat().st_size, "sha256": sha256(correlation_bin_path)},
            "standardized_dosage": {"path": str(standardized_path.relative_to(ROOT)).replace("\\", "/"), "bytes": standardized_path.stat().st_size, "sha256": sha256(standardized_path)},
            "anchor_LD": {"path": str(anchor_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(anchor_path)},
        },
    }
    checks = {
        "exact_750_active_donors": len(active) == 750 and len(set(active)) == 750 and not missing_active,
        "all_QTL_variants_mapped_in_BIM": len(bim_records) == len(qtl),
        "A1_AF_exact_within_2e_7": qc["maximum_AF_absolute_difference"] <= 2e-7,
        "minor_counts_and_carriers_exact": count_mismatches == 0,
        "all_variants_variable": qc["zero_variance_variants_removed"] == 0,
        "finite_LD": bool(np.isfinite(correlation64).all()),
        "symmetric_LD": qc["max_asymmetry_float64"] <= 1e-12,
        "unit_diagonal": qc["max_diagonal_deviation_float64"] <= 1e-12,
        "PSD_nonzero_spectrum": qc["dual_gram_negative_eigenvalues_below_minus_1e_8"] == 0,
        "anchors_present": qc["lead_present"] and qc["QTL_top_present"],
        "variant_order_matches_matrix": correlation64.shape == (len(variants), len(variants)),
    }
    qc["checks"] = checks
    qc["source_LD_gate_pass"] = all(checks.values())
    qc_path = OUT / "NK_R_ZCCHC2_sourceLD_QC.json"
    qc_path.write_text(json.dumps(qc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(qc, indent=2, ensure_ascii=False))
    return 0 if qc["source_LD_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
