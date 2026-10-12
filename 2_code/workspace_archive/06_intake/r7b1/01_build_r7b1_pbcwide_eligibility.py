#!/usr/bin/env python3
"""Freeze the R7B1 PBC-wide gene-cell universe before posterior analysis."""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
TOP_ZIP = ROOT / "1_data/qtl/OneK1K/OneK1K_TensorQTL_top_eQTL_summary.zip"
RANGES = ROOT / "3_results/01_intake/R7A1A/R7A1A_PBC_GJOKA_locus_ranges.tsv"
SCAFFOLD = ROOT / "3_results/03_qtl/R7B0/R7B0_PBCwide_56x14_universe_scaffold.tsv"
OUT = ROOT / "3_results/03_qtl/R7B1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ranges = pd.read_csv(RANGES, sep="\t")
    scaffold = pd.read_csv(SCAFFOLD, sep="\t")
    cells = sorted(scaffold["cell_type"].astype(str).unique())
    if len(ranges) != 56 or len(cells) != 14 or len(scaffold) != 56 * 14:
        raise RuntimeError("frozen disease/cell scaffold is incomplete")
    donor_n = scaffold.drop_duplicates("cell_type").set_index("cell_type")["active_donor_N"].astype(int).to_dict()

    records: list[pd.DataFrame] = []
    member_receipts: list[dict[str, object]] = []
    pattern = re.compile(r"OneK1K_(.+)\.sig_cis_qtl_pairs\.chr(\d+)\.csv$")
    with zipfile.ZipFile(TOP_ZIP) as archive:
        for name in sorted(archive.namelist()):
            if name.startswith("__MACOSX/"):
                continue
            match = pattern.fullmatch(name.rsplit("/", 1)[-1])
            if not match:
                continue
            cell, chrom = match.group(1), int(match.group(2))
            if cell not in cells:
                continue
            raw = archive.read(name)
            frame = pd.read_csv(io.BytesIO(raw), sep="\t")
            required = {"phenotype_id", "variant_id", "tss_distance", "qval", "pval_nominal"}
            if not required.issubset(frame.columns):
                raise RuntimeError(f"top-QTL schema mismatch: {name}")
            pos = pd.to_numeric(frame["variant_id"].astype(str).str.split(":").str[1], errors="coerce")
            dist = pd.to_numeric(frame["tss_distance"], errors="coerce")
            frame = frame.assign(
                gene=frame["phenotype_id"].astype(str),
                cell_type=cell,
                chromosome=chrom,
                lead_position_GRCh37=pos,
                gene_tss_GRCh37=pos - dist,
                source_qval=pd.to_numeric(frame["qval"], errors="coerce"),
                source_top_p=pd.to_numeric(frame["pval_nominal"], errors="coerce"),
                source_top_variant=frame["variant_id"].astype(str),
            )
            frame = frame[np.isfinite(frame["gene_tss_GRCh37"]) & np.isfinite(frame["source_qval"])].copy()
            records.append(frame[["gene", "cell_type", "chromosome", "gene_tss_GRCh37", "source_qval", "source_top_p", "source_top_variant"]])
            info = archive.getinfo(name)
            member_receipts.append(
                {
                    "member": name,
                    "cell_type": cell,
                    "chromosome": chrom,
                    "rows": len(frame),
                    "uncompressed_bytes": info.file_size,
                    "crc32": f"{info.CRC:08x}",
                }
            )
    top = pd.concat(records, ignore_index=True)
    if top.duplicated(["gene", "cell_type", "chromosome"]).any():
        raise RuntimeError("duplicate gene-cell-chromosome top-QTL rows")

    tss_audit = top.groupby(["gene", "chromosome"])["gene_tss_GRCh37"].agg(["min", "max", "count"]).reset_index()
    tss_audit["range_bp"] = tss_audit["max"] - tss_audit["min"]
    if (tss_audit["range_bp"] != 0).any():
        bad = tss_audit[tss_audit["range_bp"] != 0].head(10).to_dict("records")
        raise RuntimeError(f"inconsistent inferred gene TSS: {bad}")
    gene_q = top.groupby(["gene", "chromosome"], as_index=False)["source_qval"].min().rename(columns={"source_qval": "gene_min_source_qval"})
    selected = gene_q[gene_q["gene_min_source_qval"] < 0.05].copy()
    selected = selected.merge(tss_audit[["gene", "chromosome", "min"]].rename(columns={"min": "gene_tss_GRCh37"}), on=["gene", "chromosome"])

    mapped: list[dict[str, object]] = []
    for row in selected.itertuples(index=False):
        locus_hits = ranges[
            (ranges["chromosomes"].astype(str) == str(int(row.chromosome)))
            & (row.gene_tss_GRCh37 >= ranges["min_bp_grch37"] - 1_000_000)
            & (row.gene_tss_GRCh37 <= ranges["max_bp_grch37"] + 1_000_000)
        ]
        for locus in locus_hits.itertuples(index=False):
            mapped.append(
                {
                    "locus_index": int(locus.locus_index),
                    "chromosome": int(row.chromosome),
                    "region_start_GRCh37": int(locus.min_bp_grch37),
                    "region_end_GRCh37": int(locus.max_bp_grch37),
                    "gene": row.gene,
                    "gene_tss_GRCh37": int(row.gene_tss_GRCh37),
                    "gene_min_source_qval": float(row.gene_min_source_qval),
                }
            )
    locus_gene = pd.DataFrame(mapped).drop_duplicates(["locus_index", "gene"])
    if locus_gene.empty:
        raise RuntimeError("no source-significant genes mapped to the 56-locus universe")

    universe = locus_gene.merge(top, on=["gene", "chromosome", "gene_tss_GRCh37"], how="inner", validate="one_to_many")
    universe = universe[universe["cell_type"].isin(cells)].copy()
    universe["active_donor_N"] = universe["cell_type"].map(donor_n).astype(int)
    universe["source_gene_selected"] = True
    universe["source_cell_q_lt_0_05"] = universe["source_qval"] < 0.05
    universe["variant_overlap_status"] = "PENDING_HARMONIZATION"
    universe["current_PF10_status"] = "PENDING_DE_NOVO_SUMMARY"
    universe["ABF_status"] = "PENDING"
    universe = universe.sort_values(["locus_index", "gene", "cell_type"]).reset_index(drop=True)
    universe.insert(0, "comparison_id", [f"R7B1_{i:06d}" for i in range(1, len(universe) + 1)])

    locus_gene.to_csv(OUT / "R7B1_frozen_locus_gene_universe.tsv", sep="\t", index=False)
    universe.to_csv(OUT / "R7B1_frozen_comparison_universe.tsv", sep="\t", index=False)
    pd.DataFrame(member_receipts).to_csv(OUT / "R7B1_OneK_topQTL_member_receipts.tsv", sep="\t", index=False)
    tss_audit.to_csv(OUT / "R7B1_gene_TSS_consistency_audit.tsv", sep="\t", index=False)

    state = {
        "schema": "R7B1_PBCWIDE_ELIGIBILITY_1.0",
        "status": "GENE_CELL_UNIVERSE_FROZEN_PENDING_VARIANT_OVERLAP",
        "disease_loci": int(ranges["locus_index"].nunique()),
        "cells": len(cells),
        "top_qtl_members_read": len(member_receipts),
        "source_significant_genes_genomewide": int(len(selected)),
        "mapped_locus_gene_pairs": int(len(locus_gene)),
        "frozen_comparisons": int(len(universe)),
        "loci_with_at_least_one_gene": int(universe["locus_index"].nunique()),
        "top_qtl_archive_sha256": sha256(TOP_ZIP),
        "locus_ranges_sha256": sha256(RANGES),
        "scaffold_sha256": sha256(SCAFFOLD),
        "posterior_read_before_freeze": False,
    }
    (OUT / "R7B1_eligibility_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
