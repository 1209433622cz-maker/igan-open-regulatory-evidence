#!/usr/bin/env python3
"""Build the lightweight R7A1B1 release with hashes and large-file provenance."""
from pathlib import Path
import hashlib
import os
import shutil
import zipfile

import pandas as pd

ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
BUILD = ROOT / "9.Version/releases/R7A1B1_2026-09-15_build1"
ZIP = ROOT / "9.Version/releases/CMM_R7A1B1_PBC_3Control_TrueSignal_2026-09-15.zip"
SIDE = ZIP.with_suffix(ZIP.suffix + ".sha256")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

if BUILD.exists() or ZIP.exists() or SIDE.exists():
    raise FileExistsError("release output already exists; use a new build name rather than overwriting")
for name in ["code", "reports", "protocol", "results/audit", "results/gwas",
             "results/qtl", "results/integration/multisignal", "results/integration/sourceLD", "figures"]:
    (BUILD / name).mkdir(parents=True, exist_ok=True)

for src in (ROOT / "2_code/06_intake/r7a1b").iterdir():
    if src.is_file() and src.suffix.lower() in {".py", ".r", ".ps1", ".tsv"} and not src.name.startswith("SYNC_R7A1B0"):
        shutil.copy2(src, BUILD / "code" / src.name)
for src in (ROOT / "7.Report/rounds/R7A1B1").glob("*.md"):
    shutil.copy2(src, BUILD / "reports" / src.name)
shutil.copy2(ROOT / "7.Report/protocols/current/R7A1C_TenK_replication_and_PBC_liver_gate_v1.md",
             BUILD / "protocol/R7A1C_TenK_replication_and_PBC_liver_gate_v1.md")

for src in (ROOT / "3_results/00_audit/R7A1B").glob("*"):
    if src.is_file(): shutil.copy2(src, BUILD / "results/audit" / src.name)
for src in (ROOT / "3_results/01_gwas/R7A1B").glob("*"):
    if src.is_file(): shutil.copy2(src, BUILD / "results/gwas" / src.name)
for src in (ROOT / "3_results/03_qtl/R7A1B").glob("*"):
    if src.is_file(): shutil.copy2(src, BUILD / "results/qtl" / src.name)

ibase = ROOT / "3_results/04_integration/R7A1B"
for src in ibase.glob("*"):
    if src.is_file(): shutil.copy2(src, BUILD / "results/integration" / src.name)
for src in (ibase / "multisignal").glob("*"):
    if src.is_file(): shutil.copy2(src, BUILD / "results/integration/multisignal" / src.name)
for directory in sorted((ibase / "sourceLD").iterdir()):
    if not directory.is_dir(): continue
    target = BUILD / "results/integration/sourceLD" / directory.name
    target.mkdir(parents=True, exist_ok=True)
    for name in ["LD_variants.tsv", "sourceLD_QC.json", "covariate_residual_LD_QC.json"]:
        src = directory / name
        if src.exists(): shutil.copy2(src, target / name)
summary = ibase / "sourceLD/R7A1B_covariate_residual_LD_summary.tsv"
if summary.exists(): shutil.copy2(summary, BUILD / "results/integration/sourceLD" / summary.name)
shutil.copy2(ROOT / "4_figures/R7A1B/R7A1B_PBC_signal_gate_summary.png",
             BUILD / "figures/R7A1B_PBC_signal_gate_summary.png")
shutil.copy2(ROOT / "0_admin/protocol/current/project_portfolio_state_R7A1B1.json",
             BUILD / "project_portfolio_state_R7A1B1.json")

excluded = [
    ROOT / "1_data/qtl/OneK1K/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz",
    ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bed",
    ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.bim",
    ROOT / "1_data/qtl/OneK1K/plink_merged_980_donors/plink_merged_980_donors.fam",
    ROOT / "1_data/gwas/R7A1A/PBC/GCST90061440_buildGRCh37.tsv",
]
excluded += sorted((ROOT / "1_data/study_inputs/PBC_GJOKA/R7A1B").glob("*"))
excluded += sorted(path for path in (ibase / "sourceLD").rglob("*")
                   if path.is_file() and path.name not in {"LD_variants.tsv", "sourceLD_QC.json",
                                                           "covariate_residual_LD_QC.json",
                                                           "R7A1B_covariate_residual_LD_summary.tsv"})
large_rows = []
for path in excluded:
    if path.is_file():
        large_rows.append({"relative_path": path.relative_to(ROOT).as_posix(),
                           "bytes": path.stat().st_size, "sha256": sha256(path),
                           "release_policy": "NOT_MIRRORED__LOCAL_OR_THIRD_PARTY_LARGE_INPUT"})
pd.DataFrame(large_rows).to_csv(BUILD / "LARGE_FILE_MANIFEST.tsv", sep="\t", index=False)

readme = """# CMM R7A1B1 lightweight release\n\nThis release contains the corrected bounded workflow, small derived inputs/results, source-LD QC and variant order, credible-set members, reports and the diagnostic figure. Donor-level genotypes, raw GWAS, GJOKA LD and generated LD matrices are not mirrored; their byte sizes and SHA-256 values are recorded in `LARGE_FILE_MANIFEST.tsv`.\n\nFinal decision: two of three frozen PBC control genes passed the signal-specific OneK gate. The next stage is R7A1C TenK10K independent signal replication plus PBC liver target detectability. PBC is not yet promoted to the new primary project.\n"""
(BUILD / "README.md").write_text(readme, encoding="utf-8")

files = sorted(path for path in BUILD.rglob("*") if path.is_file() and path.name != "checksums.sha256")
lines = [f"{sha256(path)}  {path.relative_to(BUILD).as_posix()}" for path in files]
(BUILD / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for path in sorted(p for p in BUILD.rglob("*") if p.is_file()):
        zf.write(path, path.relative_to(BUILD).as_posix())
with zipfile.ZipFile(ZIP) as zf:
    bad = zf.testzip()
    if bad is not None: raise RuntimeError(f"ZIP CRC failed: {bad}")
digest = sha256(ZIP)
SIDE.write_text(f"{digest}  {ZIP.name}\n", encoding="ascii")

downloads = Path.home() / "Downloads"
shutil.copy2(ZIP, downloads / ZIP.name)
shutil.copy2(SIDE, downloads / SIDE.name)
action = ROOT / "7.Report/rounds/R7A1B1/99_CMM_R7A1B1_详细行动记录_2026-09-15.md"
shutil.copy2(action, downloads / action.name)
print({"zip": str(ZIP), "bytes": ZIP.stat().st_size, "sha256": digest,
       "zip_crc": "PASS", "internal_files": len(list(BUILD.rglob('*')))})
