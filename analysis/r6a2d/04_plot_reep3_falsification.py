#!/usr/bin/env python3
"""Create a compact scientific summary of the REEP3 discovery and replication gate."""
from pathlib import Path
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
C = ROOT / "3_results/04_integration/R6A2C"
D = ROOT / "3_results/04_integration/R6A2D"
OUT = ROOT / "4_output/figures/R6A2C1D"
OUT.mkdir(parents=True, exist_ok=True)

coloc = pd.read_csv(C / "multisignal/R6A2C_signal_coloc.tsv", sep="\t")
coloc = coloc[(coloc.config == "PF10_L10") & np.isclose(coloc.p12, 1e-5)].copy()
rep = pd.read_csv(D / "R6A2D_TenK_REEP3_replication_summary.tsv", sep="\t")

fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.3), constrained_layout=True)
colors = {"asian": "#b2182b", "combined": "#2166ac", "european": "#67a9cf"}

x = np.arange(len(coloc))
axes[0].bar(x - 0.18, coloc.PP_H3, width=0.36, color="#8c8c8c", label="PP.H3")
axes[0].bar(x + 0.18, coloc.PP_H4, width=0.36, color=[colors[x] for x in coloc.dataset], label="PP.H4")
axes[0].axhline(0.8, color="#b2182b", linestyle="--", linewidth=1, alpha=0.8)
axes[0].set_xticks(x, [x.capitalize() for x in coloc.dataset])
axes[0].set_ylim(0, 1.05)
axes[0].set_ylabel("Posterior probability")
axes[0].set_title("OneK1K CD4_NC: signal-specific coloc")
axes[0].legend(frameon=False, ncol=2, loc="upper center")
axes[0].text(0.02, 0.03, "PF10/L10; p12=10⁻⁵\nAsian regional Pmin=4.55×10⁻⁶", transform=axes[0].transAxes, fontsize=8.5)

primary = rep[rep.cell_type.isin(["CD4_Naive", "CD4_TCM"])].copy()
x2 = np.arange(len(primary))
axes[1].bar(x2 - 0.18, primary.author_precomputed_IgAN_PP_H3, width=0.36, color="#8c8c8c", label="PP.H3")
axes[1].bar(x2 + 0.18, primary.author_precomputed_IgAN_PP_H4, width=0.36, color="#4d9221", label="PP.H4")
axes[1].set_xticks(x2, primary.cell_type.str.replace("_", " "))
axes[1].set_ylim(0, 1.05)
axes[1].set_ylabel("Posterior probability")
axes[1].set_title("TenK10K: author-precomputed IgAN coloc")
axes[1].legend(frameon=False, ncol=2, loc="upper center")
axes[1].text(0.02, 0.03, "OneK primary CS ∩ TenK source CS = 0\nH3 favors distinct disease/QTL signals", transform=axes[1].transAxes, fontsize=8.5)

for ax, label in zip(axes, ["A", "B"]):
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(-0.12, 1.04, label, transform=ax.transAxes, fontsize=14, fontweight="bold")

fig.suptitle("REEP3 ancestry-specific discovery signal fails independent molecular replication", fontsize=12.5, fontweight="bold")
for suffix in ["png", "pdf"]:
    fig.savefig(OUT / f"R6A2C1D_REEP3_falsification_summary.{suffix}", dpi=300 if suffix == "png" else None)
print(OUT / "R6A2C1D_REEP3_falsification_summary.png")
