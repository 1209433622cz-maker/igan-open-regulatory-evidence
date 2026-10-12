"""Inspect the portable R7C3G package without local-workspace paths."""

from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from pathlib import Path

from docx import Document
import pymupdf
from PIL import Image

from repo_layout import (
    CURRENT_PACKAGE,
    FIGURES_ROOT,
    PROTOCOLS_ROOT,
    REPO_ROOT,
    RESULTS_ROOT,
    runtime_output,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_tsv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    out = runtime_output("R7C3G_inspect")
    inputs = {
        "manuscript": CURRENT_PACKAGE / "01_Manuscript" / "Manuscript_ExpertRebuilt.docx",
        "plan": REPO_ROOT / "0_admin" / "docs" / "research_plans" / "PBC_研究计划书_RP_v4_20261011.docx",
        "supplement": CURRENT_PACKAGE / "03_Supplement" / "Supplementary_Information_ExpertRebuilt.docx",
        "manuscript_pdf": CURRENT_PACKAGE / "01_Manuscript" / "Manuscript_ExpertRebuilt.pdf",
    }
    missing = [name for name, path in inputs.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing required assets: {missing}")

    receipt: list[dict] = []
    for name, path in inputs.items():
        row = {
            "role": name,
            "path": path.relative_to(REPO_ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        if path.suffix.lower() == ".docx":
            document = Document(path)
            row.update(paragraphs=len(document.paragraphs), tables=len(document.tables))
        elif path.suffix.lower() == ".pdf":
            with pymupdf.open(path) as pdf:
                row.update(pages=len(pdf))
        receipt.append(row)

    figure_rows: list[dict] = []
    for path in sorted((CURRENT_PACKAGE / "02_Figures").glob("*.png")):
        with Image.open(path) as image:
            figure_rows.append(
                {
                    "path": path.relative_to(REPO_ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "width": image.width,
                    "height": image.height,
                }
            )

    archives: list[dict] = []
    for path in sorted((CURRENT_PACKAGE / "05_Source_Data").glob("*.zip")):
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            archives.append(
                {
                    "path": path.relative_to(REPO_ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "members": len(archive.namelist()),
                    "crc": "PASS" if bad_member is None else f"FAIL:{bad_member}",
                }
            )

    portable_objects: list[dict] = []
    for root in (RESULTS_ROOT, PROTOCOLS_ROOT):
        for path in sorted(root.rglob("*")):
            if path.is_file():
                portable_objects.append(
                    {
                        "path": path.relative_to(REPO_ROOT).as_posix(),
                        "bytes": path.stat().st_size,
                        "sha256": sha256(path),
                    }
                )

    payload = {
        "repo_root": str(REPO_ROOT),
        "current_package": CURRENT_PACKAGE.relative_to(REPO_ROOT).as_posix(),
        "required_inputs": receipt,
        "figure_pngs": figure_rows,
        "source_archives": archives,
        "portable_result_and_protocol_objects": len(portable_objects),
        "figure_root_exists": FIGURES_ROOT.is_dir(),
        "status": "PASS",
    }
    (out / "R7C3G_PORTABLE_INSPECTION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_tsv(out / "R7C3G_INPUT_RECEIPT.tsv", receipt)
    write_tsv(out / "R7C3G_FIGURE_RECEIPT.tsv", figure_rows)
    write_tsv(out / "R7C3G_PORTABLE_OBJECTS.tsv", portable_objects)
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": str(out),
                "figures": len(figure_rows),
                "portable_objects": len(portable_objects),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
