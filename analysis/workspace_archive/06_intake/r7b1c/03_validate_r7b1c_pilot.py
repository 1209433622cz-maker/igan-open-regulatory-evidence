#!/usr/bin/env python3
"""Validate the two deterministic R7B1C pilot replays and freeze full launch."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
BASE = ROOT / "3_results/05_simulation/R7B1C"
AUDIT = ROOT / "3_results/00_audit/R7B1C"
PILOT_IDS = ["R7B1C_G041", "R7B1C_G122", "R7B1C_G203", "R7B1C_G284", "R7B1C_G365", "R7B1C_G446"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []
    summary: list[dict] = []
    all_frames = []
    for gid in PILOT_IDS:
        a = BASE / "pilot_a" / f"{gid}.tsv"
        b = BASE / "pilot_b" / f"{gid}.tsv"
        exact = a.read_bytes() == b.read_bytes()
        checks.append({"check": f"deterministic_{gid}", "pass": exact, "detail": sha256(a)})
        d = pd.read_csv(a, sep="\t")
        all_frames.append(d)
        summary.append(
            {
                "grid_id": gid,
                "scenario": d["scenario"].iat[0],
                "replicates": len(d),
                "abf_h4_rate": (d["abf_state"] == "H4").mean(),
                "matched_h4_rate": (d["matched_state"] == "H4").mean(),
                "matched_h3_rate": (d["matched_state"] == "H3").mean(),
                "matched_ok_rate": d["matched_ok"].mean(),
                "matched_convergence_rate": d["matched_converged"].mean(),
                "matched_pair_rate": (d["matched_pairs"] > 0).mean(),
                "mismatch_h4_rate": (d["mismatch_state"] == "H4").mean() if d["mismatch_state"].notna().any() else float("nan"),
                "sha256": sha256(a),
            }
        )
    whole = pd.concat(all_frames, ignore_index=True)
    sm = pd.DataFrame(summary)
    sm.to_csv(AUDIT / "R7B1C_pilot_summary.tsv", sep="\t", index=False)
    checks.extend(
        [
            {"check": "pilot_rows_300", "pass": len(whole) == 300, "detail": str(len(whole))},
            {"check": "abf_complete_300", "pass": whole["abf_h4"].notna().all(), "detail": str(whole["abf_h4"].notna().sum())},
            {"check": "matched_fit_success_ge_95pct", "pass": whole["matched_ok"].mean() >= 0.95, "detail": f"{whole['matched_ok'].mean():.6f}"},
            {"check": "matched_convergence_ge_95pct", "pass": whole["matched_converged"].mean() >= 0.95, "detail": f"{whole['matched_converged'].mean():.6f}"},
            {
                "check": "S1_H4_rate_gt_S2",
                "pass": float(sm.loc[sm.scenario == "S1_one_shared", "matched_h4_rate"].iat[0])
                > float(sm.loc[sm.scenario == "S2_distinct_correlated", "matched_h4_rate"].iat[0]),
                "detail": f"S1={sm.loc[sm.scenario == 'S1_one_shared', 'matched_h4_rate'].iat[0]:.3f};S2={sm.loc[sm.scenario == 'S2_distinct_correlated', 'matched_h4_rate'].iat[0]:.3f}",
            },
            {
                "check": "template_freeze_present",
                "pass": (AUDIT / "R7B1C_template_freeze_state.json").exists(),
                "detail": sha256(AUDIT / "R7B1C_template_freeze_state.json"),
            },
        ]
    )
    check_frame = pd.DataFrame(checks)
    check_frame.to_csv(AUDIT / "R7B1C_pilot_gate_checks.tsv", sep="\t", index=False)
    state = {
        "schema": "R7B1C_PILOT_GATE_1.0",
        "status": "PASS" if check_frame["pass"].all() else "FAIL",
        "checks": len(check_frame),
        "passed": int(check_frame["pass"].sum()),
        "replicates": len(whole),
        "replays": 2,
        "pilot_summary_sha256": sha256(AUDIT / "R7B1C_pilot_summary.tsv"),
        "pilot_checks_sha256": sha256(AUDIT / "R7B1C_pilot_gate_checks.tsv"),
        "formal_grid_authorized": bool(check_frame["pass"].all()),
    }
    (AUDIT / "R7B1C_pilot_gate_state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, indent=2))
    if state["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
