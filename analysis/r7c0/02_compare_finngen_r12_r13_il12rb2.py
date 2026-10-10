#!/usr/bin/env python3
"""Compare official FinnGen R12/R13 PBC IL12RB2 credible sets."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011"
EXT = WORK / "external_metadata"
OUT = WORK / "results"
REGION = "chr1:65836688-68836688"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    p12 = EXT / "finngen_R12_CHIRBIL_PRIM.SUSIE.snp.filter.tsv"
    p13 = EXT / "finngen_R13_CHIRBIL_PRIM.SUSIE.snp.filter.tsv"
    r12 = pd.read_csv(p12, sep="\t")
    r13 = pd.read_csv(p13, sep="\t")
    r12 = r12[(r12["region"] == REGION) & (r12["cs"] == 1)].copy()
    r13 = r13[(r13["region"] == REGION) & (r13["cs"] == 1)].copy()
    s12, s13 = set(r12["v"]), set(r13["v"])
    common = sorted(s12 & s13)
    merged = r12.merge(r13, on="v", suffixes=("_R12", "_R13"))
    lead12 = r12.loc[r12["cs_specific_prob"].idxmax()]
    lead13 = r13.loc[r13["cs_specific_prob"].idxmax()]
    merged.to_csv(OUT / "R7C0_FinnGen_R12_R13_IL12RB2_CS_members.tsv", sep="\t", index=False)
    comparison = {
        "stage": "R7C0_G2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "phenocode": "CHIRBIL_PRIM",
        "region": REGION,
        "r12_cs_size": len(s12),
        "r13_cs_size": len(s13),
        "intersection_size": len(common),
        "union_size": len(s12 | s13),
        "jaccard": len(common) / len(s12 | s13),
        "r13_is_subset_of_r12": s13 <= s12,
        "r12_only": sorted(s12 - s13),
        "r13_only": sorted(s13 - s12),
        "shared_lead_variant": str(lead12["v"]) == str(lead13["v"]),
        "r12_lead": {"variant": str(lead12["v"]), "pip": float(lead12["cs_specific_prob"]), "beta": float(lead12["beta"]), "p": float(lead12["p"])},
        "r13_lead": {"variant": str(lead13["v"]), "pip": float(lead13["cs_specific_prob"]), "beta": float(lead13["beta"]), "p": float(lead13["p"])},
        "shared_variant_beta_direction_concordance": float((merged["beta_R12"] * merged["beta_R13"] > 0).mean()),
        "shared_variant_pip_pearson": float(merged[["cs_specific_prob_R12", "cs_specific_prob_R13"]].corr().iloc[0, 1]),
        "source_files": [
            {"path": str(p12), "sha256": sha256(p12)},
            {"path": str(p13), "sha256": sha256(p13)},
        ],
        "adjudication": "PASS_RELEASE_STABILITY_NOT_INDEPENDENT_COHORT_REPLICATION",
        "independence_boundary": (
            "R12 and R13 are longitudinal FinnGen releases. Their concordance validates signal and byte identity "
            "but must not be counted as two participant-independent disease replications."
        ),
    }
    (OUT / "R7C0_FinnGen_R12_R13_IL12RB2_signal_identity.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(comparison, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
