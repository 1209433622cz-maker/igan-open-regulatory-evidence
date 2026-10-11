#!/usr/bin/env python3
"""Group a prefiltered MG subtype-heterogeneity candidate table by distance.

The output is descriptive only. A distance group is not an LD-independent locus.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maximum-gap", type=int, default=1_000_000)
    args = parser.parse_args()
    if args.maximum_gap < 1:
        raise SystemExit("--maximum-gap must be positive")

    with args.input.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    required = {"chromosome", "position", "variant_id", "rsid", "p_het"}
    if not rows or not required.issubset(rows[0]):
        raise RuntimeError(f"Missing required columns: {sorted(required)}")

    rows.sort(key=lambda row: (int(row["chromosome"]), int(row["position"])))
    groups: list[list[dict[str, str]]] = []
    for row in rows:
        if not groups:
            groups.append([row])
            continue
        previous = groups[-1][-1]
        same_chromosome = int(row["chromosome"]) == int(previous["chromosome"])
        within_gap = int(row["position"]) - int(previous["position"]) <= args.maximum_gap
        if same_chromosome and within_gap:
            groups[-1].append(row)
        else:
            groups.append([row])

    output_rows: list[dict[str, object]] = []
    for index, group in enumerate(groups, start=1):
        lead = min(group, key=lambda row: float(row["p_het"]))
        output_rows.append(
            {
                "candidate_region_id": f"HETC{index:03d}",
                "chromosome": int(lead["chromosome"]),
                "start": min(int(row["position"]) for row in group),
                "end": max(int(row["position"]) for row in group),
                "lead_variant_id": lead["variant_id"],
                "lead_rsid": lead["rsid"],
                "lead_p_het": lead["p_het"],
                "candidate_variant_count": len(group),
                "grouping_rule": f"distance_only_max_gap_{args.maximum_gap}; not LD independence",
            }
        )

    fields = [
        "candidate_region_id", "chromosome", "start", "end", "lead_variant_id",
        "lead_rsid", "lead_p_het", "candidate_variant_count", "grouping_rule",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"candidate_regions={len(output_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
