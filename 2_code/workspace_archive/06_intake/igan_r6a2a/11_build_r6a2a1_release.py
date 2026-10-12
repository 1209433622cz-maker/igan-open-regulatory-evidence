#!/usr/bin/env python3
"""Build and verify the compact R6A2A1 release."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
RELEASE = ROOT / "6_release/current/R6A2A1"
DOWNLOADS = Path.home() / "Downloads"
REPORT = ROOT / "7.Report/current/R6A2A1"
CODE = ROOT / "2_code/06_intake/igan_r6a2a"
AUDIT = ROOT / "3_results/00_audit/R6A2A"
GWAS = ROOT / "3_results/01_gwas/R6A2A"
QTL = ROOT / "3_results/03_qtl/R6A2A"
RESULT = ROOT / "3_results/04_integration/R6A2A"
FIG = ROOT / "0_admin/compatibility/figure_stage_view/R6A2A1"
ADMIN = ROOT / "0_admin/protocol/current"
TENK_TARGET = ROOT / "1_data/qtl/TenK10K/R6A2A_ZMIZ1_precomputed_coloc"
RELEASE.mkdir(parents=True, exist_ok=True)

name = "CMM_R6A2A1_IgAN_ZMIZ1Benchmark_TenKReplication_2026-09-14.zip"
zip_path = RELEASE / name


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


with tempfile.TemporaryDirectory(prefix="r6a2a1_", dir=str(RELEASE)) as tmp:
    stage = Path(tmp) / "CMM_R6A2A1"
    for sub in ("reports", "scripts", "protocol", "audit", "gwas", "qtl", "results", "figures", "tenk_target_members"):
        (stage / sub).mkdir(parents=True, exist_ok=True)
    for src in REPORT.glob("*.md"):
        shutil.copy2(src, stage / "reports" / src.name)
    for src in CODE.glob("*"):
        if src.is_file() and src.suffix.lower() in {".py", ".r", ".ps1", ".tsv"}:
            shutil.copy2(src, stage / "scripts" / src.name)
    for src in (
        ADMIN / "R6A2A1_state.json",
        ADMIN / "R6A2B0_bounded_positive_yield_protocol.md",
        ADMIN / "project_portfolio_state_R6A2A1.json",
    ):
        shutil.copy2(src, stage / "protocol" / src.name)
    for src in AUDIT.glob("*"):
        if src.is_file():
            shutil.copy2(src, stage / "audit" / src.name)
    for source, sub in ((GWAS, "gwas"), (QTL, "qtl"), (RESULT, "results"), (FIG, "figures")):
        for src in source.glob("*"):
            if src.is_file():
                shutil.copy2(src, stage / sub / src.name)
    for src in TENK_TARGET.glob("*"):
        if src.is_file():
            shutil.copy2(src, stage / "tenk_target_members" / src.name)

    (stage / "README.md").write_text(
        "# CMM R6A2A1 release\n\n"
        "Contains the corrected 10-combination OneK benchmark, official-R validation, targeted TenK ZMIZ1/NK evidence, the frozen 8-locus next-wave universe, reports and protocols.\n\n"
        "Excluded large inputs: 10.34 GB OneK archive, genotype BED/BIM/FAM and full IgAN GWAS files. Their identities and locations are captured in audit files.\n",
        encoding="utf-8",
    )
    members = sorted(p for p in stage.rglob("*") if p.is_file())
    (stage / "checksums.sha256").write_text(
        "\n".join(f"{sha(p)}  {p.relative_to(stage).as_posix()}" for p in members) + "\n", encoding="utf-8"
    )
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src in sorted(p for p in stage.rglob("*") if p.is_file()):
            zf.write(src, Path("CMM_R6A2A1") / src.relative_to(stage))

with zipfile.ZipFile(zip_path) as zf:
    if zf.testzip() is not None:
        raise RuntimeError("ZIP CRC failed")
    lines = zf.read("CMM_R6A2A1/checksums.sha256").decode("utf-8").splitlines()
    for line in lines:
        expected, rel = line.split("  ", 1)
        if hashlib.sha256(zf.read("CMM_R6A2A1/" + rel)).hexdigest() != expected:
            raise RuntimeError(f"internal checksum failed: {rel}")
    count = len([n for n in zf.namelist() if not n.endswith("/")])

release_sha = sha(zip_path)
sidecar = zip_path.with_suffix(zip_path.suffix + ".sha256")
sidecar.write_text(f"{release_sha}  {zip_path.name}\n", encoding="utf-8")
verification = {
    "release": str(zip_path),
    "bytes": zip_path.stat().st_size,
    "sha256": release_sha,
    "zip_crc": "PASS",
    "internal_checksums": f"{len(lines)}/{len(lines)} PASS",
    "members_including_checksum_manifest": count,
    "large_raw_inputs_included": False,
}
(AUDIT / "R6A2A1_release_verification.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")
shutil.copy2(zip_path, DOWNLOADS / zip_path.name)
shutil.copy2(sidecar, DOWNLOADS / sidecar.name)
record = REPORT / "99_CMM_R6A2A1_详细行动记录_2026-09-14.md"
shutil.copy2(record, DOWNLOADS / record.name)
print(json.dumps(verification, indent=2))
