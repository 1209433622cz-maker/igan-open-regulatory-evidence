#!/usr/bin/env python3
"""Predefined donor-level sensitivity summaries for the R7A2A1 marker panel."""
from __future__ import annotations

import csv
import itertools
import json
import math
import statistics
import sys
from pathlib import Path


METRICS = {
    "primary_log1p_target_lineage_CPM": ("target_lineage_CPM", lambda x: math.log1p(x)),
    "positive_cell_fraction": ("positive_cell_fraction", lambda x: x),
    "log1p_target_UMI_per_lineage_cell": ("target_UMI_per_lineage_cell", lambda x: math.log1p(x)),
}


def exact_p(a: list[float], b: list[float]) -> float:
    values = a + b
    observed = statistics.mean(a) - statistics.mean(b)
    total = extreme = 0
    for selected in itertools.combinations(range(len(values)), len(a)):
        selected = set(selected)
        x = [v for i, v in enumerate(values) if i in selected]
        y = [v for i, v in enumerate(values) if i not in selected]
        total += 1
        extreme += abs(statistics.mean(x) - statistics.mean(y)) >= abs(observed) - 1e-15
    return extreme / total


def bh_two(pvalues: dict[str, float]) -> dict[str, float]:
    ordered = sorted(pvalues, key=pvalues.get)
    adjusted: dict[str, float] = {}
    running = 1.0
    for reverse_rank, name in enumerate(reversed(ordered), 1):
        rank = len(ordered) - reverse_rank + 1
        running = min(running, pvalues[name] * len(ordered) / rank)
        adjusted[name] = running
    return adjusted


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else r"H:\SCI2\YR1")
    source = root / "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel.tsv"
    out_json = root / "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel_sensitivity.json"
    out_tsv = root / "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel_sensitivity.tsv"
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    targets = sorted({row["target_lineage"] for row in rows})
    results: list[dict] = []
    for metric_name, (column, transform) in METRICS.items():
        pvalues: dict[str, float] = {}
        pending: dict[str, dict] = {}
        for target in targets:
            target_rows = [r for r in rows if r["target_lineage"] == target]
            pbc = [(r["run"], transform(float(r[column]))) for r in target_rows if r["group"] == "PBC"]
            control = [(r["run"], transform(float(r[column]))) for r in target_rows if r["group"] != "PBC"]
            pbc_values = [v for _, v in pbc]
            control_values = [v for _, v in control]
            difference = statistics.mean(pbc_values) - statistics.mean(control_values)
            pvalue = exact_p(pbc_values, control_values)
            pvalues[target] = pvalue
            loo_effects = []
            for run, _ in pbc + control:
                a = [v for r, v in pbc if r != run]
                b = [v for r, v in control if r != run]
                loo_effects.append(statistics.mean(a) - statistics.mean(b))
            same_direction = sum((value > 0) == (difference > 0) for value in loo_effects)
            pending[target] = {
                "metric": metric_name,
                "target_lineage": target,
                "PBC_n": len(pbc),
                "control_n": len(control),
                "PBC_median_untransformed": statistics.median(float(r[column]) for r in target_rows if r["group"] == "PBC"),
                "control_median_untransformed": statistics.median(float(r[column]) for r in target_rows if r["group"] != "PBC"),
                "mean_transformed_difference_PBC_minus_control": difference,
                "exact_label_permutation_p": pvalue,
                "leave_one_donor_out_same_direction": same_direction,
                "leave_one_donor_out_total": len(loo_effects),
                "leave_one_donor_out_min_effect": min(loo_effects),
                "leave_one_donor_out_max_effect": max(loo_effects),
            }
        qvalues = bh_two(pvalues)
        for target in targets:
            pending[target]["BH_q_two_prespecified_targets"] = qvalues[target]
            results.append(pending[target])
    output = {
        "schema": "R7A2A1_DONOR_LEVEL_SENSITIVITY_1.0",
        "scope": "supportive sensitivity only; primary endpoint remains log1p target-lineage CPM",
        "multiple_testing": "BH within each metric across the two prespecified targets",
        "results": results,
        "status": "PASS_COMPUTED",
    }
    out_json.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    columns = list(results[0])
    with out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

