#!/usr/bin/env python3
"""Freeze the disease-side sample-size convention used by the R7B pipeline.

This is a source-identity audit.  It does not refit SuSiE or change the
author-approved R7B4B2 baseline.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011"
REPO = ROOT / "github/igan-open-regulatory-evidence"
OUT = WORK / "results"
EXT = WORK / "external_metadata"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    scripts = [
        REPO / "analysis/r7b1b_v2/11_run_r7b1b_v2_multisignal_locus.R",
        ROOT / "2_code/06_intake/r7b1/11_run_r7b1b_v2_multisignal_locus.R",
    ]
    scripts = [p for p in scripts if p.exists()]
    hits = []
    for path in scripts:
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), 1):
            if re.search(r"susie_rss|n\s*=\s*24510", line):
                hits.append({"path": str(path), "line": line_no, "text": line.strip()})

    pmc = EXT / "gjoka_pmc.html"
    official = EXT / "gjoka_official.html"
    soup = BeautifulSoup(pmc.read_text(encoding="utf-8", errors="replace"), "html.parser")
    plain = " ".join(soup.get_text(" ", strip=True).split())
    source_checks = {
        "reports_total_sample_size_24510": "24,510" in plain,
        "reports_case_count_8021": "8,021" in plain or "8021 cases" in plain,
        "reports_control_count_16489": "16,489" in plain,
        "reports_logistic_regression": "logistic regression" in plain.lower(),
        "reports_study_correlation_matrix": "correlation matrix for each locus" in plain.lower(),
        "reports_susie_rss": "susie" in plain.lower() and "summary statistics" in plain.lower(),
    }
    official_text = " ".join(
        BeautifulSoup(official.read_text(encoding="utf-8", errors="replace"), "html.parser")
        .get_text(" ", strip=True)
        .split()
    )
    source_checks["official_page_exposes_gjoka_sumstats"] = "GJOKA_SUMSTATS.zip" in official_text

    result = {
        "stage": "R7C0_G1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "question": "Is n=24510 a source-incompatible disease-side SuSiE-RSS input?",
        "source_counts": {"cases": 8021, "controls": 16489, "total": 24510},
        "alternate_balanced_case_control_neff": 4 * 8021 * 16489 / 24510,
        "source_checks": source_checks,
        "pipeline_hits": hits,
        "source_files": [
            {"path": str(pmc), "sha256": sha256(pmc), "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11656035/"},
            {"path": str(official), "sha256": sha256(official), "url": "https://www.staff.ncl.ac.uk/heather.cordell/GjokaPaper.html"},
        ],
        "adjudication": "PASS_SOURCE_MATCHED_N_TOTAL",
        "reason": (
            "The upstream study reports 24,510 participants (8,021 cases and 16,489 controls), "
            "PLINK logistic-regression coefficients/standard errors, and an in-sample correlation "
            "matrix from the same European data; the local pipeline uses the matching GJOKA z/LD "
            "pair and n=24,510 in susie_rss. The alternative balanced case-control N_eff is a "
            "different convention, not evidence that the implemented source-matched convention is erroneous."
        ),
        "action": "NO_642_RERUN; RETIRE_NEFF_REPLACEMENT_UNLESS_NEW_SOURCE_EVIDENCE",
    }
    if not all(source_checks.values()):
        raise RuntimeError(f"Required source statement missing: {source_checks}")
    if not any("n=24510" in h["text"].replace(" ", "") for h in hits):
        raise RuntimeError("No local susie_rss n=24510 implementation hit found")
    (OUT / "R7C0_G1_GJOKA_sample_size_adjudication.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({k: result[k] for k in ["adjudication", "action", "alternate_balanced_case_control_neff"]}, indent=2))


if __name__ == "__main__":
    main()
