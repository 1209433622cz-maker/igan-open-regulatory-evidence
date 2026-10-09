#!/usr/bin/env python3
"""Freeze the R7B1D external-replication targets before new API adjudication."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
ADJ = ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"
R7B0_MAP = ROOT / "github/igan-open-regulatory-evidence/environment/R7B0/R7B0_FinnGen_FCRL3_IL12RB2_feasibility.tsv"
OUT = ROOT / "3_results/04_integration/R7B1D"


TARGETS = [
    {
        "comparison_id": "R7B1_000258",
        "role": "POSITIVE_ANCHOR",
        "axis": "IL12RB2–NK",
        "FinnGen_primary": "l2.NK",
        "FinnGen_compatible": "l1.NK;l1.PBMC",
        "TenK_cell": "NK",
        "external_question": "Does the stable OneK signal recur in TenK and in a FinnGen PBC–IL12RB2 molecular/multiome layer?",
    },
    {
        "comparison_id": "R7B1_000410",
        "role": "POSITIVE_ANCHOR",
        "axis": "FCRL3–B_IN",
        "FinnGen_primary": "l2.B_intermediate",
        "FinnGen_compatible": "l1.B",
        "TenK_cell": "B_intermediate",
        "external_question": "Does the stable OneK B-cell signal recur in TenK and have FinnGen PBC disease-coloc support?",
    },
    {
        "comparison_id": "R7B1_000411",
        "role": "POSITIVE_ANCHOR",
        "axis": "FCRL3–B_MEM",
        "FinnGen_primary": "l2.B_memory",
        "FinnGen_compatible": "l1.B",
        "TenK_cell": "B_intermediate",
        "external_question": "Is the stable OneK memory-B assignment covered at exact or coarse B-cell resolution externally?",
    },
    {
        "comparison_id": "R7B1_000414",
        "role": "FALSIFICATION_ANCHOR",
        "axis": "FCRL3–CD8_ET",
        "FinnGen_primary": "l2.CD8_TEM",
        "FinnGen_compatible": "l1.CD8_T",
        "TenK_cell": "NA",
        "external_question": "Does any public external PBC evidence justify reversing the source-matched H4-to-H3 adjudication?",
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    adj = pd.read_csv(ADJ, sep="\t")
    frozen = pd.DataFrame(TARGETS)
    merged = frozen.merge(adj, on="comparison_id", how="left", validate="one_to_one")
    if merged["gene"].isna().any():
        raise RuntimeError("At least one prespecified comparison is absent from the frozen R7B1B table")
    expected = {
        "R7B1_000258": ("IL12RB2", "NK", "H4_SUPPORTED_STABLE"),
        "R7B1_000410": ("FCRL3", "B_IN", "H4_SUPPORTED_STABLE"),
        "R7B1_000411": ("FCRL3", "B_MEM", "H4_SUPPORTED_STABLE"),
        "R7B1_000414": ("FCRL3", "CD8_ET", "H3_SUPPORTED_STABLE"),
    }
    for row in merged.itertuples(index=False):
        gene, cell, state = expected[row.comparison_id]
        if (row.gene, row.cell_type, row.PF10_multisignal_state) != (gene, cell, state):
            raise RuntimeError(f"Frozen R7B1B identity drift: {row.comparison_id}")

    r7b0 = pd.read_csv(R7B0_MAP, sep="\t")
    for row in merged.itertuples(index=False):
        if row.role == "FALSIFICATION_ANCHOR":
            # R7B0 froze B/NK positive-axis mappings. CD8_ET is retained only as
            # the already-prespecified negative exemplar and is never promoted.
            continue
        available = set(r7b0.loc[(r7b0.gene == row.gene) & (r7b0.OneK_cell == row.cell_type), "FinnGen_primary_level2"])
        normalized = row.FinnGen_primary.removeprefix("l2.")
        if normalized not in available:
            raise RuntimeError(f"R7B0 cell-map mismatch: {row.comparison_id}")

    keep = [
        "comparison_id", "role", "axis", "gene", "cell_type", "ABF_classification",
        "PF10_multisignal_state", "reclassification", "PF10_PF50_sensitivity",
        "pf10_l10_best_h4", "pf50_l10_best_h4", "FinnGen_primary",
        "FinnGen_compatible", "TenK_cell", "external_question",
    ]
    registry = merged[keep].copy()
    registry_path = OUT / "R7B1D_external_target_registry.tsv"
    registry.to_csv(registry_path, sep="\t", index=False)

    state = {
        "schema": "R7B1D_TARGET_FREEZE_1.0",
        "status": "PASS",
        "selection_timing": "Targets inherited from prespecified R7B1B anchors before current R7B1D API adjudication",
        "new_candidate_selection": False,
        "targets": len(registry),
        "positive_anchors": int((registry.role == "POSITIVE_ANCHOR").sum()),
        "falsification_anchors": int((registry.role == "FALSIFICATION_ANCHOR").sum()),
        "r7b1b_adjudication_sha256": sha256(ADJ),
        "r7b0_cell_mapping_sha256": sha256(R7B0_MAP),
        "target_registry_sha256": sha256(registry_path),
        "hard_boundaries": [
            "FinnGen non-return is a public-output coverage result, not proof of biological absence",
            "TenK reuses the GJOKA disease GWAS and is molecular-QTL replication only",
            "Direction requires exact allele harmonization at the same variant",
            "Positional CASCADE evidence is not a complete disease-to-caQTL-to-expression causal chain",
            "No additional OneK gene, locus or cell may be selected in R7B1D",
        ],
    }
    (OUT / "R7B1D_target_freeze_state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
