#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(r"H:\SCI2\YR1\5_manuscript\R7C2_Q1_JournalRealityCheck_DualTrackSubmission\qa")


def build(source: Path, output: Path) -> tuple[int, int]:
    files = sorted(source.glob("page-*.png"))
    output.mkdir(parents=True, exist_ok=True)
    thumb_w, thumb_h, margin = 620, 877, 24
    for batch in range(0, len(files), 4):
        subset = files[batch:batch + 4]
        sheet = Image.new("RGB", (2 * thumb_w + 3 * margin, 2 * thumb_h + 3 * margin), "white")
        draw = ImageDraw.Draw(sheet)
        for index, path in enumerate(subset):
            page = Image.open(path).convert("RGB")
            page.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            x = margin + (index % 2) * (thumb_w + margin) + (thumb_w - page.width) // 2
            y = margin + (index // 2) * (thumb_h + margin) + (thumb_h - page.height) // 2
            sheet.paste(page, (x, y))
            draw.text((x + 4, y + 4), path.stem, fill="red", stroke_fill="white", stroke_width=2)
        sheet.save(output / f"contact_{batch // 4 + 1:02d}.png")
    return len(files), (len(files) + 3) // 4


def main():
    for name in ("manuscript", "cover", "supplement"):
        pages, contacts = build(ROOT / f"wps_{name}_v2", ROOT / f"contact_{name}_v2")
        print(f"{name}\tpages={pages}\tcontacts={contacts}")


if __name__ == "__main__":
    main()
