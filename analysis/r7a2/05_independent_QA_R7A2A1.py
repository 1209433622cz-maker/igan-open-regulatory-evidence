#!/usr/bin/env python3
"""Independent closeout audit for the exact 5 PBC vs 5 control tissue gate."""
from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path


PBC_RUNS = [f"HRR18494{i}" for i in range(59, 64)]
CONTROL_RUNS = [f"HRR18494{i}" for i in range(54, 59)]
TARGETS = {
    "FCRL3_B": ("B_lineage_gate", "FCRL3_UMI", "B_gate_cells"),
    "IL12RB2_NK": ("NK_lineage_gate", "IL12RB2_UMI", "NK_gate_cells"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_p(case: list[float], control: list[float]) -> float:
    values = case + control
    observed = statistics.mean(case) - statistics.mean(control)
    extreme = total = 0
    for selected in itertools.combinations(range(len(values)), len(case)):
        chosen = set(selected)
        a = [v for i, v in enumerate(values) if i in chosen]
        b = [v for i, v in enumerate(values) if i not in chosen]
        statistic = statistics.mean(a) - statistics.mean(b)
        total += 1
        extreme += abs(statistic) >= abs(observed) - 1e-15
    return extreme / total


def independently_aggregate(cells_path: Path, run: str) -> dict[str, dict[str, float | int]]:
    out = {
        target: {"gate_cells": 0, "positive_cells": 0, "target_umi": 0, "lineage_total_umi": 0}
        for target in TARGETS
    }
    with gzip.open(cells_path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {
            "run", "total_gene_UMI", "B_lineage_gate", "NK_lineage_gate",
            "FCRL3_UMI", "IL12RB2_UMI",
        }
        if not required.issubset(reader.fieldnames or []):
            raise RuntimeError(f"{run}: incomplete called-cell schema")
        for row in reader:
            if row["run"] != run:
                raise RuntimeError(f"{run}: mixed run identifiers in called-cell table")
            total = int(row["total_gene_UMI"])
            for target, (gate_col, umi_col, _) in TARGETS.items():
                if row[gate_col].lower() == "true":
                    umi = int(row[umi_col])
                    out[target]["gate_cells"] += 1
                    out[target]["positive_cells"] += int(umi > 0)
                    out[target]["target_umi"] += umi
                    out[target]["lineage_total_umi"] += total
    for values in out.values():
        gate = int(values["gate_cells"])
        total = int(values["lineage_total_umi"])
        values["positive_cell_fraction"] = values["positive_cells"] / gate
        values["target_UMI_per_lineage_cell"] = values["target_umi"] / gate
        values["target_lineage_CPM"] = values["target_umi"] * 1_000_000 / total
    return out


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tolerance, abs_tol=tolerance)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else r"H:\SCI2\YR1")
    code = root / "2_code/06_intake/r7a2"
    pbc_dir = root / "3_results/05_tissue/R7A1C1"
    control_dir = root / "3_results/05_tissue/R7A2A1_control"
    audit_dir = root / "3_results/00_audit/R7A2A1"
    audit_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "1_data/scrna/PBC/HRA008003/manifests/HRA008003_control_liver_primary_run_manifest_v1.tsv"
    receipt_path = audit_dir / "R7A2A1_HRA008003_control_receipts.tsv"
    official_prefix = control_dir / "PBC_vs_control_target_panel"
    rerun_prefix = audit_dir / "R7A2A1_independent_comparison"
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    manifest_rows = read_tsv(manifest_path)
    manifest = {row["run_accession"]: row for row in manifest_rows}
    check("exact_five_control_manifest", sorted(manifest) == CONTROL_RUNS and len(manifest_rows) == 5,
          {"runs": sorted(manifest), "total_expected_bytes": sum(int(r["expected_bytes"]) for r in manifest_rows)})

    receipt_rows = read_tsv(receipt_path)
    receipts = {row["run"]: row for row in receipt_rows}
    check("exact_five_unique_control_receipts", sorted(receipts) == CONTROL_RUNS and len(receipt_rows) == 5,
          {"runs": sorted(receipts), "rows": len(receipt_rows)})

    official_rows = read_tsv(official_prefix.with_suffix(".tsv"))
    official_index = {(row["run"], row["target_lineage"]): row for row in official_rows}
    independently_rebuilt: list[dict] = []
    per_run: dict[str, dict] = {}

    for run in CONTROL_RUNS:
        summary_path = control_dir / f"{run}_target_panel_summary.json"
        cells_path = control_dir / f"{run}_target_panel_called_cells.tsv.gz"
        hash_path = audit_dir / f"{run}.hashes.json"
        schema_path = audit_dir / f"{run}.bam_schema_preflight_v1_2.json"
        resume_path = audit_dir / f"{run}.resume_validation.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
        hashes = json.loads(hash_path.read_text(encoding="utf-8-sig"))
        schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
        resume = json.loads(resume_path.read_text(encoding="utf-8-sig"))
        m = manifest[run]
        r = receipts[run]
        identity_ok = all([
            summary["schema_version"] == "CMM_R7A1C1_TARGET_PANEL_2.0",
            summary["technical_QC"] == "PASS",
            summary["run"] == run,
            int(summary["bam_bytes"]) == int(m["expected_bytes"]) == int(r["bytes"]) == int(hashes["bytes"]),
            summary["bam_sha256"] == r["sha256"] == hashes["sha256"],
            m["official_md5"] == r["official_md5"] == r["observed_md5"] == hashes["md5"],
            r["status"] == "PASS_TARGET_PANEL_V2_CONTROL",
            r["bam_deleted"].lower() == "true",
            schema["schema_valid"] is True and schema["status"].startswith("PASS"),
            resume["status"] == "PASS_VALID_SUMMARY_AND_RECEIPT" and not resume["errors"],
        ])
        rebuilt = independently_aggregate(cells_path, run)
        aggregate_ok = True
        for target, (_, _, gate_count) in TARGETS.items():
            row = official_index[(run, target)]
            values = rebuilt[target]
            aggregate_ok &= int(values["gate_cells"]) == int(summary[gate_count]) == int(row["gate_cells"])
            aggregate_ok &= int(values["positive_cells"]) == int(row["positive_cells"])
            aggregate_ok &= int(values["target_umi"]) == int(row["target_umi"])
            aggregate_ok &= int(values["lineage_total_umi"]) == int(row["lineage_total_umi"])
            for metric in ("positive_cell_fraction", "target_UMI_per_lineage_cell", "target_lineage_CPM"):
                aggregate_ok &= close(float(values[metric]), float(row[metric]))
            independently_rebuilt.append({"run": run, "group": row["group"], "target": target, **values})
        per_run[run] = {
            "identity": identity_ok,
            "called_cell_aggregation": bool(aggregate_ok),
            "bytes": int(summary["bam_bytes"]),
            "sha256": summary["bam_sha256"],
            "called_cells": int(summary["scan_qc"]["cell_call"]["called_cells"]),
            "schema_status": schema["status"],
        }
        check(f"{run}_byte_schema_receipt_summary_identity", identity_ok, per_run[run])
        check(f"{run}_called_cell_reaggregation", aggregate_ok,
              {t: {k: v for k, v in rebuilt[t].items() if k in ("gate_cells", "positive_cells", "target_umi", "target_lineage_CPM")} for t in TARGETS})

    pbc_pairs = all((pbc_dir / f"{run}_target_panel_summary.json").exists() and
                    (pbc_dir / f"{run}_target_panel_called_cells.tsv.gz").exists() for run in PBC_RUNS)
    check("exact_five_pbc_compact_pairs_present", pbc_pairs, {"runs": PBC_RUNS})
    pbc_reaggregation_ok = pbc_pairs
    if pbc_pairs:
        for run in PBC_RUNS:
            summary = json.loads((pbc_dir / f"{run}_target_panel_summary.json").read_text(encoding="utf-8-sig"))
            rebuilt = independently_aggregate(pbc_dir / f"{run}_target_panel_called_cells.tsv.gz", run)
            for target, (_, _, gate_count) in TARGETS.items():
                row = official_index[(run, target)]
                values = rebuilt[target]
                pbc_reaggregation_ok &= int(values["gate_cells"]) == int(summary[gate_count]) == int(row["gate_cells"])
                pbc_reaggregation_ok &= int(values["positive_cells"]) == int(row["positive_cells"])
                pbc_reaggregation_ok &= int(values["target_umi"]) == int(row["target_umi"])
                pbc_reaggregation_ok &= int(values["lineage_total_umi"]) == int(row["lineage_total_umi"])
                for metric in ("positive_cell_fraction", "target_UMI_per_lineage_cell", "target_lineage_CPM"):
                    pbc_reaggregation_ok &= close(float(values[metric]), float(row[metric]))
                independently_rebuilt.append({"run": run, "group": row["group"], "target": target, **values})
    check("five_pbc_called_cell_reaggregation", pbc_reaggregation_ok, {"runs": PBC_RUNS})
    residual_bams = sorted(p.name for p in (root / "1_data/scrna/PBC/HRA008003/bam_control").glob("*"))
    check("control_bam_cache_empty", not residual_bams, {"residual_files": residual_bams})

    subprocess.run([
        sys.executable, str(code / "02_compare_PBC_control_target_panel.py"),
        "--pbc-dir", str(pbc_dir), "--control-dir", str(control_dir), "--out-prefix", str(rerun_prefix),
    ], check=True, capture_output=True, text=True)
    official_json = json.loads(official_prefix.with_suffix(".json").read_text(encoding="utf-8-sig"))
    rerun_json = json.loads(rerun_prefix.with_suffix(".json").read_text(encoding="utf-8-sig"))
    check("frozen_comparator_json_exact_reproduction", official_json == rerun_json,
          {"official_sha256": sha256(official_prefix.with_suffix(".json")), "rerun_sha256": sha256(rerun_prefix.with_suffix(".json"))})
    check("frozen_comparator_tsv_byte_reproduction",
          official_prefix.with_suffix(".tsv").read_bytes() == rerun_prefix.with_suffix(".tsv").read_bytes(),
          {"official_sha256": sha256(official_prefix.with_suffix(".tsv")), "rerun_sha256": sha256(rerun_prefix.with_suffix(".tsv"))})

    independent_stats: dict[str, dict] = {}
    stats_ok = True
    for target in TARGETS:
        selected = [row for row in independently_rebuilt if row["target"] == target]
        case = [math.log1p(float(row["target_lineage_CPM"])) for row in selected if row["group"] == "PBC"]
        control = [math.log1p(float(row["target_lineage_CPM"])) for row in selected if row["group"] != "PBC"]
        p = exact_p(case, control)
        effect = statistics.mean(case) - statistics.mean(control)
        expected = official_json["comparisons"][target]
        ok = close(p, expected["exact_label_permutation_p"]) and close(effect, expected["mean_log1p_CPM_difference_PBC_minus_control"])
        stats_ok &= ok
        independent_stats[target] = {"mean_log1p_CPM_difference": effect, "exact_permutation_p": p, "match": ok}
    check("independent_exact_permutation_recalculation", stats_ok, independent_stats)

    frozen_files = [
        root / "2_code/06_intake/r7a1c1/02_hra_bam_target_panel_v2.py",
        code / "02_compare_PBC_control_target_panel.py",
        code / "RUN_R7A2A1_HRA008003_CONTROL_TARGET_PANEL_HARDENED.ps1",
    ]
    check("frozen_analysis_files_present_and_hashed", all(p.exists() for p in frozen_files),
          {str(p.relative_to(root)): sha256(p) for p in frozen_files})

    failures = [row for row in checks if not row["pass"]]
    result = {
        "schema": "R7A2A1_INDEPENDENT_QA_1.0",
        "status": "PASS" if not failures else "FAIL",
        "checks_passed": len(checks) - len(failures),
        "checks_total": len(checks),
        "checks": checks,
        "per_control_run": per_run,
        "independent_statistics": independent_stats,
        "conclusion": (
            "Exact five-control bytes, compact artifacts and 5-vs-5 statistics close independently."
            if not failures else "One or more closeout checks failed."
        ),
    }
    out = audit_dir / "R7A2A1_independent_QA.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
