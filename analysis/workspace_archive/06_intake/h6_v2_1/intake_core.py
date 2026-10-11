#!/usr/bin/env python3
"""Stream and gate a sex-specific SSc summary-statistics file.

The script performs an intake audit only. It never runs fine-mapping or
colocalization, and it never invents missing alleles, standard errors, sample
sizes, or genome builds.
"""

from __future__ import annotations

import argparse
import bz2
import csv
import gzip
import hashlib
import json
import lzma
import math
import pathlib
import re
import sys
from collections import Counter
from datetime import datetime, timezone


ALIASES = {
    "chromosome": ["chromosome", "chrom", "chr"],
    "position": ["base_pair_location", "base_pair_position", "position", "pos", "bp"],
    "variant_id": ["variant_id", "snp", "rsid", "rs_id", "markername", "marker"],
    "effect_allele": ["effect_allele", "ea", "a1", "coded_allele"],
    "other_allele": ["other_allele", "non_effect_allele", "nea", "a2", "noncoded_allele"],
    "reference_allele": ["reference_allele", "ref"],
    "alternate_allele": ["alternate_allele", "alt"],
    "beta": ["beta", "effect_size", "log_odds", "log_or", "estimate"],
    "odds_ratio": ["odds_ratio", "or"],
    "standard_error": ["standard_error", "se", "stderr", "std_err"],
    "p_value": ["p_value", "p", "pval", "pvalue"],
    "effect_allele_frequency": ["effect_allele_frequency", "eaf", "effect_af", "a1freq", "a1_freq"],
    "info": ["info", "imputation_info", "info_score", "imputation_quality", "rsq"],
    # Bare `N` is intentionally absent. The v2.1 wrapper adds it to exactly
    # one semantic class only when provider metadata explicitly defines it.
    "sample_size": ["sample_size", "n_total", "total_n", "n_eff", "neff"],
    "cohort_count": ["cohort_count", "n_studies", "nstudies", "study_count"],
}

GRCH38_LEADS = {
    "rs12203592": ("6", 396_321, "IRF4"),
    "rs66578187": ("22", 39_328_807, "chr22/SYNGR1-RPL3-PDGFB"),
}

DEFAULT_REGIONS = {
    "IRF4_pm1Mb_GRCh38": ("6", 1, 1_396_321),
    "chr22_pm1Mb_GRCh38": ("22", 38_328_807, 40_328_807),
}

SUPPORTED_EFFECT_SCALES = {
    "beta": "beta",
    "log_odds": "beta",
    "odds_ratio": "odds_ratio",
}

GRCH38_ASSEMBLY_LABELS = {"grch38", "hg38"}
VALID_CHROMS = {str(value) for value in range(1, 23)} | {"x", "y", "m", "mt"}
GRCH38_CHROM_LENGTHS = {
    "1": 248_956_422, "2": 242_193_529, "3": 198_295_559, "4": 190_214_555,
    "5": 181_538_259, "6": 170_805_979, "7": 159_345_973, "8": 145_138_636,
    "9": 138_394_717, "10": 133_797_422, "11": 135_086_622, "12": 133_275_309,
    "13": 114_364_328, "14": 107_043_718, "15": 101_991_189, "16": 90_338_345,
    "17": 83_257_441, "18": 80_373_285, "19": 58_617_616, "20": 64_444_167,
    "21": 46_709_983, "22": 50_818_468, "x": 156_040_895, "y": 57_227_415,
    "m": 16_569, "mt": 16_569,
}


def normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower().lstrip("#")).strip("_")


def open_text(path: pathlib.Path):
    suffix = path.name.lower()
    if suffix.endswith((".gz", ".bgz")):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="")
    if suffix.endswith(".bz2"):
        return bz2.open(path, "rt", encoding="utf-8", errors="replace", newline="")
    if suffix.endswith((".xz", ".lzma")):
        return lzma.open(path, "rt", encoding="utf-8", errors="replace", newline="")
    return path.open("rt", encoding="utf-8", errors="replace", newline="")


def file_digests(path: pathlib.Path) -> dict[str, str]:
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            sha256.update(block)
            md5.update(block)
    return {"sha256": sha256.hexdigest(), "md5": md5.hexdigest()}


