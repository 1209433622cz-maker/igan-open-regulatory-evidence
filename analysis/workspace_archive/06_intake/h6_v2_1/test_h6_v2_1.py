#!/usr/bin/env python3
"""Regression and hostile tests for the R4A11 H6 v2.1 intake gate."""

from __future__ import annotations

import hashlib
import gzip
import json
import math
import pathlib
import subprocess
import sys
import tempfile


HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "inspect_sex_specific_sumstats_v2_1.py"
HEADER = [
    "chromosome", "base_pair_location", "variant_id", "effect_allele",
    "other_allele", "beta", "standard_error", "p_value",
    "effect_allele_frequency", "info", "sample_size",
]
ANCHOR_ROWS = [
    ["6", "396321", "rs12203592", "T", "C", "-0.248", "0.044", "2.36e-8", "0.42", "0.99", "20150"],
    ["22", "39328807", "rs66578187", "AT", "A", "0.174", "0.031", "3.18e-8", "0.45", "0.98", "20150"],
]
ROWS = ANCHOR_ROWS + [
    ["6", str(10_000 + index * 13_000), f"rsIRF4Proxy{index:03d}", "A", "G", "0.01", "0.05", "0.84148058", "0.40", "0.95", "20150"]
    for index in range(100)
] + [
    ["22", str(38_340_000 + index * 19_000), f"rsChr22Proxy{index:03d}", "C", "T", "-0.01", "0.05", "0.84148058", "0.40", "0.95", "20150"]
    for index in range(100)
]
PASS = "PASS_FROZEN_REGIONS_INTAKE_READY_FOR_HARMONIZATION"
CONDITIONAL = "CONDITIONAL_FROZEN_REGION_SUPPORT_DESIGN_OR_ANCHOR"
HOLD_CORE = "HOLD_FROZEN_REGION_CORE_INVALID_OR_MISSING"
HOLD_PROVENANCE = "HOLD_PROVENANCE_CHECKSUM_OR_TARGET_IDENTITY"
HOLD_GLOBAL = "HOLD_WHOLE_FILE_STRUCTURAL_INTEGRITY"


