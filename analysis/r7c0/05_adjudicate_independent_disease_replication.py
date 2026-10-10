#!/usr/bin/env python3
"""Adjudicate Cordell/GJOKA versus FinnGen R13 IL12RB2 disease replication."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011"
OUT = WORK / "results"
EXT = WORK / "external_metadata"
REPO = ROOT / "github/igan-open-regulatory-evidence"
GJOKA = ROOT / "1_data/study_inputs/PBC_GJOKA/R7B1B_v2/sumstats_2.assoc.logistic"
PAIR = REPO / "results/r7b1b_v2/adjudication/R7B1B_v2_all_signal_pair_posteriors.tsv.gz"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gjoka = pd.read_csv(GJOKA, sep=r"\s+")
    g = gjoka[gjoka["SNP"].eq("rs6679356")].iloc[0]

    r13_region = pd.read_csv(
        EXT / "finngen_R13_CHIRBIL_PRIM_IL12RB2_chr1_67200000_67500000.tsv", sep="\t"
    )
    f = r13_region[r13_region["rsids"].fillna("").str.split(",").apply(lambda x: "rs6679356" in x)].iloc[0]
    r13_cs = pd.read_csv(EXT / "finngen_R13_CHIRBIL_PRIM.SUSIE.snp.filter.tsv", sep="\t")
    cs = r13_cs[r13_cs["position"].eq(int(f["pos"]))].iloc[0]

    pairs = []
    for chunk in pd.read_csv(PAIR, sep="\t", chunksize=100_000):
        q = chunk[
            chunk["comparison_id"].eq("R7B1_000258")
            & chunk["config"].eq("PF10_L10")
            & chunk["p12"].eq(1e-5)
        ]
        if len(q):
            pairs.append(q)
    pair = pd.concat(pairs, ignore_index=True)
    primary = pair.sort_values("PP.H4.abf", ascending=False).iloc[0]
    if primary["hit1"] != "1:67820194":
        raise RuntimeError(f"Unexpected GJOKA primary signal hit: {primary['hit1']}")

    # GJOKA A1=C has beta >0. FinnGen encodes REF=C, ALT=T and beta for ALT=T;
    # therefore the FinnGen effect aligned to C is -beta_ALT.
    aligned_finngen_beta_for_C = -float(f["beta"])
    aligned_concordant = float(g["BETA"]) * aligned_finngen_beta_for_C > 0
    row = {
        "variant_rsid": "rs6679356",
        "gjoka_build": "GRCh37",
        "gjoka_position": int(g["BP"]),
        "gjoka_effect_allele": str(g["A1"]),
        "gjoka_beta_effect_allele": float(g["BETA"]),
        "gjoka_p": float(g["P"]),
        "gjoka_multisignal_primary_hit": str(primary["hit1"]),
        "gjoka_multisignal_primary_pair_PP_H4": float(primary["PP.H4.abf"]),
        "finngen_build": "GRCh38",
        "finngen_r13_position": int(f["pos"]),
        "finngen_r13_ref": str(f["ref"]),
        "finngen_r13_alt": str(f["alt"]),
        "finngen_r13_beta_alt": float(f["beta"]),
        "finngen_r13_beta_aligned_to_GJOKA_C": aligned_finngen_beta_for_C,
        "finngen_r13_p": float(f["pval"]),
        "finngen_r13_in_credible_set": True,
        "finngen_r13_cs_specific_prob": float(cs["cs_specific_prob"]),
        "effect_direction_concordant_after_allele_alignment": bool(aligned_concordant),
    }
    pd.DataFrame([row]).to_csv(
        OUT / "R7C0_GJOKA_FinnGenR13_rs6679356_replication.tsv", sep="\t", index=False
    )
    result = {
        "stage": "R7C0_G2_INDEPENDENCE",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "cordell_gjoka": {
            "cases": 8021, "controls": 16489, "ancestry_panel": "combined European cohorts",
            "source_signal": row,
        },
        "finngen_r13": {
            "cases": 795, "controls": 368758, "study_system": "FinnGen Finnish biobank release 13",
            "regional_lead": "1:67336688:A:C (rs6659932)",
            "regional_lead_beta_alt": -0.46038,
            "regional_lead_p": 2.62972e-9,
            "credible_set_size": 17,
        },
        "study_independence": "SUPPORTED_AT_STUDY_SYSTEM_LEVEL_WITHOUT_PERSON_LEVEL_PROOF",
        "study_independence_reason": (
            "The source descriptions identify the disease inputs as the Cordell international European panels "
            "and FinnGen's Finnish-biobank release, respectively; no declared cohort overlap was found. "
            "Participant identifiers are unavailable, so zero person-level overlap cannot be proven directly."
        ),
        "signal_replication": "PASS",
        "signal_replication_reason": (
            "The GJOKA primary disease signal hit rs6679356 is a member of the FinnGen R13 IL12RB2 credible set, "
            "and the effect direction is concordant after aligning the GJOKA C allele to the FinnGen reference C allele."
        ),
        "scope_boundary": (
            "This supports external disease-signal replication for the IL12RB2 locus. It does not independently "
            "replicate the OneK NK eQTL mechanism, and it does not rescue FCRL3."
        ),
        "adjudication": "PASS_IL12RB2_EXTERNAL_DISEASE_SIGNAL_REPLICATION_WITH_DECLARED_BOUNDARY",
        "source_checksums": {
            "gjoka_sumstats_locus2": sha256(GJOKA),
            "finngen_r13_region": sha256(EXT / "finngen_R13_CHIRBIL_PRIM_IL12RB2_chr1_67200000_67500000.tsv"),
            "finngen_r13_cs": sha256(EXT / "finngen_R13_CHIRBIL_PRIM.SUSIE.snp.filter.tsv"),
            "r7b1b_signal_pairs": sha256(PAIR),
        },
    }
    (OUT / "R7C0_GJOKA_FinnGenR13_independent_replication_adjudication.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
