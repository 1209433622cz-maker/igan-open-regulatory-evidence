#!/usr/bin/env python3
"""Validate the public OneK1K PLINK archive and MG lead-variant coverage."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import pathlib
import zipfile
from collections import Counter
from datetime import datetime, timezone


ROOT = pathlib.Path(r"H:\SCI2\YR1")
ARCHIVE = ROOT / "1_data" / "qtl" / "OneK1K" / "plink_genotype_merged_980_donors.zip"
AUDIT = ROOT / "3_results" / "00_audit" / "R5A1"
RESULTS = ROOT / "3_results" / "03_qtl" / "R5A1"
EXPECTED_MD5 = "be1053e34fa023bc808388d4e0bf2aa1"
LEADS = {
    "rs2476601": {"chrom": "1", "GRCh37": 114_377_568, "GRCh38": 113_834_946},
    "rs7596255": {"chrom": "2", "GRCh37": 39_379_926, "GRCh38": 39_152_785},
    "rs6861227": {"chrom": "5", "GRCh37": 150_447_128, "GRCh38": 151_067_567},
    "rs7239261": {"chrom": "18", "GRCh37": 60_005_046, "GRCh38": 62_337_813},
}


def digest(path: pathlib.Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    actual_md5 = digest(ARCHIVE, "md5")
    actual_sha256 = digest(ARCHIVE, "sha256")
    matches: list[dict[str, object]] = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        members = [n for n in archive.namelist() if not n.endswith("/")]
        # Finder metadata in ``__MACOSX/._*`` are AppleDouble resource forks,
        # not a second PLINK dataset. Keep them in the archive inventory and
        # CRC test, but exclude them from the scientific member selection.
        data_members = [
            n for n in members
            if not n.startswith("__MACOSX/") and not pathlib.PurePosixPath(n).name.startswith("._")
        ]
        ignored_metadata_members = sorted(set(members) - set(data_members))
        bim_members = [n for n in data_members if n.lower().endswith(".bim")]
        fam_members = [n for n in data_members if n.lower().endswith(".fam")]
        bed_members = [n for n in data_members if n.lower().endswith(".bed")]
        if len(bim_members) != 1 or len(fam_members) != 1 or len(bed_members) != 1:
            raise RuntimeError(f"Expected one BED/BIM/FAM set; found {members}")
        bad_member = archive.testzip()
        fam_rows = 0
        with archive.open(fam_members[0]) as raw, io.TextIOWrapper(raw, encoding="utf-8") as text:
            for line in text:
                if line.strip():
                    fam_rows += 1
        with archive.open(bed_members[0]) as bed:
            bed_magic = bed.read(3).hex()
        variant_rows = 0
        chromosome_counts: Counter[str] = Counter()
        wanted_positions = {
            (spec["chrom"], spec[build]): (rsid, build)
            for rsid, spec in LEADS.items()
            for build in ("GRCh37", "GRCh38")
        }
        with archive.open(bim_members[0]) as raw, io.TextIOWrapper(raw, encoding="utf-8") as text:
            for line in text:
                parts = line.rstrip("\r\n").split()
                if len(parts) != 6:
                    continue
                chrom, variant_id, cm, pos_text, a1, a2 = parts
                pos = int(pos_text)
                variant_rows += 1
                chromosome_counts[chrom] += 1
                position_match = wanted_positions.get((chrom.removeprefix("chr"), pos))
                rsid_match = variant_id if variant_id in LEADS else None
                if position_match or rsid_match:
                    target_rsid, coordinate_match = position_match or (rsid_match, "RSID_ONLY")
                    matches.append(
                        {
                            "target_rsid": target_rsid,
                            "chromosome": chrom,
                            "position": pos,
                            "variant_id_in_bim": variant_id,
                            "A1_effect_allele_for_OneK1K_summary": a1,
                            "A2": a2,
                            "coordinate_match": coordinate_match,
                        }
                    )
    grch37_targets = {str(x["target_rsid"]) for x in matches if x["coordinate_match"] == "GRCh37"}
    grch38_targets = {str(x["target_rsid"]) for x in matches if x["coordinate_match"] == "GRCh38"}
    if len(grch37_targets) >= 3 and not grch38_targets:
        build = "GRCh37"
    elif len(grch38_targets) >= 3 and not grch37_targets:
        build = "GRCh38"
    else:
        build = "UNRESOLVED"
    output = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "path": str(ARCHIVE),
        "bytes": ARCHIVE.stat().st_size,
        "md5": actual_md5,
        "expected_md5": EXPECTED_MD5,
        "md5_pass": actual_md5 == EXPECTED_MD5,
        "sha256": actual_sha256,
        "zip_crc_pass": bad_member is None,
        "members": members,
        "scientific_data_members": data_members,
        "ignored_archive_metadata_members": ignored_metadata_members,
        "fam_donors": fam_rows,
        "fam_980_pass": fam_rows == 980,
        "bed_magic_hex": bed_magic,
        "bed_snp_major_magic_pass": bed_magic == "6c1b01",
        "bim_variant_rows": variant_rows,
        "chromosome_counts": dict(sorted(chromosome_counts.items())),
        "lead_matches": matches,
        "lead_targets_with_grch37_position": sorted(grch37_targets),
        "lead_targets_with_grch38_position": sorted(grch38_targets),
        "coordinate_build_inference": build,
        "all_four_mg_leads_present": grch37_targets == set(LEADS) or grch38_targets == set(LEADS),
    }
    output["intake_pass"] = bool(
        output["md5_pass"]
        and output["zip_crc_pass"]
        and output["fam_980_pass"]
        and output["bed_snp_major_magic_pass"]
        and output["coordinate_build_inference"] in {"GRCh37", "GRCh38"}
    )
    with (AUDIT / "OneK1K_genotype_intake_audit.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    with (RESULTS / "OneK1K_MG_lead_variant_coverage.tsv").open("w", encoding="utf-8", newline="") as handle:
        fields = list(matches[0]) if matches else ["target_rsid"]
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(matches)
    print(json.dumps({key: output[key] for key in ("md5_pass", "zip_crc_pass", "fam_donors", "bim_variant_rows", "coordinate_build_inference", "all_four_mg_leads_present", "intake_pass")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
