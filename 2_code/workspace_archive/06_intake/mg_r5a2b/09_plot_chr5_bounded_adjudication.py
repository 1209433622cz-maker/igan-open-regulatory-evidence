#!/usr/bin/env python3
"""Create a four-panel figure for the frozen R5A2B chr5 adjudication."""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(r"H:\SCI2\YR1")
GWAS = ROOT / "3_results/01_gwas/R5A2B/GCST90432157_EOMG_chr5_GRCh37_fixed_1Mb.tsv.gz"
QTL = ROOT / "3_results/03_qtl/R5A2B/OneK1K_chr5_bounded_region_pairs.tsv.gz"
SMOKE = ROOT / "3_results/04_integration/R5A2B/chr5_coloc_abf_smoke.tsv"
OUT = ROOT / "0_admin/compatibility/figure_stage_view/R5A2B"
OUT.mkdir(parents=True, exist_ok=True)

g = pd.read_csv(GWAS, sep="\t")
g = g[g["inference_eligible"].eq(True)].copy()
g["mb"] = g["position_GRCh37"] / 1e6
g["mlogp"] = -np.log10(np.clip(g["p_value"], 1e-300, 1))
q = pd.read_csv(QTL, sep="\t")
q = q[(q["cell_type"].eq("NK")) & (q["phenotype_id"].eq("TNIP1"))].copy()
q["mb"] = q["position_GRCh37"] / 1e6
q["mlogp"] = -np.log10(np.clip(q["pval_nominal"], 1e-300, 1))
s = pd.read_csv(SMOKE, sep="\t")
e = s[s["trait"].eq("EOMG")].copy()

lead = "5:150447128"
top = "5:150477087"
blue, orange, red, grey = "#2878B5", "#E07B39", "#C43C39", "#B9C2C9"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(2, 2, figsize=(12, 8.2), constrained_layout=True)

ax = axes[0, 0]
ax.scatter(g["mb"], g["mlogp"], s=8, color=grey, alpha=.75, linewidths=0)
r = g[g["variant_id"].eq(lead)].iloc[0]
ax.scatter(r["mb"], r["mlogp"], s=52, color=blue, edgecolor="white", linewidth=.7, zorder=3)
ax.axhline(-np.log10(5e-8), color=red, linestyle="--", linewidth=1)
ax.set(title="A  EOMG disease association", xlabel="GRCh37 position (Mb)", ylabel=r"$-\log_{10}(P)$")
ax.text(.02, .96, "rs6861227 P = 1.053e-9", transform=ax.transAxes, va="top")

ax = axes[0, 1]
ax.scatter(q["mb"], q["mlogp"], s=8, color=grey, alpha=.75, linewidths=0)
for vid, color, label in [(top, orange, "source top"), (lead, blue, "disease lead")]:
    r = q[q["variant_id"].eq(vid)].iloc[0]
    ax.scatter(r["mb"], r["mlogp"], s=52, color=color, edgecolor="white", linewidth=.7, zorder=3, label=label)
ax.set(title="B  OneK1K NK / TNIP1 cis-eQTL", xlabel="GRCh37 position (Mb)", ylabel=r"$-\log_{10}(P)$")
ax.legend(frameon=False, fontsize=8)
ax.text(.02, .96, "top P = 1.70e-7; lead P = 0.00631", transform=ax.transAxes, va="top")

ax = axes[1, 0]
genes = sorted(e["phenotype_id"].unique())
palette = dict(zip(genes, plt.cm.tab10(np.linspace(0, .9, len(genes)))))
for gene, frame in e.groupby("phenotype_id"):
    ax.scatter(frame["PP_H3_p12_1e-5"], frame["PP_H4_p12_1e-5"], s=28, color=palette[gene], alpha=.8, label=gene)
ax.axhline(.8, color=red, linestyle="--", linewidth=1)
ax.axvline(.8, color="#777777", linestyle=":", linewidth=.8)
ax.set(title="C  EOMG default-prior evidence", xlabel="PP.H3 (distinct signals)", ylabel="PP.H4 (shared signal)", xlim=(-.02, 1.02), ylim=(-.02, .84))
ax.legend(frameon=False, fontsize=7, ncol=2, loc="upper left")

top6 = e.nlargest(6, "PP_H4_p12_1e-5").copy()
ax = axes[1, 1]
xs = np.array([1e-6, 1e-5, 1e-4])
for _, row in top6.iterrows():
    ys = [row["H4_p12_1e-6"], row["PP_H4_p12_1e-5"], row["H4_p12_1e-4"]]
    label = f"{row['cell_type']} / {row['phenotype_id']}"
    color = orange if row["phenotype_id"] == "TNIP1" else palette[row["phenotype_id"]]
    ax.plot(xs, ys, marker="o", linewidth=1.4, markersize=4, label=label, color=color, alpha=.9)
ax.axhline(.8, color=red, linestyle="--", linewidth=1)
ax.set_xscale("log")
ax.set_ylim(-.02, 1.02)
ax.set(title="D  EOMG H4 prior sensitivity", xlabel="p12", ylabel="PP.H4")
ax.legend(frameon=False, fontsize=7, loc="upper left")

fig.suptitle("R5A2B — chr5 bounded gene competition: no shared-signal trigger", fontsize=14, fontweight="bold")
fig.savefig(OUT / "Figure_R5A2B_chr5_bounded_adjudication.png", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "Figure_R5A2B_chr5_bounded_adjudication.pdf", bbox_inches="tight")
plt.close(fig)
print(OUT / "Figure_R5A2B_chr5_bounded_adjudication.png")
