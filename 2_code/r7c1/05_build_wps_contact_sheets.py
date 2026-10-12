#!/usr/bin/env python3
"""Create four-page contact sheets from the fully rendered WPS PDF pages."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(r"H:\SCI2\YR1\5_manuscript\R7C1_IL12RB2_ExternalValidation_ManuscriptFork\qa\wps_pages")


def main() -> None:
    files = sorted(ROOT.glob("page-*.png"))
    if not files:
        raise RuntimeError("No rendered WPS pages found")
    thumb_w, thumb_h, margin = 620, 877, 24
    for batch in range(0, len(files), 4):
        subset = files[batch:batch + 4]
        sheet = Image.new("RGB", (2 * thumb_w + 3 * margin, 2 * thumb_h + 3 * margin), "white")
        draw = ImageDraw.Draw(sheet)
        for index, path in enumerate(subset):
            image = Image.open(path).convert("RGB")
            image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            x = margin + (index % 2) * (thumb_w + margin) + (thumb_w - image.width) // 2
            y = margin + (index // 2) * (thumb_h + margin) + (thumb_h - image.height) // 2
            sheet.paste(image, (x, y))
            draw.text((x + 4, y + 4), path.stem, fill="red", stroke_fill="white", stroke_width=2)
        sheet.save(ROOT / f"contact_{batch // 4 + 1:02d}.png")
    print(f"pages={len(files)} contacts={(len(files) + 3) // 4}")


if __name__ == "__main__":
    main()
