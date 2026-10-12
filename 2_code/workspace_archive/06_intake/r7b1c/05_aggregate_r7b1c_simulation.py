#!/usr/bin/env python3
"""Aggregate the complete R7B1C truth-known simulation grid."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
GRID_PATH = ROOT / "3_results/00_audit/R7B1C/R7B1C_implementation_grid_486.tsv"
RAW = ROOT / "3_results/05_simulation/R7B1C/full"
OUT = ROOT / "3_results/05_simulation/R7B1C/aggregate"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rate(series: pd.Series) -> float:
    # Equality maps missing values to False without pandas' object-downcast
    # behavior, so the aggregation remains stable across pandas releases.
    return float(series.eq(True).mean())


def summarize(frame: pd.DataFrame) -> dict:
    true_shared = bool(frame["true_shared"].iloc[0])
    rec = {
        "replicates": len(frame),
        "true_shared": true_shared,
        "abf_h4_rate": rate(frame["abf_state"] == "H4"),
        "abf_h3_rate": rate(frame["abf_state"] == "H3"),
        "abf_uninformative_rate": rate(frame["abf_state"] == "UNINFORMATIVE"),
        "matched_h4_rate": rate(frame["matched_state"] == "H4"),
        "matched_h3_rate": rate(frame["matched_state"] == "H3"),
        "matched_uninformative_rate": rate(frame["matched_state"] == "UNINFORMATIVE"),
        "matched_fit_success_rate": rate(frame["matched_ok"]),
        "matched_convergence_rate": rate(frame["matched_converged"]),
        "matched_pair_rate": rate(frame["matched_pairs"] > 0),
        "matched_d_cover_all_rate": rate(frame["matched_d_cover_all"]),
        "matched_q_cover_all_rate": rate(frame["matched_q_cover_all"]),
        "matched_d_cover_any_rate": rate(frame["matched_d_cover_any"]),
        "matched_q_cover_any_rate": rate(frame["matched_q_cover_any"]),
        "matched_mean_d_cs_size": float(frame["matched_d_cs_size"].mean()),
        "matched_mean_q_cs_size": float(frame["matched_q_cs_size"].mean()),
        "mean_abf_h4": float(frame["abf_h4"].mean()),
        "mean_matched_best_h4_all": float(frame["matched_best_h4"].fillna(0).mean()),
        "abf_to_matched_h4_rate": rate((frame["abf_state"] != "H4") & (frame["matched_state"] == "H4")),
        "abf_h4_to_matched_h3_rate": rate((frame["abf_state"] == "H4") & (frame["matched_state"] == "H3")),
        "abf_h4_to_uninformative_rate": rate((frame["abf_state"] == "H4") & (frame["matched_state"] == "UNINFORMATIVE")),
    }
    if frame["mismatch_state"].notna().any():
        rec.update(
            {
                "mismatch_h4_rate": rate(frame["mismatch_state"] == "H4"),
                "mismatch_h3_rate": rate(frame["mismatch_state"] == "H3"),
                "mismatch_fit_success_rate": rate(frame["mismatch_ok"]),
                "mismatch_convergence_rate": rate(frame["mismatch_converged"]),
                "mismatch_mean_best_h4_all": float(frame["mismatch_best_h4"].fillna(0).mean()),
                "mismatch_decision_flip_rate": rate(frame["mismatch_state"] != frame["matched_state"]),
                "mismatch_mean_abs_h4_delta": float(
                    (frame["mismatch_best_h4"].fillna(0) - frame["matched_best_h4"].fillna(0)).abs().mean()
                ),
            }
        )
    else:
        rec.update({key: float("nan") for key in [
            "mismatch_h4_rate","mismatch_h3_rate","mismatch_fit_success_rate","mismatch_convergence_rate",
            "mismatch_mean_best_h4_all","mismatch_decision_flip_rate","mismatch_mean_abs_h4_delta"]})
    rec["h4_rate_delta_matched_minus_abf"] = rec["matched_h4_rate"] - rec["abf_h4_rate"]
    rec["correct_h4_decision_rate_abf"] = rec["abf_h4_rate"] if true_shared else 1 - rec["abf_h4_rate"]
    rec["correct_h4_decision_rate_matched"] = rec["matched_h4_rate"] if true_shared else 1 - rec["matched_h4_rate"]
    return rec


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    grid = pd.read_csv(GRID_PATH, sep="\t")
    row_summaries = []
    frames = []
    combined_path = OUT / "R7B1C_all_486000_replicates.tsv.gz"
    # Fix the gzip header timestamp so byte hashes are stable across reruns.
    with combined_path.open("wb") as raw_handle:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_handle, compresslevel=9, mtime=0) as gz_handle:
            with io.TextIOWrapper(gz_handle, encoding="utf-8", newline="") as combined:
                wrote_header = False
                for job in grid.itertuples(index=False):
                    path = RAW / f"{job.grid_id}.tsv.gz"
                    if not path.exists():
                        raise FileNotFoundError(path)
                    d = pd.read_csv(path, sep="\t")
                    if len(d) != 1000 or d["grid_id"].nunique() != 1 or d["grid_id"].iat[0] != job.grid_id:
                        raise RuntimeError(f"row identity failed: {job.grid_id}")
                    d.to_csv(combined, sep="\t", index=False, header=not wrote_header, lineterminator="\n")
                    wrote_header = True
                    rec = {"grid_id": job.grid_id, "scenario": job.scenario, "maf": job.maf, "causal_r2": job.causal_r2,
                           "susie_L": job.susie_L, "p12": job.p12, **summarize(d)}
                    row_summaries.append(rec)
                    frames.append(d)
    all_data = pd.concat(frames, ignore_index=True)
    if len(all_data) != 486000:
        raise RuntimeError("combined replicate count is not 486000")
    row_summary = pd.DataFrame(row_summaries)
    row_path = OUT / "R7B1C_grid_486_summary.tsv"
    row_summary.to_csv(row_path, sep="\t", index=False)

    scenario_rows = []
    for scenario, d in all_data.groupby("scenario", sort=True):
        scenario_rows.append({"scenario": scenario, **summarize(d)})
    scenario = pd.DataFrame(scenario_rows)
    scenario_path = OUT / "R7B1C_scenario_summary.tsv"
    scenario.to_csv(scenario_path, sep="\t", index=False)

    factor_rows = []
    for keys, d in all_data.groupby(["scenario", "maf", "causal_r2", "susie_L", "p12", "template_id"], sort=True):
        factor_rows.append(dict(zip(["scenario","maf","causal_r2","susie_L","p12","template_id"], keys)) | summarize(d))
    factor = pd.DataFrame(factor_rows)
    factor_path = OUT / "R7B1C_factor_stratified_summary.tsv"
    factor.to_csv(factor_path, sep="\t", index=False)

    reclass = (
        all_data.groupby(["scenario", "abf_state", "matched_state"], dropna=False)
        .size().rename("n").reset_index()
    )
    reclass["rate_within_scenario"] = reclass["n"] / reclass.groupby("scenario")["n"].transform("sum")
    reclass_path = OUT / "R7B1C_ABF_to_multisignal_reclassification.tsv"
    reclass.to_csv(reclass_path, sep="\t", index=False)

    calibration_rows = []
    bins = np.linspace(0, 1, 11)
    truth = all_data["true_shared"].astype(int)
    for method, prediction in {
        "ABF": all_data["abf_h4"].clip(0, 1),
        "MULTISIGNAL_BEST_H4_NO_PAIR_ZERO": all_data["matched_best_h4"].fillna(0).clip(0, 1),
    }.items():
        bucket = pd.cut(prediction, bins=bins, include_lowest=True, right=True, duplicates="drop")
        for level, idx in bucket.groupby(bucket, observed=True).groups.items():
            ix = list(idx)
            calibration_rows.append({"method": method, "bin": str(level), "n": len(ix),
                                     "mean_prediction": float(prediction.iloc[ix].mean()),
                                     "observed_shared_rate": float(truth.iloc[ix].mean())})
    calibration = pd.DataFrame(calibration_rows)
    calibration_path = OUT / "R7B1C_posterior_calibration_bins.tsv"
    calibration.to_csv(calibration_path, sep="\t", index=False)
    scores = pd.DataFrame(
        [
            {"method": "ABF", "brier": float(np.mean((all_data["abf_h4"] - truth) ** 2))},
            {"method": "MULTISIGNAL_BEST_H4_NO_PAIR_ZERO", "brier": float(np.mean((all_data["matched_best_h4"].fillna(0) - truth) ** 2))},
        ]
    )
    scores_path = OUT / "R7B1C_posterior_brier_scores.tsv"
    scores.to_csv(scores_path, sep="\t", index=False)

    outputs = [combined_path,row_path,scenario_path,factor_path,reclass_path,calibration_path,scores_path]
    state = {
        "schema": "R7B1C_AGGREGATE_1.0",
        "status": "PASS",
        "replicates": len(all_data),
        "grid_rows": len(row_summary),
        "scenario_counts": all_data["scenario"].value_counts().sort_index().to_dict(),
        "matched_fit_failures": int((~all_data["matched_ok"]).sum()),
        "matched_nonconverged": int((~all_data["matched_converged"]).sum()),
        "outputs": {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in outputs},
    }
    (OUT / "R7B1C_aggregate_state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
