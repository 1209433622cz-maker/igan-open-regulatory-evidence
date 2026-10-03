#!/usr/bin/env python3
"""Freeze the symmetric R7B1B v2 high-information workload.

This step reads only the already frozen R7B1A single-causal table. It does not
read or adapt to any R7B1B multi-signal result.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
ABF = ROOT / "3_results/04_integration/R7B1/R7B1_current_PF10_ABF_all_comparisons.tsv.gz"
ORIGINAL_TRIGGER = ROOT / "3_results/04_integration/R7B1/R7B1_multisignal_trigger_set.tsv"
INVENTORY = ROOT / "3_results/01_intake/R7A1A/R7A1A_PBC_GJOKA_remote_member_inventory.tsv"
OUT = ROOT / "3_results/00_audit/R7B1B_v2"
EXPECTED_ORIGINAL_TRIGGER_SHA256 = "bac35fe7572a336ceedcf60a19a3d4f7f8c3cd97337ebd34a2d08e5360cb1f0e"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if sha256(ORIGINAL_TRIGGER) != EXPECTED_ORIGINAL_TRIGGER_SHA256:
        raise RuntimeError("original immutable 184-trigger hash changed")

    master = pd.read_csv(ABF, sep="\t")
    original = pd.read_csv(ORIGINAL_TRIGGER, sep="\t")
    if len(master) != 6923 or master["comparison_id"].duplicated().any():
        raise RuntimeError("R7B1A master is not the exact 6,923-row frozen universe")
    eligible = master[master["n_variants"] >= 200].copy()
    if len(eligible) != 5460:
        raise RuntimeError(f"expected 5,460 ABF-eligible rows, got {len(eligible)}")

    work = eligible[eligible["H3_plus_H4"] >= 0.80].copy().sort_values("comparison_id")
    if len(work) != 642:
        raise RuntimeError(f"expected 642 high-information rows, got {len(work)}")
    original_ids = set(original["comparison_id"].astype(str))
    work_ids = set(work["comparison_id"].astype(str))
    if len(original_ids) != 184 or not original_ids.issubset(work_ids):
        raise RuntimeError("immutable primary 184 is not nested exactly in v2")

    is_primary = work["comparison_id"].astype(str).isin(original_ids)
    is_h3 = work["classification"].eq("H3_DISTINCT_SIGNAL")
    work["R7B1B_v2_role"] = "BORDERLINE_HIGH_INFORMATION_CALIBRATION"
    work.loc[is_primary, "R7B1B_v2_role"] = "PRIMARY_184_TRIGGER_VERIFICATION"
    work.loc[is_h3, "R7B1B_v2_role"] = "H3_RESCUE_FALSIFICATION"
    counts = work["R7B1B_v2_role"].value_counts().to_dict()
    expected_counts = {
        "PRIMARY_184_TRIGGER_VERIFICATION": 184,
        "H3_RESCUE_FALSIFICATION": 455,
        "BORDERLINE_HIGH_INFORMATION_CALIBRATION": 3,
    }
    if counts != expected_counts:
        raise RuntimeError((counts, expected_counts))

    workload_path = OUT / "R7B1B_v2_exact_642_high_information_comparisons.tsv"
    work.to_csv(workload_path, sep="\t", index=False)
    blocks = (
        work[["locus_index", "cell_type", "qtl_N"]]
        .drop_duplicates()
        .sort_values(["locus_index", "cell_type"])
        .copy()
    )
    blocks.insert(0, "cell_locus_block_id", blocks.apply(lambda row: f"L{int(row.locus_index):02d}__{row.cell_type}", axis=1))
    if len(blocks) != 286:
        raise RuntimeError(f"expected 286 cell-locus blocks, got {len(blocks)}")
    blocks_path = OUT / "R7B1B_v2_exact_286_cell_locus_blocks.tsv"
    blocks.to_csv(blocks_path, sep="\t", index=False)

    inventory = pd.read_csv(INVENTORY, sep="\t")
    loci = sorted(map(int, work["locus_index"].unique()))
    expected_members: list[str] = []
    for locus in loci:
        expected_members.extend(
            [
                f"GJOKA_SUMSTATS/covmat_{locus}.ld",
                f"GJOKA_SUMSTATS/sumstats_{locus}.assoc.logistic",
            ]
        )
    required = inventory[inventory["member"].isin(expected_members)].copy().sort_values("member")
    if len(required) != 94 or set(required["member"]) != set(expected_members):
        raise RuntimeError("94-member inventory mismatch")
    required.insert(0, "locus_index", required["member"].map(lambda value: int(value.split("_")[-1].split(".")[0])))
    required["local_status"] = "PENDING_DOWNLOAD_OR_EXISTING_BYTE_VALIDATION"
    required_path = OUT / "R7B1B_v2_required_94_GJOKA_members.tsv"
    required.to_csv(required_path, sep="\t", index=False)

    borderline = work[work["R7B1B_v2_role"] == "BORDERLINE_HIGH_INFORMATION_CALIBRATION"].copy()
    borderline_path = OUT / "R7B1B_v2_exact_3_borderline_calibration.tsv"
    borderline.to_csv(borderline_path, sep="\t", index=False)
    state = {
        "schema": "R7B1B_V2_FREEZE_1.1",
        "status": "FROZEN_BEFORE_MULTISIGNAL_RESULTS",
        "comparisons": len(work),
        "primary_184": int(is_primary.sum()),
        "h3_rescue": int(is_h3.sum()),
        "borderline": int((~(is_primary | is_h3)).sum()),
        "loci": len(loci),
        "genes": int(work["gene"].nunique()),
        "cells": int(work["cell_type"].nunique()),
        "blocks": len(blocks),
        "GJOKA_members": len(required),
        "GJOKA_compressed_bytes": int(required["compressed_bytes"].sum()),
        "GJOKA_uncompressed_bytes": int(required["uncompressed_bytes"].sum()),
        "ABF_sha256": sha256(ABF),
        "original_184_trigger_sha256": sha256(ORIGINAL_TRIGGER),
        "remote_inventory_sha256": sha256(INVENTORY),
        "outputs": {
            "workload_sha256": sha256(workload_path),
            "blocks_sha256": sha256(blocks_path),
            "required_members_sha256": sha256(required_path),
            "borderline_sha256": sha256(borderline_path),
        },
        "posterior_multisignal_read_before_freeze": False,
        "scope_ceiling": "PBC-wide ABF screening plus multi-signal reclassification of the prespecified high-information H3/H4 subset",
    }
    (OUT / "R7B1B_v2_freeze_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
