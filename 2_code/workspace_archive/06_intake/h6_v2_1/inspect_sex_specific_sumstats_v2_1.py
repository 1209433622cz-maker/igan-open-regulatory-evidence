#!/usr/bin/env python3
"""R4A11 H6 v2.1: hardened two-level intake for sex-specific SSc statistics.

The program streams the whole file through ``intake_core`` and makes the
analysis decision only from explicit provenance, structural integrity, and
the two frozen regions.  A PASS authorizes harmonization and coverage review;
it is not a fine-mapping, colocalization, or C1 result.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pathlib
import re
import sys
from types import SimpleNamespace
from urllib.parse import urlparse


HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import intake_core as core


EXPLICIT_SAMPLE_ALIASES = {"sample_size", "n_total", "total_n", "n_eff", "neff"}
EXPLICIT_COHORT_ALIASES = {"cohort_count", "n_studies", "nstudies", "study_count"}
ALLOWED_BARE_N = {"sample_size", "cohort_count", "ignore"}
PLACEHOLDER_TOKENS = {"replace", "example.invalid", "placeholder", "todo", "unknown"}
STRUCTURAL_GLOBAL_FIELDS = {
    "chromosome", "position", "utf8_decode_replacement", "control_character",
}
TARGET_PHENOTYPE_TOKENS = {"systemic_sclerosis", "ssc"}
TARGET_STRATA = {"female", "male"}
TARGET_PMID = "41999721"
TARGET_DOI = "10.1016/s2665-9913(25)00376-5"
TARGET_ANALYSIS_TYPES = {"sex_stratified_case_control_gwas", "sex_stratified_gwas"}
TRANSFER_TYPES = {"public_catalog", "author_transfer"}
CHECKSUM_EVIDENCE_TYPES = {"provider_manifest", "repository_manifest", "author_manifest"}
TARGET_ANCESTRY_TOKENS = {
    "european", "european_ancestry", "predominantly_european",
    "predominantly_european_ancestry",
}
MIN_REGION_ROWS_FOR_PASS = 100
MIN_REGION_UNIQUE_POSITIONS_FOR_PASS = 100
MIN_REGION_POSITION_SPAN_BP_FOR_PASS = 250_000
REGION_ANCHORS = {
    "IRF4_pm1Mb_GRCh38": {
        "rsid": "rs12203592", "chromosome": "6", "position": 396_321,
        "alleles": {"C", "T"},
    },
    "chr22_pm1Mb_GRCh38": {
        "rsid": "rs66578187", "chromosome": "22", "position": 39_328_807,
        "alleles": {"A", "AT"},
    },
}


def norm(value: object) -> str:
    return core.normalize_metadata_token(value)


def missing(value: object) -> bool:
    return core.is_missing("" if value is None else str(value))


def read_header(input_path: pathlib.Path) -> list[str]:
    with core.open_text(input_path) as handle:
        _, header_line = core.first_data_line(handle)
    return core.split_line(header_line, core.choose_delimiter(header_line))


def configure_bare_n(header: list[str], metadata: dict) -> dict[str, object]:
    """Map bare N to exactly one canonical meaning, or leave it unmapped."""
    core.ALIASES["sample_size"] = [value for value in core.ALIASES["sample_size"] if value != "n"]
    core.ALIASES["cohort_count"] = [value for value in core.ALIASES["cohort_count"] if value != "n"]
    normalized = [core.normalize_header(value) for value in header]
    has_bare = "n" in normalized
    has_explicit_sample = any(value in EXPLICIT_SAMPLE_ALIASES for value in normalized)
    has_explicit_cohort = any(value in EXPLICIT_COHORT_ALIASES for value in normalized)
    declared = norm(metadata.get("bare_n_semantics", ""))

    if not has_bare:
        return {"status": "NOT_APPLICABLE", "pass": True, "declared": declared or None}
    if has_explicit_sample or has_explicit_cohort:
        return {
            "status": "PASS_BARE_N_LEFT_UNMAPPED_EXPLICIT_DESIGN_COLUMN_PRESENT",
            "pass": True,
            "declared": declared or None,
        }
    if declared not in ALLOWED_BARE_N:
        return {
            "status": "CONDITIONAL_BARE_N_SEMANTICS_UNDECLARED",
            "pass": False,
            "declared": declared or None,
        }
    if declared == "sample_size":
        core.ALIASES["sample_size"].append("n")
        status = "PASS_BARE_N_MAPPED_TO_SAMPLE_SIZE"
        passed = True
    elif declared == "cohort_count":
        core.ALIASES["cohort_count"].append("n")
        status = "PASS_BARE_N_MAPPED_TO_COHORT_COUNT"
        passed = True
    else:
        status = "CONDITIONAL_BARE_N_EXPLICITLY_IGNORED"
        passed = False
    return {"status": status, "pass": passed, "declared": declared}


def load_region(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def numeric_value(value: object) -> tuple[bool, float | None]:
    if missing(value):
        return False, None
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return False, None
    return math.isfinite(number), number


def audit_region(
    rows: list[dict[str, str]],
    effect_column: str,
    allele_mode: str,
    mapped_fields: set[str],
) -> dict[str, object]:
    required = ["chromosome", "position", "effect_allele", "standard_error", "p_value", effect_column]
    required += ["other_allele"] if allele_mode == "other" else ["reference_allele", "alternate_allele"]
    support = ["effect_allele_frequency", "info"]
    sample_fields = [value for value in ("sample_size", "cohort_count") if value in mapped_fields]
    all_fields = list(dict.fromkeys(required + support + sample_fields))
    missing_counts = {field: 0 for field in all_fields}
    invalid_counts = {field: 0 for field in all_fields}
    valid_positions: list[int] = []
    sample_values: dict[str, list[float]] = {field: [] for field in sample_fields}

    for row in rows:
        for field in all_fields:
            if missing(row.get(field, "")):
                missing_counts[field] += 1

        numeric_fields = ["position", "standard_error", "p_value", effect_column] + support + sample_fields
        numbers: dict[str, float] = {}
        for field in numeric_fields:
            if missing(row.get(field, "")):
                continue
            valid, number = numeric_value(row.get(field, ""))
            if not valid or number is None:
                invalid_counts[field] += 1
            else:
                numbers[field] = number

        if "position" in numbers and (numbers["position"] <= 0 or not numbers["position"].is_integer()):
            invalid_counts["position"] += 1
        elif "position" in numbers:
            valid_positions.append(int(numbers["position"]))
        if "standard_error" in numbers and numbers["standard_error"] <= 0:
            invalid_counts["standard_error"] += 1
        if "p_value" in numbers and not 0 <= numbers["p_value"] <= 1:
            invalid_counts["p_value"] += 1
        if effect_column == "odds_ratio" and effect_column in numbers and numbers[effect_column] <= 0:
            invalid_counts[effect_column] += 1
        for field in support:
            if field in numbers and not 0 <= numbers[field] <= 1:
                invalid_counts[field] += 1
        if "sample_size" in numbers and numbers["sample_size"] <= 0:
            invalid_counts["sample_size"] += 1
        if "cohort_count" in numbers and (
            numbers["cohort_count"] <= 0 or not numbers["cohort_count"].is_integer()
        ):
            invalid_counts["cohort_count"] += 1
        for field in sample_fields:
            if field in numbers and numbers[field] > 0:
                sample_values[field].append(numbers[field])

        if all(field in numbers for field in (effect_column, "standard_error", "p_value")):
            effect = numbers[effect_column]
            if effect_column == "odds_ratio":
                effect = math.log(effect) if effect > 0 else math.nan
            se = numbers["standard_error"]
            observed_p = numbers["p_value"]
            if math.isfinite(effect) and se > 0 and 0 <= observed_p <= 1:
                z_value = abs(effect / se)
                expected_p = math.erfc(z_value / math.sqrt(2.0))
                if observed_p == 0:
                    # A literal zero can be a legitimate numerical floor only for an
                    # extreme statistic.  It is impossible for a modest z score.
                    gross_inconsistency = z_value < 20.0
                else:
                    gross_inconsistency = (
                        (observed_p <= 5e-8 and z_value < 3.5)
                        or (observed_p >= 0.05 and z_value > 5.0)
                        or (
                            expected_p > 0
                        and abs(math.log10(observed_p) - math.log10(expected_p)) > 2.0
                        )
                    )
                if gross_inconsistency:
                    invalid_counts["effect_se_p_gross_inconsistency"] = (
                        invalid_counts.get("effect_se_p_gross_inconsistency", 0) + 1
                    )

        allele_fields = (
            ["effect_allele", "other_allele"]
            if allele_mode == "other"
            else ["effect_allele", "reference_allele", "alternate_allele"]
        )
        for field in allele_fields:
            value = str(row.get(field, "")).upper()
            if not missing(value) and not re.fullmatch(r"[ACGT]+", value):
                invalid_counts[field] += 1
        if allele_mode == "other" and all(not missing(row.get(field, "")) for field in allele_fields):
            if str(row["effect_allele"]).upper() == str(row["other_allele"]).upper():
                invalid_counts["allele_pair"] = invalid_counts.get("allele_pair", 0) + 1
        if allele_mode == "refalt" and all(not missing(row.get(field, "")) for field in allele_fields):
            effect = str(row["effect_allele"]).upper()
            ref = str(row["reference_allele"]).upper()
            alt = str(row["alternate_allele"]).upper()
            if ref == alt:
                invalid_counts["reference_alternate_pair"] = invalid_counts.get("reference_alternate_pair", 0) + 1
            if effect not in {ref, alt}:
                invalid_counts["effect_allele_not_ref_alt"] = invalid_counts.get("effect_allele_not_ref_alt", 0) + 1

    core_keys = set(required) | {
        "allele_pair", "reference_alternate_pair", "effect_allele_not_ref_alt",
        "effect_se_p_gross_inconsistency",
    }
    unique_positions = len(set(valid_positions))
    position_span_bp = max(valid_positions) - min(valid_positions) if valid_positions else 0
    return {
        "rows": len(rows),
        "unique_positions": unique_positions,
        "position_span_bp": position_span_bp,
        "missing": missing_counts,
        "invalid": invalid_counts,
        "core_missing": sum(missing_counts.get(field, 0) for field in required),
        "core_invalid": sum(invalid_counts.get(field, 0) for field in core_keys),
        "support_missing": {field: missing_counts.get(field, len(rows)) for field in support},
        "support_invalid": {field: invalid_counts.get(field, 0) for field in support},
        "sample_missing": {field: missing_counts.get(field, 0) for field in sample_fields},
        "sample_invalid": {field: invalid_counts.get(field, 0) for field in sample_fields},
        "sample_summary": {
            field: {
                "minimum": min(values) if values else None,
                "maximum": max(values) if values else None,
                "non_integer_count": sum(not value.is_integer() for value in values),
            }
            for field, values in sample_values.items()
        },
    }


def regional_density_gate(regions: dict[str, dict[str, object]]) -> dict[str, object]:
    details: dict[str, dict[str, object]] = {}
    for name, region in regions.items():
        rows_ok = int(region["rows"]) >= MIN_REGION_ROWS_FOR_PASS
        unique_ok = int(region["unique_positions"]) >= MIN_REGION_UNIQUE_POSITIONS_FOR_PASS
        span_ok = int(region["position_span_bp"]) >= MIN_REGION_POSITION_SPAN_BP_FOR_PASS
        details[name] = {
            "rows": region["rows"],
            "unique_positions": region["unique_positions"],
            "position_span_bp": region["position_span_bp"],
            "rows_ok": rows_ok,
            "unique_positions_ok": unique_ok,
            "position_span_ok": span_ok,
            "pass": rows_ok and unique_ok and span_ok,
        }
    passed = all(value["pass"] for value in details.values())
    return {
        "status": "PASS_REGIONAL_DENSITY_SANITY" if passed else "CONDITIONAL_REGIONAL_DENSITY_TOO_SPARSE",
        "pass": passed,
        "thresholds": {
            "minimum_rows_per_region": MIN_REGION_ROWS_FOR_PASS,
            "minimum_unique_positions_per_region": MIN_REGION_UNIQUE_POSITIONS_FOR_PASS,
            "minimum_position_span_bp_per_region": MIN_REGION_POSITION_SPAN_BP_FOR_PASS,
        },
        "details": details,
        "boundary": "This is a truncation/sparsity sentinel, not a reference-panel coverage estimate.",
    }


def positive_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and value > 0


def positive_integer(value: object) -> bool:
    return positive_number(value) and float(value).is_integer()


def sample_design_gate(
    regions: dict[str, dict[str, object]],
    mapped_fields: set[str],
    metadata: dict,
    bare_n_gate: dict[str, object],
    canonical_mapping: dict[str, str],
) -> dict[str, object]:
    if str(bare_n_gate["status"]).startswith("CONDITIONAL"):
        return {**bare_n_gate, "detail": "Bare N is not an auditable per-variant design field."}

    def region_field_complete(field: str) -> bool:
        return all(
            int(region["rows"]) > 0
            and int(region["sample_missing"].get(field, 0)) == 0
            and int(region["sample_invalid"].get(field, 0)) == 0
            for region in regions.values()
        )

    cases = metadata.get("cases")
    controls = metadata.get("controls")
    total = metadata.get("total_sample_size")
    global_counts_valid = (
        positive_integer(cases)
        and positive_integer(controls)
        and positive_integer(total)
        and abs(float(cases) + float(controls) - float(total)) < 1e-9
    )
    if not global_counts_valid:
        return {
            "status": "CONDITIONAL_GLOBAL_CASE_CONTROL_TOTAL_MISSING_OR_INCONSISTENT",
            "pass": False,
        }

    if "sample_size" in mapped_fields and region_field_complete("sample_size"):
        summaries = [region["sample_summary"]["sample_size"] for region in regions.values()]
        minimum_ok = all(float(summary["minimum"]) >= 2 for summary in summaries)
        maximum_ok = all(float(summary["maximum"]) <= float(total) for summary in summaries)
        sample_source = core.normalize_header(canonical_mapping.get("sample_size", ""))
        integer_required = (
            bare_n_gate.get("status") == "PASS_BARE_N_MAPPED_TO_SAMPLE_SIZE"
            or sample_source in {"sample_size", "n_total", "total_n"}
        )
        integer_ok = not (
            integer_required and any(int(summary["non_integer_count"]) > 0 for summary in summaries)
        )
        if minimum_ok and maximum_ok and integer_ok:
            return {"status": "PASS_FROZEN_REGION_PER_VARIANT_SAMPLE_SIZE", "pass": True}
        return {
            "status": "CONDITIONAL_PER_VARIANT_SAMPLE_SIZE_RANGE_OR_INTEGER_INVALID",
            "pass": False,
        }
    if "cohort_count" in mapped_fields and region_field_complete("cohort_count"):
        total_cohorts = metadata.get("total_cohort_count")
        summaries = [region["sample_summary"]["cohort_count"] for region in regions.values()]
        cohort_range_valid = (
            positive_integer(total_cohorts)
            and all(float(summary["minimum"]) >= 1 for summary in summaries)
            and all(float(summary["maximum"]) <= float(total_cohorts) for summary in summaries)
            and all(int(summary["non_integer_count"]) == 0 for summary in summaries)
        )
        if global_counts_valid and cohort_range_valid:
            return {"status": "PASS_FROZEN_REGION_COHORT_COUNT_WITH_CASE_CONTROL_METADATA", "pass": True}
        return {
            "status": "CONDITIONAL_COHORT_COUNT_WITHOUT_VALID_COUNTS_OR_COHORT_BOUND",
            "pass": False,
        }

    fixed_total = (
        metadata.get("variant_sample_size_constant") is True
        and global_counts_valid
    )
    if fixed_total:
        return {"status": "PASS_PROVIDER_DECLARED_FIXED_SAMPLE_SIZE_WITH_AUDITABLE_TOTAL", "pass": True}
    if "sample_size" in mapped_fields or "cohort_count" in mapped_fields:
        return {"status": "CONDITIONAL_FROZEN_REGION_SAMPLE_DESIGN_MISSING_OR_INVALID", "pass": False}
    if global_counts_valid:
        return {"status": "CONDITIONAL_GLOBAL_COUNTS_WITHOUT_PER_VARIANT_OR_FIXED_N", "pass": False}
    return {"status": "CONDITIONAL_SAMPLE_DESIGN_UNAVAILABLE", "pass": False}


def anchor_gate(
    regional_rows: dict[str, list[dict[str, str]]],
    global_lead_records: dict[str, list[dict[str, str]]],
) -> dict[str, object]:
    details: dict[str, dict[str, object]] = {}
    for region_name, expected in REGION_ANCHORS.items():
        rows = regional_rows[region_name]
        same_id = [row for row in rows if str(row.get("variant_id", "")).strip() == expected["rsid"]]
        coordinate_matches = []
        exact = []
        for row in same_id:
            valid, position = numeric_value(row.get("position", ""))
            coordinate_match = (
                valid
                and position is not None
                and position.is_integer()
                and str(row.get("chromosome", "")).lower().removeprefix("chr") == expected["chromosome"]
                and int(position) == expected["position"]
            )
            if coordinate_match:
                coordinate_matches.append(row)
            if not missing(row.get("other_allele", "")):
                observed_alleles = {
                    str(row.get("effect_allele", "")).upper(),
                    str(row.get("other_allele", "")).upper(),
                }
            elif not missing(row.get("reference_allele", "")) and not missing(row.get("alternate_allele", "")):
                observed_alleles = {
                    str(row.get("reference_allele", "")).upper(),
                    str(row.get("alternate_allele", "")).upper(),
                }
            else:
                observed_alleles = set()
            if coordinate_match and observed_alleles == expected["alleles"]:
                exact.append(row)
        details[expected["rsid"]] = {
            "region": region_name,
            "expected_chromosome": expected["chromosome"],
            "expected_position": expected["position"],
            "expected_alleles": sorted(expected["alleles"]),
            "same_rsid_records_in_region": len(same_id),
            "same_rsid_records_in_whole_file": len(global_lead_records.get(expected["rsid"], [])),
            "exact_coordinate_records": len(coordinate_matches),
            "exact_coordinate_and_allele_records": len(exact),
            "conflicting_same_rsid_records": max(
                0, len(global_lead_records.get(expected["rsid"], [])) - len(exact)
            ),
            "pass": len(exact) == 1 and len(global_lead_records.get(expected["rsid"], [])) == 1,
        }
    return {
        "status": "PASS_EXACT_ANCHORS" if all(item["pass"] for item in details.values()) else "CONDITIONAL_EXACT_ANCHOR_MISSING_OR_AMBIGUOUS",
        "pass": all(item["pass"] for item in details.values()),
        "details": details,
    }


def real_text(value: object) -> bool:
    if value is None or not str(value).strip():
        return False
    if core.is_missing(str(value)):
        return False
    lowered = str(value).strip().lower()
    return not any(token in lowered for token in PLACEHOLDER_TOKENS)


def valid_locator(value: object, special_prefixes: tuple[str, ...] = ()) -> bool:
    if not real_text(value):
        return False
    raw = str(value).strip()
    lowered = raw.lower()
    for prefix in special_prefixes:
        if lowered.startswith(prefix):
            suffix = raw[len(prefix):].strip()
            return real_text(suffix)
    parsed = urlparse(raw)
    if parsed.scheme.lower() in {"http", "https", "ftp"}:
        return bool(parsed.netloc)
    if parsed.scheme.lower() == "s3":
        return bool(parsed.netloc and parsed.path.strip("/"))
    return False


def provenance_gate(metadata: dict) -> dict[str, object]:
    source = str(metadata.get("source_url", "")).strip()
    source_valid = valid_locator(source, ("author-supplied:",))
    identifier = metadata.get("accession") if real_text(metadata.get("accession")) else metadata.get("provider")
    identifier_valid = real_text(identifier)
    checksum_source = str(metadata.get("expected_checksum_source", "")).strip()
    checksum_source_valid = valid_locator(
        checksum_source,
        ("provider-manifest:", "repository-manifest:", "author-manifest:"),
    )
    transfer_type = norm(metadata.get("transfer_type", ""))
    if transfer_type == "public_catalog":
        source_host = (urlparse(source).hostname or "").lower()
        checksum_host = (urlparse(checksum_source).hostname or "").lower()
        host_valid = (
            (source_host == "ebi.ac.uk" or source_host.endswith(".ebi.ac.uk"))
            and (checksum_host == "ebi.ac.uk" or checksum_host.endswith(".ebi.ac.uk"))
        )
        accession_valid = bool(re.fullmatch(r"GCST\d+", str(metadata.get("accession", "")).strip(), re.I))
    elif transfer_type == "author_transfer":
        host_valid = True
        accession_valid = identifier_valid
    else:
        host_valid = False
        accession_valid = False
    passed = source_valid and identifier_valid and checksum_source_valid and host_valid and accession_valid
    return {
        "status": "PASS" if passed else "HOLD_PLACEHOLDER_OR_MISSING_PROVENANCE",
        "pass": passed,
        "source_valid": source_valid,
        "identifier_valid": identifier_valid,
        "expected_checksum_source_valid": checksum_source_valid,
        "expected_checksum_source": checksum_source or None,
        "source_and_checksum_host_valid": host_valid,
        "accession_or_author_identifier_valid": accession_valid,
    }


def checksum_evidence_gate(
    metadata: dict,
    metadata_path: pathlib.Path,
    input_path: pathlib.Path,
    checksum_gate_result: dict[str, object],
) -> dict[str, object]:
    raw_path = metadata.get("expected_checksum_evidence_file")
    raw_evidence_hash = str(metadata.get("expected_checksum_evidence_sha256", "")).strip().lower()
    evidence_type = norm(metadata.get("expected_checksum_evidence_type", ""))
    transfer_type = norm(metadata.get("transfer_type", ""))
    type_valid = evidence_type in CHECKSUM_EVIDENCE_TYPES and (
        (transfer_type == "author_transfer" and evidence_type == "author_manifest")
        or (transfer_type == "public_catalog" and evidence_type in {"provider_manifest", "repository_manifest"})
    )
    if raw_path is None or core.is_missing(str(raw_path)):
        return {
            "status": "HOLD_CHECKSUM_EVIDENCE_FILE_MISSING",
            "pass": False,
            "evidence_type_valid": type_valid,
        }
    evidence_path = pathlib.Path(str(raw_path)).expanduser()
    if not evidence_path.is_absolute():
        evidence_path = metadata_path.parent / evidence_path
    evidence_path = evidence_path.resolve()
    protected = {input_path.resolve(), metadata_path.resolve()}
    if evidence_path in protected or not evidence_path.is_file():
        return {
            "status": "HOLD_CHECKSUM_EVIDENCE_FILE_INVALID",
            "pass": False,
            "path": str(evidence_path),
            "evidence_type_valid": type_valid,
        }
    evidence_size = evidence_path.stat().st_size
    if not 0 < evidence_size <= 10 * 1024 * 1024:
        return {
            "status": "HOLD_CHECKSUM_EVIDENCE_FILE_SIZE_INVALID",
            "pass": False,
            "path": str(evidence_path),
            "bytes": evidence_size,
            "evidence_type_valid": type_valid,
        }
    raw = evidence_path.read_bytes()
    evidence_sha256 = hashlib.sha256(raw).hexdigest()
    evidence_hash_valid = bool(
        re.fullmatch(r"[0-9a-f]{64}", raw_evidence_hash)
        and evidence_sha256 == raw_evidence_hash
    )
    expected_values = [
        str(metadata[key]).strip().lower()
        for key in ("expected_sha256", "expected_md5")
        if real_text(metadata.get(key))
    ]
    evidence_text = raw.decode("utf-8", errors="replace").lower()
    digest_present = bool(expected_values) and all(value in evidence_text for value in expected_values)
    size_valid = 0 < len(raw) <= 10 * 1024 * 1024
    checksum_matched = str(checksum_gate_result.get("status", "")).startswith("PASS")
    passed = type_valid and evidence_hash_valid and digest_present and size_valid and checksum_matched
    return {
        "status": "PASS" if passed else "HOLD_CHECKSUM_EVIDENCE_NOT_VERIFIED",
        "pass": passed,
        "path": str(evidence_path),
        "bytes": len(raw),
        "sha256": evidence_sha256,
        "expected_evidence_sha256_matches": evidence_hash_valid,
        "expected_input_digest_present": digest_present,
        "evidence_type": evidence_type or None,
        "evidence_type_valid": type_valid,
        "checksum_matched": checksum_matched,
        "boundary": (
            "This verifies a frozen evidence artifact and its contents. Human review must still establish "
            "that the artifact came from the declared provider or author channel."
        ),
    }


def target_identity_gate(metadata: dict, label: str) -> dict[str, object]:
    phenotype = norm(metadata.get("phenotype", ""))
    stratum = norm(metadata.get("stratum", ""))
    ancestry_valid = norm(metadata.get("ancestry", "")) in TARGET_ANCESTRY_TOKENS
    phenotype_valid = phenotype in TARGET_PHENOTYPE_TOKENS
    stratum_valid = stratum in TARGET_STRATA and stratum == norm(label)
    pmid = str(metadata.get("target_pmid", "")).strip()
    doi = str(metadata.get("target_doi", "")).strip().lower().removeprefix("https://doi.org/")
    study_valid = pmid == TARGET_PMID or doi == TARGET_DOI
    analysis_type = norm(metadata.get("analysis_type", ""))
    analysis_valid = analysis_type in TARGET_ANALYSIS_TYPES
    transfer_type = norm(metadata.get("transfer_type", ""))
    transfer_valid = transfer_type in TRANSFER_TYPES
    passed = (
        phenotype_valid and stratum_valid and ancestry_valid
        and study_valid and analysis_valid and transfer_valid
    )
    return {
        "status": "PASS" if passed else "HOLD_TARGET_IDENTITY_MISMATCH_OR_MISSING",
        "pass": passed,
        "phenotype_valid": phenotype_valid,
        "stratum_valid": stratum_valid,
        "ancestry_valid": ancestry_valid,
        "study_identifier_valid": study_valid,
        "analysis_type_valid": analysis_valid,
        "transfer_type_valid": transfer_valid,
        "label": label,
        "metadata_phenotype": metadata.get("phenotype"),
        "metadata_stratum": metadata.get("stratum"),
        "metadata_ancestry": metadata.get("ancestry"),
        "metadata_target_pmid": metadata.get("target_pmid"),
        "metadata_target_doi": metadata.get("target_doi"),
        "metadata_analysis_type": metadata.get("analysis_type"),
        "metadata_transfer_type": metadata.get("transfer_type"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-rows", type=int, default=0)
    args = parser.parse_args()

    normalized_label = str(args.label).strip().lower()
    if normalized_label not in TARGET_STRATA or not re.fullmatch(r"[A-Za-z]+", str(args.label).strip()):
        parser.error("--label must be exactly female or male")
    args.label = normalized_label

    input_path = pathlib.Path(args.input).resolve()
    metadata_path = pathlib.Path(args.metadata).resolve()
    output_dir = pathlib.Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    wrapper_outputs = {
        output_dir / f"{args.label}_intake_v2_1.json",
        output_dir / f"{args.label}_intake_v2_1.md",
    }
    if input_path in {path.resolve() for path in wrapper_outputs} or metadata_path in {
        path.resolve() for path in wrapper_outputs
    }:
        raise ValueError("An H6 v2.1 output path collides with the input or metadata file")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    evidence_file = metadata.get("expected_checksum_evidence_file")
    if evidence_file is not None and not core.is_missing(str(evidence_file)):
        evidence_path = pathlib.Path(str(evidence_file)).expanduser()
        if not evidence_path.is_absolute():
            evidence_path = metadata_path.parent / evidence_path
        evidence_path = evidence_path.resolve()
        all_outputs = wrapper_outputs | {
            *(output_dir / f"{args.label}_{name}.tsv" for name in core.DEFAULT_REGIONS),
        }
        if evidence_path in {path.resolve() for path in all_outputs}:
            raise ValueError("An H6 v2.1 output path collides with the checksum evidence file")
    header = read_header(input_path)
    bare_n = configure_bare_n(header, metadata)

    base_args = SimpleNamespace(
        input=str(input_path), metadata=str(metadata_path), label=args.label,
        output_dir=str(output_dir), skip_hash=False, max_rows=args.max_rows,
    )
    base_result = core.audit(base_args)
    mapped_fields = set(base_result["format"]["canonical_mapping"])
    effect_column = base_result["effect_scale_gate"].get("effect_column") or "beta"
    if "other_allele" in mapped_fields:
        allele_mode = "other"
    elif {"reference_allele", "alternate_allele"}.issubset(mapped_fields):
        allele_mode = "refalt"
    else:
        allele_mode = "none"

    regional_rows: dict[str, list[dict[str, str]]] = {}
    regions: dict[str, dict[str, object]] = {}
    for region_name in core.DEFAULT_REGIONS:
        path = output_dir / f"{args.label}_{region_name}.tsv"
        rows = load_region(path) if path.is_file() else []
        regional_rows[region_name] = rows
        regions[region_name] = audit_region(rows, effect_column, allele_mode, mapped_fields)

    sample_design = sample_design_gate(
        regions, mapped_fields, metadata, bare_n, base_result["format"]["canonical_mapping"]
    )
    anchors = anchor_gate(regional_rows, base_result["lead_variant_records"])
    density = regional_density_gate(regions)
    provenance = provenance_gate(metadata)
    checksum_evidence = checksum_evidence_gate(
        metadata, metadata_path, input_path, base_result["checksum_gate"]
    )
    target_identity = target_identity_gate(metadata, args.label)
    se_scale = norm(metadata.get("standard_error_scale", ""))
    if norm(metadata.get("effect_scale", "")) == "odds_ratio":
        se_semantics_pass = se_scale in {"log_odds", "beta"}
        se_semantics_status = "PASS" if se_semantics_pass else "CONDITIONAL_OR_SE_SCALE_UNDECLARED"
    else:
        se_semantics_pass = True
        se_semantics_status = "NOT_APPLICABLE"

    rows_info = base_result["rows"]
    global_missing = rows_info["missing_by_field"]
    global_invalid = rows_info["invalid_by_field"]
    structural_missing = {
        field: int(global_missing.get(field, 0)) for field in ("chromosome", "position")
    }
    structural_invalid = {
        field: int(global_invalid.get(field, 0)) for field in STRUCTURAL_GLOBAL_FIELDS
    }
    global_integrity_pass = (
        int(rows_info["scanned"]) > 0
        and int(rows_info["malformed"]) == 0
        and not any(structural_missing.values())
        and not any(structural_invalid.values())
        and not base_result["format"].get("header_decode_replacement", False)
        and not base_result["format"].get("header_control_character", False)
    )
    schema_pass = (
        base_result["core_columns_pass"]
        and base_result["effect_scale_gate"]["status"] == "PASS"
        and allele_mode in {"other", "refalt"}
    )
    assembly_pass = base_result["assembly_gate"]["status"] == "PASS"
    checksum_pass = str(base_result["checksum_gate"]["status"]).startswith("PASS")
    regions_present_unique = (
        base_result["regional_presence_pass"] and base_result["regional_duplicate_keys_pass"]
    )
    region_core_pass = all(
        int(region["rows"]) > 0 and int(region["core_missing"]) == 0 and int(region["core_invalid"]) == 0
        for region in regions.values()
    )
    region_support_pass = all(
        not any(region["support_missing"].values()) and not any(region["support_invalid"].values())
        for region in regions.values()
    )

    diagnostic = bool(args.max_rows)
    if diagnostic:
        status = "DIAGNOSTIC_ONLY_MAX_ROWS_NO_INTAKE_DECISION"
    elif not schema_pass:
        status = "HOLD_CORE_SCHEMA_OR_EFFECT_SCALE"
    elif not assembly_pass:
        status = "HOLD_ASSEMBLY_MISMATCH"
    elif (
        not checksum_pass
        or not provenance["pass"]
        or not checksum_evidence["pass"]
        or not target_identity["pass"]
    ):
        status = "HOLD_PROVENANCE_CHECKSUM_OR_TARGET_IDENTITY"
    elif not global_integrity_pass:
        status = "HOLD_WHOLE_FILE_STRUCTURAL_INTEGRITY"
    elif not regions_present_unique:
        status = "HOLD_FROZEN_REGION_EMPTY_OR_DUPLICATE_KEYS"
    elif not region_core_pass:
        status = "HOLD_FROZEN_REGION_CORE_INVALID_OR_MISSING"
    elif (
        not region_support_pass
        or not sample_design["pass"]
        or not anchors["pass"]
        or not density["pass"]
        or not se_semantics_pass
    ):
        status = "CONDITIONAL_FROZEN_REGION_SUPPORT_DESIGN_OR_ANCHOR"
    else:
        status = "PASS_FROZEN_REGIONS_INTAKE_READY_FOR_HARMONIZATION"

    gates = {
        "schema": schema_pass,
        "assembly": assembly_pass,
        "checksum": checksum_pass,
        "provenance": bool(provenance["pass"]),
        "checksum_evidence": bool(checksum_evidence["pass"]),
        "target_identity": bool(target_identity["pass"]),
        "whole_file_structural_integrity": global_integrity_pass,
        "frozen_regions_present_unique": regions_present_unique,
        "frozen_region_core": region_core_pass,
        "frozen_region_support": region_support_pass,
        "sample_design": bool(sample_design["pass"]),
        "exact_anchors": bool(anchors["pass"]),
        "regional_density_sanity": bool(density["pass"]),
        "or_se_semantics": se_semantics_pass,
    }
    result = {
        "audit": "R4A11_H6_V2_1_HARDENED_TWO_LEVEL_INTAKE",
        "status": status,
        "base_status": base_result["status"],
        "input": base_result["input"],
        "metadata": metadata,
        "format": base_result["format"],
        "bare_n_semantics_gate": bare_n,
        "provenance_gate": provenance,
        "checksum_evidence_gate": checksum_evidence,
        "target_identity_gate": target_identity,
        "checksum_gate": base_result["checksum_gate"],
        "assembly_gate": base_result["assembly_gate"],
        "effect_scale_gate": base_result["effect_scale_gate"],
        "whole_file": {
            "rows_scanned": rows_info["scanned"],
            "malformed_rows": rows_info["malformed"],
            "structural_missing": structural_missing,
            "structural_invalid": structural_invalid,
            "all_missing": global_missing,
            "all_invalid": global_invalid,
        },
        "frozen_regions": regions,
        "sample_design_gate": sample_design,
        "anchor_gate": anchors,
        "regional_density_gate": density,
        "odds_ratio_se_semantics": {"status": se_semantics_status, "pass": se_semantics_pass},
        "gates": gates,
        "next_gate": "FASTA normalization, allele harmonization, common-variant coverage, ancestry-matched LD, and RSS diagnostics",
        "boundary": (
            "PASS authorizes harmonization and coverage review only. It does not establish adequate QTL overlap, "
            "fine-mapping validity, colocalization, or C1. Missing or invalid nonstructural values outside the "
            "two frozen regions are reported but do not decide this prespecified regional intake."
        ),
    }
    json_path = output_dir / f"{args.label}_intake_v2_1.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"# {args.label} H6 v2.1 intake",
        "",
        f"> **Status: `{status}`**",
        "",
        f"- Input rows scanned: {rows_info['scanned']}",
        f"- SHA-256: `{base_result['input']['sha256']}`",
        f"- Bare N: `{bare_n['status']}`",
        f"- Sample design: `{sample_design['status']}`",
        f"- Exact anchors: `{anchors['status']}`",
        f"- Regional density: `{density['status']}`",
        f"- Whole-file structural integrity: `{'PASS' if global_integrity_pass else 'FAIL'}`",
        "",
        "## Frozen regions",
        "",
    ]
    for region_name, region in regions.items():
        lines.append(
            f"- `{region_name}`: rows={region['rows']}, core_missing={region['core_missing']}, "
            f"core_invalid={region['core_invalid']}, support_missing={region['support_missing']}, "
            f"support_invalid={region['support_invalid']}"
        )
    lines += [
        "",
        "## Boundary",
        "",
        result["boundary"],
        "",
    ]
    (output_dir / f"{args.label}_intake_v2_1.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if status.startswith("PASS"):
        return 0
    if status.startswith("CONDITIONAL"):
        return 3
    if status.startswith("DIAGNOSTIC"):
        return 4
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
