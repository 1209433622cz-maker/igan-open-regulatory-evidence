#!/usr/bin/env python3
"""Harmonize TenK10K NK IL12RB2 eQTLs with FinnGen R12/R13 SSc.

Both sources are expected on GRCh38 and report effects for the ALT/Allele2
allele.  Only exact REF/ALT matches are retained.  Reverse-allele records at the
same position are counted as diagnostics and excluded because multi-allelic and
repeat variants can otherwise create false matches.  Strand complements are
never inferred.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


GENE_ID = "ENSG00000081985"
QTL_TOP = "1:67324915:T:C"
ANCHOR_RSID = "rs6662198"
RELEASE_METADATA = {
    "R12": {"cases": 854, "controls": 484_260},
    "R13": {"cases": 883, "controls": 483_310},
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def as_float(value: str, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"non-finite {name}: {value!r}")
    return result


def canonical(chrom: str, pos: str | int, ref: str, alt: str) -> tuple[str, int, str, str]:
    chrom = chrom.removeprefix("chr").upper()
    position = int(pos)
    ref = ref.upper()
    alt = alt.upper()
    if not ref or not alt:
        raise ValueError("empty allele")
    # Minimal representation without using a reference genome. Keep one base on
    # each allele, as required for VCF-style indels.
    while len(ref) > 1 and len(alt) > 1 and ref[-1] == alt[-1]:
        ref, alt = ref[:-1], alt[:-1]
    while len(ref) > 1 and len(alt) > 1 and ref[0] == alt[0]:
        ref, alt = ref[1:], alt[1:]
        position += 1
    return chrom, position, ref, alt


def key_text(key: tuple[str, int, str, str]) -> str:
    return f"{key[0]}:{key[1]}:{key[2]}:{key[3]}"


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def load_qtl(path: Path) -> tuple[dict, dict]:
    records: dict[tuple[str, int, str, str], dict] = {}
    observed_headers = None
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        observed_headers = reader.fieldnames
        required = {
            "CHR", "POS", "MarkerID", "Allele1", "Allele2", "AF_Allele2",
            "BETA", "SE", "p.value", "N", "gene",
        }
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"TenK10K fields missing: {sorted(missing)}")
        for line_number, row in enumerate(reader, start=2):
            if row["gene"] != GENE_ID:
                raise RuntimeError(f"non-target gene at line {line_number}: {row['gene']!r}")
            key = canonical(row["CHR"], row["POS"], row["Allele1"], row["Allele2"])
            marker_parts = row["MarkerID"].split(":")
            if len(marker_parts) != 4 or canonical(*marker_parts) != key:
                raise RuntimeError(f"MarkerID/field mismatch at line {line_number}: {row['MarkerID']}")
            if key in records:
                raise RuntimeError(f"duplicate normalized QTL key: {key_text(key)}")
            beta = as_float(row["BETA"], "QTL BETA")
            se = as_float(row["SE"], "QTL SE")
            p = as_float(row["p.value"], "QTL p")
            af = as_float(row["AF_Allele2"], "QTL AF")
            n = as_float(row["N"], "QTL N")
            if se <= 0 or not 0 <= p <= 1 or not 0 <= af <= 1 or n <= 0:
                raise RuntimeError(f"invalid QTL numeric value at line {line_number}")
            records[key] = {
                "qtl_marker": row["MarkerID"],
                "qtl_beta": beta,
                "qtl_se": se,
                "qtl_p": p,
                "qtl_af_alt": af,
                "qtl_n": n,
                "qtl_source_line": row.get("source_line", str(line_number)),
            }
    return records, {"headers": observed_headers, "rows": len(records), "sha256": sha256_file(path)}


def load_cs(path: Path) -> tuple[dict, dict]:
    mapping: dict[tuple[str, int, str, str], list[dict]] = {}
    rows = 0
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"gene", "celltype", "SNP", "PIP", "Credible_Set"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"credible-set fields missing: {sorted(missing)}")
        for row in reader:
            if row["gene"] != GENE_ID or row["celltype"] != "NK":
                continue
            parts = row["SNP"].split(":")
            if len(parts) != 4:
                raise RuntimeError(f"invalid credible-set key: {row['SNP']}")
            key = canonical(*parts)
            mapping.setdefault(key, []).append(
                {"cs": str(row["Credible_Set"]), "pip": as_float(row["PIP"], "PIP")}
            )
            rows += 1
    if not mapping:
        raise RuntimeError("no NK IL12RB2 credible-set members")
    return mapping, {"rows": rows, "unique_variants": len(mapping), "sha256": sha256_file(path)}


def load_gwas(path: Path) -> tuple[dict, dict]:
    records: dict[tuple[str, int, str, str], dict] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"#chrom", "pos", "ref", "alt", "rsids", "pval", "beta", "sebeta", "af_alt"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"FinnGen fields missing: {sorted(missing)}")
        for line_number, row in enumerate(reader, start=2):
            key = canonical(row["#chrom"], row["pos"], row["ref"], row["alt"])
            if key in records:
                raise RuntimeError(f"duplicate normalized GWAS key: {key_text(key)}")
            beta = as_float(row["beta"], "GWAS beta")
            se = as_float(row["sebeta"], "GWAS SE")
            p = as_float(row["pval"], "GWAS p")
            af = as_float(row["af_alt"], "GWAS AF")
            if se <= 0 or not 0 <= p <= 1 or not 0 <= af <= 1:
                raise RuntimeError(f"invalid GWAS numeric value at line {line_number}")
            records[key] = {
                "gwas_beta": beta,
                "gwas_se": se,
                "gwas_p": p,
                "gwas_af_alt": af,
                "gwas_rsids": row["rsids"],
                "gwas_source_line": line_number,
            }
    lead_key = min(records, key=lambda key: records[key]["gwas_p"])
    return records, {
        "rows": len(records),
        "sha256": sha256_file(path),
        "lead_key": key_text(lead_key),
        "lead_p": records[lead_key]["gwas_p"],
        "lead_rsid": records[lead_key]["gwas_rsids"],
    }


def harmonize_release(release: str, qtl: dict, gwas: dict, cs: dict) -> tuple[list[dict], dict]:
    rows = []
    exact = 0
    reverse_allele_pairs_excluded = 0
    for qtl_key, qtl_row in qtl.items():
        match = gwas.get(qtl_key)
        if match is None:
            chrom, pos, ref, alt = qtl_key
            swapped_key = (chrom, pos, alt, ref)
            if swapped_key in gwas:
                reverse_allele_pairs_excluded += 1
            continue
        exact += 1
        cs_entries = cs.get(qtl_key, [])
        rows.append(
            {
                "release": release,
                "variant_key": key_text(qtl_key),
                "chrom": qtl_key[0],
                "pos": qtl_key[1],
                "ref": qtl_key[2],
                "alt": qtl_key[3],
                "alignment": "EXACT_REF_ALT",
                **qtl_row,
                **match,
                "qtl_z": qtl_row["qtl_beta"] / qtl_row["qtl_se"],
                "gwas_z": match["gwas_beta"] / match["gwas_se"],
                "af_abs_diff": abs(qtl_row["qtl_af_alt"] - match["gwas_af_alt"]),
                "source_cs": ",".join(sorted({entry["cs"] for entry in cs_entries})),
                "source_cs_pip": sum(entry["pip"] for entry in cs_entries),
            }
        )
    rows.sort(key=lambda row: (int(row["chrom"]), row["pos"], row["ref"], row["alt"]))
    joined_qtl_keys = set()
    for row in rows:
        joined_qtl_keys.add(canonical(row["chrom"], row["pos"], row["ref"], row["alt"]))
    cs_totals: dict[str, float] = {}
    cs_covered: dict[str, float] = {}
    cs_counts: dict[str, int] = {}
    cs_counts_covered: dict[str, int] = {}
    for key, entries in cs.items():
        for entry in entries:
            cs_id = entry["cs"]
            cs_totals[cs_id] = cs_totals.get(cs_id, 0.0) + entry["pip"]
            cs_counts[cs_id] = cs_counts.get(cs_id, 0) + 1
            if key in joined_qtl_keys:
                cs_covered[cs_id] = cs_covered.get(cs_id, 0.0) + entry["pip"]
                cs_counts_covered[cs_id] = cs_counts_covered.get(cs_id, 0) + 1
    af_diffs = [row["af_abs_diff"] for row in rows]
    qtl_top_key = canonical(*QTL_TOP.split(":"))
    lead_key = min(gwas, key=lambda key: gwas[key]["gwas_p"])
    anchor_keys = [key for key, row in gwas.items() if ANCHOR_RSID in row["gwas_rsids"].split(",")]
    checks = {
        "qtl_unique_variants_ge_100": len(qtl) >= 100,
        "overlap_count_ge_100": len(rows) >= 100,
        "overlap_fraction_qtl_ge_0_80": len(rows) / len(qtl) >= 0.80 if qtl else False,
        "exact_reference_alignment_fraction_ge_0_99": exact / len(rows) >= 0.99 if rows else False,
        "af_median_abs_diff_le_0_10": (percentile(af_diffs, 0.5) or math.inf) <= 0.10,
        "af_p95_abs_diff_le_0_20": (percentile(af_diffs, 0.95) or math.inf) <= 0.20,
        "qtl_top_covered": qtl_top_key in joined_qtl_keys,
        "disease_regional_lead_covered": lead_key in {canonical(r["chrom"], r["pos"], r["ref"], r["alt"]) for r in rows},
        "rs6662198_covered": bool(anchor_keys) and all(key in {canonical(r["chrom"], r["pos"], r["ref"], r["alt"]) for r in rows} for key in anchor_keys),
        "all_source_cs_members_covered": all(cs_counts_covered.get(k, 0) == v for k, v in cs_counts.items()),
        "each_source_cs_pip_mass_fraction_ge_0_95": all(
            cs_covered.get(k, 0.0) / v >= 0.95 for k, v in cs_totals.items() if v > 0
        ),
    }
    metrics = {
        "release": release,
        "qtl_unique_variants": len(qtl),
        "gwas_regional_variants": len(gwas),
        "harmonized_variants": len(rows),
        "overlap_fraction_qtl": len(rows) / len(qtl) if qtl else 0,
        "exact_matches": exact,
        "reverse_allele_pairs_excluded": reverse_allele_pairs_excluded,
        "af_median_abs_diff": percentile(af_diffs, 0.5),
        "af_p95_abs_diff": percentile(af_diffs, 0.95),
        "qtl_span": [min((k[1] for k in qtl), default=None), max((k[1] for k in qtl), default=None)],
        "gwas_lead": {"key": key_text(lead_key), **gwas[lead_key]},
        "source_cs": {
            key: {
                "member_count": cs_counts[key],
                "covered_count": cs_counts_covered.get(key, 0),
                "pip_mass": cs_totals[key],
                "covered_pip_mass": cs_covered.get(key, 0.0),
                "covered_pip_fraction": cs_covered.get(key, 0.0) / cs_totals[key],
            }
            for key in sorted(cs_totals)
        },
        "checks": checks,
        "status": "PASS_COVERAGE_READY_FOR_CLASSIC_COLOC" if all(checks.values()) else "HOLD_COVERAGE",
        "case_control": RELEASE_METADATA[release],
    }
    return rows, metrics


def write_tsv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing to write empty harmonization: {path}")
    temporary = path.with_name(path.name + ".part")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qtl", type=Path, required=True)
    parser.add_argument("--cs", type=Path, required=True)
    parser.add_argument("--r12", type=Path, required=True)
    parser.add_argument("--r13", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    qtl, qtl_meta = load_qtl(args.qtl)
    cs, cs_meta = load_cs(args.cs)
    result = {
        "schema_version": "CMM_R4A12FG4_HARMONIZATION_GATE_1.0",
        "build": "GRCh38",
        "effect_alleles": {"TenK10K": "Allele2", "FinnGen": "ALT"},
        "qtl": {"path": str(args.qtl), **qtl_meta},
        "credible_sets": {"path": str(args.cs), **cs_meta},
        "releases": {},
    }
    for release, path in (("R12", args.r12), ("R13", args.r13)):
        gwas, gwas_meta = load_gwas(path)
        rows, metrics = harmonize_release(release, qtl, gwas, cs)
        output = args.outdir / f"{release}_M13_SYSTSLCE_x_TenK10K_NK_IL12RB2_harmonized.tsv"
        write_tsv(output, rows)
        result["releases"][release] = {
            "gwas": {"path": str(path), **gwas_meta},
            "harmonization": metrics,
            "output": str(output),
            "output_sha256": sha256_file(output),
        }
    result["status"] = (
        "PASS_SUMMARY_INPUT_READY_FOR_CLASSIC_COLOC"
        if all(
            item["harmonization"]["status"] == "PASS_COVERAGE_READY_FOR_CLASSIC_COLOC"
            for item in result["releases"].values()
        )
        else "HOLD_COVERAGE"
    )
    result["interpretation_limit"] = (
        "This gate validates summary inputs only. It is not colocalization and cannot upgrade C1."
    )
    output = args.outdir / "R4A12FG4_harmonization_gate.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(output)}, ensure_ascii=False, indent=2))
    return 0 if result["status"].startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
