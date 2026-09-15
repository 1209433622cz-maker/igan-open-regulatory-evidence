#!/usr/bin/env python3
"""Build small, public-safe R7A1B evidence tables and a diagnostic figure."""
from pathlib import Path
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
BASE = ROOT / "3_results/04_integration/R7A1B"
FIGDIR = ROOT / "4_figures/R7A1B"
FIGDIR.mkdir(parents=True, exist_ok=True)

smoke = pd.read_csv(BASE / "R7A1B_coloc_smoke.tsv", sep="\t")
sig = pd.read_csv(BASE / "multisignal/R7A1B_signal_coloc_susie.tsv", sep="\t")
fits = pd.read_csv(BASE / "multisignal/R7A1B_susie_fit_summary.tsv", sep="\t")
genes = pd.read_csv(BASE / "R7A1B_gene_adjudication.tsv", sep="\t")

default = sig[np.isclose(pd.to_numeric(sig.p12), 1e-5)].copy()
best = (default.sort_values("PP.H4.abf", ascending=False)
        .drop_duplicates(["gene", "cell_type", "config"]))
low = sig[np.isclose(pd.to_numeric(sig.p12), 1e-6)][
    ["gene", "cell_type", "config", "hit1", "hit2", "H4_over_H3H4"]
].rename(columns={"H4_over_H3H4": "H4_ratio_p12_1e6"})
best = best.merge(low, on=["gene", "cell_type", "config", "hit1", "hit2"], how="left")
best["robust_pair"] = (
    (best["PP.H4.abf"] >= 0.8)
    & (best["H4_over_H3H4"] >= 0.8)
    & (best["H4_ratio_p12_1e6"] >= 0.5)
)
best.to_csv(BASE / "R7A1B_signal_best_by_cell_config.tsv", sep="\t", index=False)

stable = best.groupby(["gene", "cell_type"], as_index=False).agg(
    configurations=("config", "nunique"),
    min_default_PP_H4=("PP.H4.abf", "min"),
    min_default_H4_ratio=("H4_over_H3H4", "min"),
    min_low_prior_H4_ratio=("H4_ratio_p12_1e6", "min"),
    robust_all_configs=("robust_pair", "all"),
)
stable = stable.merge(
    fits.groupby(["gene", "cell_type"], as_index=False).agg(
        all_disease_converged=("disease_converged", "all"),
        all_qtl_converged=("qtl_converged", "all"),
        min_disease_CS=("disease_CS", "min"),
        min_qtl_CS=("qtl_CS", "min"),
        min_common_variants=("common_variants", "min"),
    ), on=["gene", "cell_type"], how="left"
)
stable.to_csv(BASE / "R7A1B_signal_stability_by_cell.tsv", sep="\t", index=False)

state = {
    "stage": "R7A1B1",
    "single_signal_smoke_tests": int(len(smoke)),
    "single_signal_robust": int((smoke.classification == "PASS_SINGLE_CAUSAL_SMOKE").sum()),
    "multisignal_trigger_combinations": int(smoke.force_multisignal.astype(bool).sum()
                                            + ((smoke.classification == "PASS_SINGLE_CAUSAL_SMOKE")
                                               & ~smoke.force_multisignal.astype(bool)).sum()),
    "multisignal_trigger_genes": sorted(sig.gene.unique().tolist()),
    "signal_specific_pass_genes": sorted(
        genes.loc[genes.status == "PASS_SIGNAL_SPECIFIC_SHARED_GENE", "gene"].tolist()
    ),
    "stable_cells": {
        row.gene: row.stable_pass_cells.split(";") if isinstance(row.stable_pass_cells, str) and row.stable_pass_cells else []
        for row in genes.itertuples(index=False)
    },
    "decision": "GO_R7A1C_TENK_REPLICATION_AND_PBC_LIVER_DETECTABILITY",
}
(BASE / "R7A1B_public_evidence_summary.json").write_text(
    json.dumps(state, indent=2, allow_nan=False), encoding="utf-8"
)

cfgs = ["PF10_L5", "PF10_L10", "PF10_L20", "PF50_L10"]
labels = [f"{g} / {c}" for g, c in best[["gene", "cell_type"]].drop_duplicates().itertuples(index=False)]
lookup = best.assign(label=best.gene + " / " + best.cell_type).pivot(index="label", columns="config", values="PP.H4.abf")
lookup = lookup.reindex(index=labels, columns=cfgs)

fig, axes = plt.subplots(1, 2, figsize=(14, 6.8), gridspec_kw={"width_ratios": [1.0, 1.35]})
order = smoke.assign(label=smoke.gene + " / " + smoke.cell_type).sort_values("PP_H4")
colors = order.gene.map({"IL12RB2": "#2B6CB0", "FCRL3": "#2F855A", "INAVA": "#718096"})
axes[0].barh(order.label, order.PP_H4, color=colors)
axes[0].axvline(0.8, color="#C53030", linestyle="--", linewidth=1)
axes[0].set_xlim(0, 1)
axes[0].set_xlabel("PP.H4 at p12 = 1e-5")
axes[0].set_title("Single-signal smoke gate")
axes[0].grid(axis="x", alpha=0.2)

im = axes[1].imshow(lookup.to_numpy(float), vmin=0, vmax=1, cmap="viridis", aspect="auto")
axes[1].set_xticks(range(len(cfgs)), cfgs, rotation=30, ha="right")
axes[1].set_yticks(range(len(labels)), labels)
axes[1].set_title("Best signal-pair PP.H4 after source-LD SuSiE")
for i in range(len(labels)):
    for j in range(len(cfgs)):
        val = lookup.iloc[i, j]
        if np.isfinite(val):
            axes[1].text(j, i, f"{val:.3f}", ha="center", va="center",
                         color="white" if val < 0.55 else "black", fontsize=8)
fig.colorbar(im, ax=axes[1], fraction=0.035, pad=0.03, label="PP.H4")
fig.suptitle("R7A1B PBC three-control signal gate", fontsize=15, fontweight="bold")
fig.text(0.5, 0.015,
         "Final gene gate: FCRL3 PASS; IL12RB2 PASS; INAVA uninformative in OneK1K. Next: TenK10K replication + liver detectability.",
         ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.04, 1, 0.95))
fig.savefig(FIGDIR / "R7A1B_PBC_signal_gate_summary.png", dpi=220, bbox_inches="tight")
plt.close(fig)
print(json.dumps(state, indent=2))
