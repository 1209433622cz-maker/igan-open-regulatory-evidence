#!/usr/bin/env python3
"""Adjudicate R7B2A A0 -> A1 -> A2 -> M trajectories on the frozen 642.

This script is intentionally descriptive. Real-data state transitions do not
establish causal truth or method superiority; they localize where decisions
change when the support set, disease statistics, or statistical model changes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
ABF_PATH = ROOT / "3_results/04_integration/R7B2A/matched_input_abf/R7B2A_matched_input_ABF_long.tsv.gz"
IDENTITY_PATH = ROOT / "3_results/00_audit/R7B2A/input_freeze/R7B2A_arm_identity_642.tsv"
M_PATH = ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"
OUT = ROOT / "3_results/04_integration/R7B2A/adjudication"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def abf_simple(value: str) -> str:
    return {
        "ABF_H4_DOMINANT": "H4",
        "ABF_H3_DOMINANT": "H3",
        "ABF_AMBIGUOUS": "AMBIGUOUS",
        "ABF_H4_BORDERLINE": "H4_BORDERLINE",
        "ABF_UNINFORMATIVE_OR_NO_TRIGGER": "UNINFORMATIVE",
    }[value]


def m_simple(value: str) -> str:
    return {
        "H4_SUPPORTED_STABLE": "H4",
        "H3_SUPPORTED_STABLE": "H3",
        "MODEL_SENSITIVE": "MODEL_SENSITIVE",
        "UNINFORMATIVE": "UNINFORMATIVE",
    }[value]


def transition_table(frame: pd.DataFrame, left: str, right: str, label: str) -> pd.DataFrame:
    out = (
        frame.groupby([left, right], dropna=False)
        .size()
        .rename("n")
        .reset_index()
        .rename(columns={left: "from_state", right: "to_state"})
    )
    out.insert(0, "transition", label)
    out["changed"] = out["from_state"] != out["to_state"]
    out["rate_of_642"] = out["n"] / len(frame)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    abf = pd.read_csv(ABF_PATH, sep="\t")
    identity = pd.read_csv(IDENTITY_PATH, sep="\t")
    multi = pd.read_csv(M_PATH, sep="\t")

    expected_arms = {
        "A0_REPLAY", "A1_FIXED_SDY", "A1_NATIVE_SDY",
        "A2_MATCHEDZ_FIXED_SDY", "A2_MATCHEDZ_NATIVE_SDY", "A2_ROUNDED_FIXED_SDY",
    }
    if set(abf["arm"]) != expected_arms or len(abf) != 642 * 6:
        raise RuntimeError("ABF long table does not contain the frozen 642 x 6 arms")
    if identity["comparison_id"].nunique() != 642 or multi["comparison_id"].nunique() != 642:
        raise RuntimeError("identity or multi-signal table is not 642-comparison complete")

    value_cols = [
        "n_variants", "PP_H3", "PP_H4", "H3_plus_H4", "H4_over_H3H4",
        "shared_top_variant", "ABF_state", "status",
    ]
    wide_parts = []
    for arm, prefix in [
        ("A0_REPLAY", "A0"),
        ("A1_FIXED_SDY", "A1"),
        ("A1_NATIVE_SDY", "A1_NATIVE"),
        ("A2_MATCHEDZ_FIXED_SDY", "A2"),
        ("A2_MATCHEDZ_NATIVE_SDY", "A2_NATIVE"),
        ("A2_ROUNDED_FIXED_SDY", "A2_ROUNDED"),
    ]:
        part = abf.loc[abf["arm"].eq(arm), ["comparison_id", *value_cols]].copy()
        part = part.rename(columns={c: f"{prefix}_{c}" for c in value_cols})
        wide_parts.append(part)

    out = identity.copy()
    for part in wide_parts:
        out = out.merge(part, on="comparison_id", how="left", validate="one_to_one")
    mcols = [
        "comparison_id", "ABF_classification", "ABF_state", "PF10_multisignal_state",
        "reclassification", "PF10_PF50_sensitivity", "QC_error", "common_variants_min",
        "pf10_l10_best_h4", "pf10_l10_best_h4_ratio", "pf10_l10_signal_pairs",
    ]
    out = out.merge(multi[mcols], on="comparison_id", how="left", validate="one_to_one")

    for stage in ["A0", "A1", "A1_NATIVE", "A2", "A2_NATIVE", "A2_ROUNDED"]:
        out[f"{stage}_simple_state"] = out[f"{stage}_ABF_state"].map(abf_simple)
    out["M_simple_state"] = out["PF10_multisignal_state"].map(m_simple)
    if out[["A0_simple_state", "A1_simple_state", "A2_simple_state", "M_simple_state"]].isna().any().any():
        raise RuntimeError("unmapped state detected")

    out["A0_to_A1_changed"] = out["A0_simple_state"] != out["A1_simple_state"]
    out["A1_to_A2_changed"] = out["A1_simple_state"] != out["A2_simple_state"]
    out["A2_to_M_changed"] = out["A2_simple_state"] != out["M_simple_state"]
    out["fixed_to_native_A1_changed"] = out["A1_simple_state"] != out["A1_NATIVE_simple_state"]
    out["fixed_to_native_A2_changed"] = out["A2_simple_state"] != out["A2_NATIVE_simple_state"]
    out["matchedz_to_rounded_A2_changed"] = out["A2_simple_state"] != out["A2_ROUNDED_simple_state"]
    out["trajectory"] = (
        out["A0_simple_state"] + " -> " + out["A1_simple_state"] + " -> "
        + out["A2_simple_state"] + " -> " + out["M_simple_state"]
    )

    trajectory_path = OUT / "R7B2A_642_four_arm_trajectories.tsv"
    out.to_csv(trajectory_path, sep="\t", index=False)

    matrices = pd.concat(
        [
            transition_table(out, "A0_simple_state", "A1_simple_state", "A0_TO_A1_SUPPORT_SET"),
            transition_table(out, "A1_simple_state", "A2_simple_state", "A1_TO_A2_DISEASE_STATS"),
            transition_table(out, "A2_simple_state", "M_simple_state", "A2_TO_M_MODEL"),
        ],
        ignore_index=True,
    )
    matrix_path = OUT / "R7B2A_adjacent_transition_matrices.tsv"
    matrices.to_csv(matrix_path, sep="\t", index=False)

    original_direction = out[
        out["reclassification"].isin(["H4_TO_H3", "H3_TO_H4"])
    ].copy()
    if len(original_direction) != 12:
        raise RuntimeError(f"expected 12 historical direction changes, observed {len(original_direction)}")
    original_direction["strict_direction_retained_after_matching"] = (
        ((original_direction["A2_simple_state"] == "H4") & (original_direction["M_simple_state"] == "H3"))
        | ((original_direction["A2_simple_state"] == "H3") & (original_direction["M_simple_state"] == "H4"))
    )
    original_path = OUT / "R7B2A_historical_12_direction_changes_audit.tsv"
    original_direction.to_csv(original_path, sep="\t", index=False)

    strict_h4_h3 = int(((out["A2_simple_state"] == "H4") & (out["M_simple_state"] == "H3")).sum())
    strict_h3_h4 = int(((out["A2_simple_state"] == "H3") & (out["M_simple_state"] == "H4")).sum())
    summary_rows = [
        {"metric": "frozen_comparisons", "value": len(out), "interpretation": "fixed universe"},
        {"metric": "support_set_state_changes_A0_to_A1", "value": int(out["A0_to_A1_changed"].sum()), "interpretation": "support-set attributable"},
        {"metric": "disease_stat_state_changes_A1_to_A2", "value": int(out["A1_to_A2_changed"].sum()), "interpretation": "disease-stat attributable"},
        {"metric": "model_state_changes_A2_to_M", "value": int(out["A2_to_M_changed"].sum()), "interpretation": "matched-input model transition"},
        {"metric": "matched_input_H4_to_H3", "value": strict_h4_h3, "interpretation": "descriptive falsification direction"},
        {"metric": "matched_input_H3_to_H4", "value": strict_h3_h4, "interpretation": "descriptive rescue direction"},
        {"metric": "matched_input_stable_H4", "value": int(((out["A2_simple_state"] == "H4") & (out["M_simple_state"] == "H4")).sum()), "interpretation": "stable H4"},
        {"metric": "matched_input_stable_H3", "value": int(((out["A2_simple_state"] == "H3") & (out["M_simple_state"] == "H3")).sum()), "interpretation": "stable H3"},
        {"metric": "historical_12_retained_strict_direction", "value": int(original_direction["strict_direction_retained_after_matching"].sum()), "interpretation": "strict H4/H3 direction after matching"},
        {"metric": "fixed_to_native_A1_state_changes", "value": int(out["fixed_to_native_A1_changed"].sum()), "interpretation": "scale sensitivity"},
        {"metric": "fixed_to_native_A2_state_changes", "value": int(out["fixed_to_native_A2_changed"].sum()), "interpretation": "scale sensitivity"},
        {"metric": "matchedz_to_rounded_A2_state_changes", "value": int(out["matchedz_to_rounded_A2_changed"].sum()), "interpretation": "GJOKA statistic sensitivity"},
    ]
    summary = pd.DataFrame(summary_rows)
    summary_path = OUT / "R7B2A_attribution_summary.tsv"
    summary.to_csv(summary_path, sep="\t", index=False)

    state = {
        "schema": "R7B2A_ATTRIBUTION_1.0",
        "status": "PASS",
        "gate": "V3-G4_ATTRIBUTION_PASS",
        "comparisons": len(out),
        "support_set_state_changes": int(out["A0_to_A1_changed"].sum()),
        "disease_stat_state_changes": int(out["A1_to_A2_changed"].sum()),
        "matched_input_model_state_changes": int(out["A2_to_M_changed"].sum()),
        "matched_input_strict_H4_to_H3": strict_h4_h3,
        "matched_input_strict_H3_to_H4": strict_h3_h4,
        "matched_input_stable_H4": int(((out["A2_simple_state"] == "H4") & (out["M_simple_state"] == "H4")).sum()),
        "matched_input_stable_H3": int(((out["A2_simple_state"] == "H3") & (out["M_simple_state"] == "H3")).sum()),
        "historical_direction_changes": 12,
        "historical_direction_changes_retained_strict": int(original_direction["strict_direction_retained_after_matching"].sum()),
        "A1_fixed_native_state_changes": int(out["fixed_to_native_A1_changed"].sum()),
        "A2_fixed_native_state_changes": int(out["fixed_to_native_A2_changed"].sum()),
        "A2_matchedz_rounded_state_changes": int(out["matchedz_to_rounded_A2_changed"].sum()),
        "interpretation_boundary": "Real-data transitions localize decision changes; they do not establish causal truth or general method superiority.",
        "outputs": {
            p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)}
            for p in [trajectory_path, matrix_path, original_path, summary_path]
        },
    }
    state_path = OUT / "R7B2A_attribution_state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
