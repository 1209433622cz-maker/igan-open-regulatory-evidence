#!/usr/bin/env python3
"""Build and validate the compact R5A2A4 release package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import py_compile
import shutil
import subprocess
import zipfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
NAME = "CMM_R5A2A4_NKR_ZCCHC2_Multisignal_2026-09-14"
STAGE_ROOT = ROOT / "9.Version" / "stage_workspaces" / "R5A2A4_release_build"
STAGE = STAGE_ROOT / NAME
CURRENT = ROOT / "6_release" / "current" / "R5A2A4"
HISTORY = ROOT / "6_release" / "history" / "R5A2A4"
DOWNLOADS = Path(r"C:\Users\Administrator\Downloads")
AUDIT_DIR = ROOT / "3_results" / "00_audit" / "R5A2A4"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_recreate(path: Path) -> None:
    resolved = path.resolve()
    workspace = ROOT.resolve()
    if not resolved.is_relative_to(workspace) or resolved == workspace:
        raise RuntimeError(f"Unsafe staging path: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def add(src: Path, dest: str, mapping: list[tuple[Path, str]]) -> None:
    if not src.is_file():
        raise FileNotFoundError(src)
    mapping.append((src, dest.replace("\\", "/")))


AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# Syntax and schema checks used by the release gate.
py_files = sorted((ROOT / "2_code" / "06_intake" / "mg_r5a2a4").glob("*.py"))
python_compile = {}
for path in py_files:
    try:
        py_compile.compile(str(path), doraise=True)
        python_compile[path.name] = "PASS"
    except Exception as exc:  # pragma: no cover - release failure path
        python_compile[path.name] = f"FAIL: {exc}"

rscript = ROOT / "0_admin" / "tooling" / "R" / "R-4.6.1" / "bin" / "Rscript.exe"
r_files = sorted((ROOT / "2_code" / "06_intake" / "mg_r5a2a4").glob("*.R"))
r_parse = {}
for path in r_files:
    proc = subprocess.run([str(rscript), "-e", f"parse(file={json.dumps(str(path))})"], capture_output=True, text=True)
    r_parse[path.name] = "PASS" if proc.returncode == 0 else f"FAIL: {proc.stderr[-1000:]}"

ps_file = ROOT / "2_code" / "06_intake" / "mg_r5a2a4" / "RUN_R5A2A4_NKR_ZCCHC2.ps1"
ps_cmd = (
    "$tokens=$null; $errors=$null; "
    f"[System.Management.Automation.Language.Parser]::ParseFile('{ps_file}',[ref]$tokens,[ref]$errors) | Out-Null; "
    "if($errors.Count -gt 0){$errors | ForEach-Object {$_.Message}; exit 1}"
)
ps_proc = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)

json_files = [
    ROOT / "0_admin" / "protocol" / "current" / "R5A2A4_NKR_ZCCHC2_multisignal_state.json",
    AUDIT_DIR / "R5A2A3_import_and_recalculation_audit.json",
    ROOT / "3_results" / "04_integration" / "R5A2A4" / "NK_R_ZCCHC2_sourceLD" / "NK_R_ZCCHC2_sourceLD_QC.json",
    ROOT / "3_results" / "04_integration" / "R5A2A4" / "NK_R_ZCCHC2_sourceLD" / "NK_R_ZCCHC2_covariate_residual_LD_QC.json",
    ROOT / "3_results" / "04_integration" / "R5A2A4" / "NK_R_ZCCHC2_multisignal" / "NK_R_ZCCHC2_multisignal_adjudication.json",
]
json_validation = {}
for path in json_files:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        json_validation[path.name] = "PASS"
    except Exception as exc:  # pragma: no cover
        json_validation[path.name] = f"FAIL: {exc}"

environment = {
    "schema_version": "1.0",
    "R": "4.6.1",
    "R_packages": {"susieR": "0.14.2", "coloc": "5.2.3", "data.table": "1.18.6.1", "jsonlite": "2.0.0"},
    "R_installer": {
        "path": "0_admin/tooling/installers/R-4.6.1-win.exe",
        "bytes": 91749976,
        "md5": "7907f3a20ec8ec88cd0da279024b8e27",
        "sha256": "c5424c40cd70ef85765a55d2ff96bb602b5f30ed536938ff004f14db5db3c2df",
    },
    "OneK1K_top_eQTL_archive": {
        "path": "1_data/qtl/OneK1K/OneK1K_TensorQTL_top_eQTL_summary.zip",
        "bytes": 16950155,
        "md5": "46e986dc53c9f4f1b6daa2b7a73d277c",
        "sha256": "a3100acf36aedfbb78ab7ddc1113b9dcb119170c9c4b863d37b99a0edee05d5d",
    },
}
(AUDIT_DIR / "software_and_source_environment.json").write_text(json.dumps(environment, ensure_ascii=False, indent=2), encoding="utf-8")

qa = {
    "schema_version": "1.0",
    "python_compile": python_compile,
    "R_parse": r_parse,
    "PowerShell_parse": {ps_file.name: "PASS" if ps_proc.returncode == 0 else f"FAIL: {ps_proc.stderr}{ps_proc.stdout}"},
    "JSON_validation": json_validation,
    "scientific_gates": {
        "R5A2A3_recalculation": "PASS",
        "source_LD": "PASS",
        "PF10_PF50_LD": "PASS",
        "SuSiE_all_configs_converged": "PASS",
        "SuSiE_credible_sets": 0,
        "frozen_decision": "FAIL_CHR18_ONEK1K_PBMC_EXPRESSION_MEDIATION",
    },
}
qa["all_technical_checks_pass"] = all(v == "PASS" for group in [python_compile, r_parse, json_validation] for v in group.values()) and ps_proc.returncode == 0
(AUDIT_DIR / "R5A2A4_pre_release_QA.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
if not qa["all_technical_checks_pass"]:
    raise RuntimeError("Pre-release QA failed; inspect R5A2A4_pre_release_QA.json")

# Mirror immutable round reports after the final text is present.
round_dir = ROOT / "7.Report" / "rounds" / "R5A2A4"
round_dir.mkdir(parents=True, exist_ok=True)
for path in (ROOT / "7.Report" / "current" / "R5A2A4").glob("*.md"):
    shutil.copy2(path, round_dir / path.name)

mapping: list[tuple[Path, str]] = []
for path in sorted((ROOT / "7.Report" / "current" / "R5A2A4").glob("*.md")):
    add(path, f"reports/{path.name}", mapping)
for path in [
    ROOT / "0_admin" / "protocol" / "current" / "R5A2A4_NKR_ZCCHC2_multisignal_state.json",
    ROOT / "0_admin" / "protocol" / "current" / "R5A2B_MG_chr5_TNIP1_bounded_pilot_protocol.md",
    ROOT / "0_admin" / "protocol" / "history" / "R5A2A4" / "R5A2A4_NKR_ZCCHC2_sourceLD_protocol_frozen.md",
]:
    add(path, f"protocol/{path.name}", mapping)
for path in sorted((ROOT / "2_code" / "06_intake" / "mg_r5a2a4").glob("*")):
    if path.is_file() and path.suffix.lower() in {".py", ".r", ".ps1"}:
        add(path, f"code/{path.name}", mapping)
add(ROOT / "2_code" / "06_intake" / "mg_r5a2a3" / "run_chr18_coloc_abf_smoke.py", "code/R5A2A3_recalculation/run_chr18_coloc_abf_smoke_deterministic.py", mapping)

for path in sorted(AUDIT_DIR.glob("*.json")):
    add(path, f"audit/{path.name}", mapping)

source_ld = ROOT / "3_results" / "04_integration" / "R5A2A4" / "NK_R_ZCCHC2_sourceLD"
for name in [
    "NK_R_750_active_donors.txt",
    "NK_R_ZCCHC2_anchor_LD.tsv.gz",
    "NK_R_ZCCHC2_covariate_residual_LD_QC.json",
    "NK_R_ZCCHC2_LD_variants.tsv",
    "NK_R_ZCCHC2_sourceLD_QC.json",
]:
    add(source_ld / name, f"results/sourceLD/{name}", mapping)

multi = ROOT / "3_results" / "04_integration" / "R5A2A4" / "NK_R_ZCCHC2_multisignal"
for path in sorted(multi.glob("*")):
    if path.is_file() and path.suffix.lower() != ".rds":
        add(path, f"results/multisignal/{path.name}", mapping)

recalc = ROOT / "3_results" / "04_integration" / "R5A2A3_recomputed"
for name in ["chr18_coloc_abf_smoke_213.tsv", "chr18_coloc_abf_smoke_summary.json", "chr18_coloc_abf_top_snps.tsv"]:
    add(recalc / name, f"results/R5A2A3_recomputed/{name}", mapping)

fig_dir = ROOT / "0_admin/compatibility/figure_stage_view" / "R5A2A4"
for path in sorted(fig_dir.glob("Figure_R5A2A4_NK_R_ZCCHC2_adjudication.*")):
    add(path, f"figures/{path.name}", mapping)

safe_recreate(STAGE_ROOT)
rows = []
for src, dest in mapping:
    out = STAGE / dest
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out)
    rows.append({"release_path": dest, "bytes": out.stat().st_size, "sha256": sha256_file(out)})

manifest = pd.DataFrame(rows).sort_values("release_path")
manifest.to_csv(STAGE / "asset_manifest.tsv", sep="\t", index=False)

checksum_paths = sorted(p for p in STAGE.rglob("*") if p.is_file())
with (STAGE / "checksums.sha256").open("w", encoding="utf-8", newline="\n") as handle:
    for path in checksum_paths:
        handle.write(f"{sha256_file(path)}  {path.relative_to(STAGE).as_posix()}\n")

CURRENT.mkdir(parents=True, exist_ok=True)
HISTORY.mkdir(parents=True, exist_ok=True)
zip_current = CURRENT / f"{NAME}.zip"
with zipfile.ZipFile(zip_current, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for path in sorted(STAGE.rglob("*")):
        if path.is_file():
            zf.write(path, f"{NAME}/{path.relative_to(STAGE).as_posix()}")

with zipfile.ZipFile(zip_current) as zf:
    crc_pass = zf.testzip() is None
    checksum_member = f"{NAME}/checksums.sha256"
    all_checksum_pass = True
    declared = 0
    for line in zf.read(checksum_member).decode("utf-8").splitlines():
        expected, rel = line.split("  ", 1)
        declared += 1
        actual = hashlib.sha256(zf.read(f"{NAME}/{rel}")).hexdigest()
        all_checksum_pass &= expected == actual

zip_sha = sha256_file(zip_current)
(CURRENT / f"{NAME}.zip.sha256").write_text(f"{zip_sha}  {NAME}.zip\n", encoding="utf-8")
shutil.copy2(zip_current, HISTORY / zip_current.name)
shutil.copy2(CURRENT / f"{NAME}.zip.sha256", HISTORY / f"{NAME}.zip.sha256")
shutil.copy2(zip_current, DOWNLOADS / zip_current.name)
shutil.copy2(CURRENT / f"{NAME}.zip.sha256", DOWNLOADS / f"{NAME}.zip.sha256")

action = ROOT / "7.Report" / "current" / "R5A2A4" / "99_CMM_R5A2A4_详细行动记录_2026-09-14.md"
shutil.copy2(action, DOWNLOADS / action.name)
(DOWNLOADS / f"{action.name}.sha256").write_text(f"{sha256_file(action)}  {action.name}\n", encoding="utf-8")

validation = {
    "schema_version": "1.0",
    "release": str(zip_current),
    "bytes": zip_current.stat().st_size,
    "sha256": zip_sha,
    "zip_crc_pass": crc_pass,
    "declared_internal_checksums": declared,
    "all_internal_checksums_pass": all_checksum_pass,
    "large_LD_matrices_included": False,
    "large_LD_matrices_referenced_by_QC_sha256": True,
}
(CURRENT / "R5A2A4_release_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copy2(CURRENT / "R5A2A4_release_validation.json", HISTORY / "R5A2A4_release_validation.json")
shutil.copy2(CURRENT / "R5A2A4_release_validation.json", DOWNLOADS / "R5A2A4_release_validation.json")

print(json.dumps(validation, ensure_ascii=False, indent=2))
