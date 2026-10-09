#!/usr/bin/env python3
"""Run the frozen R7B2A A0 replay and matched-input A1/A2 ABF arms."""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logsumexp


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
IDENTITY = ROOT / "3_results/00_audit/R7B2A/input_freeze/R7B2A_arm_identity_642.tsv"
MEMBERS = ROOT / "3_results/00_audit/R7B2A/input_freeze/R7B2A_variant_membership_SA_SM.tsv.gz"
FREEZE_STATE = ROOT / "3_results/00_audit/R7B2A/input_freeze/R7B2A_input_freeze_state.json"
A0_OBS = ROOT / "3_results/04_integration/R7B1/R7B1_current_PF10_ABF_all_comparisons.tsv.gz"
BRIDGE = ROOT / "3_results/01_gwas/R7B1/R7B1_PBC56_GRCh37_BIM_A1.tsv.gz"
QTL_DIR = ROOT / "3_results/03_qtl/R7B1B_v2/dualmodel_qtl"
GJ_DIR = ROOT / "1_data/study_inputs/PBC_GJOKA/R7B1B_v2"
OUT = ROOT / "3_results/04_integration/R7B2A/matched_input_abf"
P12_GRID = (1e-6, 1e-5, 1e-4)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def logdiff(a: float, b: float) -> float:
    if b >= a:
        return -np.inf
    return float(a + np.log1p(-np.exp(b - a)))


def log_abf(beta: np.ndarray, se: np.ndarray, prior_sd: float) -> np.ndarray:
    variance = np.square(np.asarray(se, dtype=np.float64))
    z = np.asarray(beta, dtype=np.float64) / np.asarray(se, dtype=np.float64)
    r = prior_sd**2 / (prior_sd**2 + variance)
    return 0.5 * (np.log1p(-r) + r * np.square(z))


def coloc_posteriors(l1: np.ndarray, l2: np.ndarray, p12: float) -> tuple[np.ndarray, np.ndarray]:
    a1 = float(logsumexp(l1))
    a2 = float(logsumexp(l2))
    a12 = float(logsumexp(l1 + l2))
    log_h = np.array([
        0.0,
        math.log(1e-4) + a1,
        math.log(1e-4) + a2,
        math.log(1e-4) + math.log(1e-4) + logdiff(a1 + a2, a12),
        math.log(p12) + a12,
    ])
    return np.exp(log_h - logsumexp(log_h)), l1 + l2


def classify(default: np.ndarray) -> str:
    h34 = float(default[3] + default[4])
    ratio = float(default[4] / h34) if h34 > 0 else np.nan
    if default[4] >= 0.80 and ratio >= 0.80:
        return "ABF_H4_DOMINANT"
    if h34 >= 0.80 and 0.20 <= ratio <= 0.80:
        return "ABF_AMBIGUOUS"
    if h34 >= 0.80 and ratio < 0.20:
        return "ABF_H3_DOMINANT"
    if h34 >= 0.80 and ratio > 0.80:
        return "ABF_H4_BORDERLINE"
    return "ABF_UNINFORMATIVE_OR_NO_TRIGGER"


def run_arm(
    comparison_id: str,
    arm: str,
    variants: list[str],
    disease_beta: np.ndarray,
    disease_se: np.ndarray,
    qtl_beta: np.ndarray,
    qtl_se: np.ndarray,
    sdy: float,
    set_hash: str,
    disease_definition: str,
    scale_definition: str,
) -> dict[str, object]:
    if len(variants) < 200:
        raise RuntimeError(f"{comparison_id}/{arm}: fewer than 200 variants")
    arrays = [disease_beta, disease_se, qtl_beta, qtl_se]
    if not all(len(x) == len(variants) and np.isfinite(x).all() for x in arrays):
        raise RuntimeError(f"{comparison_id}/{arm}: malformed arrays")
    if (disease_se <= 0).any() or (qtl_se <= 0).any() or not np.isfinite(sdy) or sdy <= 0:
        raise RuntimeError(f"{comparison_id}/{arm}: invalid SE/sdY")
    ld = log_abf(disease_beta, disease_se, 0.2)
    lq = log_abf(qtl_beta, qtl_se, 0.15 * sdy)
    posts: dict[float, np.ndarray] = {}
    ratios: dict[float, float] = {}
    signal = None
    for p12 in P12_GRID:
        posterior, combined = coloc_posteriors(ld, lq, p12)
        posts[p12] = posterior
        ratios[p12] = float(posterior[4] / (posterior[3] + posterior[4])) if posterior[3] + posterior[4] > 0 else np.nan
        if p12 == 1e-5:
            signal = combined
    default = posts[1e-5]
    weights = np.exp(signal - logsumexp(signal))
    top_i = int(np.argmax(weights))
    return {
        "comparison_id": comparison_id,
        "arm": arm,
        "n_variants": len(variants),
        "variant_set_sha256": set_hash,
        "disease_definition": disease_definition,
        "qtl_definition": "CURRENT_RELEASE_PF10_SLOPE_SE",
        "scale_definition": scale_definition,
        "sdY": sdy,
        "disease_prior_sd": 0.2,
        "qtl_prior_sd": 0.15 * sdy,
        "PP_H0": float(default[0]),
        "PP_H1": float(default[1]),
        "PP_H2": float(default[2]),
        "PP_H3": float(default[3]),
        "PP_H4": float(default[4]),
        "H3_plus_H4": float(default[3] + default[4]),
        "H4_over_H3H4": ratios[1e-5],
        "H4_p12_1e_6": float(posts[1e-6][4]),
        "H4ratio_p12_1e_6": ratios[1e-6],
        "H4_p12_1e_4": float(posts[1e-4][4]),
        "H4ratio_p12_1e_4": ratios[1e-4],
        "shared_top_variant": variants[top_i],
        "shared_top_SNP_PP_H4_conditional": float(weights[top_i]),
        "ABF_state": classify(default),
        "status": "PASS",
    }


