from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
PMC_HTML = ROOT / "9.Version/stage_workspaces/r6a1_pmc.html"
OUT_AUDIT = ROOT / "3_results/00_audit/R6A1"
OUT_RESULT = ROOT / "3_results/04_integration/R6A1"
OUT_AUDIT.mkdir(parents=True, exist_ok=True)
OUT_RESULT.mkdir(parents=True, exist_ok=True)

GWAS = {
    "combined": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis.txt",
    "european": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_European_only.txt",
    "asian": ROOT / "1_data/gwas/IgAN/Kiryluk2023/IgAN_Combined_metaanalysis_Asian_only.txt",
    "serum_iga": ROOT / "1_data/gwas/serum_IgA/Kiryluk2022/META.IGA.LEVELS.ALL.COMBINED.txt",
}
EXPECTED_COLUMNS = ["SNP", "CHR", "BP_hg19", "A1", "A2", "BETA", "SE", "P"]
MHC_CHR, MHC_START, MHC_END = 6, 25_000_000, 34_000_000


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


# The article's HTML Table 1 is the authoritative 30-independent-signal universe.
published = pd.read_html(PMC_HTML)[0].copy()
published.columns = [str(c).strip() for c in published.columns]
published = published.rename(
    columns={
        "Chr.": "chromosome",
        "Genomic location (bpa)": "position_GRCh37",
        "SNPb": "rsid",
        "Locus": "locus",
        "Risk allele": "risk_allele",
    }
)
published = published[["chromosome", "position_GRCh37", "rsid", "locus", "risk_allele"]]
published["chromosome"] = pd.to_numeric(published["chromosome"], errors="raise").astype(int)
published["position_GRCh37"] = pd.to_numeric(published["position_GRCh37"], errors="raise").astype(int)
published["risk_allele"] = published["risk_allele"].str.upper()
published["is_MHC"] = (
    (published["chromosome"] == MHC_CHR)
    & published["position_GRCh37"].between(MHC_START, MHC_END)
)
non_mhc_signals = published[~published["is_MHC"]].copy()
non_mhc_locus_leads = non_mhc_signals.drop_duplicates("locus", keep="first").copy()
target_positions = set(zip(non_mhc_signals.chromosome, non_mhc_signals.position_GRCh37))


def scan(path: Path, collect_gws: bool) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    header = path.open("rt", encoding="utf-8").readline().rstrip("\n\r").split("\t")
    if header != EXPECTED_COLUMNS:
        raise RuntimeError(f"unexpected header for {path}: {header}")
    n_rows = 0
    invalid_numeric = 0
    invalid_se = 0
    invalid_p = 0
    snp_coordinate_mismatch = 0
    exact = []
    gws = []
    for chunk in pd.read_csv(path, sep="\t", dtype=str, chunksize=750_000):
        n_rows += len(chunk)
        chrom = pd.to_numeric(chunk.CHR, errors="coerce")
        pos = pd.to_numeric(chunk.BP_hg19, errors="coerce")
        beta = pd.to_numeric(chunk.BETA, errors="coerce")
        se = pd.to_numeric(chunk.SE, errors="coerce")
        pval = pd.to_numeric(chunk.P, errors="coerce")
        valid = chrom.notna() & pos.notna() & beta.notna() & se.notna() & pval.notna()
        invalid_numeric += int((~valid).sum())
        invalid_se += int((se <= 0).fillna(False).sum())
        invalid_p += int((~pval.between(0, 1)).fillna(False).sum())
        coord = chunk.SNP == (chunk.CHR + ":" + chunk.BP_hg19)
        snp_coordinate_mismatch += int((~coord).sum())
        keys = list(zip(chrom.fillna(-1).astype(int), pos.fillna(-1).astype(int)))
        mask_exact = pd.Series([key in target_positions for key in keys], index=chunk.index)
        if mask_exact.any():
            x = chunk.loc[mask_exact].copy()
            x.insert(0, "dataset", path.name)
            exact.append(x)
        if collect_gws:
            mask = valid & (pval <= 5e-8) & ~((chrom == MHC_CHR) & pos.between(MHC_START, MHC_END))
            if mask.any():
                x = chunk.loc[mask].copy()
                x["CHR"] = chrom.loc[mask].astype(int)
                x["BP_hg19"] = pos.loc[mask].astype(int)
                x["BETA"] = beta.loc[mask]
                x["SE"] = se.loc[mask]
                x["P"] = pval.loc[mask]
                gws.append(x)
    exact_df = pd.concat(exact, ignore_index=True) if exact else pd.DataFrame(columns=["dataset"] + EXPECTED_COLUMNS)
    gws_df = pd.concat(gws, ignore_index=True) if gws else pd.DataFrame(columns=EXPECTED_COLUMNS)
    audit = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "header": header,
        "rows": n_rows,
        "invalid_numeric_rows": invalid_numeric,
        "nonpositive_SE_rows": invalid_se,
        "P_outside_0_1_rows": invalid_p,
        "SNP_vs_CHR_BP_mismatch_rows": snp_coordinate_mismatch,
        "published_non_MHC_signal_rows_found": int(len(exact_df)),
        "schema_gate": "PASS" if invalid_numeric == invalid_se == invalid_p == snp_coordinate_mismatch == 0 else "FAIL",
    }
    return audit, exact_df, gws_df


