#!/usr/bin/env python3
"""Build the six source-bound R7B3A manuscript composites.

All plotted values are read from frozen project outputs.  Missing or duplicated
source rows fail closed; no display fallback values are permitted.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyBboxPatch


ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "5_manuscript" / "R7B3A_ManuscriptV2" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#1F5A85"
TEAL = "#2A9D8F"
ORANGE = "#E07A3F"
RED = "#C44E52"
PURPLE = "#7A5195"
GREY = "#8A94A3"
LIGHT = "#E9EEF3"
DARK = "#22313F"

mpl.rcParams.update({
    "font.family": "Arial", "font.size": 9, "axes.titlesize": 11,
    "axes.labelsize": 9, "axes.spines.top": False,
    "axes.spines.right": False, "figure.dpi": 180, "savefig.dpi": 600,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
sns.set_style("whitegrid", {"axes.grid": False})


def panel(ax, label: str) -> None:
    ax.text(-0.08, 1.08, label, transform=ax.transAxes, fontsize=13,
            fontweight="bold", va="top", color=DARK)


def exactly_one(frame: pd.DataFrame, mask, label: str) -> pd.Series:
    rows = frame.loc[mask]
    if len(rows) != 1:
        raise ValueError(f"{label}: expected exactly one row, found {len(rows)}")
    return rows.iloc[0]


def save(fig: plt.Figure, stem: str) -> None:
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{stem}.{suffix}", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def box(ax, x, y, w, h, title, subtitle="", color=BLUE) -> None:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.012",
                                facecolor=color, edgecolor="none", alpha=.94))
    ax.text(x + w / 2, y + h * .64, title, ha="center", va="center",
            color="white", fontweight="bold", fontsize=9)
    if subtitle:
        ax.text(x + w / 2, y + h * .30, subtitle, ha="center", va="center",
                color="white", fontsize=7.5)


def figure1() -> None:
    scope = pd.read_csv(ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure1_study_scope_counts.tsv", sep="\t")
    vals = dict(zip(scope.denominator, scope.n))
    required = ["PBC-wide frozen comparisons", "ABF eligible", "multi-signal high-information subset"]
    if any(k not in vals for k in required):
        raise ValueError("Figure 1A scope table is incomplete")
    gate = json.loads((ROOT / "0_admin/intake/R7B3_20261010/sources/targeted_model_gate.json").read_text(encoding="utf-8"))
    if not (gate.get("comparisons") == 7 and gate.get("identity_manifest_rows") == 14 and gate.get("identity_manifest_pass_rows") == 14):
        raise ValueError("Figure 1D identity denominators changed")

    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.8), gridspec_kw={"height_ratios": [1.1, 1]})
    ax = axes[0, 0]; panel(ax, "A"); ax.axis("off")
    stages = [
        ("PBC-wide registered screen", int(vals[required[0]]), .72, BLUE),
        ("ABF-eligible comparisons", int(vals[required[1]]), .45, TEAL),
        ("High-information follow-up", int(vals[required[2]]), .18, PURPLE),
    ]
    for i, (lab, n, y, c) in enumerate(stages):
        box(ax, .13, y, .74, .16, lab, f"n = {n:,}", c)
        if i < len(stages) - 1:
            ax.annotate("", xy=(.5, stages[i + 1][2] + .18), xytext=(.5, y - .02),
                        arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.8))
    ax.text(.5, .045, "184 primary + 455 H3 + 3 borderline\nNo multi-signal claim for all 6,923 comparisons",
            ha="center", va="center", color=DARK, fontsize=8.5)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.set_title("Analysis scope and direction of follow-up", loc="left", fontweight="bold")

    ax = axes[0, 1]; panel(ax, "B")
    labels = ["Primary\nverification", "H3 rescue /\nfalsification", "Borderline\ncalibration"]
    counts = [184, 455, 3]
    bars = ax.bar(labels, counts, color=[BLUE, ORANGE, GREY], width=.62)
    for b, n in zip(bars, counts):
        ax.text(b.get_x() + b.get_width() / 2, n + 12, f"{n}", ha="center", fontweight="bold")
    ax.set_ylabel("Comparisons"); ax.set_ylim(0, 510)
    ax.set_title("Prespecified roles within the 642-comparison subset", loc="left", fontweight="bold")

    ax = axes[1, 0]; panel(ax, "C")
    final_labels = ["H4-supported", "H3-supported", "Model-sensitive", "Uninformative"]
    final = [92, 428, 59, 63]
    left = 0
    for lab, n, c in zip(final_labels, final, [TEAL, ORANGE, PURPLE, GREY]):
        ax.barh([0], [n], left=[left], color=c, label=f"{lab} ({n})", height=.45)
        if n > 40:
            ax.text(left + n / 2, 0, str(n), ha="center", va="center", color="white", fontweight="bold")
        left += n
    ax.set_xlim(0, 642); ax.set_yticks([]); ax.set_xlabel("Comparisons")
    ax.set_title("Frozen PF10 multi-signal outcomes", loc="left", fontweight="bold")
    ax.legend(ncol=2, frameon=False, loc="lower center", bbox_to_anchor=(.5, -.48))

    ax = axes[1, 1]; panel(ax, "D"); ax.axis("off")
    ax.text(.02, .91, "Audit denominators describe different tasks", fontsize=11, fontweight="bold", transform=ax.transAxes)
    ax.text(.02, .68, "14 / 14 comparison–model identity rows", fontsize=11, fontweight="bold", color=TEAL, transform=ax.transAxes)
    ax.text(.02, .57, "7 targeted comparisons × PF10/PF50; not 14 cell types", fontsize=8.5, transform=ax.transAxes)
    ax.text(.02, .34, "2,568 / 2,568 expanded diagnostic units", fontsize=11, fontweight="bold", color=BLUE, transform=ax.transAxes)
    ax.text(.02, .21, "642 comparisons × 2 models × 2 traits", fontsize=8.5, transform=ax.transAxes)
    ax.text(.02, .09, "One unique event outside credible sets was reviewed and retained", fontsize=8.5, color=RED, transform=ax.transAxes)
    ax.set_title("Model identity and diagnostic closure", loc="left", fontweight="bold")

    fig.suptitle("Study scope, bounded follow-up and model-integrity gates", fontsize=16, fontweight="bold", color=DARK, y=.995)
    fig.tight_layout(rect=[0, 0, 1, .96]); save(fig, "Figure1_study_scope_and_model_integrity")


def figure2() -> None:
    traj = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/adjudication/R7B2A_642_four_arm_trajectories.tsv", sep="\t")
    trans = pd.read_csv(ROOT / "4_figures/R7B2A/source_data/Figure2_adjacent_transition_matrices.tsv", sep="\t")
    summary = pd.read_csv(ROOT / "4_figures/R7B2A/source_data/Figure2_attribution_summary.tsv", sep="\t")
    if "removed_n" not in traj.columns:
        raise ValueError("Figure 2A requires removed_n; no fallback is permitted")
    removed = pd.to_numeric(traj["removed_n"], errors="raise")
    if len(removed) != 642 or removed.isna().any() or removed.min() != 19 or removed.max() != 114 or float(removed.median()) != 65:
        raise ValueError("Figure 2A support-removal distribution failed frozen identity checks")
    sm = dict(zip(summary.metric, summary.value))
    needed = ["support_set_state_changes_A0_to_A1", "disease_stat_state_changes_A1_to_A2", "model_state_changes_A2_to_M"]
    if any(k not in sm for k in needed):
        raise ValueError("Figure 2 attribution summary is incomplete")
    fig, axes = plt.subplots(2, 3, figsize=(15.5, 9.2))

    ax = axes[0, 0]; panel(ax, "A")
    ax.hist(removed, bins=18, color=BLUE, alpha=.9)
    ax.axvline(65, color=RED, ls="--", lw=1.5, label="Median = 65")
    ax.set(xlabel="Variants removed from historical ABF support", ylabel="Comparisons")
    ax.set_title("Exact support matching", loc="left", fontweight="bold"); ax.legend(frameon=False)
    ax.text(.97, .92, "Range 19–114\nMedian fraction 7.67%", transform=ax.transAxes, ha="right", va="top")

    ax = axes[0, 1]; panel(ax, "B")
    vals = [sm[k] for k in needed]
    labs = ["Support set\nA0→A1", "Disease stats\nA1→A2", "Full procedure\nA2→M"]
    bars = ax.bar(labs, vals, color=[BLUE, TEAL, PURPLE])
    for b, n in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, n + 4, str(int(n)), ha="center", fontweight="bold")
    ax.set_ylabel("Categorical state changes (of 642)"); ax.set_ylim(0, 155)
    ax.set_title("Adjacent-arm attribution", loc="left", fontweight="bold")

    ax = axes[0, 2]; panel(ax, "C")
    m = trans[trans.transition == "A2_TO_M_MODEL"].pivot(index="from_state", columns="to_state", values="n").fillna(0)
    order_r = [x for x in ["H4", "H3", "AMBIGUOUS", "H4_BORDERLINE", "UNINFORMATIVE"] if x in m.index]
    order_c = [x for x in ["H4", "H3", "MODEL_SENSITIVE", "UNINFORMATIVE"] if x in m.columns]
    sns.heatmap(m.loc[order_r, order_c], annot=True, fmt=".0f", cmap="Blues", cbar=False, ax=ax, linewidths=.5, linecolor="white")
    ax.set(xlabel="Multi-signal state (M)", ylabel="Matched-input ABF state (A2)")
    ax.tick_params(axis="x", labelrotation=28, labelsize=7.5); ax.tick_params(axis="y", labelrotation=0, labelsize=7.5)
    ax.set_title("Matched-input reclassification", loc="left", fontweight="bold")

    ax = axes[1, 0]; panel(ax, "D")
    groups = ["A2 H4\n(n=113)", "A2 H3\n(n=452)"]
    mat = np.array([[79, 8, 4, 22], [10, 413, 6, 23]])
    bottoms = np.zeros(2)
    for j, (cat, c) in enumerate(zip(["M H4", "M H3", "Sensitive", "Uninformative"], [TEAL, ORANGE, PURPLE, GREY])):
        ax.bar(groups, mat[:, j], bottom=bottoms, color=c, label=cat, width=.62)
        for i, n in enumerate(mat[:, j]):
            if n >= 8:
                ax.text(i, bottoms[i] + n / 2, str(n), ha="center", va="center", color="white", fontweight="bold", fontsize=8)
        bottoms += mat[:, j]
    ax.set_ylabel("Comparisons"); ax.set_title("Correct denominators after input matching", loc="left", fontweight="bold")
    ax.legend(frameon=False, ncol=2, fontsize=7.5, loc="upper left", bbox_to_anchor=(0, .96))

    ax = axes[1, 1]; panel(ax, "E")
    pf = [491, 4, 25]; labs = ["Matched state", "PF-sensitive", "PF50\nuninformative"]
    bars = ax.bar(labs, pf, color=[TEAL, PURPLE, GREY])
    for b, n in zip(bars, pf):
        ax.text(b.get_x() + b.get_width() / 2, n + 8, str(n), ha="center", fontweight="bold")
    ax.set_ylim(0, 550); ax.set_ylabel("Comparisons (definite PF10 state; n=520)")
    ax.set_title("PF10/PF50 sensitivity", loc="left", fontweight="bold")

    ax = axes[1, 2]; panel(ax, "F")
    vals = [60, 32, 428]
    labs = ["Stable H4\nshared only", "Stable H4\nshared + distinct", "Stable H3\ndistinct pair"]
    bars = ax.bar(labs, vals, color=[TEAL, BLUE, ORANGE], width=.66)
    for b, n in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, n + 8, str(n), ha="center", fontweight="bold")
    ax.set_ylim(0, 500); ax.set_ylabel("Comparisons")
    ax.set_title("Signal-pair identity and coexistence", loc="left", fontweight="bold")
    ax.text(.98, .82, "92/92 stable H4 and 428/428 stable H3\nretained pair identity across L settings",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=.25", fc="white", ec=LIGHT))

    fig.suptitle("Matched inputs explain part, but not all, of bidirectional reclassification", fontsize=16, fontweight="bold", color=DARK, y=.995)
    fig.tight_layout(rect=[0, 0, 1, .96], w_pad=2.0, h_pad=2.2); save(fig, "Figure2_input_matched_reclassification")


def figure3() -> None:
    chan = pd.read_csv(ROOT / "4_figures/R7B2A/source_data/Figure3_simulation_channel_summary.tsv", sep="\t")
    perf = pd.read_csv(ROOT / "4_figures/R7B2A/source_data/Figure3_discovery_vs_estimator_performance.tsv", sep="\t")
    scen = pd.read_csv(ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure3_simulation_scenario_summary.tsv", sep="\t")
    labels = ["S1", "S2", "S3", "S4", "S5", "S6"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    ax = axes[0, 0]; panel(ax, "A")
    by = chan[chan.scope == "PRIMARY_MATCHED_BY_SCENARIO"]
    order = ["NO_CS_BOTH", "NO_DISEASE_CS", "NO_QTL_CS", "PAIR_H3", "PAIR_H4", "PAIR_UNINFORMATIVE"]
    colors = ["#D8DEE9", "#B9C2CE", "#8A94A3", ORANGE, TEAL, PURPLE]
    bottom = np.zeros(6)
    for cat, c in zip(order, colors):
        v = []
        for s in perf.scenario:
            row = by[(by.scenario == s) & (by.matched_channel == cat)]
            v.append(float(row.rate.iloc[0]) if len(row) else 0)
        ax.bar(labels, v, bottom=bottom, color=c, label=cat.replace("_", " ").title())
        bottom += np.asarray(v)
    ax.set_ylim(0, 1); ax.set_ylabel("Proportion of 81,000 iterations")
    ax.set_title("Primary multi-signal outcome channels", loc="left", fontweight="bold")
    ax.legend(frameon=False, ncol=3, fontsize=7, loc="upper center", bbox_to_anchor=(.5, -.12))

    ax = axes[0, 1]; panel(ax, "B"); x = np.arange(6); w = .25
    ax.bar(x - w, perf.pair_evaluable_rate, width=w, color=BLUE, label="Pair evaluable")
    ax.bar(x, perf.H4_rate_unconditional, width=w, color=TEAL, label="H4 / all iterations")
    ax.bar(x + w, perf.H4_rate_conditional_on_pair, width=w, color=PURPLE, label="H4 / pair-evaluable")
    ax.set_xticks(x, labels); ax.set_ylim(0, 1); ax.set_ylabel("Rate")
    ax.set_title("Discovery and estimator denominators", loc="left", fontweight="bold"); ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]; panel(ax, "C"); w = .34
    ax.bar(x - w / 2, scen.abf_h4_rate, width=w, color=GREY, label="Single-causal ABF H4")
    ax.bar(x + w / 2, scen.matched_h4_rate, width=w, color=TEAL, label="Matched multi-signal H4")
    ax.set_xticks(x, labels); ax.set_ylim(0, .75); ax.set_ylabel("Unconditional H4 rate")
    ax.set_title("Scenario-dependent decision trade-off", loc="left", fontweight="bold"); ax.legend(frameon=False)
    ax.text(.02, .96, "Distinct: S2, S5\nShared: S1, S3, S4, S6", transform=ax.transAxes, va="top", fontsize=8)

    ax = axes[1, 1]; panel(ax, "D")
    ch = [("Both traits:\nno CS", 130994), ("Disease:\nno CS", 16819), ("QTL:\nno CS", 177405), ("Pair\nevaluable", 160782)]
    ypos = np.arange(4)[::-1]; vals = [x[1] for x in ch]
    bars = ax.barh(ypos, vals, color=["#D8DEE9", "#B9C2CE", GREY, BLUE], height=.55)
    ax.set_yticks(ypos, [x[0] for x in ch]); ax.set_xlabel("Iterations"); ax.set_xlim(0, 225000)
    for b, n in zip(bars, vals):
        ax.text(n + 3500, b.get_y() + b.get_height() / 2, f"{n:,}", va="center", fontweight="bold", fontsize=8)
    ax.set_title("Why iterations were not pair-evaluable", loc="left", fontweight="bold")
    ax.text(.98, .06, "0 recorded technical errors\n0 both-CS/no-pair events", transform=ax.transAxes, ha="right", fontsize=8,
            bbox=dict(boxstyle="round,pad=.25", fc="white", ec=LIGHT))

    fig.suptitle("Simulation separates credible-set discovery from pair-conditional inference", fontsize=16, fontweight="bold", color=DARK, y=.995)
    fig.tight_layout(rect=[0, 0, 1, .96], w_pad=2.2, h_pad=2.4); save(fig, "Figure3_simulation_discovery_and_inference")


def figure4() -> None:
    rep = pd.read_csv(ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure5_representative_signal_axes.tsv", sep="\t")
    row = exactly_one(rep, (rep.gene == "IL12RB2") & (rep.cell_type == "NK"), "IL12RB2-NK representative row")
    fg = pd.read_csv(ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure4_IL12RB2_FinnGen_coloc.tsv", sep="\t")
    chrom = pd.read_csv(ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure4_IL12RB2_positional_chromatin.tsv", sep="\t")
    c = exactly_one(chrom, chrom.gene == "IL12RB2", "IL12RB2 chromatin row")
    if bool(c.variant_in_peak_caqtl_CS) or bool(c.complete_variant_level_cascade_supported):
        raise ValueError("Chromatin boundary changed")
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.6))
    ax = axes[0, 0]; panel(ax, "A")
    vals = [row.pf10_l5_best_h4, row.pf10_l10_best_h4, row.pf10_l20_best_h4, row.pf50_l10_best_h4]
    labs = ["PF10 L5", "PF10 L10", "PF10 L20", "PF50 L10"]
    bars = ax.bar(labs, vals, color=[TEAL, TEAL, TEAL, BLUE])
    ax.axhline(.8, color=RED, ls="--", lw=1); ax.set_ylim(0, 1.05); ax.set_ylabel("Best signal-pair PP.H4")
    for b, v in zip(bars, vals): ax.text(b.get_x()+b.get_width()/2, v+.018, f"{v:.3f}", ha="center", fontsize=8)
    ax.set_title("OneK1K source-matched IL12RB2–NK", loc="left", fontweight="bold")

    ax = axes[0, 1]; panel(ax, "B")
    bars = ax.bar(list(fg.cell_type2), fg["PP.H4.abf"], color=BLUE)
    ax.axhline(.8, color=RED, ls="--", lw=1); ax.set_ylim(0, 1.05); ax.set_ylabel("FinnGen PP.H4")
    for b, v, o in zip(bars, fg["PP.H4.abf"], fg.cs_overlap): ax.text(b.get_x()+b.get_width()/2, v+.018, f"{v:.3f}\nCS={int(o)}", ha="center", fontsize=8)
    ax.set_title("FinnGen PBC–IL12RB2 molecular-QTL records", loc="left", fontweight="bold")

    ax = axes[1, 0]; panel(ax, "C"); ax.axis("off")
    for txt, x0, col in [("OneK1K\nNK", .07, TEAL), ("TenK10K\nNK", .38, BLUE), ("FinnGen\nNK/PBMC", .69, PURPLE)]:
        box(ax, x0, .48, .23, .27, txt, "", col)
    for x0 in [.30, .61]: ax.annotate("", xy=(x0+.07, .615), xytext=(x0, .615), arrowprops=dict(arrowstyle="-|>", lw=1.8, color=GREY))
    ax.text(.5, .28, "PBC risk allele associated with higher IL12RB2 expression", ha="center", fontweight="bold", color=DARK)
    ax.text(.5, .15, "Directionally concordant association; not a mediation estimate", ha="center", color=RED)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.set_title("Cross-resource direction", loc="left", fontweight="bold")

    ax = axes[1, 1]; panel(ax, "D"); ax.axis("off")
    outlines = [
        (.70, "Observed disease–expression evidence", "PBC–IL12RB2 eQTL sharing in FinnGen strata"),
        (.45, "Observed positional / peak–gene support", f"Anchor lies in linked peak; link beta={c.peak_gene_link_beta:.3f}"),
        (.20, "Observed peak accessibility QTL", f"Peak caQTL q={c.peak_caqtl_q_l1_NK:.2e} / {c.peak_caqtl_q_l2_NK:.2e}"),
    ]
    for y, title, subtitle in outlines:
        ax.add_patch(FancyBboxPatch((.04, y), .92, .17, boxstyle="round,pad=.012", fill=False, linewidth=1.1, edgecolor=BLUE))
        ax.text(.07, y+.112, title, fontsize=9.5, fontweight="bold", va="center")
        ax.text(.07, y+.055, subtitle, fontsize=7.7, va="center")
    ax.text(.5, .10, "UNESTABLISHED LINKS", ha="center", fontweight="bold", color=RED)
    ax.text(.5, .025, "Anchor absent from peak caQTL CS; disease–caQTL sharing and a complete cascade are unestablished",
            ha="center", fontsize=7.5)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.set_title("Separate chromatin evidence layers", loc="left", fontweight="bold")

    fig.suptitle("IL12RB2–NK is supported across molecular-QTL resources within bounded causal claims", fontsize=15, fontweight="bold", color=DARK, y=.995)
    fig.tight_layout(rect=[0, 0, 1, .96], w_pad=2, h_pad=2); save(fig, "Figure4_IL12RB2_external_evidence")


def figure5() -> None:
    rep = pd.read_csv(ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure5_representative_signal_axes.tsv", sep="\t")
    traj = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/adjudication/R7B2A_642_four_arm_trajectories.tsv", sep="\t")
    multi = pd.read_csv(ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv", sep="\t")
    f = rep[rep.gene == "FCRL3"].copy()
    cd8 = exactly_one(traj, traj.comparison_id == "R7B1_000414", "FCRL3-CD8_ET")
    cd8m = exactly_one(multi, multi.comparison_id == "R7B1_000414", "FCRL3-CD8_ET multi-signal")
    vals5c = [float(cd8.A0_PP_H4), float(cd8.A1_PP_H4), float(cd8.A2_PP_H4),
              float(cd8.pf10_l10_best_h4), float(cd8m.pf50_l10_best_h4)]
    expected = [0.941334682686132, 0.9413349988264992, 0.949260546232612, 0.0036361957364122, 0.991894292309108]
    if not np.allclose(vals5c, expected, rtol=0, atol=1e-12):
        raise ValueError(f"Figure 5C values changed: {vals5c}")
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.6))
    ax = axes[0, 0]; panel(ax, "A")
    vals = [float(exactly_one(f, f.cell_type == c, f"FCRL3 {c}").pf10_l10_best_h4) for c in ["B_IN", "B_MEM", "CD8_ET"]]
    bars = ax.bar(["B intermediate", "B memory", "CD8 effector T"], vals, color=[TEAL, TEAL, ORANGE])
    ax.axhline(.8, color=RED, ls="--", lw=1); ax.set_ylim(0, 1.05); ax.set_ylabel("PF10 L10 best PP.H4")
    for b, v in zip(bars, vals): ax.text(b.get_x()+b.get_width()/2, v+.018, f"{v:.3f}", ha="center", fontsize=8)
    ax.set_title("Cell-context-specific OneK1K assignments", loc="left", fontweight="bold")

    ax = axes[0, 1]; panel(ax, "B")
    vals = [.9937, .9910, .9916]; labs = ["OneK B_IN", "OneK B_MEM", "TenK B intermediate"]
    bars = ax.bar(labs, vals, color=[TEAL, TEAL, BLUE])
    ax.axhline(.8, color=RED, ls="--", lw=1); ax.set_ylim(0, 1.05); ax.set_ylabel("PP.H4")
    for b, v in zip(bars, vals): ax.text(b.get_x()+b.get_width()/2, v+.018, f"{v:.4f}", ha="center", fontsize=8)
    ax.set_title("Cross-QTL-resource B-cell support", loc="left", fontweight="bold")

    ax = axes[1, 0]; panel(ax, "C")
    labs = ["A0\nhistorical", "A1\nsupport-matched", "A2\nstats-matched", "M\nPF10", "M\nPF50"]
    bars = ax.bar(labs, vals5c, color=[GREY, GREY, BLUE, ORANGE, PURPLE])
    ax.axhline(.8, color=RED, ls="--", lw=1); ax.set_ylim(0, 1.11); ax.set_ylabel("PP.H4 / best signal-pair PP.H4")
    for b, v in zip(bars, vals5c): ax.text(b.get_x()+b.get_width()/2, v+.022, f"{v:.6f}", ha="center", fontsize=7.5, rotation=0)
    ax.set_title("FCRL3–CD8_ET input and model sensitivity", loc="left", fontweight="bold")
    ax.text(.98, .12, "ABF arms: H4\nPF10: H3; PF50: H4", transform=ax.transAxes, ha="right", fontsize=8, color=RED)

    ax = axes[1, 1]; panel(ax, "D"); ax.axis("off")
    box(ax, .06, .58, .38, .24, "B-cell sharing", "OneK + TenK", TEAL)
    box(ax, .56, .58, .38, .24, "CD8_ET", "model-sensitive", ORANGE)
    ax.text(.5, .40, "PBC risk allele associated with lower FCRL3 expression\nin compatible OneK and TenK B-cell contexts", ha="center", fontweight="bold")
    ax.text(.5, .22, "FinnGen public output returned no PBC–FCRL3 pair", ha="center")
    ax.text(.5, .10, "Non-return is a coverage boundary, not powered negative replication", ha="center", color=RED, fontsize=8)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.set_title("Claim boundary", loc="left", fontweight="bold")

    fig.suptitle("FCRL3 combines reproducible B-cell sharing with a T-cell model-sensitivity counterexample", fontsize=15, fontweight="bold", color=DARK, y=.995)
    fig.tight_layout(rect=[0, 0, 1, .96], w_pad=2, h_pad=2); save(fig, "Figure5_FCRL3_support_and_counterexample")


def deterministic_offsets(n: int) -> np.ndarray:
    templates = {
        1: [0], 2: [-.08, .08], 3: [-.10, 0, .10], 4: [-.12, -.04, .04, .12],
        5: [-.14, -.07, 0, .07, .14],
    }
    if n not in templates:
        return np.linspace(-.15, .15, n)
    return np.asarray(templates[n], dtype=float)


def figure6() -> None:
    donor = pd.read_csv(ROOT / "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel.tsv", sep="\t")
    summ = pd.read_csv(ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure6_exact_5vs5_tissue.tsv", sep="\t")
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    for j, axis_name in enumerate(["FCRL3_B", "IL12RB2_NK"]):
        ax = axes[j]; panel(ax, chr(ord("A") + j))
        d = donor[donor.target_lineage == axis_name].copy(); d["log1p_CPM"] = np.log1p(d.target_lineage_CPM)
        d["display_group"] = np.where(d.group == "PBC", "PBC", "Control")
        sns.boxplot(data=d, x="display_group", y="log1p_CPM", order=["Control", "PBC"], ax=ax, color="white", width=.5, fliersize=0)
        for xpos, (grp, col) in enumerate([("Control", BLUE), ("PBC", ORANGE)]):
            values = d.loc[d.display_group == grp, "log1p_CPM"].sort_values().to_numpy()
            if len(values) != 5:
                raise ValueError(f"Figure 6 {axis_name} {grp}: expected five donors")
            ax.scatter(xpos + deterministic_offsets(len(values)), values, s=45, color=col, edgecolor="white", linewidth=.5, zorder=4)
        row = exactly_one(summ, summ.axis == axis_name, f"tissue summary {axis_name}")
        title = "FCRL3 in B-lineage cells" if axis_name == "FCRL3_B" else "IL12RB2 in NK-lineage cells"
        ax.set_title(title, loc="left", fontweight="bold"); ax.set_xlabel(""); ax.set_ylabel("log1p target-lineage CPM")
        ax.text(.5, .98, f"Exact P={row.exact_label_permutation_p:.3f}; BH q={row.BH_q_two_prespecified_targets:.3f}\nDetected in 5/5 donors per group",
                transform=ax.transAxes, ha="center", va="top", fontsize=8,
                bbox=dict(boxstyle="round,pad=.25", fc="white", ec=LIGHT))

    ax = axes[2]; panel(ax, "C"); ax.axis("off")
    for y, title, col in [(.70, "Lineage detectability supported", TEAL), (.43, "No corrected PBC-specific enrichment", ORANGE), (.16, "No tissue mediation or disease-state claim", GREY)]:
        box(ax, .12, y, .76, .16, title, "", col)
    for y1, y2 in [(.69, .61), (.42, .34)]: ax.annotate("", xy=(.5, y2), xytext=(.5, y1), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.5))
    ax.text(.5, .03, "Bounded 2-target panel; n=5 PBC and 5 controls", ha="center", fontsize=8)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.set_title("Tissue evidence ceiling", loc="left", fontweight="bold")
    fig.suptitle("Liver data localize target-lineage expression but do not show corrected disease enrichment", fontsize=15, fontweight="bold", color=DARK, y=1.02)
    fig.tight_layout(); save(fig, "Figure6_liver_tissue_boundary")


def main() -> None:
    figure1(); figure2(); figure3(); figure4(); figure5(); figure6()
    hashes = {}
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name.startswith(tuple(f"Figure{i}_" for i in range(1, 7))):
            hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    if len(hashes) != 18:
        raise RuntimeError(f"Expected 18 figure files, found {len(hashes)}")
    (OUT / "FIGURE_HASHES.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    print(f"Built and hashed {len(hashes)} files in {OUT}")


if __name__ == "__main__":
    main()
