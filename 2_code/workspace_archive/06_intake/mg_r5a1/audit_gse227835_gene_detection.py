#!/usr/bin/env python3
"""Spot-check candidate-gene detection in one MG and one control scRNA matrix."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import pathlib
from datetime import datetime, timezone


ROOT = pathlib.Path(r"H:\SCI2\YR1")
SOURCE = ROOT / "1_data" / "scrna" / "MG" / "GSE227835" / "R5A1_spotcheck"
AUDIT = ROOT / "3_results" / "00_audit" / "R5A1"
RESULTS = ROOT / "3_results" / "05_scrna" / "R5A1"
SAMPLES = {
    "GSM7266236_A1.txt.gz": "AChR-positive_MG",
    "GSM7266246_H1.txt.gz": "healthy_control",
}
CANDIDATES = {
    "TNIP1", "ANXA6", "ATOX1", "CCDC69", "GM2A", "RPS14", "SLC36A1", "TCOF1",
    "SOS1", "SRSF7", "GALM", "DHX57", "TNFRSF11A", "PIGN", "ZCCHC2",
}


def digest(path: pathlib.Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    samples: dict[str, dict[str, object]] = {}
    for filename, group in SAMPLES.items():
        path = SOURCE / filename
        genes = 0
        found: set[str] = set()
        with gzip.open(path, "rt", encoding="utf-8", errors="strict") as handle:
            header = handle.readline().rstrip("\r\n").split("\t")
            cell_count = len(header) - 1
            for line in handle:
                genes += 1
                parts = line.rstrip("\r\n").split("\t")
                gene = parts[0]
                if gene not in CANDIDATES:
                    continue
                values = [int(x) for x in parts[1:]]
                nonzero = sum(value > 0 for value in values)
                found.add(gene)
                rows.append(
                    {
                        "sample": filename.removesuffix(".txt.gz"),
                        "group": group,
                        "gene": gene,
                        "cells": cell_count,
                        "cells_nonzero": nonzero,
                        "fraction_cells_nonzero": nonzero / cell_count,
                        "total_raw_counts": sum(values),
                        "max_raw_count": max(values),
                        "detected": nonzero > 0,
                    }
                )
        samples[filename] = {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": digest(path, "sha256"),
            "gzip_complete": True,
            "matrix_cell_barcodes": cell_count,
            "matrix_gene_rows": genes,
            "candidate_genes_present": sorted(found),
            "candidate_genes_missing": sorted(CANDIDATES - found),
        }
    rows.sort(key=lambda x: (str(x["gene"]), str(x["group"])))
    with (RESULTS / "GSE227835_candidate_gene_detection_spotcheck.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    tnip1 = [row for row in rows if row["gene"] == "TNIP1"]
    output = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "series": "GSE227835",
        "samples": samples,
        "TNIP1_detected_in_both_spotcheck_samples": len(tnip1) == 2 and all(bool(row["detected"]) for row in tnip1),
        "single_cell_gene_detection_gate": "PASS" if len(tnip1) == 2 and all(bool(row["detected"]) for row in tnip1) else "FAIL",
        "interpretation_limit": "gene inclusion and nonzero single-cell counts only; no cell-type localization or disease differential claim",
    }
    with (AUDIT / "GSE227835_gene_detection_audit.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"samples": {k: {"cells": v["matrix_cell_barcodes"], "genes": v["matrix_gene_rows"]} for k, v in samples.items()}, "TNIP1": tnip1, "gate": output["single_cell_gene_detection_gate"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
