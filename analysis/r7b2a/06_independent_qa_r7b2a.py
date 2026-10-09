#!/usr/bin/env python3
"""Independent fail-closed QA for the complete R7B2A gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
AUDIT = ROOT / "3_results/00_audit/R7B2A/final_qa"
EXPECTED_PROTOCOL_SHA = "1295f072d192fa3ec22631c7a0e4ac247576d2bacc56ca32c599622594ef7c03"
EXPECTED_RP_SHA = "310b307e5463825968ee93e52ca34fb997b6a28b81d79ce791d831fc6f18ed59"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    protocol = ROOT / "0_admin/protocols/R7B2A/R7B2A_matched_input_attribution_freeze_2026-10-09.md"
    rp = ROOT / "9.Version/PBC_研究计划书_RP_v3_调控归因可靠性与同输入方法对照_20261009.docx"
    input_state = json.loads((ROOT / "3_results/00_audit/R7B2A/input_freeze/R7B2A_input_freeze_state.json").read_text(encoding="utf-8"))
    abf_state = json.loads((ROOT / "3_results/04_integration/R7B2A/matched_input_abf/R7B2A_matched_input_ABF_state.json").read_text(encoding="utf-8"))
    attr_state = json.loads((ROOT / "3_results/04_integration/R7B2A/adjudication/R7B2A_attribution_state.json").read_text(encoding="utf-8"))
    sim_state = json.loads((ROOT / "3_results/05_simulation/R7B2A_audit/R7B2A_R7B1C_channel_audit_state.json").read_text(encoding="utf-8"))
    lock_state = json.loads((ROOT / "3_results/04_integration/R7B2A/manuscript_lock/R7B2A_manuscript_lock_state.json").read_text(encoding="utf-8"))
    identity = pd.read_csv(ROOT / "3_results/00_audit/R7B2A/input_freeze/R7B2A_arm_identity_642.tsv", sep="\t")
    abf = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/matched_input_abf/R7B2A_matched_input_ABF_long.tsv.gz", sep="\t")
    traj = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/adjudication/R7B2A_642_four_arm_trajectories.tsv", sep="\t")
    matrices = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/adjudication/R7B2A_adjacent_transition_matrices.tsv", sep="\t")
    hist12 = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/adjudication/R7B2A_historical_12_direction_changes_audit.tsv", sep="\t")
    channels = pd.read_csv(ROOT / "3_results/05_simulation/R7B2A_audit/R7B2A_R7B1C_iteration_channel_audit.tsv.gz", sep="\t")
    ledger = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/manuscript_lock/R7B2A_updated_claim_evidence_ledger.tsv", sep="\t")
    mirror = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/manuscript_lock/R7B2A_methods_results_mirror.tsv", sep="\t")
    manifest = pd.read_csv(ROOT / "3_results/04_integration/R7B2A/manuscript_lock/R7B2A_Figure1_6_panel_source_manifest.tsv", sep="\t")

    checks: list[dict] = []
    def check(name: str, observed, expected) -> None:
        passed = observed == expected
        checks.append({"name": name, "pass": bool(passed), "observed": str(observed), "expected": str(expected)})

    check("protocol_sha256", sha256(protocol), EXPECTED_PROTOCOL_SHA)
    check("RP_v3_sha256", sha256(rp), EXPECTED_RP_SHA)
    check("input_state_pass", input_state["status"], "PASS")
    check("input_comparisons_642", len(identity), 642)
    check("input_unique_comparisons_642", identity["comparison_id"].nunique(), 642)
    check("role_184", int((identity["R7B1B_v2_role"] == "PRIMARY_184_TRIGGER_VERIFICATION").sum()), 184)
    check("role_455", int((identity["R7B1B_v2_role"] == "H3_RESCUE_FALSIFICATION").sum()), 455)
    check("role_3", int((identity["R7B1B_v2_role"] == "BORDERLINE_HIGH_INFORMATION_CALIBRATION").sum()), 3)
    check("GJOKA_unresolved_0", int(identity["gjoka_A1_unresolved_n"].sum()), 0)
    check("ABF_state_pass", abf_state["status"], "PASS")
    check("ABF_rows_3852", len(abf), 3852)
    check("ABF_arms_6", abf["arm"].nunique(), 6)
    check("ABF_technical_failures_0", int((abf["status"] != "PASS").sum()), 0)
    check("A0_top_variant_replay_642", abf_state["A0_shared_top_variant_match"], 642)
    check("A0_numeric_replay_below_1e-10", abf_state["A0_replay_max_abs_delta"] < 1e-10, True)
    check("A1_scale_state_changes_0", attr_state["A1_fixed_native_state_changes"], 0)
    check("A2_scale_state_changes_0", attr_state["A2_fixed_native_state_changes"], 0)
    check("A2_rounding_state_changes_0", attr_state["A2_matchedz_rounded_state_changes"], 0)
    check("trajectory_rows_642", len(traj), 642)
    check("A0_A1_changes_15", int(traj["A0_to_A1_changed"].sum()), 15)
    check("A1_A2_changes_19", int(traj["A1_to_A2_changed"].sum()), 19)
    check("A2_M_changes_139", int(traj["A2_to_M_changed"].sum()), 139)
    check("matched_H4_to_H3_8", int(((traj["A2_simple_state"] == "H4") & (traj["M_simple_state"] == "H3")).sum()), 8)
    check("matched_H3_to_H4_10", int(((traj["A2_simple_state"] == "H3") & (traj["M_simple_state"] == "H4")).sum()), 10)
    check("matched_stable_H4_79", int(((traj["A2_simple_state"] == "H4") & (traj["M_simple_state"] == "H4")).sum()), 79)
    check("matched_stable_H3_413", int(((traj["A2_simple_state"] == "H3") & (traj["M_simple_state"] == "H3")).sum()), 413)
    check("historical_direction_rows_12", len(hist12), 12)
    check("historical_strict_retained_10", int(hist12["strict_direction_retained_after_matching"].sum()), 10)
    for stage in ["A0_TO_A1_SUPPORT_SET", "A1_TO_A2_DISEASE_STATS", "A2_TO_M_MODEL"]:
        check(f"matrix_sum_{stage}_642", int(matrices.loc[matrices["transition"].eq(stage), "n"].sum()), 642)
    check("simulation_gate_scope_limited", sim_state["status"], "PASS_WITH_SCOPE_LIMIT")
    check("simulation_iterations_486000", len(channels), 486000)
    check("simulation_technical_errors_0", int((channels["matched_channel"] == "TECHNICAL_ERROR").sum()), 0)
    check("simulation_noCS_325218", int(channels["matched_channel"].isin(["NO_CS_BOTH", "NO_DISEASE_CS", "NO_QTL_CS"]).sum()), 325218)
    check("simulation_bothCS_noPair_0", int((channels["matched_channel"] == "CS_BOTH_NO_PAIR").sum()), 0)
    check("simulation_pair_evaluable_160782", int(channels["matched_channel"].str.startswith("PAIR_").sum()), 160782)
    check("simulation_rerun_not_required", sim_state["rerun_required"], False)
    check("claim_ledger_27", len(ledger), 27)
    check("claim_ids_unique", ledger["claim_id"].nunique(), 27)
    check("claim_status_allowed", sorted(ledger["status"].unique().tolist()), ["SUPPORTED", "SUPPORTED_BOUNDARY"])
    check("methods_results_mirror_10", len(mirror), 10)
    check("figure_manifest_1_to_6", sorted(manifest["figure"].astype(int).unique().tolist()), [1, 2, 3, 4, 5, 6])
    check("manuscript_lock_state_pass", lock_state["status"], "PASS")
    check("new_candidate_selection_0", lock_state["new_candidate_selection"], 0)

    missing_claim_sources = []
    for row in ledger.itertuples(index=False):
        for field in [row.primary_source_file, row.supporting_source_files]:
            if pd.isna(field):
                continue
            for item in str(field).split(";"):
                item = item.strip()
                if not item:
                    continue
                if not (ROOT / item).exists():
                    missing_claim_sources.append(f"{row.claim_id}:{item}")
    check("all_claim_sources_exist", missing_claim_sources, [])

    r7b1e_base = ROOT / "3_results/04_integration/R7B1E"
    missing_panel_sources = []
    for row in manifest.itertuples(index=False):
        for item in str(row.source_files).split(";"):
            item = item.strip()
            candidate = ROOT / item if item.startswith(("3_results/", "4_figures/")) else r7b1e_base / item
            if not candidate.exists():
                missing_panel_sources.append(f"F{row.figure}{row.panel}:{item}")
    check("all_panel_sources_exist", missing_panel_sources, [])
    for stem in ["R7B2A_Figure2_attribution_prototype", "R7B2A_Figure3_simulation_channels_prototype"]:
        for ext in ["png", "pdf", "svg"]:
            p = ROOT / "4_figures/R7B2A" / f"{stem}.{ext}"
            check(f"figure_exists_{stem}_{ext}", p.exists() and p.stat().st_size > 1000, True)

    qa = pd.DataFrame(checks)
    qa_path = AUDIT / "R7B2A_independent_QA.tsv"
    qa.to_csv(qa_path, sep="\t", index=False)
    failures = qa.loc[~qa["pass"], "name"].tolist()
    state = {
        "schema": "R7B2A_INDEPENDENT_QA_1.0",
        "status": "PASS" if not failures else "FAIL",
        "checks": len(qa),
        "passed": int(qa["pass"].sum()),
        "failed": len(failures),
        "failure_names": failures,
        "qa_tsv_sha256": sha256(qa_path),
        "gates": {
            "V3-G0_INPUT_LOCK": input_state["status"],
            "V3-G1_CONTRAST_VALID": abf_state["status"],
            "V3-G2_COVERAGE": abf_state["status"],
            "V3-G3_SIMULATION_INTERPRETABLE": sim_state["status"],
            "V3-G4_ATTRIBUTION": attr_state["status"],
            "V3-G5_MANUSCRIPT_LOCK_ASSETS": lock_state["status"],
        },
    }
    state_path = AUDIT / "R7B2A_independent_QA.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
