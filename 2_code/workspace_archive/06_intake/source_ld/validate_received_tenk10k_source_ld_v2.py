#!/usr/bin/env python3
"""Strict intake gate for the frozen TenK10K IL12RB2 source-LD request.

Exit codes: 0 = PASS, 2 = scientific/structural HOLD, 3 = validator/input error.
The report is written atomically for every outcome.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


EXPECTED_GENE = "ENSG00000081985"
EXPECTED_VARIANTS = 1366
EXPECTED_CELLS = {"NK", "CD8_TEM", "CD4_CTL", "CD4_TCM"}
REQUIRED_VM_COLUMNS = {
    "variant_key", "MarkerID", "CHR", "POS", "Allele1", "Allele2", "gene"
}
REQUIRED_CS_COLUMNS = {"celltype", "source_cs", "variant_key", "source_pip"}
REQUIRED_ANCHOR_COLUMNS = {"role", "variant_key", "required"}
ALLELE_RE = re.compile(r"^[ACGT]+$")
MARKER_RE = re.compile(r"^(?:chr)?([0-9XYM]+):(\d+):([ACGT]+):([ACGT]+)$", re.I)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def truthy(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def base_report(args: argparse.Namespace) -> dict:
    return {
        "schema_version": "R4A12FG7QA-source-ld-validator-v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "ERROR_SOURCE_LD_VALIDATOR",
        "decision_scope": (
            "TenK10K IL12RB2 molecular-QTL source-LD intake only; "
            "this result cannot satisfy the separate disease-GWAS LD gate."
        ),
        "inputs": {
            key: {"path": str(Path(getattr(args, key)).resolve())}
            for key in ("bim", "ld", "variant_manifest", "cs_manifest", "anchors")
        },
        "checks": {},
        "metrics": {},
        "fail_reasons": [],
    }


def add_check(report: dict, name: str, passed: bool, reason: str | None = None) -> None:
    report["checks"][name] = bool(passed)
    if not passed and reason:
        report["fail_reasons"].append(f"{name}: {reason}")


def validate_manifest(vm: pd.DataFrame, report: dict) -> None:
    missing = sorted(REQUIRED_VM_COLUMNS - set(vm.columns))
    add_check(report, "variant_manifest_schema", not missing, f"missing columns {missing}" if missing else None)
    if missing:
        raise ValueError("variant manifest schema is incomplete")

    report["metrics"]["variant_manifest_rows"] = int(len(vm))
    add_check(
        report, "variant_manifest_exactly_1366", len(vm) == EXPECTED_VARIANTS,
        f"expected {EXPECTED_VARIANTS}, observed {len(vm)}"
    )
    add_check(report, "variant_manifest_marker_unique", not vm["MarkerID"].astype(str).duplicated().any(), "duplicate MarkerID")
    add_check(report, "variant_manifest_key_unique", not vm["variant_key"].astype(str).duplicated().any(), "duplicate variant_key")
    add_check(report, "variant_manifest_marker_equals_key", vm["MarkerID"].astype(str).equals(vm["variant_key"].astype(str)), "MarkerID and variant_key differ")
    add_check(report, "variant_manifest_gene", set(vm["gene"].astype(str)) == {EXPECTED_GENE}, "unexpected or mixed gene")

    format_ok = True
    column_ok = True
    for row in vm.itertuples(index=False):
        marker = str(row.MarkerID)
        match = MARKER_RE.fullmatch(marker)
        if not match:
            format_ok = False
            continue
        chrom, pos, a1, a2 = match.groups()
        if (
            chrom.removeprefix("chr") != str(row.CHR).removeprefix("chr")
            or int(pos) != int(row.POS)
            or a1.upper() != str(row.Allele1).upper()
            or a2.upper() != str(row.Allele2).upper()
            or not ALLELE_RE.fullmatch(str(row.Allele1).upper())
            or not ALLELE_RE.fullmatch(str(row.Allele2).upper())
        ):
            column_ok = False
    add_check(report, "variant_manifest_marker_format", format_ok, "one or more MarkerID values are noncanonical")
    add_check(report, "variant_manifest_columns_match_marker", column_ok, "CHR/POS/alleles disagree with MarkerID")


def validate_support_manifests(
    vm: pd.DataFrame, cs: pd.DataFrame, anchors: pd.DataFrame, report: dict
) -> tuple[pd.DataFrame, pd.DataFrame]:
    cs_missing = sorted(REQUIRED_CS_COLUMNS - set(cs.columns))
    anchor_missing = sorted(REQUIRED_ANCHOR_COLUMNS - set(anchors.columns))
    add_check(report, "cs_manifest_schema", not cs_missing, f"missing columns {cs_missing}" if cs_missing else None)
    add_check(report, "anchor_manifest_schema", not anchor_missing, f"missing columns {anchor_missing}" if anchor_missing else None)
    if cs_missing or anchor_missing:
        raise ValueError("support manifest schema is incomplete")

    cs = cs.copy()
    cs["source_pip"] = pd.to_numeric(cs["source_pip"], errors="coerce")
    add_check(report, "cs_pip_finite_positive", bool(np.isfinite(cs["source_pip"]).all() and (cs["source_pip"] > 0).all()), "invalid source_pip")
    cells = set(cs["celltype"].astype(str))
    add_check(report, "cs_exact_four_cells", cells == EXPECTED_CELLS, f"observed cells {sorted(cells)}")
    add_check(
        report, "cs_rows_unique",
        not cs[["celltype", "source_cs", "variant_key"]].astype(str).duplicated().any(),
        "duplicate celltype/source_cs/variant_key"
    )
    vm_keys = set(vm["variant_key"].astype(str))
    cs_keys = set(cs["variant_key"].astype(str))
    add_check(report, "cs_variants_in_frozen_manifest", cs_keys <= vm_keys, f"{len(cs_keys - vm_keys)} CS variants absent")

    required = anchors.loc[truthy(anchors["required"])].copy()
    report["metrics"]["required_anchor_rows"] = int(len(required))
    add_check(report, "anchor_keys_unique", not required["variant_key"].astype(str).duplicated().any(), "duplicate required anchor")
    required_keys = set(required["variant_key"].astype(str))
    add_check(report, "anchors_in_frozen_manifest", required_keys <= vm_keys, f"{len(required_keys - vm_keys)} anchors absent")
    return cs, required


def write_subset(prefix: Path, vm: pd.DataFrame, bim: pd.DataFrame, ld: np.ndarray) -> dict:
    order = [int(bim.index[bim["SNP"] == marker][0]) for marker in vm["MarkerID"].astype(str)]
    sub_bim = bim.iloc[order]
    sub_ld = ld[np.ix_(order, order)]
    bim_path = Path(str(prefix) + ".bim")
    ld_path = Path(str(prefix) + ".ld")
    bim_path.parent.mkdir(parents=True, exist_ok=True)
    sub_bim.to_csv(bim_path, sep="\t", header=False, index=False, lineterminator="\n")
    np.savetxt(ld_path, sub_ld, fmt="%.12g", delimiter="\t")
    return {
        "bim": {"path": str(bim_path.resolve()), "sha256": sha256(bim_path)},
        "ld": {"path": str(ld_path.resolve()), "sha256": sha256(ld_path)},
        "variant_order": "frozen variant_manifest row order",
    }


def run(args: argparse.Namespace, report: dict) -> int:
    paths = {key: Path(getattr(args, key)) for key in ("bim", "ld", "variant_manifest", "cs_manifest", "anchors")}
    for key, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"{key} not found: {path}")
        report["inputs"][key].update({"bytes": path.stat().st_size, "sha256": sha256(path)})

    vm = pd.read_csv(paths["variant_manifest"], sep="\t", dtype=str, keep_default_na=False)
    cs = pd.read_csv(paths["cs_manifest"], sep="\t", dtype=str, keep_default_na=False)
    anchors = pd.read_csv(paths["anchors"], sep="\t", dtype=str, keep_default_na=False)
    validate_manifest(vm, report)
    cs, required_anchors = validate_support_manifests(vm, cs, anchors, report)

    bim = pd.read_csv(
        paths["bim"], sep=r"\s+", header=None,
        names=["CHR", "SNP", "CM", "POS", "A1", "A2"], dtype=str, keep_default_na=False,
    )
    if len(bim) > args.max_variants:
        raise ValueError(f"BIM has {len(bim)} rows, above --max-variants={args.max_variants}")
    report["metrics"]["n_ld_variants"] = int(len(bim))
    add_check(report, "bim_nonempty", len(bim) > 0, "BIM is empty")
    add_check(report, "bim_six_columns", bim.shape[1] == 6, "BIM must have six columns")
    add_check(report, "bim_snp_unique", not bim["SNP"].duplicated().any(), "duplicate BIM SNP IDs")

    ld = np.loadtxt(paths["ld"], dtype=float, ndmin=2)
    shape_ok = ld.ndim == 2 and ld.shape[0] == ld.shape[1] == len(bim)
    report["metrics"]["ld_shape"] = [int(x) for x in ld.shape]
    add_check(report, "square_shape_matches_bim", shape_ok, f"LD shape {ld.shape}, BIM rows {len(bim)}")

    finite = bool(np.isfinite(ld).all())
    add_check(report, "finite", finite, "LD contains NaN or infinite values")
    if shape_ok and finite and len(bim):
        max_sym = float(np.max(np.abs(ld - ld.T)))
        max_diag = float(np.max(np.abs(np.diag(ld) - 1.0)))
        report["metrics"]["max_symmetry_error"] = max_sym
        report["metrics"]["max_diag_error"] = max_diag
        add_check(report, "symmetric", max_sym <= args.symmetry_tolerance, f"max error {max_sym}")
        add_check(report, "diag_one", max_diag <= args.diag_tolerance, f"max error {max_diag}")
        eig = np.linalg.eigvalsh((ld + ld.T) / 2.0)
        min_eig = float(eig.min())
        report["metrics"]["min_eigenvalue"] = min_eig
        add_check(report, "psd_tolerance", min_eig >= -args.psd_tolerance, f"minimum eigenvalue {min_eig}")
    else:
        for name in ("symmetric", "diag_one", "psd_tolerance"):
            add_check(report, name, False, "not evaluated because matrix shape/finite check failed")

    req = list(vm["MarkerID"].astype(str))
    native = set(bim["SNP"].astype(str))
    covered = [marker for marker in req if marker in native]
    report["metrics"]["requested_1366_covered"] = int(len(covered))
    report["metrics"]["requested_1366_fraction"] = float(len(covered) / EXPECTED_VARIANTS)
    report["metrics"]["extra_bim_variants"] = int(len(native - set(req)))
    add_check(
        report, "all_requested_1366_present", len(covered) == EXPECTED_VARIANTS,
        f"covered {len(covered)}/{EXPECTED_VARIANTS}"
    )

    vm_idx = vm.set_index("MarkerID", verify_integrity=False)
    allele_checked = 0
    allele_ok = 0
    for row in bim.itertuples(index=False):
        marker = str(row.SNP)
        if marker in vm_idx.index:
            allele_checked += 1
            q = vm_idx.loc[marker]
            if str(row.A1).upper() == str(q.Allele1).upper() and str(row.A2).upper() == str(q.Allele2).upper():
                allele_ok += 1
    report["metrics"]["allele_rows_checked"] = int(allele_checked)
    report["metrics"]["native_A1A2_exact_rows"] = int(allele_ok)
    add_check(
        report, "native_allele_orientation_all_1366",
        allele_checked == EXPECTED_VARIANTS and allele_ok == EXPECTED_VARIANTS,
        f"exact orientation {allele_ok}/{EXPECTED_VARIANTS}; checked {allele_checked}"
    )

    anchor_rows = []
    for row in required_anchors.itertuples(index=False):
        present = str(row.variant_key) in native
        anchor_rows.append({"role": str(row.role), "variant_key": str(row.variant_key), "present": present})
    report["anchors"] = anchor_rows
    add_check(report, "all_required_anchors", bool(anchor_rows) and all(x["present"] for x in anchor_rows), "one or more required anchors absent")

    cs_rows = []
    for (cell, csid), group in cs.groupby(["celltype", "source_cs"], dropna=False):
        total = float(group["source_pip"].sum())
        present = group["variant_key"].astype(str).isin(native)
        kept = float(group.loc[present, "source_pip"].sum())
        fraction = kept / total if total > 0 else None
        cs_rows.append({
            "celltype": str(cell), "source_cs": str(csid), "members": int(len(group)),
            "pip_total": total, "pip_present": kept, "pip_fraction": fraction,
        })
    report["source_cs"] = cs_rows
    add_check(
        report, "all_source_cs_pip_ge_0_95",
        bool(cs_rows) and all(x["pip_fraction"] is not None and x["pip_fraction"] >= 0.95 for x in cs_rows),
        "one or more frozen source credible sets have <95% PIP coverage"
    )

    core = [
        "variant_manifest_schema", "variant_manifest_exactly_1366", "variant_manifest_marker_unique",
        "variant_manifest_key_unique", "variant_manifest_marker_equals_key", "variant_manifest_gene",
        "variant_manifest_marker_format", "variant_manifest_columns_match_marker", "cs_manifest_schema",
        "anchor_manifest_schema", "cs_pip_finite_positive", "cs_exact_four_cells", "cs_rows_unique",
        "cs_variants_in_frozen_manifest", "anchor_keys_unique", "anchors_in_frozen_manifest",
        "bim_nonempty", "bim_six_columns", "bim_snp_unique", "square_shape_matches_bim", "finite",
        "symmetric", "diag_one", "psd_tolerance", "all_requested_1366_present",
        "native_allele_orientation_all_1366", "all_required_anchors", "all_source_cs_pip_ge_0_95",
    ]
    passed = all(report["checks"].get(name, False) for name in core)
    report["core_checks"] = core
    report["status"] = "PASS_SOURCE_LD_STRUCTURAL_GATE" if passed else "HOLD_SOURCE_LD_STRUCTURAL_GATE"
    if passed and args.subset_prefix:
        report["requested_subset"] = write_subset(Path(args.subset_prefix), vm, bim, ld)
    return 0 if passed else 2


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Strictly validate received TenK10K native IL12RB2 .bim/.ld.")
    ap.add_argument("--bim", required=True)
    ap.add_argument("--ld", required=True)
    ap.add_argument("--variant-manifest", required=True)
    ap.add_argument("--cs-manifest", required=True)
    ap.add_argument("--anchors", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--subset-prefix", help="On PASS, emit the 1,366 requested variants in manifest order.")
    ap.add_argument("--max-variants", type=int, default=10000)
    ap.add_argument("--symmetry-tolerance", type=float, default=1e-8)
    ap.add_argument("--diag-tolerance", type=float, default=1e-8)
    ap.add_argument("--psd-tolerance", type=float, default=1e-7)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    report = base_report(args)
    try:
        exit_code = run(args, report)
    except Exception as exc:  # Always produce a machine-readable receipt.
        report["status"] = "ERROR_SOURCE_LD_VALIDATOR"
        report["fail_reasons"].append(f"validator_error: {type(exc).__name__}: {exc}")
        exit_code = 3
    atomic_json(Path(args.out_json), report)
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
