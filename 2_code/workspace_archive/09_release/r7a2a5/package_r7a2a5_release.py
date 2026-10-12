from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
NAME = "CMM_R7A2A5_HumanGenomics_SubmissionFormat_2026-09-30"
RELEASE_ROOT = ROOT / "6_release"
STAGE = RELEASE_ROOT / NAME
ZIP_PATH = RELEASE_ROOT / f"{NAME}.zip"
SIDECAR = RELEASE_ROOT / f"{NAME}.zip.sha256"
RECEIPT = RELEASE_ROOT / f"{NAME}.receipt.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


if STAGE.exists():
    resolved = STAGE.resolve()
    if resolved.parent != RELEASE_ROOT.resolve() or resolved.name != NAME:
        raise RuntimeError(f"Refusing to replace unexpected directory: {resolved}")
    shutil.rmtree(STAGE)
STAGE.mkdir(parents=True)

copies = [
    (ROOT / "5_manuscript" / "R7A2A5_HumanGenomics" / "manuscript", STAGE / "manuscript"),
    (ROOT / "5_manuscript" / "R7A2A5_HumanGenomics" / "cover_letter", STAGE / "cover_letter"),
    (ROOT / "5_manuscript" / "R7A2A5_HumanGenomics" / "figures", STAGE / "figures"),
    (ROOT / "5_manuscript" / "R7A2A5_HumanGenomics" / "graphical_abstract", STAGE / "graphical_abstract"),
    (ROOT / "5_manuscript" / "R7A2A5_HumanGenomics" / "supplement", STAGE / "supplement"),
    (ROOT / "5_manuscript" / "R7A2A5_HumanGenomics" / "results", STAGE / "results"),
    (ROOT / "5_manuscript" / "R7A2A5_HumanGenomics" / "submission", STAGE / "submission"),
    (ROOT / "7.Report" / "rounds" / "R7A2A5", STAGE / "reports"),
]
for src, dst in copies:
    shutil.copytree(src, dst)

code_dir = STAGE / "code"
code_dir.mkdir()
for name in [
    "build_r7a2a5_manuscript_assets.py",
    "build_r7a2a5_supplement.mjs",
    "export_r7a2a5_with_wps.ps1",
    "run_r7a2a5_final_qa.py",
    "package_r7a2a5_release.py",
    "SYNC_R7A2A5_TO_GITHUB.ps1",
]:
    shutil.copy2(ROOT / "2_code" / "09_release" / "r7a2a5" / name, code_dir / name)

readme = """# CMM R7A2A5 — Human Genomics submission-format package

This package converts the R7A2A4 hostile-audit manuscript into a target-journal review and submission assembly for Human Genomics / Research.

Key state:

```text
PBC_PRIMARY_PROJECT = GO
R7A2A5_MACHINE_QA = PASS_55_FAIL_0
TARGET_JOURNAL = Human Genomics
ARTICLE_TYPE = Research
SUBMISSION_STATE = AWAITING_AUTHOR_METADATA
NEW_BIOLOGICAL_ANALYSIS_REQUIRED = NO
NEXT = R7A2A6_AUTHOR_METADATA_AND_FINAL_SUBMISSION_QA
```

The manuscript contains explicit placeholders for authorship, affiliations, correspondence, CRediT, funding, competing interests and local ethics/waiver wording. Do not submit until those fields are completed and approved by every author.

The PDFs were generated in background mode with WPS Office. LibreOffice was not used. The manuscript PDF is a review copy; the DOCX is the submission-editable source.

Use `reports/99_CMM_R7A2A5_详细行动记录_2026-09-30.md` for the full audit trail and `results/R7A2A5_final_QA.json` for deterministic QA.
"""
(STAGE / "README.md").write_text(readme, encoding="utf-8")

files = sorted(p for p in STAGE.rglob("*") if p.is_file() and p.name != "checksums.sha256")
checksum_lines = [f"{sha256(path)}  {path.relative_to(STAGE).as_posix()}" for path in files]
(STAGE / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

if ZIP_PATH.exists():
    ZIP_PATH.unlink()
with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted(p for p in STAGE.rglob("*") if p.is_file()):
        archive.write(path, (Path(NAME) / path.relative_to(STAGE)).as_posix())

with zipfile.ZipFile(ZIP_PATH) as archive:
    bad_member = archive.testzip()
    entries = archive.namelist()
if bad_member is not None:
    raise RuntimeError(f"ZIP CRC failure: {bad_member}")

zip_sha = sha256(ZIP_PATH)
SIDECAR.write_text(f"{zip_sha}  {ZIP_PATH.name}\n", encoding="utf-8")

manifest_failures = []
for line in (STAGE / "checksums.sha256").read_text(encoding="utf-8").splitlines():
    expected, rel = line.split("  ", 1)
    actual = sha256(STAGE / rel)
    if actual != expected:
        manifest_failures.append(rel)

result = {
    "release_directory": str(STAGE),
    "zip": str(ZIP_PATH),
    "zip_sha256": zip_sha,
    "zip_entries": len(entries),
    "zip_crc": "PASS",
    "internal_checksums": f"PASS_{len(checksum_lines)}_OF_{len(checksum_lines)}" if not manifest_failures else f"FAIL_{len(manifest_failures)}",
    "bytes": ZIP_PATH.stat().st_size,
}
RECEIPT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
