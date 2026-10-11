#!/usr/bin/env python3
"""Reproduce the FG7 validator gaps and regression-test the hardened validator."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_fixture(prefix: Path, rows: pd.DataFrame, matrix: np.ndarray) -> tuple[Path, Path]:
    bim = Path(str(prefix) + ".bim")
    ld = Path(str(prefix) + ".ld")
    pd.DataFrame({
        0: rows["CHR"], 1: rows["MarkerID"], 2: "0", 3: rows["POS"],
        4: rows["Allele1"], 5: rows["Allele2"],
    }).to_csv(bim, sep="\t", header=False, index=False, lineterminator="\n")
    np.savetxt(ld, matrix, fmt="%.8g", delimiter="\t")
    return bim, ld


def invoke(script: Path, bim: Path, ld: Path, a: argparse.Namespace, output: Path) -> dict:
    cmd = [
        sys.executable, str(script), "--bim", str(bim), "--ld", str(ld),
        "--variant-manifest", str(a.variant_manifest), "--cs-manifest", str(a.cs_manifest),
        "--anchors", str(a.anchors), "--out-json", str(output),
    ]
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    payload = None
    if output.is_file():
        try:
            payload = json.loads(output.read_text(encoding="utf-8"))
        except Exception as exc:
            payload = {"parse_error": str(exc)}
    return {
        "exit_code": p.returncode,
        "status": payload.get("status") if isinstance(payload, dict) else None,
        "requested_fraction": (
            payload.get("metrics", {}).get("requested_1366_fraction") if isinstance(payload, dict) else None
        ),
        "fail_reasons": payload.get("fail_reasons", []) if isinstance(payload, dict) else [],
        "json_written": output.is_file(),
        "stderr_tail": p.stderr[-1000:],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--original-validator", type=Path, required=True)
    ap.add_argument("--hardened-validator", type=Path, required=True)
    ap.add_argument("--variant-manifest", type=Path, required=True)
    ap.add_argument("--cs-manifest", type=Path, required=True)
    ap.add_argument("--anchors", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    a = ap.parse_args()

    vm = pd.read_csv(a.variant_manifest, sep="\t", dtype=str, keep_default_na=False)
    cs = pd.read_csv(a.cs_manifest, sep="\t", dtype=str, keep_default_na=False)
    anchors = pd.read_csv(a.anchors, sep="\t", dtype=str, keep_default_na=False)
    partial_keys = set(cs["variant_key"]) | set(anchors["variant_key"])
    partial = vm.loc[vm["MarkerID"].isin(partial_keys)].copy()

    with tempfile.TemporaryDirectory(prefix="r4a12fg7qa_") as td:
        temp = Path(td)
        full_bim, full_ld = write_fixture(temp / "full_identity", vm, np.eye(len(vm)))
        partial_bim, partial_ld = write_fixture(temp / "partial_identity", partial, np.eye(len(partial)))
        nonfinite = np.eye(len(partial))
        nonfinite[0, 1] = np.nan
        nonfinite[1, 0] = np.nan
        nf_bim, nf_ld = write_fixture(temp / "partial_nonfinite", partial, nonfinite)

        tests = {
            "original_partial_fixture": invoke(a.original_validator, partial_bim, partial_ld, a, temp / "orig_partial.json"),
            "hardened_partial_fixture": invoke(a.hardened_validator, partial_bim, partial_ld, a, temp / "new_partial.json"),
            "original_nonfinite_fixture": invoke(a.original_validator, nf_bim, nf_ld, a, temp / "orig_nonfinite.json"),
            "hardened_nonfinite_fixture": invoke(a.hardened_validator, nf_bim, nf_ld, a, temp / "new_nonfinite.json"),
            "hardened_full_identity_fixture": invoke(a.hardened_validator, full_bim, full_ld, a, temp / "new_full.json"),
        }
        fixture_metrics = {
            "full_variants": len(vm), "partial_variants": len(partial),
            "partial_fraction": len(partial) / len(vm),
        }

    assertions = {
        "reproduced_original_false_pass": (
            tests["original_partial_fixture"]["status"] == "PASS_SOURCE_LD_STRUCTURAL_GATE"
            and tests["original_partial_fixture"]["requested_fraction"] < 1.0
        ),
        "hardened_rejects_partial": (
            tests["hardened_partial_fixture"]["exit_code"] == 2
            and tests["hardened_partial_fixture"]["status"] == "HOLD_SOURCE_LD_STRUCTURAL_GATE"
        ),
        "hardened_handles_nonfinite_as_hold": (
            tests["hardened_nonfinite_fixture"]["exit_code"] == 2
            and tests["hardened_nonfinite_fixture"]["status"] == "HOLD_SOURCE_LD_STRUCTURAL_GATE"
            and tests["hardened_nonfinite_fixture"]["json_written"]
        ),
        "hardened_accepts_complete_structural_positive_control": (
            tests["hardened_full_identity_fixture"]["exit_code"] == 0
            and tests["hardened_full_identity_fixture"]["status"] == "PASS_SOURCE_LD_STRUCTURAL_GATE"
            and tests["hardened_full_identity_fixture"]["requested_fraction"] == 1.0
        ),
    }
    payload = {
        "schema_version": "R4A12FG7QA-hostile-tests-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "original_validator_sha256": sha256(a.original_validator),
            "hardened_validator_sha256": sha256(a.hardened_validator),
            "variant_manifest_sha256": sha256(a.variant_manifest),
            "cs_manifest_sha256": sha256(a.cs_manifest),
            "anchors_sha256": sha256(a.anchors),
        },
        "fixture_metrics": fixture_metrics,
        "tests": tests,
        "assertions": assertions,
        "overall": "PASS" if all(assertions.values()) else "FAIL",
    }
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(0 if payload["overall"] == "PASS" else 1)


if __name__ == "__main__":
    main()
