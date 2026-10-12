#!/usr/bin/env python3
"""Render WPS-exported PDFs to labelled contact sheets for visual QA."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"H:\SCI2\YR1\5_manuscript\R7C3H_StatisticalReproducibilityClosure_20261013")
OUT = Path(r"H:\SCI2\YR1\5_analysis\R7C3H0_StatisticalReproducibilityClosure_20261013\visual_wps")
PDFS = [
    ROOT / "01_Manuscript/Manuscript_ExpertRebuilt.pdf",
    ROOT / "01_Manuscript/Manuscript_AuthorReview_InlineFigures.pdf",
    ROOT / "03_Supplement/Supplementary_Information_ExpertRebuilt.pdf",
    ROOT / "04_Cover/Cover_Letter_ExpertRebuilt_DRAFT.pdf",
]


def main() -> None:
    if OUT.exists():
        resolved = OUT.resolve()
        workspace = Path(r"H:\SCI2\YR1").resolve()
        if workspace not in resolved.parents:
            raise RuntimeError(f"Refusing to remove output outside workspace: {resolved}")
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 24)
    records = []
    sheets = []
    for pdf_path in PDFS:
        doc = pymupdf.open(pdf_path)
        page_dir = OUT / pdf_path.stem
        page_dir.mkdir()
        images = []
        for index, page in enumerate(doc):
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(1.35, 1.35), alpha=False)
            page_path = page_dir / f"page_{index + 1:03d}.png"
            pixmap.save(page_path)
            image = Image.open(page_path).convert("RGB")
            images.append(image)
            records.append(
                {
                    "pdf": pdf_path.relative_to(ROOT).as_posix(),
                    "page": index + 1,
                    "width_points": page.rect.width,
                    "height_points": page.rect.height,
                    "text_characters": len(page.get_text().strip()),
                    "render": str(page_path),
                }
            )
        for start in range(0, len(images), 4):
            group = images[start : start + 4]
            thumb_w = 880
            resized = []
            for offset, image in enumerate(group):
                height = round(image.height * thumb_w / image.width)
                thumb = image.resize((thumb_w, height), Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", (thumb_w, height + 42), "white")
                canvas.paste(thumb, (0, 42))
                ImageDraw.Draw(canvas).text((12, 8), f"{pdf_path.stem} page {start + offset + 1}", fill="black", font=font)
                resized.append(canvas)
            cell_h = max(image.height for image in resized)
            sheet = Image.new("RGB", (thumb_w * 2, cell_h * 2), "#d9d9d9")
            for position, image in enumerate(resized):
                sheet.paste(image, ((position % 2) * thumb_w, (position // 2) * cell_h))
            sheet_path = OUT / f"{pdf_path.stem}_pages_{start + 1:03d}-{start + len(group):03d}.png"
            sheet.save(sheet_path, optimize=True)
            sheets.append(str(sheet_path))
        doc.close()
    payload = {"renderer": "WPS PDF then PyMuPDF raster", "pages": records, "contact_sheets": sheets}
    (OUT / "VISUAL_QA_RENDER_STATE.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pdfs": len(PDFS), "pages": len(records), "contact_sheets": len(sheets), "output": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
