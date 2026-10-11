#!/usr/bin/env python3
"""Plot R6A2A1 benchmark and targeted ZMIZ1 replication results."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "3_results/04_integration/R6A2A"
FIG = ROOT / "0_admin/compatibility/figure_stage_view/R6A2A1"
FIG.mkdir(parents=True, exist_ok=True)

res = pd.read_csv(OUT / "R6A2A_coloc_smoke.tsv", sep="\t")
c = res[res.dataset == "combined"].copy()
c["label"] = c["locus"] + " | " + c["cell_type"] + " | " + c["gene"]
c["role_order"] = c.benchmark_role.map({"PUBLISHED_CELL_CLASS_PRIMARY": 0, "CROSS_CELL_SECONDARY": 1})
c = c.sort_values(["role_order", "locus", "gene", "cell_type"]).reset_index(drop=True)

tenk = pd.read_csv(OUT / "R6A2A1_TenK_ZMIZ1_precomputed_coloc.tsv", sep="\t")
onek_z = res[(res.locus == "ZMIZ1") & (res.gene == "ZMIZ1") & (res.cell_type == "NK")].copy()
zlabels = ["OneK combined", "OneK European", "OneK Asian", "TenK NK", "TenK NK CD56bright"]
h4 = [
    float(onek_z[onek_z.dataset == "combined"].PP_H4.iloc[0]),
    float(onek_z[onek_z.dataset == "european"].PP_H4.iloc[0]),
    float(onek_z[onek_z.dataset == "asian"].PP_H4.iloc[0]),
    float(tenk[tenk.celltype == "NK"]["PP.H4.abf"].iloc[0]),
    float(tenk[tenk.celltype == "NK_CD56bright"]["PP.H4.abf"].iloc[0]),
]
h3 = [
    float(onek_z[onek_z.dataset == "combined"].PP_H3.iloc[0]),
    float(onek_z[onek_z.dataset == "european"].PP_H3.iloc[0]),
    float(onek_z[onek_z.dataset == "asian"].PP_H3.iloc[0]),
    float(tenk[tenk.celltype == "NK"]["PP.H3.abf"].iloc[0]),
    float(tenk[tenk.celltype == "NK_CD56bright"]["PP.H3.abf"].iloc[0]),
]

plt.rcParams.update({"font.size": 9, "axes.titlesize": 11})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), gridspec_kw={"width_ratios": [1.45, 1]}, constrained_layout=True)

y = np.arange(len(c))
hw = 0.36
ax1.barh(y - hw / 2, c.PP_H3, height=hw, color="#d9a441", label="PP.H3")
ax1.barh(y + hw / 2, c.PP_H4, height=hw, color="#1976b8", label="PP.H4")
ax1.set_yticks(y, c.label)
ax1.invert_yaxis()
ax1.set_xlim(0, 1.04)
ax1.set_xlabel("Posterior probability")
ax1.set_title("A. Combined IgAN × OneK1K benchmark")
ax1.legend(loc="lower right", frameon=False)
for i, row in c.iterrows():
    marker = "primary" if row.benchmark_role == "PUBLISHED_CELL_CLASS_PRIMARY" else "secondary"
    ax1.text(1.015, i, marker, va="center", fontsize=8, color="#7b2cbf" if marker == "secondary" else "#455a64")
ax1.axvline(0.8, color="#8d99ae", lw=0.8, ls="--")

x = np.arange(len(zlabels))
w = 0.38
ax2.bar(x - w / 2, h3, width=w, color="#d9a441", label="PP.H3")
ax2.bar(x + w / 2, h4, width=w, color="#1976b8", label="PP.H4")
ax2.set_xticks(x, zlabels, rotation=28, ha="right")
ax2.set_ylim(0, 1.08)
ax2.set_ylabel("Posterior probability")
ax2.set_title("B. ZMIZ1/NK cross-resource support")
ax2.axhline(0.8, color="#8d99ae", lw=0.8, ls="--")
for xi, value in zip(x, h4):
    ax2.text(xi + w / 2, value + 0.025, f"{value:.3f}", ha="center", va="bottom", fontsize=8)
ax2.legend(frameon=False, loc="upper left")

fig.suptitle("R6A2A1 — IgAN positive-control signal gate", fontsize=15, fontweight="bold")
fig.savefig(FIG / "Figure_R6A2A1_benchmark_and_ZMIZ1_replication.png", dpi=240, bbox_inches="tight")
fig.savefig(FIG / "Figure_R6A2A1_benchmark_and_ZMIZ1_replication.pdf", bbox_inches="tight")
print(FIG / "Figure_R6A2A1_benchmark_and_ZMIZ1_replication.png")
