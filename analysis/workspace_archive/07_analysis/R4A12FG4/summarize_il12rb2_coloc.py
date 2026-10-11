#!/usr/bin/env python3
"""Classify R12/R13 coloc.abf sensitivity outputs under frozen thresholds."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 3:
        raise RuntimeError(f"expected three p12 rows in {path}, found {len(rows)}")
    for row in rows:
        for key in ("p12", "PP.H3", "PP.H4", "H4_over_H3H4"):
            row[key] = float(row[key])
    return rows


def classify(rows: list[dict]) -> dict:
    primary = next(row for row in rows if abs(row["p12"] - 1e-5) < 1e-12)
    strong = (
        primary["PP.H4"] >= 0.80
        and primary["H4_over_H3H4"] >= 0.90
        and all(row["PP.H4"] >= 0.50 and row["H4_over_H3H4"] >= 0.80 for row in rows)
    )
    distinct = all(row["PP.H3"] >= 0.80 and row["H4_over_H3H4"] < 0.20 for row in rows)
    if strong:
        label = "STRONG_SINGLE_CAUSAL_SENSITIVITY_WORTH_LD_AWARE_TEST"
    elif distinct:
        label = "DISTINCT_UNDER_SINGLE_CAUSAL_SENSITIVITY_MULTI_SIGNAL_STILL_REQUIRED"
    else:
        label = "AMBIGUOUS_SINGLE_CAUSAL_SENSITIVITY"
    return {"classification": label, "primary_p12_1e_5": primary, "all_priors": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r12", type=Path, required=True)
    parser.add_argument("--r13", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema_version": "CMM_R4A12FG4_COLOC_ABF_SENSITIVITY_1.0",
        "method_role": "POST_EXACT_COVERAGE_GATE_SINGLE_CAUSAL_DIAGNOSTIC_ONLY",
        "coverage_gate": "HOLD_EXACT_COVERAGE; run retained only because the missing high-PIP variant has an r2=1.0 external-EUR proxy among exact overlaps",
        "cannot_satisfy_C1": True,
        "R12": classify(load(args.r12)),
        "R13": classify(load(args.r13)),
        "release_dependence": "R12 and R13 overlap heavily and are not independent replication cohorts.",
        "multi_signal_status": "HOLD_LD_GATE",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"R12": result["R12"]["classification"], "R13": result["R13"]["classification"], "out": str(args.out)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
