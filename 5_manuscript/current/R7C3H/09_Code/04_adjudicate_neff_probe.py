#!/usr/bin/env python3
"""Adjudicate the frozen 33-comparison disease-N robustness probe.

The primary N=24,510 follows the source GJOKA analysis.  The case-control
effective N is evaluated only as a secondary stress test and is never used to
overwrite the frozen R7B1B results.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
WORK = ROOT / "3_results/00_audit/R7C3H0/R7C3H0_neff_probe_comparisons.tsv"
PRIMARY_BASE = ROOT / "3_results/04_integration/R7B1B_v2/multisignal"
PRIMARY_STATES = ROOT / "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv"
PROBE_BASE = ROOT / "3_results/04_integration/R7C3H0/neff_probe/multisignal"
OUT = ROOT / "3_results/04_integration/R7C3H0/neff_probe/adjudication"
CONFIGS = ("PF10_L5", "PF10_L10", "PF10_L20", "PF50_L10")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def config_status(frame: pd.DataFrame, config: str) -> dict[str, object]:
    default = frame[(frame["config"] == config) & np.isclose(frame["p12"], 1e-5)].copy()
    skeptical = frame[(frame["config"] == config) & np.isclose(frame["p12"], 1e-6)].copy()
    if default.empty:
        return {"h4": False, "h3": False, "high_info": False, "best_h4": np.nan, "best_ratio": np.nan, "pairs": 0}
    default["pair"] = default["idx1"].astype(str) + "|" + default["idx2"].astype(str)
    skeptical["pair"] = skeptical["idx1"].astype(str) + "|" + skeptical["idx2"].astype(str)
    low_ratio = skeptical.groupby("pair")["H4_over_H3H4"].max().to_dict()
    candidates = default[(default["PP.H4.abf"] >= 0.80) & (default["H4_over_H3H4"] >= 0.80)]
    h4 = any(float(low_ratio.get(pair, -math.inf)) >= 0.50 for pair in candidates["pair"])
    h3 = bool(((default["PP.H3.abf"] >= 0.80) & (default["H4_over_H3H4"] <= 0.20)).any())
    return {
        "h4": bool(h4),
        "h3": h3,
        "high_info": bool((default["H3_plus_H4"] >= 0.80).any()),
        "best_h4": float(default["PP.H4.abf"].max()),
        "best_ratio": float(default["H4_over_H3H4"].max()),
        "pairs": int(len(default)),
    }


def state_from_status(statuses: dict[str, dict[str, object]]) -> str:
    pf10 = [statuses[name] for name in ("PF10_L5", "PF10_L10", "PF10_L20")]
    stable_h4 = bool(statuses["PF10_L10"]["h4"]) and sum(bool(x["h4"]) for x in pf10) >= 2
    stable_h3 = (not stable_h4) and bool(statuses["PF10_L10"]["h3"]) and sum(bool(x["h3"]) for x in pf10) >= 2
    if stable_h4:
        return "H4_SUPPORTED_STABLE"
    if stable_h3:
        return "H3_SUPPORTED_STABLE"
    if any(bool(x["high_info"]) or bool(x["h4"]) or bool(x["h3"]) for x in pf10):
        return "MODEL_SENSITIVE"
    return "UNINFORMATIVE"


def cs_sets(path: Path) -> dict[tuple[str, str], set[str]]:
    frame = pd.read_csv(path, sep="\t")
    frame = frame[frame["trait"] == "PBC"].copy()
    return {
        (str(config), str(credible_set)): set(group["variant_id"].astype(str))
        for (config, credible_set), group in frame.groupby(["config", "credible_set"], dropna=False)
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    work = pd.read_csv(WORK, sep="\t", dtype={"comparison_id": str}).sort_values("comparison_id")
    primary = pd.read_csv(PRIMARY_STATES, sep="\t", dtype={"comparison_id": str}).set_index("comparison_id")
    if len(work) != 33 or work["comparison_id"].duplicated().any():
        raise RuntimeError("frozen probe workload drift")

    rows: list[dict[str, object]] = []
    cs_rows: list[dict[str, object]] = []
    fit_rows = 0
    qc_failures: list[str] = []
    for job in work.to_dict("records"):
        cid = str(job["comparison_id"])
        locus = int(job["locus_index"])
        directory = PROBE_BASE / f"locus_{locus:02d}"
        coloc_path = directory / f"{cid}_coloc_susie.tsv.gz"
        fit_path = directory / f"{cid}_fit_QC.tsv"
        state_path = directory / f"{cid}_state.json"
        cs_path = directory / f"{cid}_credible_set_members.tsv.gz"
        required = [coloc_path, fit_path, state_path, cs_path]
        if not all(path.is_file() for path in required):
            qc_failures.append(f"{cid}:MISSING_OUTPUT")
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        fits = pd.read_csv(fit_path, sep="\t")
        fit_rows += len(fits)
        converged = fits["disease_converged"].astype(str).str.lower().eq("true") & fits["qtl_converged"].astype(str).str.lower().eq("true")
        if state.get("status") != "COMPLETE" or len(fits) != 4 or set(fits["config"]) != set(CONFIGS) or not converged.all() or (fits["common_variants"] < 200).any():
            qc_failures.append(f"{cid}:FIT_QC")
            continue
        coloc = pd.read_csv(coloc_path, sep="\t")
        statuses = {config: config_status(coloc, config) for config in CONFIGS}
        probe_state = state_from_status(statuses)
        frozen = primary.loc[cid]
        row: dict[str, object] = {
            **job,
            "primary_state_N24510": frozen["PF10_multisignal_state"],
            "probe_state_Neff": probe_state,
            "state_identical": str(frozen["PF10_multisignal_state"]) == probe_state,
            "common_variants_min": int(fits["common_variants"].min()),
        }
        for config in CONFIGS:
            slug = config.lower()
            status = statuses[config]
            row[f"probe_{slug}_h4_pass"] = status["h4"]
            row[f"probe_{slug}_h3_pass"] = status["h3"]
            row[f"probe_{slug}_best_h4"] = status["best_h4"]
            row[f"probe_{slug}_best_h4_ratio"] = status["best_ratio"]
            row[f"probe_{slug}_signal_pairs"] = status["pairs"]
            row[f"primary_{slug}_best_h4"] = frozen[f"{slug}_best_h4"]
            row[f"delta_{slug}_best_h4"] = float(status["best_h4"]) - float(frozen[f"{slug}_best_h4"])
        rows.append(row)

        original_cs = cs_sets(PRIMARY_BASE / f"locus_{locus:02d}" / f"{cid}_credible_set_members.tsv.gz")
        probe_cs = cs_sets(cs_path)
        for key in sorted(set(original_cs) | set(probe_cs)):
            left, right = original_cs.get(key, set()), probe_cs.get(key, set())
            union = left | right
            cs_rows.append(
                {
                    "comparison_id": cid,
                    "locus_index": locus,
                    "config": key[0],
                    "credible_set": key[1],
                    "primary_members": len(left),
                    "probe_members": len(right),
                    "intersection": len(left & right),
                    "union": len(union),
                    "jaccard": len(left & right) / len(union) if union else 1.0,
                    "exact_identity": left == right,
                }
            )

    comparison = pd.DataFrame(rows).sort_values("comparison_id")
    credible_sets = pd.DataFrame(cs_rows).sort_values(["comparison_id", "config", "credible_set"])
    if len(comparison) != 33 or qc_failures or fit_rows != 132:
        raise RuntimeError(f"probe closure failure rows={len(comparison)} fits={fit_rows} failures={qc_failures}")

    comparison_path = OUT / "R7C3H0_33_neff_state_comparison.tsv"
    cs_path = OUT / "R7C3H0_disease_CS_identity.tsv"
    comparison.to_csv(comparison_path, sep="\t", index=False)
    credible_sets.to_csv(cs_path, sep="\t", index=False)
    state_changes = int((~comparison["state_identical"]).sum())
    key_axes = comparison[comparison["selection_reason"].str.contains("MANUSCRIPT_KEY_AXIS", na=False)]
    max_delta = float(comparison["delta_pf10_l10_best_h4"].abs().max())
    cs_exact = int(credible_sets["exact_identity"].sum())
    state = {
        "schema": "R7C3H0_NEFF_STRESS_ADJUDICATION_1.0",
        "status": "PASS_STABLE" if state_changes == 0 else "REVIEW_REQUIRED",
        "scientific_role": "SECONDARY_ROBUSTNESS_STRESS_TEST_NOT_PRIMARY_CORRECTION",
        "source_matched_primary_disease_N": 24510,
        "probe_case_control_effective_N": float(work["probe_disease_N"].iloc[0]),
        "comparisons": len(comparison),
        "fit_QC_rows": fit_rows,
        "comparison_state_changes": state_changes,
        "manuscript_key_axis_state_changes": int((~key_axes["state_identical"]).sum()),
        "maximum_absolute_PF10_L10_best_H4_change": max_delta,
        "disease_credible_set_rows": len(credible_sets),
        "disease_credible_set_exact_identity_rows": cs_exact,
        "disease_credible_set_minimum_jaccard": float(credible_sets["jaccard"].min()),
        "primary_interpretation": "N=24,510 is source-matched to the GJOKA SuSiE-RSS analysis; Neff is a bounded secondary robustness probe.",
        "outputs": {
            "state_comparison_sha256": sha256(comparison_path),
            "credible_set_identity_sha256": sha256(cs_path),
        },
    }
    state_path = OUT / "R7C3H0_neff_probe_state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
