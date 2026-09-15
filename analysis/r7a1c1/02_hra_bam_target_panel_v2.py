#!/usr/bin/env python3
"""R7A1C1 donor target panel with molecule and called-cell hardening.

The GSA-Human files are Cell Ranger 3.1 coordinate-sorted BAMs.  CB is a
barcode-whitelist tag, not a called-cell flag.  This script therefore:
1. directly retains only xf bit 8 molecule-representative records;
2. reconstructs total gene-expression UMI and target-panel counts in one pass;
3. applies the Cell Ranger order-of-magnitude cell-calling rule around the
   study's declared 6,000 recovered-cell target; and
4. evaluates the frozen B/NK marker panels only within called barcodes.

This remains a donor-level detectability gate.  It is not a replacement for
the manuscript-scale full-matrix QC, integration, annotation, or pseudobulk.
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics

import pysam


TARGETS = {"FCRL3", "IL12RB2"}
B_MARKERS = {"CD79A", "CD79B", "MS4A1", "CD37", "CD74", "HLA-DRA", "CD19", "CD22"}
NK_MARKERS = {"NKG7", "GNLY", "KLRD1", "PRF1", "GZMB", "XCL1", "XCL2"}
T_MARKERS = {"CD3D", "CD3E", "TRBC1", "TRBC2", "IL7R"}
MY_MARKERS = {"LST1", "TYROBP", "FCER1G", "CTSS", "AIF1", "LYZ"}
PANEL = TARGETS | B_MARKERS | NK_MARKERS | T_MARKERS | MY_MARKERS


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gene_name(rec: pysam.AlignedSegment) -> str | None:
    if not rec.has_tag("GN"):
        return None
    hits = [x for x in str(rec.get_tag("GN")).split(";") if x]
    return hits[0] if len(hits) == 1 else None


def call_cells(total_umi: collections.Counter[str], expected_cells: int) -> tuple[set[str], dict]:
    if len(total_umi) < expected_cells:
        raise RuntimeError(f"only {len(total_umi)} barcodes have molecule records; expected >= {expected_cells}")
    ordered = sorted(total_umi.values(), reverse=True)
    top = ordered[:expected_cells]
    # Cell Ranger's order-of-magnitude rule: 10% of the 99th percentile UMI
    # count among the expected recovered-cell set.
    top_ascending = sorted(top)
    baseline = float(top_ascending[math.ceil(0.99 * (len(top_ascending) - 1))])
    threshold = max(1, int(math.ceil(baseline / 10.0)))
    called = {barcode for barcode, count in total_umi.items() if count >= threshold}
    called_counts = [total_umi[x] for x in called]
    if not 2500 <= len(called) <= 7500:
        raise RuntimeError(
            f"called-cell count {len(called)} outside predeclared 2500-7500 plausibility range; "
            "do not use target results until cell calling is independently resolved"
        )
    if float(statistics.median(called_counts)) < 500:
        raise RuntimeError("called-cell median total UMI <500")
    return called, {
        "method": "ordmag_10pct_of_99th_percentile_with_expected_cells",
        "expected_cells": expected_cells,
        "baseline_99th_percentile_UMI": baseline,
        "called_cell_UMI_threshold": threshold,
        "called_cells": len(called),
        "called_cell_total_UMI_min": int(min(called_counts)),
        "called_cell_total_UMI_median": float(statistics.median(called_counts)),
        "called_cell_total_UMI_max": int(max(called_counts)),
    }


def scan_molecules(bam_path: Path, expected_cells: int) -> tuple[list[dict], dict]:
    total_umi: collections.Counter[str] = collections.Counter()
    panel_by_barcode: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    all_records = 0
    molecule_records = 0
    tag_qc: collections.Counter[str] = collections.Counter()
    with pysam.AlignmentFile(str(bam_path), "rb", check_sq=False) as bam:
        for rec in bam.fetch(until_eof=True):
            all_records += 1
            if not rec.has_tag("xf") or (int(rec.get_tag("xf")) & 8) == 0:
                tag_qc["excluded_not_xf_bit8_molecule_representative"] += 1
                continue
            molecule_records += 1
            if rec.is_unmapped or rec.is_secondary or rec.is_supplementary:
                tag_qc["excluded_alignment_flag"] += 1
                continue
            if not rec.has_tag("CB"):
                tag_qc["missing_CB"] += 1
                continue
            gene = gene_name(rec)
            if gene is None:
                tag_qc["missing_or_ambiguous_GN"] += 1
                continue
            barcode = rec.get_tag("CB")
            total_umi[barcode] += 1
            if gene in PANEL:
                panel_by_barcode[barcode][gene] += 1

    called, cell_call = call_cells(total_umi, expected_cells)
    panel_molecules = sum(sum(panel_by_barcode[barcode].values()) for barcode in called)

    rows = []
    for barcode in sorted(called):
        counts = panel_by_barcode[barcode]
        b_genes = sum(counts[g] > 0 for g in B_MARKERS)
        nk_genes = sum(counts[g] > 0 for g in NK_MARKERS)
        t_genes = sum(counts[g] > 0 for g in T_MARKERS)
        my_genes = sum(counts[g] > 0 for g in MY_MARKERS)
        b_umi = sum(counts[g] for g in B_MARKERS)
        nk_umi = sum(counts[g] for g in NK_MARKERS)
        t_umi = sum(counts[g] for g in T_MARKERS)
        my_umi = sum(counts[g] for g in MY_MARKERS)
        b_gate = b_genes >= 2 and b_umi >= 3 and b_umi > max(nk_umi, t_umi, my_umi)
        nk_gate = nk_genes >= 2 and nk_umi >= 3 and nk_umi > max(b_umi, my_umi) and nk_umi >= t_umi
        rows.append(
            {
                "cell_barcode": barcode,
                "total_gene_UMI": total_umi[barcode],
                "B_marker_genes": b_genes, "B_marker_UMI": b_umi,
                "NK_marker_genes": nk_genes, "NK_marker_UMI": nk_umi,
                "T_marker_genes": t_genes, "T_marker_UMI": t_umi,
                "MY_marker_genes": my_genes, "MY_marker_UMI": my_umi,
                "B_lineage_gate": b_gate, "NK_lineage_gate": nk_gate,
                "FCRL3_UMI": counts["FCRL3"], "IL12RB2_UMI": counts["IL12RB2"],
            }
        )
    return rows, {
        "all_alignment_records": all_records,
        "molecule_records": molecule_records,
        "barcodes_with_unambiguous_gene_molecules": len(total_umi),
        "panel_molecules_in_called_cells": panel_molecules,
        "tag_qc": dict(tag_qc),
        "cell_call": cell_call,
        "molecule_filter": "direct_pysam_xf_bit8_single_pass",
    }


def summarize(run: str, bam: Path, cells: list[dict], scan_qc: dict, software: dict) -> dict:
    b_cells = [x for x in cells if x["B_lineage_gate"]]
    nk_cells = [x for x in cells if x["NK_lineage_gate"]]
    f_positive = [x for x in b_cells if x["FCRL3_UMI"] > 0]
    i_positive = [x for x in nk_cells if x["IL12RB2_UMI"] > 0]
    f_umi = sum(x["FCRL3_UMI"] for x in b_cells)
    i_umi = sum(x["IL12RB2_UMI"] for x in nk_cells)
    f_sensitivity = f_umi >= 3 and len(f_positive) >= 2
    i_sensitivity = i_umi >= 3 and len(i_positive) >= 2
    b_adequate = len(b_cells) >= 10
    nk_adequate = len(nk_cells) >= 10
    return {
        "schema_version": "CMM_R7A1C1_TARGET_PANEL_2.0",
        "run": run,
        "bam": str(bam),
        "bam_bytes": bam.stat().st_size,
        "bam_sha256": sha256_file(bam),
        "software": software,
        "scan_qc": scan_qc,
        "B_gate_cells": len(b_cells),
        "NK_gate_cells": len(nk_cells),
        "B_lineage_adequacy": b_adequate,
        "NK_lineage_adequacy": nk_adequate,
        "FCRL3_B_positive_cells": len(f_positive),
        "FCRL3_B_UMI": f_umi,
        "IL12RB2_NK_positive_cells": len(i_positive),
        "IL12RB2_NK_UMI": i_umi,
        "primary_FCRL3_B_detectable": bool(b_adequate and f_umi > 0),
        "primary_IL12RB2_NK_detectable": bool(nk_adequate and i_umi > 0),
        "sensitivity_FCRL3_B": bool(b_adequate and f_sensitivity),
        "sensitivity_IL12RB2_NK": bool(nk_adequate and i_sensitivity),
        "promotion_eligible_FCRL3_B": bool(b_adequate and f_sensitivity),
        "promotion_eligible_IL12RB2_NK": bool(nk_adequate and i_sensitivity),
        "technical_QC": "PASS",
        "boundary": "called-cell donor target detectability only; final analysis requires full QC/reclustering and donor-by-cell-type pseudobulk",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bam", type=Path, required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True, help="runner compatibility; no large intermediate is created")
    parser.add_argument("--samtools-threads", type=int, default=4, help="runner compatibility")
    parser.add_argument("--expected-cells", type=int, default=6000)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    args.workdir.mkdir(parents=True, exist_ok=True)
    if not args.bam.exists():
        raise FileNotFoundError(args.bam)
    software = {
        "python": platform.python_version(),
        "pysam": pysam.__version__,
        "htslib": getattr(pysam, "__samtools_version__", "unknown"),
    }
    cells, scan_qc = scan_molecules(args.bam, args.expected_cells)
    for row in cells:
        row["run"] = args.run
    cell_path = args.outdir / f"{args.run}_target_panel_called_cells.tsv.gz"
    with gzip.open(cell_path, "wt", encoding="utf-8", newline="") as handle:
        columns = ["run"] + [x for x in cells[0].keys() if x != "run"]
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(cells)
    summary = summarize(args.run, args.bam, cells, scan_qc, software)
    write_json(args.outdir / f"{args.run}_target_panel_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