def first_data_line(handle) -> tuple[list[str], str]:
    comments = []
    for line in handle:
        stripped = line.strip("\r\n")
        if not stripped:
            continue
        if stripped.startswith("##"):
            comments.append(stripped)
            continue
        return comments, stripped
    raise ValueError("No header line found")


def choose_delimiter(header_line: str) -> str:
    if "\t" in header_line:
        return "tab"
    if "," in header_line:
        return "comma"
    return "whitespace"


def split_line(line: str, delimiter: str) -> list[str]:
    if delimiter == "tab":
        return line.rstrip("\r\n").split("\t")
    if delimiter == "comma":
        return next(csv.reader([line]))
    return re.split(r"\s+", line.strip())


def canonical_mapping(header: list[str]) -> tuple[dict[str, int], dict[str, list[str]]]:
    normalized = [normalize_header(x) for x in header]
    mapping: dict[str, int] = {}
    ambiguous: dict[str, list[str]] = {}
    for canonical, aliases in ALIASES.items():
        hits = [i for i, value in enumerate(normalized) if value in aliases]
        if len(hits) == 1:
            mapping[canonical] = hits[0]
        elif len(hits) > 1:
            ambiguous[canonical] = [header[i] for i in hits]
    return mapping, ambiguous


def clean_chrom(value: str) -> str:
    v = value.strip().lower().removeprefix("chr")
    if v == "23":
        return "x"
    return v


def is_missing(value: str) -> bool:
    return value.strip().lower() in {"", ".", "na", "nan", "null", "none"}


def parse_float(value: str) -> float:
    return float(value.strip())


