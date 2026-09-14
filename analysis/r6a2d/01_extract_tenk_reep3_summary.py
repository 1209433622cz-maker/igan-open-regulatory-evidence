#!/usr/bin/env python3
"""Extract the frozen REEP3 rows from public TenK10K gene-level and SuSiE ZIPs."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

import pandas as pd

ROOT = Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
RAW = ROOT / "1_data/qtl/eqtl/tenk10k/raw"
OUT = ROOT / "3_results/04_integration/R6A2D"
OUT.mkdir(parents=True, exist_ok=True)
CELLS = ["CD4_Naive", "CD4_TCM", "Treg"]
GENE = "REEP3"
GENE_ID = "ENSG00000165476"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def gene_mask(frame: pd.DataFrame) -> pd.Series:
    masks = []
    for column in frame.columns:
        values = frame[column].astype(str)
        if values.str.contains(GENE, case=False, na=False).any() or values.str.contains(GENE_ID, case=False, na=False).any():
            masks.append(values.str.contains(GENE, case=False, na=False) | values.str.contains(GENE_ID, case=False, na=False))
    if not masks:
        return pd.Series(False, index=frame.index)
    result = masks[0]
    for mask in masks[1:]:
        result |= mask
    return result


gene_zip = RAW / "common_variant_gene_level_results_with_annotated_fails.zip"
susie_zip = RAW / "susie_summary.zip"
for path in (gene_zip, susie_zip):
    if not path.exists():
        raise FileNotFoundError(path)

gene_rows = []
susie_rows = []
schemas = {}
with zipfile.ZipFile(gene_zip) as archive:
    for cell in CELLS:
        member = f"gene_level_results_with_annotated_fails/{cell}_all_cis_cv_gene_level_results.tsv"
        with archive.open(member) as handle:
            frame = pd.read_csv(handle)
        schemas[f"gene_level:{cell}"] = frame.columns.tolist()
        target = frame.loc[gene_mask(frame)].copy()
        target.insert(0, "cell_type", cell)
        target.insert(1, "source_member", member)
        gene_rows.append(target)

with zipfile.ZipFile(susie_zip) as archive:
    for cell in CELLS:
        member = f"susie_summary/{cell}_all_credible_snps.tsv"
        with archive.open(member) as handle:
            frame = pd.read_csv(handle)
        schemas[f"susie:{cell}"] = frame.columns.tolist()
        target = frame.loc[gene_mask(frame)].copy()
        target.insert(0, "cell_type", cell)
        target.insert(1, "source_member", member)
        susie_rows.append(target)

genes = pd.concat(gene_rows, ignore_index=True, sort=False) if gene_rows else pd.DataFrame()
susie = pd.concat(susie_rows, ignore_index=True, sort=False) if susie_rows else pd.DataFrame()
genes.to_csv(OUT / "R6A2D_TenK_REEP3_gene_level.tsv", sep="\t", index=False)
susie.to_csv(OUT / "R6A2D_TenK_REEP3_source_credible_members.tsv", sep="\t", index=False)

receipt = {
    "status": "PASS",
    "gene": GENE,
    "gene_ensembl": GENE_ID,
    "frozen_cells": CELLS[:2],
    "auxiliary_cell": CELLS[2],
    "gene_level_rows": int(len(genes)),
    "source_credible_member_rows": int(len(susie)),
    "rows_by_cell_gene_level": {cell: int((genes.get("cell_type", pd.Series(dtype=str)) == cell).sum()) for cell in CELLS},
    "rows_by_cell_susie": {cell: int((susie.get("cell_type", pd.Series(dtype=str)) == cell).sum()) for cell in CELLS},
    "source_archives": {
        str(gene_zip.relative_to(ROOT)): {"bytes": gene_zip.stat().st_size, "sha256": sha256(gene_zip)},
        str(susie_zip.relative_to(ROOT)): {"bytes": susie_zip.stat().st_size, "sha256": sha256(susie_zip)},
    },
    "schemas": schemas,
}
(OUT / "R6A2D_TenK_summary_intake_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
print(json.dumps(receipt, indent=2))
