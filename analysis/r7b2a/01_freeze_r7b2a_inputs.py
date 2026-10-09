#!/usr/bin/env python3
"""Freeze the exact R7B2A A0/A1/A2/M input identities before new ABF results."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
WORK = ROOT / "3_results/00_audit/R7B1B_v2/R7B1B_v2_exact_642_high_information_comparisons.tsv"
A0 = ROOT / "3_results/04_integration/R7B1/R7B1_current_PF10_ABF_all_comparisons.tsv.gz"
M = ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"
BRIDGE = ROOT / "3_results/01_gwas/R7B1/R7B1_PBC56_GRCh37_BIM_A1.tsv.gz"
QTL_DIR = ROOT / "3_results/03_qtl/R7B1B_v2/dualmodel_qtl"
BLOCK_DIR = ROOT / "3_results/04_integration/R7B1B_v2/sourceLD_blocks"
GJ_DIR = ROOT / "1_data/study_inputs/PBC_GJOKA/R7B1B_v2"
GJ_RECEIPTS = ROOT / "3_results/00_audit/R7B1B_v2/R7B1B_v2_GJOKA_member_receipts.tsv"
PROTOCOL = ROOT / "0_admin/protocols/R7B2A/R7B2A_matched_input_attribution_freeze_2026-10-09.md"
RPV3 = ROOT / "9.Version/PBC_研究计划书_RP_v3_调控归因可靠性与同输入方法对照_20261009.docx"
OUT = ROOT / "3_results/00_audit/R7B2A/input_freeze"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def variant_hash(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(values) + "\n").encode("utf-8")).hexdigest()


def read_gjoka(locus: int) -> pd.DataFrame:
    path = GJ_DIR / f"sumstats_{locus}.assoc.logistic"
    frame = pd.read_csv(path, sep=r"\s+")
    if "TEST" in frame.columns:
        frame = frame[frame["TEST"].astype(str) == "ADD"].copy()
    required = {"SNP", "BP", "A1", "BETA", "SE", "STAT", "NMISS"}
    if not required.issubset(frame.columns):
        raise RuntimeError(f"locus {locus}: GJOKA missing {sorted(required-set(frame.columns))}")
    frame["BP"] = pd.to_numeric(frame["BP"], errors="coerce")
    for col in ["BETA", "SE", "STAT", "NMISS"]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame = frame[np.isfinite(frame["STAT"]) & np.isfinite(frame["SE"]) & (frame["SE"] > 0)].copy()
    if frame.duplicated(["SNP", "BP"]).any():
        raise RuntimeError(f"locus {locus}: duplicate GJOKA SNP/BP")
    return frame


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in [WORK, A0, M, BRIDGE, GJ_RECEIPTS, PROTOCOL, RPV3]:
        if not path.is_file():
            raise RuntimeError(f"missing required file: {path}")

    work = pd.read_csv(WORK, sep="\t", dtype={"comparison_id": str}).sort_values("comparison_id")
    a0 = pd.read_csv(A0, sep="\t", dtype={"comparison_id": str}).set_index("comparison_id")
    m = pd.read_csv(M, sep="\t", dtype={"comparison_id": str}).set_index("comparison_id")
    bridge = pd.read_csv(BRIDGE, sep="\t", dtype={"variant_id": str, "rsid": str})
    receipts = pd.read_csv(GJ_RECEIPTS, sep="\t")
    if len(work) != 642 or work["comparison_id"].duplicated().any():
        raise RuntimeError("workload is not exact 642 unique comparison IDs")
    if not set(work["comparison_id"]).issubset(a0.index) or set(work["comparison_id"]) != set(m.index):
        raise RuntimeError("A0/M comparison identity drift")
    role_counts = work["R7B1B_v2_role"].value_counts().to_dict()
    expected_roles = {
        "PRIMARY_184_TRIGGER_VERIFICATION": 184,
        "H3_RESCUE_FALSIFICATION": 455,
        "BORDERLINE_HIGH_INFORMATION_CALIBRATION": 3,
    }
    if role_counts != expected_roles:
        raise RuntimeError(f"role drift: {role_counts}")

    # Revalidate the small GJOKA summary statistics used by A2. Large LD bytes
    # are not reread because M is frozen; their historical SHA-256 receipts are retained.
    source_rows: list[dict[str, object]] = []
    for locus in sorted(work["locus_index"].astype(int).unique()):
        for prefix in ["sumstats", "covmat"]:
            suffix = ".assoc.logistic" if prefix == "sumstats" else ".ld"
            path = GJ_DIR / f"{prefix}_{locus}{suffix}"
            rec = receipts[(receipts["locus_index"].astype(int) == locus) & receipts["member"].astype(str).str.endswith(path.name)]
            if len(rec) != 1 or not path.is_file():
                raise RuntimeError(f"locus {locus}: missing unique receipt/file for {path.name}")
            row = rec.iloc[0]
            if path.stat().st_size != int(row["bytes"]):
                raise RuntimeError(f"size drift: {path}")
            observed = sha256(path) if prefix == "sumstats" else str(row["sha256"])
            if prefix == "sumstats" and observed != str(row["sha256"]):
                raise RuntimeError(f"SHA-256 drift: {path}")
            source_rows.append({
                "locus_index": locus,
                "role": "A2_DISEASE_SUMMARY" if prefix == "sumstats" else "FROZEN_M_DISEASE_LD",
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": observed,
                "verification": "CURRENT_FULL_SHA256" if prefix == "sumstats" else "HISTORICAL_RECEIPT_SIZE_MATCH",
            })

    bridge_by_locus = {int(k): v.copy() for k, v in bridge.groupby("locus_index")}
    gj_cache = {int(locus): read_gjoka(int(locus)) for locus in work["locus_index"].unique()}
    identity_rows: list[dict[str, object]] = []
    membership_rows: list[pd.DataFrame] = []

    for n, job in enumerate(work.itertuples(index=False), start=1):
        cid = str(job.comparison_id)
        locus = int(job.locus_index)
        cell = str(job.cell_type)
        qtl_path = QTL_DIR / f"{cid}_PF10_QTL.tsv.gz"
        block_path = BLOCK_DIR / f"L{locus:02d}_{cell}" / "variants.tsv.gz"
        block_qc_path = block_path.parent / "block_QC.json"
        if not qtl_path.is_file() or not block_path.is_file() or not block_qc_path.is_file():
            raise RuntimeError(f"{cid}: missing QTL or block input")
        qtl = pd.read_csv(qtl_path, sep="\t", dtype={"variant_id": str, "rsid": str})
        block = pd.read_csv(block_path, sep="\t", dtype={"variant_id": str, "rsid": str}).sort_values("block_order_zero_based")
        if qtl["variant_id"].duplicated().any() or block["variant_id"].duplicated().any():
            raise RuntimeError(f"{cid}: duplicate QTL/block variants")
        s_a = qtl["variant_id"].astype(str).tolist()
        a0_row = a0.loc[cid]
        if len(s_a) != int(a0_row["n_variants"]) or variant_hash(s_a) != str(a0_row["variant_set_sha256"]):
            raise RuntimeError(f"{cid}: S_A does not reproduce A0 set identity")

        b = bridge_by_locus[locus][["variant_id", "rsid", "position_GRCh37", "BIM_A1", "BIM_A2"]].copy()
        b["position_GRCh37"] = pd.to_numeric(b["position_GRCh37"], errors="coerce").astype("Int64")
        b["BIM_A1"] = b["BIM_A1"].astype(str).str.upper()
        b["BIM_A2"] = b["BIM_A2"].astype(str).str.upper()
        v = block[["variant_id", "rsid", "position_GRCh37", "BIM_A1", "BIM_A2", "block_order_zero_based"]].copy()
        v["position_GRCh37"] = pd.to_numeric(v["position_GRCh37"], errors="coerce").astype("Int64")
        v["BIM_A1"] = v["BIM_A1"].astype(str).str.upper()
        v["BIM_A2"] = v["BIM_A2"].astype(str).str.upper()
        mapped = v.merge(b, on="variant_id", suffixes=("_block", "_bridge"), how="inner")
        mapped = mapped[
            (mapped["position_GRCh37_block"] == mapped["position_GRCh37_bridge"])
            & (mapped["BIM_A1_block"] == mapped["BIM_A1_bridge"])
            & (mapped["BIM_A2_block"] == mapped["BIM_A2_bridge"])
        ].copy()
        gj = gj_cache[locus]
        mapped = mapped.merge(gj, left_on=["rsid_bridge", "position_GRCh37_block"], right_on=["SNP", "BP"], how="inner")
        mapped = mapped[np.isfinite(mapped["STAT"])].drop_duplicates("variant_id").sort_values("block_order_zero_based")
        qtl_set = set(s_a)
        mapped = mapped[mapped["variant_id"].isin(qtl_set)].copy()
        s_m = mapped["variant_id"].astype(str).tolist()
        recorded_m = int(m.loc[cid, "common_variants_min"])
        if len(s_m) < 200 or len(s_m) != recorded_m:
            raise RuntimeError(f"{cid}: S_M size {len(s_m)} != recorded {recorded_m}")

        a1 = mapped["A1"].astype(str).str.upper()
        bim1 = mapped["BIM_A1_block"].astype(str).str.upper()
        bim2 = mapped["BIM_A2_block"].astype(str).str.upper()
        exact = int((a1 == bim1).sum())
        flipped = int((a1 == bim2).sum())
        unresolved = int((~((a1 == bim1) | (a1 == bim2))).sum())
        if unresolved:
            raise RuntimeError(f"{cid}: unresolved GJOKA allele rows={unresolved}")

        native_sdy = math.sqrt(
            float(np.sum((1.0 / np.square(qtl.set_index("variant_id").loc[s_m, "slope_se"].to_numpy(float)))
                         * (2.0 * int(qtl["n_expression_donors"].iloc[0])
                            * qtl.set_index("variant_id").loc[s_m, "maf"].to_numpy(float)
                            * (1.0 - qtl.set_index("variant_id").loc[s_m, "maf"].to_numpy(float))))
                  / np.sum(np.square(1.0 / np.square(qtl.set_index("variant_id").loc[s_m, "slope_se"].to_numpy(float))))
            )
        )
        block_qc = json.loads(block_qc_path.read_text(encoding="utf-8"))
        identity_rows.append({
            "comparison_id": cid,
            "locus_index": locus,
            "gene": str(job.gene),
            "cell_type": cell,
            "R7B1B_v2_role": str(job.R7B1B_v2_role),
            "A0_state": str(m.loc[cid, "ABF_state"]),
            "M_state": str(m.loc[cid, "PF10_multisignal_state"]),
            "S_A_n": len(s_a),
            "S_A_sha256": variant_hash(s_a),
            "S_M_n": len(s_m),
            "S_M_sha256": variant_hash(s_m),
            "removed_n": len(s_a) - len(s_m),
            "removed_fraction": (len(s_a) - len(s_m)) / len(s_a),
            "qtl_N": int(qtl["n_expression_donors"].iloc[0]),
            "qtl_file_sha256": sha256(qtl_path),
            "source_ld_variant_sha256": str(block_qc["variant_metadata_sha256"]),
            "source_ld_PF10_sha256": str(block_qc["modes"]["PF10"]["ld_sha256"]),
            "fixed_sdY": float(a0_row["sdY_estimate"]),
            "native_SM_sdY": native_sdy,
            "gjoka_A1_exact_n": exact,
            "gjoka_A1_flipped_n": flipped,
            "gjoka_A1_unresolved_n": unresolved,
            "gjoka_NMISS_min": int(mapped["NMISS"].min()),
            "gjoka_NMISS_median": float(mapped["NMISS"].median()),
            "gjoka_NMISS_max": int(mapped["NMISS"].max()),
            "gjoka_beta_se_vs_STAT_max_abs_delta": float(np.max(np.abs(mapped["BETA"] / mapped["SE"] - mapped["STAT"]))),
            "input_status": "PASS",
        })
        for label, variants in [("S_A", s_a), ("S_M", s_m)]:
            membership_rows.append(pd.DataFrame({
                "comparison_id": cid,
                "set": label,
                "order_zero_based": np.arange(len(variants), dtype=int),
                "variant_id": variants,
            }))
        if n % 100 == 0:
            print(f"INPUT_FREEZE {n}/642", flush=True)

    identity = pd.DataFrame(identity_rows).sort_values("comparison_id")
    membership = pd.concat(membership_rows, ignore_index=True)
    if len(identity) != 642 or identity["comparison_id"].duplicated().any() or not (identity["input_status"] == "PASS").all():
        raise RuntimeError("identity output incomplete")
    if not (identity["S_M_n"].to_numpy(int) == m.loc[identity["comparison_id"], "common_variants_min"].to_numpy(int)).all():
        raise RuntimeError("S_M/M count identity failed")

    identity_path = OUT / "R7B2A_arm_identity_642.tsv"
    membership_path = OUT / "R7B2A_variant_membership_SA_SM.tsv.gz"
    source_path = OUT / "R7B2A_source_file_manifest.tsv"
    identity.to_csv(identity_path, sep="\t", index=False)
    membership.to_csv(membership_path, sep="\t", index=False, compression="gzip")
    pd.DataFrame(source_rows).to_csv(source_path, sep="\t", index=False)
    state = {
        "schema": "R7B2A_INPUT_FREEZE_1.0",
        "status": "PASS",
        "gate": "V3-G0_INPUT_LOCK_PASS",
        "comparisons": 642,
        "roles": role_counts,
        "loci": int(identity["locus_index"].nunique()),
        "genes": int(identity["gene"].nunique()),
        "cells": int(identity["cell_type"].nunique()),
        "S_A_n_range": [int(identity["S_A_n"].min()), int(identity["S_A_n"].max())],
        "S_M_n_range": [int(identity["S_M_n"].min()), int(identity["S_M_n"].max())],
        "removed_n_range": [int(identity["removed_n"].min()), int(identity["removed_n"].max())],
        "removed_n_median": float(identity["removed_n"].median()),
        "removed_fraction_median": float(identity["removed_fraction"].median()),
        "gjoka_A1_exact_total": int(identity["gjoka_A1_exact_n"].sum()),
        "gjoka_A1_flipped_total": int(identity["gjoka_A1_flipped_n"].sum()),
        "gjoka_A1_unresolved_total": int(identity["gjoka_A1_unresolved_n"].sum()),
        "protocol_sha256": sha256(PROTOCOL),
        "rp_v3_sha256": sha256(RPV3),
        "outputs": {
            "identity_sha256": sha256(identity_path),
            "membership_sha256": sha256(membership_path),
            "source_manifest_sha256": sha256(source_path),
        },
        "next": "R7B2A_A0_REPLAY_AND_A1_A2_ABF",
    }
    (OUT / "R7B2A_input_freeze_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