def write_table(path: pathlib.Path, header: list[str], rows: list[list[str]]) -> None:
    path.write_text(
        "\t".join(header) + "\n" + "\n".join("\t".join(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def metadata() -> dict[str, object]:
    return {
        "phenotype": "systemic sclerosis",
        "target_pmid": "41999721",
        "target_doi": "10.1016/S2665-9913(25)00376-5",
        "analysis_type": "sex_stratified_case_control_gwas",
        "transfer_type": "public_catalog",
        "stratum": "female",
        "assembly": "GRCh38",
        "ancestry": "European",
        "cases": 9097,
        "controls": 11053,
        "total_sample_size": 20150,
        "total_cohort_count": 15,
        "variant_sample_size_constant": False,
        "effect_scale": "log_odds",
        "source_url": "https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST99999999/female.tsv.gz",
        "accession": "GCST99999999",
        "provider": "synthetic regression fixture",
        "expected_checksum_source": "https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST99999999/checksums.sha256",
        "expected_checksum_evidence_type": "repository_manifest",
    }


def run_case(
    root: pathlib.Path,
    name: str,
    *,
    header: list[str] | None = None,
    rows: list[list[str]] | None = None,
    metadata_update: dict[str, object] | None = None,
    checksum: str = "sha256",
    extra: list[str] | None = None,
    malformed_line: str | None = None,
    format_kind: str = "tsv",
) -> tuple[int, dict]:
    case_header = list(HEADER if header is None else header)
    case_rows = [list(row) for row in (ROWS if rows is None else rows)]
    suffix = {"tsv": ".tsv", "comma": ".csv", "whitespace": ".txt", "gzip": ".tsv.gz"}[format_kind]
    source = root / f"{name}{suffix}"
    delimiter = {"tsv": "\t", "comma": ",", "whitespace": " ", "gzip": "\t"}[format_kind]
    table_text = delimiter.join(case_header) + "\n" + "\n".join(delimiter.join(row) for row in case_rows) + "\n"
    if format_kind == "gzip":
        with gzip.open(source, "wt", encoding="utf-8", newline="") as handle:
            handle.write(table_text)
    else:
        source.write_text(table_text, encoding="utf-8")
    if malformed_line is not None:
        with source.open("a", encoding="utf-8") as handle:
            handle.write(malformed_line + "\n")
    meta = metadata()
    if metadata_update:
        meta.update(metadata_update)
    if checksum == "sha256":
        meta["expected_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        digest_line = f"{meta['expected_sha256']}  {source.name}\n"
    elif checksum == "md5":
        meta["expected_md5"] = hashlib.md5(source.read_bytes()).hexdigest()
        digest_line = f"{meta['expected_md5']}  {source.name}\n"
    elif checksum != "none":
        raise ValueError(checksum)
    else:
        digest_line = ""
    if checksum != "none" and "expected_checksum_evidence_file" not in (metadata_update or {}):
        evidence_path = root / f"{name}.provider_checksums.txt"
        evidence_path.write_text(digest_line, encoding="utf-8")
        meta["expected_checksum_evidence_file"] = str(evidence_path)
        meta["expected_checksum_evidence_sha256"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    metadata_path = root / f"{name}.json"
    metadata_path.write_text(json.dumps(meta), encoding="utf-8")
    output_dir = root / f"out_{name}"
    command = [
        sys.executable, str(SCRIPT), "--input", str(source), "--metadata", str(metadata_path),
        "--label", "female", "--output-dir", str(output_dir),
    ] + (extra or [])
    completed = subprocess.run(command, capture_output=True, text=True)
    result_path = output_dir / "female_intake_v2_1.json"
    if not result_path.is_file():
        raise AssertionError(
            f"{name}: no result JSON; rc={completed.returncode}; stdout={completed.stdout}; stderr={completed.stderr}"
        )
    return completed.returncode, json.loads(result_path.read_text(encoding="utf-8"))


def replace(rows: list[list[str]], header: list[str], row_index: int, field: str, value: str) -> list[list[str]]:
    changed = [list(row) for row in rows]
    changed[row_index][header.index(field)] = value
    return changed


def drop(header: list[str], rows: list[list[str]], field: str) -> tuple[list[str], list[list[str]]]:
    index = header.index(field)
    return header[:index] + header[index + 1 :], [row[:index] + row[index + 1 :] for row in rows]


def expect(
    results: list[dict[str, object]],
    root: pathlib.Path,
    name: str,
    expected_status: str,
    expected_rc: int,
    **kwargs,
) -> dict:
    rc, result = run_case(root, name, **kwargs)
    assert rc == expected_rc, (name, rc, result.get("status"))
    assert result["status"] == expected_status, (name, result["status"], expected_status)
    results.append({"name": name, "status": result["status"], "returncode": rc, "pass": True})
    return result


def main() -> int:
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="r4a11_h6_v2_1_") as temp:
        root = pathlib.Path(temp)
        expect(results, root, "complete", PASS, 0)
        expect(results, root, "complete_gzip", PASS, 0, format_kind="gzip")
        expect(results, root, "complete_comma", PASS, 0, format_kind="comma")
        expect(results, root, "complete_whitespace", PASS, 0, format_kind="whitespace")

        outside = ROWS + [["1", "100000", "rsOutside", "A", "G", "0.01", "0.02", "0.5", "NA", "NA", "20150"]]
        expect(results, root, "outside_support_missing", PASS, 0, rows=outside)
        outside_se = replace(outside, HEADER, len(ROWS), "standard_error", "NA")
        expect(results, root, "outside_se_missing", PASS, 0, rows=outside_se)
        outside_bad_beta = replace(outside, HEADER, len(ROWS), "beta", "not_numeric")
        expect(results, root, "outside_beta_invalid", PASS, 0, rows=outside_bad_beta)

        for field in ("standard_error", "p_value", "beta"):
            bad = replace(ROWS, HEADER, 1, field, "not_numeric")
            expect(results, root, f"inside_{field}_nonnumeric", HOLD_CORE, 2, rows=bad)
        missing_se = replace(ROWS, HEADER, 1, "standard_error", "NA")
        expect(results, root, "inside_se_missing", HOLD_CORE, 2, rows=missing_se)
        infinite_se = replace(ROWS, HEADER, 1, "standard_error", "inf")
        expect(results, root, "inside_se_infinite", HOLD_CORE, 2, rows=infinite_se)
        bad_p = replace(ROWS, HEADER, 1, "p_value", "1.1")
        expect(results, root, "inside_p_out_of_range", HOLD_CORE, 2, rows=bad_p)

        bad_eaf = replace(ROWS, HEADER, 1, "effect_allele_frequency", "not_numeric")
        expect(results, root, "inside_eaf_nonnumeric", CONDITIONAL, 3, rows=bad_eaf)
        bad_info = replace(ROWS, HEADER, 1, "info", "1.1")
        expect(results, root, "inside_info_out_of_range", CONDITIONAL, 3, rows=bad_info)

        incoherent = replace(ROWS, HEADER, 1, "beta", "0.001")
        expect(results, root, "effect_se_p_gross_inconsistency", HOLD_CORE, 2, rows=incoherent)
        impossible_zero_p = replace(ROWS, HEADER, 1, "p_value", "0")
        expect(results, root, "impossible_zero_p_for_moderate_z", HOLD_CORE, 2, rows=impossible_zero_p)
        moderate_incoherence = replace(ROWS, HEADER, 1, "beta", "0.062")
        moderate_incoherence = replace(moderate_incoherence, HEADER, 1, "p_value", "5e-5")
        expect(results, root, "moderate_effect_se_p_incoherence", HOLD_CORE, 2, rows=moderate_incoherence)

        bare_header = list(HEADER)
        bare_header[bare_header.index("sample_size")] = "N"
        expect(results, root, "bare_n_undeclared", CONDITIONAL, 3, header=bare_header)
        bare_sample = expect(
            results, root, "bare_n_sample", PASS, 0, header=bare_header,
            metadata_update={"bare_n_semantics": "sample_size"},
        )
        assert bare_sample["format"]["canonical_mapping"]["sample_size"] == "N"
        cohort_rows = [
            replace([row], HEADER, 0, "sample_size", str(14 + (i % 2)))[0]
            for i, row in enumerate(ROWS)
        ]
        bare_cohort = expect(
            results, root, "bare_n_cohort", PASS, 0, header=bare_header, rows=cohort_rows,
            metadata_update={"bare_n_semantics": "cohort_count"},
        )
        assert bare_cohort["format"]["canonical_mapping"]["cohort_count"] == "N"
        assert "sample_size" not in bare_cohort["format"]["canonical_mapping"]
        fractional = replace(cohort_rows, bare_header, 1, "N", "14.5")
        expect(
            results, root, "bare_n_fractional_cohort", CONDITIONAL, 3,
            header=bare_header, rows=fractional, metadata_update={"bare_n_semantics": "cohort_count"},
        )
        expect(
            results, root, "bare_n_cohort_negative_cases", CONDITIONAL, 3,
            header=bare_header, rows=cohort_rows,
            metadata_update={"bare_n_semantics": "cohort_count", "cases": -1},
        )
        expect(
            results, root, "bare_n_ignored", CONDITIONAL, 3, header=bare_header,
            metadata_update={"bare_n_semantics": "ignore"},
        )

        or_header = [
            "chromosome", "base_pair_location", "variant_id", "effect_allele", "reference_allele",
            "alternate_allele", "odds_ratio", "standard_error", "p_value",
            "effect_allele_frequency", "info", "sample_size",
        ]
        or_rows = [
            [
                row[0], row[1], row[2], row[3], row[4], row[3],
                f"{math.exp(float(row[5])):.12g}", row[6], row[7], row[8], row[9], row[10],
            ]
            for row in ROWS
        ]
        expect(
            results, root, "or_without_se_scale", CONDITIONAL, 3, header=or_header, rows=or_rows,
            metadata_update={"effect_scale": "odds_ratio"},
        )
        expect(
            results, root, "or_log_odds_se", PASS, 0, header=or_header, rows=or_rows,
            metadata_update={"effect_scale": "odds_ratio", "standard_error_scale": "log_odds"},
        )

        missing_lead = [row for row in ROWS if row[HEADER.index("variant_id")] != "rs66578187"]
        expect(results, root, "missing_chr22_lead", CONDITIONAL, 3, rows=missing_lead)
        wrong_coordinate = replace(ROWS, HEADER, 0, "base_pair_location", "397000")
        expect(results, root, "same_rsid_wrong_coordinate", CONDITIONAL, 3, rows=wrong_coordinate)
        wrong_chromosome = replace(ROWS, HEADER, 0, "chromosome", "1")
        expect(results, root, "same_rsid_wrong_chromosome", CONDITIONAL, 3, rows=wrong_chromosome)
        wrong_anchor_alleles = replace(ROWS, HEADER, 0, "other_allele", "A")
        expect(results, root, "same_rsid_coordinate_wrong_alleles", CONDITIONAL, 3, rows=wrong_anchor_alleles)
        conflicting_rsid = ROWS + [["6", "500000", "rs12203592", "A", "G", "0.01", "0.05", "0.84148058", "0.4", "0.95", "20150"]]
        expect(results, root, "exact_anchor_plus_conflicting_rsid", CONDITIONAL, 3, rows=conflicting_rsid)
        expect(results, root, "one_variant_per_region", CONDITIONAL, 3, rows=ANCHOR_ROWS)

        expect(results, root, "wrong_build", "HOLD_ASSEMBLY_MISMATCH", 2, metadata_update={"assembly": "GRCh37"})
        expect(results, root, "no_checksum", HOLD_PROVENANCE, 2, checksum="none")
        expect(
            results, root, "no_trusted_checksum_source", HOLD_PROVENANCE, 2,
            metadata_update={"expected_checksum_source": ""},
        )
        expect(
            results, root, "no_checksum_evidence_artifact", HOLD_PROVENANCE, 2,
            metadata_update={"expected_checksum_evidence_file": None, "expected_checksum_evidence_sha256": None},
        )
        expect(
            results, root, "checksum_evidence_type_invalid", HOLD_PROVENANCE, 2,
            metadata_update={"expected_checksum_evidence_type": "local_self_hash"},
        )
        expect(
            results, root, "author_transfer_with_manifest", PASS, 0,
            metadata_update={
                "transfer_type": "author_transfer",
                "source_url": "author-supplied:secure-transfer-2026-09-12",
                "expected_checksum_source": "author-manifest:signed-message-2026-09-12",
                "expected_checksum_evidence_type": "author_manifest",
            },
        )
        expect(
            results, root, "placeholder_provenance", HOLD_PROVENANCE, 2,
            metadata_update={"source_url": "REPLACE", "accession": "REPLACE", "provider": "REPLACE"},
        )
        expect(
            results, root, "empty_url_shells", HOLD_PROVENANCE, 2,
            metadata_update={"source_url": "https:", "accession": "NA", "provider": "NA", "expected_checksum_source": "https:"},
        )
        expect(
            results, root, "empty_author_locator", HOLD_PROVENANCE, 2,
            metadata_update={"source_url": "author-supplied:", "expected_checksum_source": "author-manifest:"},
        )
        expect(
            results, root, "public_catalog_wrong_host", HOLD_PROVENANCE, 2,
            metadata_update={
                "source_url": "https://unrelated.test/female.tsv.gz",
                "expected_checksum_source": "https://unrelated.test/checksums.sha256",
            },
        )
        expect(
            results, root, "public_catalog_bad_accession", HOLD_PROVENANCE, 2,
            metadata_update={"accession": "UNVERIFIED"},
        )
        expect(
            results, root, "stratum_mismatch", HOLD_PROVENANCE, 2,
            metadata_update={"stratum": "male"},
        )
        expect(
            results, root, "phenotype_mismatch", HOLD_PROVENANCE, 2,
            metadata_update={"phenotype": "rheumatoid arthritis"},
        )
        expect(
            results, root, "wrong_target_study", HOLD_PROVENANCE, 2,
            metadata_update={"target_pmid": "99999999", "target_doi": "10.0000/wrong"},
        )
        expect(
            results, root, "overall_analysis_type", HOLD_PROVENANCE, 2,
            metadata_update={"analysis_type": "overall_gwas"},
        )
        expect(
            results, root, "transfer_type_missing", HOLD_PROVENANCE, 2,
            metadata_update={"transfer_type": ""},
        )
        expect(
            results, root, "ancestry_missing", HOLD_PROVENANCE, 2,
            metadata_update={"ancestry": ""},
        )
        expect(
            results, root, "ancestry_placeholder", HOLD_PROVENANCE, 2,
            metadata_update={"ancestry": "Martian"},
        )
        expect(results, root, "md5_only", PASS, 0, checksum="md5")

        expect(
            results, root, "duplicate_regional_key", "HOLD_FROZEN_REGION_EMPTY_OR_DUPLICATE_KEYS", 2,
            rows=ROWS + [ROWS[1]],
        )
        expect(
            results, root, "max_rows_diagnostic", "DIAGNOSTIC_ONLY_MAX_ROWS_NO_INTAKE_DECISION", 4,
            extra=["--max-rows", "1"],
        )
        bad_refalt = replace(or_rows, or_header, 1, "effect_allele", "C")
        expect(
            results, root, "effect_not_refalt", HOLD_CORE, 2, header=or_header, rows=bad_refalt,
            metadata_update={"effect_scale": "odds_ratio", "standard_error_scale": "log_odds"},
        )
        same_alleles = replace(ROWS, HEADER, 1, "other_allele", "AT")
        expect(results, root, "identical_effect_other_allele", HOLD_CORE, 2, rows=same_alleles)

        missing_position = ROWS + [["1", "NA", "rsNoPos", "A", "G", "0.1", "0.1", "0.5", "0.4", "0.9", "20150"]]
        expect(results, root, "global_position_missing", HOLD_GLOBAL, 2, rows=missing_position)
        invalid_position = ROWS + [["1", "bad", "rsBadPos", "A", "G", "0.1", "0.1", "0.5", "0.4", "0.9", "20150"]]
        expect(results, root, "global_position_invalid", HOLD_GLOBAL, 2, rows=invalid_position)
        invalid_chrom = ROWS + [["chrUn", "100000", "rsBadChr", "A", "G", "0.1", "0.1", "0.5", "0.4", "0.9", "20150"]]
        expect(results, root, "global_chromosome_invalid", HOLD_GLOBAL, 2, rows=invalid_chrom)
        out_of_chromosome = ROWS + [["1", "999999999", "rsBeyondChr1", "A", "G", "0.1", "0.1", "0.31731051", "0.4", "0.9", "20150"]]
        expect(results, root, "global_position_beyond_chromosome", HOLD_GLOBAL, 2, rows=out_of_chromosome)
        replacement_char = ROWS + [["1", "100000", "bad\ufffdid", "A", "G", "0.1", "0.1", "0.5", "0.4", "0.9", "20150"]]
        expect(results, root, "utf8_replacement_character", HOLD_GLOBAL, 2, rows=replacement_char)
        nul_character = ROWS + [["1", "100000", "bad\x00id", "A", "G", "0.1", "0.1", "0.31731051", "0.4", "0.9", "20150"]]
        expect(results, root, "nul_control_character", HOLD_GLOBAL, 2, rows=nul_character)
        nul_header = list(HEADER)
        nul_header[nul_header.index("variant_id")] = "variant_id\x00"
        expect(results, root, "nul_control_character_in_header", HOLD_GLOBAL, 2, header=nul_header)
        expect(
            results, root, "malformed_row", HOLD_GLOBAL, 2,
            malformed_line="1\t100000\trsMalformed\tA",
        )

        no_n_header, no_n_rows = drop(HEADER, ROWS, "sample_size")
        expect(
            results, root, "global_counts_only", CONDITIONAL, 3,
            header=no_n_header, rows=no_n_rows,
        )
        expect(
            results, root, "provider_fixed_total", PASS, 0, header=no_n_header, rows=no_n_rows,
            metadata_update={"variant_sample_size_constant": True},
        )
        expect(
            results, root, "per_variant_n_negative_cases", CONDITIONAL, 3,
            metadata_update={"cases": -1, "controls": 20151},
        )
        expect(
            results, root, "per_variant_n_inconsistent_total", CONDITIONAL, 3,
            metadata_update={"total_sample_size": 20151},
        )
        tiny_n = replace(ROWS, HEADER, 1, "sample_size", "0.5")
        expect(results, root, "per_variant_n_below_two", CONDITIONAL, 3, rows=tiny_n)
        fractional_explicit_n = replace(ROWS, HEADER, 1, "sample_size", "14.5")
        expect(results, root, "explicit_sample_size_fractional", CONDITIONAL, 3, rows=fractional_explicit_n)
        fractional_bare_sample = replace(ROWS, HEADER, 1, "sample_size", "14.5")
        expect(
            results, root, "bare_n_fractional_sample_size", CONDITIONAL, 3,
            header=bare_header, rows=fractional_bare_sample,
            metadata_update={"bare_n_semantics": "sample_size"},
        )
        expect(
            results, root, "cohort_count_missing_total_cohorts", CONDITIONAL, 3,
            header=bare_header, rows=cohort_rows,
            metadata_update={"bare_n_semantics": "cohort_count", "total_cohort_count": None},
        )

        # Output labels cannot become paths.
        safe_source = root / "safe_input.tsv"
        write_table(safe_source, HEADER, ROWS)
        safe_meta = metadata()
        safe_meta["expected_sha256"] = hashlib.sha256(safe_source.read_bytes()).hexdigest()
        safe_meta_path = root / "safe_metadata.json"
        safe_meta_path.write_text(json.dumps(safe_meta), encoding="utf-8")
        safe_output = root / "safe_output"
        traversal = subprocess.run(
            [
                sys.executable, str(SCRIPT), "--input", str(safe_source), "--metadata", str(safe_meta_path),
                "--label", "../female", "--output-dir", str(safe_output),
            ],
            capture_output=True,
            text=True,
        )
        assert traversal.returncode != 0
        assert not (root / "female_intake_v2_1.json").exists()
        results.append({"name": "path_traversal_label_rejected", "status": "REJECTED", "returncode": traversal.returncode, "pass": True})

        # A regional output name cannot overwrite the raw input.
        collision_dir = root / "collision"
        collision_dir.mkdir()
        collision_input = collision_dir / "female_IRF4_pm1Mb_GRCh38.tsv"
        write_table(collision_input, HEADER, ROWS)
        collision_before = collision_input.read_bytes()
        collision_meta = metadata()
        collision_meta["expected_sha256"] = hashlib.sha256(collision_before).hexdigest()
        collision_meta_path = root / "collision_metadata.json"
        collision_meta_path.write_text(json.dumps(collision_meta), encoding="utf-8")
        collision = subprocess.run(
            [
                sys.executable, str(SCRIPT), "--input", str(collision_input), "--metadata", str(collision_meta_path),
                "--label", "female", "--output-dir", str(collision_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert collision.returncode != 0
        assert collision_input.read_bytes() == collision_before
        results.append({"name": "input_output_collision_rejected", "status": "REJECTED", "returncode": collision.returncode, "pass": True})

    output = {
        "suite": "R4A11_H6_V2_1_REGRESSION_AND_HOSTILE_TESTS",
        "status": "PASS",
        "tests_passed": len(results),
        "tests_total": len(results),
        "cases": results,
    }
    (HERE / "test_results_v2_1.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"R4A11_H6_V2_1_TESTS_PASS {len(results)}/{len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
