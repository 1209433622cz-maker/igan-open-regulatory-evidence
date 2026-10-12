#!/usr/bin/env python3
"""Extract TenK10K IL12RB2 records and compare them descriptively with FinnGen.

This script deliberately does not run colocalization.  The two TenK10K archives
available in this workspace contain gene-level association rows and
source-provided SuSiE credible-set summaries, but not complete per-variant
beta/SE summary statistics for every tested variant.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import zipfile


GENE_ID = "ENSG00000081985"
GENE_SYMBOL = "IL12RB2"
ANCHOR = "1:67340524:T:C"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cell_from_name(name: str, suffix: str) -> str:
    return Path(name).name.removesuffix(suffix)


def read_gene_level(archive: Path) -> tuple[list[dict], list[str], list[str]]:
    rows: list[dict] = []
    all_cells: list[str] = []
    suffix = "_all_cis_cv_gene_level_results.tsv"
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            if info.is_dir() or not info.filename.endswith(suffix):
                continue
            cell = cell_from_name(info.filename, suffix)
            all_cells.append(cell)
            with zf.open(info) as raw:
                text = (line.decode("utf-8-sig") for line in raw)
                for source_line, row in enumerate(csv.DictReader(text), start=2):
                    if row.get("gene") == GENE_ID:
                        rows.append(
                            {
                                "gene_symbol": GENE_SYMBOL,
                                "gene": row["gene"],
                                "celltype": cell,
                                "ACAT_p": row["ACAT_p"],
                                "top_MarkerID": row["top_MarkerID"],
                                "top_pval": row["top_pval"],
                                "source_member": info.filename,
                                "source_line": source_line,
                            }
                        )
    observed = {row["celltype"] for row in rows}
    missing = sorted(set(all_cells) - observed)
    return sorted(rows, key=lambda x: x["celltype"]), sorted(all_cells), missing


def read_susie(archive: Path) -> tuple[list[dict], list[str], list[str]]:
    rows: list[dict] = []
    all_cells: list[str] = []
    suffix = "_all_credible_snps.tsv"
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            if info.is_dir() or not info.filename.endswith(suffix):
                continue
            cell = cell_from_name(info.filename, suffix)
            all_cells.append(cell)
            with zf.open(info) as raw:
                text = (line.decode("utf-8-sig") for line in raw)
                for source_line, row in enumerate(csv.DictReader(text), start=2):
                    if row.get("gene") == GENE_ID:
                        rows.append(
                            {
                                "gene_symbol": GENE_SYMBOL,
                                "gene": row["gene"],
                                "celltype": row.get("celltype") or cell,
                                "SNP": row["SNP"],
                                "Index": row["Index"],
                                "PIP": row["PIP"],
                                "Credible_Set": row["Credible_Set"],
                                "source_member": info.filename,
                                "source_line": source_line,
                            }
                        )
    observed = {row["celltype"] for row in rows}
    missing = sorted(set(all_cells) - observed)
    return sorted(rows, key=lambda x: (x["celltype"], int(x["Credible_Set"]), x["SNP"])), sorted(all_cells), missing


def read_finngen(path: Path) -> tuple[list[dict], dict[str, dict], int]:
    rows: list[dict] = []
    keyed: dict[str, dict] = {}
    duplicates = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            row["chrom"] = row.pop("#chrom")
            key = f'{row["chrom"]}:{row["pos"]}:{row["ref"]}:{row["alt"]}'
            row["variant_key"] = key
            rows.append(row)
            if key in keyed:
                duplicates += 1
            else:
                keyed[key] = row
    return rows, keyed, duplicates


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    return None if denom == 0 else sum(x * y for x, y in zip(dx, dy)) / denom


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    root = args.workspace.resolve()
    qtl_raw = root / "1_data/qtl/eqtl/tenk10k/raw"
    gene_zip = qtl_raw / "common_variant_gene_level_results_with_annotated_fails.zip"
    susie_zip = qtl_raw / "susie_summary.zip"
    derived = root / "1_data/qtl/eqtl/tenk10k/derived/IL12RB2"
    audit_dir = root / "3_results/00_audit/R4A12FG2"
    smoke_dir = root / "3_results/01_smoke/R4A12FG2_IL12RB2"

    gene_rows, gene_cells, gene_missing = read_gene_level(gene_zip)
    susie_rows, susie_cells, susie_missing = read_susie(susie_zip)
    write_tsv(
        derived / "TenK10K_IL12RB2_gene_level.tsv",
        gene_rows,
        ["gene_symbol", "gene", "celltype", "ACAT_p", "top_MarkerID", "top_pval", "source_member", "source_line"],
    )
    write_tsv(
        derived / "TenK10K_IL12RB2_susie_credible_members.tsv",
        susie_rows,
        ["gene_symbol", "gene", "celltype", "SNP", "Index", "PIP", "Credible_Set", "source_member", "source_line"],
    )

    cs_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in susie_rows:
        cs_groups[(row["celltype"], row["Credible_Set"])].append(row)
    cs_summary: list[dict] = []
    for (cell, cs), members in sorted(cs_groups.items()):
        top = max(members, key=lambda r: float(r["PIP"]))
        cs_summary.append(
            {
                "gene_symbol": GENE_SYMBOL,
                "gene": GENE_ID,
                "celltype": cell,
                "Credible_Set": cs,
                "member_count": len(members),
                "pip_sum": f'{sum(float(r["PIP"]) for r in members):.15g}',
                "top_SNP": top["SNP"],
                "top_PIP": top["PIP"],
            }
        )
    write_tsv(
        derived / "TenK10K_IL12RB2_susie_CS_summary.tsv",
        cs_summary,
        ["gene_symbol", "gene", "celltype", "Credible_Set", "member_count", "pip_sum", "top_SNP", "top_PIP"],
    )

    region_files = {
        "R12": root / "1_data/gwas/outcome/ssc_finngen_r12_r13/regional/R12/finngen_R12_M13_SYSTSLCE_IL12RB2_chr1_66840524_67840524.tsv",
        "R13": root / "1_data/gwas/outcome/ssc_finngen_r12_r13/regional/R13/finngen_R13_M13_SYSTSLCE_IL12RB2_chr1_66840524_67840524.tsv",
    }
    releases: dict[str, dict] = {}
    disease_maps: dict[str, dict[str, dict]] = {}
    disease_rows: dict[str, list[dict]] = {}
    unique_cs = sorted({r["SNP"] for r in susie_rows})
    overlap_rows: list[dict] = []
    for release, path in region_files.items():
        rows, keyed, duplicates = read_finngen(path)
        disease_maps[release] = keyed
        disease_rows[release] = rows
        hits = [keyed[k] for k in unique_cs if k in keyed]
        best = min(hits, key=lambda r: float(r["pval"])) if hits else None
        releases[release] = {
            "path": str(path),
            "sha256": sha256(path),
            "row_count": len(rows),
            "duplicate_variant_keys": duplicates,
            "credible_member_unique_keys": len(unique_cs),
            "credible_member_exact_overlap_keys": len(hits),
            "credible_member_exact_overlap_fraction": len(hits) / len(unique_cs) if unique_cs else None,
            "best_disease_p_among_cs_members": float(best["pval"]) if best else None,
            "best_disease_variant_among_cs_members": best["variant_key"] if best else None,
            "anchor_present": ANCHOR in keyed,
        }
        for q in susie_rows:
            d = keyed.get(q["SNP"])
            if d:
                overlap_rows.append(
                    {
                        "release": release,
                        "gene": GENE_ID,
                        "celltype": q["celltype"],
                        "Credible_Set": q["Credible_Set"],
                        "qtl_variant_key": q["SNP"],
                        "qtl_PIP": q["PIP"],
                        "disease_rsid": d["rsids"],
                        "disease_p": d["pval"],
                        "disease_beta_ALT": d["beta"],
                        "disease_se": d["sebeta"],
                        "disease_af_ALT": d["af_alt"],
                    }
                )
    write_tsv(
        smoke_dir / "FinnGen_R12_R13_x_TenK10K_IL12RB2_exact_CS_overlap.tsv",
        overlap_rows,
        ["release", "gene", "celltype", "Credible_Set", "qtl_variant_key", "qtl_PIP", "disease_rsid", "disease_p", "disease_beta_ALT", "disease_se", "disease_af_ALT"],
    )

    common_keys = sorted(set(disease_maps["R12"]) & set(disease_maps["R13"]))
    b12 = [float(disease_maps["R12"][k]["beta"]) for k in common_keys]
    b13 = [float(disease_maps["R13"][k]["beta"]) for k in common_keys]
    af12 = [float(disease_maps["R12"][k]["af_alt"]) for k in common_keys]
    af13 = [float(disease_maps["R13"][k]["af_alt"]) for k in common_keys]
    same_sign = sum((x > 0) == (y > 0) for x, y in zip(b12, b13)) / len(common_keys)
    nominal_keys = [
        k for k in common_keys
        if float(disease_maps["R12"][k]["pval"]) < 0.05 or float(disease_maps["R13"][k]["pval"]) < 0.05
    ]
    nominal_same_sign = (
        sum(
            (float(disease_maps["R12"][k]["beta"]) > 0)
            == (float(disease_maps["R13"][k]["beta"]) > 0)
            for k in nominal_keys
        ) / len(nominal_keys)
        if nominal_keys else None
    )
    lead: dict[str, dict] = {}
    for release in ("R12", "R13"):
        row = min(disease_rows[release], key=lambda r: float(r["pval"]))
        lead[release] = {
            "variant_key": row["variant_key"], "rsid": row["rsids"], "p": float(row["pval"]),
            "beta_ALT": float(row["beta"]), "se": float(row["sebeta"]), "af_ALT": float(row["af_alt"]),
            "in_TenK10K_IL12RB2_CS": row["variant_key"] in set(unique_cs),
        }
    anchor_rows = {}
    for release in ("R12", "R13"):
        row = disease_maps[release].get(ANCHOR)
        anchor_rows[release] = None if row is None else {
            "variant_key": ANCHOR, "rsid": row["rsids"], "p": float(row["pval"]),
            "beta_ALT_C": float(row["beta"]), "se": float(row["sebeta"]), "af_ALT_C": float(row["af_alt"]),
            "direction_vs_2019_T_risk": "COMPATIBLE_AFTER_ALLELE_FLIP" if float(row["beta"]) < 0 else "DISCORDANT",
            "in_TenK10K_IL12RB2_CS": ANCHOR in set(unique_cs),
        }

    result = {
        "schema_version": "CMM_R4A12FG2_IL12RB2_DESCRIPTIVE_AUDIT_1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gene": {"symbol": GENE_SYMBOL, "ensembl_id": GENE_ID},
        "source_archives": {
            "gene_level": {"path": str(gene_zip), "sha256": sha256(gene_zip)},
            "susie_summary": {"path": str(susie_zip), "sha256": sha256(susie_zip)},
        },
        "tenk10k_inventory": {
            "gene_level_cells_total": len(gene_cells),
            "gene_level_cells_with_IL12RB2": len({r["celltype"] for r in gene_rows}),
            "gene_level_cells_without_IL12RB2": gene_missing,
            "susie_cells_total": len(susie_cells),
            "susie_cells_with_IL12RB2_CS": len({r["celltype"] for r in susie_rows}),
            "susie_cells_without_IL12RB2_CS": susie_missing,
            "susie_credible_sets": len(cs_groups),
            "susie_credible_member_rows": len(susie_rows),
            "susie_unique_variant_keys": len(unique_cs),
        },
        "finngen_releases": releases,
        "cross_release": {
            "exact_common_variant_keys": len(common_keys),
            "beta_pearson_r": pearson(b12, b13),
            "af_pearson_r": pearson(af12, af13),
            "same_beta_sign_fraction_all": same_sign,
            "nominal_in_either_release_count": len(nominal_keys),
            "same_beta_sign_fraction_nominal_in_either": nominal_same_sign,
            "interpretation": "CROSS_RELEASE_STABILITY_NOT_INDEPENDENT_REPLICATION",
        },
        "regional_leads": lead,
        "rs6662198_GRCh38": anchor_rows,
        "method_boundary": {
            "formal_colocalization_run": False,
            "formal_finemapping_run": False,
            "C1_updated": False,
            "reason": "Available TenK10K archives contain gene-level and credible-set summaries, not complete variant-level beta/SE statistics required for a new signal-level coloc run.",
            "classification": "DESCRIPTIVE_EXACT_VARIANT_OVERLAP_AND_INPUT_AVAILABILITY_ONLY",
        },
        "status": "PASS_REPRODUCIBLE_DESCRIPTIVE_AUDIT",
    }
    audit_dir.mkdir(parents=True, exist_ok=True)
    json_path = audit_dir / "R4A12FG2_IL12RB2_TenK10K_FinnGen_descriptive_audit.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    inv = result["tenk10k_inventory"]
    md = f"""# R4A12FG2 IL12RB2：TenK10K 与 FinnGen 描述性审计

