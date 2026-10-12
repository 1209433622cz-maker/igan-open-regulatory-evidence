#!/usr/bin/env python3
"""Freeze a bounded effective-N stress-test subset and generate its R runner.

The primary N=24,510 remains source-matched to Gjoka & Cordell.  This probe is
an additional robustness analysis; it is not a correction of the primary fit.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
OUT = ROOT / "3_results" / "00_audit" / "R7C3H0"
WORK_OUT = OUT / "R7C3H0_neff_probe_comparisons.tsv"
STATE_OUT = OUT / "R7C3H0_neff_probe_selection_state.json"
TRAJ = ROOT / "3_results" / "04_integration" / "R7B2A" / "adjudication" / "R7B2A_642_four_arm_trajectories.tsv"
FROZEN = ROOT / "3_results" / "04_integration" / "R7B1B_v2" / "adjudication" / "R7B1B_v2_642_bidirectional_reclassification.tsv"
PAIR = ROOT / "3_results" / "04_integration" / "R7B1B_v2" / "adjudication" / "R7B1B_v2_all_signal_pair_posteriors.tsv.gz"
ORIGINAL_R = ROOT / "2_code" / "06_intake" / "r7b1" / "11_run_r7b1b_v2_multisignal_locus.R"
GENERATED_R = ROOT / "2_code" / "06_intake" / "r7c3h0" / "02_run_neff_probe_locus.R"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    traj = pd.read_csv(TRAJ, sep="\t", dtype={"comparison_id": str})
    frozen = pd.read_csv(FROZEN, sep="\t", dtype={"comparison_id": str})
    pairs = pd.read_csv(PAIR, sep="\t", low_memory=False)
    chosen: dict[str, set[str]] = {}

    def add(ids, reason: str) -> None:
        for cid in ids:
            chosen.setdefault(str(cid), set()).add(reason)

    strict = traj[
        ((traj["A2_simple_state"] == "H4") & (traj["M_simple_state"] == "H3"))
        | ((traj["A2_simple_state"] == "H3") & (traj["M_simple_state"] == "H4"))
    ]
    add(strict["comparison_id"], "ALL_18_STRICT_A2_TO_M_REVERSALS")

    key = frozen[
        ((frozen["gene"] == "FCRL3") & frozen["cell_type"].isin(["CD8_ET", "B_IN", "B_MEM"]))
        | ((frozen["gene"] == "IL12RB2") & frozen["cell_type"].str.contains("NK", na=False))
    ]
    add(key["comparison_id"], "MANUSCRIPT_KEY_AXES")

    # Comparisons closest to the primary PF10 H4 decision threshold.
    h4 = frozen[frozen["PF10_multisignal_state"] == "H4_SUPPORTED_STABLE"].copy()
    h4["threshold_margin"] = (h4["pf10_l10_best_h4"] - 0.80).abs()
    add(h4.nsmallest(6, "threshold_margin")["comparison_id"], "H4_THRESHOLD_MARGIN_6")

    # Stress high-information comparisons whose final state is not definite.
    d = pairs[(pairs["config"] == "PF10_L10") & np.isclose(pairs["p12"], 1e-5)].copy()
    info = d.groupby("comparison_id", as_index=False)["H3_plus_H4"].max()
    uncertain = frozen[frozen["PF10_multisignal_state"].isin(["MODEL_SENSITIVE", "UNINFORMATIVE"])][["comparison_id"]].merge(info, on="comparison_id", how="left")
    add(uncertain.nlargest(6, "H3_plus_H4")["comparison_id"], "UNCERTAIN_HIGH_INFORMATION_6")

    selected_ids = sorted(chosen)
    base_cols = ["comparison_id", "locus_index", "gene", "cell_type", "R7B1B_v2_role", "ABF_classification"]
    selected = frozen[frozen["comparison_id"].isin(selected_ids)][base_cols].copy()
    selected = selected.rename(columns={"ABF_classification": "classification"})
    selected["selection_reason"] = selected["comparison_id"].map(lambda x: ";".join(sorted(chosen[x])))
    selected["primary_disease_N"] = 24510.0
    selected["probe_disease_N"] = 4.0 / (1.0 / 8021.0 + 1.0 / 16489.0)
    selected = selected.sort_values(["locus_index", "comparison_id"])
    if len(selected) < 24 or selected["comparison_id"].duplicated().any():
        raise RuntimeError(f"unexpected bounded probe size: {len(selected)}")
    selected.to_csv(WORK_OUT, sep="\t", index=False)

    text = ORIGINAL_R.read_text(encoding="utf-8")
    replacements = {
        'work_path <- file.path(root,"3_results","00_audit","R7B1B_v2","R7B1B_v2_exact_642_high_information_comparisons.tsv")':
            'work_path <- file.path(root,"3_results","00_audit","R7C3H0","R7C3H0_neff_probe_comparisons.tsv")',
        'outbase <- file.path(root,"3_results","04_integration","R7B1B_v2","multisignal")':
            'outbase <- file.path(root,"3_results","04_integration","R7C3H0","neff_probe","multisignal")',
        'locus <- as.integer(locus_env)':
            'locus <- as.integer(locus_env)\ndisease_n <- as.numeric(Sys.getenv("R7C3H_DISEASE_N", unset="21584.376825785395"))\nif (!is.finite(disease_n) || disease_n <= 0) stop("invalid R7C3H_DISEASE_N")',
        'fitD <- susie_rss(z=zD,R=dld,n=24510,L=cfg$L,':
            'fitD <- susie_rss(z=zD,R=dld,n=disease_n,L=cfg$L,',
        'ds0 <- safe_s_rss(zD,dld,24510)':
            'ds0 <- safe_s_rss(zD,dld,disease_n)',
        'ddiag <- list(s=ds0,k=safe_kriging(zD,dld,24510,ds0))':
            'ddiag <- list(s=ds0,k=safe_kriging(zD,dld,disease_n,ds0))',
        'schema="R7B1B_V2_COMPARISON_1.0",status="COMPLETE",comparison_id=cid,':
            'schema="R7C3H0_NEFF_PROBE_COMPARISON_1.0",status="COMPLETE",comparison_id=cid,disease_n=disease_n,',
        'schema="R7B1B_V2_COMPARISON_1.0",status="QC_FAILURE",comparison_id=cid,':
            'schema="R7C3H0_NEFF_PROBE_COMPARISON_1.0",status="QC_FAILURE",comparison_id=cid,disease_n=disease_n,',
        'schema="R7B1B_V2_LOCUS_1.0",':
            'schema="R7C3H0_NEFF_PROBE_LOCUS_1.0",disease_n=disease_n,',
    }
    for old, new in replacements.items():
        if text.count(old) != 1:
            raise RuntimeError(f"runner template contract drift: {old[:80]} count={text.count(old)}")
        text = text.replace(old, new)
    GENERATED_R.write_text(text, encoding="utf-8")

    state = {
        "schema": "R7C3H0_NEFF_PROBE_SELECTION_1.0",
        "status": "PASS",
        "scientific_role": "SECONDARY_ROBUSTNESS_STRESS_TEST_NOT_PRIMARY_CORRECTION",
        "source_matched_primary_N": 24510,
        "probe_effective_N": float(selected["probe_disease_N"].iloc[0]),
        "comparisons": len(selected),
        "loci": int(selected["locus_index"].nunique()),
        "reason_counts_nonexclusive": {reason: sum(reason in reasons for reasons in chosen.values()) for reason in sorted({x for v in chosen.values() for x in v})},
        "workload_sha256": sha(WORK_OUT),
        "original_runner_sha256": sha(ORIGINAL_R),
        "generated_runner_sha256": sha(GENERATED_R),
        "primary_source_evidence": "Gjoka & Cordell explicitly applied SuSiE-RSS with total N=24,510 (8,021 cases; 16,489 controls).",
    }
    STATE_OUT.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
