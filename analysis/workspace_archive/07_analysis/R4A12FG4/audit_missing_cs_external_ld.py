#!/usr/bin/env python3
"""Audit missing NK credible-set variants using the frozen 1000G EUR panel.

The result is a post-gate diagnostic.  It can justify a labelled classic-coloc
sensitivity run, but it cannot turn the exact-coverage or source-matched-LD
gates into PASS.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_bed_variants(bed: Path, bim: Path, fam: Path, wanted: set[str]) -> tuple[dict, dict]:
    sample_count = sum(1 for _ in fam.open())
    bytes_per_variant = math.ceil(sample_count / 4)
    indices = {}
    metadata = {}
    with bim.open() as handle:
        for index, line in enumerate(handle):
            fields = line.split()
            if fields[1] in wanted:
                indices[fields[1]] = index
                metadata[fields[1]] = {
                    "chrom": fields[0],
                    "grch37_pos": int(fields[3]),
                    "bim_A1": fields[4],
                    "bim_A2": fields[5],
                }
    raw = bed.read_bytes()
    if raw[:3] != b"\x6c\x1b\x01":
        raise RuntimeError("PLINK BED is not SNP-major")
    code_to_dosage = {0: 0.0, 2: 1.0, 3: 2.0, 1: np.nan}
    genotypes = {}
    for rsid, index in indices.items():
        packed = raw[3 + index * bytes_per_variant : 3 + (index + 1) * bytes_per_variant]
        dosage = np.empty(sample_count, dtype=float)
        for sample in range(sample_count):
            code = (packed[sample // 4] >> (2 * (sample % 4))) & 3
            dosage[sample] = code_to_dosage[code]
        genotypes[rsid] = dosage
    return genotypes, {
        "samples": sample_count,
        "variants": metadata,
        "bed_sha256": sha256(bed),
        "bim_sha256": sha256(bim),
        "fam_sha256": sha256(fam),
    }


def correlation(a: np.ndarray, b: np.ndarray) -> tuple[int, float]:
    keep = np.isfinite(a) & np.isfinite(b)
    if keep.sum() < 3:
        raise RuntimeError("fewer than three complete samples for LD")
    value = float(np.corrcoef(a[keep], b[keep])[0, 1])
    return int(keep.sum()), value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harmonized", type=Path, required=True)
    parser.add_argument("--cs-map", type=Path, required=True)
    parser.add_argument("--bed", type=Path, required=True)
    parser.add_argument("--bim", type=Path, required=True)
    parser.add_argument("--fam", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    with args.harmonized.open(encoding="utf-8-sig", newline="") as handle:
        harmonized_keys = {row["qtl_marker"] for row in csv.DictReader(handle, delimiter="\t")}
    mapping = json.loads(args.cs_map.read_text(encoding="utf-8"))["rows"]
    for row in mapping:
        row["rsids"] = [f"rs{value}" for value in row["rsids"]]
        row["exact_gwas_overlap"] = row["variant"] in harmonized_keys
    wanted = {rsid for row in mapping for rsid in row["rsids"]}
    wanted.update({"rs6662198", "rs1954118"})
    genotypes, panel = read_bed_variants(args.bed, args.bim, args.fam, wanted)

    diagnostics = []
    for missing in [row for row in mapping if not row["exact_gwas_overlap"]]:
        candidates = []
        for rsid in missing["rsids"]:
            if rsid not in genotypes:
                continue
            for present in [
                row for row in mapping
                if row["exact_gwas_overlap"] and row["credible_set"] == missing["credible_set"]
            ]:
                for other_rsid in present["rsids"]:
                    if other_rsid not in genotypes:
                        continue
                    n, signed_r = correlation(genotypes[rsid], genotypes[other_rsid])
                    candidates.append(
                        {
                            "missing_rsid": rsid,
                            "proxy_variant": present["variant"],
                            "proxy_rsid": other_rsid,
                            "n_complete": n,
                            "signed_r_bed_A1_dosage": signed_r,
                            "r2": signed_r * signed_r,
                        }
                    )
        best = max(candidates, key=lambda row: row["r2"], default=None)
        diagnostics.append(
            {
                "missing_variant": missing["variant"],
                "rsids": missing["rsids"],
                "credible_set": missing["credible_set"],
                "pip": missing["pip"],
                "panel_variant_present": any(rsid in genotypes for rsid in missing["rsids"]),
                "best_same_cs_exact_overlap_proxy": best,
            }
        )

    high_pip_missing = [row for row in diagnostics if row["pip"] >= 0.10]
    high_pip_proxy_pass = bool(high_pip_missing) and all(
        row["best_same_cs_exact_overlap_proxy"] is not None
        and row["best_same_cs_exact_overlap_proxy"]["r2"] >= 0.80
        for row in high_pip_missing
    )
    result = {
        "schema_version": "CMM_R4A12FG4_EXTERNAL_PROXY_AUDIT_1.0",
        "status": (
            "CONDITIONAL_PROXY_SUPPORT_FOR_POST_GATE_DIAGNOSTIC"
            if high_pip_proxy_pass else "HOLD_NO_HIGH_PIP_PROXY_SUPPORT"
        ),
        "exact_coverage_gate": "REMAINS_HOLD",
        "source_matched_ld_gate": "REMAINS_HOLD",
        "allowed_use": "classic coloc.abf post-gate diagnostic only",
        "panel": {
            "name": "1000 Genomes Phase 3 v5a EUR503",
            "build": "GRCh37",
            "role": "external LD diagnostic",
            **panel,
        },
        "missing_credible_set_variants": diagnostics,
        "high_pip_missing_proxy_r2_threshold": 0.80,
        "high_pip_missing_proxy_check": high_pip_proxy_pass,
        "limitations": [
            "LD is not from TenK10K or FinnGen participants.",
            "Signed r follows PLINK BED A1 dosage and is not harmonized to eQTL effect direction.",
            "A proxy does not restore the missing variant's disease association statistic.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "missing": diagnostics}, ensure_ascii=False, indent=2))
    return 0 if high_pip_proxy_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
