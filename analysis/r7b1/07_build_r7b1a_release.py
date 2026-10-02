#!/usr/bin/env python3
"""Build and verify the lightweight R7B1A release."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1")).resolve()
BUILD = (ROOT / "6_release/current/R7B1A").resolve()
DOWNLOADS = Path(r"C:\Users\Administrator\Downloads")
ZIP_PATH = DOWNLOADS / "CMM_R7B1A_PBCwide_ABF_TriggerFreeze_2026-10-03.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy_file(source: Path, relative: str) -> None:
    destination = BUILD / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree_files(source: Path, relative: str, pattern: str = "*") -> None:
    for path in sorted(source.glob(pattern)):
        if path.is_file():
            copy_file(path, str(Path(relative) / path.name))


def main() -> None:
    if ROOT not in BUILD.parents:
        raise RuntimeError("release path escaped workspace")
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    copy_tree_files(ROOT / "7.Report/rounds/R7B1A", "reports", "*.md")
    copy_tree_files(ROOT / "2_code/06_intake/r7b1", "code", "*.py")
    copy_tree_files(ROOT / "2_code/06_intake/r7b1", "code", "*.ps1")
    copy_file(ROOT / "0_admin/protocols/R7B1/R7B1_PBCwide_eligibility_and_ABF_protocol_v1.md", "protocols/R7B1_PBCwide_eligibility_and_ABF_protocol_v1.md")
    copy_file(ROOT / "0_admin/protocols/R7B1B/R7B1B_exact_trigger_multisignal_protocol_v1.md", "protocols/R7B1B_exact_trigger_multisignal_protocol_v1.md")

    qtl_root = ROOT / "3_results/03_qtl/R7B1"
    for name in [
        "R7B1_frozen_locus_gene_universe.tsv",
        "R7B1_frozen_comparison_universe.tsv",
        "R7B1_OneK_topQTL_member_receipts.tsv",
        "R7B1_gene_TSS_consistency_audit.tsv",
        "R7B1_eligibility_state.json",
    ]:
        copy_file(qtl_root / name, f"results/eligibility/{name}")
    copy_tree_files(qtl_root / "pf10_trigger_qtl", "results/pf10_trigger_qtl", "*.tsv.gz")

    gwas_root = ROOT / "3_results/01_gwas/R7B1"
    for name in ["R7B1_PBC56_harmonization_manifest.tsv", "R7B1_PBC56_harmonization_state.json"]:
        copy_file(gwas_root / name, f"results/harmonization/{name}")

    integration = ROOT / "3_results/04_integration/R7B1"
    copy_tree_files(integration, "results/abf", "*")
    copy_tree_files(ROOT / "3_results/00_audit/R7B1A", "audit/R7B1A", "*")
    copy_tree_files(ROOT / "3_results/00_audit/R7B1B", "audit/R7B1B_freeze", "*")
    copy_file(ROOT / "3_results/04_integration/R7B0A/current_release_dualmodel/R7B0A_state.json", "audit/R7B0A/R7B0A_state.json")
    copy_file(ROOT / "3_results/04_integration/R7B0A/current_release_dualmodel/R7B0A_current_release_reclassification.tsv", "audit/R7B0A/R7B0A_current_release_reclassification.tsv")

    known = {
        "1_data/gwas/R7A1A/PBC/GCST90061440_buildGRCh37.tsv": "439aa72c59b876236de2b8172c443a447cefa6868ace535183cec8b758a05921",
        "1_data/qtl/OneK1K/OneK1K_pseudobulk_mean_mx.zip": "92b38f54e1dd77cdac6d1c814db30ff0e83eaff209825f020839402b90e027e5",
        "1_data/qtl/OneK1K/OneK1K_pseudobulk_mx_gene_list.zip": "68757fb2c571da1c4a123aa9d8ee22ae30e75661960d81d7daadac78c467f407",
        "1_data/qtl/OneK1K/updated_covariates_OneK1K_980_donors.zip": "d1f97568bd0836dd2434f71f79b6f3a027498083d0de71043f1915ba1f24a838",
        "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bed": "75a2ebd613b9c63b7a283722180aeef871d08490cb75ba1bce52deec6a19eb63",
        "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim": "6e28edad34d5930ca99f7be873e4684a885e26433d13ddba3d970bb8f8ad0bb6",
        "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.fam": "774c0c1c7491e892520c5c645fd790ba6f7ee0204467260fcf6088b68eb428ad",
    }
    large_rows = []
    for relative, digest in known.items():
        path = ROOT / relative
        large_rows.append({"resource": relative, "bytes": path.stat().st_size, "sha256": digest, "included": False, "reason": "third-party large source input"})
    large_rows.append(
        {
            "resource": "https://www.staff.ncl.ac.uk/heather.cordell/GJOKA_SUMSTATS.zip",
            "bytes": 1184054519,
            "sha256": "NOT_DOWNLOADED_FULL_ARCHIVE",
            "included": False,
            "reason": "R7B1B range-fetches only the frozen 50 required members",
        }
    )
    pd.DataFrame(large_rows).to_csv(BUILD / "LARGE_FILE_MANIFEST.tsv", sep="\t", index=False)
    readme = """# CMM R7B1A lightweight release

This release freezes the R7B0A current-model gate, the result-blind PBC-wide
comparison universe, the 6,923-comparison current PF10 ABF screen, the exact
184-comparison R7B1B trigger workload, independent QA, protocols, code, and
small derived QTL summaries. Large third-party GWAS, OneK donor genotype,
pseudobulk, covariate and GJOKA LD files are excluded and identified in
`LARGE_FILE_MANIFEST.tsv`.

Scientific status: ABF triggers are a multi-signal workload, not final
colocalization positives. R7B1B must classify all 184 comparisons before the
PBC-wide benchmark can be interpreted.
"""
    (BUILD / "README.md").write_text(readme, encoding="utf-8")
    package_state = {
        "schema": "R7B1A_LIGHTWEIGHT_RELEASE_1.0",
        "status": "COMPLETE_R7B1A_PENDING_R7B1B_MULTISIGNAL",
        "frozen_comparisons": 6923,
        "trigger_comparisons": 184,
        "large_third_party_inputs_included": False,
    }
    (BUILD / "PACKAGE_STATE.json").write_text(json.dumps(package_state, indent=2), encoding="utf-8")

    files = sorted(path for path in BUILD.rglob("*") if path.is_file() and path.name != "checksums.sha256")
    checksum_lines = [f"{sha256(path)}  {path.relative_to(BUILD).as_posix()}" for path in files]
    (BUILD / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in BUILD.rglob("*") if p.is_file()):
            archive.write(path, path.relative_to(BUILD).as_posix())
    with zipfile.ZipFile(ZIP_PATH) as archive:
        bad = archive.testzip()
        entries = len(archive.infolist())
    if bad is not None:
        raise RuntimeError(f"ZIP CRC failure: {bad}")
    digest = sha256(ZIP_PATH)
    sidecar = ZIP_PATH.with_suffix(ZIP_PATH.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {ZIP_PATH.name}\n", encoding="utf-8")
    state = {
        "status": "PASS",
        "release_directory": str(BUILD),
        "zip": str(ZIP_PATH),
        "zip_sha256": digest,
        "zip_entries": entries,
        "internal_checksums": len(checksum_lines),
        "zip_bytes": ZIP_PATH.stat().st_size,
    }
    ZIP_PATH.with_suffix(".zip.state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
