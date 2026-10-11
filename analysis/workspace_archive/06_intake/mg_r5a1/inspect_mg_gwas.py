#!/usr/bin/env python3
"""R5A1 byte-level QC and EOMG-vs-LOMG lead-variant heterogeneity audit."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import pathlib
from collections import Counter
from datetime import datetime, timezone


ROOT = pathlib.Path(r"H:\SCI2\YR1")
DATA = ROOT / "1_data" / "gwas" / "MG" / "R5A1_GWAS_Catalog"
AUDIT = ROOT / "3_results" / "00_audit" / "R5A1"
RESULTS = ROOT / "3_results" / "01_gwas" / "R5A1"

STUDIES = {
    "GCST90432156": {
        "label": "MG_overall",
        "cases": 5708,
        "controls": 432028,
        "official_md5": "dff27532c33b47ed0b3b9197848d3ba8",
        "expected_bytes": 195170755,
    },
    "GCST90432157": {
        "label": "EOMG",
        "cases": 1391,
        "controls": 22407,
        "official_md5": "ef79b92a35ec5e03c6be652e1ed908b0",
        "expected_bytes": 217879063,
    },
    "GCST90432158": {
        "label": "LOMG",
        "cases": 2404,
        "controls": 64103,
        "official_md5": "35fb1e9a999b4566f940071e0d72ec54",
        "expected_bytes": 187396334,
    },
}

REQUIRED_HEADER = [
    "chromosome",
    "base_pair_location",
    "effect_allele",
    "other_allele",
    "odds_ratio",
    "standard_error",
    "effect_allele_frequency",
    "p_value",
    "rsid",
    "hm_coordinate_conversion",
    "hm_code",
    "variant_id",
]


def digest(path: pathlib.Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            hasher.update(block)
    return hasher.hexdigest()


def parse_variant_id(value: str) -> tuple[str, int, str, str]:
    chrom, pos, ref, alt = value.split("_", 3)
    return chrom, int(pos), ref.upper(), alt.upper()


def chrom_rank(chrom: str) -> int:
    token = chrom.removeprefix("chr").upper()
    if token.isdigit():
        return int(token)
    return {"X": 23, "Y": 24, "MT": 25, "M": 25}.get(token, 99)


def in_mhc(chrom: str, pos: int) -> bool:
    return chrom.removeprefix("chr") == "6" and 25_000_000 <= pos <= 35_000_000


def decode_row(parts: list[bytes], index: dict[str, int]) -> dict[str, object]:
    def s(name: str) -> str:
        return parts[index[name]].decode("ascii", errors="strict")

    return {
        "chromosome": s("chromosome"),
        "base_pair_location": int(s("base_pair_location")),
        "effect_allele": s("effect_allele").upper(),
        "other_allele": s("other_allele").upper(),
        "odds_ratio": float(s("odds_ratio")),
        "standard_error": float(s("standard_error")),
        "effect_allele_frequency": float(s("effect_allele_frequency")),
        "p_value": float(s("p_value")),
        "rsid": s("rsid"),
        "hm_coordinate_conversion": s("hm_coordinate_conversion"),
        "hm_code": s("hm_code"),
        "variant_id": s("variant_id"),
    }


def scan(path: pathlib.Path, expected_md5: str, expected_bytes: int) -> tuple[dict, list[dict]]:
    summary: dict[str, object] = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "expected_bytes": expected_bytes,
        "md5": digest(path, "md5"),
        "expected_md5": expected_md5,
        "sha256": digest(path, "sha256"),
        "rows": 0,
        "invalid_column_count": 0,
        "invalid_numeric": 0,
        "invalid_variant_id": 0,
        "coordinate_mismatch": 0,
        "allele_mapping_fail": 0,
        "invalid_effect_fields": 0,
        "duplicate_gws_variant_id": 0,
        "chromosome_counts": Counter(),
        "hm_code_counts": Counter(),
        "min_p": None,
        "gws_rows": 0,
        "gws_non_mhc_rows": 0,
        "gzip_stream_complete": False,
    }
    gws: list[dict] = []
    gws_ids: set[str] = set()
    with gzip.open(path, "rb") as handle:
        header = handle.readline().decode("utf-8-sig").rstrip("\r\n").split("\t")
        summary["header"] = header
        summary["header_exact"] = header == REQUIRED_HEADER
        if not all(name in header for name in REQUIRED_HEADER):
            raise RuntimeError(f"Missing required columns in {path}: {header}")
        index = {name: header.index(name) for name in REQUIRED_HEADER}
        for raw in handle:
            if not raw.strip():
                continue
            summary["rows"] += 1
            parts = raw.rstrip(b"\r\n").split(b"\t")
            if len(parts) != len(header):
                summary["invalid_column_count"] += 1
                continue
            try:
                row = decode_row(parts, index)
            except (ValueError, UnicodeDecodeError):
                summary["invalid_numeric"] += 1
                continue
            chrom = str(row["chromosome"])
            pos = int(row["base_pair_location"])
            summary["chromosome_counts"][chrom] += 1
            summary["hm_code_counts"][str(row["hm_code"])] += 1
            p = float(row["p_value"])
            current_min = summary["min_p"]
            summary["min_p"] = p if current_min is None else min(float(current_min), p)
            if not (
                float(row["odds_ratio"]) > 0
                and float(row["standard_error"]) > 0
                and 0 <= float(row["effect_allele_frequency"]) <= 1
                and 0 <= p <= 1
                and row["effect_allele"] != row["other_allele"]
            ):
                summary["invalid_effect_fields"] += 1
            try:
                vchrom, vpos, ref, alt = parse_variant_id(str(row["variant_id"]))
            except (ValueError, AttributeError):
                summary["invalid_variant_id"] += 1
                continue
            if chrom != vchrom or pos != vpos:
                summary["coordinate_mismatch"] += 1
            if row["effect_allele"] not in {ref, alt} or row["other_allele"] not in {ref, alt}:
                summary["allele_mapping_fail"] += 1
            if p < 5e-8:
                summary["gws_rows"] += 1
                if not in_mhc(chrom, pos):
                    summary["gws_non_mhc_rows"] += 1
                if row["variant_id"] in gws_ids:
                    summary["duplicate_gws_variant_id"] += 1
                gws_ids.add(str(row["variant_id"]))
                gws.append(row)
        summary["gzip_stream_complete"] = True
    summary["chromosome_counts"] = dict(sorted(summary["chromosome_counts"].items(), key=lambda x: chrom_rank(x[0])))
    summary["hm_code_counts"] = dict(sorted(summary["hm_code_counts"].items()))
    summary["md5_pass"] = summary["md5"] == expected_md5
    summary["byte_size_pass"] = summary["bytes"] == expected_bytes
    summary["schema_pass"] = bool(summary["header_exact"])
    summary["content_pass"] = all(
        summary[key] == 0
        for key in (
            "invalid_column_count",
            "invalid_numeric",
            "invalid_variant_id",
            "coordinate_mismatch",
            "allele_mapping_fail",
            "invalid_effect_fields",
            "duplicate_gws_variant_id",
        )
    )
    summary["intake_pass"] = bool(
        summary["md5_pass"]
        and summary["byte_size_pass"]
        and summary["schema_pass"]
        and summary["content_pass"]
        and summary["gzip_stream_complete"]
        and int(summary["rows"]) > 0
    )
    return summary, gws


def select_rows(path: pathlib.Path, wanted: set[str]) -> dict[str, dict]:
    found: dict[str, dict] = {}
    with gzip.open(path, "rb") as handle:
        header = handle.readline().decode("utf-8-sig").rstrip("\r\n").split("\t")
        index = {name: header.index(name) for name in REQUIRED_HEADER}
        variant_index = index["variant_id"]
        for raw in handle:
            parts = raw.rstrip(b"\r\n").split(b"\t")
            if len(parts) != len(header):
                continue
            variant_id = parts[variant_index].decode("ascii", errors="strict")
            if variant_id in wanted:
                found[variant_id] = decode_row(parts, index)
    return found


def alt_aligned(row: dict | None) -> dict[str, object]:
    if row is None:
        return {"present": False}
    _chrom, _pos, ref, alt = parse_variant_id(str(row["variant_id"]))
    effect = str(row["effect_allele"])
    beta = math.log(float(row["odds_ratio"]))
    eaf = float(row["effect_allele_frequency"])
    if effect == ref:
        beta = -beta
        eaf = 1 - eaf
    elif effect != alt:
        raise RuntimeError(f"Cannot align {row['variant_id']}: effect={effect}, ref={ref}, alt={alt}")
    return {
        "present": True,
        "effect_allele_original": effect,
        "other_allele_original": row["other_allele"],
        "odds_ratio_original": row["odds_ratio"],
        "beta_alt": beta,
        "se": row["standard_error"],
        "eaf_alt": eaf,
        "p": row["p_value"],
        "rsid": row["rsid"],
    }


def make_regions(gws_by_label: dict[str, list[dict]]) -> list[dict]:
    rows: dict[str, dict] = {}
    for label in ("EOMG", "LOMG"):
        for row in gws_by_label[label]:
            if in_mhc(str(row["chromosome"]), int(row["base_pair_location"])):
                continue
            item = rows.setdefault(
                str(row["variant_id"]),
                {
                    "variant_id": row["variant_id"],
                    "chromosome": row["chromosome"],
                    "position": row["base_pair_location"],
                    "rsid": row["rsid"],
                    "EOMG_p": None,
                    "LOMG_p": None,
                },
            )
            item[f"{label}_p"] = row["p_value"]
    ordered = sorted(rows.values(), key=lambda x: (chrom_rank(str(x["chromosome"])), int(x["position"])))
    regions: list[dict] = []
    for item in ordered:
        if (
            not regions
            or str(regions[-1]["chromosome"]) != str(item["chromosome"])
            or int(item["position"]) - int(regions[-1]["end"]) > 3_000_000
        ):
            regions.append(
                {
                    "region_id": f"GWSR{len(regions)+1:02d}",
                    "chromosome": item["chromosome"],
                    "start": item["position"],
                    "end": item["position"],
                    "members": [item],
                }
            )
        else:
            regions[-1]["end"] = item["position"]
            regions[-1]["members"].append(item)
    for region in regions:
        lead = min(
            region["members"],
            key=lambda x: min(p for p in (x["EOMG_p"], x["LOMG_p"]) if p is not None),
        )
        region["lead_variant_id"] = lead["variant_id"]
        region["lead_rsid"] = lead["rsid"]
        region["lead_position"] = lead["position"]
        region["lead_source"] = (
            "EOMG" if lead["LOMG_p"] is None or (lead["EOMG_p"] is not None and lead["EOMG_p"] <= lead["LOMG_p"]) else "LOMG"
        )
        region["min_p"] = min(p for p in (lead["EOMG_p"], lead["LOMG_p"]) if p is not None)
        region["gws_variant_count"] = len(region["members"])
    return regions


def write_tsv(path: pathlib.Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    summaries: dict[str, dict] = {}
    gws_by_label: dict[str, list[dict]] = {}
    for accession, metadata in STUDIES.items():
        path = DATA / accession / f"{accession}.h.tsv.gz"
        summary, gws = scan(path, str(metadata["official_md5"]), int(metadata["expected_bytes"]))
        summary["actual_md5"] = summary.pop("md5")
        summary["official_md5"] = summary.pop("expected_md5")
        summary["official_md5_pass"] = summary.pop("md5_pass")
        summary["independent_retrieval_identical"] = None
        summary["source_sidecar_exception_pass"] = False
        if accession == "GCST90432157":
            replica = pathlib.Path(str(path) + ".redownload")
            summary["independent_retrieval_path"] = str(replica)
            if replica.exists() and replica.stat().st_size == path.stat().st_size:
                replica_sha256 = digest(replica, "sha256")
                summary["independent_retrieval_sha256"] = replica_sha256
                summary["independent_retrieval_identical"] = replica_sha256 == summary["sha256"]
                summary["source_sidecar_exception_pass"] = bool(
                    not summary["official_md5_pass"] and summary["independent_retrieval_identical"]
                )
        summary["checksum_adjudication_pass"] = bool(
            summary["official_md5_pass"] or summary["source_sidecar_exception_pass"]
        )
        summary["intake_pass"] = bool(
            summary["checksum_adjudication_pass"]
            and summary["byte_size_pass"]
            and summary["schema_pass"]
            and summary["content_pass"]
            and summary["gzip_stream_complete"]
            and int(summary["rows"]) > 0
        )
        summary.update({"accession": accession, **metadata})
        summaries[accession] = summary
        gws_by_label[str(metadata["label"])] = gws
        print(f"SCAN_OK\t{accession}\trows={summary['rows']}\tgws={summary['gws_rows']}\tpass={summary['intake_pass']}", flush=True)

    regions = make_regions(gws_by_label)
    lead_ids = {str(region["lead_variant_id"]) for region in regions}
    selected: dict[str, dict[str, dict]] = {}
    for accession, metadata in STUDIES.items():
        selected[str(metadata["label"])] = select_rows(DATA / accession / f"{accession}.h.tsv.gz", lead_ids)
        print(f"LEADS_OK\t{accession}\tfound={len(selected[str(metadata['label'])])}/{len(lead_ids)}", flush=True)

    heterogeneity: list[dict] = []
    for region in regions:
        variant_id = str(region["lead_variant_id"])
        e = alt_aligned(selected["EOMG"].get(variant_id))
        l = alt_aligned(selected["LOMG"].get(variant_id))
        o = alt_aligned(selected["MG_overall"].get(variant_id))
        record: dict[str, object] = {
            key: region[key]
            for key in ("region_id", "chromosome", "start", "end", "lead_variant_id", "lead_rsid", "lead_position", "lead_source", "min_p", "gws_variant_count")
        }
        _chrom, _pos, ref, alt = parse_variant_id(variant_id)
        record.update({"reference_allele": ref, "alternate_allele": alt})
        for label, values in (("overall", o), ("EOMG", e), ("LOMG", l)):
            record[f"{label}_present"] = values["present"]
            for field in ("beta_alt", "se", "eaf_alt", "p", "odds_ratio_original", "effect_allele_original"):
                record[f"{label}_{field}"] = values.get(field)
        record["heterogeneity_testable"] = bool(e["present"] and l["present"])
        if record["heterogeneity_testable"]:
            delta = float(e["beta_alt"]) - float(l["beta_alt"])
            se_delta = math.sqrt(float(e["se"]) ** 2 + float(l["se"]) ** 2)
            z = delta / se_delta
            p_het = math.erfc(abs(z) / math.sqrt(2))
            record.update({"delta_beta_alt_E_minus_L": delta, "se_delta": se_delta, "z_het": z, "p_het": p_het})
        heterogeneity.append(record)

    testable = [x for x in heterogeneity if x["heterogeneity_testable"]]
    multiplicity = len(testable)
    for row in heterogeneity:
        if row.get("p_het") is not None:
            row["p_het_bonferroni"] = min(1.0, float(row["p_het"]) * multiplicity)
            row["heterogeneity_nominal"] = float(row["p_het"]) < 0.05
            row["heterogeneity_bonferroni"] = float(row["p_het_bonferroni"]) < 0.05

    manifest_rows = []
    for accession, summary in summaries.items():
        manifest_rows.append(
            {
                "accession": accession,
                "label": summary["label"],
                "path": summary["path"],
                "bytes": summary["bytes"],
                "actual_md5": summary["actual_md5"],
                "official_md5": summary["official_md5"],
                "official_md5_pass": summary["official_md5_pass"],
                "source_sidecar_exception_pass": summary["source_sidecar_exception_pass"],
                "sha256": summary["sha256"],
                "rows": summary["rows"],
                "build": "GRCh38",
                "cases": summary["cases"],
                "controls": summary["controls"],
                "gws_rows": summary["gws_rows"],
                "gws_non_mhc_rows": summary["gws_non_mhc_rows"],
                "intake_pass": summary["intake_pass"],
            }
        )
    write_tsv(
        RESULTS / "MG_GWAS_byte_manifest.tsv",
        manifest_rows,
        list(manifest_rows[0]),
    )
    fields = list(heterogeneity[0]) if heterogeneity else ["region_id"]
    write_tsv(RESULTS / "EOMG_LOMG_heterogeneity_at_GWS_region_leads.tsv", heterogeneity, fields)

    gate = {
        "all_3_gwas_bytes": all(bool(x["intake_pass"]) for x in summaries.values()),
        "heterogeneity_schema": all(row["heterogeneity_testable"] for row in heterogeneity) and len(heterogeneity) > 0,
        "non_mhc_gws_regions": len(regions),
        "non_mhc_testable_loci": len(testable),
        "non_mhc_testable_loci_at_least_2": len(testable) >= 2,
        "heterogeneity_nominal_count": sum(bool(row.get("heterogeneity_nominal")) for row in heterogeneity),
        "heterogeneity_bonferroni_count": sum(bool(row.get("heterogeneity_bonferroni")) for row in heterogeneity),
    }
    output = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mhc_exclusion_grch38": "chr6:25000000-35000000",
        "region_grouping": "distance-only 3 Mb descriptive grouping; not LD independence",
        "heterogeneity": "independent-sample z test on ALT-aligned log(OR)",
        "studies": summaries,
        "gate": gate,
    }
    with (AUDIT / "MG_GWAS_intake_and_heterogeneity_audit.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(gate, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
