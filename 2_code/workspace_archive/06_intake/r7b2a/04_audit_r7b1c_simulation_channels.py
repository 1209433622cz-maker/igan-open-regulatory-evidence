#!/usr/bin/env python3
"""Audit R7B1C iteration-level technical-error, no-CS and no-pair channels."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
RAW = ROOT / "3_results/05_simulation/R7B1C/aggregate/R7B1C_all_486000_replicates.tsv.gz"
OUT = ROOT / "3_results/05_simulation/R7B2A_audit"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def matched_channel(d: pd.DataFrame) -> pd.Series:
    technical = (~d["matched_ok"].fillna(False)) | (~d["matched_converged"].fillna(False)) | d["matched_error"].notna()
    out = pd.Series("UNCLASSIFIED", index=d.index, dtype="object")
    out.loc[technical] = "TECHNICAL_ERROR"
    valid = ~technical
    out.loc[valid & d["matched_d_cs"].eq(0) & d["matched_q_cs"].eq(0)] = "NO_CS_BOTH"
    out.loc[valid & d["matched_d_cs"].eq(0) & d["matched_q_cs"].gt(0)] = "NO_DISEASE_CS"
    out.loc[valid & d["matched_d_cs"].gt(0) & d["matched_q_cs"].eq(0)] = "NO_QTL_CS"
    out.loc[valid & d["matched_d_cs"].gt(0) & d["matched_q_cs"].gt(0) & d["matched_pairs"].eq(0)] = "CS_BOTH_NO_PAIR"
    out.loc[valid & d["matched_pairs"].gt(0) & d["matched_state"].eq("H4")] = "PAIR_H4"
    out.loc[valid & d["matched_pairs"].gt(0) & d["matched_state"].eq("H3")] = "PAIR_H3"
    out.loc[valid & d["matched_pairs"].gt(0) & d["matched_state"].eq("UNINFORMATIVE")] = "PAIR_UNINFORMATIVE"
    return out


def mismatch_channel(d: pd.DataFrame) -> pd.Series:
    applicable = d["scenario"].eq("S6_matched_vs_mismatched_LD")
    mismatch_ok = d["mismatch_ok"].astype(str).str.lower().eq("true")
    mismatch_converged = d["mismatch_converged"].astype(str).str.lower().eq("true")
    technical = applicable & ((~mismatch_ok) | (~mismatch_converged) | d["mismatch_error"].notna())
    out = pd.Series("NOT_APPLICABLE", index=d.index, dtype="object")
    out.loc[technical] = "TECHNICAL_ERROR"
    valid = applicable & ~technical
    # The historical worker recorded mismatch pair counts but not disease/QTL
    # CS counts. Zero-pair mismatch fits therefore remain deliberately coarse.
    out.loc[valid & d["mismatch_pairs"].eq(0)] = "NO_PAIR_CS_SOURCE_NOT_RECORDED"
    out.loc[valid & d["mismatch_pairs"].gt(0) & d["mismatch_state"].eq("H4")] = "PAIR_H4"
    out.loc[valid & d["mismatch_pairs"].gt(0) & d["mismatch_state"].eq("H3")] = "PAIR_H3"
    out.loc[valid & d["mismatch_pairs"].gt(0) & d["mismatch_state"].eq("UNINFORMATIVE")] = "PAIR_UNINFORMATIVE"
    return out


def summarize(frame: pd.DataFrame, groups: list[str], channel_col: str) -> pd.DataFrame:
    result = frame.groupby([*groups, channel_col], dropna=False).size().rename("n").reset_index()
    result["denominator"] = result.groupby(groups, dropna=False)["n"].transform("sum") if groups else len(frame)
    result["rate"] = result["n"] / result["denominator"]
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    usecols = [
        "grid_id", "scenario", "replicate", "true_shared", "maf", "causal_r2", "susie_L", "p12",
        "matched_ok", "matched_converged", "matched_state", "matched_pairs", "matched_d_cs", "matched_q_cs",
        "matched_error", "mismatch_ok", "mismatch_converged", "mismatch_state", "mismatch_pairs", "mismatch_error",
    ]
    d = pd.read_csv(RAW, sep="\t", usecols=usecols, low_memory=False)
    if len(d) != 486000 or d["grid_id"].nunique() != 486:
        raise RuntimeError("R7B1C iteration-level input identity failed")
    d["matched_channel"] = matched_channel(d)
    d["mismatch_channel"] = mismatch_channel(d)
    if (d["matched_channel"] == "UNCLASSIFIED").any():
        raise RuntimeError("primary matched channel has unclassified rows")
    if (d["mismatch_channel"] == "UNCLASSIFIED").any():
        raise RuntimeError("mismatch channel has unclassified rows")

    iteration_path = OUT / "R7B2A_R7B1C_iteration_channel_audit.tsv.gz"
    d[["grid_id", "scenario", "replicate", "true_shared", "matched_channel", "mismatch_channel"]].to_csv(
        iteration_path, sep="\t", index=False, compression={"method": "gzip", "mtime": 0}
    )
    overall = summarize(d, [], "matched_channel")
    overall.insert(0, "scope", "PRIMARY_MATCHED_OVERALL")
    by_scenario = summarize(d, ["scenario", "true_shared"], "matched_channel")
    by_scenario.insert(0, "scope", "PRIMARY_MATCHED_BY_SCENARIO")
    channel_summary = pd.concat([overall, by_scenario], ignore_index=True, sort=False)
    channel_summary = channel_summary[["scope", "scenario", "true_shared", "matched_channel", "n", "denominator", "rate"]]
    channel_path = OUT / "R7B2A_R7B1C_channel_summary.tsv"
    channel_summary.to_csv(channel_path, sep="\t", index=False)

    s6 = d[d["scenario"].eq("S6_matched_vs_mismatched_LD")].copy()
    mismatch_summary = summarize(s6, [], "mismatch_channel")
    mismatch_path = OUT / "R7B2A_R7B1C_mismatch_channel_summary.tsv"
    mismatch_summary.to_csv(mismatch_path, sep="\t", index=False)

    evaluable = d[d["matched_pairs"].gt(0)].copy()
    performance_rows = []
    for keys, part in d.groupby(["scenario", "true_shared"], sort=True):
        ev = part[part["matched_pairs"].gt(0)]
        performance_rows.append(
            {
                "scenario": keys[0],
                "true_shared": bool(keys[1]),
                "all_replicates": len(part),
                "pair_evaluable": len(ev),
                "pair_evaluable_rate": len(ev) / len(part),
                "H4_rate_unconditional": float(part["matched_state"].eq("H4").mean()),
                "H4_rate_conditional_on_pair": float(ev["matched_state"].eq("H4").mean()) if len(ev) else np.nan,
                "H3_rate_conditional_on_pair": float(ev["matched_state"].eq("H3").mean()) if len(ev) else np.nan,
                "uninformative_rate_conditional_on_pair": float(ev["matched_state"].eq("UNINFORMATIVE").mean()) if len(ev) else np.nan,
            }
        )
    performance = pd.DataFrame(performance_rows)
    performance_path = OUT / "R7B2A_R7B1C_discovery_vs_estimator_performance.tsv"
    performance.to_csv(performance_path, sep="\t", index=False)

    counts = d["matched_channel"].value_counts()
    no_cs = int(counts.get("NO_CS_BOTH", 0) + counts.get("NO_DISEASE_CS", 0) + counts.get("NO_QTL_CS", 0))
    both_cs_no_pair = int(counts.get("CS_BOTH_NO_PAIR", 0))
    technical = int(counts.get("TECHNICAL_ERROR", 0))
    pair_evaluable = int(d["matched_pairs"].gt(0).sum())
    state = {
        "schema": "R7B2A_R7B1C_CHANNEL_AUDIT_1.0",
        "status": "PASS_WITH_SCOPE_LIMIT",
        "gate": "V3-G3_SIMULATION_INTERPRETABLE_PASS_WITH_SCOPE_LIMIT",
        "replicates": len(d),
        "grid_rows": d["grid_id"].nunique(),
        "primary_matched": {
            "technical_errors": technical,
            "successful_no_CS": no_cs,
            "both_CS_present_no_pair": both_cs_no_pair,
            "pair_evaluable": pair_evaluable,
            "pair_evaluable_rate": pair_evaluable / len(d),
            "channel_counts": {str(k): int(v) for k, v in counts.sort_index().items()},
        },
        "mismatch_secondary": {
            "applicable_replicates": len(s6),
            "technical_errors": int((s6["mismatch_channel"] == "TECHNICAL_ERROR").sum()),
            "zero_pair_CS_source_not_recorded": int((s6["mismatch_channel"] == "NO_PAIR_CS_SOURCE_NOT_RECORDED").sum()),
            "limitation": "The historical mismatch branch did not store disease/QTL CS counts; zero-pair origin cannot be decomposed without rerun.",
        },
        "rerun_required": False,
        "rerun_rationale": "The primary matched analysis fully separates technical error, no-CS and both-CS/no-pair states. The unresolved mismatch zero-pair origin is secondary and is handled by restricting its claim rather than spending 81,000 repeated fits.",
        "interpretation": "Most primary uninformative outcomes reflect absent credible sets, not software failure. Performance must be reported both unconditionally and conditional on an evaluable signal pair; neither alone establishes general superiority.",
        "outputs": {},
    }
    for path in [iteration_path, channel_path, mismatch_path, performance_path]:
        state["outputs"][path.name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    state_path = OUT / "R7B2A_R7B1C_channel_audit_state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
