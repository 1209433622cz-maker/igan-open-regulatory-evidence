from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
GSE127 = ROOT / "1_data/scrna/IgAN/GSE127136"
OUT = ROOT / "3_results/04_integration/R6A1"
AUDIT = ROOT / "3_results/00_audit/R6A1"
OUT.mkdir(parents=True, exist_ok=True)
AUDIT.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_soft_gz(path: Path) -> pd.DataFrame:
    rows, current = [], None
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.rstrip("\n\r")
            if line.startswith("^SAMPLE = "):
                if current:
                    rows.append(current)
                current = {"accession": line.split(" = ", 1)[1]}
            elif current is not None and line.startswith("!Sample_title = "):
                current["title"] = line.split(" = ", 1)[1]
            elif current is not None and line.startswith("!Sample_characteristics_ch1 = "):
                value = line.split(" = ", 1)[1]
                if ": " in value:
                    key, val = value.split(": ", 1)
                    current[key.strip().lower().replace(" ", "_")] = val.strip()
        if current:
            rows.append(current)
    return pd.DataFrame(rows)


def parse_text_samples(path: Path) -> pd.DataFrame:
    rows, current = [], None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("^SAMPLE = "):
            if current:
                rows.append(current)
            current = {"accession": line.split(" = ", 1)[1]}
        elif current is not None and line.startswith("!Sample_title = "):
            current["title"] = line.split(" = ", 1)[1]
        elif current is not None and line.startswith("!Sample_characteristics_ch1 = "):
            value = line.split(" = ", 1)[1]
            if ": " in value:
                key, val = value.split(": ", 1)
                current[key.strip().lower().replace(" ", "_")] = val.strip()
    if current:
        rows.append(current)
    return pd.DataFrame(rows)


cross = pd.read_csv(OUT / "IgAN_OneK1K_TenK10K_cross_resource_candidates.tsv", sep="\t")
targets = sorted(set(cross.gene_symbol.dropna().astype(str)))
controls = pd.read_csv(OUT / "IgAN_published_positive_control_screening_recovery.tsv", sep="\t")
target_set = set(targets) | set(controls.gene_symbol.dropna().astype(str))

metadata = parse_soft_gz(GSE127 / "GSE127136_family.soft.gz")
metadata["compartment"] = np.where(metadata.patients.astype(str).str.startswith("PBM_"), "peripheral_CD14_monocytes", "kidney")
metadata.to_csv(OUT / "GSE127136_cell_metadata.tsv.gz", sep="\t", index=False, compression="gzip")

counts_path = GSE127 / "GSE127136_project_IgA_nephropathy_counts.csv.gz"
detection = []
all_gene_rows = 0
duplicate_target_rows = Counter()
with gzip.open(counts_path, "rt", encoding="utf-8") as handle:
    header = handle.readline().rstrip("\n\r").split(",")
    cell_titles = header[1:]
    for line in handle:
        all_gene_rows += 1
        gene, values = line.rstrip("\n\r").split(",", 1)
        if gene not in target_set:
            continue
        x = np.fromstring(values, dtype=np.int64, sep=",")
        if len(x) != len(cell_titles):
            raise RuntimeError(f"count width mismatch for {gene}: {len(x)} != {len(cell_titles)}")
        duplicate_target_rows[gene] += 1
        detection.append({
            "gene_symbol": gene,
            "total_counts": int(x.sum()),
            "cells_nonzero": int((x > 0).sum()),
            "fraction_cells_nonzero": float((x > 0).mean()),
            "detected": bool((x > 0).any()),
        })
detection = pd.DataFrame(detection)
if not detection.empty:
    detection = detection.groupby("gene_symbol", as_index=False).agg(total_counts=("total_counts", "sum"), cells_nonzero=("cells_nonzero", "sum"), fraction_cells_nonzero=("fraction_cells_nonzero", "max"), detected=("detected", "max"))
detected_genes = set(detection.loc[detection.detected, "gene_symbol"])

cross["GSE127136_detected"] = cross.gene_symbol.isin(detected_genes)
locus_detectability = cross.groupby("locus", as_index=False).agg(
    cross_resource_genes=("gene_symbol", "nunique"),
    detectable_cross_resource_genes=("GSE127136_detected", "sum"),
)
# Sum above is pair-level; replace with unique-gene count for the second column.
locus_detectability["detectable_cross_resource_genes"] = [cross[(cross.locus == locus) & cross.GSE127136_detected].gene_symbol.nunique() for locus in locus_detectability.locus]
locus_detectability["kidney_detectable_candidate"] = locus_detectability.detectable_cross_resource_genes > 0

