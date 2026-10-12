#!/usr/bin/env python3
"""Build the R4A12FG7-QA release from an explicit allow-list."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


WORKSPACE = Path(r"H:\SCI2\YR1")
RELEASE = WORKSPACE / "6_release" / "current" / "R4A12FG7QA"
ROOT = RELEASE / "CMM_R4A12FG7QA_AccessPackageHostileQA_v4_2026-09-13"
ZIP = ROOT.with_suffix(".zip")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy(src: Path, destination: str) -> None:
    target = ROOT / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target)


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    if ZIP.exists() or Path(str(ZIP) + ".sha256").exists():
        raise SystemExit(f"final release target already exists: {ZIP}")
    ROOT.mkdir(parents=True, exist_ok=True)

    report_dir = WORKSPACE / "7.Report" / "rounds" / "R4A12FG7QA"
    for src in report_dir.glob("*.md"):
        if src.name == "06_author_request_native_IL12RB2_LD_READY_FOR_IDENTITY.md":
            copy(src, f"access/{src.name}")
        else:
            copy(src, f"reports/{src.name}")

    source_ld = WORKSPACE / "2_code" / "06_intake" / "source_ld"
    for name in (
        "validate_received_tenk10k_source_ld_v2.py",
        "build_il12rb2_source_ld_from_approved_vcf_v2.sh",
        "RUN_VALIDATE_RECEIVED_TENK10K_IL12RB2_LD.ps1",
    ):
        copy(source_ld / name, f"scripts/{name}")
    copy(
        WORKSPACE / "2_code" / "envs" / "tenk10k_source_ld_environment.yml",
        "environment/tenk10k_source_ld_environment.yml",
    )
    copy(
        WORKSPACE / "2_code" / "07_analysis" / "R4A12FG7QA" / "run_source_ld_validator_hostile_tests.py",
        "tests/run_source_ld_validator_hostile_tests.py",
    )

    for src in (WORKSPACE / "1_data" / "manifests" / "R4A12FG7").glob("*.tsv"):
        copy(src, f"manifests/{src.name}")

    audit_dir = WORKSPACE / "3_results" / "00_audit" / "R4A12FG7QA"
    for name in (
        "fg7_release_integrity.json",
        "fg7_standalone_byte_identity.json",
        "source_ld_validator_hostile_tests.json",
        "source_ld_local_inventory.json",
        "external_primary_source_status.json",
    ):
        copy(audit_dir / name, f"audit/{name}")
    copy(
        audit_dir / "tenk10k_public_code" / "retrieval_receipt.json",
        "audit/tenk10k_public_code_retrieval_receipt.json",
    )

    protocol = WORKSPACE / "0_admin" / "protocol" / "current"
    for name in (
        "analysis_manifest_v11_amendment_A4_R4A12FG7QA.json",
        "R4A12FG7QA_state.json",
    ):
        copy(protocol / name, f"protocol/{name}")

    access = WORKSPACE / "7.Report" / "rounds" / "R4A12FG7"
    for name in ("02_EGA_project_abstract_DRAFT.md", "03_EGA_submission_checklist.md"):
        copy(access / name, f"access/{name}")

    readme = """# CMM R4A12FG7-QA release

状态：`ACCESS_PENDING_NO_FG8_TRIGGER`

本包完成FG7访问材料的独立完整性复核、原validator false-PASS复现、v2门控修复、受控重建脚本加固和下一阶段触发冻结。包内不含source `.bim/.ld`、受控VCF或任何个体级数据。

优先阅读：

1. `reports/00_CMM_R4A12FG7QA_执行摘要_访问包敌意复核与门控加固.md`
2. `reports/02_CMM_R4A12FG7QA_SourceLD验证器敌意测试与v2修复.md`
3. `reports/04_CMM_R4A12FG7QA_收件运行手册与受控重建协议v2.md`
4. `reports/05_CMM_R4A12FG7QA_下一阶段冻结目标与触发矩阵.md`
5. `reports/99_CMM_R4A12FG7QA_详细行动记录_2026-09-13.md`

作者文件到达后，Windows入口为 `scripts/RUN_VALIDATE_RECEIVED_TENK10K_IL12RB2_LD.ps1`。EGA获批后只在机构安全环境运行 `scripts/build_il12rb2_source_ld_from_approved_vcf_v2.sh`。
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8", newline="\n")

    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and p.name != "checksums.sha256")
    lines = [f"{digest(p)}  {p.relative_to(ROOT).as_posix()}" for p in files]
    (ROOT / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in ROOT.rglob("*") if p.is_file()):
            zf.write(path, (Path(ROOT.name) / path.relative_to(ROOT)).as_posix())

    zip_sha = digest(ZIP)
    Path(str(ZIP) + ".sha256").write_text(zip_sha + "\n", encoding="ascii", newline="\n")
    print(json.dumps({
        "root": str(ROOT), "zip": str(ZIP), "zip_bytes": ZIP.stat().st_size,
        "zip_sha256": zip_sha, "package_files": sum(1 for p in ROOT.rglob("*") if p.is_file()),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
