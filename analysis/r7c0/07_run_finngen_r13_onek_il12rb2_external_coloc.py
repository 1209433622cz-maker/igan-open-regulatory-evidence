#!/usr/bin/env python3
"""Run the frozen FinnGen R13 PBC x OneK NK/IL12RB2 external coloc.

Builds are bridged by rsID through the verified GJOKA locus-2 table.  The
analysis is a single-causal ABF validation plus exact source-CS membership
audit; it is not presented as a second source-LD multi-signal fit.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logsumexp


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011"
EXT = WORK / "external_metadata"
OUT = WORK / "results"
QTL = ROOT / "3_results/03_qtl/R7B0/pf50_targeted/IL12RB2_NK_PF10.tsv.gz"
GJOKA = ROOT / "1_data/study_inputs/PBC_GJOKA/R7B1B_v2/sumstats_2.assoc.logistic"
ONEK_CS = ROOT / "3_results/04_integration/R7B1B_v2/multisignal/locus_02/R7B1_000258_credible_set_members.tsv.gz"
R13 = EXT / "finngen_R13_CHIRBIL_PRIM_IL12RB2_chr1_66307873_68398724.tsv"
R13_CS = EXT / "finngen_R13_CHIRBIL_PRIM.SUSIE.snp.filter.tsv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def logdiff(a: float, b: float) -> float:
    if b >= a:
        return -np.inf
    return a + np.log1p(-np.exp(b - a))


def labf(beta: pd.Series, se: pd.Series, prior_sd: float) -> np.ndarray:
    variance = np.asarray(se, dtype=float) ** 2
    z = np.asarray(beta, dtype=float) / np.asarray(se, dtype=float)
    r = prior_sd**2 / (prior_sd**2 + variance)
    return 0.5 * (np.log1p(-r) + r * z * z)


def coloc(l1: np.ndarray, l2: np.ndarray, p12: float) -> tuple[np.ndarray, np.ndarray]:
    a1, a2, a12 = logsumexp(l1), logsumexp(l2), logsumexp(l1 + l2)
    log_h = np.array([
        0.0,
        math.log(1e-4) + a1,
        math.log(1e-4) + a2,
        math.log(1e-4) + math.log(1e-4) + logdiff(a1 + a2, a12),
        math.log(p12) + a12,
    ])
    return np.exp(log_h - logsumexp(log_h)), l1 + l2


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    qtl = pd.read_csv(QTL, sep="\t")
    bridge = pd.read_csv(GJOKA, sep=r"\s+")[["BP", "SNP"]].drop_duplicates("BP")
    disease = pd.read_csv(R13, sep="\t")
    disease = disease.assign(SNP=disease["rsids"].fillna("").str.split(",")).explode("SNP")
    merged = (
        qtl.merge(bridge, left_on="position_GRCh37", right_on="BP", how="inner")
        .merge(disease[["SNP", "pos", "ref", "alt", "pval", "beta", "sebeta", "af_alt"]], on="SNP", how="inner")
        .drop_duplicates(["variant_id", "pos"])
    )
    valid = (
        np.isfinite(merged["slope_A1"]) & np.isfinite(merged["slope_se"]) & (merged["slope_se"] > 0)
        & np.isfinite(merged["beta"]) & np.isfinite(merged["sebeta"]) & (merged["sebeta"] > 0)
    )
    merged = merged.loc[valid].copy()
    if len(merged) < 1000:
        raise RuntimeError(f"Insufficient harmonized coverage: {len(merged)}")

    maf = np.minimum(merged["af_A1"].to_numpy(float), 1 - merged["af_A1"].to_numpy(float))
    vbeta = merged["slope_se"].to_numpy(float) ** 2
    inv = 1 / vbeta
    nvx = 2 * int(merged["n_expression_donors"].iloc[0]) * maf * (1 - maf)
    sdy = math.sqrt(np.sum(inv * nvx) / np.sum(inv * inv))
    disease_labf = labf(merged["beta"], merged["sebeta"], 0.2)
    qtl_labf = labf(merged["slope_A1"], merged["slope_se"], 0.15 * sdy)

    posterior_rows = []
    shared = None
    for p12 in [1e-6, 1e-5, 1e-4]:
        pp, joint = coloc(disease_labf, qtl_labf, p12)
        ratio = pp[4] / (pp[3] + pp[4])
        posterior_rows.append({
            "p12": p12, "n_variants": len(merged), "PP_H0": pp[0], "PP_H1": pp[1],
            "PP_H2": pp[2], "PP_H3": pp[3], "PP_H4": pp[4], "H4_over_H3H4": ratio,
        })
        if p12 == 1e-5:
            snp_prob = np.exp(joint - logsumexp(joint))
            idx = int(np.argmax(snp_prob))
            row = merged.iloc[idx]
            shared = {
                "rsid": row["SNP"], "onek_GRCh37_variant": row["variant_id"],
                "finngen_GRCh38_variant": f"1:{int(row['pos'])}:{row['ref']}:{row['alt']}",
                "conditional_shared_variant_probability": float(snp_prob[idx]),
                "onek_A1": row["A1_effect_allele"], "onek_A2": row["A2_other_allele"],
                "onek_beta_A1": float(row["slope_A1"]),
                "finngen_ref": row["ref"], "finngen_alt": row["alt"],
                "finngen_beta_alt": float(row["beta"]), "finngen_p": float(row["pval"]),
                "aligned_direction": "CONCORDANT" if row["A1_effect_allele"] == row["ref"] and float(row["slope_A1"]) * -float(row["beta"]) > 0 else "CHECK_COMPLEMENT_OR_OTHER",
            }
    posterior = pd.DataFrame(posterior_rows)
    posterior.to_csv(OUT / "R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv", sep="\t", index=False)

    onek_cs = pd.read_csv(ONEK_CS, sep="\t")
    onek_cs = onek_cs[
        onek_cs["config"].eq("PF10_L10")
        & onek_cs["trait"].eq("OneK_QTL")
        & onek_cs["credible_set"].eq("L1")
    ].copy()
    onek_cs["position_GRCh37"] = onek_cs["variant_id"].str.split(":").str[1].astype(int)
    r13_cs = pd.read_csv(R13_CS, sep="\t")
    r13_cs = r13_cs[(r13_cs["region"].eq("chr1:65836688-68836688")) & r13_cs["cs"].eq(1)].copy()
    r13_cs = r13_cs.merge(
        disease[["pos", "SNP"]].drop_duplicates("pos"), left_on="position", right_on="pos", how="left"
    )
    cs_overlap = (
        onek_cs.merge(bridge, left_on="position_GRCh37", right_on="BP", how="left")
        .merge(r13_cs[["SNP", "v", "cs_specific_prob", "beta", "p"]], on="SNP", how="left")
    )
    cs_overlap["in_finngen_r13_disease_cs"] = cs_overlap["v"].notna()
    cs_overlap.to_csv(OUT / "R7C0_OneK_NK_IL12RB2_CS_in_FinnGenR13_disease_CS.tsv", sep="\t", index=False)

    default = posterior[posterior["p12"].eq(1e-5)].iloc[0]
    low = posterior[posterior["p12"].eq(1e-6)].iloc[0]
    robust = bool(default["PP_H4"] >= 0.8 and default["H4_over_H3H4"] >= 0.8 and low["H4_over_H3H4"] >= 0.5)
    cs_pass = bool(cs_overlap["in_finngen_r13_disease_cs"].all())
    result = {
        "stage": "R7C0_G2_EXTERNAL_COLOC",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "comparison": "FinnGen R13 CHIRBIL_PRIM x OneK NK IL12RB2",
        "harmonization": "GRCh37 OneK positions -> GJOKA rsID bridge -> FinnGen R13 GRCh38 rsID",
        "n_variants": len(merged),
        "onek_input_variants": len(qtl),
        "harmonized_fraction_of_onek_input": len(merged) / len(qtl),
        "qtl_N": int(merged["n_expression_donors"].iloc[0]),
        "estimated_sdY": sdy,
        "default_PP_H4": float(default["PP_H4"]),
        "default_H4_over_H3H4": float(default["H4_over_H3H4"]),
        "low_prior_PP_H4": float(low["PP_H4"]),
        "low_prior_H4_over_H3H4": float(low["H4_over_H3H4"]),
        "robust_single_causal_gate": robust,
        "shared_top_variant": shared,
        "onek_primary_qtl_cs_members": len(cs_overlap),
        "onek_primary_qtl_cs_members_in_finngen_r13_disease_cs": int(cs_overlap["in_finngen_r13_disease_cs"].sum()),
        "onek_primary_qtl_cs_pip_mass_in_finngen_r13_disease_cs": float(cs_overlap.loc[cs_overlap["in_finngen_r13_disease_cs"], "PIP"].sum()),
        "source_cs_identity_gate": cs_pass,
        "adjudication": "PASS_INDEPENDENT_DISEASE_X_ONEK_MOLECULAR_SIGNAL" if robust and cs_pass else "HOLD",
        "allowed_claim": (
            "The OneK NK/IL12RB2 molecular signal shares the FinnGen R13 PBC signal under the frozen ABF gate, "
            "and both variants in the OneK primary QTL credible set are members of the FinnGen R13 disease credible set."
        ),
        "boundary": (
            "This is a single-causal, rsID-harmonized external validation. It does not replace the original GJOKA "
            "source-LD multi-signal fit and does not establish chromatin-to-expression mediation."
        ),
        "source_checksums": {
            "onek_qtl": sha256(QTL), "gjoka_rsid_bridge": sha256(GJOKA),
            "onek_source_cs": sha256(ONEK_CS), "finngen_r13_fullwindow": sha256(R13),
            "finngen_r13_source_cs": sha256(R13_CS),
        },
    }
    (OUT / "R7C0_FinnGenR13_x_OneK_IL12RB2_external_coloc_state.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
