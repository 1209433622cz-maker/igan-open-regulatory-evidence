#!/usr/bin/env python3
"""Strict genome-wide EOMG-versus-LOMG effect heterogeneity scan.

The two GWAS Catalog harmonised inputs are streamed in coordinate order. Variant
identity comes from ``variant_id=chrom_position_REF_ALT``; the effect estimate and
frequency are then oriented to that ALT allele. This avoids using the reported
effect/other allele pair itself as the merge key.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import heapq
import json
import math
import pathlib
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterator, TextIO


MHC_CHR = 6
MHC_START = 25_000_000
MHC_END = 35_000_000
KNOWN_RSIDS = {"rs2476601", "rs7596255", "rs6861227", "rs7239261"}
P_BINS = (5e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 0.05)


class RowError(ValueError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(detail or code)
        self.code = code


@dataclass(frozen=True)
class Record:
    chromosome: int
    position: int
    reference_allele: str
    alternate_allele: str
    effect_allele: str
    other_allele: str
    beta_alt: float
    se: float
    p: float
    eaf_alt: float | None
    rsid: str
    variant_id: str

    @property
    def key(self) -> tuple[int, int, str, str]:
        return (self.chromosome, self.position, self.reference_allele, self.alternate_allele)


def open_text(path: pathlib.Path) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open("r", encoding="utf-8", newline="")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def normalize_chromosome(value: str) -> int:
    text = value.strip().lower()
    if text.startswith("chr"):
        text = text[3:]
    mapping = {"x": 23, "y": 24, "m": 25, "mt": 25}
    if text in mapping:
        return mapping[text]
    chromosome = int(text)
    if chromosome < 1 or chromosome > 25:
        raise RowError("invalid_chromosome")
    return chromosome


def parse_variant_id(value: str) -> tuple[int, int, str, str]:
    parts = value.strip().split("_")
    if len(parts) != 4:
        raise RowError("invalid_variant_id")
    chromosome = normalize_chromosome(parts[0])
    position = int(parts[1])
    reference = parts[2].upper()
    alternate = parts[3].upper()
    if not reference or not alternate or reference == alternate:
        raise RowError("invalid_variant_alleles")
    return chromosome, position, reference, alternate


def finite_float(value: str, code: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise RowError(code) from exc
    if not math.isfinite(number):
        raise RowError(code)
    return number


def parse_row(row: dict[str, str]) -> Record:
    required = (
        "chromosome", "base_pair_location", "effect_allele", "other_allele",
        "odds_ratio", "standard_error", "p_value", "variant_id",
    )
    if any(not row.get(field) for field in required):
        raise RowError("missing_required_field")

    chromosome, position, reference, alternate = parse_variant_id(row["variant_id"])
    if normalize_chromosome(row["chromosome"]) != chromosome:
        raise RowError("chromosome_mismatch")
    if int(row["base_pair_location"]) != position:
        raise RowError("position_mismatch")

    effect = row["effect_allele"].upper()
    other = row["other_allele"].upper()
    if {effect, other} != {reference, alternate}:
        raise RowError("allele_set_mismatch")

    odds_ratio = finite_float(row["odds_ratio"], "invalid_odds_ratio")
    se = finite_float(row["standard_error"], "invalid_standard_error")
    p_value = finite_float(row["p_value"], "invalid_p_value")
    if odds_ratio <= 0:
        raise RowError("invalid_odds_ratio")
    if se <= 0:
        raise RowError("invalid_standard_error")
    if p_value < 0 or p_value > 1:
        raise RowError("invalid_p_value")

    beta = math.log(odds_ratio)
    if effect == alternate:
        beta_alt = beta
        orientation = "ALT"
    elif effect == reference:
        beta_alt = -beta
        orientation = "REF"
    else:  # guarded by allele-set check, retained for explicitness
        raise RowError("effect_allele_unresolved")

    eaf_alt: float | None = None
    eaf_text = row.get("effect_allele_frequency", "")
    if eaf_text not in {"", "NA", "NaN", "nan"}:
        eaf = finite_float(eaf_text, "invalid_eaf")
        if eaf < 0 or eaf > 1:
            raise RowError("invalid_eaf")
        eaf_alt = eaf if orientation == "ALT" else 1.0 - eaf

    return Record(
        chromosome=chromosome,
        position=position,
        reference_allele=reference,
        alternate_allele=alternate,
        effect_allele=effect,
        other_allele=other,
        beta_alt=beta_alt,
        se=se,
        p=p_value,
        eaf_alt=eaf_alt,
        rsid=row.get("rsid", "") or "",
        variant_id=row["variant_id"],
    )


def iter_unique_records(path: pathlib.Path, skip_mhc: bool, stats: dict[str, object]) -> Iterator[Record]:
    error_counts: Counter[str] = Counter()
    orientation_counts: Counter[str] = Counter()
    stats.update({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    previous_coordinate: tuple[int, int] | None = None
    group: dict[tuple[int, int, str, str], Record] = {}
    duplicated_keys: set[tuple[int, int, str, str]] = set()

    def flush_group() -> list[Record]:
        output: list[Record] = []
        for key in sorted(group):
            record = group[key]
            if key in duplicated_keys:
                stats["duplicate_canonical_keys_excluded"] = int(stats.get("duplicate_canonical_keys_excluded", 0)) + 1
            elif skip_mhc and record.chromosome == MHC_CHR and MHC_START <= record.position <= MHC_END:
                stats["mhc_rows_excluded"] = int(stats.get("mhc_rows_excluded", 0)) + 1
            else:
                stats["unique_rows_emitted"] = int(stats.get("unique_rows_emitted", 0)) + 1
                output.append(record)
        return output

    with open_text(path) as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        stats["header"] = reader.fieldnames
        if not reader.fieldnames:
            raise RuntimeError(f"No header in {path}")
        for row in reader:
            stats["total_rows"] = int(stats.get("total_rows", 0)) + 1
            try:
                record = parse_row(row)
            except (RowError, ValueError) as exc:
                error_counts[getattr(exc, "code", "unclassified_parse_error")] += 1
                continue

            coordinate = (record.chromosome, record.position)
            if previous_coordinate is not None and coordinate < previous_coordinate:
                raise RuntimeError(f"Input is not sorted by chromosome/position: {coordinate} after {previous_coordinate} in {path}")
            orientation_counts["effect_is_ALT" if record.effect_allele == record.alternate_allele else "effect_is_REF"] += 1
            stats["parsed_rows"] = int(stats.get("parsed_rows", 0)) + 1

            if previous_coordinate is not None and coordinate != previous_coordinate:
                yield from flush_group()
                group.clear()
                duplicated_keys.clear()
            previous_coordinate = coordinate
            if record.key in group:
                duplicated_keys.add(record.key)
            else:
                group[record.key] = record

    if group:
        yield from flush_group()

    stats["parse_error_counts"] = dict(sorted(error_counts.items()))
    stats["effect_orientation_counts"] = dict(sorted(orientation_counts.items()))


def exact_merge(
    left_path: pathlib.Path,
    right_path: pathlib.Path,
    skip_mhc: bool,
    left_stats: dict[str, object],
    right_stats: dict[str, object],
    merge_stats: dict[str, int],
) -> Iterator[tuple[Record, Record]]:
    left_iterator = iter_unique_records(left_path, skip_mhc, left_stats)
    right_iterator = iter_unique_records(right_path, skip_mhc, right_stats)
    left = next(left_iterator, None)
    right = next(right_iterator, None)
    while left is not None and right is not None:
        if left.key == right.key:
            merge_stats["exact_shared"] += 1
            yield left, right
            left = next(left_iterator, None)
            right = next(right_iterator, None)
        elif left.key < right.key:
            merge_stats["eomg_only"] += 1
            left = next(left_iterator, None)
        else:
            merge_stats["lomg_only"] += 1
            right = next(right_iterator, None)
    while left is not None:
        merge_stats["eomg_only"] += 1
        left = next(left_iterator, None)
    while right is not None:
        merge_stats["lomg_only"] += 1
        right = next(right_iterator, None)


def heterogeneity_row(eomg: Record, lomg: Record) -> dict[str, object]:
    delta = eomg.beta_alt - lomg.beta_alt
    se_delta = math.sqrt(eomg.se * eomg.se + lomg.se * lomg.se)
    z = delta / se_delta
    p_het = math.erfc(abs(z) / math.sqrt(2.0))
    rsid = eomg.rsid if eomg.rsid == lomg.rsid else eomg.rsid or lomg.rsid
    return {
        "chromosome": eomg.chromosome,
        "position": eomg.position,
        "reference_allele": eomg.reference_allele,
        "alternate_allele": eomg.alternate_allele,
        "variant_id": eomg.variant_id,
        "rsid": rsid,
        "rsid_EOMG": eomg.rsid,
        "rsid_LOMG": lomg.rsid,
        "effect_allele_EOMG": eomg.effect_allele,
        "effect_allele_LOMG": lomg.effect_allele,
        "beta_EOMG_ALT": eomg.beta_alt,
        "se_EOMG": eomg.se,
        "p_EOMG": eomg.p,
        "eaf_EOMG_ALT": eomg.eaf_alt,
        "beta_LOMG_ALT": lomg.beta_alt,
        "se_LOMG": lomg.se,
        "p_LOMG": lomg.p,
        "eaf_LOMG_ALT": lomg.eaf_alt,
        "delta_beta_E_minus_L": delta,
        "se_delta": se_delta,
        "z_het": z,
        "p_het": p_het,
    }


def write_tsv(path: pathlib.Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_significant_regions(rows: list[dict[str, object]], maximum_gap: int = 1_000_000) -> list[dict[str, object]]:
    grouped: list[list[dict[str, object]]] = []
    for row in sorted(rows, key=lambda item: (int(item["chromosome"]), int(item["position"]))):
        if not grouped:
            grouped.append([row])
            continue
        prior = grouped[-1][-1]
        if int(row["chromosome"]) == int(prior["chromosome"]) and int(row["position"]) - int(prior["position"]) <= maximum_gap:
            grouped[-1].append(row)
        else:
            grouped.append([row])
    output = []
    for index, group in enumerate(grouped, start=1):
        lead = min(group, key=lambda item: float(item["p_het"]))
        output.append(
            {
                "descriptive_region_id": f"HETR{index:03d}",
                "chromosome": lead["chromosome"],
                "start": min(int(item["position"]) for item in group),
                "end": max(int(item["position"]) for item in group),
                "lead_variant_id": lead["variant_id"],
                "lead_rsid": lead["rsid"],
                "lead_p_het": lead["p_het"],
                "significant_variant_count": len(group),
                "grouping_rule": f"distance_only_max_gap_{maximum_gap}; not LD independence",
            }
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eomg", type=pathlib.Path, required=True)
    parser.add_argument("--lomg", type=pathlib.Path, required=True)
    parser.add_argument("--out-prefix", type=pathlib.Path, required=True)
    parser.add_argument("--top-n", type=int, default=2000)
    parser.add_argument("--candidate-p", type=float, default=1e-5)
    parser.add_argument("--include-mhc", action="store_true")
    args = parser.parse_args()
    if args.top_n < 1 or not 0 < args.candidate_p <= 1:
        raise SystemExit("Invalid --top-n or --candidate-p")
    for path in (args.eomg, args.lomg):
        if not path.is_file():
            raise FileNotFoundError(path)

    args.out_prefix.parent.mkdir(parents=True, exist_ok=True)
    eomg_stats: dict[str, object] = {}
    lomg_stats: dict[str, object] = {}
    merge_stats: defaultdict[str, int] = defaultdict(int)
    top_heap: list[tuple[float, int, dict[str, object]]] = []
    candidates: list[dict[str, object]] = []
    known: dict[str, dict[str, object]] = {}
    chromosome_shared: Counter[int] = Counter()
    chromosome_minimum: dict[int, float] = {}
    p_bin_counts: Counter[str] = Counter()
    sum_z = 0.0
    sum_z_squared = 0.0
    sequence = 0

    for eomg, lomg in exact_merge(
        args.eomg, args.lomg, not args.include_mhc, eomg_stats, lomg_stats, merge_stats
    ):
        row = heterogeneity_row(eomg, lomg)
        p_value = float(row["p_het"])
        z_value = float(row["z_het"])
        sequence += 1
        chromosome = int(row["chromosome"])
        chromosome_shared[chromosome] += 1
        chromosome_minimum[chromosome] = min(chromosome_minimum.get(chromosome, 1.0), p_value)
        sum_z += z_value
        sum_z_squared += z_value * z_value
        for threshold in P_BINS:
            if p_value < threshold:
                p_bin_counts[f"p_lt_{threshold:g}"] += 1
        if p_value <= args.candidate_p:
            candidates.append(row)
        if str(row["rsid"]) in KNOWN_RSIDS:
            known[str(row["rsid"])] = row
        item = (-p_value, sequence, row)
        if len(top_heap) < args.top_n:
            heapq.heappush(top_heap, item)
        elif p_value < -top_heap[0][0]:
            heapq.heapreplace(top_heap, item)

    tested = merge_stats["exact_shared"]
    if tested == 0:
        raise RuntimeError("No exact shared testable variants; check schema, build and sorting")
    bonferroni_threshold = 0.05 / tested
    fields = list(heterogeneity_row(
        Record(1, 1, "A", "G", "G", "A", 0, 1, 1, None, "", "1_1_A_G"),
        Record(1, 1, "A", "G", "G", "A", 0, 1, 1, None, "", "1_1_A_G"),
    ).keys()) + ["p_het_bonferroni_all_shared", "genomewide_heterogeneity_pass"]

    def finalize(row: dict[str, object]) -> dict[str, object]:
        result = dict(row)
        result["p_het_bonferroni_all_shared"] = min(1.0, float(row["p_het"]) * tested)
        result["genomewide_heterogeneity_pass"] = float(row["p_het"]) <= bonferroni_threshold
        return result

    candidates_final = [finalize(row) for row in sorted(candidates, key=lambda item: float(item["p_het"]))]
    top_final = [finalize(item[2]) for item in sorted(top_heap, key=lambda item: -item[0])]
    known_final = [finalize(known[rsid]) for rsid in sorted(KNOWN_RSIDS) if rsid in known]
    significant = [row for row in candidates_final if bool(row["genomewide_heterogeneity_pass"])]
    regions = group_significant_regions(significant)

    prefix = args.out_prefix
    write_tsv(pathlib.Path(str(prefix) + ".top.tsv"), top_final, fields)
    write_tsv(pathlib.Path(str(prefix) + ".candidates.tsv"), candidates_final, fields)
    write_tsv(pathlib.Path(str(prefix) + ".known_loci.tsv"), known_final, fields)
    write_tsv(pathlib.Path(str(prefix) + ".significant_variants.tsv"), significant, fields)
    region_fields = [
        "descriptive_region_id", "chromosome", "start", "end", "lead_variant_id",
        "lead_rsid", "lead_p_het", "significant_variant_count", "grouping_rule",
    ]
    write_tsv(pathlib.Path(str(prefix) + ".significant_regions.tsv"), regions, region_fields)
    chromosome_rows = [
        {
            "chromosome": chromosome,
            "exact_shared_testable_variants": chromosome_shared[chromosome],
            "minimum_p_het": chromosome_minimum[chromosome],
        }
        for chromosome in sorted(chromosome_shared)
    ]
    write_tsv(
        pathlib.Path(str(prefix) + ".chromosome_summary.tsv"),
        chromosome_rows,
        ["chromosome", "exact_shared_testable_variants", "minimum_p_het"],
    )

    mean_z = sum_z / tested
    mean_chi_squared = sum_z_squared / tested
    variance_z = max(0.0, sum_z_squared / tested - mean_z * mean_z)
    summary = {
        "schema_version": "2.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "method": "independent-sample ALT-aligned log(OR) difference z test",
        "variant_identity": "canonical GRCh38 chromosome_position_REF_ALT parsed from variant_id",
        "mhc_excluded": not args.include_mhc,
        "mhc_interval": None if args.include_mhc else "GRCh38 chr6:25000000-35000000 inclusive",
        "exact_shared_testable_variants": tested,
        "bonferroni_alpha": 0.05,
        "genomewide_heterogeneity_threshold": bonferroni_threshold,
        "candidate_p_threshold": args.candidate_p,
        "candidate_count": len(candidates_final),
        "genomewide_significant_variant_count": len(significant),
        "descriptive_significant_region_count": len(regions),
        "known_loci_found": [str(row["rsid"]) for row in known_final],
        "known_loci_missing": sorted(KNOWN_RSIDS - set(known)),
        "z_calibration": {
            "mean_z": mean_z,
            "variance_z": variance_z,
            "mean_chi_squared": mean_chi_squared,
            "warning": "Descriptive calibration only; not an LD-score intercept and not corrected for residual sample overlap.",
        },
        "p_value_counts": dict(p_bin_counts),
        "eomg_input": eomg_stats,
        "lomg_input": lomg_stats,
        "merge": dict(merge_stats),
    }
    pathlib.Path(str(prefix) + ".summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
