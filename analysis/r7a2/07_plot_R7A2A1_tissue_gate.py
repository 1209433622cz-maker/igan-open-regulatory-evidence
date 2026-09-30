#!/usr/bin/env python3
"""Create a publication-ready donor plot for the R7A2A1 tissue gate."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else r"H:\SCI2\YR1")
    data_dir = root / "3_results/05_tissue/R7A2A1_control"
    fig_dir = root / "4_figures/R7A2A1"
    fig_dir.mkdir(parents=True, exist_ok=True)
    with (data_dir / "PBC_vs_control_target_panel.tsv").open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    stats = json.loads((data_dir / "PBC_vs_control_target_panel.json").read_text(encoding="utf-8-sig"))
    panels = [("FCRL3_B", "FCRL3 in B-lineage gate"), ("IL12RB2_NK", "IL12RB2 in NK-lineage gate")]
    groups = [("CONTROL_HEMANGIOMA_NONLESION", "Non-lesion control", "#4477AA"), ("PBC", "PBC", "#CC6677")]
    fig, axes = plt.subplots(1, 2, figsize=(8.3, 4.1), sharey=False)
    for ax, (target, title) in zip(axes, panels):
        for x, (group, label, color) in enumerate(groups):
            selected = sorted((r for r in rows if r["target_lineage"] == target and r["group"] == group), key=lambda r: r["run"])
            values = np.array([float(r["target_lineage_CPM"]) for r in selected])
            offsets = np.linspace(-0.08, 0.08, len(values))
            ax.scatter(np.full(len(values), x) + offsets, values, s=42, color=color, edgecolor="white", linewidth=0.7, zorder=3)
            median = float(np.median(values))
            q1, q3 = np.quantile(values, [0.25, 0.75])
            ax.plot([x - 0.18, x + 0.18], [median, median], color="black", linewidth=1.6, zorder=4)
            ax.plot([x, x], [q1, q3], color="black", linewidth=1.0, zorder=2)
        result = stats["comparisons"][target]
        ax.set_title(title, fontsize=10.5, fontweight="bold")
        ax.set_xticks([0, 1], ["Control", "PBC"])
        ax.set_yscale("log")
        ax.set_ylabel("Target-lineage CPM (log scale)")
        ax.grid(axis="y", color="#DDDDDD", linewidth=0.7)
        ax.set_axisbelow(True)
        direction = result["mean_log1p_CPM_difference_PBC_minus_control"]
        ax.text(0.03, 0.97, f"PBC − control (log1p): {direction:+.3f}\nExact P = {result['exact_label_permutation_p']:.4f}\nBH q = {result['BH_q_two_prespecified_targets']:.4f}",
                transform=ax.transAxes, ha="left", va="top", fontsize=8.4,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#BBBBBB", "alpha": 0.92})
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("PBC and matched non-lesion liver: prespecified lineage target panel", fontsize=12, fontweight="bold", y=1.01)
    fig.text(0.5, -0.01, "Points are donors (n=5 per group); bars show median and interquartile range. Marker-panel analysis; no target passed q<0.05.",
             ha="center", va="top", fontsize=8.2)
    fig.tight_layout()
    prefix = fig_dir / "R7A2A1_PBC_vs_control_target_panel"
    fig.savefig(prefix.with_suffix(".png"), dpi=320, bbox_inches="tight")
    fig.savefig(prefix.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(prefix.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    print(prefix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

