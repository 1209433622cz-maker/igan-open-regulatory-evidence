#!/usr/bin/env python3
"""Create the frozen R6A2B0 decision figure from small result tables."""

from pathlib import Path
import os
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
INTEGRATION = ROOT / "3_results/04_integration/R6A2B0"
OUT = ROOT / "4_figures/R6A2B0"
OUT.mkdir(parents=True, exist_ok=True)

loci = pd.read_csv(INTEGRATION / "R6A2B0_locus_adjudication.tsv", sep="\t").sort_values("best_PP_H4")
smoke = pd.read_csv(INTEGRATION / "R6A2B0_coloc_smoke_549max.tsv", sep="\t")
reep = smoke[(smoke.locus == "REEP3") & (smoke.gene == "REEP3") & (smoke.cell_type == "CD4_NC")]
reep = reep.set_index("dataset").loc[["combined", "european", "asian"]].reset_index()

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.6), constrained_layout=True)

colors = loci.status.map({
    "HOLD_TARGETED_LD": "#d89000",
    "DISTINCT_SIGNAL_PRESENT": "#5875a4",
    "UNINFORMATIVE": "#a6a6a6",
}).fillna("#a6a6a6")
axes[0].barh(loci.locus, loci.best_PP_H4, color=colors)
axes[0].axvline(0.8, color="#a61b1b", linestyle="--", linewidth=1)
axes[0].set_xlim(0, 1)
axes[0].set_xlabel("Best combined IgAN PP.H4")
axes[0].set_title("A  Primary 8-locus smoke gate")
for y, v in enumerate(loci.best_PP_H4):
    axes[0].text(v + 0.015, y, f"{v:.3f}", va="center", fontsize=8)

axes[1].bar(reep.dataset, reep.PP_H4, color=["#586f7c", "#8aa1b1", "#b83b5e"])
axes[1].axhline(0.8, color="#a61b1b", linestyle="--", linewidth=1)
axes[1].set_ylim(0, 1)
axes[1].set_ylabel("PP.H4")
axes[1].set_title("B  REEP3 × CD4_NC ancestry check")
for x, r in reep.iterrows():
    axes[1].text(x, r.PP_H4 + 0.025, f"{r.PP_H4:.3f}\nPmin={r.gwas_min_p:.1e}", ha="center", fontsize=8)

fig.suptitle("R6A2B0: no additional combined-IgAN robust locus; Asian REEP3 remains bounded follow-up", fontsize=11)
fig.savefig(OUT / "R6A2B0_decision_summary.png", dpi=240, bbox_inches="tight")
fig.savefig(OUT / "R6A2B0_decision_summary.svg", bbox_inches="tight")
print(OUT / "R6A2B0_decision_summary.png")


if __name__ == "__main__":
    pass
