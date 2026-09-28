#!/usr/bin/env python3
"""Donor-level comparison of the frozen PBC/control liver target panels.

This is a bounded supportive analysis. Marker-panel lineage gates are reused
without post-outcome tuning. It does not replace full scRNA-seq clustering.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import itertools
import json
import math
import statistics
from pathlib import Path


PBC_RUNS = [f"HRR18494{i}" for i in range(59, 64)]
CONTROL_RUNS = [f"HRR18494{i}" for i in range(54, 59)]
TARGETS = {
    "FCRL3_B": {"gate": "B_lineage_gate", "umi": "FCRL3_UMI", "gate_count": "B_gate_cells"},
    "IL12RB2_NK": {"gate": "NK_lineage_gate", "umi": "IL12RB2_UMI", "gate_count": "NK_gate_cells"},
}


def exact_label_permutation_p(case: list[float], control: list[float]) -> float:
    values = case + control
    n_case = len(case)
    observed = statistics.mean(case) - statistics.mean(control)
    extreme = 0
    total = 0
    indices = range(len(values))
    for selected in itertools.combinations(indices, n_case):
        chosen = set(selected)
        a = [value for i, value in enumerate(values) if i in chosen]
        b = [value for i, value in enumerate(values) if i not in chosen]
        statistic = statistics.mean(a) - statistics.mean(b)
        total += 1
        if abs(statistic) >= abs(observed) - 1e-15:
            extreme += 1
    return extreme / total


def read_donor(directory: Path, run: str, group: str) -> tuple[dict, dict[str, dict]]:
    summary_path = directory / f"{run}_target_panel_summary.json"
    cells_path = directory / f"{run}_target_panel_called_cells.tsv.gz"
    if not summary_path.exists() or not cells_path.exists():
        raise FileNotFoundError(f"missing summary/called-cell pair for {run}")
    summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
    if summary.get("schema_version") != "CMM_R7A1C1_TARGET_PANEL_2.0" or summary.get("technical_QC") != "PASS":
        raise RuntimeError(f"{run}: invalid target-panel schema or technical QC")
    if summary.get("run") != run:
        raise RuntimeError(f"{run}: summary run mismatch")

    aggregates = {name: {"lineage_total_umi": 0, "target_umi": 0, "gate_cells": 0, "positive_cells": 0} for name in TARGETS}
    with gzip.open(cells_path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"run", "total_gene_UMI", "B_lineage_gate", "NK_lineage_gate", "FCRL3_UMI", "IL12RB2_UMI"}
        if not required.issubset(reader.fieldnames or []):
            raise RuntimeError(f"{run}: called-cell schema is incomplete")
        for row in reader:
            if row["run"] != run:
                raise RuntimeError(f"{run}: called-cell run mismatch")
            total_umi = int(row["total_gene_UMI"])
            for name, spec in TARGETS.items():
                if row[spec["gate"]].lower() == "true":
                    value = int(row[spec["umi"]])
                    aggregates[name]["gate_cells"] += 1
                    aggregates[name]["lineage_total_umi"] += total_umi
                    aggregates[name]["target_umi"] += value
                    aggregates[name]["positive_cells"] += value > 0

    metrics: dict[str, dict] = {}
    for name, values in aggregates.items():
        expected_gate = int(summary[TARGETS[name]["gate_count"]])
        if values["gate_cells"] != expected_gate:
            raise RuntimeError(f"{run}/{name}: gate count does not reproduce summary")
        lineage_total = values["lineage_total_umi"]
        gate_cells = values["gate_cells"]
        metrics[name] = {
            **values,
            "positive_cell_fraction": values["positive_cells"] / gate_cells if gate_cells else None,
            "target_UMI_per_lineage_cell": values["target_umi"] / gate_cells if gate_cells else None,
            "target_lineage_CPM": values["target_umi"] * 1_000_000 / lineage_total if lineage_total else None,
        }
    return {
        "run": run,
        "group": group,
        "called_cells": summary["scan_qc"]["cell_call"]["called_cells"],
        "technical_QC": summary["technical_QC"],
    }, metrics


def bh_two(pvalues: dict[str, float]) -> dict[str, float]:
    ordered = sorted(pvalues, key=pvalues.get)
    adjusted: dict[str, float] = {}
    running = 1.0
    for rank_from_end, name in enumerate(reversed(ordered), 1):
        rank = len(ordered) - rank_from_end + 1
        value = min(running, pvalues[name] * len(ordered) / rank)
        adjusted[name] = value
        running = value
    return adjusted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pbc-dir", type=Path, required=True)
    parser.add_argument("--control-dir", type=Path, required=True)
    parser.add_argument("--out-prefix", type=Path, required=True)
    args = parser.parse_args()

    donors: list[dict] = []
    donor_metrics: list[dict] = []
    for group, runs, directory in (
        ("PBC", PBC_RUNS, args.pbc_dir),
        ("CONTROL_HEMANGIOMA_NONLESION", CONTROL_RUNS, args.control_dir),
    ):
        for run in runs:
            donor, metrics = read_donor(directory, run, group)
            donors.append(donor)
            for target, values in metrics.items():
                donor_metrics.append({**donor, "target_lineage": target, **values})

    comparisons: dict[str, dict] = {}
    pvalues: dict[str, float] = {}
    for target in TARGETS:
        selected = [row for row in donor_metrics if row["target_lineage"] == target]
        pbc = [row for row in selected if row["group"] == "PBC"]
        control = [row for row in selected if row["group"] != "PBC"]
        case_values = [math.log1p(row["target_lineage_CPM"]) for row in pbc]
        control_values = [math.log1p(row["target_lineage_CPM"]) for row in control]
        pvalue = exact_label_permutation_p(case_values, control_values)
        pvalues[target] = pvalue
        comparisons[target] = {
            "primary_descriptive_endpoint": "log1p(target_lineage_CPM)",
            "PBC_n": len(pbc),
            "control_n": len(control),
            "PBC_median_target_lineage_CPM": statistics.median(row["target_lineage_CPM"] for row in pbc),
            "control_median_target_lineage_CPM": statistics.median(row["target_lineage_CPM"] for row in control),
            "mean_log1p_CPM_difference_PBC_minus_control": statistics.mean(case_values) - statistics.mean(control_values),
            "exact_label_permutation_p": pvalue,
            "PBC_positive_donors": sum(row["positive_cells"] > 0 for row in pbc),
            "control_positive_donors": sum(row["positive_cells"] > 0 for row in control),
        }
    qvalues = bh_two(pvalues)
    for target in comparisons:
        comparisons[target]["BH_q_two_prespecified_targets"] = qvalues[target]

    output = {
        "schema": "R7A2A1_PBC_CONTROL_TARGET_PANEL_1.0",
        "groups": {"PBC": 5, "CONTROL_HEMANGIOMA_NONLESION": 5},
        "comparisons": comparisons,
        "interpretation_rule": "Case-control statistics are supportive because lineage gates come from a bounded marker panel. Full cell-state differential claims require full QC/reclustering and donor-level pseudobulk.",
        "status": "PASS_COMPUTED_EXACT_5_VS_5",
    }
    args.out_prefix.parent.mkdir(parents=True, exist_ok=True)
    args.out_prefix.with_suffix(".json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    columns = [
        "run", "group", "technical_QC", "called_cells", "target_lineage", "gate_cells",
        "positive_cells", "target_umi", "lineage_total_umi", "positive_cell_fraction",
        "target_UMI_per_lineage_cell", "target_lineage_CPM",
    ]
    with args.out_prefix.with_suffix(".tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(donor_metrics, key=lambda row: (row["target_lineage"], row["group"], row["run"])))
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
