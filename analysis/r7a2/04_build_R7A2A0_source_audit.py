#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
MANIFEST = ROOT / "1_data/scrna/PBC/HRA008003/manifests/HRA008003_control_liver_primary_run_manifest_v1.tsv"
AUDIT = ROOT / "3_results/00_audit"
OUT = AUDIT / "R7A2A0_control_source_audit.json"


def table_values(path: Path) -> dict[str, str]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    values: dict[str, str] = {}
    for row in soup.select("table.table-left tr"):
        cells = row.find_all(["th", "td"], recursive=False)
        if len(cells) >= 2:
            values[cells[0].get_text(" ", strip=True).rstrip(":")] = cells[1].get_text(" ", strip=True)
    return values


with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))
evidence = []
errors = []
for row in rows:
    run = row["run_accession"]
    sample = row["sample_accession"]
    run_page = AUDIT / f"R7A2A0_{run}_runDetail.html"
    sample_page = AUDIT / f"R7A2A0_{sample}_sampleDetail.html"
    if not run_page.exists() or not sample_page.exists():
        errors.append(f"missing cached official page for {run}/{sample}")
        continue
    run_values = table_values(run_page)
    sample_values = table_values(sample_page)
    expected_name = row["donor_label"]
    checks = {
        "run_accession": run_values.get("Accession") == run,
        "sample_accession": run_values.get("Sample") == sample,
        "sample_name": sample_values.get("Sample name") == expected_name,
        "tissue": sample_values.get("Tissue", "").lower() == "liver",
        "control_title": "hemangioma" in sample_values.get("Sample title", "").lower(),
        "file_name": f"{run}.bam" in run_page.read_text(encoding="utf-8"),
    }
    if not all(checks.values()):
        errors.append(f"{run}: official page mapping mismatch")
    evidence.append({
        "run": run,
        "sample": sample,
        "sample_name": sample_values.get("Sample name"),
        "sample_title": sample_values.get("Sample title"),
        "tissue": sample_values.get("Tissue"),
        "expected_bytes": int(row["expected_bytes"]),
        "official_md5": row["official_md5"],
        "checks": checks,
    })

output = {
    "schema": "R7A2A0_HRA008003_CONTROL_SOURCE_AUDIT_1.0",
    "source": "HRA008003 official run/sample pages and public directory",
    "runs": evidence,
    "total_expected_bytes": sum(row["expected_bytes"] for row in evidence),
    "errors": errors,
    "status": "PASS" if len(evidence) == 5 and not errors else "FAIL",
}
OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(output, ensure_ascii=False, indent=2))
raise SystemExit(0 if output["status"] == "PASS" else 2)
