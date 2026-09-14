#!/usr/bin/env python3
"""Freeze R6A2B0 targeted multi-signal results and next-stage decision."""

from pathlib import Path
import os
import json
import numpy as np
import pandas as pd

ROOT = Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
OUT = ROOT / "3_results/04_integration/R6A2B0/multisignal"


def main():
    summary = pd.read_csv(OUT / "R6A2B0_targeted_susie_summary.tsv", sep="\t")
    coloc_path = OUT / "R6A2B0_targeted_signal_coloc.tsv"
    coloc = pd.read_csv(coloc_path, sep="\t") if coloc_path.stat().st_size > 0 else pd.DataFrame()
    primary = summary[summary.config.eq("PF10_L10")].copy()
    rows = []
    for r in primary.itertuples(index=False):
        signals = coloc[(coloc.locus == r.locus) & (coloc.gene == r.gene) &
                        (coloc.cell_type == r.cell_type) & (coloc.config == "PF10_L10")] if len(coloc) else pd.DataFrame()
        robust = False
        best_h4 = best_ratio = np.nan
        if len(signals):
            default = signals[np.isclose(signals.p12, 1e-5)].copy()
            low = signals[np.isclose(signals.p12, 1e-6)][["component", "PP_H4", "H4_over_H3H4"]].rename(
                columns={"PP_H4": "low_H4", "H4_over_H3H4": "low_ratio"})
            x = default.merge(low, on="component", how="left")
            robust = bool(((x.PP_H4 >= 0.80) & (x.H4_over_H3H4 >= 0.80) & (x.low_ratio >= 0.50)).any())
            best_h4 = float(default.PP_H4.max())
            best_ratio = float(default.loc[default.PP_H4.idxmax(), "H4_over_H3H4"])
        sensitivity = summary[(summary.locus == r.locus) & (summary.gene == r.gene) &
                              (summary.cell_type == r.cell_type)]
        all_converged = bool(sensitivity.converged.all())
        any_cs = bool((sensitivity.credible_sets_95 > 0).any())
        if robust:
            status = "PASS_SIGNAL_SPECIFIC_SHARED_SIGNAL"
        elif r.credible_sets_95 == 0 and not any_cs:
            status = "FAIL_NO_STABLE_QTL_CREDIBLE_SIGNAL"
        elif r.credible_sets_95 == 0:
            status = "HOLD_SUSIE_SENSITIVITY_UNSTABLE"
        else:
            status = "FAIL_SIGNAL_SPECIFIC_COLOC"
        rows.append({
            "locus": r.locus, "gene": r.gene, "cell_type": r.cell_type,
            "status": status, "all_configs_converged": all_converged,
            "primary_credible_sets_95": int(r.credible_sets_95),
            "primary_max_PIP": float(r.max_PIP),
            "disease_lead_PIP": None if pd.isna(r.disease_lead_PIP) else float(r.disease_lead_PIP),
            "best_signal_PP_H4": None if pd.isna(best_h4) else best_h4,
            "best_signal_H4_ratio": None if pd.isna(best_ratio) else best_ratio,
        })
    adjud = pd.DataFrame(rows)
    adjud.to_csv(OUT / "R6A2B0_targeted_multisignal_adjudication.tsv", sep="\t", index=False)
    robust_loci = int(adjud[adjud.status.eq("PASS_SIGNAL_SPECIFIC_SHARED_SIGNAL")].locus.nunique())
    holds = int(adjud.status.str.startswith("HOLD").sum())
    if robust_loci >= 2:
        decision = "GO_TENK_REPLICATION_THEN_FULL24"
    elif robust_loci == 1:
        decision = "CONDITIONAL_GO_REPLICATE_THEN_ONE_MORE_BOUNDED_BLOCK"
    elif holds:
        decision = "HOLD_RESOLVE_SUSIE_INSTABILITY"
    else:
        decision = "HOLD_FULL24_REASSESS_DESIGN"
    state = {
        "trigger_combinations": len(adjud), "trigger_loci": int(adjud.locus.nunique()),
        "signal_specific_robust_loci": robust_loci, "unresolved_combinations": holds,
        "decision": decision, "results": adjud.to_dict("records"),
    }
    (OUT / "R6A2B0_targeted_multisignal_final.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
