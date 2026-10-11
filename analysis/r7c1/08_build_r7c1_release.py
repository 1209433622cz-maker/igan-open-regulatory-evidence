#!/usr/bin/env python3
"""Build the self-checking R7C1 release archive."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_manuscript/R7C1_IL12RB2_ExternalValidation_ManuscriptFork"
RELEASE = ROOT / "6_release/R7C1_2026-10-11"
STAGE = RELEASE / "CMM_R7C1_IL12RB2_ExternalValidation_ManuscriptFork_2026-10-11"
ZIP = RELEASE / "CMM_R7C1_IL12RB2_ExternalValidation_ManuscriptFork_2026-10-11.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy_tree_files(source: Path, target: Path, include=None) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.iterdir()):
        if path.is_file() and (include is None or path.name in include):
            shutil.copy2(path, target / path.name)


def main() -> None:
    if not STAGE.resolve().is_relative_to(RELEASE.resolve()):
        raise RuntimeError(f"Unsafe stage path: {STAGE}")
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True, exist_ok=True)

    copy_tree_files(WORK / "manuscript", STAGE / "manuscript")
    copy_tree_files(WORK / "figures", STAGE / "figures")
    copy_tree_files(WORK / "supplement", STAGE / "supplement", {
        "Additional_file_1_Supplementary_Tables_S1-S10.xlsx",
        "Additional_file_2_Machine_Readable_Supplementary_Data.zip",
        "Additional_file_3_R7C1_External_Validation_Data.zip",
    })
    copy_tree_files(WORK / "code", STAGE / "code")
    copy_tree_files(WORK / "protocols", STAGE / "protocols")
    copy_tree_files(WORK / "reports", STAGE / "reports")
    copy_tree_files(WORK / "results", STAGE / "results")
    copy_tree_files(WORK / "qa", STAGE / "qa", {
        "R7C1_machine_hostile_QA.json", "R7C1_machine_hostile_QA.tsv"
    })

    readme = """# R7C1 release

This release contains the bounded IL12RB2-NK external-validation manuscript fork.
It preserves the byte-identical R7B4B2 Human Genomics baseline and adds only the
prespecified FinnGen R13 disease-study, source-CS, CASCADE chromatin-triangle and
descriptive OMIX modules.

The manuscript does not claim person-level zero overlap, a second source-LD
multi-signal validation, a direct eQTL-caQTL posterior, chromatin mediation or
independent spatial replication.

The PDF was exported with WPS Writer. Machine and hostile-claim QA passed 38/38.
"""
    (STAGE / "README.md").write_text(readme, encoding="utf-8")

    manifest = []
    for path in sorted(STAGE.rglob("*")):
        if path.is_file() and path.name != "checksums.sha256.tsv":
            manifest.append({
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "path": path.relative_to(STAGE).as_posix(),
            })
    lines = ["sha256\tbytes\tpath"] + [f"{x['sha256']}\t{x['bytes']}\t{x['path']}" for x in manifest]
    (STAGE / "checksums.sha256.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(STAGE.rglob("*")):
            if path.is_file():
                archive.write(path, f"{STAGE.name}/{path.relative_to(STAGE).as_posix()}")

    with zipfile.ZipFile(ZIP) as archive:
        bad = archive.testzip()
        entries = len(archive.namelist())
    state = {
        "zip": str(ZIP),
        "sha256": sha256(ZIP),
        "bytes": ZIP.stat().st_size,
        "entries": entries,
        "internal_manifest_rows": len(manifest),
        "zip_crc": "PASS" if bad is None else f"FAIL:{bad}",
    }
    (RELEASE / "R7C1_release_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    (RELEASE / f"{ZIP.name}.sha256").write_text(f"{state['sha256']}  {ZIP.name}\n", encoding="utf-8")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
