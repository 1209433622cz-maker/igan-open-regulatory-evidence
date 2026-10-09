#!/usr/bin/env python3
"""Build R7B2A claim, Methods/Results, Figure 1-6 and visual source assets."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
R7B1E = ROOT / "3_results/04_integration/R7B1E"
if not R7B1E.exists():
    R7B1E = ROOT / "github/igan-open-regulatory-evidence/results/r7b1e"
ADJ = ROOT / "3_results/04_integration/R7B2A/adjudication"
SIM = ROOT / "3_results/05_simulation/R7B2A_audit"
OUT = ROOT / "3_results/04_integration/R7B2A/manuscript_lock"
FIG = ROOT / "4_figures/R7B2A"
SRC = FIG / "source_data"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SRC.mkdir(parents=True, exist_ok=True)
    transitions = pd.read_csv(ADJ / "R7B2A_adjacent_transition_matrices.tsv", sep="\t")
    attribution = pd.read_csv(ADJ / "R7B2A_attribution_summary.tsv", sep="\t")
    hist12 = pd.read_csv(ADJ / "R7B2A_historical_12_direction_changes_audit.tsv", sep="\t")
    channels = pd.read_csv(SIM / "R7B2A_R7B1C_channel_summary.tsv", sep="\t")
    perf = pd.read_csv(SIM / "R7B2A_R7B1C_discovery_vs_estimator_performance.tsv", sep="\t")

    source_map = {
        "Figure2_adjacent_transition_matrices.tsv": transitions,
        "Figure2_attribution_summary.tsv": attribution,
        "Figure2_historical_12_direction_changes.tsv": hist12,
        "Figure3_simulation_channel_summary.tsv": channels,
        "Figure3_discovery_vs_estimator_performance.tsv": perf,
    }
    for name, frame in source_map.items():
        frame.to_csv(SRC / name, sep="\t", index=False)

    old_ledger = pd.read_csv(R7B1E / "R7B1E_integrated_claim_evidence_ledger.tsv", sep="\t")
    ledger = old_ledger.copy()
    replacements = {
        "C03": {
            "claim_text": "After exact support and disease-statistic matching, multi-signal analysis still showed bidirectional H4/H3 reclassification.",
            "quantitative_anchor": "matched-input H4-to-H3=8; H3-to-H4=10",
            "primary_source_file": rel(ADJ / "R7B2A_642_four_arm_trajectories.tsv"),
            "supporting_source_files": rel(ADJ / "R7B2A_adjacent_transition_matrices.tsv"),
            "allowed_verbs": "reclassified; remained after input matching",
            "prohibited_verbs": "proved correct/incorrect; superior",
            "limitation": "Real data contain no causal truth; A2-to-M contrasts full inference procedures.",
        },
        "C04": {
            "claim_text": "Among 113 matched-input ABF H4 comparisons, 79 retained H4 and 8 changed to H3 under the multi-signal model.",
            "quantitative_anchor": "79/113 stable H4; 8/113 H4-to-H3; 4 sensitive; 22 uninformative",
            "primary_source_file": rel(ADJ / "R7B2A_642_four_arm_trajectories.tsv"),
            "supporting_source_files": rel(ADJ / "R7B2A_adjacent_transition_matrices.tsv"),
            "allowed_verbs": "retained; changed",
            "prohibited_verbs": "false-positive rate in real data",
            "limitation": "Model-sensitive and uninformative outcomes are separate from H3.",
        },
        "C05": {
            "claim_text": "Among 452 matched-input ABF H3 comparisons, 413 retained H3 and 10 changed to H4 under the multi-signal model.",
            "quantitative_anchor": "413/452 stable H3; 10/452 H3-to-H4; 6 sensitive; 23 uninformative",
            "primary_source_file": rel(ADJ / "R7B2A_642_four_arm_trajectories.tsv"),
            "supporting_source_files": rel(ADJ / "R7B2A_adjacent_transition_matrices.tsv"),
            "allowed_verbs": "retained; changed",
            "prohibited_verbs": "global absence of shared signals",
            "limitation": "H3-pair support can coexist with other shared pairs.",
        },
        "C11": {
            "supporting_source_files": rel(SIM / "R7B2A_R7B1C_discovery_vs_estimator_performance.tsv"),
            "limitation": "The unconditional rate includes credible-set discovery failure; pair-conditional results are reported separately.",
        },
        "C12": {
            "supporting_source_files": rel(SIM / "R7B2A_R7B1C_discovery_vs_estimator_performance.tsv"),
            "limitation": "Many complex shared simulations lacked an evaluable signal pair; this is not a software error.",
        },
        "C14": {
            "primary_source_file": rel(SIM / "R7B2A_R7B1C_channel_audit_state.json"),
            "supporting_source_files": "3_results/00_audit/R7B1C/R7B1C_scientific_interpretation_state.json",
            "limitation": "The mismatch branch lacks per-trait CS counts for its zero-pair fits and receives no mechanistic no-CS attribution.",
        },
        "C20": {
            "claim_text": "FCRL3-CD8_ET retained the H4-to-H3 direction after exact support and disease-statistic matching and remained a model counterexample.",
            "quantitative_anchor": "A0 H4; A1 H4; A2 H4; M H3",
            "primary_source_file": rel(ADJ / "R7B2A_historical_12_direction_changes_audit.tsv"),
            "supporting_source_files": "3_results/04_integration/R7B1E/figure_source_data/Figure5_representative_signal_axes.tsv",
            "allowed_verbs": "retained transition; illustrated",
            "prohibited_verbs": "FCRL3 was disproved in CD8 cells",
            "limitation": "The counterexample concerns signal sharing under the tested cell-QTL model.",
        },
    }
    for claim_id, fields in replacements.items():
        mask = ledger["claim_id"].eq(claim_id)
        if mask.sum() != 1:
            raise RuntimeError(f"claim replacement identity failed: {claim_id}")
        for key, value in fields.items():
            ledger.loc[mask, key] = value

    added = [
        {
            "claim_id": "C23", "manuscript_section": "Results 2", "claim_text": "Restricting ABF to the actual multi-signal support changed 15 of 642 categorical states, while all 112 historical H4 states were retained.",
            "evidence_tier": "T1_DIRECT", "status": "SUPPORTED", "quantitative_anchor": "A0-to-A1 state changes=15; historical H4 retained=112/112",
            "primary_source_file": rel(ADJ / "R7B2A_adjacent_transition_matrices.tsv"), "supporting_source_files": rel(ADJ / "R7B2A_642_four_arm_trajectories.tsv"),
            "allowed_verbs": "changed after support restriction; retained", "prohibited_verbs": "support-set mismatch was irrelevant", "limitation": "The 15 changes include H3/borderline transitions to uninformative and one ambiguity shift.", "figure": 2, "panel": "A",
        },
        {
            "claim_id": "C24", "manuscript_section": "Results 2", "claim_text": "Replacing harmonized GCST statistics with the GJOKA statistic definition changed 19 of 642 categorical states.",
            "evidence_tier": "T1_DIRECT", "status": "SUPPORTED", "quantitative_anchor": "A1-to-A2 state changes=19",
            "primary_source_file": rel(ADJ / "R7B2A_adjacent_transition_matrices.tsv"), "supporting_source_files": rel(ADJ / "R7B2A_642_four_arm_trajectories.tsv"),
            "allowed_verbs": "changed after disease-statistic matching", "prohibited_verbs": "proved dataset error", "limitation": "This contrast includes source and rounding definitions but fixed-scale primary results are insensitive to rounded BETA/SE.", "figure": 2, "panel": "B",
        },
        {
            "claim_id": "C25", "manuscript_section": "Results 2", "claim_text": "After matched inputs, 18 comparisons showed strict bidirectional H4/H3 changes between ABF and multi-signal inference.",
            "evidence_tier": "T1_DIRECT", "status": "SUPPORTED", "quantitative_anchor": "8 H4-to-H3; 10 H3-to-H4",
            "primary_source_file": rel(ADJ / "R7B2A_642_four_arm_trajectories.tsv"), "supporting_source_files": rel(ADJ / "R7B2A_attribution_summary.tsv"),
            "allowed_verbs": "persisted under matched inputs; reclassified", "prohibited_verbs": "18 corrections; method superiority", "limitation": "The comparison changes the full inference procedure and cannot isolate causal-variant count alone.", "figure": 2, "panel": "C-D",
        },
        {
            "claim_id": "C26", "manuscript_section": "Results 2", "claim_text": "No categorical result changed under native-versus-fixed sdY or matched-z-versus-rounded GJOKA sensitivity definitions.",
            "evidence_tier": "T1_SENSITIVITY", "status": "SUPPORTED", "quantitative_anchor": "A1 scale changes=0; A2 scale changes=0; A2 statistic-rounding changes=0",
            "primary_source_file": rel(ADJ / "R7B2A_attribution_state.json"), "supporting_source_files": "3_results/04_integration/R7B2A/matched_input_abf/R7B2A_matched_input_ABF_long.tsv.gz",
            "allowed_verbs": "was insensitive at the categorical threshold", "prohibited_verbs": "numerically identical; universally robust", "limitation": "This statement concerns categorical states in the frozen 642 only.", "figure": 2, "panel": "E",
        },
        {
            "claim_id": "C27", "manuscript_section": "Results 3", "claim_text": "The primary simulation had no technical errors; most non-evaluable multi-signal outcomes arose because one or both traits lacked a credible set.",
            "evidence_tier": "T2_SIMULATION_DIAGNOSTIC", "status": "SUPPORTED_BOUNDARY", "quantitative_anchor": "0 technical errors; 325,218 no-CS; 0 both-CS/no-pair; 160,782 pair-evaluable",
            "primary_source_file": rel(SIM / "R7B2A_R7B1C_channel_audit_state.json"), "supporting_source_files": rel(SIM / "R7B2A_R7B1C_channel_summary.tsv"),
            "allowed_verbs": "arose from absent credible sets; pair-evaluable", "prohibited_verbs": "all uninformative outcomes were method failures", "limitation": "The secondary mismatch branch lacks per-trait CS counts for zero-pair fits.", "figure": 3, "panel": "E-F",
        },
    ]
    ledger = pd.concat([ledger, pd.DataFrame(added, columns=ledger.columns)], ignore_index=True)
    ledger_path = OUT / "R7B2A_updated_claim_evidence_ledger.tsv"
    ledger.to_csv(ledger_path, sep="\t", index=False)

    mirror_rows = [
        ("MR01", "Freeze exact 642 comparison identities and roles before A1/A2 results.", "All 642 were retained: 184 primary, 455 H3 rescue/falsification, 3 borderline.", "V3-G0", "1A-C"),
        ("MR02", "Reconstruct original ABF support S_A and actual multi-signal support S_M.", "S_M removed 19-114 variants per comparison (median 65; median 7.67%).", "V3-G0", "2A"),
        ("MR03", "Replay A0 with the historical ABF formula and priors.", "A0 replay matched historical posteriors to maximum absolute difference 3.55e-13.", "V3-G1", "S Methods/QC"),
        ("MR04", "Run A1 on S_M with original GCST disease statistics and fixed sdY.", "A0-to-A1 yielded 15 categorical changes and retained all 112 historical H4 states.", "V3-G1-2", "2A"),
        ("MR05", "Run A2 on S_M using GJOKA matched-z disease statistics.", "A1-to-A2 yielded 19 categorical changes.", "V3-G1-2", "2B"),
        ("MR06", "Compare A2 with frozen M without refitting M.", "A2-to-M retained 79 H4 and 413 H3, with 8 H4-to-H3 and 10 H3-to-H4 strict transitions.", "V3-G4", "2C-D"),
        ("MR07", "Evaluate native sdY and rounded GJOKA BETA/SE sensitivities separately.", "No sensitivity definition changed a categorical state.", "V3-G1", "2E"),
        ("MR08", "Audit all 486,000 simulation iterations for technical error, no CS and no pair.", "Zero technical errors; 325,218 no-CS; zero both-CS/no-pair; 160,782 pair-evaluable.", "V3-G3", "3E-F"),
        ("MR09", "Report simulation decision rates both unconditionally and conditional on a signal pair.", "Pair-evaluable rates ranged from 13.29% to 59.79%; conditional H4 rates are reported as estimator behavior after discovery.", "V3-G3", "3E-F"),
        ("MR10", "Preserve external molecular-QTL and exact 5-vs-5 tissue boundaries.", "External and tissue claims remain unchanged and bounded; no new candidate was selected.", "V3-G4-5", "4-6"),
    ]
    mirror = pd.DataFrame(mirror_rows, columns=["module_id", "methods_commitment", "results_mirror", "gate", "figure_panel"])
    mirror_path = OUT / "R7B2A_methods_results_mirror.tsv"
    mirror.to_csv(mirror_path, sep="\t", index=False)

    old_manifest = pd.read_csv(R7B1E / "R7B1E_Figure1_6_panel_source_manifest.tsv", sep="\t")
    manifest = old_manifest.copy()
    f2 = manifest["figure"].eq(2) & manifest["panel"].eq("A-D")
    manifest.loc[f2, "purpose"] = "Matched-input attribution and bidirectional transition"
    manifest.loc[f2, "source_files"] = "; ".join(rel(SRC / x) for x in [
        "Figure2_adjacent_transition_matrices.tsv", "Figure2_attribution_summary.tsv", "Figure2_historical_12_direction_changes.tsv"
    ])
    manifest.loc[f2, "quantitative_anchor"] = "15 support-set; 19 disease-stat; matched-input 8 H4-to-H3 and 10 H3-to-H4"
    manifest.loc[f2, "allowed_caption"] = "input-attributed and matched-input reclassification"
    manifest.loc[f2, "prohibited_inference"] = "all historical transitions were method effects; truth-proven correction"
    f3 = manifest["figure"].eq(3)
    manifest.loc[f3, "source_files"] = "; ".join(rel(SRC / x) for x in [
        "Figure3_simulation_channel_summary.tsv", "Figure3_discovery_vs_estimator_performance.tsv"
    ])
    manifest.loc[f3, "quantitative_anchor"] = "0 technical errors; 325,218 no-CS; 160,782 pair-evaluable; scenario-dependent trade-off"
    manifest.loc[f3, "allowed_caption"] = "discovery adequacy and pair-conditional estimator behavior"
    manifest.loc[f3, "prohibited_inference"] = "uninformative equals software failure; general superiority"
    manifest_path = OUT / "R7B2A_Figure1_6_panel_source_manifest.tsv"
    manifest.to_csv(manifest_path, sep="\t", index=False)

    # Figure 2 prototype: three adjacent transition count matrices.
    state_order = ["H4", "H4_BORDERLINE", "AMBIGUOUS", "H3", "MODEL_SENSITIVE", "UNINFORMATIVE"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), constrained_layout=True)
    for ax, stage, title in zip(axes, ["A0_TO_A1_SUPPORT_SET", "A1_TO_A2_DISEASE_STATS", "A2_TO_M_MODEL"], ["Support set", "Disease statistics", "Inference model"]):
        part = transitions[transitions["transition"].eq(stage)]
        matrix = part.pivot(index="from_state", columns="to_state", values="n").fillna(0)
        rows = [x for x in state_order if x in matrix.index]
        cols = [x for x in state_order if x in matrix.columns]
        arr = matrix.reindex(index=rows, columns=cols, fill_value=0).to_numpy()
        im = ax.imshow(np.log1p(arr), cmap="Blues", aspect="auto")
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                if arr[i, j] > 0:
                    ax.text(j, i, str(int(arr[i, j])), ha="center", va="center", fontsize=8, color="black")
        ax.set_xticks(range(len(cols)), [x.replace("_", "\n") for x in cols], fontsize=7)
        ax.set_yticks(range(len(rows)), [x.replace("_", " ") for x in rows], fontsize=7)
        ax.set_xlabel("To state")
        ax.set_ylabel("From state")
        ax.set_title(title)
    fig.suptitle("R7B2A matched-input attribution across the frozen 642", fontsize=13)
    fig2_base = FIG / "R7B2A_Figure2_attribution_prototype"
    for ext in ["png", "pdf", "svg"]:
        target = fig2_base.with_suffix(f".{ext}")
        fig.savefig(target, dpi=300 if ext == "png" else None, bbox_inches="tight")
        if ext == "svg":
            target.write_text("\n".join(line.rstrip() for line in target.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)

    # Figure 3 prototype: channel composition and pair-evaluable rate.
    sc = channels[channels["scope"].eq("PRIMARY_MATCHED_BY_SCENARIO")].copy()
    channel_order = ["PAIR_H4", "PAIR_H3", "PAIR_UNINFORMATIVE", "NO_QTL_CS", "NO_DISEASE_CS", "NO_CS_BOTH"]
    pivot = sc.pivot(index="scenario", columns="matched_channel", values="rate").fillna(0)
    names = list(pivot.index)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), constrained_layout=True)
    bottom = np.zeros(len(names))
    colors = ["#2F7D32", "#B55335", "#9C9C9C", "#6E9BC5", "#E3A43B", "#C7D3DD"]
    for channel, color in zip(channel_order, colors):
        vals = pivot[channel].to_numpy() if channel in pivot.columns else np.zeros(len(names))
        axes[0].bar(range(len(names)), vals, bottom=bottom, label=channel.replace("_", " "), color=color)
        bottom += vals
    axes[0].set_xticks(range(len(names)), [n.split("_", 1)[0] for n in names])
    axes[0].set_ylim(0, 1)
    axes[0].set_ylabel("Fraction of replicates")
    axes[0].set_title("Primary matched simulation channels")
    axes[0].legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1))
    x = np.arange(len(perf))
    axes[1].bar(x - 0.18, perf["pair_evaluable_rate"], 0.36, label="Pair evaluable", color="#6E9BC5")
    axes[1].bar(x + 0.18, perf["H4_rate_unconditional"], 0.36, label="H4 unconditional", color="#2F7D32")
    axes[1].plot(x, perf["H4_rate_conditional_on_pair"], "o-", color="#7B2C8C", label="H4 | pair")
    axes[1].set_xticks(x, [s.split("_", 1)[0] for s in perf["scenario"]])
    axes[1].set_ylim(0, 1)
    axes[1].set_ylabel("Rate")
    axes[1].set_title("Discovery adequacy vs pair-conditional decision")
    axes[1].legend(fontsize=8)
    fig.suptitle("R7B2A simulation interpretability audit", fontsize=13)
    fig3_base = FIG / "R7B2A_Figure3_simulation_channels_prototype"
    for ext in ["png", "pdf", "svg"]:
        target = fig3_base.with_suffix(f".{ext}")
        fig.savefig(target, dpi=300 if ext == "png" else None, bbox_inches="tight")
        if ext == "svg":
            target.write_text("\n".join(line.rstrip() for line in target.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)

    outputs = [ledger_path, mirror_path, manifest_path, *SRC.glob("*.tsv"), *FIG.glob("R7B2A_*.*")]
    outputs = sorted(set(outputs))
    hash_path = OUT / "R7B2A_manuscript_lock_asset_hashes.tsv"
    hashes = pd.DataFrame([{"file": rel(p), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in outputs])
    hashes.to_csv(hash_path, sep="\t", index=False)
    state = {
        "schema": "R7B2A_MANUSCRIPT_LOCK_ASSETS_1.0",
        "status": "PASS",
        "gate": "V3-G5_MANUSCRIPT_LOCK_ASSETS_READY",
        "claims": len(ledger),
        "methods_results_modules": len(mirror),
        "figure_manifest_rows": len(manifest),
        "figures_1_to_6": sorted(int(x) for x in manifest["figure"].unique()),
        "new_candidate_selection": 0,
        "scope": "PBC-wide single-causal screening with matched-input, source-matched multi-signal reclassification of the prespecified high-information subset; simulation and external/tissue evidence remain bounded.",
        "outputs": {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in [ledger_path, mirror_path, manifest_path, hash_path]},
    }
    state_path = OUT / "R7B2A_manuscript_lock_state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
