#!/usr/bin/env python3
"""Validate a local FinnGen all-sex IL12RB2 regional extract.

This is a FinnGen all-sex P0 structural gate. It is deliberately separate
from H6 v2.1, which is frozen for the 2026 sex-stratified author/GWAS Catalog
input and would reject an all-sex FinnGen file by design.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from datetime import datetime, timezone
from pathlib import Path


REQUIRED = {
    "#chrom",
    "pos",
    "ref",
    "alt",
    "rsids",
    "pval",
    "beta",
    "sebeta",
    "af_alt",
    "af_alt_cases",
    "af_alt_controls",
}


def open_text(path: Path):
    if path.suffix.lower() in {".gz", ".bgz"}:
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open("r", encoding="utf-8-sig", newline="")


def finite_number(text: str) -> float:
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("non-finite numeric value")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--release", choices=("R12", "R13"), required=True)
    parser.add_argument("--endpoint", default="M13_SYSTSLCE")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    region = config["grch38_region"]
    errors: list[str] = []
    rows = 0
    positions: set[int] = set()
    anchor_rows: list[dict[str, str]] = []

    try:
        with open_text(args.input) as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            columns = reader.fieldnames or []
            missing = sorted(REQUIRED - set(columns))
            if missing:
                errors.append("missing_columns:" + ",".join(missing))
            else:
                for line_number, row in enumerate(reader, start=2):
                    rows += 1
                    try:
                        chrom = row["#chrom"].removeprefix("chr")
                        pos = int(row["pos"])
                        if chrom != region["chrom"]:
                            raise ValueError("unexpected chromosome")
                        if not region["start_1based"] <= pos <= region["end_1based"]:
                            raise ValueError("position outside frozen region")
                        ref, alt = row["ref"].upper(), row["alt"].upper()
                        if not ref or not alt or ref == alt:
                            raise ValueError("invalid alleles")
                        pval = finite_number(row["pval"])
                        finite_number(row["beta"])
                        sebeta = finite_number(row["sebeta"])
                        afs = [finite_number(row[key]) for key in ("af_alt", "af_alt_cases", "af_alt_controls")]
                        if not 0 <= pval <= 1 or sebeta <= 0 or any(not 0 <= value <= 1 for value in afs):
                            raise ValueError("numeric domain violation")
                        positions.add(pos)
                        ids = {token.strip() for token in row["rsids"].replace(";", ",").split(",")}
                        if region["anchor_rsid"] in ids:
                            anchor_rows.append(row)
                    except Exception as exc:
                        if len(errors) < 50:
                            errors.append(f"line_{line_number}:{exc}")
        if rows < 100:
            errors.append(f"insufficient_rows:{rows}<100")
        if len(positions) < 100:
            errors.append(f"insufficient_unique_positions:{len(positions)}<100")
        if positions and max(positions) - min(positions) < 250_000:
            errors.append("insufficient_span:<250000")
        exact_anchor = [
            row
            for row in anchor_rows
            if int(row["pos"]) == region["anchor_pos_1based"]
            and {row["ref"].upper(), row["alt"].upper()} == set(region["anchor_alleles_unordered"])
        ]
        if len(exact_anchor) != 1:
            errors.append(f"exact_anchor_count:{len(exact_anchor)}!=1")
    except Exception as exc:
        errors.append(f"input_open_or_parse:{type(exc).__name__}:{exc}")

    status = "PASS_REGION_STRUCTURAL_READY_FOR_HARMONIZATION" if not errors else "HOLD_REGION_STRUCTURAL_GATE_FAILED"
    result = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "input": str(args.input),
        "release": args.release,
        "endpoint": args.endpoint,
        "region": region,
        "row_count": rows,
        "unique_position_count": len(positions),
        "observed_min_pos": min(positions) if positions else None,
        "observed_max_pos": max(positions) if positions else None,
        "anchor_candidate_count": len(anchor_rows),
        "errors": errors,
        "scientific_boundary": "P0 structural readiness only; no association, fine-mapping, coloc, SMR, C1, or project status result.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "rows": rows, "errors": len(errors), "output": str(args.output)}, ensure_ascii=False))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
