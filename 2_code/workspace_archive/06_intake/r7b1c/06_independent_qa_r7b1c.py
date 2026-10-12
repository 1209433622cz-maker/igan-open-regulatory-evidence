#!/usr/bin/env python3
"""Independent mechanical QA for the R7B1C full simulation outputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
GRID = pd.read_csv(ROOT / "3_results/00_audit/R7B1C/R7B1C_implementation_grid_486.tsv", sep="\t")
RAW = ROOT / "3_results/05_simulation/R7B1C/full"
AGG = ROOT / "3_results/05_simulation/R7B1C/aggregate"
OUT = ROOT / "3_results/00_audit/R7B1C/independent_QA"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []
    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    add("grid_486", len(GRID) == 486, str(len(GRID)))
    add("grid_replicates_486000", int(GRID.replicates.sum()) == 486000, str(int(GRID.replicates.sum())))
    states = list(RAW.glob("R7B1C_G*.state.json")); results = list(RAW.glob("R7B1C_G*.tsv.gz"))
    add("state_files_486", len(states) == 486, str(len(states)))
    add("result_files_486", len(results) == 486, str(len(results)))
    bad_states = []
    for path in states:
        state = json.loads(path.read_text(encoding="utf-8"))
        if state.get("status") != "COMPLETE" or state.get("replicates") != 1000:
            bad_states.append(path.name)
    add("all_states_complete", not bad_states, ",".join(bad_states[:10]) or "0 bad")

    combined_path = AGG / "R7B1C_all_486000_replicates.tsv.gz"
    d = pd.read_csv(combined_path, sep="\t", low_memory=False)
    add("combined_rows_486000", len(d) == 486000, str(len(d)))
    add("unique_grid_replicate", not d.duplicated(["grid_id", "replicate"]).any(), str(int(d.duplicated(["grid_id", "replicate"]).sum())))
    add("grid_ids_exact", set(d.grid_id) == set(GRID.grid_id), f"{d.grid_id.nunique()}")
    counts = d.scenario.value_counts()
    add("six_scenarios_81000_each", len(counts) == 6 and (counts == 81000).all(), counts.to_dict().__repr__())
    template_counts = d.groupby(["grid_id", "template_id"]).size().unstack(fill_value=0)
    add("templates_500_each_per_grid", template_counts.shape == (486, 2) and (template_counts == 500).all().all(), str(template_counts.min().min()))
    add("abf_complete", d.abf_h4.notna().all(), str(int(d.abf_h4.notna().sum())))
    add("matched_fit_success_ge_99pct", d.matched_ok.mean() >= 0.99, f"{d.matched_ok.mean():.8f}")
    add("matched_convergence_ge_99pct", d.matched_converged.mean() >= 0.99, f"{d.matched_converged.mean():.8f}")
    s6 = d[d.scenario == "S6_matched_vs_mismatched_LD"]
    add("S6_mismatch_complete", len(s6) == 81000 and s6.mismatch_ok.notna().all(), f"{len(s6)}")
    add("nonS6_mismatch_absent", d[d.scenario != "S6_matched_vs_mismatched_LD"].mismatch_ok.isna().all(), "expected NA")
    add("state_labels_valid", set(d.abf_state.dropna()) <= {"H4","H3","UNINFORMATIVE"} and set(d.matched_state.dropna()) <= {"H4","H3","UNINFORMATIVE","QC_FAILURE"}, "valid")

    row = pd.read_csv(AGG / "R7B1C_grid_486_summary.tsv", sep="\t")
    scenario = pd.read_csv(AGG / "R7B1C_scenario_summary.tsv", sep="\t")
    add("row_summary_486", len(row) == 486 and set(row.grid_id) == set(GRID.grid_id), str(len(row)))
    add("scenario_summary_6", len(scenario) == 6, str(len(scenario)))
    recomputed = d.groupby("scenario").apply(lambda x: (x.matched_state == "H4").mean(), include_groups=False)
    reported = scenario.set_index("scenario").matched_h4_rate
    delta = float((recomputed - reported).abs().max())
    add("scenario_h4_rates_reproduced", delta < 1e-12, f"max_delta={delta}")
    add("pilot_gate_pass", json.loads((ROOT / "3_results/00_audit/R7B1C/R7B1C_pilot_gate_state.json").read_text())["status"] == "PASS", "PASS")
    add("template_freeze_pass", json.loads((ROOT / "3_results/00_audit/R7B1C/R7B1C_template_freeze_state.json").read_text())["status"] == "PASS", "PASS")

    frame = pd.DataFrame(checks)
    frame.to_csv(OUT / "R7B1C_independent_QA_checks.tsv", sep="\t", index=False)
    state = {
        "schema": "R7B1C_INDEPENDENT_QA_1.0",
        "status": "PASS" if frame["pass"].all() else "FAIL",
        "checks": len(frame), "passed": int(frame["pass"].sum()), "failed": int((~frame["pass"]).sum()),
        "failed_checks": frame.loc[~frame["pass"], "check"].tolist(),
        "combined_sha256": sha256(combined_path),
        "row_summary_sha256": sha256(AGG / "R7B1C_grid_486_summary.tsv"),
        "scenario_summary_sha256": sha256(AGG / "R7B1C_scenario_summary.tsv"),
    }
    (OUT / "R7B1C_independent_QA_state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, indent=2))
    if state["status"] != "PASS": raise SystemExit(1)


if __name__ == "__main__":
    main()
