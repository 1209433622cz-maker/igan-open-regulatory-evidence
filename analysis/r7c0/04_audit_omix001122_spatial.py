#!/usr/bin/env python3
"""Audit the public OMIX001122 spatial Matrix Market bytes.

Only descriptive donor-level detectability is produced.  The archive contains
one control matrix and one PBC matrix and lacks tissue-image coordinates, so
it cannot support replication statistics or spatial localization by itself.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from scipy.io import mmread


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011"
EXTRACTED = WORK / "external_metadata/OMIX001122_spatial_extracted/processed_data_Spatial_transcriptomics"
FREEZE = WORK / "results/R7C0_frozen_92_stableH4_comparisons.tsv"
OUT = WORK / "results"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_lines(path: Path) -> list[str]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [line.rstrip("\n") for line in handle]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    genes = sorted(pd.read_csv(FREEZE, sep="\t")["gene"].unique())
    rows, samples = [], []
    for sample in ["CTR4_2", "PBC5_2"]:
        feature_path = EXTRACTED / f"{sample}_features.tsv.gz"
        barcode_path = EXTRACTED / f"{sample}_barcodes.tsv.gz"
        matrix_path = EXTRACTED / f"{sample}_matrix.mtx.gz"
        features = [line.split("\t") for line in load_lines(feature_path)]
        barcodes = load_lines(barcode_path)
        matrix = mmread(matrix_path).tocsr()
        if matrix.shape != (len(features), len(barcodes)):
            raise RuntimeError(f"Matrix shape mismatch for {sample}: {matrix.shape}, {len(features)}, {len(barcodes)}")
        symbol_to_idx: dict[str, list[int]] = {}
        for idx, parts in enumerate(features):
            symbol = parts[1] if len(parts) > 1 else parts[0]
            symbol_to_idx.setdefault(symbol, []).append(idx)
        library_total = float(matrix.sum())
        for gene in genes:
            idxs = symbol_to_idx.get(gene, [])
            if idxs:
                values = matrix[idxs, :].sum(axis=0).A1
                total = float(values.sum())
                positive = int((values > 0).sum())
            else:
                total, positive = 0.0, 0
            rows.append({
                "sample": sample, "condition": "PBC" if sample.startswith("PBC") else "control",
                "gene": gene, "feature_rows": len(idxs), "spots": len(barcodes),
                "total_umi": total, "positive_spots": positive,
                "positive_spot_fraction": positive / len(barcodes),
                "pseudobulk_cpm": total / library_total * 1e6 if library_total else None,
            })
        samples.append({
            "sample": sample, "condition": "PBC" if sample.startswith("PBC") else "control",
            "matrix_genes": matrix.shape[0], "matrix_spots": matrix.shape[1],
            "nonzero_entries": int(matrix.nnz), "library_total_umi": library_total,
            "matrix_sha256": sha256(matrix_path), "features_sha256": sha256(feature_path),
            "barcodes_sha256": sha256(barcode_path),
        })
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "R7C0_OMIX001122_27gene_spatial_detectability.tsv", sep="\t", index=False)
    pd.DataFrame(samples).to_csv(OUT / "R7C0_OMIX001122_spatial_sample_QC.tsv", sep="\t", index=False)
    pivot = result.pivot(index="gene", columns="condition", values="positive_spots")
    summary = {
        "stage": "R7C0_G4",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "archive_file_count": 6,
        "biological_matrices": 2,
        "control_matrices": 1,
        "pbc_matrices": 1,
        "prespecified_genes": len(genes),
        "genes_detected_in_control": int((pivot.get("control", 0) > 0).sum()),
        "genes_detected_in_pbc": int((pivot.get("PBC", 0) > 0).sum()),
        "IL12RB2": result[result["gene"].eq("IL12RB2")].to_dict("records"),
        "FCRL3": result[result["gene"].eq("FCRL3")].to_dict("records"),
        "adjudication": "PASS_OPEN_BYTES_FAIL_INDEPENDENT_SPATIAL_VALIDATION_GATE",
        "reason": (
            "The 34.63 MB public archive is valid but contains six Matrix Market component files for only two "
            "biological matrices (CTR4_2 and PBC5_2), not six donors. No tissue-image coordinates or spot-level "
            "annotation accompany these files. Descriptive detectability is valid; spatial localization, donor-level "
            "replication, and case-control inference are not. The data originate from an already published PBC study."
        ),
        "action": "DO_NOT_USE_AS_Q1_INDEPENDENT_SPATIAL_REPLICATION; RETAIN_AS_OPTIONAL_DESCRIPTIVE_RESOURCE",
    }
    (OUT / "R7C0_OMIX001122_spatial_adjudication.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