audits = {}
exact_all = []
gws_combined = pd.DataFrame()
for label, path in GWAS.items():
    print(f"SCANNING {label} {path}", flush=True)
    audit, exact, gws = scan(path, collect_gws=(label == "combined"))
    audit["dataset"] = label
    audits[label] = audit
    exact["dataset_key"] = label
    exact_all.append(exact)
    if label == "combined":
        gws_combined = gws
    print(f"DONE {label}: {audit['rows']:,} rows", flush=True)

exact_all = pd.concat(exact_all, ignore_index=True)

# Rebuild GWS clusters using a transparent 1-Mb positional clustering rule.
clusters = []
for chrom, cdf in gws_combined.sort_values(["CHR", "BP_hg19", "P"]).groupby("CHR", sort=True):
    current = []
    previous = None
    for row in cdf.sort_values("BP_hg19").itertuples(index=False):
        pos = int(row.BP_hg19)
        if previous is None or pos - previous <= 1_000_000:
            current.append(row)
        else:
            best = min(current, key=lambda z: float(z.P))
            clusters.append({"chromosome": int(chrom), "start": int(current[0].BP_hg19), "end": int(current[-1].BP_hg19), "n_gws_variants": len(current), "lead_position": int(best.BP_hg19), "lead_p": float(best.P)})
            current = [row]
        previous = pos
    if current:
        best = min(current, key=lambda z: float(z.P))
        clusters.append({"chromosome": int(chrom), "start": int(current[0].BP_hg19), "end": int(current[-1].BP_hg19), "n_gws_variants": len(current), "lead_position": int(best.BP_hg19), "lead_p": float(best.P)})
cluster_df = pd.DataFrame(clusters)

# A pure 1-Mb gap heuristic splits one distal CFH tail SNP (1:197,921,246)
# from the paper-defined CFH locus. Anchor GWS rows to the 24 published lead
# loci within 1.5 Mb and retain both counts rather than silently changing the
# heuristic until it reproduces the publication.
anchored = []
for row in gws_combined.itertuples(index=False):
    options = non_mhc_locus_leads[non_mhc_locus_leads.chromosome == int(row.CHR)].copy()
    if options.empty:
        anchored.append(None)
        continue
    options["distance"] = (options.position_GRCh37 - int(row.BP_hg19)).abs()
    best = options.sort_values(["distance", "position_GRCh37"]).iloc[0]
    anchored.append(best.locus if best.distance <= 1_500_000 else None)
gws_combined["published_locus_anchor_1p5Mb"] = anchored

lead_matrix = non_mhc_signals.copy()
for label in GWAS:
    sub = exact_all[exact_all.dataset_key == label].copy()
    if sub.duplicated(["CHR", "BP_hg19"]).any():
        raise RuntimeError(f"duplicate target coordinate rows in {label}")
    sub["key"] = list(zip(pd.to_numeric(sub.CHR).astype(int), pd.to_numeric(sub.BP_hg19).astype(int)))
    lookup = sub.set_index("key")
    for col in ["A1", "A2", "BETA", "SE", "P"]:
        lead_matrix[f"{label}_{col}"] = [lookup.at[(r.chromosome, r.position_GRCh37), col] if (r.chromosome, r.position_GRCh37) in lookup.index else np.nan for r in lead_matrix.itertuples()]

