#!/usr/bin/env python3
"""Convert MG GEO family SOFT metadata into a reproducible sample audit."""

from __future__ import annotations

import csv
import gzip
import json
import pathlib
from collections import Counter
from datetime import datetime, timezone


ROOT = pathlib.Path(r"H:\SCI2\YR1")
SOURCE = ROOT / "1_data" / "scrna" / "MG" / "R5A1_metadata"
OUTPUT = ROOT / "3_results" / "00_audit" / "R5A1"
ACCESSIONS = ["GSE297547", "GSE227835", "GSE233180"]


def parse_soft(path: pathlib.Path) -> tuple[dict[str, list[str]], list[dict[str, list[str]]]]:
    series: dict[str, list[str]] = {}
    samples: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] | None = None
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\r\n")
            if line.startswith("^SAMPLE = "):
                current = {"accession": [line.split("=", 1)[1].strip()]}
                samples.append(current)
                continue
            if not line.startswith("!") or " = " not in line:
                continue
            key, value = line[1:].split(" = ", 1)
            if current is None:
                if key.startswith("Series_"):
                    series.setdefault(key.removeprefix("Series_"), []).append(value)
            elif key.startswith("Sample_"):
                current.setdefault(key.removeprefix("Sample_"), []).append(value)
    return series, samples


def first(values: list[str] | None) -> str:
    return values[0] if values else ""


def role(acc: str, title: str, characteristics: str) -> str:
    text = f"{title} {characteristics}".lower()
    if acc == "GSE297547":
        if title.startswith("PBMC from C"):
            return "C_PREFIX_RNA_SAMPLE"
        if title.startswith("PBMC from MG"):
            return "MG_PREFIX_RNA_SAMPLE_TITLE_CONTAINS_CONTROL"
        if "vdj" in text:
            return "VDJ_INFORMATION_FILE"
    if "healthy control" in text:
        return "HEALTHY_CONTROL"
    if "achr-positive mg" in text:
        return "ACHR_POSITIVE_MG"
    if "seronegative mg pre-treatment" in text:
        return "SERONEGATIVE_MG_PRE_TREATMENT"
    if "seronegative mg post-treatment" in text:
        return "SERONEGATIVE_MG_POST_TREATMENT"
    if "early-onset myasthenia gravis" in text and "rna seq" in text:
        return "EOMG_THYMUS_SCRNA"
    if "early-onset myasthenia gravis" in text and "bcr" in text:
        return "EOMG_THYMUS_BCR"
    return "UNRESOLVED"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    table: list[dict[str, str]] = []
    summaries: dict[str, dict] = {}
    for acc in ACCESSIONS:
        path = SOURCE / f"{acc}_family.soft.gz"
        series, samples = parse_soft(path)
        roles: Counter[str] = Counter()
        for sample in samples:
            title = first(sample.get("title"))
            characteristics = "; ".join(sample.get("characteristics_ch1", []))
            sample_role = role(acc, title, characteristics)
            roles[sample_role] += 1
            table.append(
                {
                    "series": acc,
                    "sample": first(sample.get("accession")),
                    "title": title,
                    "source": first(sample.get("source_name_ch1")),
                    "characteristics": characteristics,
                    "library_strategy": first(sample.get("library_strategy")),
                    "supplementary_files": "; ".join(
                        value
                        for key, values in sample.items()
                        if key.startswith("supplementary_file")
                        for value in values
                    ),
                    "role_from_deposition": sample_role,
                }
            )
        summaries[acc] = {
            "title": first(series.get("title")),
            "summary": " ".join(series.get("summary", [])),
            "overall_design": " ".join(series.get("overall_design", [])),
            "sample_records": len(samples),
            "role_counts": dict(sorted(roles.items())),
            "series_supplementary_files": series.get("supplementary_file", []),
            "metadata_path": str(path),
        }
    out_tsv = OUTPUT / "MG_GEO_sample_manifest.tsv"
    with out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)
    output = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "series": summaries,
        "adjudication": {
            "GSE227835": "PASS_DISEASE_CONTROL_AND_PAIRED_TREATMENT_METADATA",
            "GSE233180": "PASS_EOMG_DISEASE_STATE_LOCALIZATION_ONLY_NO_HEALTHY_CONTROL",
            "GSE297547": "PASS_PUBLIC_RNA_ABSEQ_RESOURCE_WITH_LABEL_ANOMALY_REQUIRING_PUBLICATION_OR_SAMPLE_MAP",
        },
    }
    with (OUTPUT / "MG_GEO_metadata_audit.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(output["adjudication"], ensure_ascii=False))


if __name__ == "__main__":
    main()
