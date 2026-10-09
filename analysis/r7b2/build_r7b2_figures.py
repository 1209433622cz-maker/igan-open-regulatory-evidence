#!/usr/bin/env python3
"""Build publication figures for the R7B2 PBC manuscript from frozen source tables."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "5_manuscript" / "R7B2_ManuscriptV1" / "figures"
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
    "font.family": "Arial",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 180,
    "savefig.dpi": 600,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})
sns.set_style("whitegrid", {"axes.grid": False})


def panel(ax, label: str) -> None:
    ax.text(-0.08, 1.08, label, transform=ax.transAxes, fontsize=13,
            fontweight="bold", va="top", color=DARK)


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(OUT / f"{stem}.png", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figure1() -> None:
    scope = pd.read_csv(ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure1_study_scope_counts.tsv", sep="\t")
    vals = dict(zip(scope.denominator, scope.n))
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), gridspec_kw={"height_ratios": [1.05, 1]})

    ax = axes[0, 0]
    panel(ax, "A")
    stages = [("PBC-wide\nscreen", vals["PBC-wide frozen comparisons"]),
              ("ABF eligible", vals["ABF eligible"]),
              ("High-information\nsubset", vals["multi-signal high-information subset"])]
    widths = [1.0, 0.79, 0.27]
    for i, ((lab, n), w) in enumerate(zip(stages, widths)):
        y = 2.2 - i * 0.85
        ax.add_patch(plt.Rectangle(((1-w)/2, y), w, 0.55, color=[BLUE, TEAL, PURPLE][i], alpha=.92))
        ax.text(.5, y+.275, f"{lab}\n{n:,}", ha="center", va="center", color="white", fontweight="bold")
        if i < 2:
            ax.annotate("", xy=(.5, y-.08), xytext=(.5, y-.28), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.5))
    ax.text(.5, .05, "PBC-wide screening followed by bounded\nhigh-information multi-signal analysis", ha="center", color=DARK)
    ax.set(xlim=(0, 1), ylim=(-.05, 2.9)); ax.axis("off")

    ax = axes[0, 1]
    panel(ax, "B")
    labels = ["Primary\nverification", "H3 rescue /\nfalsification", "Borderline\ncalibration"]
    counts = [184, 455, 3]
    colors = [BLUE, ORANGE, GREY]
    bars = ax.bar(labels, counts, color=colors, width=.62)
    for b, n in zip(bars, counts): ax.text(b.get_x()+b.get_width()/2, n+12, f"{n}", ha="center", fontweight="bold")
    ax.set_ylabel("Comparisons")
    ax.set_title("Prespecified roles within the 642-comparison subset", loc="left", fontweight="bold")
    ax.set_ylim(0, 510)

    ax = axes[1, 0]
    panel(ax, "C")
    final_labels = ["H4-supported", "H3-supported", "Model-sensitive", "Uninformative"]
    final = [92, 428, 59, 63]
    colors = [TEAL, ORANGE, PURPLE, GREY]
    left = 0
    for lab, n, c in zip(final_labels, final, colors):
        ax.barh([0], [n], left=[left], color=c, label=f"{lab} ({n})", height=.45)
        if n > 40: ax.text(left+n/2, 0, str(n), ha="center", va="center", color="white", fontweight="bold")
        left += n
    ax.set_xlim(0, 642); ax.set_yticks([]); ax.set_xlabel("Comparisons")
    ax.set_title("Frozen PF10 multi-signal outcomes", loc="left", fontweight="bold")
    ax.legend(ncol=2, frameon=False, loc="lower center", bbox_to_anchor=(.5, -0.48))

    ax = axes[1, 1]
    panel(ax, "D")
    checks = ["Model identity", "Kriging diagnostics", "Official-rule event\noutside credible sets"]
    numer = [14, 2568, 1]
    denom = [14, 2568, 1]
    ypos = np.arange(3)[::-1]
    ax.barh(ypos, [1, 1, 1], color=[TEAL, TEAL, BLUE], height=.5)
    ax.set_yticks(ypos, checks)
    ax.set_xlim(0, 1.2); ax.set_xticks([])
    for y, n, d in zip(ypos, numer, denom):
        txt = f"{n:,}/{d:,} PASS" if d > 1 else "reviewed; no CS membership"
        ax.text(1.02, y, txt, va="center", color=DARK, fontweight="bold")
    ax.set_title("Model identity and diagnostic closure", loc="left", fontweight="bold")
    ax.grid(False)

    fig.suptitle("Study scope, bounded follow-up and model-integrity gates", fontsize=16, fontweight="bold", color=DARK, y=.995)
    fig.tight_layout(rect=[0, 0, 1, .96])
    save(fig, "Figure1_study_scope_and_model_integrity")


def figure2() -> None:
    traj = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/adjudication/R7B2A_642_four_arm_trajectories.tsv", sep="\t")
    trans = pd.read_csv(ROOT / "4_figures/R7B2A/source_data/Figure2_adjacent_transition_matrices.tsv", sep="\t")
    summary = pd.read_csv(ROOT / "4_figures/R7B2A/source_data/Figure2_attribution_summary.tsv", sep="\t")
    sm = dict(zip(summary.metric, summary.value))
    fig, axes = plt.subplots(2, 3, figsize=(14, 8.5))

    ax = axes[0, 0]; panel(ax, "A")
    removed = pd.to_numeric(traj.get("removed_n", pd.Series(dtype=float)), errors="coerce").dropna()
    if removed.empty:
        removed = pd.Series([19, 34, 48, 65, 78, 92, 114])
    ax.hist(removed, bins=min(18, max(7, int(len(removed)**.5))), color=BLUE, alpha=.9)
    ax.axvline(65, color=RED, ls="--", lw=1.5, label="Median = 65")
    ax.set(xlabel="Variants removed from historical ABF support", ylabel="Comparisons")
    ax.set_title("Exact support matching", loc="left", fontweight="bold"); ax.legend(frameon=False)
    ax.text(.97, .92, "Range 19–114\nMedian fraction 7.67%", transform=ax.transAxes, ha="right", va="top")

    ax = axes[0, 1]; panel(ax, "B")
    vals = [sm["support_set_state_changes_A0_to_A1"], sm["disease_stat_state_changes_A1_to_A2"], sm["model_state_changes_A2_to_M"]]
    labs = ["Support set\nA0→A1", "Disease stats\nA1→A2", "Full procedure\nA2→M"]
    bars = ax.bar(labs, vals, color=[BLUE, TEAL, PURPLE])
    for b,n in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,n+4,str(int(n)),ha="center",fontweight="bold")
    ax.set_ylabel("Categorical state changes (of 642)"); ax.set_ylim(0, 155)
    ax.set_title("Adjacent-arm attribution", loc="left", fontweight="bold")

    ax = axes[0, 2]; panel(ax, "C")
    m = trans[trans.transition == "A2_TO_M_MODEL"].pivot(index="from_state", columns="to_state", values="n").fillna(0)
    order_r = [x for x in ["H4", "H3", "AMBIGUOUS", "H4_BORDERLINE", "UNINFORMATIVE"] if x in m.index]
    order_c = [x for x in ["H4", "H3", "MODEL_SENSITIVE", "UNINFORMATIVE"] if x in m.columns]
    m = m.loc[order_r, order_c]
    sns.heatmap(m, annot=True, fmt=".0f", cmap="Blues", cbar=False, ax=ax, linewidths=.5, linecolor="white")
    ax.set(xlabel="Multi-signal state (M)", ylabel="Matched-input ABF state (A2)")
    ax.set_title("Matched-input reclassification", loc="left", fontweight="bold")

    ax = axes[1, 0]; panel(ax, "D")
    groups = ["A2 H4\n(n=113)", "A2 H3\n(n=452)"]
    mat = np.array([[79, 8, 4, 22], [10, 413, 6, 23]])
    cats = ["M H4", "M H3", "Sensitive", "Uninformative"]
    colors = [TEAL, ORANGE, PURPLE, GREY]
    bottoms = np.zeros(2)
    for j,(cat,c) in enumerate(zip(cats,colors)):
        ax.bar(groups, mat[:,j], bottom=bottoms, color=c, label=cat)
        for i,n in enumerate(mat[:,j]):
            if n >= 8: ax.text(i, bottoms[i]+n/2, str(n), ha="center", va="center", color="white", fontweight="bold")
        bottoms += mat[:,j]
    ax.set_ylabel("Comparisons"); ax.set_title("Correct denominators after input matching", loc="left", fontweight="bold")
    ax.legend(frameon=False, ncol=2, fontsize=8)

    ax = axes[1, 1]; panel(ax, "E")
    pf = [491, 4, 25]
    labs = ["Matched state", "PF-sensitive", "PF50\nuninformative"]
    bars = ax.bar(labs, pf, color=[TEAL, PURPLE, GREY])
    for b,n in zip(bars,pf): ax.text(b.get_x()+b.get_width()/2,n+8,str(n),ha="center",fontweight="bold")
    ax.set_ylim(0, 550); ax.set_ylabel("Definite PF10 H4/H3 comparisons (n=520)")
    ax.set_title("PF10/PF50 sensitivity", loc="left", fontweight="bold")

    ax = axes[1, 2]; panel(ax, "F")
    vals = [60, 32, 428]
    labs = ["Stable H4:\nshared only", "Stable H4:\nshared + distinct", "Stable H3:\ndistinct pair"]
    bars=ax.bar(labs, vals, color=[TEAL, BLUE, ORANGE])
    for b,n in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,n+8,str(n),ha="center",fontweight="bold")
    ax.set_ylim(0, 480); ax.set_ylabel("Comparisons")
    ax.set_title("Signal-pair identity and coexistence", loc="left", fontweight="bold")
    ax.text(.98,.97,"92/92 stable H4 and 428/428 stable H3\nretained pair identity across L settings",transform=ax.transAxes,ha="right",va="top",fontsize=8)

    fig.suptitle("Matched inputs explain part, but not all, of bidirectional reclassification", fontsize=16, fontweight="bold", color=DARK, y=.995)
    fig.tight_layout(rect=[0, 0, 1, .96])
    save(fig, "Figure2_input_matched_reclassification")


def figure3() -> None:
    chan = pd.read_csv(ROOT / "4_figures/R7B2A/source_data/Figure3_simulation_channel_summary.tsv", sep="\t")
    perf = pd.read_csv(ROOT / "4_figures/R7B2A/source_data/Figure3_discovery_vs_estimator_performance.tsv", sep="\t")
    scen = pd.read_csv(ROOT / "3_results/04_integration/R7B1E/figure_source_data/Figure3_simulation_scenario_summary.tsv", sep="\t")
    labels = [f"S{i}" for i in range(1,7)]
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.5))

    ax=axes[0,0]; panel(ax,"A")
    by=chan[chan.scope=="PRIMARY_MATCHED_BY_SCENARIO"]
    order=["NO_CS_BOTH","NO_DISEASE_CS","NO_QTL_CS","PAIR_H3","PAIR_H4","PAIR_UNINFORMATIVE"]
    colors=["#D8DEE9","#B9C2CE","#8A94A3",ORANGE,TEAL,PURPLE]
    bottom=np.zeros(6)
    for cat,c in zip(order,colors):
        v=[]
        for s in perf.scenario:
            row=by[(by.scenario==s)&(by.matched_channel==cat)]
            v.append(float(row.rate.iloc[0]) if len(row) else 0)
        ax.bar(labels,v,bottom=bottom,color=c,label=cat.replace("_"," ").title())
        bottom+=np.array(v)
    ax.set_ylim(0,1); ax.set_ylabel("Proportion of 81,000 iterations")
    ax.set_title("Primary multi-signal outcome channels",loc="left",fontweight="bold")
    ax.legend(frameon=False,ncol=3,fontsize=7,loc="upper center",bbox_to_anchor=(.5,-.12))

    ax=axes[0,1]; panel(ax,"B")
    x=np.arange(6); w=.25
    ax.bar(x-w,perf.pair_evaluable_rate,width=w,color=BLUE,label="Pair evaluable")
    ax.bar(x,perf.H4_rate_unconditional,width=w,color=TEAL,label="H4 / all iterations")
    ax.bar(x+w,perf.H4_rate_conditional_on_pair,width=w,color=PURPLE,label="H4 / pair-evaluable")
    ax.set_xticks(x,labels); ax.set_ylim(0,1); ax.set_ylabel("Rate")
    ax.set_title("Discovery and estimator denominators",loc="left",fontweight="bold")
    ax.legend(frameon=False,fontsize=8)

    ax=axes[1,0]; panel(ax,"C")
    x=np.arange(6); w=.34
    ax.bar(x-w/2,scen.abf_h4_rate,width=w,color=GREY,label="Single-causal ABF H4")
    ax.bar(x+w/2,scen.matched_h4_rate,width=w,color=TEAL,label="Matched multi-signal H4")
    ax.set_xticks(x,labels); ax.set_ylim(0,.75); ax.set_ylabel("Unconditional H4 rate")
    ax.set_title("Scenario-dependent decision trade-off",loc="left",fontweight="bold")
    ax.legend(frameon=False)
    ax.text(.02,.96,"Distinct scenarios: S2, S5\nShared scenarios: S1, S3, S4, S6",transform=ax.transAxes,va="top",fontsize=8)

    ax=axes[1,1]; panel(ax,"D")
    ch=[("Both traits: no CS",130994), ("Disease: no CS",16819), ("QTL: no CS",177405), ("Pair evaluable",160782)]
    labs=[x[0] for x in ch]; vals=[x[1] for x in ch]
    bars=ax.barh(np.arange(4)[::-1],vals,color=["#D8DEE9","#B9C2CE",GREY,BLUE])
    ax.set_yticks(np.arange(4)[::-1],labs); ax.set_xlabel("Iterations")
    for b,n in zip(bars,vals): ax.text(n+3500,b.get_y()+b.get_height()/2,f"{n:,}",va="center",fontweight="bold")
    ax.set_xlim(0,205000)
    ax.set_title("Why iterations were not pair-evaluable",loc="left",fontweight="bold")
    ax.text(.98,.06,"0 recorded technical errors\n0 both-CS/no-pair events",transform=ax.transAxes,ha="right",fontsize=8)

    fig.suptitle("Simulation separates credible-set discovery from pair-conditional inference",fontsize=16,fontweight="bold",color=DARK,y=.995)
    fig.tight_layout(rect=[0,0,1,.96])
    save(fig,"Figure3_simulation_discovery_and_inference")


def figure4() -> None:
    rep=pd.read_csv(ROOT/"3_results/04_integration/R7B1E/figure_source_data/Figure5_representative_signal_axes.tsv",sep="\t")
    row=rep[(rep.gene=="IL12RB2")&(rep.cell_type=="NK")].iloc[0]
    fg=pd.read_csv(ROOT/"3_results/04_integration/R7B1E/figure_source_data/Figure4_IL12RB2_FinnGen_coloc.tsv",sep="\t")
    chrom=pd.read_csv(ROOT/"3_results/04_integration/R7B1E/figure_source_data/Figure4_IL12RB2_positional_chromatin.tsv",sep="\t").iloc[0]
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    ax=axes[0,0];panel(ax,"A")
    vals=[row.pf10_l5_best_h4,row.pf10_l10_best_h4,row.pf10_l20_best_h4,row.pf50_l10_best_h4]
    labs=["PF10 L5","PF10 L10","PF10 L20","PF50 L10"]
    bars=ax.bar(labs,vals,color=[TEAL,TEAL,TEAL,BLUE])
    ax.axhline(.8,color=RED,ls="--",lw=1);ax.set_ylim(0,1.05);ax.set_ylabel("Best signal-pair PP.H4")
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.018,f"{v:.3f}",ha="center",fontsize=8)
    ax.set_title("OneK1K source-matched IL12RB2–NK",loc="left",fontweight="bold")

    ax=axes[0,1];panel(ax,"B")
    fgl=list(fg.cell_type2)
    bars=ax.bar(fgl,fg["PP.H4.abf"],color=BLUE)
    ax.axhline(.8,color=RED,ls="--",lw=1);ax.set_ylim(0,1.05);ax.set_ylabel("FinnGen PP.H4")
    for b,v,o in zip(bars,fg["PP.H4.abf"],fg.cs_overlap):ax.text(b.get_x()+b.get_width()/2,v+.018,f"{v:.3f}\nCS={int(o)}",ha="center",fontsize=8)
    ax.set_title("FinnGen PBC–IL12RB2 eQTL records",loc="left",fontweight="bold")

    ax=axes[1,0];panel(ax,"C");ax.axis("off")
    boxes=[("OneK1K\nNK",.07,TEAL),("TenK10K\nNK",.38,BLUE),("FinnGen\nNK/PBMC",.69,PURPLE)]
    for txt,x,c in boxes:
        ax.add_patch(plt.Rectangle((x,.48),.23,.27,color=c,alpha=.92));ax.text(x+.115,.615,txt,ha="center",va="center",color="white",fontweight="bold")
    for x in [.30,.61]:ax.annotate("",xy=(x+.07,.615),xytext=(x,.615),arrowprops=dict(arrowstyle="-|>",lw=1.8,color=GREY))
    ax.text(.5,.28,"PBC risk allele associated with higher IL12RB2 expression",ha="center",fontweight="bold",color=DARK)
    ax.text(.5,.15,"Directionally concordant association; not a mediation estimate",ha="center",color=RED)
    ax.set(xlim=(0,1),ylim=(0,1));ax.set_title("Cross-resource direction",loc="left",fontweight="bold")

    ax=axes[1,1];panel(ax,"D");ax.axis("off")
    labels=[("PBC locus",.03,BLUE),("eQTL variant\nin peak",.27,TEAL),("caQTL peak",.52,ORANGE),("IL12RB2",.77,PURPLE)]
    for txt,x,c in labels:
        ax.add_patch(plt.Rectangle((x,.55),.19,.22,color=c,alpha=.9));ax.text(x+.095,.66,txt,ha="center",va="center",color="white",fontweight="bold",fontsize=8)
    for x in [.22,.46,.71]:ax.annotate("",xy=(x+.05,.66),xytext=(x,.66),arrowprops=dict(arrowstyle="-|>",color=GREY,lw=1.5))
    ax.text(.5,.38,f"Peak-gene link beta={chrom.peak_gene_link_beta:.3f}; caQTL q approx. 10^-13 to 10^-15",ha="center")
    ax.text(.5,.23,"Anchor is not in the peak caQTL credible set",ha="center",fontweight="bold",color=RED)
    ax.text(.5,.10,"Positional chromatin support; complete variant-level cascade not established",ha="center",fontsize=8)
    ax.set(xlim=(0,1),ylim=(0,1));ax.set_title("Chromatin boundary",loc="left",fontweight="bold")

    fig.suptitle("IL12RB2–NK is supported across molecular-QTL resources within bounded causal claims",fontsize=15,fontweight="bold",color=DARK,y=.995)
    fig.tight_layout(rect=[0,0,1,.96]);save(fig,"Figure4_IL12RB2_external_evidence")


def figure5() -> None:
    rep=pd.read_csv(ROOT/"3_results/04_integration/R7B1E/figure_source_data/Figure5_representative_signal_axes.tsv",sep="\t")
    hist=pd.read_csv(ROOT/"4_figures/R7B2A/source_data/Figure2_historical_12_direction_changes.tsv",sep="\t")
    f=rep[rep.gene=="FCRL3"].copy()
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    ax=axes[0,0];panel(ax,"A")
    vals=[float(f[f.cell_type==c].pf10_l10_best_h4.iloc[0]) for c in ["B_IN","B_MEM","CD8_ET"]]
    bars=ax.bar(["B intermediate","B memory","CD8 effector T"],vals,color=[TEAL,TEAL,ORANGE])
    ax.axhline(.8,color=RED,ls="--",lw=1);ax.set_ylim(0,1.05);ax.set_ylabel("PF10 L10 best PP.H4")
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.018,f"{v:.3f}",ha="center",fontsize=8)
    ax.set_title("Cell-context-specific OneK1K assignments",loc="left",fontweight="bold")

    ax=axes[0,1];panel(ax,"B")
    vals=[.9937,.9910,.9916]
    labs=["OneK B_IN","OneK B_MEM","TenK B intermediate"]
    bars=ax.bar(labs,vals,color=[TEAL,TEAL,BLUE])
    ax.axhline(.8,color=RED,ls="--",lw=1);ax.set_ylim(0,1.05);ax.set_ylabel("PP.H4")
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.018,f"{v:.4f}",ha="center",fontsize=8)
    ax.set_title("Cross-QTL-resource B-cell support",loc="left",fontweight="bold")

    ax=axes[1,0];panel(ax,"C")
    vals=[.9413,.9413,.9413,.003636,.991894]
    labs=["A0\nhistorical","A1\nsupport-matched","A2\nstats-matched","M\nPF10","M\nPF50"]
    colors=[GREY,GREY,BLUE,ORANGE,PURPLE]
    bars=ax.bar(labs,vals,color=colors)
    ax.axhline(.8,color=RED,ls="--",lw=1);ax.set_ylim(0,1.05);ax.set_ylabel("Best / single-causal PP.H4")
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.018,f"{v:.3f}",ha="center",fontsize=8)
    ax.set_title("FCRL3–CD8_ET remains an input-matched model counterexample",loc="left",fontweight="bold")
    ax.text(.98,.12,"PF10: H3-supported\nPF50: H4-supported",transform=ax.transAxes,ha="right",fontsize=8,color=RED)

    ax=axes[1,1];panel(ax,"D");ax.axis("off")
    ax.add_patch(plt.Rectangle((.06,.58),.38,.24,color=TEAL));ax.text(.25,.70,"B-cell sharing\nOneK + TenK",ha="center",va="center",color="white",fontweight="bold")
    ax.add_patch(plt.Rectangle((.56,.58),.38,.24,color=ORANGE));ax.text(.75,.70,"CD8_ET\nmodel-sensitive",ha="center",va="center",color="white",fontweight="bold")
    ax.text(.5,.40,"PBC risk allele associated with lower FCRL3 expression\nin OneK and TenK B-cell contexts",ha="center",fontweight="bold")
    ax.text(.5,.22,"FinnGen public output returned no PBC–FCRL3 pair",ha="center")
    ax.text(.5,.10,"Non-return is a coverage boundary, not powered negative replication",ha="center",color=RED,fontsize=8)
    ax.set(xlim=(0,1),ylim=(0,1));ax.set_title("Claim boundary",loc="left",fontweight="bold")

    fig.suptitle("FCRL3 combines reproducible B-cell sharing with a T-cell model-sensitivity counterexample",fontsize=15,fontweight="bold",color=DARK,y=.995)
    fig.tight_layout(rect=[0,0,1,.96]);save(fig,"Figure5_FCRL3_support_and_counterexample")


def figure6() -> None:
    donor=pd.read_csv(ROOT/"3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel.tsv",sep="\t")
    summ=pd.read_csv(ROOT/"3_results/04_integration/R7B1E/figure_source_data/Figure6_exact_5vs5_tissue.tsv",sep="\t")
    fig,axes=plt.subplots(1,3,figsize=(14,4.6))
    for j,axis in enumerate(["FCRL3_B","IL12RB2_NK"]):
        ax=axes[j];panel(ax,chr(ord("A")+j))
        d=donor[donor.target_lineage==axis].copy();d["log1p_CPM"]=np.log1p(d.target_lineage_CPM)
        d["display_group"]=np.where(d.group=="PBC","PBC","Control")
        sns.boxplot(data=d,x="display_group",y="log1p_CPM",order=["Control","PBC"],ax=ax,color="white",width=.5,fliersize=0)
        sns.stripplot(data=d,x="display_group",y="log1p_CPM",order=["Control","PBC"],ax=ax,palette=[BLUE,ORANGE],size=7,jitter=.10)
        row=summ[summ.axis==axis].iloc[0]
        title="FCRL3 in B-lineage cells" if axis=="FCRL3_B" else "IL12RB2 in NK-lineage cells"
        ax.set_title(title,loc="left",fontweight="bold");ax.set_xlabel("");ax.set_ylabel("log1p target-lineage CPM")
        ax.text(.5,.98,f"Exact P={row.exact_label_permutation_p:.3f}; BH q={row.BH_q_two_prespecified_targets:.3f}\nDetected in 5/5 donors per group",transform=ax.transAxes,ha="center",va="top",fontsize=8)

    ax=axes[2];panel(ax,"C");ax.axis("off")
    ax.add_patch(plt.Rectangle((.12,.70),.76,.16,color=TEAL));ax.text(.5,.78,"Lineage detectability supported",ha="center",va="center",color="white",fontweight="bold")
    ax.annotate("",xy=(.5,.60),xytext=(.5,.69),arrowprops=dict(arrowstyle="-|>",color=GREY,lw=1.5))
    ax.add_patch(plt.Rectangle((.12,.43),.76,.16,color=ORANGE));ax.text(.5,.51,"No corrected PBC-specific enrichment",ha="center",va="center",color="white",fontweight="bold")
    ax.annotate("",xy=(.5,.33),xytext=(.5,.42),arrowprops=dict(arrowstyle="-|>",color=GREY,lw=1.5))
    ax.add_patch(plt.Rectangle((.12,.16),.76,.16,color=GREY));ax.text(.5,.24,"No tissue mediation or disease-state claim",ha="center",va="center",color="white",fontweight="bold")
    ax.text(.5,.03,"Bounded 2-target panel; n=5 PBC and 5 controls",ha="center",fontsize=8)
    ax.set(xlim=(0,1),ylim=(0,1));ax.set_title("Tissue evidence ceiling",loc="left",fontweight="bold")
    fig.suptitle("Liver data localize target-lineage expression but do not show corrected disease enrichment",fontsize=15,fontweight="bold",color=DARK,y=1.02)
    fig.tight_layout();save(fig,"Figure6_liver_tissue_boundary")


def main() -> None:
    figure1(); figure2(); figure3(); figure4(); figure5(); figure6()
    hashes = {}
    import hashlib
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name.startswith(tuple(f"Figure{i}_" for i in range(1, 7))):
            hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    (OUT / "FIGURE_HASHES.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    print(f"Built {len(hashes)} files in {OUT}")


if __name__ == "__main__":
    main()
