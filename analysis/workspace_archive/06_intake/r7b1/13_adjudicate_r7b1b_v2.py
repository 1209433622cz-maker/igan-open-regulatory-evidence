#!/usr/bin/env python3
"""Apply the pre-result-frozen R7B1B v2 bidirectional adjudication rules."""
from __future__ import annotations

import hashlib
import json
import math
import os
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
WORK = ROOT / "3_results/00_audit/R7B1B_v2/R7B1B_v2_exact_642_high_information_comparisons.tsv"
BASE = ROOT / "3_results/04_integration/R7B1B_v2/multisignal"
OUT = ROOT / "3_results/04_integration/R7B1B_v2/adjudication"
PROTOCOL = ROOT / "0_admin/protocols/R7B1B/R7B1B_v2_adjudication_freeze_2026-10-03.md"
CONFIGS = ("PF10_L5", "PF10_L10", "PF10_L20", "PF50_L10")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def config_status(frame: pd.DataFrame, config: str) -> dict[str, object]:
    if frame.empty or "config" not in frame.columns:
        return {"h4": False, "h3": False, "high_info": False, "best_h4": np.nan, "best_ratio": np.nan, "pairs": 0}
    d = frame[(frame["config"] == config) & np.isclose(frame["p12"], 1e-5)].copy()
    low = frame[(frame["config"] == config) & np.isclose(frame["p12"], 1e-6)].copy()
    if d.empty:
        return {"h4": False, "h3": False, "high_info": False, "best_h4": np.nan, "best_ratio": np.nan, "pairs": 0}
    d["pair"] = d["idx1"].astype(str) + "|" + d["idx2"].astype(str)
    low["pair"] = low["idx1"].astype(str) + "|" + low["idx2"].astype(str)
    low_ratio = low.groupby("pair")["H4_over_H3H4"].max().to_dict()
    h4_rows = d[(d["PP.H4.abf"] >= 0.80) & (d["H4_over_H3H4"] >= 0.80)].copy()
    h4 = any(float(low_ratio.get(pair, -math.inf)) >= 0.50 for pair in h4_rows["pair"])
    h3 = bool(((d["PP.H3.abf"] >= 0.80) & (d["H4_over_H3H4"] <= 0.20)).any())
    high = bool((d["H3_plus_H4"] >= 0.80).any())
    return {
        "h4": bool(h4),
        "h3": h3,
        "high_info": high,
        "best_h4": float(d["PP.H4.abf"].max()),
        "best_ratio": float(d["H4_over_H3H4"].max()),
        "pairs": int(len(d)),
    }


def abf_state(job: pd.Series) -> str:
    role = str(job["R7B1B_v2_role"])
    classification = str(job["classification"])
    if role == "BORDERLINE_HIGH_INFORMATION_CALIBRATION":
        return "ABF_H4_BORDERLINE"
    if classification == "ROBUST_H4_TRIGGER":
        return "ABF_H4_DOMINANT"
    if classification == "H3_H4_AMBIGUITY_TRIGGER":
        return "ABF_AMBIGUOUS"
    if classification == "H3_DISTINCT_SIGNAL":
        return "ABF_H3_DOMINANT"
    raise RuntimeError(f"unexpected frozen ABF class: {classification}/{role}")


