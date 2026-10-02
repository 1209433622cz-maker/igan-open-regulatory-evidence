#!/usr/bin/env python3
"""Harmonize the PBC GWAS to OneK BIM A1 across the frozen 56 regions."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
GWAS = ROOT / "1_data/gwas/R7A1A/PBC/GCST90061440_buildGRCh37.tsv"
BIM = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
RANGES = ROOT / "3_results/01_intake/R7A1A/R7A1A_PBC_GJOKA_locus_ranges.tsv"
OUT = ROOT / "3_results/01_gwas/R7B1"

COMPLEMENT = str.maketrans("ACGT", "TGCA")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def reverse_complement(value: str) -> str:
    return str(value).upper().translate(COMPLEMENT)[::-1]


def palindromic(a1: str, a2: str) -> bool:
    return len(a1) == 1 and len(a2) == 1 and reverse_complement(a1) == a2


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ranges = pd.read_csv(RANGES, sep="\t").sort_values("locus_index")
    if len(ranges) != 56:
        raise RuntimeError("expected 56 GJOKA regions")
    bim = pd.read_csv(
        BIM,
        sep=r"\s+",
        header=None,
        names=["chromosome", "variant_id", "cm", "position_GRCh37", "BIM_A1", "BIM_A2"],
        dtype={"variant_id": str, "BIM_A1": str, "BIM_A2": str},
    )
    bim["chromosome"] = pd.to_numeric(bim["chromosome"], errors="coerce")
    bim["position_GRCh37"] = pd.to_numeric(bim["position_GRCh37"], errors="coerce")
    bim["gi"] = np.arange(len(bim), dtype=np.int64)

    locus_parts: dict[int, list[pd.DataFrame]] = {int(x): [] for x in ranges["locus_index"]}
    for chunk in pd.read_csv(GWAS, sep="\t", dtype=str, chunksize=600_000):
        chrom = pd.to_numeric(chunk["chromosome"], errors="coerce")
        pos = pd.to_numeric(chunk["base_pair_location"], errors="coerce")
        for locus in ranges.itertuples(index=False):
            mask = (
                (chrom == int(locus.chromosomes))
                & pos.between(int(locus.min_bp_grch37), int(locus.max_bp_grch37))
            )
            if mask.any():
                piece = chunk.loc[mask].copy()
                piece["chromosome"] = chrom.loc[mask].astype(int)
                piece["base_pair_location"] = pos.loc[mask].astype(int)
                locus_parts[int(locus.locus_index)].append(piece)

    combined: list[pd.DataFrame] = []
    manifest: list[dict[str, object]] = []
    for locus in ranges.itertuples(index=False):
        idx = int(locus.locus_index)
        source = pd.concat(locus_parts[idx], ignore_index=True) if locus_parts[idx] else pd.DataFrame()
        b = bim[
            (bim["chromosome"] == int(locus.chromosomes))
            & bim["position_GRCh37"].between(int(locus.min_bp_grch37), int(locus.max_bp_grch37))
        ].copy()
        merged = source.merge(
            b[["chromosome", "variant_id", "position_GRCh37", "BIM_A1", "BIM_A2", "gi"]],
            left_on=["chromosome", "base_pair_location"],
            right_on=["chromosome", "position_GRCh37"],
            how="inner",
        )
        output: list[dict[str, object]] = []
        for row in merged.itertuples(index=False):
            ea = str(row.effect_allele).upper()
            oa = str(row.other_allele).upper()
            a1 = str(row.BIM_A1).upper()
            a2 = str(row.BIM_A2).upper()
            if palindromic(a1, a2):
                continue
            sign = None
            match_type = ""
            if ea == a1 and oa == a2:
                sign, match_type = 1, "DIRECT"
            elif ea == a2 and oa == a1:
                sign, match_type = -1, "SWAP"
            elif reverse_complement(ea) == a1 and reverse_complement(oa) == a2:
                sign, match_type = 1, "STRAND_DIRECT"
            elif reverse_complement(ea) == a2 and reverse_complement(oa) == a1:
                sign, match_type = -1, "STRAND_SWAP"
            if sign is None:
                continue
            try:
                beta = float(row.beta) * sign
                se = float(row.standard_error)
                p = float(row.p_value)
            except (TypeError, ValueError):
                continue
            if not (np.isfinite(beta) and np.isfinite(se) and se > 0 and np.isfinite(p) and 0 <= p <= 1):
                continue
            output.append(
                {
                    "locus_index": idx,
                    "chromosome": int(row.chromosome),
                    "variant_id": str(row.variant_id_y),
                    "position_GRCh37": int(row.position_GRCh37),
                    "BIM_A1": a1,
                    "BIM_A2": a2,
                    "gi": int(row.gi),
                    "rsid": str(row.variant_id_x),
                    "beta_A1": beta,
                    "standard_error": se,
                    "p_value": p,
                    "match_type": match_type,
                }
            )
        frame = pd.DataFrame(output)
        duplicate_count = 0
        if not frame.empty:
            duplicates = frame[frame.duplicated("variant_id", keep=False)]
            duplicate_count = int(duplicates["variant_id"].nunique())
            if duplicate_count:
                frame = frame[~frame["variant_id"].isin(set(duplicates["variant_id"]))].copy()
            frame = frame.drop_duplicates("variant_id").sort_values("position_GRCh37")
        target = OUT / f"PBC_locus_{idx:02d}_GRCh37_BIM_A1.tsv.gz"
        frame.to_csv(target, sep="\t", index=False, compression="gzip")
        if not frame.empty:
            combined.append(frame)
        manifest.append(
            {
                "locus_index": idx,
                "chromosome": int(locus.chromosomes),
                "region_start_GRCh37": int(locus.min_bp_grch37),
                "region_end_GRCh37": int(locus.max_bp_grch37),
                "source_gwas_rows": int(len(source)),
                "eligible_rows": int(len(frame)),
                "duplicate_conflict_variants_excluded": duplicate_count,
                "min_p": None if frame.empty else float(frame["p_value"].min()),
                "output_sha256": sha256(target),
            }
        )
    all_rows = pd.concat(combined, ignore_index=True)
    if all_rows.duplicated(["locus_index", "variant_id"]).any():
        raise RuntimeError("duplicate harmonized disease keys")
    combined_path = OUT / "R7B1_PBC56_GRCh37_BIM_A1.tsv.gz"
    all_rows.to_csv(combined_path, sep="\t", index=False, compression="gzip")
    man = pd.DataFrame(manifest)
    man.to_csv(OUT / "R7B1_PBC56_harmonization_manifest.tsv", sep="\t", index=False)
    state = {
        "schema": "R7B1_PBC56_HARMONIZATION_1.0",
        "loci": int(len(man)),
        "loci_ge_200_variants": int((man["eligible_rows"] >= 200).sum()),
        "total_eligible_rows": int(len(all_rows)),
        "minimum_locus_rows": int(man["eligible_rows"].min()),
        "maximum_locus_rows": int(man["eligible_rows"].max()),
        "gate": "PASS" if len(man) == 56 and (man["eligible_rows"] >= 200).all() else "HOLD",
        "gwas_sha256": sha256(GWAS),
        "bim_sha256": sha256(BIM),
        "ranges_sha256": sha256(RANGES),
        "combined_sha256": sha256(combined_path),
    }
    (OUT / "R7B1_PBC56_harmonization_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
