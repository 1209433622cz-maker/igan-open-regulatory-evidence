#!/usr/bin/env python3
"""Independent hostile QA for the R4A11 H6 v2.1 intake gate.

This test treats the target programs as black boxes.  It does not import or
modify them.  Synthetic files live in a temporary directory.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
from typing import Any


WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = WORKSPACE_ROOT / "2_code" / "06_intake" / "h6_v2_1" / "inspect_sex_specific_sumstats_v2_1.py"
OUTPUT = WORKSPACE_ROOT / "3_results" / "00_audit" / "R4A11" / "H6_v2_1_current_runtime_hostile_qa.json"

HEADER = [
    "chromosome",
    "base_pair_location",
    "variant_id",
    "effect_allele",
    "other_allele",
    "beta",
    "standard_error",
    "p_value",
    "effect_allele_frequency",
    "info",
    "sample_size",
]

ANCHOR_ROWS = [
    ["6", "396321", "rs12203592", "T", "C", "-0.248", "0.044", "2.36e-8", "0.42", "0.99", "20150"],
    ["22", "39328807", "rs66578187", "AT", "A", "0.174", "0.031", "3.18e-8", "0.45", "0.98", "20150"],
]

# A passing v2.1 fixture needs at least 100 rows and unique positions in each
# frozen region, spanning at least 250 kb.  Anchor rows remain indices 0 and 1.
ROWS = ANCHOR_ROWS + [
    ["6", str(100_000 + index * 4_000), f"rs6Independent{index:03d}", "A", "G", "0.1", "0.05", "0.0455003", "0.40", "0.99", "20150"]
    for index in range(99)
] + [
    ["22", str(39_000_000 + index * 4_000), f"rs22Independent{index:03d}", "C", "T", "0.1", "0.05", "0.0455003", "0.40", "0.99", "20150"]
    for index in range(99)
]

PASS = "PASS_FROZEN_REGIONS_INTAKE_READY_FOR_HARMONIZATION"


def base_metadata() -> dict[str, Any]:
    return {
        "phenotype": "systemic sclerosis",
        "stratum": "female",
        "assembly": "GRCh38",
        "ancestry": "European",
        "cases": 9097,
        "controls": 11053,
        "total_sample_size": 20150,
        "total_cohort_count": 15,
        "variant_sample_size_constant": False,
        "effect_scale": "log_odds",
        "target_pmid": "41999721",
        "target_doi": "10.1016/S2665-9913(25)00376-5",
        "analysis_type": "sex_stratified_case_control_gwas",
        "transfer_type": "public_catalog",
        "source_url": "https://data.ebi.ac.uk/ssc/female.tsv.gz",
        "accession": "GCST99999998",
        "provider": "NHGRI-EBI GWAS Catalog",
        "expected_checksum_source": "https://data.ebi.ac.uk/ssc/checksums.sha256",
        "expected_checksum_evidence_type": "repository_manifest",
    }


def clone_rows(rows: list[list[str]] | None = None) -> list[list[str]]:
    return [list(row) for row in (ROWS if rows is None else rows)]


def mutate(
    rows: list[list[str]], header: list[str], row_index: int, field: str, value: str
) -> list[list[str]]:
    result = clone_rows(rows)
    result[row_index][header.index(field)] = value
    return result


def write_table(path: pathlib.Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\t".join(header) + "\n" + "\n".join("\t".join(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def run_case(
    root: pathlib.Path,
    name: str,
    *,
    header: list[str] | None = None,
    rows: list[list[str]] | None = None,
    metadata_update: dict[str, Any] | None = None,
    label: str = "female",
    expected: str = "PASS",
) -> dict[str, Any]:
    case_header = list(HEADER if header is None else header)
    case_rows = clone_rows(rows)
    source = root / f"{name}.tsv"
    write_table(source, case_header, case_rows)
    metadata = base_metadata()
    metadata.update(metadata_update or {})
    metadata["expected_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    if "expected_checksum_evidence_file" not in (metadata_update or {}):
        evidence = root / f"{name}.provider.sha256"
        evidence.write_text(f"{metadata['expected_sha256']}  {source.name}\n", encoding="utf-8")
        metadata["expected_checksum_evidence_file"] = str(evidence)
        metadata["expected_checksum_evidence_sha256"] = hashlib.sha256(evidence.read_bytes()).hexdigest()
    metadata_path = root / f"{name}.metadata.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    output_dir = root / f"out_{name}"
    command = [
        sys.executable,
        str(SCRIPT),
        "--input",
        str(source),
        "--metadata",
        str(metadata_path),
        "--label",
        label,
        "--output-dir",
        str(output_dir),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    result_path = (output_dir / f"{label}_intake_v2_1.json").resolve()
    result: dict[str, Any] | None = None
    if result_path.is_file():
        result = json.loads(result_path.read_text(encoding="utf-8"))
    actual_status = result.get("status") if result else None
    false_pass = expected == "BLOCK" and actual_status == PASS
    missed_expected_pass = expected == "PASS" and actual_status != PASS
    return {
        "name": name,
        "expected": expected,
        "return_code": completed.returncode,
        "actual_status": actual_status,
        "false_pass": false_pass,
        "missed_expected_pass": missed_expected_pass,
        "result_path": str(result_path),
        "result_inside_declared_output_dir": output_dir.resolve() in result_path.parents,
        "base_status": result.get("base_status") if result else None,
        "gates": result.get("gates") if result else None,
        "sample_design_gate": result.get("sample_design_gate") if result else None,
        "anchor_gate": result.get("anchor_gate") if result else None,
        "provenance_gate": result.get("provenance_gate") if result else None,
        "target_identity_gate": result.get("target_identity_gate") if result else None,
        "whole_file": result.get("whole_file") if result else None,
        "stderr_tail": completed.stderr[-1000:],
    }


def input_output_collision_case(root: pathlib.Path) -> dict[str, Any]:
    """Use an input name equal to the first regional output name."""
    name = "input_output_collision"
    output_dir = root / f"out_{name}"
    output_dir.mkdir(parents=True)
    source = output_dir / "female_IRF4_pm1Mb_GRCh38.tsv"
    write_table(source, HEADER, clone_rows())
    before = source.read_bytes()
    metadata = base_metadata()
    metadata["expected_sha256"] = hashlib.sha256(before).hexdigest()
    evidence = root / f"{name}.provider.sha256"
    evidence.write_text(f"{metadata['expected_sha256']}  {source.name}\n", encoding="utf-8")
    metadata["expected_checksum_evidence_file"] = str(evidence)
    metadata["expected_checksum_evidence_sha256"] = hashlib.sha256(evidence.read_bytes()).hexdigest()
    metadata_path = root / f"{name}.metadata.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    command = [
        sys.executable,
        str(SCRIPT),
        "--input",
        str(source),
        "--metadata",
        str(metadata_path),
        "--label",
        "female",
        "--output-dir",
        str(output_dir),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    result_path = output_dir / "female_intake_v2_1.json"
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else None
    after = source.read_bytes() if source.exists() else b""
    actual_status = result.get("status") if result else None
    return {
        "name": name,
        "expected": "BLOCK",
        "return_code": completed.returncode,
        "actual_status": actual_status,
        "false_pass": actual_status == PASS,
        "missed_expected_pass": False,
        "input_mutated": before != after,
        "input_sha256_before": hashlib.sha256(before).hexdigest(),
        "input_sha256_after": hashlib.sha256(after).hexdigest(),
        "input_bytes_before": len(before),
        "input_bytes_after": len(after),
        "gates": result.get("gates") if result else None,
        "stderr_tail": completed.stderr[-1000:],
    }


def main() -> int:
    cases: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="h6_v2_1_independent_") as tmp:
        root = pathlib.Path(tmp)

        # Positive and repaired-boundary controls.
        cases.append(run_case(root, "baseline", expected="PASS"))
        bad_se = mutate(ROWS, HEADER, 1, "standard_error", "not_numeric")
        cases.append(run_case(root, "control_nonnumeric_se", rows=bad_se, expected="BLOCK"))
        bad_eaf = mutate(ROWS, HEADER, 1, "effect_allele_frequency", "not_numeric")
        cases.append(run_case(root, "control_nonnumeric_eaf", rows=bad_eaf, expected="BLOCK"))
        wrong_anchor = mutate(ROWS, HEADER, 1, "base_pair_location", "39330000")
        cases.append(run_case(root, "control_wrong_anchor_coordinate", rows=wrong_anchor, expected="BLOCK"))
        bad_chr_rows = clone_rows() + [
            ["chrUn", "100000", "rsBadChr", "A", "G", "0.1", "0.1", "0.5", "0.4", "0.9", "20150"]
        ]
        cases.append(run_case(root, "control_invalid_chromosome", rows=bad_chr_rows, expected="BLOCK"))
        cases.append(
            run_case(
                root,
                "control_placeholder",
                metadata_update={"source_url": "REPLACE", "accession": "REPLACE", "provider": "REPLACE"},
                expected="BLOCK",
            )
        )

        bare_header = list(HEADER)
        bare_header[-1] = "N"
        cohort_rows = clone_rows()
        cohort_rows[0][-1] = "14"
        cohort_rows[1][-1] = "14.5"
        cases.append(
            run_case(
                root,
                "control_fractional_bare_cohort",
                header=bare_header,
                rows=cohort_rows,
                metadata_update={"bare_n_semantics": "cohort_count"},
                expected="BLOCK",
            )
        )
        cases.append(run_case(root, "control_sparse_single_variant_per_region", rows=ANCHOR_ROWS, expected="BLOCK"))

        # P=0 skips the current effect/SE/P coherence calculation.  A tiny z
        # score paired with zero P must not be accepted as coherent input.
        zero_p_incoherent = clone_rows()
        zero_p_incoherent[1][HEADER.index("beta")] = "0.001"
        zero_p_incoherent[1][HEADER.index("standard_error")] = "1"
        zero_p_incoherent[1][HEADER.index("p_value")] = "0"
        cases.append(run_case(root, "effect_se_p_zero_p_bypass", rows=zero_p_incoherent, expected="BLOCK"))

        # The gross-consistency tolerance is three orders of magnitude.  This
        # fixture stays just inside it while remaining incompatible by ~900x.
        near_threshold_incoherent = clone_rows()
        near_threshold_incoherent[1][HEADER.index("beta")] = "0.1"
        near_threshold_incoherent[1][HEADER.index("standard_error")] = "0.05"
        near_threshold_incoherent[1][HEADER.index("p_value")] = "0.00005"
        cases.append(run_case(root, "effect_se_p_approximately_900fold_mismatch", rows=near_threshold_incoherent, expected="BLOCK"))

        # Exact-anchor identity conflicts that are not covered by the bundled test.
        conflict_inside = clone_rows() + [
            ["22", "39330000", "rs66578187", "C", "G", "0.1", "0.05", "0.1", "0.4", "0.9", "20150"]
        ]
        cases.append(run_case(root, "anchor_conflict_same_rsid_inside_region", rows=conflict_inside, expected="BLOCK"))
        conflict_outside = clone_rows() + [
            ["1", "100000", "rs66578187", "C", "G", "0.1", "0.05", "0.1", "0.4", "0.9", "20150"]
        ]
        cases.append(run_case(root, "anchor_conflict_same_rsid_outside_region", rows=conflict_outside, expected="BLOCK"))

        # Provenance strings are syntactically under-validated and not authenticated.
        cases.append(
            run_case(
                root,
                "provenance_scheme_only_and_na_identifier",
                metadata_update={
                    "source_url": "https:",
                    "accession": "NA",
                    "provider": "NA",
                    "expected_checksum_source": "https:",
                },
                expected="BLOCK",
            )
        )
        cases.append(
            run_case(
                root,
                "provenance_empty_author_markers",
                metadata_update={
                    "source_url": "author-supplied:",
                    "accession": "-",
                    "provider": "-",
                    "expected_checksum_source": "author-manifest:",
                },
                expected="BLOCK",
            )
        )
        cases.append(
            run_case(
                root,
                "checksum_source_unverified_self_assertion",
                metadata_update={
                    "source_url": "https://unrelated.test/file.tsv",
                    "accession": "UNVERIFIED",
                    "provider": "unverified",
                    "expected_checksum_source": "https://unrelated.test/not-retrieved.txt",
                    "expected_checksum_evidence_file": None,
                    "expected_checksum_evidence_sha256": None,
                },
                expected="BLOCK",
            )
        )

        # Target ancestry is called valid when it is merely a non-placeholder string.
        cases.append(run_case(root, "target_ancestry_na", metadata_update={"ancestry": "NA"}, expected="BLOCK"))
        cases.append(run_case(root, "target_ancestry_arbitrary", metadata_update={"ancestry": "Martian"}, expected="BLOCK"))

        # Sample-design contradictions are bypassed when per-variant sample_size exists.
        cases.append(
            run_case(
                root,
                "sample_size_without_case_control_metadata",
                metadata_update={"cases": None, "controls": None, "total_sample_size": None},
                expected="BLOCK",
            )
        )
        cases.append(
            run_case(
                root,
                "sample_size_with_negative_cases",
                metadata_update={"cases": -1, "controls": 20151, "total_sample_size": 20150},
                expected="BLOCK",
            )
        )
        cases.append(
            run_case(
                root,
                "sample_size_with_inconsistent_total",
                metadata_update={"cases": 9097, "controls": 11053, "total_sample_size": 999},
                expected="BLOCK",
            )
        )
        fractional_sample = clone_rows()
        fractional_sample[0][-1] = "0.5"
        fractional_sample[1][-1] = "0.5"
        cases.append(run_case(root, "explicit_sample_size_fractional_below_one", rows=fractional_sample, expected="BLOCK"))
        fractional_bare_sample = clone_rows()
        fractional_bare_sample[0][-1] = "14.5"
        fractional_bare_sample[1][-1] = "14.5"
        cases.append(
            run_case(
                root,
                "bare_n_sample_size_fractional",
                header=bare_header,
                rows=fractional_bare_sample,
                metadata_update={"bare_n_semantics": "sample_size"},
                expected="BLOCK",
            )
        )
        valid_bare_cohort = clone_rows()
        valid_bare_cohort[0][-1] = "14"
        valid_bare_cohort[1][-1] = "15"
        cases.append(
            run_case(
                root,
                "cohort_count_with_inconsistent_total_metadata",
                header=bare_header,
                rows=valid_bare_cohort,
                metadata_update={
                    "bare_n_semantics": "cohort_count",
                    "cases": 9000,
                    "controls": 11000,
                    "total_sample_size": 1,
                },
                expected="BLOCK",
            )
        )

        # Whole-file position range and control-character structure.
        huge_position = clone_rows() + [
            ["1", "999999999999", "rsBeyondChr1", "A", "G", "0.1", "0.05", "0.1", "0.4", "0.9", "20150"]
        ]
        cases.append(run_case(root, "whole_file_position_beyond_chromosome", rows=huge_position, expected="BLOCK"))
        nul_header = list(HEADER)
        nul_header[0] = "chromosome\x00"
        cases.append(run_case(root, "whole_file_nul_in_header", header=nul_header, expected="BLOCK"))
        nul_row = clone_rows() + [
            ["1", "100000", "rsBad\x00Id", "A", "G", "0.1", "0.05", "0.1", "0.4", "0.9", "20150"]
        ]
        cases.append(run_case(root, "whole_file_nul_in_data", rows=nul_row, expected="BLOCK"))

        # Output isolation and source preservation.
        cases.append(run_case(root, "label_path_traversal", label="../female", expected="BLOCK"))
        cases.append(input_output_collision_case(root))

    false_passes = [case["name"] for case in cases if case.get("false_pass")]
    controls_ok = [
        case["name"]
        for case in cases
        if not case.get("false_pass") and not case.get("missed_expected_pass")
    ]
    missed_passes = [case["name"] for case in cases if case.get("missed_expected_pass")]
    result = {
        "suite": "R4A11_H6_V2_1_FINAL_HOSTILE_QA",
        "target_script": str(SCRIPT),
        "target_script_sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
        "intake_core_sha256": hashlib.sha256(SCRIPT.with_name("intake_core.py").read_bytes()).hexdigest(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "status": "FAIL" if false_passes or missed_passes else "PASS",
        "case_count": len(cases),
        "false_pass_count": len(false_passes),
        "false_pass_cases": false_passes,
        "missed_expected_pass_count": len(missed_passes),
        "missed_expected_pass_cases": missed_passes,
        "non_false_pass_cases": controls_ok,
        "cases": cases,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "case_count", "false_pass_count", "false_pass_cases")}, indent=2))
    return 1 if false_passes else 0


if __name__ == "__main__":
    raise SystemExit(main())
