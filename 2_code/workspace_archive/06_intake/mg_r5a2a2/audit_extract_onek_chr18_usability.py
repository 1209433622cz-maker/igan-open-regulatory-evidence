#!/usr/bin/env python3
"""Validate OneK1K chr18 eQTL schema, samples, alleles, and extract the fixed region."""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(r"H:\SCI2\YR1")
QTL_DIR = ROOT / "1_data/qtl/OneK1K/R5A2A2_chr18_members"
PLINK_DIR = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors"
PSEUDOBULK_ZIP = ROOT / "1_data/qtl/OneK1K/OneK1K_pseudobulk_mean_mx.zip"
COVARIATE_DIR = ROOT / "1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors"
RESULT_DIR = ROOT / "3_results/03_qtl/R5A2A2"
AUDIT_DIR = ROOT / "3_results/00_audit/R5A2A2"
LEAD_POSITION_GRCH37 = 60_005_046
WINDOW = 1_000_000
REGION_START = LEAD_POSITION_GRCH37 - WINDOW
REGION_END = LEAD_POSITION_GRCH37 + WINDOW
EXPECTED_PSEUDOBULK_BYTES = 376_109_718
EXPECTED_PSEUDOBULK_MD5 = "415d7f28e305598f52caef9a520732b2"
EXPECTED_SCHEMA = {
    "phenotype_id": "string",
    "variant_id": "string",
    "tss_distance": "int32",
    "af": "float",
    "ma_samples": "int32",
    "ma_count": "int32",
    "pval_nominal": "double",
    "slope": "float",
    "slope_se": "float",
}
CELL_PATTERN = re.compile(r"OneK1K_(.+?)\.cis_qtl_pairs\.chr18\.parquet$")


