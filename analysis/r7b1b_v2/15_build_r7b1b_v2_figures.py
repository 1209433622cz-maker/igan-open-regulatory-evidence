#!/usr/bin/env python3
"""Build transparent benchmark figures and source data for R7B1B v2."""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
INPUT = ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"
OUT = ROOT / "4_figures/R7B1B_v2"
SOURCE = OUT / "source_data"

ABF_ORDER = ["ABF_H4_DOMINANT", "ABF_AMBIGUOUS", "ABF_H3_DOMINANT", "ABF_H4_BORDERLINE"]
MULTI_ORDER = ["H4_SUPPORTED_STABLE", "H3_SUPPORTED_STABLE", "MODEL_SENSITIVE", "UNINFORMATIVE", "QC_FAILURE"]
ROLE_ORDER = ["PRIMARY_184_TRIGGER_VERIFICATION", "H3_RESCUE_FALSIFICATION", "BORDERLINE_HIGH_INFORMATION_CALIBRATION"]
COLORS = {
    "H4_SUPPORTED_STABLE": "#0072B2",
    "H3_SUPPORTED_STABLE": "#D55E00",
    "MODEL_SENSITIVE": "#E69F00",
    "UNINFORMATIVE": "#999999",
    "QC_FAILURE": "#000000",
}


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(OUT / f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SOURCE.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(INPUT, sep="\t")
    if len(d) != 642:
        raise RuntimeError("expected exact 642-row adjudication")

    matrix = pd.crosstab(d.ABF_state, d.PF10_multisignal_state).reindex(index=ABF_ORDER, columns=MULTI_ORDER, fill_value=0)
    matrix.to_csv(SOURCE / "Figure_R7B1B_1_ABF_to_multisignal_matrix.tsv", sep="\t")
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    im = ax.imshow(matrix.to_numpy(), cmap="Blues", aspect="auto")
    for i in range(matrix.shape[0]):
        row_n = matrix.iloc[i].sum()
        for j in range(matrix.shape[1]):
            n = int(matrix.iloc[i, j])
            pct = 100 * n / row_n if row_n else 0
            ax.text(j, i, f"{n}\n({pct:.1f}%)", ha="center", va="center", fontsize=9,
                    color="white" if im.norm(n) > 0.55 else "black")
    ax.set_xticks(range(len(matrix.columns)), [x.replace("_", "\n") for x in matrix.columns], fontsize=8)
    ax.set_yticks(range(len(matrix.index)), [x.replace("_", " ") for x in matrix.index], fontsize=9)
    ax.set_xlabel("Source-matched PF10 multi-signal state")
    ax.set_ylabel("Single-causal ABF screening state")
    ax.set_title("Bidirectional reclassification of the prespecified high-information subset")
    fig.colorbar(im, ax=ax, label="Comparisons", fraction=0.035, pad=0.03)
    save(fig, "Figure_R7B1B_1_bidirectional_reclassification")

    role = pd.crosstab(d.R7B1B_v2_role, d.PF10_multisignal_state).reindex(index=ROLE_ORDER, columns=MULTI_ORDER, fill_value=0)
    role.to_csv(SOURCE / "Figure_R7B1B_2_role_state_counts.tsv", sep="\t")
    fig, ax = plt.subplots(figsize=(9.2, 4.5))
    left = np.zeros(len(role))
    for state in MULTI_ORDER:
        values = role[state].to_numpy()
        ax.barh(range(len(role)), values, left=left, color=COLORS[state], label=state.replace("_", " "))
        for i, (v, start) in enumerate(zip(values, left)):
            if v >= 3:
                ax.text(start + v / 2, i, str(int(v)), ha="center", va="center", fontsize=8,
                        color="white" if state in {"H4_SUPPORTED_STABLE", "H3_SUPPORTED_STABLE", "QC_FAILURE"} else "black")
        left += values
    ax.set_yticks(range(len(role)), [x.replace("_", " ") for x in role.index], fontsize=8)
    ax.set_xlabel("Comparisons")
    ax.set_title("Primary verification and symmetric falsification cohorts remain separate")
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="lower right")
    save(fig, "Figure_R7B1B_2_cohort_separated_outcomes")

    focus = d[d.reclassification.isin(["STABLE_H4", "H4_TO_H3", "H3_TO_H4", "STABLE_H3"])].copy()
    cell = pd.crosstab(focus.cell_type, focus.reclassification).reindex(
        columns=["STABLE_H4", "H4_TO_H3", "H3_TO_H4", "STABLE_H3"], fill_value=0
    ).sort_values(["H3_TO_H4", "STABLE_H4"], ascending=False)
    cell.to_csv(SOURCE / "Figure_R7B1B_3_cell_reclassification_counts.tsv", sep="\t")
    fig, ax = plt.subplots(figsize=(9.2, max(4.5, 0.36 * len(cell) + 1.5)))
    y = np.arange(len(cell)); width = 0.19
    palette = {"STABLE_H4": "#0072B2", "H4_TO_H3": "#CC79A7", "H3_TO_H4": "#009E73", "STABLE_H3": "#D55E00"}
    for k, state in enumerate(cell.columns):
        ax.barh(y + (k - 1.5) * width, cell[state], height=width, color=palette[state], label=state.replace("_", " "))
    ax.set_yticks(y, cell.index)
    ax.invert_yaxis()
    ax.set_xlabel("Comparisons")
    ax.set_title("Cell-context distribution of stable and reclassified comparisons")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    save(fig, "Figure_R7B1B_3_cell_context_reclassification")

    state = {
        "schema": "R7B1B_V2_FIGURE_ASSEMBLY_1.0",
        "status": "PASS",
        "input_rows": len(d),
        "figures": 3,
        "formats": ["png_300dpi", "pdf_vector"],
        "claim_ceiling": "prespecified high-information H3/H4 subset",
    }
    (OUT / "figure_assembly_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
