#!/usr/bin/env python3
"""Build and verify the compact R6A1 release package (raw large data excluded)."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RELEASE = ROOT / "6_release/current/R6A1"
REPORT = ROOT / "7.Report/current/R6A1"
AUDIT = ROOT / "3_results/00_audit/R6A1"
RESULT = ROOT / "3_results/04_integration/R6A1"
FIG = ROOT / "0_admin/compatibility/figure_stage_view/R6A1"
ADMIN = ROOT / "0_admin/protocol/current"
CODE = ROOT / "2_code/06_intake/igan_r6a1"
DOWNLOADS = Path.home() / "Downloads"
RELEASE.mkdir(parents=True, exist_ok=True)

name = "CMM_R6A1_IgAN_ByteLevel_PositiveEvidencePreflight_2026-09-14.zip"
zip_path = RELEASE / name


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


with tempfile.TemporaryDirectory(prefix="r6a1_release_", dir=str(RELEASE)) as tmp:
    stage = Path(tmp) / "CMM_R6A1"
    for sub in ("reports", "protocol", "scripts", "audit", "results", "figures", "provenance_inputs"):
        (stage / sub).mkdir(parents=True, exist_ok=True)

    for src in REPORT.glob("*.md"):
        shutil.copy2(src, stage / "reports" / src.name)
    for src in (
        ADMIN / "R6A1_IgAN_preflight_final_state.json",
        ADMIN / "R6A2_IgAN_regulatory_landscape_protocol.md",
        ADMIN / "project_portfolio_state_R6A1.json",
    ):
        shutil.copy2(src, stage / "protocol" / src.name)
    for src in CODE.glob("*.py"):
        if src.name != "05_download_geo_range.py":
            shutil.copy2(src, stage / "scripts" / src.name)
    for src in AUDIT.glob("*.json"):
        shutil.copy2(src, stage / "audit" / src.name)
    for pattern in ("*.tsv", "*.tsv.gz"):
        for src in RESULT.glob(pattern):
            shutil.copy2(src, stage / "results" / src.name)
    for src in FIG.glob("Figure_R6A1_preflight_overview.*"):
        shutil.copy2(src, stage / "figures" / src.name)
    input_dir = ROOT / "7.Report/rounds/R6A1/inputs"
    if input_dir.exists():
        for src in input_dir.glob("*.md"):
            shutil.copy2(src, stage / "provenance_inputs" / src.name)

    release_readme = """# CMM R6A1 release\n\nThis compact package contains reports, scripts, machine-readable audits, derived result tables, the overview figure and the frozen R6A2 protocol.\n\nLarge raw inputs are intentionally excluded: four GWAS analysis files (~1.9 GB), OneK1K full cis-eQTL (~10.34 GB), public genotype, and GEO raw archives remain under the workspace `1_data` tree. Their paths, byte sizes and hashes are recorded in the audit manifests.\n\nR6A1 establishes access/testability/detectability. It makes zero new disease-QTL colocalization-positive claims.\n"""
    (stage / "README.md").write_text(release_readme, encoding="utf-8")

    members = sorted(p for p in stage.rglob("*") if p.is_file())
    checksum_lines = [f"{sha256(p)}  {p.relative_to(stage).as_posix()}" for p in members]
    (stage / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src in sorted(p for p in stage.rglob("*") if p.is_file()):
            zf.write(src, Path("CMM_R6A1") / src.relative_to(stage))

# ZIP CRC and internal checksum verification.
with zipfile.ZipFile(zip_path) as zf:
    bad = zf.testzip()
    if bad is not None:
        raise RuntimeError(f"ZIP CRC failure: {bad}")
    manifest_name = "CMM_R6A1/checksums.sha256"
    lines = zf.read(manifest_name).decode("utf-8").splitlines()
    checked = 0
    for line in lines:
        expected, rel = line.split("  ", 1)
        actual = hashlib.sha256(zf.read("CMM_R6A1/" + rel)).hexdigest()
        if actual != expected:
            raise RuntimeError(f"internal checksum mismatch: {rel}")
        checked += 1
    member_count = len([n for n in zf.namelist() if not n.endswith("/")])

zip_hash = sha256(zip_path)
sidecar = zip_path.with_suffix(zip_path.suffix + ".sha256")
sidecar.write_text(f"{zip_hash}  {zip_path.name}\n", encoding="utf-8")
audit = {
    "release": str(zip_path),
    "bytes": zip_path.stat().st_size,
    "sha256": zip_hash,
    "zip_crc": "PASS",
    "internal_checksums": f"{checked}/{checked} PASS",
    "zip_members_including_checksum_manifest": member_count,
    "large_raw_data_included": False,
}
(AUDIT / "R6A1_release_verification.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

shutil.copy2(zip_path, DOWNLOADS / zip_path.name)
shutil.copy2(sidecar, DOWNLOADS / sidecar.name)
record = REPORT / "99_CMM_R6A1_详细行动记录_2026-09-14.md"
shutil.copy2(record, DOWNLOADS / record.name)

print(json.dumps(audit, indent=2))
