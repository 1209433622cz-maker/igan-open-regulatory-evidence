#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import shutil
import zipfile
from pathlib import Path


STATIC_FILES = [
    "README_WORKSPACE.md",
    "0_admin/protocol/current/project_portfolio_state_R7A2A1_R7A2A2.json",
    "0_admin/protocol/current/R7A2A2_manuscript_evidence_freeze_v1.md",
    "1_data/scrna/PBC/HRA008003/manifests/HRA008003_control_liver_primary_run_manifest_v1.tsv",
    "2_code/06_intake/r7a1c1/02_hra_bam_target_panel_v2.py",
    "2_code/06_intake/r7a2/01_validate_HRA008003_control_manifest.py",
    "2_code/06_intake/r7a2/02_compare_PBC_control_target_panel.py",
    "2_code/06_intake/r7a2/05_independent_QA_R7A2A1.py",
    "2_code/06_intake/r7a2/06_R7A2A1_sensitivity.py",
    "2_code/06_intake/r7a2/07_plot_R7A2A1_tissue_gate.py",
    "2_code/06_intake/r7a2/08_build_R7A2A1_final_adjudication.py",
    "2_code/06_intake/r7a2/RUN_R7A2A1_HRA008003_CONTROL_TARGET_PANEL_HARDENED.ps1",
    "2_code/06_intake/r7a2/RUN_R7A2A1_README.md",
    "2_code/09_release/build_r7a2a1_r7a2a2_release.py",
    "3_results/00_audit/R7A2A1/R7A2A0_control_manifest_preflight.json",
    "3_results/00_audit/R7A2A1/R7A2A1_HRA008003_control_receipts.tsv",
    "3_results/00_audit/R7A2A1/R7A2A1_independent_QA.json",
    "3_results/00_audit/R7A2A1/R7A2A1_runner_parser_audit.json",
    "3_results/00_audit/R7A2A1/R7A2A1_independent_comparison.json",
    "3_results/00_audit/R7A2A1/R7A2A1_independent_comparison.tsv",
    "3_results/04_integration/R7A1B/R7A1B_final_adjudication.json",
    "3_results/04_integration/R7A1B/R7A1B_gene_adjudication.tsv",
    "3_results/04_integration/R7A1C/R7A1C_FCRL3_TenK_Bintermediate_result.json",
    "3_results/04_integration/R7A1C/R7A1C_IL12RB2_TenK_NK_fullPBC_coloc.tsv",
    "3_results/04_integration/R7A2A1/R7A2A1_final_adjudication.json",
    "3_results/04_integration/R7A2A1/R7A2A2_claim_evidence_matrix.tsv",
    "3_results/05_tissue/R7A1C1/R7A1C1_liver_final_adjudication_v2.json",
    "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel.json",
    "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel.tsv",
    "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel_sensitivity.json",
    "3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel_sensitivity.tsv",
    "0_admin/compatibility/figure_stage_view/R7A2A1/R7A2A1_PBC_vs_control_target_panel.png",
    "0_admin/compatibility/figure_stage_view/R7A2A1/R7A2A1_PBC_vs_control_target_panel.pdf",
    "0_admin/compatibility/figure_stage_view/R7A2A1/R7A2A1_PBC_vs_control_target_panel.svg",
    "7.Report/rounds/R7A2A1_R7A2A2/00_CMM_R7A2A1_执行摘要_五对五组织终裁.md",
    "7.Report/rounds/R7A2A1_R7A2A2/01_CMM_R7A2A1_字节接入与独立复核.md",
    "7.Report/rounds/R7A2A1_R7A2A2/02_CMM_R7A2A1_组织结果科学终裁.md",
    "7.Report/rounds/R7A2A1_R7A2A2/03_CMM_R7A2A1_HardenedRunner审计.md",
    "7.Report/rounds/R7A2A1_R7A2A2/04_CMM_R7A2A2_下一阶段冻结目标.md",
    "7.Report/rounds/R7A2A1_R7A2A2/99_CMM_R7A2A1_R7A2A2_详细行动记录_2026-09-30.md",
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
    parser.add_argument("--name", default="CMM_R7A2A1_PBC_5v5_TissueAdjudication_2026-09-30")
    args = parser.parse_args()
    root = args.root.resolve()
    files = list(STATIC_FILES)
    for run in [f"HRR18494{i}" for i in range(54, 59)]:
        files.extend([
            f"3_results/00_audit/R7A2A1/{run}.hashes.json",
            f"3_results/00_audit/R7A2A1/{run}.bam_schema_preflight_v1_2.json",
            f"3_results/00_audit/R7A2A1/{run}.resume_validation.json",
            f"3_results/05_tissue/R7A2A1_control/{run}_target_panel_summary.json",
        ])
    release_parent = (root / "6_release").resolve()
    release_root = (release_parent / args.name).resolve()
    zip_path = root / "9.Version/releases" / f"{args.name}.zip"
    if release_root.parent != release_parent:
        raise ValueError(f"unsafe release directory: {release_root}")
    if release_root.exists():
        shutil.rmtree(release_root)
    release_root.mkdir(parents=True)
    missing = [relative for relative in files if not (root / relative).is_file()]
    if missing:
        raise FileNotFoundError("Missing release inputs:\n" + "\n".join(missing))
    for relative in files:
        source = root / relative
        destination = release_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    readme = """# CMM R7A2A1 release

This package closes the exact 5 PBC versus 5 non-lesion control liver target
panel. All five control BAM identities and compact outputs passed independent
QA. Neither prespecified target passed the corrected case-control enrichment
gate. FCRL3-B was directionally lower in PBC; IL12RB2-NK was directionally
higher but BH q was 0.1111 for both targets.

The PBC project continues because its core claim is the replicated disease-eQTL
signal sharing in OneK1K and TenK10K. The tissue layer is limited to bounded
lineage localization and does not support PBC-specific upregulation.

Raw BAMs and per-cell tables are excluded. Provider identities, hashes,
donor-level aggregate metrics, code, audits, reports and figure sources are
included.
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
    with zipfile.ZipFile(zip_path) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
    sha = digest(zip_path)
    sha_path = zip_path.with_suffix(zip_path.suffix + ".sha256")
    sha_path.write_text(f"{sha}  {zip_path.name}\n", encoding="utf-8")
    print(f"ZIP={zip_path}")
    print(f"SHA256={sha}")
    print("ZIP_CRC=PASS")
    print(f"CHECKSUM_ENTRIES={len(checksum_lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

