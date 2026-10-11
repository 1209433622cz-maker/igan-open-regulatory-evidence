#!/usr/bin/env python3
"""Freeze the exact R7B1B workload and required GJOKA members."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
TRIGGER = ROOT / "3_results/04_integration/R7B1/R7B1_multisignal_trigger_set.tsv"
INVENTORY = ROOT / "3_results/01_intake/R7A1A/R7A1A_PBC_GJOKA_remote_member_inventory.tsv"
OUT = ROOT / "3_results/00_audit/R7B1B"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    triggers = pd.read_csv(TRIGGER, sep="\t").sort_values("comparison_id")
    inventory = pd.read_csv(INVENTORY, sep="\t")
    if len(triggers) != 184 or triggers["comparison_id"].duplicated().any():
        raise RuntimeError("expected exact 184-row trigger set")
    loci = sorted(map(int, triggers["locus_index"].unique()))
    expected_members = []
    for locus in loci:
        expected_members.extend([f"GJOKA_SUMSTATS/sumstats_{locus}.assoc.logistic", f"GJOKA_SUMSTATS/covmat_{locus}.ld"])
    required = inventory[inventory["member"].isin(expected_members)].copy().sort_values("member")
    if len(required) != 50 or set(required["member"]) != set(expected_members):
        raise RuntimeError("remote inventory does not contain exact required member set")
    required.insert(0, "locus_index", required["member"].map(lambda x: int(x.split("_")[-1].split(".")[0])))
    required["local_status"] = "PENDING_DOWNLOAD_OR_EXISTING_BYTE_VALIDATION"
    required.to_csv(OUT / "R7B1B_required_GJOKA_members.tsv", sep="\t", index=False)

    work = triggers.copy()
    work["cell_locus_block_id"] = work.apply(lambda r: f"L{int(r.locus_index):02d}__{r.cell_type}", axis=1)
    work["disease_source"] = "GJOKA_STUDY_DERIVED"
    work["PF10_summary"] = "CURRENT_RELEASE_DE_NOVO_COMPLETE"
    work["PF10_model_matched_LD"] = "PENDING"
    work["PF50_summary_and_model_matched_LD"] = "PENDING"
    work["multisignal_terminal_class"] = "PENDING"
    work.to_csv(OUT / "R7B1B_exact_184_comparison_workload.tsv", sep="\t", index=False)
    blocks = work[["cell_locus_block_id", "locus_index", "cell_type", "qtl_N"]].drop_duplicates().sort_values(["locus_index", "cell_type"])
    blocks.to_csv(OUT / "R7B1B_exact_120_cell_locus_blocks.tsv", sep="\t", index=False)

    state = {
        "schema": "R7B1B_EXACT_WORKLOAD_1.0",
        "status": "FROZEN_BEFORE_MULTISIGNAL_RESULTS",
        "trigger_comparisons": len(work),
        "trigger_loci": len(loci),
        "trigger_genes": int(work["gene"].nunique()),
        "trigger_cells": int(work["cell_type"].nunique()),
        "cell_locus_blocks": len(blocks),
        "required_GJOKA_members": len(required),
        "required_GJOKA_compressed_bytes": int(required["compressed_bytes"].sum()),
        "required_GJOKA_uncompressed_bytes": int(required["uncompressed_bytes"].sum()),
        "trigger_set_sha256": sha256(TRIGGER),
        "remote_inventory_sha256": sha256(INVENTORY),
        "no_post_result_filtering": True,
        "next": "DOWNLOAD_50_GJOKA_MEMBERS_THEN_BUILD_120_DUAL_MODEL_QTL_LD_BLOCKS",
    }
    (OUT / "R7B1B_exact_workload_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