gse286184 = parse_text_samples(ROOT / "1_data/scrna/IgAN/GSE286184/GSE286184_samples.txt")
gse286186 = parse_text_samples(ROOT / "1_data/scrna/IgAN/GSE286186/GSE286186_samples.txt")

meta_titles = set(metadata.title.dropna().astype(str))
matrix_titles = set(cell_titles)
condition_col_184 = "condition" if "condition" in gse286184.columns else None
diagnosis_col_186 = "diagnosis" if "diagnosis" in gse286186.columns else None

summary = {
    "schema_version": "1.0",
    "GSE127136": {
        "counts_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE127136&format=file&file=GSE127136_project_IgA_nephropathy_counts.csv.gz",
        "counts_bytes": counts_path.stat().st_size,
        "counts_sha256": sha256_file(counts_path),
        "soft_bytes": (GSE127 / "GSE127136_family.soft.gz").stat().st_size,
        "soft_sha256": sha256_file(GSE127 / "GSE127136_family.soft.gz"),
        "matrix_cells": len(cell_titles),
        "metadata_cell_records": len(metadata),
        "matrix_titles_matching_metadata": len(matrix_titles & meta_titles),
        "matrix_metadata_exact_set_match": matrix_titles == meta_titles,
        "gene_rows": all_gene_rows,
        "unique_patients": int(metadata.patients.nunique()) if "patients" in metadata else None,
        "kidney_donor_counts": metadata[metadata.compartment == "kidney"].groupby("disease_state").patients.nunique().to_dict(),
        "peripheral_monocyte_donor_counts": metadata[metadata.compartment == "peripheral_CD14_monocytes"].groupby("disease_state").patients.nunique().to_dict(),
        "disease_state_counts_cells": metadata.disease_state.value_counts().to_dict() if "disease_state" in metadata else {},
        "disease_state_counts_patients": metadata.groupby("disease_state").patients.nunique().to_dict() if {"disease_state", "patients"}.issubset(metadata.columns) else {},
        "source_cell_type_counts": metadata.cell_type.value_counts().to_dict() if "cell_type" in metadata else {},
        "cross_resource_target_genes": len(targets),
        "target_genes_detected": len(set(targets) & detected_genes),
        "target_gene_detection_fraction": len(set(targets) & detected_genes) / len(targets) if targets else None,
        "loci_with_detectable_cross_resource_candidate": int(locus_detectability.kidney_detectable_candidate.sum()),
        "duplicate_target_gene_rows": {k: v for k, v in duplicate_target_rows.items() if v > 1},
    },
    "GSE286184_Xenium": {
        "sample_records": len(gse286184),
        "condition_counts": gse286184[condition_col_184].value_counts().to_dict() if condition_col_184 else {},
        "IgAN_samples": int((gse286184[condition_col_184] == "IgAN").sum()) if condition_col_184 else None,
        "filelist_bytes": (ROOT / "1_data/scrna/IgAN/GSE286184/filelist.txt").stat().st_size,
        "raw_tar_declared_bytes": 335_585_280,
        "use_boundary": "spatial localization; no disease-control inference from four IgAN samples alone",
    },
    "GSE286186_SuperSeries": {
        "sample_records": len(gse286186),
        "diagnosis_counts_when_present": gse286186[diagnosis_col_186].value_counts().to_dict() if diagnosis_col_186 else {},
        "filelist_bytes": (ROOT / "1_data/scrna/IgAN/GSE286186/filelist.txt").stat().st_size,
        "raw_tar_declared_bytes": 3_452_221_440,
        "download_status": "METADATA_AND_FILELIST_PASS_RAW_HOLD_FOR_R6A2",
    },
}
g = summary["GSE127136"]
summary["kidney_detectability_gate"] = "PASS" if g["matrix_metadata_exact_set_match"] and g["target_gene_detection_fraction"] >= 0.80 and g["loci_with_detectable_cross_resource_candidate"] >= 3 else "FAIL"

detection.sort_values(["detected", "total_counts", "gene_symbol"], ascending=[False, False, True]).to_csv(OUT / "GSE127136_cross_resource_gene_detectability.tsv", sep="\t", index=False)
locus_detectability.to_csv(OUT / "GSE127136_locus_candidate_detectability.tsv", sep="\t", index=False)
gse286184.to_csv(OUT / "GSE286184_Xenium_sample_manifest.tsv", sep="\t", index=False)
gse286186.to_csv(OUT / "GSE286186_sample_manifest.tsv", sep="\t", index=False)
(AUDIT / "IgAN_kidney_tissue_byte_metadata_detectability_audit.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
