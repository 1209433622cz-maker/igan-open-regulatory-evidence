"""Read-only figure inventory and local previews; never modifies scientific assets."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(r'H:\SCI2\YR1')
FIG = ROOT / '4_figures'
OUT = ROOT / '5_analysis/R7C3D_FigureClassification_20261012'
PREVIEW = OUT / 'previews'
if (OUT/'before_inventory.json').exists():
    raise RuntimeError('Baseline inventory is already frozen; use 04_verify_and_report.py for post-organization checks.')
OUT.mkdir(parents=True, exist_ok=True)
PREVIEW.mkdir(exist_ok=True)
records = []
panels = []
font = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 22)
small = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 18)
for p in sorted(FIG.rglob('*')):
    if not p.is_file():
        continue
    data = p.read_bytes()
    rec = {'old_relative': p.relative_to(ROOT).as_posix(), 'bytes': len(data),
           'sha256': hashlib.sha256(data).hexdigest(), 'extension': p.suffix.lower()}
    if p.suffix.lower() == '.png':
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            rec['width'], rec['height'] = im.size
            rec['mode'] = im.mode
            rec['dpi'] = im.info.get('dpi')
            thumb = ImageOps.contain(im.convert('RGB'), (1510, 810))
        panel = Image.new('RGB', (1600, 885), 'white')
        panel.paste(thumb, ((1600-thumb.width)//2, 50))
        draw = ImageDraw.Draw(panel)
        draw.text((18, 12), f'{len(panels)+1:02d} | {p.parent.name} | {p.stem}', font=small, fill='black')
        panels.append(panel)
        preview = PREVIEW / f'{p.parent.name}__{p.stem}.png'
        panel.save(preview)
        rec['preview'] = preview.relative_to(ROOT).as_posix()
    elif p.suffix.lower() == '.pdf':
        with pymupdf.open(p) as doc:
            rec['pages'] = len(doc)
            rec['text'] = '\n'.join(page.get_text() for page in doc)
            rec['page_sizes'] = [list(page.rect) for page in doc]
            for i, page in enumerate(doc):
                pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
                pix.save(PREVIEW / f'{p.parent.name}__{p.stem}__PDF_page{i+1}.png')
    elif p.suffix.lower() == '.svg':
        tree = ET.fromstring(data)
        rec['viewBox'] = tree.get('viewBox')
        rec['svg_comments'] = re.findall(r'<!--\s*(.*?)\s*-->', data.decode('utf-8'), flags=re.S)
        with pymupdf.open(p) as doc:
            for i, page in enumerate(doc):
                page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).save(
                    PREVIEW / f'{p.parent.name}__{p.stem}__SVG_page{i+1}.png')
    elif p.suffix.lower() in {'.tsv', '.json', '.md'}:
        rec['text'] = data.decode('utf-8-sig')
    records.append(rec)
for i in range(0, len(panels), 2):
    sheet = Image.new('RGB', (1600, 1770), '#dddddd')
    for j, panel in enumerate(panels[i:i+2]):
        sheet.paste(panel, (0, j*885))
    sheet.save(PREVIEW / f'contact_{i//2+1:02d}.jpg', quality=94)
(OUT/'before_inventory.json').write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'files': len(records), 'unique_png_figures': len(panels),
                  'image_files': sum(r['extension'] in {'.png','.pdf','.svg'} for r in records),
                  'total_bytes': sum(r['bytes'] for r in records), 'output': str(OUT)}, ensure_ascii=False))
