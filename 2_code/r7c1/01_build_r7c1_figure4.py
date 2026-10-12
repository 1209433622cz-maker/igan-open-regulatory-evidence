#!/usr/bin/env python3
"""Build the source-bound R7C1 Figure 4 manuscript panel."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_manuscript/R7C1_IL12RB2_ExternalValidation_ManuscriptFork"
RESULTS = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011/results"
OUT = WORK / "figures"


def node(ax, x, y, text, color, width=0.27, height=0.17):
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        fc=color, ec="#263238", lw=1.2,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.2, color="#102027")


def edge(ax, start, end, label, color="#3b657a", dashed=False):
    arrow = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=12, lw=1.5,
        color=color, linestyle="--" if dashed else "-",
    )
    ax.add_patch(arrow)
    ax.text(
        (start[0] + end[0]) / 2,
        (start[1] + end[1]) / 2 + 0.035,
        label,
        ha="center", va="center", fontsize=7.4, color=color,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cs = pd.read_csv(RESULTS / "R7C0_FinnGen_R12_R13_IL12RB2_CS_members.tsv", sep="\t")
    coloc = pd.read_csv(RESULTS / "R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv", sep="\t")
    coverage = pd.read_csv(RESULTS / "R7C0_CASCADE_27gene_coverage.tsv", sep="\t")
    triangle = json.loads(
        (RESULTS / "R7C0_IL12RB2_chromatin_triangle_adjudication.json").read_text(encoding="utf-8")
    )

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    fig = plt.figure(figsize=(12.4, 9.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 2)

    ax = fig.add_subplot(gs[0, 0])
    ax.scatter(
        cs["cs_specific_prob_R12"], cs["cs_specific_prob_R13"],
        s=42, color="#2a788e", edgecolor="white", linewidth=0.5, alpha=0.9,
    )
    mx = max(cs["cs_specific_prob_R12"].max(), cs["cs_specific_prob_R13"].max()) * 1.08
    ax.plot([0, mx], [0, mx], color="#9aa0a6", lw=1, ls="--")
    lead = cs.loc[cs["cs_specific_prob_R13"].idxmax()]
    ax.annotate(
        "Shared release lead\n1:67336688:A:C",
        (lead["cs_specific_prob_R12"], lead["cs_specific_prob_R13"]),
        xytext=(8, -32), textcoords="offset points", fontsize=8,
        arrowprops=dict(arrowstyle="->", color="#455a64"),
    )
    ax.set(
        xlabel="FinnGen R12 disease-CS probability",
        ylabel="FinnGen R13 disease-CS probability",
        title="A  Disease credible-set stability",
    )
    ax.text(
        0.03, 0.96, "17/17 R13 variants in R12 CS\nJaccard = 0.895; r = 0.833",
        transform=ax.transAxes, va="top", fontsize=8.5,
        bbox=dict(boxstyle="round", fc="#eef6f7", ec="#9bbdc3"),
    )
    ax.spines[["top", "right"]].set_visible(False)

    ax = fig.add_subplot(gs[0, 1])
    vals = coloc.set_index("p12")["PP_H4"]
    ratios = coloc.set_index("p12")["H4_over_H3H4"]
    x = np.arange(3)
    ax.bar(x - 0.18, [vals.loc[1e-6], vals.loc[1e-5], vals.loc[1e-4]], 0.36,
           color="#3b8c6e", label="PP.H4")
    ax.bar(x + 0.18, [ratios.loc[1e-6], ratios.loc[1e-5], ratios.loc[1e-4]], 0.36,
           color="#76b7b2", label="H4/(H3+H4)")
    ax.axhline(0.8, color="#b24a4a", lw=1, ls="--")
    ax.set_xticks(x, ["$10^{-6}$", "$10^{-5}$", "$10^{-4}$"])
    ax.set_ylim(0, 1.06)
    ax.set(
        xlabel="Prior p12", ylabel="Posterior",
        title="B  Different disease study × OneK validation",
    )
    ax.text(
        0.03, 0.08,
        "FinnGen R13 × OneK NK/IL12RB2\n1,175 variants; source-CS overlap 2/2\nshared top: rs6702599",
        transform=ax.transAxes, fontsize=8.5,
        bbox=dict(boxstyle="round", fc="#eef6f0", ec="#8bb39a"),
    )
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)

    ax = fig.add_subplot(gs[1, 0])
    counts = [27, int((coverage["relevant_l1_eqtl_q_lt_0_05"] > 0).sum()), 1, 1]
    labels = ["Frozen genes", "Relevant-cell\neQTL coverage", "PBC–eQTL\ncoloc genes", "PP.H4 ≥ 0.8\ngenes"]
    colors = ["#90a4ae", "#5f9ea0", "#3b8c6e", "#2f6f58"]
    ax.bar(np.arange(4), counts, color=colors, width=0.68)
    for i, value in enumerate(counts):
        ax.text(i, value + 0.7, str(value), ha="center", fontsize=10, fontweight="bold")
    ax.set_xticks(np.arange(4), labels)
    ax.set_ylim(0, 31)
    ax.set_ylabel("Genes")
    ax.set_title("C  Prespecified 27-gene CASCADE coverage")
    ax.text(
        2.5, 8, "Only IL12RB2\npassed the disease-coloc layer", ha="center", fontsize=9,
        bbox=dict(boxstyle="round", fc="#eef6f0", ec="#8bb39a"),
    )
    ax.spines[["top", "right"]].set_visible(False)

    ax = fig.add_subplot(gs[1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    node(ax, 0.18, 0.76, "FinnGen PBC\ndisease signal", "#f1d6a8")
    node(ax, 0.76, 0.76, "IL12RB2 eQTL\nNK", "#b7dfd0")
    node(ax, 0.18, 0.25, "Linked peak caQTL\nNK", "#b9d7ea")
    node(ax, 0.76, 0.25, "IL12RB2\npeak–gene link", "#d8c8e8")
    edge(ax, (0.33, 0.76), (0.61, 0.76), f"PP.H4={triangle['disease_eQTL']['PP_H4_abf']:.3f}")
    edge(ax, (0.18, 0.66), (0.18, 0.36), f"PP.H4={triangle['disease_caQTL']['PP_H4_abf']:.3f}")
    edge(ax, (0.33, 0.25), (0.61, 0.25), f"link β={triangle['peak_gene_link']['link_beta']:.3f}")
    edge(
        ax, (0.69, 0.67), (0.31, 0.34),
        "direct eQTL–caQTL\nposterior unavailable", color="#9b5c5c", dashed=True,
    )
    ax.text(0.5, 0.96, "D  Source-integrated chromatin triangle", ha="center", fontsize=11)
    ax.text(
        0.5, 0.05, "OMIX001122: one PBC and one control matrix; descriptive only",
        ha="center", fontsize=8.5, color="#7a4040",
        bbox=dict(boxstyle="round", fc="#fbefef", ec="#c78e8e"),
    )

    fig.suptitle(
        "IL12RB2–NK gains external disease-study and chromatin signal support",
        fontsize=15, fontweight="bold",
    )
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"Figure4_IL12RB2_external_evidence.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    svg = OUT / "Figure4_IL12RB2_external_evidence.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
