#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import shutil
import zipfile
from pathlib import Path


FILES = [
    "README_WORKSPACE.md",
    "0_admin/protocol/current/project_portfolio_state_R7A1C1B2_R7A2A0.json",
    "0_admin/protocol/current/R7A2A0_PBC_manuscript_scale_architecture_v1.md",
    "1_data/scrna/PBC/HRA008003/manifests/HRA008003_PBC_liver_primary_run_manifest_v2.tsv",
    "1_data/scrna/PBC/HRA008003/manifests/HRA008003_control_liver_primary_run_manifest_v1.tsv",
    "1_data/scrna/PBC/HRA008003/manifests/R7A1C1B2_R7A2A0_large_asset_manifest.tsv",
    "2_code/06_intake/r7a1c1/00_hash_file_dual.py",
    "2_code/06_intake/r7a1c1/02_hra_bam_target_panel_v2.py",
    "2_code/06_intake/r7a1c1/03_adjudicate_HRA008003_liver_gate_v2.py",
    "2_code/06_intake/r7a1c1/08_check_HRA008003_bam_schema_v1_2.py",
    "2_code/06_intake/r7a1c1/11_validate_HRA008003_resume_state.py",
    "2_code/06_intake/r7a1c1/14_independent_QA_R7A1C1B2.py",
    "2_code/06_intake/r7a2/01_validate_HRA008003_control_manifest.py",
    "2_code/06_intake/r7a2/02_compare_PBC_control_target_panel.py",
    "2_code/06_intake/r7a2/03_test_R7A2A0_execution_pack.py",
    "2_code/06_intake/r7a2/04_build_R7A2A0_source_audit.py",
    "2_code/06_intake/r7a2/RUN_R7A2A1_HRA008003_CONTROL_TARGET_PANEL.ps1",
    "2_code/06_intake/r7a2/RUN_R7A2A1_README.md",
    "2_code/09_release/build_r7a1c1b2_r7a2a0_release.py",
    "3_results/00_audit/R7A1C1/R7A1C1_HRA008003_receipts_v2.tsv",
    "3_results/00_audit/R7A1C1/HRR1849462.bam_schema_preflight_v1_2.json",
    "3_results/00_audit/R7A1C1/HRR1849463.bam_schema_preflight_v1_2.json",
    "3_results/00_audit/R7A1C1B2_independent_final_adjudication.json",
    "3_results/00_audit/R7A1C1B2_independent_final_adjudication.tsv",
    "3_results/00_audit/R7A1C1B2_independent_QA.json",
    "3_results/00_audit/R7A1C1B2_five_donor_compact_summary.tsv",
    "3_results/00_audit/R7A2A0_control_manifest_preflight.json",
    "3_results/00_audit/R7A2A0_control_source_audit.json",
    "3_results/00_audit/R7A2A0_execution_pack_tests.json",
    "3_results/05_tissue/R7A1C1/HRR1849459_target_panel_summary.json",
    "3_results/05_tissue/R7A1C1/HRR1849460_target_panel_summary.json",
    "3_results/05_tissue/R7A1C1/HRR1849461_target_panel_summary.json",
    "3_results/05_tissue/R7A1C1/HRR1849462_target_panel_summary.json",
    "3_results/05_tissue/R7A1C1/HRR1849463_target_panel_summary.json",
    "3_results/05_tissue/R7A1C1/R7A1C1_liver_final_adjudication_v2.json",
    "3_results/05_tissue/R7A1C1/R7A1C1_liver_final_adjudication_v2.tsv",
    "7.Report/rounds/R7A1C1B2_R7A2A0/00_CMM_R7A1C1B2_执行摘要_PBC五供者终裁.md",
    "7.Report/rounds/R7A1C1B2_R7A2A0/01_CMM_R7A1C1B2_五供者独立复核与数据清理审计.md",
    "7.Report/rounds/R7A1C1B2_R7A2A0/02_CMM_R7A2A0_HRA008003对照来源与可执行性审计.md",
    "7.Report/rounds/R7A1C1B2_R7A2A0/03_CMM_R7A2A0_论文架构与R7A2A1冻结目标.md",
    "7.Report/rounds/R7A1C1B2_R7A2A0/99_CMM_R7A1C1B2_R7A2A0_详细行动记录_2026-09-28.md",
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 << 20), b""):
            value.update(block)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(r"H:\SCI2\YR1"))
    parser.add_argument("--name", default="CMM_R7A1C1B2_R7A2A0_PBC_FiveDonorClosure_ControlGate_2026-09-28")
    args = parser.parse_args()
    root = args.root.resolve()
    release_parent = (root / "6_release").resolve()
    release_root = (release_parent / args.name).resolve()
    zip_path = root / "9.Version/releases" / f"{args.name}.zip"
    if release_root.parent != release_parent:
        raise ValueError(f"unsafe release directory: {release_root}")
    if release_root.exists():
        shutil.rmtree(release_root)
    release_root.mkdir(parents=True)
    missing = [relative for relative in FILES if not (root / relative).is_file()]
    if missing:
        raise FileNotFoundError("Missing release inputs:\n" + "\n".join(missing))
    for relative in FILES:
        source = root / relative
        destination = release_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    readme = """# CMM R7A1C1B2 / R7A2A0 release

This package closes the exact five-donor PBC liver target gate and freezes the
five-control R7A2A1 execution path. All five PBC donors passed technical QC;
FCRL3-B and IL12RB2-NK were promotion-eligible in 5/5 donors. The included
control runner downloads one source-hosted BAM at a time, validates it, creates
compact outputs, and deletes the BAM only after receipt validation.

Raw BAMs and called-cell tables are excluded. Source URLs, byte counts, provider
MD5 values and local SHA-256 values are recorded in the included manifests.

Run R7A2A1 from the full workspace with:

    pwsh -File .\\2_code\\06_intake\\r7a2\\RUN_R7A2A1_HRA008003_CONTROL_TARGET_PANEL.ps1
"""
    (release_root / "README_RELEASE.md").write_text(readme, encoding="utf-8")
    checksum_lines = []
    for path in sorted(p for p in release_root.rglob("*") if p.is_file()):
        relative = path.relative_to(release_root).as_posix()
        checksum_lines.append(f"{digest(path)}  {relative}")
    (release_root / "CHECKSUMS.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in release_root.rglob("*") if p.is_file()):
            archive.write(path, (Path(args.name) / path.relative_to(release_root)).as_posix())
    sha = digest(zip_path)
    sha_path = zip_path.with_suffix(zip_path.suffix + ".sha256")
    sha_path.write_text(f"{sha}  {zip_path.name}\n", encoding="utf-8")
    print(f"ZIP={zip_path}")
    print(f"SHA256={sha}")
    print(f"FILES={len(checksum_lines) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
