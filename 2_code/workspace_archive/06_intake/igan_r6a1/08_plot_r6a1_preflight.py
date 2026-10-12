#!/usr/bin/env python3
"""Create the static R6A1 preflight overview figure."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap


ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "3_results" / "04_integration" / "R6A1"
FIG = ROOT / "0_admin/compatibility/figure_stage_view" / "R6A1"
FIG.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RESULT / "IgAN_24_locus_R6A2_entry_matrix.tsv", sep="\t")
order = {
    "A_BENCHMARK_POSITIVE_CONTROL": 0,
    "B_TRAIT_CONCORDANT_CROSS_RESOURCE": 1,
    "C_LANDSCAPE_TESTABLE": 2,
    "D_RESOURCE_ASYMMETRIC": 3,
}
df["_order"] = df["R6A2_entry_stratum"].map(order)
df = df.sort_values(["_order", "chromosome", "position_GRCh37"]).reset_index(drop=True)

features = [
    "OneK1K_testable",
    "TenK10K_testable",
    "cross_resource_candidate",
    "serum_IgA_nominal_concordant_signal",
    "published_DICE_control_cross_resource_recovered",
    "kidney_target_detectable",
]
labels = ["OneK1K", "TenK10K", "Cross-resource", "Serum IgA", "DICE control", "Kidney"]
matrix = df[features].astype(bool).astype(int).to_numpy()

plt.rcParams.update({"font.size": 9, "axes.titlesize": 11, "axes.labelsize": 9})
fig = plt.figure(figsize=(12.5, 9), constrained_layout=True)
grid = fig.add_gridspec(2, 2, width_ratios=[2.2, 1], height_ratios=[2.2, 1])

ax = fig.add_subplot(grid[:, 0])
ax.imshow(matrix, aspect="auto", interpolation="nearest", cmap=ListedColormap(["#eceff1", "#1677b8"]), vmin=0, vmax=1)
ax.set_xticks(range(len(labels)), labels, rotation=35, ha="right")
ax.set_yticks(range(len(df)), df["locus"])
ax.set_title("A. IgAN non-HLA locus evidence availability")
for y in range(len(df) + 1):
    ax.axhline(y - 0.5, color="white", lw=0.6)
for x in range(len(labels) + 1):
    ax.axvline(x - 0.5, color="white", lw=0.6)
for i, row in df.iterrows():
    if row["R6A2_entry_stratum"].startswith("A_"):
        ax.text(6.05, i, "benchmark", va="center", color="#b23a48", fontsize=8, clip_on=False)
    elif row["R6A2_entry_stratum"].startswith("B_"):
        ax.text(6.05, i, "trait-support", va="center", color="#7b2cbf", fontsize=8, clip_on=False)

ax2 = fig.add_subplot(grid[0, 1])
metrics = [24, 22, 24, 22, 9, 3]
names = ["Published\nloci", "OneK1K", "TenK10K", "Cross-\nresource", "Serum IgA", "Benchmark"]
colors = ["#455a64", "#1677b8", "#2a9d8f", "#7b2cbf", "#e76f51", "#b23a48"]
bars = ax2.bar(range(len(metrics)), metrics, color=colors)
ax2.set_xticks(range(len(metrics)), names, rotation=20, ha="right")
ax2.set_ylim(0, 27)
ax2.set_ylabel("Count")
ax2.set_title("B. Frozen R6A1 gate metrics")
ax2.spines[["top", "right"]].set_visible(False)
for bar, val in zip(bars, metrics):
    ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.5, str(val), ha="center", va="bottom", fontweight="bold")

ax3 = fig.add_subplot(grid[1, 1])
ax3.axis("off")
notes = (
    "R6A1 decision: GO to R6A2\n\n"
    "GSE127136: 145/146 cross-resource genes detected\n"
    "Published DICE controls recovered in both QTL resources:\n"
    "IRF4, DUSP22, ZMIZ1, ITGAX\n\n"
    "Boundary: availability and screening evidence only.\n"
    "New shared-signal claims require R6A2 colocalization."
)
ax3.text(0, 1, notes, va="top", ha="left", linespacing=1.45, bbox={"boxstyle": "round,pad=0.6", "fc": "#f7f9fb", "ec": "#9aa5ad"})

fig.suptitle("R6A1 — IgAN byte-level and positive-evidence preflight", fontsize=15, fontweight="bold")
fig.savefig(FIG / "Figure_R6A1_preflight_overview.png", dpi=240, bbox_inches="tight")
fig.savefig(FIG / "Figure_R6A1_preflight_overview.pdf", bbox_inches="tight")
print(FIG / "Figure_R6A1_preflight_overview.png")