for label in GWAS:
    a1 = lead_matrix[f"{label}_A1"].astype(str).str.upper()
    a2 = lead_matrix[f"{label}_A2"].astype(str).str.upper()
    beta = pd.to_numeric(lead_matrix[f"{label}_BETA"], errors="coerce")
    aligned = np.where(a1 == lead_matrix.risk_allele, beta, np.where(a2 == lead_matrix.risk_allele, -beta, np.nan))
    lead_matrix[f"{label}_beta_risk_allele"] = aligned

lead_matrix["serum_iga_nominal"] = pd.to_numeric(lead_matrix.serum_iga_P, errors="coerce") < 0.05
lead_matrix["serum_iga_direction_concordant"] = lead_matrix.serum_iga_beta_risk_allele > 0
lead_matrix["serum_iga_nominal_concordant"] = lead_matrix.serum_iga_nominal & lead_matrix.serum_iga_direction_concordant

published_non_mhc_loci = int(non_mhc_signals.locus.nunique())
published_non_mhc_signals = int(len(non_mhc_signals))
all_exact = all(audits[k]["published_non_MHC_signal_rows_found"] == published_non_mhc_signals for k in audits)
summary = {
    "schema_version": "1.0",
    "build": "GRCh37/hg19",
    "published_signal_universe": {
        "all_independent_signals": int(len(published)),
        "HLA_independent_signals": int(published.is_MHC.sum()),
        "non_HLA_independent_signals": published_non_mhc_signals,
        "non_HLA_loci": published_non_mhc_loci,
        "note": "CFH has two independent signals, hence 25 signals across 24 non-HLA loci.",
    },
    "dataset_audits": audits,
    "combined_recalculation": {
        "non_HLA_GWS_rows": int(len(gws_combined)),
        "one_Mb_positional_clusters": int(len(cluster_df)),
        "one_Mb_heuristic_matches_published_count": int(len(cluster_df)) == published_non_mhc_loci,
        "one_Mb_heuristic_known_split": "CFH distal tail at GRCh37 1:197921246 is 1,234,328 bp from the CFH lead",
    "published_1p5Mb_anchored_loci_with_GWS": int(gws_combined.published_locus_anchor_1p5Mb.nunique()),
        "unassigned_GWS_rows_at_1p5Mb": int(gws_combined.published_locus_anchor_1p5Mb.isna().sum()),
        "published_locus_recovery_pass": int(gws_combined.published_locus_anchor_1p5Mb.nunique()) == published_non_mhc_loci and not gws_combined.published_locus_anchor_1p5Mb.isna().any(),
    },
    "serum_IgA_overlap": {
        "non_HLA_signals_tested": published_non_mhc_signals,
        "nominal_P_lt_0_05": int(lead_matrix.serum_iga_nominal.sum()),
        "nominal_and_risk_direction_concordant": int(lead_matrix.serum_iga_nominal_concordant.sum()),
    },
    "all_four_files_have_all_25_non_HLA_signal_coordinates": bool(all_exact),
    "overall_gate": "PASS" if all_exact and all(x["schema_gate"] == "PASS" for x in audits.values()) and int(gws_combined.published_locus_anchor_1p5Mb.nunique()) == published_non_mhc_loci and not gws_combined.published_locus_anchor_1p5Mb.isna().any() else "FAIL",
}

published.to_csv(OUT_RESULT / "published_30_independent_IgAN_signals.tsv", sep="\t", index=False)
non_mhc_locus_leads.to_csv(OUT_RESULT / "IgAN_24_non_HLA_locus_leads.tsv", sep="\t", index=False)
lead_matrix.to_csv(OUT_RESULT / "IgAN_25_non_HLA_signal_ancestry_serumIgA_matrix.tsv", sep="\t", index=False)
gws_combined.sort_values(["CHR", "BP_hg19"]).to_csv(OUT_RESULT / "IgAN_combined_non_HLA_GWS_variants.tsv.gz", sep="\t", index=False, compression="gzip")
cluster_df.to_csv(OUT_RESULT / "IgAN_combined_non_HLA_1Mb_clusters.tsv", sep="\t", index=False)
(OUT_AUDIT / "IgAN_GWAS_schema_loci_serumIgA_audit.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
