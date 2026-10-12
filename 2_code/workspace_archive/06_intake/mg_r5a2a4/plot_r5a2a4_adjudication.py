#!/usr/bin/env python3
"""Create the frozen R5A2A4 NK_R/ZCCHC2 adjudication figure."""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "3_results" / "04_integration" / "R5A2A4"
LD_DIR = RESULT / "NK_R_ZCCHC2_sourceLD"
MS_DIR = RESULT / "NK_R_ZCCHC2_multisignal"
OUT = ROOT / "0_admin/compatibility/figure_stage_view" / "R5A2A4"
OUT.mkdir(parents=True, exist_ok=True)

TOP = "18:60243208"
LEAD = "18:60005046"  # rs7239261 in the OneK1K GRCh37 variant namespace

v = pd.read_csv(LD_DIR / "NK_R_ZCCHC2_LD_variants.tsv", sep="\t")
v = v.sort_values("LD_order_zero_based").reset_index(drop=True)
v["mb"] = v["position_GRCh37"] / 1e6
v["minus_log10_p"] = -np.log10(np.clip(v["QTL_pval_nominal"], 1e-300, 1.0))

pf10 = np.load(LD_DIR / "NK_R_ZCCHC2_PF10_residualized_A1_correlation.npy", mmap_mode="r")
top_i = int(v.index[v["variant_id"].eq(TOP)][0])
lead_i = int(v.index[v["variant_id"].eq(LEAD)][0])
v["r2_top_pf10"] = np.asarray(pf10[top_i, :], dtype=float) ** 2
v["r2_lead_pf10"] = np.asarray(pf10[lead_i, :], dtype=float) ** 2

cond = pd.read_csv(MS_DIR / "NK_R_ZCCHC2_forced_conditioned_top25.tsv", sep="\t")
cond = cond[cond["LD_mode"].eq("PF10")].copy()
cond["mb"] = cond["position_GRCh37"] / 1e6
cond["minus_log10_conditional_p"] = -np.log10(np.clip(cond["conditional_p"], 1e-300, 1.0))

pip = pd.read_csv(MS_DIR / "NK_R_ZCCHC2_susie_PIP.tsv.gz", sep="\t")
pip = pip[pip["config"].eq("PF10_L10_primary")].copy()
pip["mb"] = pip["position_GRCh37"] / 1e6

thr = -np.log10(0.05 / len(v))
blue = "#2878B5"
orange = "#E07B39"
red = "#C43C39"
grey = "#B9C2C9"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})
fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.2), constrained_layout=True)

ax = axes[0, 0]
ax.scatter(v["mb"], v["minus_log10_p"], s=7, c=grey, alpha=0.75, linewidths=0)
ax.axhline(thr, color=red, linestyle="--", linewidth=1, label="within-window Bonferroni")
for variant, color, label in [(TOP, orange, "source top eQTL"), (LEAD, blue, "rs7239261")]:
    row = v.loc[v["variant_id"].eq(variant)].iloc[0]
    ax.scatter(row["mb"], row["minus_log10_p"], s=46, c=color, edgecolor="white", linewidth=0.7, zorder=4, label=label)
ax.set_title("A  Marginal NK_R / ZCCHC2 cis-eQTL")
ax.set_ylabel(r"$-\log_{10}(P)$")
ax.set_xlabel("GRCh37 position (Mb)")
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.text(0.02, 0.97, "source permutation q = 0.383\n0 variants pass local threshold", transform=ax.transAxes, va="top", fontsize=8)

ax = axes[0, 1]
ax.scatter(v["mb"], v["r2_top_pf10"], s=7, c=orange, alpha=0.50, linewidths=0, label="LD with 18:60243208")
ax.scatter(v["mb"], v["r2_lead_pf10"], s=7, c=blue, alpha=0.42, linewidths=0, label="LD with rs7239261")
ax.axhline(0.8, color="#555555", linestyle="--", linewidth=0.8)
ax.set_ylim(-0.03, 1.05)
ax.set_title("B  Source LD after PF10 covariate residualization")
ax.set_ylabel(r"$r^2$")
ax.set_xlabel("GRCh37 position (Mb)")
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.text(0.02, 0.97, r"lead–top $r^2$ = 0.0124", transform=ax.transAxes, va="top", fontsize=8)

ax = axes[1, 0]
ax.scatter(cond["mb"], cond["minus_log10_conditional_p"], s=22, c=blue, alpha=0.78, linewidths=0)
ax.axhline(thr, color=red, linestyle="--", linewidth=1)
lead_cond = cond.loc[cond["variant_id"].eq(LEAD)]
if not lead_cond.empty:
    ax.scatter(lead_cond["mb"], lead_cond["minus_log10_conditional_p"], s=50, c=blue, edgecolor="white", linewidth=0.7, zorder=4)
ax.set_title("C  Forced conditioning on the source top eQTL")
ax.set_ylabel(r"$-\log_{10}(P_{conditional})$")
ax.set_xlabel("GRCh37 position (Mb)")
ax.text(0.02, 0.97, "rs7239261 conditional P = 0.0177\n0 residual variants pass local threshold", transform=ax.transAxes, va="top", fontsize=8)

ax = axes[1, 1]
ax.scatter(pip["mb"], pip["PIP"], s=8, c=grey, alpha=0.75, linewidths=0)
for variant, color in [(TOP, orange), (LEAD, blue)]:
    row = pip.loc[pip["variant_id"].eq(variant)].iloc[0]
    ax.scatter(row["mb"], row["PIP"], s=48, c=color, edgecolor="white", linewidth=0.7, zorder=4)
ax.set_ylim(0, max(0.04, pip["PIP"].max() * 1.25))
ax.set_title("D  SuSiE-RSS PIP (PF10, L=10)")
ax.set_ylabel("Posterior inclusion probability")
ax.set_xlabel("GRCh37 position (Mb)")
ax.text(0.02, 0.97, "max PIP = 0.0296; rs7239261 = 0.00665\n95% credible sets = 0", transform=ax.transAxes, va="top", fontsize=8)

fig.suptitle("R5A2A4 — NK_R / ZCCHC2 source-LD and multi-signal adjudication", fontsize=14, fontweight="bold")
fig.savefig(OUT / "Figure_R5A2A4_NK_R_ZCCHC2_adjudication.png", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "Figure_R5A2A4_NK_R_ZCCHC2_adjudication.pdf", bbox_inches="tight")
plt.close(fig)

print(OUT / "Figure_R5A2A4_NK_R_ZCCHC2_adjudication.png")
