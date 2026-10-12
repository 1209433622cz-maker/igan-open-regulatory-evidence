#!/usr/bin/env python3
"""Create a figure-ready R7B1D external-evidence overview."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap


ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "3_results/04_integration/R7B1D"
FIG = ROOT / "5_analysis/figures/R7B1D"


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    coloc = pd.read_csv(RES / "R7B1D_FinnGen_PBC_molQTL_coloc.tsv", sep="\t")
    direction = pd.read_csv(RES / "R7B1D_risk_allele_expression_direction.tsv", sep="\t")

    rows = ["IL12RB2–NK", "FCRL3–B", "FCRL3–CD8_ET"]
    cols = ["OneK\nmulti-signal", "TenK\nmolecular", "FinnGen\nPBC–eQTL", "FinnGen\nchromatin", "Allele\ndirection"]
    # 0 absent/unavailable, 1 bounded/partial, 2 supported, 3 falsification/negative control.
    matrix = np.array([
        [2, 2, 2, 1, 2],
        [2, 2, 0, 0, 2],
        [3, 0, 0, 0, 3],
    ])
    labels = np.array([
        ["stable H4", "H4 smoke", "3 records", "positional", "higher"],
        ["stable H4", "H4 smoke", "not returned", "none", "lower"],
        ["H4→H3", "not tested", "not returned", "none", "not shared"],
    ])
    cmap = ListedColormap(["#E5E7EB", "#F4B942", "#2A9D8F", "#B65C70"])

    fig = plt.figure(figsize=(12.2, 7.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1])
    ax = fig.add_subplot(gs[:, 0])
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=3, aspect="auto")
    ax.set_xticks(range(len(cols)), cols, fontsize=9)
    ax.set_yticks(range(len(rows)), rows, fontsize=10)
    ax.tick_params(length=0)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, labels[i, j], ha="center", va="center", fontsize=8,
                    color="white" if matrix[i, j] in (2, 3) else "#1F2937")
    ax.set_title("A  Bounded external evidence matrix", loc="left", fontweight="bold", fontsize=12)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax2 = fig.add_subplot(gs[0, 1])
    il = coloc[coloc.trait2_symbol == "IL12RB2"].sort_values("cell_type2")
    ax2.barh(il.cell_type2, il["PP.H4.abf"], color="#2A9D8F")
    ax2.axvline(0.8, color="#6B7280", linestyle="--", linewidth=1)
    ax2.set_xlim(0, 1.02)
    ax2.set_xlabel("FinnGen R12 PP.H4.abf")
    ax2.set_title("B  Public PBC–IL12RB2 coloc", loc="left", fontweight="bold", fontsize=12)
    for y, (_, r) in enumerate(il.iterrows()):
        ax2.text(r["PP.H4.abf"] - 0.01, y, f"CS overlap {int(r.cs_overlap)}", ha="right", va="center", color="white", fontsize=8)
    ax2.spines[["top", "right"]].set_visible(False)

    ax3 = fig.add_subplot(gs[1, 1])
    use = direction[direction.eligible_for_shared_signal_direction.astype(bool)].copy()
    use["group"] = use.axis.str.replace("–B_IN", "–B", regex=False).str.replace("–B_MEM", "–B", regex=False)
    palette = {"OneK1K_PF10": "#264653", "TenK10K": "#E76F51", "FinnGen_R12_multiome": "#2A9D8F"}
    ymap = {"IL12RB2–NK": 1, "FCRL3–B": 0}
    offsets = {"OneK1K_PF10": -0.10, "TenK10K": 0.0, "FinnGen_R12_multiome": 0.10}
    for resource, sub in use.groupby("resource"):
        x = np.sign(sub.risk_allele_expression_beta.astype(float))
        y = [ymap[g] + offsets[resource] for g in sub.group]
        ax3.scatter(x, y, label=resource.replace("_PF10", "").replace("_R12_multiome", ""),
                    color=palette[resource], s=45, alpha=0.85)
    ax3.axvline(0, color="#6B7280", linewidth=1)
    ax3.set_xlim(-1.35, 1.35)
    ax3.set_xticks([-1, 1], ["Risk allele → lower expression", "Risk allele → higher expression"])
    ax3.set_yticks([0, 1], ["FCRL3–B", "IL12RB2–NK"])
    ax3.set_title("C  Exact-allele direction", loc="left", fontweight="bold", fontsize=12)
    ax3.legend(frameon=False, fontsize=8, loc="lower right")
    ax3.spines[["top", "right"]].set_visible(False)

    fig.suptitle("R7B1D external molecular/multiome evidence and claim boundaries", fontsize=14, fontweight="bold")
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(FIG / f"R7B1D_external_evidence_overview.{ext}", dpi=300 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