def reclassification(abf: str, multi: str) -> str:
    table = {
        ("ABF_H4_DOMINANT", "H4_SUPPORTED_STABLE"): "STABLE_H4",
        ("ABF_H4_DOMINANT", "H3_SUPPORTED_STABLE"): "H4_TO_H3",
        ("ABF_H4_DOMINANT", "MODEL_SENSITIVE"): "H4_TO_MODEL_SENSITIVE",
        ("ABF_H4_DOMINANT", "UNINFORMATIVE"): "H4_TO_UNINFORMATIVE",
        ("ABF_H3_DOMINANT", "H4_SUPPORTED_STABLE"): "H3_TO_H4",
        ("ABF_H3_DOMINANT", "H3_SUPPORTED_STABLE"): "STABLE_H3",
        ("ABF_H3_DOMINANT", "MODEL_SENSITIVE"): "H3_TO_MODEL_SENSITIVE",
        ("ABF_H3_DOMINANT", "UNINFORMATIVE"): "H3_TO_UNINFORMATIVE",
        ("ABF_AMBIGUOUS", "H4_SUPPORTED_STABLE"): "AMBIGUITY_TO_H4",
        ("ABF_AMBIGUOUS", "H3_SUPPORTED_STABLE"): "AMBIGUITY_TO_H3",
        ("ABF_AMBIGUOUS", "MODEL_SENSITIVE"): "AMBIGUITY_REMAINS_MODEL_SENSITIVE",
        ("ABF_AMBIGUOUS", "UNINFORMATIVE"): "AMBIGUITY_TO_UNINFORMATIVE",
        ("ABF_H4_BORDERLINE", "H4_SUPPORTED_STABLE"): "BORDERLINE_TO_H4",
        ("ABF_H4_BORDERLINE", "H3_SUPPORTED_STABLE"): "BORDERLINE_TO_H3",
        ("ABF_H4_BORDERLINE", "MODEL_SENSITIVE"): "BORDERLINE_MODEL_SENSITIVE",
        ("ABF_H4_BORDERLINE", "UNINFORMATIVE"): "BORDERLINE_UNINFORMATIVE",
    }
    return "QC_FAILURE" if multi == "QC_FAILURE" else table[(abf, multi)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    work = pd.read_csv(WORK, sep="\t", dtype={"comparison_id": str}).sort_values("comparison_id")
    if len(work) != 642 or work["comparison_id"].duplicated().any():
        raise RuntimeError("frozen workload drift")
    rows: list[dict[str, object]] = []
    signal_frames: list[pd.DataFrame] = []
    fit_frames: list[pd.DataFrame] = []
    for job in work.to_dict("records"):
        job = pd.Series(job)
        cid = str(job["comparison_id"])
        directory = BASE / f"locus_{int(job['locus_index']):02d}"
        state_path = directory / f"{cid}_state.json"
        fit_path = directory / f"{cid}_fit_QC.tsv"
        coloc_path = directory / f"{cid}_coloc_susie.tsv.gz"
        abf = abf_state(job)
        qc_error = ""
        if not state_path.exists():
            qc_error = "MISSING_COMPARISON_STATE"
        else:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            if state.get("status") != "COMPLETE":
                qc_error = str(state.get("error", state.get("status", "NONCOMPLETE")))
        fit = pd.DataFrame()
        if not qc_error:
            if not fit_path.exists():
                qc_error = "MISSING_FIT_QC"
            else:
                fit = pd.read_csv(fit_path, sep="\t")
                if len(fit) != 4 or set(fit["config"]) != set(CONFIGS):
                    qc_error = "INCOMPLETE_CONFIG_SET"
                elif (fit["common_variants"] < 200).any():
                    qc_error = "COMMON_VARIANTS_LT_200"
                elif not (fit["disease_converged"].astype(bool) & fit["qtl_converged"].astype(bool)).all():
                    qc_error = "NONCONVERGED_FIT"
        coloc = pd.DataFrame()
        if not qc_error and coloc_path.exists() and coloc_path.stat().st_size > 0:
            try:
                coloc = pd.read_csv(coloc_path, sep="\t")
            except pd.errors.EmptyDataError:
                coloc = pd.DataFrame()
            required = {"config", "p12", "PP.H3.abf", "PP.H4.abf", "H3_plus_H4", "H4_over_H3H4", "idx1", "idx2"}
            if not coloc.empty and (not required.issubset(coloc.columns) or not np.isfinite(coloc[list(required - {"config"})].select_dtypes(include=[np.number])).all().all()):
                qc_error = "NONFINITE_OR_MALFORMED_POSTERIOR"
        if qc_error:
            multi = "QC_FAILURE"
            statuses = {cfg: {"h4": False, "h3": False, "high_info": False, "best_h4": np.nan, "best_ratio": np.nan, "pairs": 0} for cfg in CONFIGS}
        else:
            statuses = {cfg: config_status(coloc, cfg) for cfg in CONFIGS}
            pf = [statuses[cfg] for cfg in ("PF10_L5", "PF10_L10", "PF10_L20")]
            stable_h4 = statuses["PF10_L10"]["h4"] and sum(x["h4"] for x in pf) >= 2
            stable_h3 = (not stable_h4) and statuses["PF10_L10"]["h3"] and sum(x["h3"] for x in pf) >= 2
            if stable_h4:
                multi = "H4_SUPPORTED_STABLE"
            elif stable_h3:
                multi = "H3_SUPPORTED_STABLE"
            elif any(x["high_info"] or x["h4"] or x["h3"] for x in pf):
                multi = "MODEL_SENSITIVE"
            else:
                multi = "UNINFORMATIVE"
        pf50 = statuses["PF50_L10"]
        if multi == "QC_FAILURE":
            sensitivity = "NOT_COMPARABLE"
        elif multi == "H4_SUPPORTED_STABLE":
            sensitivity = "MATCH" if pf50["h4"] else ("PF50_UNINFORMATIVE" if not pf50["high_info"] else "PF10_PF50_SENSITIVE")
        elif multi == "H3_SUPPORTED_STABLE":
            sensitivity = "MATCH" if pf50["h3"] and not pf50["h4"] else ("PF50_UNINFORMATIVE" if not pf50["high_info"] else "PF10_PF50_SENSITIVE")
        else:
            sensitivity = "NOT_COMPARABLE"
        out = {
            "comparison_id": cid,
            "locus_index": int(job["locus_index"]),
            "gene": job["gene"],
            "cell_type": job["cell_type"],
            "R7B1B_v2_role": job["R7B1B_v2_role"],
            "ABF_classification": job["classification"],
            "ABF_state": abf,
            "PF10_multisignal_state": multi,
            "reclassification": reclassification(abf, multi),
            "PF10_PF50_sensitivity": sensitivity,
            "QC_error": qc_error,
            "common_variants_min": int(fit["common_variants"].min()) if not fit.empty else np.nan,
        }
        for cfg in CONFIGS:
            slug = cfg.lower()
            out[f"{slug}_h4_pass"] = statuses[cfg]["h4"]
            out[f"{slug}_h3_pass"] = statuses[cfg]["h3"]
            out[f"{slug}_high_information"] = statuses[cfg]["high_info"]
            out[f"{slug}_best_h4"] = statuses[cfg]["best_h4"]
            out[f"{slug}_best_h4_ratio"] = statuses[cfg]["best_ratio"]
            out[f"{slug}_signal_pairs"] = statuses[cfg]["pairs"]
        rows.append(out)
        if not coloc.empty:
            signal_frames.append(coloc)
        if not fit.empty:
            fit_frames.append(fit)

    final = pd.DataFrame(rows).sort_values("comparison_id")
    signals = pd.concat(signal_frames, ignore_index=True) if signal_frames else pd.DataFrame()
    fits = pd.concat(fit_frames, ignore_index=True) if fit_frames else pd.DataFrame()
    if len(final) != 642 or final["comparison_id"].duplicated().any():
        raise RuntimeError("adjudication key set is not exact 642")
    final_path = OUT / "R7B1B_v2_642_bidirectional_reclassification.tsv"
    signal_path = OUT / "R7B1B_v2_all_signal_pair_posteriors.tsv.gz"
    fit_path = OUT / "R7B1B_v2_all_fit_QC.tsv.gz"
    final.to_csv(final_path, sep="\t", index=False)
    signals.to_csv(signal_path, sep="\t", index=False, compression="gzip")
    fits.to_csv(fit_path, sep="\t", index=False, compression="gzip")
    overall = final["reclassification"].value_counts().rename_axis("reclassification").reset_index(name="n")
    by_role = final.groupby(["R7B1B_v2_role", "reclassification"]).size().rename("n").reset_index()
    sensitivity = final["PF10_PF50_sensitivity"].value_counts().rename_axis("PF10_PF50_sensitivity").reset_index(name="n")
    overall_path = OUT / "R7B1B_v2_reclassification_counts.tsv"
    role_path = OUT / "R7B1B_v2_reclassification_by_role.tsv"
    sensitivity_path = OUT / "R7B1B_v2_PF10_PF50_sensitivity_counts.tsv"
    overall.to_csv(overall_path, sep="\t", index=False)
    by_role.to_csv(role_path, sep="\t", index=False)
    sensitivity.to_csv(sensitivity_path, sep="\t", index=False)
    counts = Counter(final["reclassification"])
    state = {
        "schema": "R7B1B_V2_ADJUDICATION_1.0",
        "status": "PASS" if counts.get("QC_FAILURE", 0) == 0 else "COMPLETE_WITH_QC_FAILURES",
        "comparisons": 642,
        "primary_184": int((final["R7B1B_v2_role"] == "PRIMARY_184_TRIGGER_VERIFICATION").sum()),
        "h3_rescue_455": int((final["R7B1B_v2_role"] == "H3_RESCUE_FALSIFICATION").sum()),
        "borderline_3": int((final["R7B1B_v2_role"] == "BORDERLINE_HIGH_INFORMATION_CALIBRATION").sum()),
        "reclassification_counts": dict(sorted(counts.items())),
        "PF10_PF50_sensitivity_counts": dict(sorted(Counter(final["PF10_PF50_sensitivity"]).items())),
        "signal_pair_rows": len(signals),
        "fit_QC_rows": len(fits),
        "protocol_sha256": sha256(PROTOCOL),
        "outputs": {
            "reclassification_sha256": sha256(final_path),
            "signals_sha256": sha256(signal_path),
            "fit_QC_sha256": sha256(fit_path),
            "counts_sha256": sha256(overall_path),
            "by_role_sha256": sha256(role_path),
            "sensitivity_sha256": sha256(sensitivity_path),
        },
        "scope_ceiling": "PBC-wide ABF screening plus source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset",
        "next": "INDEPENDENT_QA_THEN_SIMULATION_CALIBRATION",
    }
    state_path = OUT / "R7B1B_v2_adjudication_state.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
