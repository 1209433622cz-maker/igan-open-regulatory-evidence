#!/usr/bin/env python3
"""Assemble the compact, public-safe R7C1 external-validation supplement."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_manuscript/R7C1_IL12RB2_ExternalValidation_ManuscriptFork"
SOURCE = ROOT / "5_analysis/R7C0_SourceIdentity_ExternalEvidence_Preflight_20261011/results"
STAGE = WORK / "supplement/R7C1_External_Validation_Data"
OUT = WORK / "supplement/Additional_file_3_R7C1_External_Validation_Data.zip"

FILES = [
    "R7C0_G1_GJOKA_sample_size_adjudication.json",
    "R7C0_FinnGen_R12_R13_IL12RB2_CS_members.tsv",
    "R7C0_FinnGen_R12_R13_IL12RB2_signal_identity.json",
    "R7C0_FinnGenR13_x_OneK_IL12RB2_external_coloc_state.json",
    "R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv",
    "R7C0_GJOKA_FinnGenR13_independent_replication_adjudication.json",
    "R7C0_GJOKA_FinnGenR13_rs6679356_replication.tsv",
    "R7C0_OneK_NK_IL12RB2_CS_in_FinnGenR13_disease_CS.tsv",
    "R7C0_frozen_92_receipt.json",
    "R7C0_frozen_92_stableH4_comparisons.tsv",
    "R7C0_CASCADE_27gene_coverage.tsv",
    "R7C0_CASCADE_27gene_coverage_summary.json",
    "R7C0_CASCADE_PBC_coloc_in_fixed_27genes.tsv",
    "R7C0_CASCADE_API_receipts.tsv",
    "R7C0_IL12RB2_NK_disease_eQTL_caQTL_edges.tsv",
    "R7C0_IL12RB2_chromatin_triangle_adjudication.json",
    "R7C0_OMIX001122_spatial_sample_QC.tsv",
    "R7C0_OMIX001122_27gene_spatial_detectability.tsv",
    "R7C0_OMIX001122_spatial_adjudication.json",
    "R7C0_source_ledger.tsv",
    "R7C0_final_state.json",
    "R7C0_independent_QA.tsv",
    "R7C0_independent_QA.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    (STAGE / "data").mkdir(parents=True, exist_ok=True)
    for name in FILES:
        src = SOURCE / name
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, STAGE / "data" / name)

    readme = """# Additional file 3: R7C1 external validation data

This archive contains compact derived tables and adjudication records for the
prespecified IL12RB2-NK external-validation module.

The module evaluates:

1. FinnGen R12/R13 disease credible-set stability;
2. FinnGen R13 disease statistics against the frozen OneK NK/IL12RB2 eQTL;
3. source credible-set overlap;
4. a prespecified 27-gene CASCADE coverage audit;
5. PBC-disease/eQTL and PBC-disease/caQTL sharing at a linked IL12RB2 peak;
6. descriptive OMIX001122 target-gene detectability.

Interpretive boundaries:

- FinnGen R13 is a different disease study system; person-level zero overlap
  with the discovery GWAS has not been demonstrated.
- The external disease/eQTL analysis is single-causal and includes a source-CS
  audit. It is not a second source-LD multi-signal fit.
- A direct eQTL-caQTL posterior and a causal mediation estimate are unavailable.
- OMIX001122 contains one PBC and one control matrix in the public processed
  archive and is descriptive rather than an independent spatial replication.
- Third-party source archives, genotypes and individual-level data are not
  redistributed.
"""
    (STAGE / "README.md").write_text(readme, encoding="utf-8")

    manifest_lines = ["sha256\tbytes\tpath"]
    for path in sorted(STAGE.rglob("*")):
        if path.is_file() and path.name != "checksums.sha256.tsv":
            manifest_lines.append(f"{sha256(path)}\t{path.stat().st_size}\t{path.relative_to(STAGE).as_posix()}")
    (STAGE / "checksums.sha256.tsv").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(STAGE.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(STAGE).as_posix())
    print(f"{OUT}\nsha256={sha256(OUT)}\nfiles={len(FILES) + 2}")


if __name__ == "__main__":
    main()
