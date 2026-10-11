#!/usr/bin/env python3
"""Byte, archive, schema, and MG lead audit for hum0197.v29.MG-gwas.v1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import zipfile
from collections import Counter
from datetime import datetime, timezone


ROOT = pathlib.Path(r"H:\SCI2\YR1")
SOURCE_DIR = ROOT / "1_data" / "gwas" / "MG" / "NBDC" / "hum0197.v29.MG-gwas.v1"
ARCHIVE = SOURCE_DIR / "hum0197.v29.MG-gwas.v1.zip"
DICTIONARY = SOURCE_DIR / "Dictionary_hum0197_v29.docx"
OUT_DIR = ROOT / "3_results" / "01_gwas" / "R5A2A"
EXPECTED_ZIP_BYTES = 229_751_515
EXPECTED_VARIANTS = 9_034_566
EXPECTED_HEADER = [
    "#CHR", "POS", "MarkerID", "Allele1", "Allele2", "AF_Allele2",
    "imputationInfo", "BETA", "SE", "p.value",
]
TARGETS = {
    ("1", 114_377_568): "rs2476601",
    ("2", 39_379_926): "rs7596255",
    ("5", 150_447_128): "rs6861227",
    ("18", 60_005_046): "rs7239261",
}


def file_hash(path: pathlib.Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.is_file() or not DICTIONARY.is_file():
        raise FileNotFoundError("NBDC archive or dictionary is missing")

    chromosome_counts: Counter[str] = Counter()
    errors: Counter[str] = Counter()
    target_rows: list[dict[str, object]] = []
    min_p = 1.0
    min_p_row: dict[str, object] | None = None
    inner_sha = hashlib.sha256()
    row_count = 0

    with zipfile.ZipFile(ARCHIVE) as archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        if len(members) != 1:
            raise RuntimeError(f"Expected one data member, found {len(members)}")
        member = members[0]
        crc_bad_member = archive.testzip()
        with archive.open(member) as stream:
            header_bytes = stream.readline()
            inner_sha.update(header_bytes)
            header = header_bytes.decode("utf-8").rstrip("\r\n").split("\t")
            for raw_line in stream:
                inner_sha.update(raw_line)
                row_count += 1
                fields = raw_line.decode("utf-8").rstrip("\r\n").split("\t")
                if len(fields) != 10:
                    errors["column_count"] += 1
                    continue
                chromosome, position_text, marker, allele1, allele2, af_text, info_text, beta_text, se_text, p_text = fields
                try:
                    position = int(position_text)
                    marker_fields = marker.split(":")
                    if len(marker_fields) != 4:
                        errors["marker_format"] += 1
                        continue
                    marker_chromosome, marker_position, marker_ref, marker_alt = marker_fields
                    if marker_chromosome != chromosome or int(marker_position) != position:
                        errors["marker_coordinate_mismatch"] += 1
                    if marker_ref.upper() != allele1.upper() or marker_alt.upper() != allele2.upper():
                        errors["marker_allele_mismatch"] += 1
                    if allele1.upper() == allele2.upper():
                        errors["identical_alleles"] += 1
                    af = float(af_text)
                    info = float(info_text)
                    beta = float(beta_text)
                    se = float(se_text)
                    p_value = float(p_text)
                    if not all(math.isfinite(value) for value in (af, info, beta, se, p_value)):
                        errors["nonfinite_numeric"] += 1
                    if not 0 <= af <= 1:
                        errors["af_out_of_range"] += 1
                    if not 0 <= info <= 1.00001:
                        errors["info_out_of_range"] += 1
                    if se <= 0:
                        errors["invalid_se"] += 1
                    if not 0 <= p_value <= 1:
                        errors["p_out_of_range"] += 1
                except (ValueError, UnicodeDecodeError):
                    errors["parse_error"] += 1
                    continue

                chromosome_counts[chromosome] += 1
                if p_value < min_p:
                    min_p = p_value
                    min_p_row = {
                        "chromosome": chromosome,
                        "position_hg19": position,
                        "marker_id": marker,
                        "reference_allele": allele1,
                        "alternate_effect_allele": allele2,
                        "effect_allele_frequency": af,
                        "imputation_info": info,
                        "beta_alt": beta,
                        "se": se,
                        "p": p_value,
                    }
                rsid = TARGETS.get((chromosome, position))
                if rsid:
                    target_rows.append(
                        {
                            "target_rsid": rsid,
                            "chromosome": chromosome,
                            "position_hg19": position,
                            "marker_id": marker,
                            "reference_allele": allele1,
                            "alternate_effect_allele": allele2,
                            "effect_allele_frequency": af,
                            "imputation_info": info,
                            "beta_alt": beta,
                            "se": se,
                            "p": p_value,
                        }
                    )

    target_ids = {str(row["target_rsid"]) for row in target_rows}
    audit = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "NBDC Human Database hum0197.v29.MG-gwas.v1",
        "source_url": "https://humandbs-production.ddbj.nig.ac.jp/en/research/hum0197/v29",
        "download_url": "https://humandbs-production.ddbj.nig.ac.jp/files/hum0197/hum0197.v29.MG-gwas.v1.zip",
        "access": "UNRESTRICTED",
        "population": "Japanese",
        "cases": 1434,
        "controls": 42913,
        "build": "hg19_GRCh37",
        "effect_definition": "Allele2 is ALT and the effect allele; BETA is its effect",
        "archive": {
            "path": str(ARCHIVE),
            "bytes": ARCHIVE.stat().st_size,
            "expected_http_content_length": EXPECTED_ZIP_BYTES,
            "byte_size_pass": ARCHIVE.stat().st_size == EXPECTED_ZIP_BYTES,
            "sha256": file_hash(ARCHIVE, "sha256"),
            "md5": file_hash(ARCHIVE, "md5"),
            "zip_crc_pass": crc_bad_member is None,
            "member": member.filename,
            "member_uncompressed_bytes": member.file_size,
            "member_crc32": f"{member.CRC:08x}",
            "member_sha256": inner_sha.hexdigest(),
        },
        "dictionary": {
            "path": str(DICTIONARY),
            "bytes": DICTIONARY.stat().st_size,
            "sha256": file_hash(DICTIONARY, "sha256"),
        },
        "header": header,
        "header_exact": header == EXPECTED_HEADER,
        "variant_rows": row_count,
        "expected_variant_rows": EXPECTED_VARIANTS,
        "row_count_pass": row_count == EXPECTED_VARIANTS,
        "chromosome_counts": dict(chromosome_counts),
        "error_counts": dict(errors),
        "minimum_p": min_p,
        "minimum_p_row": min_p_row,
        "target_rows": target_rows,
        "targets_found": sorted(target_ids),
        "targets_missing": sorted(set(TARGETS.values()) - target_ids),
    }
    audit["content_pass"] = bool(
        audit["archive"]["byte_size_pass"]
        and audit["archive"]["zip_crc_pass"]
        and audit["header_exact"]
        and audit["row_count_pass"]
        and not errors
    )
    (OUT_DIR / "Japanese_MG_GWAS_intake_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    target_fields = [
        "target_rsid", "chromosome", "position_hg19", "marker_id", "reference_allele",
        "alternate_effect_allele", "effect_allele_frequency", "imputation_info",
        "beta_alt", "se", "p",
    ]
    with (OUT_DIR / "Japanese_MG_four_target_variants.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=target_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(target_rows)
    print(json.dumps({
        "content_pass": audit["content_pass"],
        "variant_rows": row_count,
        "minimum_p": min_p,
        "targets_found": audit["targets_found"],
        "targets_missing": audit["targets_missing"],
    }, ensure_ascii=False, indent=2))
    return 0 if audit["content_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
