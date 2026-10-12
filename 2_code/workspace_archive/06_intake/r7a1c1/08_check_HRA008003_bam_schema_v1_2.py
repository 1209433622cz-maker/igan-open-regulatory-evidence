#!/usr/bin/env python3
"""Outcome-blind schema audit for a fully downloaded HRA008003 BAM.

This audit establishes that the coordinate-sorted BAM can be interpreted as
Cell Ranger molecule-tagged data.  It intentionally does not use the density
of molecule representatives in a genomic prefix as a quantitative adequacy
gate.  Molecule abundance, cell calling, lineage adequacy and target
detectability are evaluated by the frozen full-file target-panel scan.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import pysam


def nonempty_tag(record: pysam.AlignedSegment, tag: str) -> bool:
    if not record.has_tag(tag):
        return False
    value = record.get_tag(tag)
    return value is not None and str(value).strip() != ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bam", type=Path, required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--min-records", type=int, default=500_000)
    parser.add_argument("--max-records", type=int, default=5_000_000)
    parser.add_argument("--target-xf8", type=int, default=1_000)
    parser.add_argument(
        "--allow-truncated-test",
        action="store_true",
        help="QA only: permit a deliberately truncated BAM; production never sets this",
    )
    args = parser.parse_args()
    if not 0 < args.min_records <= args.max_records:
        raise ValueError("require 0 < min-records <= max-records")
    if args.target_xf8 < 1:
        raise ValueError("target-xf8 must be >=1")

    counts: collections.Counter[str] = collections.Counter()
    examples: list[dict] = []
    errors: list[str] = []
    warnings: list[str] = []
    header: dict = {}
    program_header: list[dict] = []

    try:
        with pysam.AlignmentFile(
            str(args.bam),
            "rb",
            check_sq=False,
            ignore_truncation=args.allow_truncated_test,
        ) as bam:
            header = bam.header.to_dict()
            program_header = header.get("PG", [])
            for index, record in enumerate(bam.fetch(until_eof=True), start=1):
                counts["records"] += 1
                if record.has_tag("xf"):
                    counts["has_xf"] += 1
                    try:
                        xf = int(record.get_tag("xf"))
                    except Exception:
                        counts["bad_xf"] += 1
                        xf = 0
                    if xf & 8:
                        counts["xf8"] += 1
                        for tag in ("CB", "GN", "UB"):
                            if nonempty_tag(record, tag):
                                counts[f"xf8_{tag}"] += 1
                            else:
                                counts[f"xf8_missing_or_empty_{tag}"] += 1
                        if nonempty_tag(record, "GN"):
                            gene = str(record.get_tag("GN"))
                            if ";" not in gene:
                                counts["xf8_unambiguous_GN"] += 1
                        if len(examples) < 5:
                            examples.append(
                                {
                                    "CB": record.get_tag("CB") if record.has_tag("CB") else None,
                                    "GN": record.get_tag("GN") if record.has_tag("GN") else None,
                                    "UB": record.get_tag("UB") if record.has_tag("UB") else None,
                                    "xf": xf,
                                }
                            )
                if index >= args.min_records and counts["xf8"] >= args.target_xf8:
                    break
                if index >= args.max_records:
                    break
    except Exception as exc:  # keep a machine-readable failure receipt
        errors.append(f"input_read_error:{type(exc).__name__}:{exc}")

    records = counts["records"]
    xf8 = counts["xf8"]
    if records < args.min_records:
        errors.append(f"too few records inspected: {records} < {args.min_records}")
    if counts["bad_xf"]:
        errors.append(f"non-integer xf values observed: {counts['bad_xf']}")

    pg_ids = {str(x.get("ID", "")) for x in program_header}
    pg_names = {str(x.get("PN", "")) for x in program_header}
    if "STAR" not in pg_ids and "STAR" not in pg_names:
        errors.append("STAR program header is absent")
    if "annotate_reads" not in pg_ids and "annotate_reads" not in pg_names:
        errors.append("annotate_reads program header is absent")
    sort_order = str(header.get("HD", {}).get("SO", ""))
    if sort_order != "coordinate":
        errors.append(f"expected coordinate-sorted BAM header; observed SO={sort_order!r}")

    if xf8 == 0:
        errors.append("zero xf bit8 molecule representatives observed")
    else:
        if xf8 < args.target_xf8:
            warnings.append(
                f"LOW_PREFIX_XF8_DENSITY:{xf8} observed before {records} records; "
                "quantitative adequacy is deferred to the full-file scan"
            )
        for tag in ("CB", "GN", "UB"):
            missing = xf8 - counts[f"xf8_{tag}"]
            if missing:
                errors.append(f"{missing}/{xf8} xf bit8 records lack a non-empty {tag} tag")
        unambiguous_fraction = counts["xf8_unambiguous_GN"] / xf8
        if unambiguous_fraction < 0.70:
            errors.append(
                "unambiguous GN fraction among xf bit8 records <0.70: "
                f"{unambiguous_fraction:.4f}"
            )

    fractions = {
        "CB_among_xf8": counts["xf8_CB"] / xf8 if xf8 else 0,
        "GN_among_xf8": counts["xf8_GN"] / xf8 if xf8 else 0,
        "UB_among_xf8": counts["xf8_UB"] / xf8 if xf8 else 0,
        "unambiguous_GN_among_xf8": counts["xf8_unambiguous_GN"] / xf8 if xf8 else 0,
    }
    output = {
        "schema": "R7A1C1B1R_BAM_SCHEMA_PREFLIGHT_1.2",
        "run": args.run,
        "bam": str(args.bam),
        "records_inspected": records,
        "sampling_rule": {
            "min_records": args.min_records,
            "max_records": args.max_records,
            "stop_after_target_xf8": args.target_xf8,
            "coordinate_sorted_adaptive_prefix": True,
            "prefix_xf8_abundance_is_not_a_hard_gate": True,
        },
        "counts": dict(counts),
        "fractions": fractions,
        "xf8_density_per_million_records": (xf8 / records * 1_000_000) if records else 0,
        "program_header": program_header,
        "bam_sort_order": sort_order,
        "examples": examples,
        "warnings": warnings,
        "errors": errors,
        "schema_valid": not errors,
        "quantitative_adequacy": "DEFERRED_TO_FULL_TARGET_PANEL_SCAN",
        "status": "FAIL" if errors else ("PASS_WITH_WARNING" if warnings else "PASS"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
