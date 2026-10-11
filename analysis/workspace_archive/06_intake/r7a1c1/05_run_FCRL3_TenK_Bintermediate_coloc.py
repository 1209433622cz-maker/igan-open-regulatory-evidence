#!/usr/bin/env python3
"""Run the pre-registered PBC x TenK10K B-intermediate FCRL3 ABF smoke test.

The program uses exact GRCh38 position and allele-set matching after lifting the
PBC GWAS from GRCh37.  It also extracts the publisher's TenK10K source SuSiE
credible set for FCRL3 so that the single-causal ABF result is never presented
without its multi-signal/source-fine-mapping context.
"""
from __future__ import annotations

import json
import math
import os
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from pyliftover import LiftOver
from scipy.special import logsumexp


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
GWAS = ROOT / "1_data/gwas/R7A1A/PBC/GCST90061440_buildGRCh37.tsv"
CHAIN = ROOT / "1_data/reference/liftover/hg19ToHg38.over.chain"
TENK = ROOT / "1_data/qtl/eqtl/tenk10k/derived/FCRL3_full/B_intermediate/B_intermediate_FCRL3_full_variant_eqtl.tsv"
SUSIE_ZIP = ROOT / "1_data/qtl/eqtl/tenk10k/raw/susie_summary.zip"
SUSIE_MEMBER = "susie_summary/B_intermediate_all_credible_snps.tsv"
GENE = "ENSG00000160856"
OUT = ROOT / "3_results/04_integration/R7A1C"
OUT.mkdir(parents=True, exist_ok=True)


def require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def reverse_complement(value: str) -> str:
    return str(value).upper().translate(str.maketrans("ACGT", "TGCA"))[::-1]


def logdiff(a: float, b: float) -> float:
    if b >= a:
        return -np.inf
    return a + np.log1p(-np.exp(b - a))


def sd_y(varbeta: np.ndarray, maf: np.ndarray, n: int) -> float:
    inv = 1 / np.asarray(varbeta)
    nvx = 2 * n * maf * (1 - maf)
    return math.sqrt(np.sum(inv * nvx) / np.sum(inv * inv))


def log_abf(beta: np.ndarray, se: np.ndarray, trait: str, sy: float = 1.0) -> np.ndarray:
    variance = np.asarray(se, float) ** 2
    z = np.asarray(beta, float) / np.asarray(se, float)
    prior_sd = 0.2 if trait == "cc" else 0.15 * sy
    r = prior_sd**2 / (prior_sd**2 + variance)
    return 0.5 * (np.log1p(-r) + r * z**2)