def file_hash(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def load_pseudobulk_samples(archive: zipfile.ZipFile, cell: str) -> tuple[list[str], int, bool]:
    name = f"{cell}_cells_mean_mx.txt"
    with archive.open(name) as raw, io.TextIOWrapper(raw, encoding="utf-8") as stream:
        header = stream.readline().split()
        first_rows = [stream.readline().split() for _ in range(5)]
    if any(len(row) != len(header) for row in first_rows):
        raise RuntimeError(f"Pseudobulk row width mismatch for {cell}")
    masks = [[value != "NA" for value in row] for row in first_rows]
    mask_stable = all(mask == masks[0] for mask in masks[1:])
    samples = [sample for sample, keep in zip(header, masks[0]) if keep]
    return samples, len(header), mask_stable


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    sample_dir = RESULT_DIR / "cell_sample_lists"
    sample_dir.mkdir(parents=True, exist_ok=True)

    fam_path = PLINK_DIR / "plink_merged_980_donors.fam"
    bim_path = PLINK_DIR / "plink_merged_980_donors.bim"
    bed_path = PLINK_DIR / "plink_merged_980_donors.bed"
    fam_ids = [line.split()[1] for line in fam_path.open(encoding="utf-8") if line.strip()]
    if len(fam_ids) != 980 or len(set(fam_ids)) != 980:
        raise RuntimeError("Unexpected FAM sample structure")
    fam_index = {sample: index for index, sample in enumerate(fam_ids)}

    chr18_bim: dict[str, tuple[int, int, str, str]] = {}
    region_bim_rows: list[dict[str, object]] = []
    with bim_path.open(encoding="utf-8") as stream:
        for global_index, line in enumerate(stream):
            chromosome, variant_id, cm, position_text, a1, a2 = line.split()
            if chromosome != "18":
                continue
            position = int(position_text)
            if variant_id in chr18_bim:
                raise RuntimeError(f"Duplicate chr18 BIM variant ID: {variant_id}")
            chr18_bim[variant_id] = (global_index, position, a1, a2)
            if REGION_START <= position <= REGION_END:
                region_bim_rows.append({
                    "global_bim_index_zero_based": global_index,
                    "variant_id": variant_id,
                    "chromosome": 18,
                    "position_GRCh37": position,
                    "A1_effect_allele": a1,
                    "A2_other_allele": a2,
                })
    if len(chr18_bim) != 152_852:
        raise RuntimeError(f"Unexpected chr18 BIM count: {len(chr18_bim)}")

    bytes_per_variant = (len(fam_ids) + 3) // 4
    with bed_path.open("rb") as bed:
        if bed.read(3).hex() != "6c1b01":
            raise RuntimeError("BED is not SNP-major PLINK v1 format")

    def decode_alleles(variant_id: str, sample_indices: np.ndarray, bed) -> tuple[int, int, int, int, int]:
        global_index, _, _, _ = chr18_bim[variant_id]
        bed.seek(3 + global_index * bytes_per_variant)
        raw = bed.read(bytes_per_variant)
        codes = np.fromiter(
            ((byte >> shift) & 3 for byte in raw for shift in (0, 2, 4, 6)),
            dtype=np.int8,
            count=bytes_per_variant * 4,
        )[: len(fam_ids)][sample_indices]
        called = codes != 1
        a1_dosage = np.where(codes == 0, 2, np.where(codes == 2, 1, np.where(codes == 3, 0, -9)))
        called_dosage = a1_dosage[called]
        a1_count = int(called_dosage.sum())
        a2_dosage = 2 - called_dosage
        return (
            a1_count,
            int((called_dosage > 0).sum()),
            int(a2_dosage.sum()),
            int((a2_dosage > 0).sum()),
            int(called.sum()),
        )

    qtl_files = sorted(QTL_DIR.glob("OneK1K_*.cis_qtl_pairs.chr18.parquet"))
    cells = [CELL_PATTERN.fullmatch(path.name).group(1) for path in qtl_files if CELL_PATTERN.fullmatch(path.name)]
    if len(cells) != 14 or len(set(cells)) != 14:
        raise RuntimeError(f"Expected 14 chr18 cell files, found {cells}")

    pseudobulk_md5 = file_hash(PSEUDOBULK_ZIP, "md5")
    sample_rows: list[dict[str, object]] = []
    schema_rows: list[dict[str, object]] = []
    gene_rows: list[dict[str, object]] = []
    lead_rows: list[dict[str, object]] = []
    validation_counts = {"allele_count_rows_checked": 0, "minor_allele_count_exact": 0, "af_A1_exact_tolerance": 0}
    region_output = RESULT_DIR / "OneK1K_chr18_fixed_1Mb_region_pairs.tsv.gz"
    region_header_written = False
    total_qtl_rows = 0
    total_region_rows = 0
    all_schemas_pass = True
    all_variants_in_bim = True
    all_stats_valid = True
    all_tss_consistent = True
    all_sample_interfaces_pass = True

    with zipfile.ZipFile(PSEUDOBULK_ZIP) as pseudobulk, bed_path.open("rb") as bed:
        for path, cell in zip(qtl_files, cells):
            samples, matrix_columns, mask_stable = load_pseudobulk_samples(pseudobulk, cell)
            missing_fam = sorted(set(samples) - set(fam_ids))
            covariate_path = COVARIATE_DIR / f"{cell}_mx_pf50.txt"
            covariates = pd.read_csv(covariate_path, sep=r"\s+", usecols=["sampleid"])["sampleid"].astype(str).tolist()
            missing_covariates = sorted(set(samples) - set(covariates))
            sample_interface_pass = mask_stable and not missing_fam and not missing_covariates and len(samples) == len(set(samples))
            all_sample_interfaces_pass &= sample_interface_pass
            (sample_dir / f"{cell}.samples.txt").write_text("\n".join(samples) + "\n", encoding="utf-8")

            parquet_file = pq.ParquetFile(path)
            schema = {field.name: str(field.type) for field in parquet_file.schema_arrow}
            schema_pass = schema == EXPECTED_SCHEMA and parquet_file.metadata.num_row_groups == 1
            all_schemas_pass &= schema_pass
            frame = pd.read_parquet(path)
            total_qtl_rows += len(frame)
            variant_match = frame["variant_id"].str.fullmatch(r"18:\d+").fillna(False)
            positions = pd.to_numeric(frame["variant_id"].str.slice(3), errors="coerce").astype("Int64")
            in_bim = frame["variant_id"].isin(chr18_bim)
            all_variants_in_bim &= bool(variant_match.all() and in_bim.all())
            stat_valid = (
                frame["af"].between(0, 1, inclusive="both").all()
                and frame["ma_samples"].between(0, len(samples), inclusive="both").all()
                and frame["ma_count"].between(0, 2 * len(samples), inclusive="both").all()
                and frame["pval_nominal"].between(0, 1, inclusive="both").all()
                and np.isfinite(frame[["af", "pval_nominal", "slope", "slope_se"]].to_numpy()).all()
                and (frame["slope_se"] > 0).all()
            )
            all_stats_valid &= bool(stat_valid)
            tss = positions.astype("int64") - frame["tss_distance"].astype("int64")
            tss_table = pd.DataFrame({"phenotype_id": frame["phenotype_id"], "tss": tss}).groupby("phenotype_id")["tss"].agg(["min", "max", "size"])
            tss_consistent = bool((tss_table["min"] == tss_table["max"]).all())
            all_tss_consistent &= tss_consistent
            selected_genes = tss_table[(tss_table["min"] >= REGION_START) & (tss_table["min"] <= REGION_END)].index.tolist()
            region_mask = frame["phenotype_id"].isin(selected_genes) & positions.between(REGION_START, REGION_END)
            region = frame.loc[region_mask].copy()
            region_positions = positions.loc[region_mask].astype("int64")
            region["cell_type"] = cell
            region["n_expression_donors"] = len(samples)
            region["chromosome"] = 18
            region["position_GRCh37"] = region_positions.to_numpy()
            region["phenotype_tss_GRCh37"] = region["phenotype_id"].map(tss_table["min"])
            region["A1_effect_allele"] = region["variant_id"].map(lambda value: chr18_bim[value][2])
            region["A2_other_allele"] = region["variant_id"].map(lambda value: chr18_bim[value][3])
            region = region[[
                "cell_type", "n_expression_donors", "phenotype_id", "phenotype_tss_GRCh37",
                "variant_id", "chromosome", "position_GRCh37", "A1_effect_allele", "A2_other_allele",
                "tss_distance", "af", "ma_samples", "ma_count", "pval_nominal", "slope", "slope_se",
            ]]
            region.rename(columns={"af": "af_A1", "slope": "slope_A1"}, inplace=True)
            region.to_csv(region_output, sep="\t", index=False, mode="at" if region_header_written else "wt",
                          header=not region_header_written, compression="gzip", encoding="utf-8", lineterminator="\n")
            region_header_written = True
            total_region_rows += len(region)

            sample_indices = np.array([fam_index[sample] for sample in samples], dtype=np.int64)
            audit_indices = np.unique(np.linspace(0, len(frame) - 1, num=min(256, len(frame)), dtype=int))
            lead_indices = np.flatnonzero(frame["variant_id"].to_numpy() == f"18:{LEAD_POSITION_GRCH37}")
            audit_indices = np.unique(np.concatenate([audit_indices, lead_indices]))
            for index in audit_indices:
                row = frame.iloc[int(index)]
                a1_count, a1_carriers, a2_count, a2_carriers, called = decode_alleles(str(row["variant_id"]), sample_indices, bed)
                validation_counts["allele_count_rows_checked"] += 1
                if float(row["af"]) <= 0.5:
                    minor_count, minor_carriers = a1_count, a1_carriers
                else:
                    minor_count, minor_carriers = a2_count, a2_carriers
                if minor_count == int(row["ma_count"]) and minor_carriers == int(row["ma_samples"]):
                    validation_counts["minor_allele_count_exact"] += 1
                if called and math.isclose(a1_count / (2 * called), float(row["af"]), abs_tol=2e-7):
                    validation_counts["af_A1_exact_tolerance"] += 1

            sample_rows.append({
                "cell_type": cell,
                "pseudobulk_matrix_columns": matrix_columns,
                "expression_analysis_donors": len(samples),
                "covariate_rows": len(covariates),
                "active_donors_missing_from_FAM": len(missing_fam),
                "active_donors_missing_from_covariates": len(missing_covariates),
                "first_five_expression_NA_masks_identical": mask_stable,
                "sample_interface_pass": sample_interface_pass,
            })
            schema_rows.append({
                "cell_type": cell,
                "parquet_rows": len(frame),
                "parquet_row_groups": parquet_file.metadata.num_row_groups,
                "phenotypes": frame["phenotype_id"].nunique(),
                "unique_variants": frame["variant_id"].nunique(),
                "selected_regional_genes": len(selected_genes),
                "fixed_window_pairs": len(region),
                "schema_pass": schema_pass,
                "variant_bim_pass": bool(variant_match.all() and in_bim.all()),
                "statistics_pass": bool(stat_valid),
                "tss_consistency_pass": tss_consistent,
            })
            for gene in selected_genes:
                gene_all = frame[frame["phenotype_id"] == gene]
                gene_region = region[region["phenotype_id"] == gene]
                top = gene_region.loc[gene_region["pval_nominal"].idxmin()] if len(gene_region) else None
                lead = gene_region[gene_region["variant_id"] == f"18:{LEAD_POSITION_GRCH37}"]
                gene_rows.append({
                    "cell_type": cell,
                    "n_expression_donors": len(samples),
                    "phenotype_id": gene,
                    "phenotype_tss_GRCh37": int(tss_table.loc[gene, "min"]),
                    "all_cis_pairs": len(gene_all),
                    "fixed_window_pairs": len(gene_region),
                    "fixed_window_unique_variants": gene_region["variant_id"].nunique(),
                    "top_variant": "" if top is None else top["variant_id"],
                    "top_pval_nominal": "" if top is None else top["pval_nominal"],
                    "top_slope_A1": "" if top is None else top["slope_A1"],
                    "lead_present": len(lead) == 1,
                    "lead_pval_nominal": "" if len(lead) != 1 else lead.iloc[0]["pval_nominal"],
                    "lead_slope_A1": "" if len(lead) != 1 else lead.iloc[0]["slope_A1"],
                    "lead_slope_se": "" if len(lead) != 1 else lead.iloc[0]["slope_se"],
                })
                if len(lead) == 1:
                    lead_rows.append(dict(gene_rows[-1]))

    def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    write_tsv(RESULT_DIR / "OneK1K_chr18_cell_sample_manifest.tsv", sample_rows)
    write_tsv(RESULT_DIR / "OneK1K_chr18_schema_by_cell.tsv", schema_rows)
    write_tsv(RESULT_DIR / "OneK1K_chr18_cell_gene_summary.tsv", gene_rows)
    write_tsv(RESULT_DIR / "OneK1K_chr18_lead_associations.tsv", lead_rows)
    write_tsv(RESULT_DIR / "OneK1K_chr18_LD_variant_universe.tsv", region_bim_rows)

    allele_interface_pass = (
        validation_counts["allele_count_rows_checked"] > 0
        and validation_counts["allele_count_rows_checked"] == validation_counts["minor_allele_count_exact"]
        and validation_counts["allele_count_rows_checked"] == validation_counts["af_A1_exact_tolerance"]
    )
    checks = {
        "pseudobulk_byte_size_pass": PSEUDOBULK_ZIP.stat().st_size == EXPECTED_PSEUDOBULK_BYTES,
        "pseudobulk_md5_pass": pseudobulk_md5 == EXPECTED_PSEUDOBULK_MD5,
        "pseudobulk_zip_crc_pass": zipfile.ZipFile(PSEUDOBULK_ZIP).testzip() is None,
        "fourteen_cell_files_pass": len(qtl_files) == 14,
        "schema_pass": all_schemas_pass,
        "sample_interface_pass": all_sample_interfaces_pass,
        "variant_id_and_bim_pass": all_variants_in_bim,
        "summary_statistics_range_pass": all_stats_valid,
        "phenotype_tss_consistency_pass": all_tss_consistent,
        "A1_count_AF_concordance_pass": allele_interface_pass,
        "fixed_region_nonempty": total_region_rows > 0,
    }
    audit = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixed_region": {"build": "GRCh37", "chromosome": 18, "lead": LEAD_POSITION_GRCH37, "start": REGION_START, "end": REGION_END},
        "parquet_schema": EXPECTED_SCHEMA,
        "total_chr18_qtl_pairs": total_qtl_rows,
        "fixed_region_pairs": total_region_rows,
        "fixed_region_genes": sorted(set(row["phenotype_id"] for row in gene_rows)),
        "TNFRSF11A_present_in_any_cell": any(row["phenotype_id"] == "TNFRSF11A" for row in gene_rows),
        "cell_sample_sizes": {row["cell_type"]: row["expression_analysis_donors"] for row in sample_rows},
        "allele_validation": validation_counts,
        "effect_allele_definition": "slope and af correspond to PLINK BIM A1; established by TensorQTL source code plus exact BED ma_count/ma_samples/af concordance",
        "checks": checks,
        "schema_and_usability_gate_pass": all(checks.values()),
    }
    (AUDIT_DIR / "OneK1K_chr18_schema_usability_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "schema_and_usability_gate_pass": audit["schema_and_usability_gate_pass"],
        "total_chr18_qtl_pairs": total_qtl_rows,
        "fixed_region_pairs": total_region_rows,
        "fixed_region_genes": audit["fixed_region_genes"],
        "TNFRSF11A_present_in_any_cell": audit["TNFRSF11A_present_in_any_cell"],
        "allele_validation": validation_counts,
    }, ensure_ascii=False))
    return 0 if audit["schema_and_usability_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
