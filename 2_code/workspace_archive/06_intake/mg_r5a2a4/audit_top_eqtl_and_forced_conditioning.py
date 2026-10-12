#!/usr/bin/env python3
"""Audit source permutation evidence and condition ZCCHC2 on its nominal top SNP."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm


ROOT = Path(r"H:\SCI2\YR1")
ZIP_PATH = ROOT / "1_data/qtl/OneK1K/OneK1K_TensorQTL_top_eQTL_summary.zip"
MEMBER = "OneK1K_TensorQTL_top_eQTL_summary/OneK1K_NK_R.sig_cis_qtl_pairs.chr18.csv"
LD_DIR = ROOT / "3_results/04_integration/R5A2A4/NK_R_ZCCHC2_sourceLD"
SUSIE_DIR = ROOT / "3_results/04_integration/R5A2A4/NK_R_ZCCHC2_multisignal"
OUT_DIR = ROOT / "3_results/04_integration/R5A2A4/NK_R_ZCCHC2_multisignal"
LEAD = "18:60005046"
TOP = "18:60243208"
EXPECTED_BYTES = 16_950_155
EXPECTED_MD5 = "46e986dc53c9f4f1b6daa2b7a73d277c"


def hashes(path: Path) -> tuple[str, str]:
    md5 = hashlib.md5()
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            md5.update(block)
            sha.update(block)
    return md5.hexdigest(), sha.hexdigest()


def p_from_z(z: np.ndarray | float) -> np.ndarray | float:
    return 2 * norm.sf(np.abs(z))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    actual_md5, actual_sha256 = hashes(ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH) as archive:
        bad_member = archive.testzip()
        scientific = [
            item for item in archive.infolist()
            if not item.is_dir() and not item.filename.startswith("__MACOSX/") and "/._" not in item.filename
        ]
        if MEMBER not in archive.namelist():
            raise RuntimeError("NK_R chr18 top-eQTL member missing")
        top = pd.read_csv(io.BytesIO(archive.read(MEMBER)), sep="\t")
    target = top[top["phenotype_id"].eq("ZCCHC2")]
    if len(target) != 1:
        raise RuntimeError(f"Expected one ZCCHC2 source row, found {len(target)}")
    source = target.iloc[0]
    source_audit = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "archive_bytes": ZIP_PATH.stat().st_size,
        "expected_bytes": EXPECTED_BYTES,
        "byte_count_pass": ZIP_PATH.stat().st_size == EXPECTED_BYTES,
        "actual_md5": actual_md5,
        "expected_md5": EXPECTED_MD5,
        "md5_pass": actual_md5 == EXPECTED_MD5,
        "actual_sha256": actual_sha256,
        "zip_crc_pass": bad_member is None,
        "scientific_members": len(scientific),
        "NK_R_chr18_rows": len(top),
        "NK_R_chr18_qval_lt_0_05": int((top["qval"] < 0.05).sum()),
        "NK_R_chr18_min_qval": float(top["qval"].min()),
        "ZCCHC2": {
            key: (int(source[key]) if key in {"num_var", "ma_samples", "ma_count", "tss_distance"} else float(source[key]) if key not in {"phenotype_id", "variant_id"} else str(source[key]))
            for key in ["phenotype_id", "num_var", "variant_id", "tss_distance", "ma_samples", "ma_count", "af", "pval_nominal", "slope", "slope_se", "pval_perm", "pval_beta", "qval"]
        },
    }
    source_audit["ZCCHC2_source_significant_qval_0_05"] = bool(source["qval"] < 0.05)
    source_audit["top_eQTL_archive_gate_pass"] = all([
        source_audit["byte_count_pass"], source_audit["md5_pass"], source_audit["zip_crc_pass"], len(scientific) == 308,
    ])
    (OUT_DIR / "OneK1K_top_eQTL_NK_R_chr18_ZCCHC2_audit.json").write_text(
        json.dumps(source_audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    variants = pd.read_csv(LD_DIR / "NK_R_ZCCHC2_LD_variants.tsv", sep="\t")
    variants = variants.sort_values("LD_order_zero_based").reset_index(drop=True)
    z = variants["QTL_slope_A1"].to_numpy(float) / variants["QTL_slope_se"].to_numpy(float)
    local_threshold = 0.05 / len(variants)
    index = {variant: i for i, variant in enumerate(variants["variant_id"])}
    if LEAD not in index or TOP not in index:
        raise RuntimeError("Required anchors missing")

    matrices = {
        "RAW": "NK_R_ZCCHC2_signed_A1_correlation.npy",
        "PF10": "NK_R_ZCCHC2_PF10_residualized_A1_correlation.npy",
        "PF50": "NK_R_ZCCHC2_PF50_residualized_A1_correlation.npy",
    }
    summary_rows = []
    top_rows = []
    for label, name in matrices.items():
        correlation = np.load(LD_DIR / name).astype(np.float64)
        if correlation.shape != (len(variants), len(variants)):
            raise RuntimeError(f"{label} LD dimensions mismatch")
        condition_index = index[TOP]
        r = correlation[:, condition_index]
        denominator = np.sqrt(np.maximum(1 - r * r, 1e-12))
        z_conditional = (z - r * z[condition_index]) / denominator
        z_conditional[condition_index] = np.nan
        p_conditional = p_from_z(z_conditional)
        lead_index = index[LEAD]
        finite = np.isfinite(p_conditional)
        ordered = np.flatnonzero(finite)[np.argsort(p_conditional[finite], kind="stable")]
        for rank, j in enumerate(ordered[:25], 1):
            top_rows.append({
                "LD_mode": label,
                "rank_after_conditioning_on_18_60243208": rank,
                "variant_id": variants.loc[j, "variant_id"],
                "position_GRCh37": int(variants.loc[j, "position_GRCh37"]),
                "marginal_z": float(z[j]),
                "marginal_p": float(p_from_z(z[j])),
                "conditional_z": float(z_conditional[j]),
                "conditional_p": float(p_conditional[j]),
                "r_with_conditioning_variant": float(r[j]),
                "r_squared_with_conditioning_variant": float(r[j] ** 2),
                "is_rs7239261": variants.loc[j, "variant_id"] == LEAD,
            })
        summary_rows.append({
            "LD_mode": label,
            "variants": len(variants),
            "local_bonferroni_threshold": local_threshold,
            "marginal_top_variant": TOP,
            "marginal_top_z": float(z[condition_index]),
            "marginal_top_p": float(p_from_z(z[condition_index])),
            "marginal_signals_passing_local_bonferroni": int((p_from_z(z) <= local_threshold).sum()),
            "rs7239261_marginal_z": float(z[lead_index]),
            "rs7239261_marginal_p": float(p_from_z(z[lead_index])),
            "lead_to_top_signed_r": float(correlation[lead_index, condition_index]),
            "lead_to_top_r_squared": float(correlation[lead_index, condition_index] ** 2),
            "rs7239261_conditional_z": float(z_conditional[lead_index]),
            "rs7239261_conditional_p": float(p_conditional[lead_index]),
            "best_residual_variant": variants.loc[ordered[0], "variant_id"],
            "best_residual_p": float(p_conditional[ordered[0]]),
            "residual_signals_passing_local_bonferroni": int((p_conditional[finite] <= local_threshold).sum()),
        })

    summary = pd.DataFrame(summary_rows)
    top_table = pd.DataFrame(top_rows)
    summary_path = OUT_DIR / "NK_R_ZCCHC2_forced_conditioning_summary.tsv"
    top_path = OUT_DIR / "NK_R_ZCCHC2_forced_conditioned_top25.tsv"
    summary.to_csv(summary_path, sep="\t", index=False, lineterminator="\n")
    top_table.to_csv(top_path, sep="\t", index=False, lineterminator="\n")

    susie = json.loads((SUSIE_DIR / "NK_R_ZCCHC2_susie_audit.json").read_text(encoding="utf-8"))
    primary = susie["primary"]
    adjudication = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_permutation": source_audit,
        "LD_modes": summary_rows,
        "SuSiE_primary": primary,
        "SuSiE_multisignal_support_pass": bool(susie["multisignal_support_pass"]),
        "frozen_questions": {
            "ZCCHC2_has_source_significant_eQTL": bool(source["qval"] < 0.05),
            "any_marginal_variant_passes_within_gene_bonferroni": bool((p_from_z(z) <= local_threshold).any()),
            "any_SuSiE_95pct_credible_set": bool(susie["adjudication_checks"]["any_sensitivity_has_95pct_credible_set"]),
            "rs7239261_in_credible_signal": bool(primary["rs7239261_PIP"] >= 0.1 and primary["credible_sets_95"] > 0),
            "rs7239261_residual_signal_after_top_conditioning": bool((summary["rs7239261_conditional_p"] <= local_threshold).any()),
        },
    }
    adjudication["R5A2A4_decision"] = (
        "GO_SIGNAL_SPECIFIC_COLOC_AND_TENK10K"
        if all(adjudication["frozen_questions"].values())
        else "FAIL_CHR18_ONEK1K_PBMC_EXPRESSION_MEDIATION"
    )
    adjudication["next_stage"] = (
        "CHR18_SIGNAL_SPECIFIC_COLOC"
        if adjudication["R5A2A4_decision"].startswith("GO_")
        else "R5A2B_CHR5_TNIP1_BOUNDED_PILOT"
    )
    path = OUT_DIR / "NK_R_ZCCHC2_multisignal_adjudication.json"
    path.write_text(json.dumps(adjudication, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(adjudication, indent=2, ensure_ascii=False))
    return 0 if source_audit["top_eQTL_archive_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
