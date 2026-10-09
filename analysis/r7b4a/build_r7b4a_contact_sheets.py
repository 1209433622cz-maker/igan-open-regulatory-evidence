#!/usr/bin/env python3
"""Build compact contact sheets from WPS-rendered PDF page images."""

from pathlib import Path
from PIL import Image, ImageDraw


BASE = Path(r"H:\SCI2\YR1\5_manuscript\R7B4A_HumanGenomics_SubmissionInterface\qa")


def contact(source: Path, output: Path, columns: int, thumb_width: int) -> None:
    paths = sorted(source.glob("*.png"))
    thumbs = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        ratio = thumb_width / image.width
        image = image.resize((thumb_width, int(image.height * ratio)), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (thumb_width + 20, image.height + 40), "white")
        canvas.paste(image, (10, 25))
        ImageDraw.Draw(canvas).text((10, 5), path.stem, fill="black")
        thumbs.append(canvas)
    rows = (len(thumbs) + columns - 1) // columns
    cell_width = max(image.width for image in thumbs)
    cell_height = max(image.height for image in thumbs)
    sheet = Image.new("RGB", (cell_width * columns, cell_height * rows), (232, 232, 232))
    for index, image in enumerate(thumbs):
        sheet.paste(image, ((index % columns) * cell_width, (index // columns) * cell_height))
    sheet.save(output)
    print(f"CONTACT_OK\t{output}\t{sheet.size}\t{len(paths)} pages")


def main() -> None:
    contact(BASE / "manuscript_pages_final", BASE / "manuscript_contact_final.png", 4, 290)
    contact(BASE / "cover_pages_final", BASE / "cover_contact_final.png", 1, 900)


if __name__ == "__main__":
    main()
