#!/usr/bin/env python3
"""Build the frozen MG locus ranking from computed and published evidence.

Published 23andMe values are transcribed from Braun et al. 2024 tables and
oriented to the canonical ALT allele used in the harmonised GWAS. Qualitative
subtype-replication statements are kept separate from numeric overall-MG tests.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


BRAUN = {
    "rs2476601": {
        "overall_replication_beta_alt": math.log(1 / 1.311637),
        "overall_replication_p": 3.92e-14,
        "subtype_replication": "shared MG control; not a heterogeneity locus",
    },
    "rs7596255": {
        "overall_replication_beta_alt": "",
        "overall_replication_p": "",
        "subtype_replication": "EOMG/SOS1 signal not replicated in 23andMe",
    },
    "rs6861227": {
        "overall_replication_beta_alt": math.log(1.075955),
        "overall_replication_p": 2.07e-2,
        "subtype_replication": "EOMG/TNIP1 signal not replicated as subtype-specific",
    },
    "rs7239261": {
        "overall_replication_beta_alt": math.log(1 / 1.079214),
        "overall_replication_p": 4.43e-4,
        "subtype_replication": "LOMG discovery; 23andMe replication lacked age-at-diagnosis stratification",
    },
}

DECISION = {
    "rs7239261": (1, "PRIMARY_MECHANISTIC_PILOT", "TNFRSF11A/PIGN/ZCCHC2 bounded competition"),
    "rs6861227": (2, "SECONDARY_MOLECULAR_PILOT", "TNIP1-centered bounded competition"),
    "rs7596255": (3, "EXPLORATORY_LOW_FREQUENCY", "SOS1/DHX57/GALM/SRSF7 bounded competition"),
    "rs2476601": (4, "SHARED_EFFECT_POSITIVE_CONTROL", "PTPN22 region"),
}


def read_by_key(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return {row[key]: row for row in csv.DictReader(stream, delimiter="\t")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--known-loci", type=Path, required=True)
    parser.add_argument("--japanese-targets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    known = read_by_key(args.known_loci, "rsid")
    japanese = read_by_key(args.japanese_targets, "target_rsid")
    rows: list[dict[str, object]] = []
    for rsid, (rank, role, gene_model) in sorted(DECISION.items(), key=lambda item: item[1][0]):
        if rsid not in known:
            raise RuntimeError(f"Required locus missing from computed table: {rsid}")
        source = known[rsid]
        jp = japanese.get(rsid)
        if jp:
            jp_beta: object = jp["beta_alt"]
            jp_p: object = jp["p"]
            jp_status = "SAME_DIRECTION_PASS" if float(jp_beta) * float(source["beta_LOMG_ALT"]) > 0 else "DIRECTION_DISCORDANT"
        else:
            jp_beta = ""
            jp_p = ""
            jp_status = "NOT_PRESENT_AFTER_PUBLIC_SOURCE_FILTERS"

        if rsid == "rs7239261":
            rationale = "Exact disease replication in 23andMe overall MG and Japanese MG; historical LOMG-region support; strongest bounded mechanistic target."
        elif rsid == "rs6861227":
            rationale = "Strong EOMG discovery and molecular-QTL screen; overall MG replication is nominal, but EOMG-specific and Japanese evidence do not replicate."
        elif rsid == "rs7596255":
            rationale = "Smallest nominal heterogeneity P, but fails all-shared Bonferroni, is low frequency, and lacks independent disease replication."
        else:
            rationale = "Strong shared MG association with no EOMG-versus-LOMG difference; retain as pipeline positive control."

        rows.append(
            {
                "rank": rank,
                "role": role,
                "rsid": rsid,
                "chromosome": source["chromosome"],
                "position_GRCh38": source["position"],
                "reference_allele": source["reference_allele"],
                "alternate_allele": source["alternate_allele"],
                "candidate_gene_model": gene_model,
                "beta_EOMG_ALT": source["beta_EOMG_ALT"],
                "p_EOMG": source["p_EOMG"],
                "beta_LOMG_ALT": source["beta_LOMG_ALT"],
                "p_LOMG": source["p_LOMG"],
                "p_heterogeneity": source["p_het"],
                "p_heterogeneity_bonferroni_all_shared": source["p_het_bonferroni_all_shared"],
                "genomewide_heterogeneity_pass": source["genomewide_heterogeneity_pass"],
                "Braun_23andMe_overall_beta_ALT": BRAUN[rsid]["overall_replication_beta_alt"],
                "Braun_23andMe_overall_p": BRAUN[rsid]["overall_replication_p"],
                "Braun_subtype_replication_note": BRAUN[rsid]["subtype_replication"],
                "Japanese_beta_ALT": jp_beta,
                "Japanese_p": jp_p,
                "Japanese_replication_status": jp_status,
                "frozen_rationale": rationale,
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"rows={len(rows)} primary={rows[0]['rsid']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