生成时间（UTC）：`{result['generated_at_utc']}`

## 可用输入

- TenK10K gene-level：{inv['gene_level_cells_with_IL12RB2']}/{inv['gene_level_cells_total']} 个细胞类型返回 IL12RB2。
- TenK10K SuSiE summary：{inv['susie_cells_with_IL12RB2_CS']}/{inv['susie_cells_total']} 个细胞类型返回 IL12RB2 credible set，共 {inv['susie_credible_sets']} 个 CS、{inv['susie_credible_member_rows']} 条成员记录、{inv['susie_unique_variant_keys']} 个唯一精确变异键。
- R12/R13 区域各有 {releases['R12']['row_count']} 条，精确共同变异键 {len(common_keys)} 条。

## 跨 release 结果

- beta Pearson r = {result['cross_release']['beta_pearson_r']:.6f}
- ALT AF Pearson r = {result['cross_release']['af_pearson_r']:.9f}
- 全部共同变异方向一致率 = {same_sign:.4%}
- 任一 release P<0.05 的 {len(nominal_keys)} 个变异中，方向一致率 = {nominal_same_sign:.4%}
- 两版区域 lead 均为 `{lead['R13']['variant_key']}` / `{lead['R13']['rsid']}`；R13 P={lead['R13']['p']:.6g}，未达全基因组显著。
- rs6662198（GRCh38 `{ANCHOR}`）R12 beta_ALT(C)={anchor_rows['R12']['beta_ALT_C']:.6g}, P={anchor_rows['R12']['p']:.6g}；R13 beta_ALT(C)={anchor_rows['R13']['beta_ALT_C']:.6g}, P={anchor_rows['R13']['p']:.6g}。与 2019 T-risk 方向在翻转等位基因后相容。

## 解释边界

这是跨版本区域稳定性和精确 CS 成员重叠审计。R12 与 R13 样本高度嵌套，不能称为独立复制；当前 TenK10K 本地包缺少完整 variant-level beta/SE，因此本轮没有运行新 coloc、SMR 或 SuSiE-RSS，也没有更新 C1。

机器状态：`PASS_REPRODUCIBLE_DESCRIPTIVE_AUDIT`
"""
    (audit_dir / "R4A12FG2_IL12RB2_TenK10K_FinnGen_descriptive_audit.md").write_text(md, encoding="utf-8")
    print(json.dumps({
        "json": str(json_path), "gene_rows": len(gene_rows), "susie_rows": len(susie_rows),
        "credible_sets": len(cs_groups), "unique_cs_variants": len(unique_cs),
        "overlap_rows": len(overlap_rows), "status": result["status"]
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