def normalize_metadata_token(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def effect_scale_gate(metadata: dict, mapping: dict[str, int]) -> tuple[str, str | None, str]:
    raw = metadata.get("effect_scale")
    if raw is None or not str(raw).strip():
        return "MISSING", None, "effect_scale is required"
    normalized = normalize_metadata_token(raw)
    effect_column = SUPPORTED_EFFECT_SCALES.get(normalized)
    if effect_column is None:
        allowed = ", ".join(sorted(SUPPORTED_EFFECT_SCALES))
        return "UNSUPPORTED", None, f"unsupported effect_scale; use one of: {allowed}"
    if effect_column not in mapping:
        return (
            "INCONSISTENT_WITH_COLUMNS",
            effect_column,
            f"effect_scale={normalized} requires a mapped {effect_column} column",
        )
    return "PASS", effect_column, f"effect_scale={normalized} uses {effect_column}"


def assembly_gate(metadata: dict) -> tuple[str, str]:
    raw = metadata.get("assembly")
    if raw is None or not str(raw).strip():
        return "MISSING", "assembly is required and must be GRCh38 or hg38"
    normalized = normalize_metadata_token(raw)
    if normalized not in GRCH38_ASSEMBLY_LABELS:
        return "MISMATCH", f"assembly={raw!s} does not match the frozen GRCh38/hg38 windows"
    return "PASS", f"assembly={raw!s} matches the frozen GRCh38/hg38 windows"


def checksum_gate(
    metadata: dict,
    sha256_digest: str | None,
    md5_digest: str | None,
) -> dict[str, str]:
    raw_sha256 = metadata.get("expected_sha256")
    raw_md5 = metadata.get("expected_md5")

    if raw_sha256 is None or not str(raw_sha256).strip():
        sha256_status = "NOT_PROVIDED"
    elif not re.fullmatch(r"[0-9a-fA-F]{64}", str(raw_sha256).strip()):
        sha256_status = "INVALID_EXPECTED_SHA256"
    elif sha256_digest is None:
        sha256_status = "NOT_COMPUTED"
    elif sha256_digest.lower() != str(raw_sha256).strip().lower():
        sha256_status = "MISMATCH"
    else:
        sha256_status = "PASS"

    if raw_md5 is None or not str(raw_md5).strip():
        md5_status = "NOT_PROVIDED"
    elif not re.fullmatch(r"[0-9a-fA-F]{32}", str(raw_md5).strip()):
        md5_status = "INVALID_EXPECTED_MD5"
    elif md5_digest is None:
        md5_status = "NOT_COMPUTED"
    elif md5_digest.lower() != str(raw_md5).strip().lower():
        md5_status = "MISMATCH"
    else:
        md5_status = "PASS"

    if sha256_status == "NOT_PROVIDED" and md5_status == "NOT_PROVIDED":
        status = "HOLD_NO_TRUSTED_EXPECTED_CHECKSUM"
    elif sha256_status not in {"PASS", "NOT_PROVIDED"}:
        status = f"HOLD_SHA256_{sha256_status}"
    elif md5_status not in {"PASS", "NOT_PROVIDED"}:
        status = f"HOLD_MD5_{md5_status}"
    elif sha256_status == "PASS" and md5_status == "PASS":
        status = "PASS_SHA256_AND_MD5"
    elif sha256_status == "PASS":
        status = "PASS_SHA256"
    else:
        status = "PASS_MD5"

    return {
        "status": status,
        "sha256_status": sha256_status,
        "md5_status": md5_status,
        "detail": (
            "At least one trusted expected_sha256 or expected_md5 is required. Every supplied "
            "checksum is computed and must match."
        ),
    }


def sample_design_gate(metadata: dict, mapping: dict[str, int], missing: Counter, invalid: Counter) -> dict[str, object]:
    per_variant_n = (
        "sample_size" in mapping
        and missing["sample_size"] == 0
        and invalid["sample_size"] == 0
    )
    per_variant_cohorts = (
        "cohort_count" in mapping
        and missing["cohort_count"] == 0
        and invalid["cohort_count"] == 0
    )
    cases = metadata.get("cases")
    controls = metadata.get("controls")
    total = metadata.get("total_sample_size")
    counts_numeric = all(
        isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0
        for value in (cases, controls)
    )
    total_auditable = (
        counts_numeric
        and isinstance(total, (int, float))
        and not isinstance(total, bool)
        and total > 0
        and abs(float(total) - float(cases) - float(controls)) < 1e-9
    )

    if per_variant_n:
        status = "PASS_PER_VARIANT_SAMPLE_SIZE"
    elif per_variant_cohorts and counts_numeric:
        status = "PASS_PER_VARIANT_COHORT_COUNT_WITH_METADATA_CASE_CONTROL_COUNTS"
    elif metadata.get("variant_sample_size_constant") is True and total_auditable:
        status = "PASS_DECLARED_CONSTANT_WITH_AUDITABLE_TOTAL"
    elif counts_numeric:
        status = "CONDITIONAL_METADATA_COUNTS_WITHOUT_PER_VARIANT_DESIGN"
    else:
        status = "MISSING_SAMPLE_DESIGN"

    return {
        "status": status,
        "pass": status.startswith("PASS"),
        "per_variant_sample_size": per_variant_n,
        "per_variant_cohort_count": per_variant_cohorts,
        "variant_sample_size_constant": metadata.get("variant_sample_size_constant") is True,
        "auditable_fixed_total": total_auditable,
    }


def canonical_variant_key(
    chrom: str,
    pos: int,
    get,
    allele_partner_fields: tuple[str, ...],
) -> str | None:
    """Return an order-independent locus/allele key for regional duplicate checks."""
    if not chrom or pos is None or is_missing(get("effect_allele")):
        return None
    if allele_partner_fields == ("other_allele",):
        if is_missing(get("other_allele")):
            return None
        alleles = [get("effect_allele").upper(), get("other_allele").upper()]
    else:
        if any(is_missing(get(name)) for name in allele_partner_fields):
            return None
        alleles = [get("reference_allele").upper(), get("alternate_allele").upper()]
    first, second = sorted(alleles)
    return f"{chrom}:{pos}:{first}:{second}"


def load_metadata(path: pathlib.Path | None) -> dict:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Metadata JSON must contain an object")
    return data


def audit(args: argparse.Namespace) -> dict:
    input_path = pathlib.Path(args.input).resolve()
    output_dir = pathlib.Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = pathlib.Path(args.metadata).resolve() if args.metadata else None
    label = str(args.label)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", label) or ".." in label:
        raise ValueError("Unsafe output label")
    planned_outputs = {
        *(output_dir / f"{label}_{name}.tsv" for name in DEFAULT_REGIONS),
        output_dir / f"{label}_intake_audit.json",
        output_dir / f"{label}_intake_audit.md",
    }
    protected_inputs = {input_path}
    if metadata_path is not None:
        protected_inputs.add(metadata_path)
    if any(path.resolve() in protected_inputs for path in planned_outputs):
        raise ValueError("An output path collides with the input or metadata file")
    metadata = load_metadata(metadata_path)
    digests = {"sha256": None, "md5": None} if args.skip_hash else file_digests(input_path)

    with open_text(input_path) as handle:
        comments, header_line = first_data_line(handle)
        delimiter = choose_delimiter(header_line)
        header = split_line(header_line, delimiter)
        mapping, ambiguous = canonical_mapping(header)
        header_decode_replacement = any("\ufffd" in value for value in header)
        header_control_character = any(
            any(ord(character) < 32 for character in value) for value in header
        )

        required_core = {"chromosome", "position", "effect_allele", "standard_error", "p_value"}
        if "other_allele" in mapping:
            allele_partner_fields: tuple[str, ...] = ("other_allele",)
        elif {"reference_allele", "alternate_allele"}.issubset(mapping):
            allele_partner_fields = ("reference_allele", "alternate_allele")
        else:
            allele_partner_fields = ()
        allele_partner_ok = bool(allele_partner_fields)
        effect_scale_status, effect_column, effect_scale_detail = effect_scale_gate(metadata, mapping)
        core_columns_pass = (
            required_core.issubset(mapping)
            and allele_partner_ok
            and effect_scale_status == "PASS"
            and not ambiguous
        )
        core_row_fields = set(required_core)
        core_row_fields.update(allele_partner_fields)
        if effect_column:
            core_row_fields.add(effect_column)

        missing_counts = Counter()
        core_missing_counts = Counter()
        invalid_counts = Counter()
        total_rows = 0
        malformed_rows = 0
        region_rows = {name: [] for name in DEFAULT_REGIONS}
        lead_records: dict[str, list[dict[str, str]]] = {rsid: [] for rsid in GRCH38_LEADS}
        region_keys = {name: set() for name in DEFAULT_REGIONS}
        region_duplicate_counts = Counter()
        region_duplicate_examples: dict[str, list[str]] = {name: [] for name in DEFAULT_REGIONS}

        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            total_rows += 1
            fields = split_line(line, delimiter)
            if len(fields) != len(header):
                malformed_rows += 1
                continue
            if any("\ufffd" in value for value in fields):
                invalid_counts["utf8_decode_replacement"] += 1
            if any(any(ord(character) < 32 for character in value) for value in fields):
                invalid_counts["control_character"] += 1

            def get(name: str) -> str:
                return fields[mapping[name]] if name in mapping else ""

            for field_name in mapping:
                if is_missing(get(field_name)):
                    missing_counts[field_name] += 1

            if core_columns_pass:
                for field_name in core_row_fields:
                    if is_missing(get(field_name)):
                        core_missing_counts[field_name] += 1

            chrom = clean_chrom(get("chromosome")) if "chromosome" in mapping else ""
            if chrom and chrom not in VALID_CHROMS:
                invalid_counts["chromosome"] += 1
            try:
                if "position" not in mapping or is_missing(get("position")):
                    pos = None
                else:
                    numeric_pos = parse_float(get("position"))
                    if not math.isfinite(numeric_pos) or numeric_pos <= 0 or not numeric_pos.is_integer():
                        raise ValueError
                    pos = int(numeric_pos)
            except (ValueError, OverflowError):
                invalid_counts["position"] += 1
                pos = None
            if pos is not None and chrom in GRCH38_CHROM_LENGTHS and pos > GRCH38_CHROM_LENGTHS[chrom]:
                invalid_counts["position"] += 1
                pos = None

            for name in ("standard_error", "p_value", "beta", "odds_ratio", "effect_allele_frequency", "info", "sample_size", "cohort_count"):
                if name not in mapping or is_missing(get(name)):
                    continue
                try:
                    value = parse_float(get(name))
                    if not math.isfinite(value):
                        invalid_counts[name] += 1
                    elif name == "standard_error" and value <= 0:
                        invalid_counts[name] += 1
                    elif name == "p_value" and not (0 <= value <= 1):
                        invalid_counts[name] += 1
                    elif name == "odds_ratio" and value <= 0:
                        invalid_counts[name] += 1
                    elif name in {"effect_allele_frequency", "info"} and not (0 <= value <= 1):
                        invalid_counts[name] += 1
                    elif name in {"sample_size", "cohort_count"} and value <= 0:
                        invalid_counts[name] += 1
                    elif name == "cohort_count" and not value.is_integer():
                        invalid_counts[name] += 1
                except ValueError:
                    invalid_counts[name] += 1

            for name in ("effect_allele", "other_allele", "reference_allele", "alternate_allele"):
                if name in mapping and not is_missing(get(name)):
                    allele = get(name).upper()
                    if not re.fullmatch(r"[ACGT]+", allele):
                        invalid_counts[name] += 1
            if "other_allele" in mapping and not is_missing(get("effect_allele")) and not is_missing(get("other_allele")):
                if get("effect_allele").upper() == get("other_allele").upper():
                    invalid_counts["allele_pair"] += 1
            if {"reference_allele", "alternate_allele"}.issubset(mapping):
                if not is_missing(get("reference_allele")) and not is_missing(get("alternate_allele")):
                    ref = get("reference_allele").upper()
                    alt = get("alternate_allele").upper()
                    if ref == alt:
                        invalid_counts["reference_alternate_pair"] += 1
                    if not is_missing(get("effect_allele")) and get("effect_allele").upper() not in {ref, alt}:
                        invalid_counts["effect_allele_not_ref_alt"] += 1

            row_out = {
                "chromosome": chrom,
                "position": "" if pos is None else str(pos),
                "variant_id": get("variant_id"),
                "effect_allele": get("effect_allele"),
                "other_allele": get("other_allele"),
                "reference_allele": get("reference_allele"),
                "alternate_allele": get("alternate_allele"),
                "beta": get("beta"),
                "odds_ratio": get("odds_ratio"),
                "standard_error": get("standard_error"),
                "p_value": get("p_value"),
                "effect_allele_frequency": get("effect_allele_frequency"),
                "info": get("info"),
                "sample_size": get("sample_size"),
                "cohort_count": get("cohort_count"),
            }

            variant_id = get("variant_id") if "variant_id" in mapping else ""
            if variant_id in lead_records:
                lead_records[variant_id].append(row_out.copy())

            if pos is not None:
                for region_name, (rchrom, start, end) in DEFAULT_REGIONS.items():
                    if chrom == rchrom and start <= pos <= end:
                        region_rows[region_name].append(row_out.copy())
                        key = canonical_variant_key(chrom, pos, get, allele_partner_fields)
                        if key is not None:
                            if key in region_keys[region_name]:
                                region_duplicate_counts[region_name] += 1
                                if len(region_duplicate_examples[region_name]) < 20:
                                    region_duplicate_examples[region_name].append(key)
                            region_keys[region_name].add(key)

            if args.max_rows and total_rows >= args.max_rows:
                break

    output_fields = [
        "chromosome", "position", "variant_id", "effect_allele", "other_allele",
        "reference_allele", "alternate_allele", "beta", "odds_ratio", "standard_error",
        "p_value", "effect_allele_frequency", "info", "sample_size", "cohort_count",
    ]
    for region_name, rows in region_rows.items():
        path = output_dir / f"{args.label}_{region_name}.tsv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=output_fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

    metadata_required = ["assembly", "ancestry", "stratum", "phenotype", "source_url", "effect_scale"]
    metadata_missing = [name for name in metadata_required if not metadata.get(name)]
    sample_design = sample_design_gate(metadata, mapping, missing_counts, invalid_counts)
    provenance_ok = bool(metadata.get("source_url")) and bool(
        metadata.get("accession") or metadata.get("provider")
    )
    assembly_status, assembly_detail = assembly_gate(metadata)
    checksum = checksum_gate(metadata, digests["sha256"], digests["md5"])
    target_presence = {rsid: len(records) for rsid, records in lead_records.items()}
    regional_presence_pass = all(len(rows) > 0 for rows in region_rows.values())
    regional_duplicates_pass = not any(region_duplicate_counts.values())
    core_values_pass = not any(core_missing_counts.values())
    diagnostic_only = bool(args.max_rows)

    paper_grade_fields = {
        "effect_allele_frequency": (
            "effect_allele_frequency" in mapping
            and missing_counts["effect_allele_frequency"] == 0
            and invalid_counts["effect_allele_frequency"] == 0
        ),
        "imputation_info": (
            "info" in mapping
            and missing_counts["info"] == 0
            and invalid_counts["info"] == 0
        ),
        "sample_design": bool(sample_design["pass"]),
        "assembly": assembly_status == "PASS",
        "effect_scale": effect_scale_status == "PASS",
        "provenance": provenance_ok,
        "checksum": str(checksum["status"]).startswith("PASS"),
        "complete_core_values": core_values_pass,
        "both_frozen_regions_present": regional_presence_pass,
        "unique_regional_variant_keys": regional_duplicates_pass,
        "full_file_scan": not diagnostic_only,
    }
    numerical_pass = malformed_rows == 0 and not any(invalid_counts.values())
    if diagnostic_only:
        status = "DIAGNOSTIC_ONLY_MAX_ROWS_NO_PAPER_GRADE_DECISION"
    elif effect_scale_status != "PASS":
        status = "HOLD_EFFECT_SCALE_UNSUPPORTED_OR_INCONSISTENT"
    elif not core_columns_pass:
        status = "HOLD_CORE_SCHEMA_MISSING_OR_AMBIGUOUS"
    elif not core_values_pass:
        status = "HOLD_CORE_VALUES_MISSING"
    elif not numerical_pass:
        status = "HOLD_INVALID_OR_MALFORMED_ROWS"
    elif assembly_status != "PASS":
        status = "HOLD_ASSEMBLY_MISSING_OR_MISMATCH"
    elif not str(checksum["status"]).startswith("PASS") or metadata_missing:
        status = "HOLD_METADATA_OR_CHECKSUM"
    elif not regional_presence_pass or not regional_duplicates_pass:
        status = "HOLD_REGIONAL_COVERAGE_OR_DUPLICATE_VARIANT_KEYS"
    elif all(paper_grade_fields.values()):
        status = "PASS_PAPER_GRADE_INTAKE_READY_FOR_HARMONIZATION"
    else:
        status = "CONDITIONAL_CORE_INTAKE_PASS_SUPPORT_FIELDS_INCOMPLETE"

    result = {
        "audit": "R4A9_H6_SEX_SPECIFIC_SUMSTATS_INTAKE",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "input": {
            "path": str(input_path),
            "bytes": input_path.stat().st_size,
            "sha256": digests["sha256"],
            "md5": digests["md5"],
            "label": args.label,
        },
        "metadata": metadata,
        "format": {
            "delimiter": delimiter,
            "header": header,
            "comment_header_lines": comments,
            "canonical_mapping": {name: header[index] for name, index in mapping.items()},
            "ambiguous_mappings": ambiguous,
            "header_decode_replacement": header_decode_replacement,
            "header_control_character": header_control_character,
        },
        "rows": {
            "scanned": total_rows,
            "malformed": malformed_rows,
            "missing_by_field": dict(missing_counts),
            "core_missing_by_field": dict(core_missing_counts),
            "invalid_by_field": dict(invalid_counts),
            "scan_mode": "DIAGNOSTIC_MAX_ROWS" if diagnostic_only else "FULL_FILE",
            "max_rows": args.max_rows,
        },
        "core_columns_pass": core_columns_pass,
        "core_values_pass": core_values_pass,
        "effect_scale_gate": {
            "status": effect_scale_status,
            "effect_column": effect_column,
            "detail": effect_scale_detail,
            "supported_values": sorted(SUPPORTED_EFFECT_SCALES),
        },
        "assembly_gate": {"status": assembly_status, "detail": assembly_detail},
        "checksum_gate": checksum,
        "sample_design_gate": sample_design,
        "paper_grade_support": paper_grade_fields,
        "metadata_missing": metadata_missing,
        "region_rows": {name: len(rows) for name, rows in region_rows.items()},
        "regional_presence_pass": regional_presence_pass,
        "regional_duplicate_keys_pass": regional_duplicates_pass,
        "region_duplicate_keys": {
            name: region_duplicate_counts[name] for name in DEFAULT_REGIONS
        },
        "region_duplicate_key_examples": region_duplicate_examples,
        "lead_variant_records": lead_records,
        "lead_variant_counts": target_presence,
        "next_step": (
            "Run reference/alternate normalization, build validation, coverage checks, and LD matching. "
            "Do not run fine-mapping or colocalization from this intake result alone."
        ),
    }
    return result


def write_report(result: dict, output_dir: pathlib.Path, label: str) -> None:
    json_path = output_dir / f"{label}_intake_audit.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    mapping_lines = "\n".join(
        f"- `{canonical}` ← `{source}`" for canonical, source in result["format"]["canonical_mapping"].items()
    ) or "- None"
    support_lines = "\n".join(
        f"- {name}: {'PASS' if value else 'MISSING'}" for name, value in result["paper_grade_support"].items()
    )
    region_lines = "\n".join(f"- {name}: {count:,}" for name, count in result["region_rows"].items())
    lead_lines = "\n".join(f"- {rsid}: {count}" for rsid, count in result["lead_variant_counts"].items())
    report = f"""# {label} sex-specific SSc summary-statistics intake audit

**Status:** `{result['status']}`

## Input

- File: `{result['input']['path']}`
- Bytes: {result['input']['bytes']:,}
- SHA-256: `{result['input']['sha256']}`
- MD5: `{result['input']['md5']}`
- Rows scanned: {result['rows']['scanned']:,}
- Malformed rows: {result['rows']['malformed']:,}
- Scan mode: `{result['rows']['scan_mode']}`

## Hard-gate diagnostics

- Core columns: `{'PASS' if result['core_columns_pass'] else 'FAIL'}`
- Complete core values: `{'PASS' if result['core_values_pass'] else 'FAIL'}`; missing `{result['rows']['core_missing_by_field']}`
- Effect scale: `{result['effect_scale_gate']['status']}` — {result['effect_scale_gate']['detail']}
- Assembly: `{result['assembly_gate']['status']}` — {result['assembly_gate']['detail']}
- Checksum: `{result['checksum_gate']['status']}` — SHA-256 `{result['checksum_gate']['sha256_status']}`, MD5 `{result['checksum_gate']['md5_status']}`
- Sample design: `{result['sample_design_gate']['status']}`
- Both frozen regions present: `{'PASS' if result['regional_presence_pass'] else 'FAIL'}`
- Regional variant keys unique: `{'PASS' if result['regional_duplicate_keys_pass'] else 'FAIL'}`

## Canonical column mapping

{mapping_lines}

## Paper-grade support fields

{support_lines}

## Frozen regional extraction

{region_lines}

## Target lead records found

{lead_lines}

## Boundary

This is an intake and schema gate. A PASS does not establish disease–QTL colocalization. The next step is reference/alternate normalization, build verification, regional coverage review, ancestry-matched LD, and only then signal-level analysis.
"""
    (output_dir / f"{label}_intake_audit.md").write_text(report, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to summary-statistics file (.gz/.bgz/.bz2/.xz/plain)")
    parser.add_argument("--metadata", help="Path to metadata JSON")
    parser.add_argument("--label", required=True, help="Output label, e.g. female or male")
    parser.add_argument("--output-dir", required=True, help="Directory for audit and regional extracts")
    parser.add_argument("--skip-hash", action="store_true", help="Skip SHA-256 only for a quick local smoke test")
    parser.add_argument("--max-rows", type=int, default=0, help="Optional bounded smoke-test row count; zero scans all")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    output_dir = pathlib.Path(args.output_dir).resolve()
    try:
        result = audit(args)
        write_report(result, output_dir, args.label)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"].startswith(("PASS", "CONDITIONAL")) else 2
    except Exception as exc:
        output_dir.mkdir(parents=True, exist_ok=True)
        failure = {"audit": "R4A9_H6_SEX_SPECIFIC_SUMSTATS_INTAKE", "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
        (output_dir / f"{args.label}_intake_audit.json").write_text(
            json.dumps(failure, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