def read_gjoka(locus: int) -> pd.DataFrame:
    frame = pd.read_csv(GJ_DIR / f"sumstats_{locus}.assoc.logistic", sep=r"\s+")
    if "TEST" in frame.columns:
        frame = frame[frame["TEST"].astype(str) == "ADD"].copy()
    for col in ["BP", "BETA", "SE", "STAT", "NMISS"]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    return frame[np.isfinite(frame["STAT"]) & np.isfinite(frame["SE"]) & (frame["SE"] > 0)].copy()


def main() -> None:
    started = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    frozen = json.loads(FREEZE_STATE.read_text(encoding="utf-8"))
    if frozen.get("gate") != "V3-G0_INPUT_LOCK_PASS":
        raise RuntimeError("V3-G0 has not passed")
    identity = pd.read_csv(IDENTITY, sep="\t", dtype={"comparison_id": str}).sort_values("comparison_id")
    members = pd.read_csv(MEMBERS, sep="\t", dtype={"comparison_id": str, "variant_id": str})
    a0_obs = pd.read_csv(A0_OBS, sep="\t", dtype={"comparison_id": str}).set_index("comparison_id")
    bridge = pd.read_csv(BRIDGE, sep="\t", dtype={"variant_id": str, "rsid": str}).set_index("variant_id")
    gj_cache = {int(locus): read_gjoka(int(locus)) for locus in identity["locus_index"].unique()}
    member_groups = {(cid, label): f.sort_values("order_zero_based")["variant_id"].astype(str).tolist()
                     for (cid, label), f in members.groupby(["comparison_id", "set"], sort=False)}
    rows: list[dict[str, object]] = []

    for n, job in enumerate(identity.itertuples(index=False), start=1):
        cid = str(job.comparison_id)
        locus = int(job.locus_index)
        s_a = member_groups[(cid, "S_A")]
        s_m = member_groups[(cid, "S_M")]
        qtl = pd.read_csv(QTL_DIR / f"{cid}_PF10_QTL.tsv.gz", sep="\t", dtype={"variant_id": str}).set_index("variant_id")
        d_gcst = bridge.loc[s_a]
        q_a = qtl.loc[s_a]
        fixed_sdy = float(job.fixed_sdY)
        native_sdy = float(job.native_SM_sdY)

        rows.append(run_arm(
            cid, "A0_REPLAY", s_a,
            d_gcst["beta_A1"].to_numpy(float), d_gcst["standard_error"].to_numpy(float),
            q_a["slope_A1"].to_numpy(float), q_a["slope_se"].to_numpy(float),
            fixed_sdy, str(job.S_A_sha256), "GCST_HARMONIZED_BETA_SE", "A0_FIXED_HISTORICAL_SDY",
        ))

        d1 = bridge.loc[s_m]
        q_m = qtl.loc[s_m]
        rows.append(run_arm(
            cid, "A1_FIXED_SDY", s_m,
            d1["beta_A1"].to_numpy(float), d1["standard_error"].to_numpy(float),
            q_m["slope_A1"].to_numpy(float), q_m["slope_se"].to_numpy(float),
            fixed_sdy, str(job.S_M_sha256), "GCST_HARMONIZED_BETA_SE", "FIXED_A0_SDY",
        ))
        rows.append(run_arm(
            cid, "A1_NATIVE_SDY", s_m,
            d1["beta_A1"].to_numpy(float), d1["standard_error"].to_numpy(float),
            q_m["slope_A1"].to_numpy(float), q_m["slope_se"].to_numpy(float),
            native_sdy, str(job.S_M_sha256), "GCST_HARMONIZED_BETA_SE", "NATIVE_SM_SDY_SENSITIVITY",
        ))

        gj = gj_cache[locus].set_index(["SNP", "BP"])
        bridge_m = bridge.loc[s_m]
        gj_rows = gj.loc[list(zip(bridge_m["rsid"].astype(str), bridge_m["position_GRCh37"].astype(int)))].copy()
        source_a1 = gj_rows["A1"].astype(str).str.upper().to_numpy()
        bim_a1 = bridge_m["BIM_A1"].astype(str).str.upper().to_numpy()
        bim_a2 = bridge_m["BIM_A2"].astype(str).str.upper().to_numpy()
        sign = np.where(source_a1 == bim_a1, 1.0, np.where(source_a1 == bim_a2, -1.0, np.nan))
        if not np.isfinite(sign).all():
            raise RuntimeError(f"{cid}: unresolved GJOKA allele during A2")
        se = gj_rows["SE"].to_numpy(float)
        stat = gj_rows["STAT"].to_numpy(float) * sign
        beta_matched = stat * se
        beta_rounded = gj_rows["BETA"].to_numpy(float) * sign
        rows.append(run_arm(
            cid, "A2_MATCHEDZ_FIXED_SDY", s_m,
            beta_matched, se, q_m["slope_A1"].to_numpy(float), q_m["slope_se"].to_numpy(float),
            fixed_sdy, str(job.S_M_sha256), "GJOKA_STAT_TIMES_SE_ALIGNED_TO_BIM_A1", "FIXED_A0_SDY",
        ))
        rows.append(run_arm(
            cid, "A2_MATCHEDZ_NATIVE_SDY", s_m,
            beta_matched, se, q_m["slope_A1"].to_numpy(float), q_m["slope_se"].to_numpy(float),
            native_sdy, str(job.S_M_sha256), "GJOKA_STAT_TIMES_SE_ALIGNED_TO_BIM_A1", "NATIVE_SM_SDY_SENSITIVITY",
        ))
        rows.append(run_arm(
            cid, "A2_ROUNDED_FIXED_SDY", s_m,
            beta_rounded, se, q_m["slope_A1"].to_numpy(float), q_m["slope_se"].to_numpy(float),
            fixed_sdy, str(job.S_M_sha256), "GJOKA_SOURCE_ROUNDED_BETA_SE_ALIGNED_TO_BIM_A1", "FIXED_A0_SDY",
        ))
        if n % 100 == 0:
            print(f"MATCHED_ABF {n}/642", flush=True)

    result = pd.DataFrame(rows).sort_values(["comparison_id", "arm"])
    if len(result) != 642 * 6 or result.duplicated(["comparison_id", "arm"]).any() or not (result["status"] == "PASS").all():
        raise RuntimeError("matched-input output is incomplete")

    # Deterministic A0 implementation check against the historical output.
    replay = result[result["arm"] == "A0_REPLAY"].set_index("comparison_id")
    numeric_map = {
        "PP_H0": "PP_H0", "PP_H1": "PP_H1", "PP_H2": "PP_H2", "PP_H3": "PP_H3", "PP_H4": "PP_H4",
        "H3_plus_H4": "H3_plus_H4", "H4_over_H3H4": "H4_over_H3H4",
        "H4_p12_1e_6": "H4_p12_1e_6", "H4ratio_p12_1e_6": "H4ratio_p12_1e_6",
        "H4_p12_1e_4": "H4_p12_1e_4", "H4ratio_p12_1e_4": "H4ratio_p12_1e_4",
        "shared_top_SNP_PP_H4_conditional": "shared_top_SNP_PP_H4_conditional",
    }
    audit_rows = []
    for new_col, old_col in numeric_map.items():
        delta = np.abs(replay[new_col].to_numpy(float) - a0_obs.loc[replay.index, old_col].to_numpy(float))
        audit_rows.append({"field": new_col, "max_abs_delta": float(np.nanmax(delta)), "mean_abs_delta": float(np.nanmean(delta))})
    audit = pd.DataFrame(audit_rows)
    top_match = replay["shared_top_variant"].astype(str).eq(a0_obs.loc[replay.index, "shared_top_variant"].astype(str))
    max_delta = float(audit["max_abs_delta"].max())
    if max_delta > 1e-10 or not top_match.all():
        raise RuntimeError(f"A0 replay mismatch: max_delta={max_delta}, top_match={int(top_match.sum())}/642")

    result_path = OUT / "R7B2A_matched_input_ABF_long.tsv.gz"
    audit_path = OUT / "R7B2A_A0_replay_numeric_audit.tsv"
    result.to_csv(result_path, sep="\t", index=False, compression="gzip")
    audit.to_csv(audit_path, sep="\t", index=False)
    state = {
        "schema": "R7B2A_MATCHED_INPUT_ABF_1.0",
        "status": "PASS",
        "gate": "V3-G1_CONTRAST_VALID_PASS__V3-G2_COVERAGE_PASS",
        "comparisons": 642,
        "arms_per_comparison": 6,
        "result_rows": len(result),
        "A0_replay_max_abs_delta": max_delta,
        "A0_shared_top_variant_match": int(top_match.sum()),
        "technical_failures": int((result["status"] != "PASS").sum()),
        "runtime_seconds": round(time.time() - started, 3),
        "arm_state_counts": {
            arm: frame["ABF_state"].value_counts().sort_index().to_dict()
            for arm, frame in result.groupby("arm")
        },
        "outputs": {
            "matched_abf_sha256": sha256(result_path),
            "A0_audit_sha256": sha256(audit_path),
        },
        "next": "R7B2A_TRAJECTORY_ADJUDICATION",
    }
    (OUT / "R7B2A_matched_input_ABF_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
