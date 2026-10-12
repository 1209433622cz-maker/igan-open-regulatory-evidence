#!/usr/bin/env python3
"""Extract and harmonize the MG GRCh37 chr5 bounded pilot interval to OneK1K BIM A1.

The GWAS Catalog original files are unsorted GRCh37 summary statistics.  This
script scans every row, selects chr5:149,447,128-151,447,128, joins by the
unique OneK1K BIM position, and orients log(OR) and EAF to the BIM A1 allele.
Palindromic SNPs are resolved only when the GWAS EAF clearly agrees with the
OneK1K 980-donor A1 frequency; otherwise they are retained as audit rows but
excluded from downstream inference.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(r"H:\SCI2\YR1")
GWAS_ROOT = ROOT / "1_data/gwas/MG/R5A1_GWAS_Catalog"
PLINK_ROOT = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors"
OUT_ROOT = ROOT / "3_results/01_gwas/R5A2B"
AUDIT_ROOT = ROOT / "3_results/00_audit/R5A2B"

CHROMOSOME = "5"
LEAD_POSITION = 150_447_128
REGION_START = 149_447_128
REGION_END = 151_447_128

EXPECTED_HEADER = [
    "chromosome",
    "base_pair_location",
    "effect_allele",
    "other_allele",
    "odds_ratio",
    "standard_error",
    "effect_allele_frequency",
    "p_value",
]

TRAITS = {
    "GCST90432156": {
        "label": "MG_overall",
        "cases": 5_708,
        "controls": 432_028,
        "bytes": 332_462_076,
        "md5": "59c0ec0573a9814e6d6cf556389f587b",
    },
    "GCST90432157": {
        "label": "EOMG",
        "cases": 1_391,
        "controls": 22_407,
        "bytes": 359_301_658,
        "md5": "fbc95996b50da89b9b2f940243ad1de9",
    },
    "GCST90432158": {
        "label": "LOMG",
        "cases": 2_404,
        "controls": 64_103,
        "bytes": 300_669_210,
        "md5": "e7a87afec001edf0e0d3f738c7dc2427",
    },
}


def hashes(path: Path) -> tuple[str, str]:
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            md5.update(block)
            sha256.update(block)
    return md5.hexdigest(), sha256.hexdigest()


def reverse_complement(allele: str) -> str:
    table = str.maketrans("ACGT", "TGCA")
    return allele.translate(table)[::-1]


def is_palindromic(a1: str, a2: str) -> bool:
    return len(a1) == 1 and len(a2) == 1 and reverse_complement(a1) == a2


def load_bim_and_af() -> tuple[dict[int, dict[str, object]], int, int]:
    fam_path = PLINK_ROOT / "plink_merged_980_donors.fam"
    bim_path = PLINK_ROOT / "plink_merged_980_donors.bim"
    bed_path = PLINK_ROOT / "plink_merged_980_donors.bed"
    n_samples = sum(1 for line in fam_path.open(encoding="utf-8") if line.strip())
    if n_samples != 980:
        raise RuntimeError(f"Expected 980 OneK1K donors, found {n_samples}")
    bytes_per_variant = (n_samples + 3) // 4
    positions: dict[int, dict[str, object]] = {}
    with bim_path.open(encoding="utf-8") as stream:
        for global_index, line in enumerate(stream):
            chromosome, variant_id, _, position_text, a1, a2 = line.split()
            if chromosome != CHROMOSOME:
                continue
            position = int(position_text)
            if not REGION_START <= position <= REGION_END:
                continue
            if position in positions:
                raise RuntimeError(f"Duplicate OneK1K BIM position: chr5:{position}")
            positions[position] = {
                "global_bim_index_zero_based": global_index,
                "variant_id": variant_id,
                "A1": a1.upper(),
                "A2": a2.upper(),
            }
    with bed_path.open("rb") as bed:
        if bed.read(3).hex() != "6c1b01":
            raise RuntimeError("OneK1K BED is not SNP-major PLINK v1")
        for item in positions.values():
            bed.seek(3 + int(item["global_bim_index_zero_based"]) * bytes_per_variant)
            raw = bed.read(bytes_per_variant)
            codes = np.fromiter(
                ((byte >> shift) & 3 for byte in raw for shift in (0, 2, 4, 6)),
                dtype=np.int8,
                count=bytes_per_variant * 4,
            )[:n_samples]
            called = codes != 1
            a1_dosage = np.where(codes == 0, 2, np.where(codes == 2, 1, np.where(codes == 3, 0, -9)))
            item["oneK1K_called_980"] = int(called.sum())
            item["oneK1K_AF_A1_980"] = float(a1_dosage[called].sum() / (2 * called.sum()))
    return positions, n_samples, bytes_per_variant


def classify_and_orient(
    effect: str,
    other: str,
    a1: str,
    a2: str,
    raw_beta: float,
    raw_eaf: float,
    onek_af_a1: float,
) -> dict[str, object]:
    effect = effect.upper()
    other = other.upper()
    palindromic = is_palindromic(a1, a2)
    relation = "ALLELE_MISMATCH"
    sign = None
    if effect == a1 and other == a2:
        relation, sign = "DIRECT_A1", 1
    elif effect == a2 and other == a1:
        relation, sign = "SWAPPED_A2", -1
    elif reverse_complement(effect) == a1 and reverse_complement(other) == a2:
        relation, sign = "STRAND_DIRECT_A1", 1
    elif reverse_complement(effect) == a2 and reverse_complement(other) == a1:
        relation, sign = "STRAND_SWAPPED_A2", -1

    if sign is None:
        return {
            "match_type": relation,
            "palindromic": palindromic,
            "beta_A1": None,
            "eaf_A1": None,
            "frequency_difference": None,
            "inference_eligible": False,
            "exclusion_reason": "ALLELE_MISMATCH",
        }

    eaf_candidate = raw_eaf if sign == 1 else 1.0 - raw_eaf
    beta_candidate = raw_beta * sign
    freq_difference = abs(eaf_candidate - onek_af_a1)
    exclusion_reason = ""

    if palindromic:
        opposite_eaf = 1.0 - eaf_candidate
        opposite_difference = abs(opposite_eaf - onek_af_a1)
        # Resolve the strand only when one orientation is at least 0.10 closer
        # and the chosen frequency differs by no more than 0.20.
        if opposite_difference + 0.10 < freq_difference and opposite_difference <= 0.20:
            eaf_candidate = opposite_eaf
            beta_candidate = -beta_candidate
            freq_difference = opposite_difference
            relation += "_PALINDROMIC_FREQ_FLIPPED"
        elif freq_difference + 0.10 <= opposite_difference and freq_difference <= 0.20:
            relation += "_PALINDROMIC_FREQ_RESOLVED"
        else:
            exclusion_reason = "PALINDROMIC_FREQUENCY_AMBIGUOUS"

    if not exclusion_reason and freq_difference > 0.20:
        exclusion_reason = "EAF_DISCORDANCE_GT_0.20"

    return {
        "match_type": relation,
        "palindromic": palindromic,
        "beta_A1": beta_candidate,
        "eaf_A1": eaf_candidate,
        "frequency_difference": freq_difference,
        "inference_eligible": not exclusion_reason,
        "exclusion_reason": exclusion_reason,
    }


def process_trait(accession: str, meta: dict[str, object], bim: dict[int, dict[str, object]]) -> dict[str, object]:
    source = GWAS_ROOT / accession / f"{accession}.tsv"
    actual_md5, actual_sha256 = hashes(source)
    byte_pass = source.stat().st_size == int(meta["bytes"])
    md5_pass = actual_md5 == str(meta["md5"])
    if not byte_pass or not md5_pass:
        raise RuntimeError(f"Byte/hash failure for {accession}")

    out_path = OUT_ROOT / f"{accession}_{meta['label']}_chr5_GRCh37_fixed_1Mb.tsv.gz"
    output_fields = [
        "accession", "trait", "n_cases", "n_controls", "chromosome", "position_GRCh37",
        "variant_id", "BIM_A1_effect_allele", "BIM_A2_other_allele", "GWAS_effect_allele",
        "GWAS_other_allele", "odds_ratio_GWAS_effect", "beta_logOR_GWAS_effect", "standard_error",
        "p_value", "EAF_GWAS_effect", "oneK1K_AF_A1_980", "oneK1K_called_980", "match_type",
        "palindromic", "beta_logOR_A1", "EAF_A1", "frequency_difference", "inference_eligible",
        "exclusion_reason",
    ]
    counters: Counter[str] = Counter()
    seen_region_positions: Counter[int] = Counter()
    seen_matched_positions: Counter[int] = Counter()
    seen_inference_eligible_positions: Counter[int] = Counter()
    lead_row: dict[str, object] | None = None
    numeric_failure_examples: list[dict[str, str]] = []

    with source.open("r", encoding="utf-8", newline="") as source_stream, gzip.open(
        out_path, "wt", encoding="utf-8", newline=""
    ) as out_stream:
        reader = csv.DictReader(source_stream, delimiter="\t")
        if reader.fieldnames != EXPECTED_HEADER:
            raise RuntimeError(f"Unexpected {accession} header: {reader.fieldnames}")
        writer = csv.DictWriter(out_stream, fieldnames=output_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in reader:
            counters["all_data_rows"] += 1
            chromosome = row["chromosome"].removeprefix("chr")
            if chromosome != CHROMOSOME:
                continue
            counters["chr5_rows"] += 1
            try:
                position = int(row["base_pair_location"])
            except ValueError:
                counters["invalid_position"] += 1
                continue
            if not REGION_START <= position <= REGION_END:
                continue
            counters["fixed_window_rows"] += 1
            seen_region_positions[position] += 1
            item = bim.get(position)
            if item is None:
                counters["not_in_OneK1K_BIM"] += 1
                continue
            counters["position_in_OneK1K_BIM"] += 1
            seen_matched_positions[position] += 1
            try:
                odds_ratio = float(row["odds_ratio"])
                standard_error = float(row["standard_error"])
                eaf = float(row["effect_allele_frequency"])
                p_value = float(row["p_value"])
                if not (odds_ratio > 0 and standard_error > 0 and 0 <= eaf <= 1 and 0 <= p_value <= 1):
                    raise ValueError("numeric value outside valid range")
            except (ValueError, TypeError) as exc:
                counters["invalid_numeric"] += 1
                if len(numeric_failure_examples) < 5:
                    numeric_failure_examples.append({"position": str(position), "error": str(exc)})
                continue

            raw_beta = math.log(odds_ratio)
            oriented = classify_and_orient(
                row["effect_allele"], row["other_allele"], str(item["A1"]), str(item["A2"]),
                raw_beta, eaf, float(item["oneK1K_AF_A1_980"]),
            )
            counters[str(oriented["match_type"])] += 1
            if oriented["palindromic"]:
                counters["palindromic_rows"] += 1
            if oriented["inference_eligible"]:
                counters["inference_eligible_rows"] += 1
                seen_inference_eligible_positions[position] += 1
            else:
                counters["inference_excluded_rows"] += 1
                counters[f"excluded_{oriented['exclusion_reason']}"] += 1

            output = {
                "accession": accession,
                "trait": meta["label"],
                "n_cases": meta["cases"],
                "n_controls": meta["controls"],
                "chromosome": 5,
                "position_GRCh37": position,
                "variant_id": item["variant_id"],
                "BIM_A1_effect_allele": item["A1"],
                "BIM_A2_other_allele": item["A2"],
                "GWAS_effect_allele": row["effect_allele"].upper(),
                "GWAS_other_allele": row["other_allele"].upper(),
                "odds_ratio_GWAS_effect": odds_ratio,
                "beta_logOR_GWAS_effect": raw_beta,
                "standard_error": standard_error,
                "p_value": p_value,
                "EAF_GWAS_effect": eaf,
                "oneK1K_AF_A1_980": item["oneK1K_AF_A1_980"],
                "oneK1K_called_980": item["oneK1K_called_980"],
                "match_type": oriented["match_type"],
                "palindromic": oriented["palindromic"],
                "beta_logOR_A1": oriented["beta_A1"],
                "EAF_A1": oriented["eaf_A1"],
                "frequency_difference": oriented["frequency_difference"],
                "inference_eligible": oriented["inference_eligible"],
                "exclusion_reason": oriented["exclusion_reason"],
            }
            writer.writerow(output)
            if position == LEAD_POSITION:
                lead_row = output

    duplicate_region_positions = sum(1 for count in seen_region_positions.values() if count > 1)
    duplicate_matched_positions = sum(1 for count in seen_matched_positions.values() if count > 1)
    duplicate_inference_eligible_positions = sum(1 for count in seen_inference_eligible_positions.values() if count > 1)
    return {
        "accession": accession,
        "trait": meta["label"],
        "source_path": str(source.relative_to(ROOT)).replace("\\", "/"),
        "source_bytes": source.stat().st_size,
        "expected_bytes": meta["bytes"],
        "byte_count_pass": byte_pass,
        "actual_md5": actual_md5,
        "expected_md5": meta["md5"],
        "md5_pass": md5_pass,
        "actual_sha256": actual_sha256,
        "header_pass": True,
        "counts": dict(sorted(counters.items())),
        "duplicate_positions_in_fixed_window": duplicate_region_positions,
        "duplicate_BIM_position_rows": duplicate_matched_positions,
        "duplicate_inference_eligible_positions": duplicate_inference_eligible_positions,
        "numeric_failure_examples": numeric_failure_examples,
        "lead_rs6861227": lead_row,
        "output_path": str(out_path.relative_to(ROOT)).replace("\\", "/"),
        "output_bytes": out_path.stat().st_size,
    }


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    bim, n_samples, bytes_per_variant = load_bim_and_af()
    trait_results = [process_trait(accession, meta, bim) for accession, meta in TRAITS.items()]

    manifest_path = OUT_ROOT / "MG_GRCh37_chr5_fixed_1Mb_harmonization_manifest.tsv"
    manifest_fields = [
        "accession", "trait", "source_bytes", "md5_pass", "all_data_rows", "fixed_window_rows",
        "position_in_OneK1K_BIM", "inference_eligible_rows", "inference_excluded_rows",
        "duplicate_positions_in_fixed_window", "duplicate_BIM_position_rows",
        "duplicate_inference_eligible_positions", "lead_present", "output_path", "output_bytes",
    ]
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=manifest_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for result in trait_results:
            counts = result["counts"]
            writer.writerow({
                "accession": result["accession"],
                "trait": result["trait"],
                "source_bytes": result["source_bytes"],
                "md5_pass": result["md5_pass"],
                "all_data_rows": counts.get("all_data_rows", 0),
                "fixed_window_rows": counts.get("fixed_window_rows", 0),
                "position_in_OneK1K_BIM": counts.get("position_in_OneK1K_BIM", 0),
                "inference_eligible_rows": counts.get("inference_eligible_rows", 0),
                "inference_excluded_rows": counts.get("inference_excluded_rows", 0),
                "duplicate_positions_in_fixed_window": result["duplicate_positions_in_fixed_window"],
                "duplicate_BIM_position_rows": result["duplicate_BIM_position_rows"],
                "duplicate_inference_eligible_positions": result["duplicate_inference_eligible_positions"],
                "lead_present": result["lead_rs6861227"] is not None,
                "output_path": result["output_path"],
                "output_bytes": result["output_bytes"],
            })

    audit = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixed_region": {
            "build": "GRCh37",
            "chromosome": 5,
            "lead_rsID": "rs6861227",
            "lead_position": LEAD_POSITION,
            "start": REGION_START,
            "end": REGION_END,
        },
        "OneK1K_reference": {
            "samples": n_samples,
            "bytes_per_variant": bytes_per_variant,
            "unique_BIM_positions_in_window": len(bim),
            "effect_allele": "BIM_A1",
        },
        "harmonization_rules": {
            "join": "same GRCh37 chromosome and unique base-pair position",
            "effect_orientation": "log(OR) and EAF oriented to OneK1K BIM A1",
            "palindromic_resolution": "frequency-selected only if one orientation is >=0.10 closer and selected difference <=0.20",
            "frequency_guard": "exclude if abs(GWAS EAF_A1 - OneK1K AF_A1_980) > 0.20",
        },
        "traits": trait_results,
    }
    required_counts_pass = all(
        result["counts"].get("inference_eligible_rows", 0) >= 1_000
        and result["counts"].get("invalid_numeric", 0) == 0
        and result["duplicate_inference_eligible_positions"] == 0
        and result["lead_rs6861227"] is not None
        for result in trait_results
    )
    audit["checks"] = {
        "all_three_source_byte_counts_pass": all(result["byte_count_pass"] for result in trait_results),
        "all_three_source_md5_pass": all(result["md5_pass"] for result in trait_results),
        "all_three_headers_pass": all(result["header_pass"] for result in trait_results),
        "all_three_leads_present": all(result["lead_rs6861227"] is not None for result in trait_results),
        "regional_harmonization_sufficient": required_counts_pass,
    }
    audit["GRCh37_disease_input_gate_pass"] = all(audit["checks"].values())
    audit_path = AUDIT_ROOT / "MG_GRCh37_chr5_harmonization_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "audit": str(audit_path),
        "manifest": str(manifest_path),
        "OneK1K_BIM_variants": len(bim),
        "traits": [{"accession": r["accession"], "counts": r["counts"], "lead": r["lead_rs6861227"]} for r in trait_results],
        "GRCh37_disease_input_gate_pass": audit["GRCh37_disease_input_gate_pass"],
    }, indent=2, ensure_ascii=False))
    return 0 if audit["GRCh37_disease_input_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
