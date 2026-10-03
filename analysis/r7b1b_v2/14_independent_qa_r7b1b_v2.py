#!/usr/bin/env python3
"""Independent mechanical QA for the R7B1B v2 execution and adjudication."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
AUDIT = ROOT / "3_results/00_audit/R7B1B_v2"
WORK = AUDIT / "R7B1B_v2_exact_642_high_information_comparisons.tsv"
BLOCKS = AUDIT / "R7B1B_v2_exact_286_cell_locus_blocks.tsv"
MEMBERS = AUDIT / "R7B1B_v2_required_94_GJOKA_members.tsv"
INTAKE = ROOT / "1_data/study_inputs/PBC_GJOKA/R7B1B_v2"
MULTI = ROOT / "3_results/04_integration/R7B1B_v2/multisignal"
ADJ = ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"
OUT = AUDIT / "independent_QA"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def truth(value: object) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    return str(value).strip().upper() == "TRUE"


def independent_config(frame: pd.DataFrame, config: str) -> tuple[bool, bool, bool]:
    default = frame[(frame.config == config) & np.isclose(frame.p12, 1e-5)].copy()
    skeptical = frame[(frame.config == config) & np.isclose(frame.p12, 1e-6)].copy()
    if default.empty:
        return False, False, False
    skeptical_lookup = {
        (str(row.idx1), str(row.idx2)): float(row.H4_over_H3H4)
        for row in skeptical.itertuples(index=False)
    }
    h4 = False
    # Use row indexing because itertuples sanitizes posterior column names.
    for _, row in default.iterrows():
        key = (str(row["idx1"]), str(row["idx2"]))
        if row["PP.H4.abf"] >= 0.80 and row["H4_over_H3H4"] >= 0.80 and skeptical_lookup.get(key, -math.inf) >= 0.50:
            h4 = True
            break
    h3 = bool(((default["PP.H3.abf"] >= 0.80) & (default["H4_over_H3H4"] <= 0.20)).any())
    high = bool((default["H3_plus_H4"] >= 0.80).any())
    return h4, h3, high


def expected_state(frame: pd.DataFrame) -> str:
    statuses = {cfg: independent_config(frame, cfg) for cfg in ("PF10_L5", "PF10_L10", "PF10_L20")}
    h4 = statuses["PF10_L10"][0] and sum(v[0] for v in statuses.values()) >= 2
    h3 = (not h4) and statuses["PF10_L10"][1] and sum(v[1] for v in statuses.values()) >= 2
    if h4:
        return "H4_SUPPORTED_STABLE"
    if h3:
        return "H3_SUPPORTED_STABLE"
    if any(any(v) for v in statuses.values()):
        return "MODEL_SENSITIVE"
    return "UNINFORMATIVE"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    work = pd.read_csv(WORK, sep="\t", dtype={"comparison_id": str})
    blocks = pd.read_csv(BLOCKS, sep="\t")
    members = pd.read_csv(MEMBERS, sep="\t")
    final = pd.read_csv(ADJ, sep="\t", dtype={"comparison_id": str})
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object, expected: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "observed": str(observed), "expected": str(expected)})

    check("workload_rows", len(work) == 642, len(work), 642)
    check("workload_unique_ids", work.comparison_id.nunique() == 642, work.comparison_id.nunique(), 642)
    check("block_rows", len(blocks) == 286, len(blocks), 286)
    check("member_rows", len(members) == 94, len(members), 94)
    check("adjudication_rows", len(final) == 642, len(final), 642)
    check("adjudication_key_identity", set(final.comparison_id) == set(work.comparison_id), len(set(final.comparison_id)^set(work.comparison_id)), 0)
    check("primary_184", int((work.R7B1B_v2_role == "PRIMARY_184_TRIGGER_VERIFICATION").sum()) == 184,
          int((work.R7B1B_v2_role == "PRIMARY_184_TRIGGER_VERIFICATION").sum()), 184)
    check("h3_rescue_455", int((work.R7B1B_v2_role == "H3_RESCUE_FALSIFICATION").sum()) == 455,
          int((work.R7B1B_v2_role == "H3_RESCUE_FALSIFICATION").sum()), 455)
    check("borderline_3", int((work.R7B1B_v2_role == "BORDERLINE_HIGH_INFORMATION_CALIBRATION").sum()) == 3,
          int((work.R7B1B_v2_role == "BORDERLINE_HIGH_INFORMATION_CALIBRATION").sum()), 3)

    missing_members = [name for name in members["member"].astype(str) if not (INTAKE / Path(name).name).is_file()]
    check("GJOKA_94_files_present", not missing_members, len(missing_members), 0)
    qtl_receipts = pd.read_csv(AUDIT / "R7B1B_v2_dualmodel_QTL_receipts.tsv", sep="\t")
    ld_receipts = pd.read_csv(AUDIT / "R7B1B_v2_sourceLD_block_receipts.tsv", sep="\t")
    regression = pd.read_csv(AUDIT / "R7B1B_v2_original184_PF10_regression_QA.tsv", sep="\t")
    check("dualmodel_QTL_1284", len(qtl_receipts) == 1284, len(qtl_receipts), 1284)
    check("sourceLD_blocks_286", len(ld_receipts) == 286 and ld_receipts.gate_pass.map(truth).all(), len(ld_receipts), 286)
    check("original184_regression", len(regression) == 184 and regression["pass"].map(truth).all(), len(regression), 184)

    state_count = 0
    fit_rows = 0
    raw_states: dict[str, str] = {}
    nonconverged = 0
    for row in work.itertuples(index=False):
        directory = MULTI / f"locus_{int(row.locus_index):02d}"
        sp = directory / f"{row.comparison_id}_state.json"
        fp = directory / f"{row.comparison_id}_fit_QC.tsv"
        cp = directory / f"{row.comparison_id}_coloc_susie.tsv.gz"
        if not sp.exists() or not fp.exists() or not cp.exists():
            continue
        state = json.loads(sp.read_text(encoding="utf-8"))
        state_count += 1
        fit = pd.read_csv(fp, sep="\t")
        fit_rows += len(fit)
        if len(fit) != 4 or not all(truth(x) for x in fit.disease_converged) or not all(truth(x) for x in fit.qtl_converged):
            nonconverged += 1
        if state.get("status") != "COMPLETE":
            raw_states[str(row.comparison_id)] = "QC_FAILURE"
        elif cp.stat().st_size == 0:
            raw_states[str(row.comparison_id)] = "UNINFORMATIVE"
        else:
            try:
                posterior = pd.read_csv(cp, sep="\t")
            except pd.errors.EmptyDataError:
                posterior = pd.DataFrame()
            raw_states[str(row.comparison_id)] = "UNINFORMATIVE" if posterior.empty else expected_state(posterior)
    check("comparison_states_642", state_count == 642, state_count, 642)
    check("fit_rows_2568", fit_rows == 2568, fit_rows, 2568)
    check("all_fits_converged", nonconverged == 0, nonconverged, 0)
    merged = final.set_index("comparison_id")
    mismatches = [cid for cid, value in raw_states.items() if str(merged.loc[cid, "PF10_multisignal_state"]) != value]
    check("independent_PF10_state_reproduction", not mismatches, len(mismatches), 0)
    allowed = {
        "STABLE_H4", "H4_TO_H3", "H4_TO_MODEL_SENSITIVE", "H4_TO_UNINFORMATIVE",
        "H3_TO_H4", "STABLE_H3", "H3_TO_MODEL_SENSITIVE", "H3_TO_UNINFORMATIVE",
        "AMBIGUITY_TO_H4", "AMBIGUITY_TO_H3", "AMBIGUITY_REMAINS_MODEL_SENSITIVE", "AMBIGUITY_TO_UNINFORMATIVE",
        "BORDERLINE_TO_H4", "BORDERLINE_TO_H3", "BORDERLINE_MODEL_SENSITIVE", "BORDERLINE_UNINFORMATIVE", "QC_FAILURE",
    }
    check("classification_vocabulary", set(final.reclassification).issubset(allowed), sorted(set(final.reclassification)-allowed), [])
    check("no_unreported_rows", final.reclassification.notna().all(), int(final.reclassification.isna().sum()), 0)

    frame = pd.DataFrame(checks)
    receipt_path = OUT / "R7B1B_v2_independent_QA_checks.tsv"
    frame.to_csv(receipt_path, sep="\t", index=False)
    state = {
        "schema": "R7B1B_V2_INDEPENDENT_QA_1.0",
        "status": "PASS" if frame["pass"].all() else "FAIL",
        "checks": len(frame),
        "passed": int(frame["pass"].sum()),
        "failed": int((~frame["pass"]).sum()),
        "failed_checks": frame.loc[~frame["pass"], "check"].tolist(),
        "workload_sha256": sha256(WORK),
        "adjudication_sha256": sha256(ADJ),
        "receipt_sha256": sha256(receipt_path),
    }
    (OUT / "R7B1B_v2_independent_QA_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2))
    if state["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
