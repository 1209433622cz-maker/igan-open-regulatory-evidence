#!/usr/bin/env python3
"""Independent deterministic QA and workload freeze for the R7B1A ABF screen."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
FROZEN = ROOT / "3_results/03_qtl/R7B1/R7B1_frozen_comparison_universe.tsv"
ALL = ROOT / "3_results/04_integration/R7B1/R7B1_current_PF10_ABF_all_comparisons.tsv.gz"
TRIGGER = ROOT / "3_results/04_integration/R7B1/R7B1_multisignal_trigger_set.tsv"
STATE = ROOT / "3_results/04_integration/R7B1/R7B1_current_PF10_ABF_state.json"
QTL_DIR = ROOT / "3_results/03_qtl/R7B1/pf10_trigger_qtl"
OUT = ROOT / "3_results/00_audit/R7B1A"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frozen = pd.read_csv(FROZEN, sep="\t")
    all_rows = pd.read_csv(ALL, sep="\t")
    triggers = pd.read_csv(TRIGGER, sep="\t")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": json.dumps(detail, ensure_ascii=False, default=str)})

    expected_ids = set(frozen["comparison_id"].astype(str))
    observed_ids = set(all_rows["comparison_id"].astype(str))
    check("exact_frozen_key_set", len(frozen) == 6923 and len(all_rows) == 6923 and expected_ids == observed_ids, {"frozen": len(frozen), "observed": len(all_rows)})
    check("unique_result_keys", not all_rows["comparison_id"].duplicated().any(), int(all_rows["comparison_id"].duplicated().sum()))

    eligible = all_rows[all_rows["n_variants"] >= 200].copy()
    insufficient = all_rows[all_rows["n_variants"] < 200].copy()
    robust = (eligible["PP_H4"] >= 0.80) & (eligible["H4_over_H3H4"] >= 0.80)
    ambiguous = (~robust) & (eligible["H3_plus_H4"] >= 0.80) & eligible["H4_over_H3H4"].between(0.20, 0.80, inclusive="both")
    expected_trigger_ids = set(eligible.loc[robust | ambiguous, "comparison_id"].astype(str))
    check("trigger_logic_exact", expected_trigger_ids == set(triggers["comparison_id"].astype(str)), {"expected": len(expected_trigger_ids), "observed": len(triggers)})
    check("insufficient_overlap_class_exact", (insufficient["classification"] == "INSUFFICIENT_VARIANT_OVERLAP").all(), {"rows": len(insufficient)})
    check("eligible_numeric_finite", np.isfinite(eligible[["PP_H0", "PP_H1", "PP_H2", "PP_H3", "PP_H4", "H4_over_H3H4"]].to_numpy(float)).all(), {"rows": len(eligible)})
    posterior_sum = eligible[["PP_H0", "PP_H1", "PP_H2", "PP_H3", "PP_H4"]].sum(axis=1)
    check("posterior_sums_one", bool(np.allclose(posterior_sum, 1.0, atol=1e-10, rtol=0)), {"max_abs_error": float(np.max(np.abs(posterior_sum - 1)))})

    qtl_files = sorted(QTL_DIR.glob("*_PF10_QTL.tsv.gz"))
    qtl_ids = {path.name.removesuffix("_PF10_QTL.tsv.gz") for path in qtl_files}
    check("trigger_qtl_file_set_exact", qtl_ids == expected_trigger_ids, {"expected": len(expected_trigger_ids), "observed": len(qtl_ids)})
    qtl_bad: list[str] = []
    for path in qtl_files:
        comparison_id = path.name.removesuffix("_PF10_QTL.tsv.gz")
        frame = pd.read_csv(path, sep="\t")
        expected_n = int(triggers.set_index("comparison_id").loc[comparison_id, "n_variants"])
        required = {"variant_id", "slope_A1", "slope_se", "pval_nominal", "af_A1", "mode", "implementation"}
        if len(frame) != expected_n or frame["variant_id"].duplicated().any() or not required.issubset(frame.columns):
            qtl_bad.append(comparison_id)
    check("trigger_qtl_content_qc", not qtl_bad, qtl_bad[:20])

    anchors = {
        ("IL12RB2", "NK"): ("ROBUST_H4_TRIGGER", 0.998156, 3e-5),
        ("FCRL3", "B_IN"): ("ROBUST_H4_TRIGGER", 0.992898, 2e-4),
        ("FCRL3", "B_MEM"): ("ROBUST_H4_TRIGGER", 0.989944, 3e-4),
        ("FCRL3", "CD8_ET"): ("ROBUST_H4_TRIGGER", 0.941339, 3e-4),
    }
    anchor_results = []
    anchor_pass = True
    for (gene, cell), (expected_class, expected_h4, tolerance) in anchors.items():
        row = all_rows[(all_rows["gene"] == gene) & (all_rows["cell_type"] == cell)]
        passed = len(row) == 1 and str(row.iloc[0]["classification"]) == expected_class and abs(float(row.iloc[0]["PP_H4"]) - expected_h4) <= tolerance
        anchor_pass &= passed
        anchor_results.append({"gene": gene, "cell": cell, "observed_rows": len(row), "observed_class": None if row.empty else row.iloc[0]["classification"], "observed_H4": None if row.empty else float(row.iloc[0]["PP_H4"]), "pass": passed})
    check("historical_anchor_consistency", anchor_pass, anchor_results)
    inava_new = all_rows[(all_rows["gene"] == "INAVA") & (all_rows["cell_type"] == "CD4_NC")]
    check(
        "historical_weak_qtl_control_excluded_by_frozen_source_q_rule",
        inava_new.empty and "INAVA" not in set(frozen["gene"].astype(str)),
        {"R7B1_rows": len(inava_new), "reason": "no source q<0.05 in any frozen cell; historical R7A1B control remains archived"},
    )
    check("state_output_hashes", state["outputs"]["all_comparisons_sha256"] == sha256(ALL) and state["outputs"]["trigger_set_sha256"] == sha256(TRIGGER), state["outputs"])
    check("posterior_not_used_for_freeze", state.get("posterior_read_before_universe_freeze") is False, state.get("posterior_read_before_universe_freeze"))

    locus = (
        triggers.groupby("locus_index")
        .agg(trigger_comparisons=("comparison_id", "size"), trigger_genes=("gene", "nunique"), trigger_cells=("cell_type", "nunique"), robust_H4=("classification", lambda s: int((s == "ROBUST_H4_TRIGGER").sum())), H3_H4_ambiguity=("classification", lambda s: int((s == "H3_H4_AMBIGUITY_TRIGGER").sum())))
        .reset_index()
        .sort_values("locus_index")
    )
    locus.to_csv(OUT / "R7B1A_trigger_workload_by_locus.tsv", sep="\t", index=False)
    cell = (
        triggers.groupby("cell_type")
        .agg(trigger_comparisons=("comparison_id", "size"), trigger_loci=("locus_index", "nunique"), trigger_genes=("gene", "nunique"), robust_H4=("classification", lambda s: int((s == "ROBUST_H4_TRIGGER").sum())), H3_H4_ambiguity=("classification", lambda s: int((s == "H3_H4_AMBIGUITY_TRIGGER").sum())))
        .reset_index()
        .sort_values("cell_type")
    )
    cell.to_csv(OUT / "R7B1A_trigger_workload_by_cell.tsv", sep="\t", index=False)
    prior = triggers.groupby("classification").agg(
        comparisons=("comparison_id", "size"),
        skeptical_ratio_ge_0_5=("H4ratio_p12_1e_6", lambda s: int((s >= 0.5).sum())),
        source_cell_q_lt_0_05=("source_cell_q_lt_0_05", "sum"),
        median_qtl_min_p=("qtl_min_p", "median"),
    ).reset_index()
    prior.to_csv(OUT / "R7B1A_trigger_prior_and_sourceQ_summary.tsv", sep="\t", index=False)

    qa = pd.DataFrame(checks)
    qa.to_csv(OUT / "R7B1A_independent_QA.tsv", sep="\t", index=False)
    overall = bool(qa["pass"].all())
    summary = {
        "schema": "R7B1A_INDEPENDENT_QA_1.0",
        "status": "PASS" if overall else "FAIL",
        "checks_pass": int(qa["pass"].sum()),
        "checks_total": int(len(qa)),
        "frozen_comparisons": int(len(frozen)),
        "eligible_comparisons": int(len(eligible)),
        "insufficient_variant_overlap": int(len(insufficient)),
        "trigger_comparisons": int(len(triggers)),
        "trigger_loci": int(triggers["locus_index"].nunique()),
        "trigger_cell_locus_blocks": int(len(triggers[["cell_type", "locus_index"]].drop_duplicates())),
        "robust_H4": int((triggers["classification"] == "ROBUST_H4_TRIGGER").sum()),
        "H3_H4_ambiguity": int((triggers["classification"] == "H3_H4_AMBIGUITY_TRIGGER").sum()),
        "skeptical_prior_H4_ratio_ge_0_5": int((triggers["H4ratio_p12_1e_6"] >= 0.5).sum()),
        "interpretation": "screen triggers only; no multi-signal biological conclusion",
        "next": "R7B1B_exact_184_trigger_source_matched_multisignal",
    }
    (OUT / "R7B1A_independent_QA_state.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not overall:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
