#!/usr/bin/env python3
"""Audit public OneK1K/TenK10K indexes around R5A1 MG subtype loci."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import pathlib
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone


ROOT = pathlib.Path(r"H:\SCI2\YR1")
QTL = ROOT / "1_data" / "qtl"
REGIONS = ROOT / "3_results" / "01_gwas" / "R5A1" / "EOMG_LOMG_heterogeneity_at_GWS_region_leads.tsv"
AUDIT = ROOT / "3_results" / "00_audit" / "R5A1"
RESULTS = ROOT / "3_results" / "03_qtl" / "R5A1"
WINDOW = 1_000_000
GRCH37_BY_RSID = {
    "rs2476601": 114_377_568,
    "rs7596255": 39_379_926,
    "rs6861227": 150_447_128,
    "rs7239261": 60_005_046,
}


def digest(path: pathlib.Path, name: str) -> str:
    h = hashlib.new(name)
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def load_regions() -> list[dict[str, object]]:
    with REGIONS.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return [
        {
            "region_id": row["region_id"],
            "chromosome": row["chromosome"],
            "lead_position": int(row["lead_position"]),
            "lead_rsid": row["lead_rsid"],
            "lead_variant_id": row["lead_variant_id"],
            "lead_source": row["lead_source"],
            "p_het": float(row["p_het"]),
            "lead_position_grch37": GRCH37_BY_RSID[row["lead_rsid"]],
        }
        for row in rows
    ]


def locus_for(
    chrom: str,
    pos: int,
    regions: list[dict[str, object]],
    position_key: str = "lead_position",
) -> dict[str, object] | None:
    matches = [r for r in regions if str(r["chromosome"]) == chrom and abs(int(r[position_key]) - pos) <= WINDOW]
    if not matches:
        return None
    return min(matches, key=lambda r: abs(int(r[position_key]) - pos))


def bh_adjust(values: list[float]) -> list[float]:
    n = len(values)
    order = sorted(range(n), key=values.__getitem__, reverse=True)
    adjusted = [1.0] * n
    running = 1.0
    for index in order:
        rank = sum(values[j] <= values[index] for j in range(n))
        raw = values[index] * n / max(1, rank)
        running = min(running, raw)
        adjusted[index] = min(1.0, running)
    return adjusted


def bh_adjust_fast(values: list[float]) -> list[float]:
    n = len(values)
    ordered = sorted(enumerate(values), key=lambda x: x[1])
    adjusted = [1.0] * n
    running = 1.0
    for rank_from_end in range(n - 1, -1, -1):
        original_index, p = ordered[rank_from_end]
        rank = rank_from_end + 1
        running = min(running, p * n / rank)
        adjusted[original_index] = min(1.0, running)
    return adjusted


def scan_onek(path: pathlib.Path, regions: list[dict[str, object]]) -> tuple[list[dict], dict]:
    records: list[dict] = []
    cells: Counter[str] = Counter()
    q05 = 0
    rows = 0
    with zipfile.ZipFile(path) as archive:
        members = [n for n in archive.namelist() if n.endswith(".csv") and not n.startswith("__MACOSX")]
        bad = archive.testzip()
        for member in members:
            match = re.search(r"OneK1K_(.+?)\.sig_cis_qtl_pairs\.chr", pathlib.PurePosixPath(member).name)
            if not match:
                continue
            cell = match.group(1)
            with archive.open(member) as raw, io.TextIOWrapper(raw, encoding="utf-8-sig") as text:
                reader = csv.DictReader(text, delimiter="\t")
                for row in reader:
                    rows += 1
                    cells[cell] += 1
                    qval = float(row["qval"])
                    if qval < 0.05:
                        q05 += 1
                    chrom, pos_text = row["variant_id"].split(":", 1)
                    pos = int(pos_text)
                    region = locus_for(chrom, pos, regions, "lead_position_grch37")
                    if region is None:
                        continue
                    records.append(
                        {
                            "region_id": region["region_id"],
                            "lead_rsid": region["lead_rsid"],
                            "lead_source": region["lead_source"],
                            "cell_type": cell,
                            "gene_symbol": row["phenotype_id"],
                            "top_variant": row["variant_id"],
                            "coordinate_build": "GRCh37",
                            "top_variant_distance_from_gwas_lead": pos - int(region["lead_position_grch37"]),
                            "tss_distance": row["tss_distance"],
                            "pval_nominal": row["pval_nominal"],
                            "pval_beta": row["pval_beta"],
                            "qval": row["qval"],
                            "qval_lt_0_05": qval < 0.05,
                            "slope": row["slope"],
                            "slope_se": row["slope_se"],
                        }
                    )
    return records, {
        "zip_crc_pass": bad is None,
        "members": len(members),
        "rows": rows,
        "cell_types": dict(sorted(cells.items())),
        "qval_lt_0_05_rows": q05,
    }


def scan_tenk_gene(path: pathlib.Path, regions: list[dict[str, object]]) -> tuple[list[dict], dict]:
    records: list[dict] = []
    cells: dict[str, dict] = {}
    with zipfile.ZipFile(path) as archive:
        members = [n for n in archive.namelist() if n.endswith(".tsv")]
        bad = archive.testzip()
        for member in members:
            cell = pathlib.PurePosixPath(member).name.split("_all_cis", 1)[0]
            parsed: list[dict] = []
            failures = 0
            with archive.open(member) as raw, io.TextIOWrapper(raw, encoding="utf-8-sig") as text:
                reader = csv.DictReader(text)
                for row in reader:
                    try:
                        acat = float(row["ACAT_p"])
                        top_p = float(row["top_pval"])
                        chrom, pos_text, ref, alt = row["top_MarkerID"].split(":", 3)
                        pos = int(pos_text)
                    except (ValueError, TypeError, AttributeError):
                        failures += 1
                        continue
                    parsed.append({"row": row, "acat": acat, "top_p": top_p, "chrom": chrom, "pos": pos, "ref": ref, "alt": alt})
            qvals = bh_adjust_fast([x["acat"] for x in parsed])
            cells[cell] = {
                "numeric_gene_rows": len(parsed),
                "annotated_failure_rows": failures,
                "acat_fdr_lt_0_05": sum(q < 0.05 for q in qvals),
            }
            for item, qval in zip(parsed, qvals):
                region = locus_for(item["chrom"], item["pos"], regions)
                if region is None:
                    continue
                records.append(
                    {
                        "region_id": region["region_id"],
                        "lead_rsid": region["lead_rsid"],
                        "lead_source": region["lead_source"],
                        "cell_type": cell,
                        "gene_ensembl": item["row"]["gene"],
                        "top_variant": item["row"]["top_MarkerID"],
                        "coordinate_build": "GRCh38",
                        "top_variant_distance_from_gwas_lead": item["pos"] - int(region["lead_position"]),
                        "ACAT_p": item["acat"],
                        "ACAT_BH_q_within_cell": qval,
                        "ACAT_BH_q_lt_0_05": qval < 0.05,
                        "top_pval": item["top_p"],
                    }
                )
    return records, {"zip_crc_pass": bad is None, "members": len(members), "cell_types": cells}


def scan_tenk_susie(path: pathlib.Path, regions: list[dict[str, object]]) -> tuple[list[dict], dict]:
    records: list[dict] = []
    cells: Counter[str] = Counter()
    total = 0
    with zipfile.ZipFile(path) as archive:
        members = [n for n in archive.namelist() if n.endswith(".tsv")]
        bad = archive.testzip()
        for member in members:
            with archive.open(member) as raw, io.TextIOWrapper(raw, encoding="utf-8-sig") as text:
                reader = csv.DictReader(text)
                for row in reader:
                    total += 1
                    cells[row["celltype"]] += 1
                    chrom, pos_text, ref, alt = row["SNP"].split(":", 3)
                    pos = int(pos_text)
                    region = locus_for(chrom, pos, regions)
                    if region is None:
                        continue
                    records.append(
                        {
                            "region_id": region["region_id"],
                            "lead_rsid": region["lead_rsid"],
                            "lead_source": region["lead_source"],
                            "cell_type": row["celltype"],
                            "gene_ensembl": row["gene"],
                            "credible_set": row["Credible_Set"],
                            "variant": row["SNP"],
                            "coordinate_build": "GRCh38",
                            "variant_distance_from_gwas_lead": pos - int(region["lead_position"]),
                            "PIP": float(row["PIP"]),
                        }
                    )
    return records, {
        "zip_crc_pass": bad is None,
        "members": len(members),
        "credible_set_member_rows": total,
        "cell_types": dict(sorted(cells.items())),
    }


def write_tsv(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["region_id"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    regions = load_regions()
    onek_path = QTL / "OneK1K" / "OneK1K_TensorQTL_top_eQTL_summary.zip"
    tenk_gene_path = QTL / "TenK10K" / "common_variant_gene_level_results_with_annotated_fails.zip"
    tenk_susie_path = QTL / "TenK10K" / "susie_summary.zip"
    onek, onek_inventory = scan_onek(onek_path, regions)
    print(f"ONEK_OK\trows_in_loci={len(onek)}", flush=True)
    tenk_gene, tenk_gene_inventory = scan_tenk_gene(tenk_gene_path, regions)
    print(f"TENK_GENE_OK\trows_in_loci={len(tenk_gene)}", flush=True)
    tenk_susie, tenk_susie_inventory = scan_tenk_susie(tenk_susie_path, regions)
    print(f"TENK_SUSIE_OK\tcs_members_in_loci={len(tenk_susie)}", flush=True)
    write_tsv(RESULTS / "OneK1K_top_eQTL_in_MG_loci.tsv", onek)
    write_tsv(RESULTS / "TenK10K_gene_level_in_MG_loci.tsv", tenk_gene)
    write_tsv(RESULTS / "TenK10K_SuSiE_CS_in_MG_loci.tsv", tenk_susie)
    inventory = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "search_window": "+/-1 Mb around each distance-defined GWS region lead; GRCh37 positions for OneK1K and GRCh38 positions for TenK10K",
        "interpretation_limit": "index-level feasibility only; full regional coloc requires complete variant-level QTL",
        "resources": {
            "OneK1K_top_eQTL": {
                "path": str(onek_path),
                "bytes": onek_path.stat().st_size,
                "md5": digest(onek_path, "md5"),
                "expected_md5": "46e986dc53c9f4f1b6daa2b7a73d277c",
                **onek_inventory,
                "rows_in_mg_loci": len(onek),
                "significant_rows_in_mg_loci": sum(bool(x["qval_lt_0_05"]) for x in onek),
            },
            "TenK10K_gene_level": {
                "path": str(tenk_gene_path),
                "bytes": tenk_gene_path.stat().st_size,
                "md5": digest(tenk_gene_path, "md5"),
                "expected_md5": "b5cd2ee1f34f90539ebf6683dcd35a2e",
                **tenk_gene_inventory,
                "rows_in_mg_loci": len(tenk_gene),
                "significant_rows_in_mg_loci": sum(bool(x["ACAT_BH_q_lt_0_05"]) for x in tenk_gene),
            },
            "TenK10K_susie": {
                "path": str(tenk_susie_path),
                "bytes": tenk_susie_path.stat().st_size,
                "md5": digest(tenk_susie_path, "md5"),
                "expected_md5": "f321c719030cc837cf27e09cd2ea6b65",
                **tenk_susie_inventory,
                "credible_set_members_in_mg_loci": len(tenk_susie),
            },
        },
    }
    for resource in inventory["resources"].values():
        resource["md5_pass"] = resource["md5"] == resource["expected_md5"]
    with (AUDIT / "MG_QTL_index_inventory.json").open("w", encoding="utf-8") as handle:
        json.dump(inventory, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
