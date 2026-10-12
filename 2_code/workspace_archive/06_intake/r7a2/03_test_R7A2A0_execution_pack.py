#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def find_project_root() -> Path:
    configured = os.environ.get("R7_PROJECT_ROOT")
    if configured:
        return Path(configured)
    for parent in Path(__file__).resolve().parents:
        if (parent / "README_WORKSPACE.md").exists() or (parent / ".git").exists():
            return parent
    return Path(__file__).resolve().parents[3]


ROOT = find_project_root()
COMPARE = Path(__file__).with_name("02_compare_PBC_control_target_panel.py")
OUT = ROOT / "3_results/00_audit/R7A2A0_execution_pack_tests.json"
PBC_RUNS = [f"HRR18494{i}" for i in range(59, 64)]
CONTROL_RUNS = [f"HRR18494{i}" for i in range(54, 59)]


def write_donor(directory: Path, run: str, scale: int) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    rows = [
        {"run": run, "cell_barcode": "B1", "total_gene_UMI": 1000, "B_lineage_gate": True, "NK_lineage_gate": False, "FCRL3_UMI": scale, "IL12RB2_UMI": 0},
        {"run": run, "cell_barcode": "B2", "total_gene_UMI": 1000, "B_lineage_gate": True, "NK_lineage_gate": False, "FCRL3_UMI": scale, "IL12RB2_UMI": 0},
        {"run": run, "cell_barcode": "N1", "total_gene_UMI": 1000, "B_lineage_gate": False, "NK_lineage_gate": True, "FCRL3_UMI": 0, "IL12RB2_UMI": scale},
        {"run": run, "cell_barcode": "N2", "total_gene_UMI": 1000, "B_lineage_gate": False, "NK_lineage_gate": True, "FCRL3_UMI": 0, "IL12RB2_UMI": scale},
    ]
    columns = ["run", "cell_barcode", "total_gene_UMI", "B_lineage_gate", "NK_lineage_gate", "FCRL3_UMI", "IL12RB2_UMI"]
    with gzip.open(directory / f"{run}_target_panel_called_cells.tsv.gz", "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "schema_version": "CMM_R7A1C1_TARGET_PANEL_2.0", "run": run, "technical_QC": "PASS",
        "B_gate_cells": 2, "NK_gate_cells": 2, "scan_qc": {"cell_call": {"called_cells": 4}},
    }
    (directory / f"{run}_target_panel_summary.json").write_text(json.dumps(summary), encoding="utf-8")


checks = []
with tempfile.TemporaryDirectory() as temp:
    temp_path = Path(temp)
    pbc = temp_path / "pbc"
    control = temp_path / "control"
    for run in PBC_RUNS:
        write_donor(pbc, run, 4)
    for run in CONTROL_RUNS:
        write_donor(control, run, 1)
    prefix = temp_path / "comparison"
    result = subprocess.run(
        [sys.executable, str(COMPARE), "--pbc-dir", str(pbc), "--control-dir", str(control), "--out-prefix", str(prefix)],
        capture_output=True, text=True,
    )
    value = json.loads(prefix.with_suffix(".json").read_text(encoding="utf-8")) if result.returncode == 0 else {}
    checks.append({"name": "synthetic_exact_5_vs_5", "pass": result.returncode == 0 and value.get("status") == "PASS_COMPUTED_EXACT_5_VS_5"})
    checks.append({"name": "two_targets", "pass": set(value.get("comparisons", {})) == {"FCRL3_B", "IL12RB2_NK"}})
    checks.append({"name": "known_direction", "pass": all(x.get("mean_log1p_CPM_difference_PBC_minus_control", 0) > 0 for x in value.get("comparisons", {}).values())})
    checks.append({"name": "exact_permutation_minimum", "pass": all(abs(x.get("exact_label_permutation_p", 1) - 2/252) < 1e-12 for x in value.get("comparisons", {}).values())})

output = {
    "schema": "R7A2A0_EXECUTION_PACK_TESTS_1.0",
    "passed": sum(row["pass"] for row in checks),
    "total": len(checks),
    "checks": checks,
    "status": "PASS" if all(row["pass"] for row in checks) else "FAIL",
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
print(json.dumps(output, indent=2))
raise SystemExit(0 if output["status"] == "PASS" else 2)