def main() -> int:
    missing = [str(path) for path in (GWAS, CHAIN, TENK, SUSIE_ZIP) if not path.exists()]
    if missing:
        raise FileNotFoundError(missing)

    qtl = pd.read_csv(TENK, sep="\t")
    qtl = qtl.rename(columns={"p.value": "p_value"})
    require_columns(
        qtl,
        {"CHR", "POS", "MarkerID", "Allele1", "Allele2", "AF_Allele2", "BETA", "SE", "p_value", "N", "gene"},
        "TenK FCRL3",
    )
    if set(qtl["gene"].astype(str)) != {GENE}:
        raise RuntimeError("selective extract contains genes outside frozen FCRL3 Ensembl ID")
    qtl = qtl[(pd.to_numeric(qtl.CHR, errors="coerce") == 1)].copy()
    qtl["POS"] = pd.to_numeric(qtl.POS, errors="raise").astype(int)
    # The downloaded object is already the exact FCRL3 ±100-kb source member;
    # retain its complete published window rather than imposing a second window.
    qtl["ref"] = qtl.Allele1.astype(str).str.upper()
    qtl["alt"] = qtl.Allele2.astype(str).str.upper()
    qtl["key38"] = "1:" + qtl.POS.astype(str) + ":" + qtl.ref + ":" + qtl.alt
    qtl = qtl.drop_duplicates("key38")

    parts: list[pd.DataFrame] = []
    for chunk in pd.read_csv(GWAS, sep="\t", dtype=str, chunksize=500_000):
        chrom = pd.to_numeric(chunk["chromosome"], errors="coerce")
        pos = pd.to_numeric(chunk["base_pair_location"], errors="coerce")
        keep = (chrom == 1) & pos.between(157_350_000, 157_950_000)
        if keep.any():
            parts.append(chunk.loc[keep].copy())
    if not parts:
        raise RuntimeError("zero PBC variants in frozen broad GRCh37 window")
    gwas = pd.concat(parts, ignore_index=True)

    lifter = LiftOver(str(CHAIN))
    rows: list[dict] = []
    for row in gwas.itertuples(index=False):
        try:
            pos37 = int(row.base_pair_location)
            effect = str(row.effect_allele).upper()
            other = str(row.other_allele).upper()
            beta = float(row.beta)
            se = float(row.standard_error)
            pvalue = float(row.p_value)
            rsid = str(row.variant_id)
        except Exception:
            continue
        hits = [x for x in lifter.convert_coordinate("chr1", pos37 - 1) if x[0] in ("chr1", "1")]
        if len(hits) != 1:
            continue
        _, pos0, strand, _ = hits[0]
        pos38 = int(pos0) + 1
        if strand == "-":
            effect, other = reverse_complement(effect), reverse_complement(other)
        for qr in qtl[qtl.POS == pos38].itertuples(index=False):
            ref, alt = str(qr.ref).upper(), str(qr.alt).upper()
            if effect == alt and other == ref:
                disease_beta_alt = beta
            elif effect == ref and other == alt:
                disease_beta_alt = -beta
            else:
                continue
            rows.append(
                {
                    "rsid": rsid,
                    "variant_id": qr.MarkerID,
                    "pos37": pos37,
                    "pos38": pos38,
                    "ref": ref,
                    "alt": alt,
                    "disease_beta_ALT": disease_beta_alt,
                    "disease_se": se,
                    "disease_p": pvalue,
                    "qtl_beta_ALT": float(qr.BETA),
                    "qtl_se": float(qr.SE),
                    "qtl_p": float(qr.p_value),
                    "qtl_af_alt": float(qr.AF_Allele2),
                    "qtl_n": int(qr.N),
                }
            )
    overlap = pd.DataFrame(rows).drop_duplicates("variant_id")
    if len(overlap) < 100:
        raise RuntimeError(f"insufficient exact allele overlap: {len(overlap)}")
    numeric = ["disease_beta_ALT", "disease_se", "qtl_beta_ALT", "qtl_se", "qtl_af_alt"]
    if not np.isfinite(overlap[numeric].to_numpy()).all():
        raise RuntimeError("non-finite ABF input")
    if not ((overlap.disease_se > 0).all() and (overlap.qtl_se > 0).all()):
        raise RuntimeError("non-positive standard error")
    if not overlap.qtl_af_alt.between(0, 1, inclusive="neither").all():
        raise RuntimeError("QTL ALT frequency outside (0,1)")

    disease_labf = log_abf(overlap.disease_beta_ALT, overlap.disease_se, "cc")
    maf = np.minimum(overlap.qtl_af_alt.to_numpy(float), 1 - overlap.qtl_af_alt.to_numpy(float))
    unique_n = sorted(set(overlap.qtl_n.astype(int)))
    if len(unique_n) != 1:
        raise RuntimeError(f"non-constant TenK sample size: {unique_n}")
    sy = sd_y(overlap.qtl_se.to_numpy(float) ** 2, maf, unique_n[0])
    qtl_labf = log_abf(overlap.qtl_beta_ALT, overlap.qtl_se, "quant", sy)
    a1, a2, a12 = logsumexp(disease_labf), logsumexp(qtl_labf), logsumexp(disease_labf + qtl_labf)

    posterior: list[dict] = []
    for p12 in (1e-6, 1e-5, 1e-4):
        logh = np.array(
            [0, np.log(1e-4) + a1, np.log(1e-4) + a2,
             np.log(1e-8) + logdiff(a1 + a2, a12), np.log(p12) + a12]
        )
        pp = np.exp(logh - logsumexp(logh))
        posterior.append(
            {"p12": p12, "n": len(overlap), "PP_H0": pp[0], "PP_H1": pp[1], "PP_H2": pp[2],
             "PP_H3": pp[3], "PP_H4": pp[4], "H4_over_H3H4": pp[4] / (pp[3] + pp[4])}
        )

    shared_weight = np.exp(disease_labf + qtl_labf - a12)
    overlap["conditional_shared_variant_weight"] = shared_weight
    top = overlap.sort_values("conditional_shared_variant_weight", ascending=False).head(25).copy()

    with zipfile.ZipFile(SUSIE_ZIP) as archive, archive.open(SUSIE_MEMBER) as handle:
        susie = pd.read_csv(handle)
    require_columns(susie, {"SNP", "PIP", "Credible_Set", "gene", "celltype"}, "TenK source SuSiE")
    susie = susie[susie.gene.astype(str) == GENE].copy()
    if susie.empty:
        raise RuntimeError("zero TenK source SuSiE rows for FCRL3")
    susie["in_exact_disease_qtl_overlap"] = susie.SNP.astype(str).isin(set(overlap.variant_id.astype(str)))
    susie["is_frozen_shared_variant"] = susie.SNP.astype(str).eq("1:157699488:C:T")

    default = next(x for x in posterior if x["p12"] == 1e-5)
    low = next(x for x in posterior if x["p12"] == 1e-6)
    if default["PP_H4"] >= 0.8 and default["H4_over_H3H4"] >= 0.8 and low["H4_over_H3H4"] >= 0.8:
        classification = "PASS_ROBUST_SINGLE_CAUSAL_ABF_SMOKE"
    elif default["H4_over_H3H4"] >= 0.8:
        classification = "HOLD_PRIOR_SENSITIVE_SINGLE_CAUSAL_ABF"
    else:
        classification = "FAIL_OR_UNINFORMATIVE_SINGLE_CAUSAL_ABF"

    overlap.to_csv(OUT / "R7A1C_FCRL3_TenK_Bintermediate_fullPBC_overlap.tsv.gz", sep="\t", index=False, compression="gzip")
    pd.DataFrame(posterior).to_csv(OUT / "R7A1C_FCRL3_TenK_Bintermediate_coloc.tsv", sep="\t", index=False)
    top.to_csv(OUT / "R7A1C_FCRL3_TenK_Bintermediate_top_shared_weights.tsv", sep="\t", index=False)
    susie.to_csv(OUT / "R7A1C_FCRL3_TenK_Bintermediate_sourceCS.tsv", sep="\t", index=False)
    result = {
        "schema_version": "CMM_R7A1C1_FCRL3_TENK_ABF_1.0",
        "status": classification,
        "gene": "FCRL3",
        "gene_id": GENE,
        "cell": "B_intermediate",
        "exact_overlap_n": len(overlap),
        "tenk_n": unique_n[0],
        "estimated_sdY": sy,
        "posterior": posterior,
        "source_cs_rows": len(susie),
        "source_cs_in_exact_overlap": int(susie.in_exact_disease_qtl_overlap.sum()),
        "frozen_shared_variant_in_source_cs": bool(susie.is_frozen_shared_variant.any()),
        "frozen_shared_variant_in_exact_overlap": "1:157699488:C:T" in set(overlap.variant_id.astype(str)),
        "interpretation_ceiling": "single-causal coloc.abf smoke; source SuSiE table reported separately",
    }
    (OUT / "R7A1C_FCRL3_TenK_Bintermediate_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
