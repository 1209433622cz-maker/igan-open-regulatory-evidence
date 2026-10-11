#!/usr/bin/env python3
"""Build and validate the compact R5A2B final adjudication release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import py_compile
import shutil
import subprocess
import zipfile

import pandas as pd

ROOT = Path(r"H:\SCI2\YR1")
NAME = "CMM_R5A2B_chr5_BoundedFinalAdjudication_2026-09-14"
STAGE_ROOT = ROOT / "9.Version/stage_workspaces/R5A2B_release_build"
STAGE = STAGE_ROOT / NAME
CURRENT = ROOT / "6_release/current/R5A2B"
HISTORY = ROOT / "6_release/history/R5A2B"
DOWNLOADS = Path(r"C:\Users\Administrator\Downloads")
AUDIT = ROOT / "3_results/00_audit/R5A2B"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def recreate(path: Path) -> None:
    resolved = path.resolve()
    workspace = ROOT.resolve()
    if not resolved.is_relative_to(workspace) or resolved == workspace:
        raise RuntimeError(f"Unsafe staging path: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


code_dir = ROOT / "2_code/06_intake/mg_r5a2b"
python_status = {}
for path in sorted(code_dir.glob("*.py")):
    try:
        py_compile.compile(str(path), doraise=True)
        python_status[path.name] = "PASS"
    except Exception as exc:
        python_status[path.name] = f"FAIL: {exc}"

rscript = ROOT / "0_admin/tooling/R/R-4.6.1/bin/Rscript.exe"
r_status = {}
for path in sorted(code_dir.glob("*.R")):
    proc = subprocess.run([str(rscript), "-e", f"parse(file={json.dumps(str(path))})"], capture_output=True, text=True)
    r_status[path.name] = "PASS" if proc.returncode == 0 else f"FAIL: {proc.stderr[-1000:]}"

ps = code_dir / "RUN_R5A2B_CHR5_BOUNDED_SMOKE.ps1"
ps_command = (
    "$tokens=$null; $errors=$null; "
    f"[System.Management.Automation.Language.Parser]::ParseFile('{ps}',[ref]$tokens,[ref]$errors) | Out-Null; "
    "if($errors.Count -gt 0){$errors | ForEach-Object {$_.Message}; exit 1}"
)
ps_proc = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_command], capture_output=True, text=True)

json_paths = [
    ROOT / "0_admin/protocol/current/R5A2B_chr5_bounded_final_state.json",
    ROOT / "0_admin/protocol/current/project_portfolio_state_R6A0.json",
    AUDIT / "R5A2B0_package_and_target_recalculation_audit.json",
    AUDIT / "OneK1K_archive_intake_audit.json",
    AUDIT / "MG_GRCh37_chr5_harmonization_audit.json",
    AUDIT / "chr5_python_vs_official_R_coloc_audit.json",
    ROOT / "3_results/04_integration/R5A2B/chr5_bounded_final_adjudication.json",
]
json_status = {}
for path in json_paths:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        json_status[path.name] = "PASS"
    except Exception as exc:
        json_status[path.name] = f"FAIL: {exc}"

smoke = pd.read_csv(ROOT / "3_results/04_integration/R5A2B/chr5_coloc_abf_smoke.tsv", sep="\t")
trigger = pd.read_csv(ROOT / "3_results/04_integration/R5A2B/chr5_sourceLD_trigger_matrix.tsv", sep="\t")
scientific = {
    "smoke_tests_96": len(smoke) == 96,
    "three_traits_32_each": smoke.groupby("trait").size().to_dict() == {"EOMG": 32, "LOMG": 32, "MG_overall": 32},
    "robust_shared_signal_zero": int(trigger["robust_H4"].sum()) == 0,
    "resolvable_ambiguity_zero": int(trigger["resolvable_H3H4_ambiguity"].sum()) == 0,
    "source_LD_trigger_zero": int(trigger["source_LD_trigger"].sum()) == 0,
    "official_R_validation_pass": json.loads((AUDIT / "chr5_python_vs_official_R_coloc_audit.json").read_text())["validation_pass"],
}

qa = {
    "schema_version": "1.0",
    "python_compile": python_status,
    "R_parse": r_status,
    "PowerShell_parse": {ps.name: "PASS" if ps_proc.returncode == 0 else f"FAIL: {ps_proc.stdout}{ps_proc.stderr}"},
    "JSON_validation": json_status,
    "scientific_checks": scientific,
}
qa["all_technical_and_scientific_checks_pass"] = (
    all(v == "PASS" for v in python_status.values())
    and all(v == "PASS" for v in r_status.values())
    and ps_proc.returncode == 0
    and all(v == "PASS" for v in json_status.values())
    and all(scientific.values())
)
(AUDIT / "R5A2B_pre_release_QA.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
if not qa["all_technical_and_scientific_checks_pass"]:
    raise RuntimeError("R5A2B pre-release QA failed")

round_dir = ROOT / "7.Report/rounds/R5A2B"
round_dir.mkdir(parents=True, exist_ok=True)
for path in (ROOT / "7.Report/current/R5A2B").glob("*.md"):
    shutil.copy2(path, round_dir / path.name)

mapping: list[tuple[Path, str]] = []


def add(path: Path, dest: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    mapping.append((path, dest))


for path in sorted((ROOT / "7.Report/current/R5A2B").glob("*.md")):
    add(path, f"reports/{path.name}")
for path in [
    ROOT / "0_admin/protocol/current/R5A2B_chr5_bounded_final_state.json",
    ROOT / "0_admin/protocol/current/R6A0_IgAN_open_data_byte_level_preflight_protocol.md",
    ROOT / "0_admin/protocol/current/project_portfolio_state_R6A0.json",
    ROOT / "0_admin/protocol/history/R5A2B/R5A2B_chr5_bounded_pilot_protocol_v2_frozen.md",
]:
    add(path, f"protocol/{path.name}")
for path in sorted(code_dir.glob("*")):
    if path.is_file() and path.suffix.lower() in {".py", ".r", ".ps1", ".tsv"}:
        add(path, f"code/{path.name}")
for path in sorted(AUDIT.glob("*")):
    if path.is_file():
        add(path, f"audit/{path.name}")
for directory, release_dir in [
    (ROOT / "3_results/01_gwas/R5A2B", "results/gwas"),
    (ROOT / "3_results/03_qtl/R5A2B", "results/qtl"),
    (ROOT / "3_results/04_integration/R5A2B", "results/integration"),
    (ROOT / "0_admin/compatibility/figure_stage_view/R5A2B", "figures"),
]:
    for path in sorted(directory.glob("*")):
        if path.is_file():
            add(path, f"{release_dir}/{path.name}")

recreate(STAGE_ROOT)
manifest = []
for src, dest in mapping:
    out = STAGE / dest
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out)
    manifest.append({"release_path": dest, "bytes": out.stat().st_size, "sha256": sha256_file(out)})
pd.DataFrame(manifest).sort_values("release_path").to_csv(STAGE / "asset_manifest.tsv", sep="\t", index=False)

checksum_files = sorted(p for p in STAGE.rglob("*") if p.is_file())
with (STAGE / "checksums.sha256").open("w", encoding="utf-8", newline="\n") as handle:
    for path in checksum_files:
        handle.write(f"{sha256_file(path)}  {path.relative_to(STAGE).as_posix()}\n")

CURRENT.mkdir(parents=True, exist_ok=True)
HISTORY.mkdir(parents=True, exist_ok=True)
archive = CURRENT / f"{NAME}.zip"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for path in sorted(STAGE.rglob("*")):
        if path.is_file():
            zf.write(path, f"{NAME}/{path.relative_to(STAGE).as_posix()}")

with zipfile.ZipFile(archive) as zf:
    crc_pass = zf.testzip() is None
    lines = zf.read(f"{NAME}/checksums.sha256").decode("utf-8").splitlines()
    internal_pass = all(
        hashlib.sha256(zf.read(f"{NAME}/{rel}")).hexdigest() == expected
        for expected, rel in (line.split("  ", 1) for line in lines)
    )

archive_sha = sha256_file(archive)
sidecar = CURRENT / f"{NAME}.zip.sha256"
sidecar.write_text(f"{archive_sha}  {archive.name}\n", encoding="utf-8")
for destination in [HISTORY, DOWNLOADS]:
    shutil.copy2(archive, destination / archive.name)
    shutil.copy2(sidecar, destination / sidecar.name)

action = ROOT / "7.Report/current/R5A2B/99_CMM_R5A2B_详细行动记录_2026-09-14.md"
shutil.copy2(action, DOWNLOADS / action.name)
(DOWNLOADS / f"{action.name}.sha256").write_text(f"{sha256_file(action)}  {action.name}\n", encoding="utf-8")

validation = {
    "schema_version": "1.0",
    "archive": str(archive),
    "bytes": archive.stat().st_size,
    "sha256": archive_sha,
    "zip_crc_pass": crc_pass,
    "declared_internal_checksums": len(lines),
    "all_internal_checksums_pass": internal_pass,
    "raw_10GB_archive_included": False,
    "extracted_851MB_parquet_members_included": False,
    "derived_bounded_QTL_table_included": True,
}
(CURRENT / "R5A2B_release_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
for destination in [HISTORY, DOWNLOADS]:
    shutil.copy2(CURRENT / "R5A2B_release_validation.json", destination / "R5A2B_release_validation.json")
print(json.dumps(validation, ensure_ascii=False, indent=2))
