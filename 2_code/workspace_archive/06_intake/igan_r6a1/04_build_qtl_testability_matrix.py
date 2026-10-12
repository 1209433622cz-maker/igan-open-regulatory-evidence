from __future__ import annotations

import csv
import gzip
import io
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
LEADS = ROOT / "3_results/04_integration/R6A1/IgAN_24_non_HLA_locus_leads_crossbuild.tsv"
ONEK_TOP = ROOT / "1_data/qtl/OneK1K/OneK1K_TensorQTL_top_eQTL_summary.zip"
ONEK_BIM = ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim"
TENK_GENE = ROOT / "1_data/qtl/TenK10K/common_variant_gene_level_results_with_annotated_fails.zip"
TENK_SUSIE = ROOT / "1_data/qtl/TenK10K/susie_summary.zip"
GENCODE = ROOT / "1_data/reference/gene_annotation/gencode.v50.annotation.gtf.gz"
OUT_AUDIT = ROOT / "3_results/00_audit/R6A1"
OUT = ROOT / "3_results/04_integration/R6A1"
OUT_AUDIT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
WINDOW = 1_000_000


def bh(values: pd.Series) -> pd.Series:
    x = pd.to_numeric(values, errors="coerce")
    result = pd.Series(np.nan, index=x.index, dtype=float)
    valid = x.notna() & x.between(0, 1)
    p = x.loc[valid].to_numpy()
    if len(p) == 0:
        return result
    order = np.argsort(p)
    ranked = p[order]
    adjusted = ranked * len(p) / np.arange(1, len(p) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    tmp = np.empty(len(p))
    tmp[order] = np.minimum(adjusted, 1.0)
    result.loc[valid] = tmp
    return result


leads = pd.read_csv(LEADS, sep="\t")
LEAD_INDEX = {}
for build_col in ["position_GRCh37", "position_GRCh38"]:
    LEAD_INDEX[build_col] = {}
    for r in leads.itertuples(index=False):
        LEAD_INDEX[build_col].setdefault(int(r.chromosome), []).append((int(getattr(r, build_col)), str(r.locus)))


def assign_locus(chrom: int, pos: int, build_col: str) -> str | None:
    candidates = LEAD_INDEX[build_col].get(int(chrom), [])
    if not candidates:
        return None
    best_pos, best_locus = min(candidates, key=lambda x: (abs(x[0] - int(pos)), x[0]))
    return best_locus if abs(best_pos - int(pos)) <= WINDOW else None


def broad_cell(cell: str) -> str:
    if cell.startswith("B_"):
        return "B"
    if cell.startswith("CD4") or cell in {"Treg"}:
        return "CD4"
    if cell.startswith("CD8"):
        return "CD8"
    if cell in {"dnT", "gdT", "MAIT"}:
        return "other_T"
    if "Mono" in cell:
        return "Mono"
    if cell == "DC" or "DC" in cell:
        return "DC"
    if cell.startswith("NK"):
        return "NK"
    if cell in {"Plasma", "Plasmablast"}:
        return "Plasma"
    return cell


# OneK1K source-significant top eQTLs within each disease-locus window.
onek_rows = []
with zipfile.ZipFile(ONEK_TOP) as zf:
    onek_crc = zf.testzip() is None
    scientific_members = [n for n in zf.namelist() if n.endswith(".csv") and "__MACOSX" not in n and "/._" not in n]
    for member in scientific_members:
        match = re.fullmatch(r"OneK1K_(.+?)\.sig_cis_qtl_pairs\.chr(\d+)\.csv", Path(member).name)
        if not match:
            continue
        cell, chrom = match.group(1), int(match.group(2))
        df = pd.read_csv(zf.open(member), sep="\t")
        df["qval"] = pd.to_numeric(df.qval, errors="coerce")
        for row in df[df.qval < 0.05].itertuples(index=False):
            parts = str(row.variant_id).split(":")
            if len(parts) < 2:
                continue
            pos = int(parts[1])
            locus = assign_locus(chrom, pos, "position_GRCh37")
            if locus:
                onek_rows.append({
                    "locus": locus,
                    "cell_type": cell,
                    "broad_cell": broad_cell(cell),
                    "gene_symbol": str(row.phenotype_id),
                    "top_variant_GRCh37": str(row.variant_id),
                    "top_p": float(row.pval_nominal),
                    "qval": float(row.qval),
                })
onek = pd.DataFrame(onek_rows).drop_duplicates(["locus", "cell_type", "gene_symbol"])

# OneK1K public genotype regional and exact-lead coverage.
bim = pd.read_csv(ONEK_BIM, sep=r"\s+", header=None, names=["chromosome", "variant_id", "cm", "position", "A1", "A2"])
bim_rows = []
for row in leads.itertuples(index=False):
    x = bim[(bim.chromosome == row.chromosome) & bim.position.between(row.position_GRCh37 - WINDOW, row.position_GRCh37 + WINDOW)]
    exact = x[x.position == row.position_GRCh37]
    bim_rows.append({
        "locus": row.locus,
        "chromosome": row.chromosome,
        "lead_position_GRCh37": row.position_GRCh37,
        "regional_variants": len(x),
        "exact_lead_position_rows": len(exact),
        "risk_allele_in_exact_BIM_pair": bool(any(str(row.risk_allele).upper() in {str(r.A1).upper(), str(r.A2).upper()} for r in exact.itertuples())),
    })
bim_coverage = pd.DataFrame(bim_rows)

# TenK10K gene-level results: compute BH q-values within each source cell file,
# then retain source-significant genes whose source top marker is in a locus.
tenk_gene_rows = []
all_relevant_ids = set()
with zipfile.ZipFile(TENK_GENE) as zf:
    tenk_gene_crc = zf.testzip() is None
    members = [n for n in zf.namelist() if n.endswith(".tsv")]
    for member in members:
        cell = Path(member).name.replace("_all_cis_cv_gene_level_results.tsv", "")
        df = pd.read_csv(zf.open(member))
        df["ACAT_q_BH_within_cell"] = bh(df.ACAT_p)
        for row in df.itertuples(index=False):
            marker = str(row.top_MarkerID)
            parts = marker.split(":")
            if len(parts) != 4 or not parts[0].isdigit() or not parts[1].isdigit():
                continue
            chrom, pos = int(parts[0]), int(parts[1])
            locus = assign_locus(chrom, pos, "position_GRCh38")
            if locus:
                gid = str(row.gene).split(".")[0]
                all_relevant_ids.add(gid)
                tenk_gene_rows.append({
                    "locus": locus,
                    "cell_type": cell,
                    "broad_cell": broad_cell(cell),
                    "gene_ensembl": gid,
                    "top_variant_GRCh38": marker,
                    "ACAT_p": float(row.ACAT_p) if pd.notna(row.ACAT_p) else np.nan,
                    "ACAT_q_BH_within_cell": float(row.ACAT_q_BH_within_cell) if pd.notna(row.ACAT_q_BH_within_cell) else np.nan,
                    "top_p": float(row.top_pval) if pd.notna(row.top_pval) else np.nan,
                })
tenk_gene = pd.DataFrame(tenk_gene_rows)

# TenK10K source SuSiE credible sets intersecting each locus.
susie_rows = []
with zipfile.ZipFile(TENK_SUSIE) as zf:
    tenk_susie_crc = zf.testzip() is None
    for member in [n for n in zf.namelist() if n.endswith(".tsv")]:
        df = pd.read_csv(zf.open(member))
        for row in df.itertuples(index=False):
            parts = str(row.SNP).split(":")
            if len(parts) != 4 or not parts[0].isdigit() or not parts[1].isdigit():
                continue
            locus = assign_locus(int(parts[0]), int(parts[1]), "position_GRCh38")
            if locus:
                gid = str(row.gene).split(".")[0]
                all_relevant_ids.add(gid)
                susie_rows.append({
                    "locus": locus,
                    "cell_type": str(row.celltype),
                    "broad_cell": broad_cell(str(row.celltype)),
                    "gene_ensembl": gid,
                    "SNP_GRCh38": str(row.SNP),
                    "PIP": float(row.PIP),
                    "credible_set": str(row.Credible_Set),
                })
susie = pd.DataFrame(susie_rows)

# GENCODE release 50 is used only for stable ENSG-to-symbol annotation.
gene_map = {}
gene_coords = {}
attr_re = re.compile(r'(\w+) "([^"]+)"')
with gzip.open(GENCODE, "rt", encoding="utf-8") as handle:
    for line in handle:
        if line.startswith("#"):
            continue
        fields = line.rstrip("\n").split("\t")
        if len(fields) != 9 or fields[2] != "gene":
            continue
        attrs = dict(attr_re.findall(fields[8]))
        gid = attrs.get("gene_id", "").split(".")[0]
        if gid in all_relevant_ids:
            gene_map[gid] = attrs.get("gene_name", gid)
            gene_coords[gid] = {"chromosome": fields[0], "start_GRCh38": int(fields[3]), "end_GRCh38": int(fields[4]), "gene_type": attrs.get("gene_type")}

tenk_gene["gene_symbol"] = tenk_gene.gene_ensembl.map(gene_map)
if not susie.empty:
    susie["gene_symbol"] = susie.gene_ensembl.map(gene_map)

tenk_sig = tenk_gene[tenk_gene.ACAT_q_BH_within_cell < 0.05].copy()
susie_gene = susie[["locus", "cell_type", "broad_cell", "gene_ensembl", "gene_symbol"]].drop_duplicates() if not susie.empty else pd.DataFrame(columns=["locus", "cell_type", "broad_cell", "gene_ensembl", "gene_symbol"])
tenk_support = pd.concat([
    tenk_sig[["locus", "cell_type", "broad_cell", "gene_ensembl", "gene_symbol"]].assign(support="ACAT_FDR"),
    susie_gene.assign(support="SuSiE_CS"),
], ignore_index=True).dropna(subset=["gene_symbol"])
tenk_support = tenk_support.groupby(["locus", "cell_type", "broad_cell", "gene_ensembl", "gene_symbol"], as_index=False).support.agg(lambda x: "+".join(sorted(set(x))))

# Same locus, same symbol, and compatible broad immune class.
cross = onek.merge(tenk_support, on=["locus", "broad_cell", "gene_symbol"], suffixes=("_OneK1K", "_TenK10K"))
cross = cross.drop_duplicates(["locus", "broad_cell", "gene_symbol", "cell_type_OneK1K", "cell_type_TenK10K"])

# Published DICE PP4>0.5 controls from Supplementary Table 23.
controls = pd.DataFrame([
    ("REL", "NONOP2"),
    ("IRF4/DUSP22", "IRF4"), ("IRF4/DUSP22", "DUSP22"),
    ("ZMIZ1", "ZMIZ1"),
    ("IGH", "IGHV4-61"), ("IGH", "IGHV3-65"), ("IGH", "IGHV1-69"), ("IGH", "IGHV3-33-2"), ("IGH", "IGHVII-78-1"), ("IGH", "IGHV3-64"),
    ("ITGAM/ITGAX", "ITGAX"),
    ("FCAR", "NLRP7"), ("FCAR", "NCR1"),
    ("LIF/OSM", "LIF"),
], columns=["locus", "gene_symbol"])
controls["OneK1K_source_significant_recovered"] = [not onek[(onek.locus == r.locus) & (onek.gene_symbol == r.gene_symbol)].empty for r in controls.itertuples()]
controls["TenK10K_source_supported"] = [not tenk_support[(tenk_support.locus == r.locus) & (tenk_support.gene_symbol == r.gene_symbol)].empty for r in controls.itertuples()]
controls["cross_resource_compatible_cell_recovered"] = [not cross[(cross.locus == r.locus) & (cross.gene_symbol == r.gene_symbol)].empty for r in controls.itertuples()]

locus_matrix = leads[["locus", "chromosome", "position_GRCh37", "position_GRCh38", "rsid"]].copy()
locus_matrix = locus_matrix.merge(bim_coverage, on=["locus", "chromosome"], how="left")
locus_matrix["OneK1K_source_significant_cell_gene"] = locus_matrix.locus.map(onek.groupby("locus").size()).fillna(0).astype(int)
locus_matrix["OneK1K_source_significant_genes"] = locus_matrix.locus.map(onek.groupby("locus").gene_symbol.nunique()).fillna(0).astype(int)
locus_matrix["TenK10K_ACAT_FDR_cell_gene"] = locus_matrix.locus.map(tenk_sig.groupby("locus").size()).fillna(0).astype(int)
locus_matrix["TenK10K_SuSiE_gene_cell"] = locus_matrix.locus.map(susie_gene.groupby("locus").size()).fillna(0).astype(int)
locus_matrix["cross_resource_compatible_candidates"] = locus_matrix.locus.map(cross.groupby("locus").size()).fillna(0).astype(int)
locus_matrix["OneK1K_testable"] = locus_matrix.OneK1K_source_significant_cell_gene > 0
locus_matrix["TenK10K_testable"] = (locus_matrix.TenK10K_ACAT_FDR_cell_gene > 0) | (locus_matrix.TenK10K_SuSiE_gene_cell > 0)
locus_matrix["cross_resource_candidate"] = locus_matrix.cross_resource_compatible_candidates > 0

summary = {
    "schema_version": "1.0",
    "definitions": {
        "locus_window": "+/-1 Mb around published non-HLA lead in the matching build",
        "OneK1K_source_positive": "source q-value <0.05 and source top eQTL inside locus window",
        "TenK10K_source_positive": "within-cell BH FDR of gene-level ACAT P <0.05 or source SuSiE credible-set member inside locus window",
        "cross_resource_candidate": "same locus, same GENCODE symbol, compatible broad immune class; preflight candidate only, not colocalization",
    },
    "input_integrity": {
        "OneK1K_top_zip_crc": onek_crc,
        "OneK1K_scientific_members": len(scientific_members),
        "TenK10K_gene_zip_crc": tenk_gene_crc,
        "TenK10K_gene_members": len(members),
        "TenK10K_susie_zip_crc": tenk_susie_crc,
        "GENCODE_release": 50,
        "relevant_Ensembl_ids": len(all_relevant_ids),
        "mapped_Ensembl_ids": len(gene_map),
    },
    "OneK1K": {
        "source_significant_cell_gene_pairs_in_loci": len(onek),
        "source_significant_genes": int(onek.gene_symbol.nunique()),
        "testable_loci": int(locus_matrix.OneK1K_testable.sum()),
        "exact_lead_position_loci_in_public_genotype": int((locus_matrix.exact_lead_position_rows > 0).sum()),
    },
    "TenK10K": {
        "ACAT_FDR_cell_gene_pairs_in_loci": len(tenk_sig),
        "SuSiE_gene_cell_pairs_in_loci": len(susie_gene),
        "testable_loci": int(locus_matrix.TenK10K_testable.sum()),
    },
    "cross_resource": {
        "compatible_cell_gene_pairs": len(cross),
        "genes": int(cross.gene_symbol.nunique()) if not cross.empty else 0,
        "loci": int(locus_matrix.cross_resource_candidate.sum()),
    },
    "published_positive_control_screening_recovery": {
        "controls": len(controls),
        "OneK1K_source_significant": int(controls.OneK1K_source_significant_recovered.sum()),
        "TenK10K_source_supported": int(controls.TenK10K_source_supported.sum()),
        "cross_resource_compatible_cell": int(controls.cross_resource_compatible_cell_recovered.sum()),
        "claim_boundary": "screening/testability recovery only; disease-QTL shared-signal recovery is deferred to R6A2",
    },
}
summary["preflight_QTL_gate"] = "PASS" if summary["OneK1K"]["testable_loci"] >= 8 and summary["cross_resource"]["loci"] >= 4 and summary["published_positive_control_screening_recovery"]["OneK1K_source_significant"] >= 2 else "FAIL"

onek.sort_values(["locus", "gene_symbol", "cell_type"]).to_csv(OUT / "IgAN_OneK1K_source_significant_testability.tsv", sep="\t", index=False)
tenk_gene.sort_values(["locus", "gene_ensembl", "cell_type"]).to_csv(OUT / "IgAN_TenK10K_gene_level_testability.tsv.gz", sep="\t", index=False, compression="gzip")
tenk_sig.sort_values(["locus", "gene_ensembl", "cell_type"]).to_csv(OUT / "IgAN_TenK10K_ACAT_FDR_significant.tsv", sep="\t", index=False)
susie.sort_values(["locus", "gene_ensembl", "cell_type", "credible_set", "PIP"]).to_csv(OUT / "IgAN_TenK10K_SuSiE_locus_members.tsv.gz", sep="\t", index=False, compression="gzip")
tenk_support.sort_values(["locus", "gene_symbol", "cell_type"]).to_csv(OUT / "IgAN_TenK10K_source_supported_genes.tsv", sep="\t", index=False)
cross.sort_values(["locus", "gene_symbol", "broad_cell"]).to_csv(OUT / "IgAN_OneK1K_TenK10K_cross_resource_candidates.tsv", sep="\t", index=False)
controls.to_csv(OUT / "IgAN_published_positive_control_screening_recovery.tsv", sep="\t", index=False)
locus_matrix.to_csv(OUT / "IgAN_24_locus_positive_evidence_preflight_matrix.tsv", sep="\t", index=False)
(OUT_AUDIT / "IgAN_QTL_testability_positive_control_audit.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
