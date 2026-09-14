#!/usr/bin/env python3
"""Compare frozen OneK1K REEP3 CS with public TenK10K source CS across builds."""
from pathlib import Path
import hashlib
import json
import math
import os

import pandas as pd
from pyliftover import LiftOver

ROOT = Path(os.environ.get("IGAN_PROJECT_ROOT", Path.cwd()))
OUT = ROOT / "3_results/04_integration/R6A2D"
CHAIN = ROOT / "1_data/reference/liftover/hg19ToHg38.over.chain.gz"
ONEK_CS = ROOT / "3_results/04_integration/R6A2C/multisignal/R6A2C_susie_credible_sets.tsv"
ONEK_VARIANTS = ROOT / "3_results/04_integration/R6A2C/sourceLD/REEP3_REEP3_CD4_NC/LD_variants.tsv"
TENK_CS = OUT / "R6A2D_TenK_REEP3_source_credible_members.tsv"
PRECOMPUTED = ROOT / "1_data/qtl/TenK10K/R6A2D_REEP3_precomputed_coloc"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def parse_tenk(value: str):
    fields = str(value).replace("chr", "", 1).split(":")
    if len(fields) < 4:
        raise ValueError(value)
    return fields[0], int(fields[1]), fields[2].upper(), fields[3].upper()


lo = LiftOver(str(CHAIN))
cs = pd.read_csv(ONEK_CS, sep="\t")
cs = cs[(cs["config"] == "PF10_L10") & (cs["credible_set"] == "L1")].copy()
variants = pd.read_csv(ONEK_VARIANTS, sep="\t", dtype={"variant_id": str, "A1": str, "A2": str})
cs = cs.merge(variants[["variant_id", "position_GRCh37", "A1", "A2"]], on="variant_id", how="left", validate="one_to_one")

mapped = []
for row in cs.itertuples(index=False):
    hits = lo.convert_coordinate("chr10", int(row.position_GRCh37) - 1)
    assembled = [x for x in hits if x[0] == "chr10"]
    if len(assembled) == 1 and assembled[0][2] == "+":
        pos38 = int(assembled[0][1]) + 1
        status = "UNIQUE_PLUS"
    else:
        pos38 = None
        status = f"NONUNIQUE_OR_STRAND_{len(assembled)}"
    mapped.append({
        "variant_id_GRCh37": row.variant_id,
        "position_GRCh37": int(row.position_GRCh37),
        "A1": row.A1,
        "A2": row.A2,
        "position_GRCh38": pos38,
        "liftover_status": status,
        "OneK_alpha": float(row.alpha),
        "OneK_PIP": float(row.PIP),
        "is_smoke_shared_top": bool(row.is_smoke_shared_top),
    })
mapped = pd.DataFrame(mapped)

tenk = pd.read_csv(TENK_CS, sep="\t")
tenk_parsed = tenk["SNP"].map(parse_tenk)
tenk[["chromosome", "position_GRCh38", "REF", "ALT"]] = pd.DataFrame(tenk_parsed.tolist(), index=tenk.index)
tenk["allele_set"] = tenk.apply(lambda r: "/".join(sorted([r.REF, r.ALT])), axis=1)
mapped["allele_set"] = mapped.apply(lambda r: "/".join(sorted([str(r.A1).upper(), str(r.A2).upper()])), axis=1)

exact_rows = []
for row in mapped.itertuples(index=False):
    hit = tenk[(tenk.position_GRCh38 == row.position_GRCh38) & (tenk.allele_set == row.allele_set)]
    exact_rows.append({
        "variant_id_GRCh37": row.variant_id_GRCh37,
        "position_GRCh38": row.position_GRCh38,
        "allele_set": row.allele_set,
        "TenK_exact_source_CS_cells": ",".join(sorted(hit.cell_type.unique())) if len(hit) else "",
        "TenK_exact_source_CS_member_count": int(len(hit)),
        "TenK_max_PIP": None if hit.empty else float(hit.PIP.max()),
    })
exact = pd.DataFrame(exact_rows)
mapped = mapped.merge(exact, on=["variant_id_GRCh37", "position_GRCh38", "allele_set"], how="left")
mapped.to_csv(OUT / "R6A2D_OneK_CS_GRCh37_to_GRCh38_exact_TenK_overlap.tsv", sep="\t", index=False)

pre_rows = []
for cell in ["CD4_Naive", "CD4_TCM", "Treg"]:
    path = PRECOMPUTED / f"{cell}_chr10.csv"
    frame = pd.read_csv(path)
    row = frame[frame["gene"] == "ENSG00000165476"]
    if len(row) != 1:
        raise RuntimeError(f"{cell}: expected one REEP3 row, got {len(row)}")
    pre_rows.append(row.iloc[0].to_dict())
