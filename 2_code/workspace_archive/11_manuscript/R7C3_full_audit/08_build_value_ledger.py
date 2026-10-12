#!/usr/bin/env python3
"""Curate the evidence, reusable method and governance assets retained after R7C3."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "5_analysis" / "R7C3_FullWorkspaceAudit_2026-10-11" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

ASSETS = [
    ("CURRENT_PAPER", "SUBMISSION", "5_manuscript/R7C2_Q1_JournalRealityCheck_DualTrackSubmission/manuscript/R7C2_npj_Genomic_Medicine_manuscript.docx", "Current npj Genomic Medicine manuscript; WPS-verified scientific text", "PUBLIC_DERIVED"),
    ("CURRENT_PAPER", "SUBMISSION", "5_manuscript/R7C2_Q1_JournalRealityCheck_DualTrackSubmission/cover_letter/R7C2_npj_Genomic_Medicine_cover_letter.docx", "Current npj cover letter", "PUBLIC_DERIVED"),
    ("CURRENT_PAPER", "SUBMISSION", "5_manuscript/R7C2_Q1_JournalRealityCheck_DualTrackSubmission/figures", "Six journal figures in PDF/PNG/SVG", "PUBLIC_DERIVED"),
    ("CURRENT_PAPER", "SUBMISSION", "5_manuscript/R7C2_Q1_JournalRealityCheck_DualTrackSubmission/supplement", "Supplementary guide, tables and machine-readable source-data archives", "PUBLIC_DERIVED"),
    ("CURRENT_PAPER", "FALLBACK", "5_manuscript/R7B4B_FinalSubmissionCandidate", "Frozen Human Genomics fallback package", "LOCAL_SUBMISSION"),
    ("PBC_CORE", "DISEASE_INPUT", "1_data/gwas/R7A1A/PBC/GCST90061440_buildGRCh37.tsv", "Primary European PBC GWAS, 8,021 cases and 16,489 controls", "THIRD_PARTY_NO_REUPLOAD"),
    ("PBC_CORE", "DISEASE_LD", "1_data/study_inputs/PBC_GJOKA/R7B1B_v2", "47 downloaded GJOKA region LD/statistic pairs supporting source-matched multi-signal analysis", "THIRD_PARTY_NO_REUPLOAD"),
    ("PBC_CORE", "QTL_INPUT", "1_data/qtl/OneK1K/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz", "Full OneK1K cis-eQTL source archive", "THIRD_PARTY_NO_REUPLOAD"),
    ("PBC_CORE", "QTL_LD", "1_data/qtl/OneK1K/plink_merged_980_donors", "OneK1K genotype BED/BIM/FAM for cell-specific source-LD reconstruction", "THIRD_PARTY_NO_REUPLOAD"),
    ("PBC_CORE", "QTL_REPLICATION", "1_data/qtl/eqtl/tenk10k/raw/susie_summary.zip", "TenK10K source credible sets used for bounded molecular-QTL replication", "THIRD_PARTY_NO_REUPLOAD"),
    ("PBC_CORE", "ABF_UNIVERSE", "3_results/03_qtl/R7B1/R7B1_frozen_comparison_universe.tsv", "Frozen 6,923 locus-gene-cell comparison universe", "PUBLIC_DERIVED"),
    ("PBC_CORE", "MULTISIGNAL", "3_results/04_integration/R7B1B_v2/adjudication/R7B1B_v2_642_bidirectional_reclassification.tsv", "Complete 642-comparison multi-signal reclassification ledger", "PUBLIC_DERIVED"),
    ("PBC_CORE", "SIGNAL_SEMANTICS", "3_results/04_integration/R7B1E0/signal_semantics/R7B1E0_signal_semantics_642.tsv", "Cross-L signal-pair identity and coexistence audit", "PUBLIC_DERIVED"),
    ("PBC_CORE", "MATCHED_INPUT", "3_results/04_integration/R7B2A/adjudication/R7B2A_642_four_arm_trajectories.tsv", "A0/A1/A2/M same-input attribution trajectories", "PUBLIC_DERIVED"),
    ("PBC_CORE", "SIMULATION", "3_results/05_simulation/R7B1C/aggregate", "486-grid, 486,000-replicate truth-known simulation aggregate", "PUBLIC_DERIVED"),
    ("PBC_CORE", "EXTERNAL_VALIDATION", "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011/results", "FinnGen R13 IL12RB2-NK, CASCADE chromatin and OMIX boundary outputs", "PUBLIC_DERIVED"),
    ("METHOD_LIBRARY", "CODE", "2_code/06_intake/r7b1", "642-comparison source-LD and coloc.susie execution pipeline", "PUBLIC_CODE"),
    ("METHOD_LIBRARY", "CODE", "2_code/06_intake/r7b1c", "Truth-known simulation implementation", "PUBLIC_CODE"),
    ("METHOD_LIBRARY", "CODE", "2_code/06_intake/r7b2a", "Matched-input A0/A1/A2/M attribution pipeline", "PUBLIC_CODE"),
    ("METHOD_LIBRARY", "CODE", "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011/code", "External disease-study and chromatin-triangle bounded validation", "PUBLIC_CODE"),
    ("METHOD_LIBRARY", "GOVERNANCE", "0_admin/protocols", "Frozen protocols, stopping rules and no-fishing governance", "REVIEW_BEFORE_PUBLIC"),
    ("METHOD_LIBRARY", "LEGACY_REUSE", "2_code/06_intake", "Cross-project harmonization, download, LD, QTL and validation engineering accumulated from SSc, MG, IgAN and PBC", "REVIEW_BEFORE_PUBLIC"),
    ("PROJECT_MEMORY", "ACTION_RECORDS", "7.Report/rounds", "Canonical stage-by-stage work records and decisions", "REVIEW_BEFORE_PUBLIC"),
    ("PROJECT_MEMORY", "PLANS", "9.Version/PBC_研究计划书_RP_v4_20261011.docx", "Current RP v4 dual-track research plan", "LOCAL_GOVERNANCE"),
    ("PROJECT_MEMORY", "VERSIONS", "9.Version", "Historical snapshots and rollback assets", "LOCAL_ARCHIVE"),
    ("PUBLIC_IDENTITY", "GITHUB", "github/igan-open-regulatory-evidence", "Public code, aggregate outputs, manuscript and provenance repository", "PUBLIC_REPOSITORY"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


rows = []
missing = []
for group, role, rel, value, public in ASSETS:
    p = ROOT / rel
    if p.is_file():
        count, size, digest, kind = 1, p.stat().st_size, sha256(p), "FILE"
    elif p.is_dir():
        files = [x for x in p.rglob("*") if x.is_file() and ".git" not in x.parts]
        count, size, digest, kind = len(files), sum(x.stat().st_size for x in files), "DIRECTORY_SEE_FILE_MANIFEST", "DIRECTORY"
    else:
        count, size, digest, kind = 0, 0, "MISSING", "MISSING"
        missing.append(rel)
    rows.append({
        "asset_group": group, "role": role, "relative_path": rel, "kind": kind,
        "file_count": count, "size_bytes": size, "size_gib": f"{size/1024**3:.6f}",
        "sha256_or_receipt": digest, "value_and_future_use": value, "publication_boundary": public,
    })

with (OUT / "R7C3_high_value_asset_ledger.tsv").open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
state = {"assets": len(rows), "missing": missing, "groups": sorted({x["asset_group"] for x in rows})}
(OUT / "R7C3_high_value_asset_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(state, ensure_ascii=False, indent=2))
