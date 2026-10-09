#!/usr/bin/env python3
"""Build publication-facing R7B1C calibration figures and source tables."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
AGG = ROOT / "3_results/05_simulation/R7B1C/aggregate"
OUT = ROOT / "4_figures/R7B1C"
SRC = OUT / "source_data"
COLORS = {"ABF": "#8B95A5", "Source-matched multi-signal": "#176B87", "PF50-LD mismatch": "#C8553D"}


def save(fig, name: str) -> None:
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True); SRC.mkdir(exist_ok=True)
    scenario = pd.read_csv(AGG / "R7B1C_scenario_summary.tsv", sep="\t")
    row = pd.read_csv(AGG / "R7B1C_grid_486_summary.tsv", sep="\t")
    order = [f"S{i}" for i in range(1, 7)]
    scenario["short"] = scenario.scenario.str.extract(r"^(S\d)")
    scenario = scenario.set_index("short").loc[order].reset_index()

    f1 = scenario[["short","scenario","true_shared","abf_h4_rate","matched_h4_rate"]].copy()
    f1.to_csv(SRC / "Figure_R7B1C_1_decision_rates.tsv", sep="\t", index=False)
    x = np.arange(len(f1)); width = .36
    fig, ax = plt.subplots(figsize=(9.2, 4.9))
    ax.bar(x-width/2, f1.abf_h4_rate, width, label="Single-causal ABF", color=COLORS["ABF"])
    ax.bar(x+width/2, f1.matched_h4_rate, width, label="Source-matched multi-signal", color=COLORS["Source-matched multi-signal"])
    ax.set_xticks(x, f1.short); ax.set_ylim(0,1); ax.set_ylabel("H4 decision rate")
    ax.set_title("Truth-known shared-signal decisions across six frozen scenarios", loc="left", fontweight="bold")
    ax.legend(frameon=False, ncol=2); ax.grid(axis="y",alpha=.2)
    for i, shared in enumerate(f1.true_shared):
        ax.text(i,.98,"shared" if shared else "distinct",ha="center",va="top",fontsize=8,color="#4A5568")
    fig.tight_layout(); save(fig,"Figure_R7B1C_1_scenario_H4_decisions")

    long = []
    for (sc, r2), d in row.groupby(["scenario","causal_r2"]):
        long += [
            {"scenario":sc,"causal_r2":r2,"method":"ABF","H4_rate":np.average(d.abf_h4_rate,weights=d.replicates)},
            {"scenario":sc,"causal_r2":r2,"method":"Source-matched multi-signal","H4_rate":np.average(d.matched_h4_rate,weights=d.replicates)},
        ]
    f2 = pd.DataFrame(long); f2.to_csv(SRC / "Figure_R7B1C_2_r2_stratified.tsv",sep="\t",index=False)
    fig, axes = plt.subplots(2,3,figsize=(11,6.3),sharex=True,sharey=True)
    for ax, sc in zip(axes.flat, scenario.scenario):
        d=f2[f2.scenario==sc]
        for method, md in d.groupby("method"):
            ax.plot(md.causal_r2,md.H4_rate,marker="o",lw=2,label=method,color=COLORS[method])
        ax.set_title(sc.split("_",1)[0]); ax.set_ylim(0,1); ax.grid(alpha=.2)
    axes[1,0].set_xlabel("Target causal r²"); axes[1,1].set_xlabel("Target causal r²"); axes[1,2].set_xlabel("Target causal r²")
    axes[0,0].set_ylabel("H4 decision rate"); axes[1,0].set_ylabel("H4 decision rate")
    handles,labels=axes[0,0].get_legend_handles_labels(); fig.legend(handles,labels,loc="upper center",ncol=2,frameon=False)
    fig.suptitle("LD-dependent decision behavior",x=.05,ha="left",fontweight="bold"); fig.tight_layout(rect=(0,0,1,.93))
    save(fig,"Figure_R7B1C_2_LD_stratified_decisions")

    s6row=row[row.scenario=="S6_matched_vs_mismatched_LD"].copy()
    f3=(s6row.groupby(["maf","causal_r2"],as_index=False)
        .apply(lambda d: pd.Series({
            "matched_H4_rate":np.average(d.matched_h4_rate,weights=d.replicates),
            "mismatch_H4_rate":np.average(d.mismatch_h4_rate,weights=d.replicates),
            "decision_flip_rate":np.average(d.mismatch_decision_flip_rate,weights=d.replicates),
            "mean_abs_H4_delta":np.average(d.mismatch_mean_abs_h4_delta,weights=d.replicates)}),include_groups=False))
    f3.to_csv(SRC / "Figure_R7B1C_3_S6_mismatch.tsv",sep="\t",index=False)
    fig,axes=plt.subplots(1,2,figsize=(9.5,4.1))
    for maf,d in f3.groupby("maf"):
        axes[0].plot(d.causal_r2,d.matched_H4_rate,marker="o",label=f"matched MAF={maf:g}")
        axes[0].plot(d.causal_r2,d.mismatch_H4_rate,marker="x",ls="--",label=f"mismatch MAF={maf:g}")
        axes[1].plot(d.causal_r2,d.mean_abs_H4_delta,marker="o",label=f"MAF={maf:g}")
    axes[0].set_ylabel("H4 decision rate"); axes[1].set_ylabel("Mean |Δ best H4|")
    for ax in axes: ax.set_xlabel("Target causal r²"); ax.grid(alpha=.2)
    axes[0].legend(frameon=False,fontsize=7,ncol=2); axes[1].legend(frameon=False,fontsize=8)
    fig.suptitle("Bounded same-locus PF10→PF50 LD mismatch",x=.06,ha="left",fontweight="bold")
    fig.tight_layout(); save(fig,"Figure_R7B1C_3_same_locus_LD_mismatch")

    f4=scenario[["short","scenario","matched_d_cover_all_rate","matched_q_cover_all_rate","matched_mean_d_cs_size","matched_mean_q_cs_size"]].copy()
    f4.to_csv(SRC / "Figure_R7B1C_4_credible_set_coverage.tsv",sep="\t",index=False)
    fig,ax=plt.subplots(figsize=(9,4.8)); x=np.arange(len(f4))
    ax.plot(x,f4.matched_d_cover_all_rate,marker="o",lw=2,label="Disease all-causal coverage",color="#5B4B8A")
    ax.plot(x,f4.matched_q_cover_all_rate,marker="o",lw=2,label="QTL all-causal coverage",color="#2A9D8F")
    ax.set_xticks(x,f4.short);ax.set_ylim(0,1);ax.set_ylabel("95% CS all-causal coverage")
    ax.set_title("Credible-set coverage under the matched model",loc="left",fontweight="bold")
    ax.grid(axis="y",alpha=.2);ax.legend(frameon=False,ncol=2);fig.tight_layout();save(fig,"Figure_R7B1C_4_credible_set_coverage")

    state={"schema":"R7B1C_FIGURE_ASSEMBLY_1.0","status":"PASS","figures":4,"source_tables":4}
    (OUT/"figure_assembly_state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state,indent=2))


if __name__=="__main__": main()