pre = pd.DataFrame(pre_rows)
pre.to_csv(OUT / "R6A2D_TenK_author_precomputed_IgAN_REEP3_coloc.tsv", sep="\t", index=False)

cell_summary = []
onek_positions = mapped.position_GRCh38.dropna().astype(int)
for cell in ["CD4_Naive", "CD4_TCM", "Treg"]:
    t = tenk[tenk.cell_type == cell]
    p = pre[pre.celltype == cell].iloc[0]
    distances = [abs(int(x) - int(y)) for x in onek_positions for y in t.position_GRCh38] if len(t) else []
    cell_summary.append({
        "cell_type": cell,
        "gene_level_ACAT_p": float(pd.read_csv(OUT / "R6A2D_TenK_REEP3_gene_level.tsv", sep="\t").query("cell_type == @cell").iloc[0].ACAT_p),
        "source_CS_count": int(t.Credible_Set.nunique()) if len(t) else 0,
        "source_CS_members": int(len(t)),
        "source_CS_max_PIP": None if t.empty else float(t.PIP.max()),
        "exact_OneK_primary_CS_overlap": int((mapped.TenK_exact_source_CS_cells.fillna("").str.split(",").map(lambda xs: cell in xs)).sum()),
        "minimum_distance_OneK_CS_to_TenK_CS_bp": None if not distances else int(min(distances)),
        "author_precomputed_IgAN_PP_H3": float(p["PP.H3.abf"]),
        "author_precomputed_IgAN_PP_H4": float(p["PP.H4.abf"]),
        "author_precomputed_IgAN_H4_ratio": float(p["PP.H4.abf"] / (p["PP.H3.abf"] + p["PP.H4.abf"])),
        "author_precomputed_top_snp": p["top_snp"],
        "replication_status": "FAIL_DISTINCT_SIGNAL_FAVORED" if float(p["PP.H3.abf"]) > float(p["PP.H4.abf"]) else "UNRESOLVED",
    })
cell_summary = pd.DataFrame(cell_summary)
cell_summary.to_csv(OUT / "R6A2D_TenK_REEP3_replication_summary.tsv", sep="\t", index=False)

primary = cell_summary[cell_summary.cell_type.isin(["CD4_Naive", "CD4_TCM"])]
status = "FAIL_INDEPENDENT_TENK_REPLICATION" if (primary.replication_status == "FAIL_DISTINCT_SIGNAL_FAVORED").all() else "HOLD_REPLICATION_UNRESOLVED"
decision = {
    "status": status,
    "OneK_primary_CS_members": int(len(mapped)),
    "OneK_primary_CS_unique_liftover": int((mapped.liftover_status == "UNIQUE_PLUS").sum()),
    "OneK_primary_CS_exact_overlap_with_TenK_source_CS": int((mapped.TenK_exact_source_CS_member_count > 0).sum()),
    "primary_cells": primary.to_dict(orient="records"),
    "auxiliary_Treg": cell_summary[cell_summary.cell_type == "Treg"].to_dict(orient="records"),
    "interpretation": "TenK10K confirms REEP3 is a T-cell cis-eQTL gene, but its source credible signal does not exactly reproduce the OneK1K primary credible signal and author-precomputed IgAN colocalization is H3-dominant in both frozen replication cells.",
    "claim_ceiling": "ONEK_DISCOVERY_ONLY_NO_INDEPENDENT_MOLECULAR_COLOC_REPLICATION",
    "project_decision": "DO_NOT_ADVANCE_TO_TWO_LOCUS_ANCESTRY_AWARE_MANUSCRIPT",
    "next_stage": "R6A3_IGAN_DESIGN_REASSESSMENT_KIDNEY_PQTL_TISSUE",
    "provenance": {
        "liftover_chain": str(CHAIN.relative_to(ROOT)),
        "liftover_chain_sha256": sha256(CHAIN),
        "OneK_CS_sha256": sha256(ONEK_CS),
        "TenK_source_CS_sha256": sha256(TENK_CS),
        "TenK_precomputed_member_manifest_sha256": sha256(PRECOMPUTED / "R6A2D_TenK_precomputed_coloc_member_manifest.json"),
    },
}


def strict_json(value):
    if isinstance(value, dict):
        return {key: strict_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [strict_json(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


decision = strict_json(decision)
(OUT / "R6A2D_final_adjudication.json").write_text(json.dumps(decision, indent=2, allow_nan=False), encoding="utf-8")
print(json.dumps(decision, indent=2, allow_nan=False))
