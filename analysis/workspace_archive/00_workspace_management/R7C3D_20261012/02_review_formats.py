"""Read-only cross-format structural checks and vector review contact sheets."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(r'H:\SCI2\YR1')
OUT = ROOT / '5_analysis/R7C3D_FigureClassification_20261012'
PRE = OUT / 'previews'
records = json.loads((OUT/'before_inventory.json').read_text(encoding='utf-8'))
checks, panels = [], []
font = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 15)
for rec in records:
    if rec['extension'] not in {'.pdf','.svg'}:
        continue
    p = ROOT/rec['old_relative']
    with pymupdf.open(p) as doc:
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False)
            vec = Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            png = Image.open(p.with_suffix('.png')).convert('RGB')
            a = np.asarray(png.resize((600,400)),dtype=float).mean(axis=2).ravel()
            b = np.asarray(vec.resize((600,400)),dtype=float).mean(axis=2).ravel()
            checks.append({'file': rec['old_relative'], 'page': i+1,
                           'grayscale_correlation': float(np.corrcoef(a,b)[0,1]),
                           'raster_vector_RMSE_0_255':float(np.sqrt(np.mean((a-b)**2))),
                           'scope':'Structural screen only; not pixel identity across formats.'})
            panel=Image.new('RGB',(1000,610),'white')
            thumb=ImageOps.contain(vec,(980,560));panel.paste(thumb,((1000-thumb.width)//2,45))
            ImageDraw.Draw(panel).text((10,10),p.parent.name+' | '+p.stem+' | '+p.suffix,font=font,fill='black')
            panels.append(panel)
for j in range(0,len(panels),4):
    sheet=Image.new('RGB',(2000,1220),'#dddddd')
    for k,panel in enumerate(panels[j:j+4]):sheet.paste(panel,((k%2)*1000,(k//2)*610))
    sheet.save(PRE/f'vector_contact_{j//4+1:02d}.jpg',quality=94)
current=[]
for i in range(1,7):
    for ext,name in [('.pdf',f'Figure_{i}.pdf'),('.png',f'Figure_{i}_embed.png')]:
        p=ROOT/'5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/02_Figures'/name
        data=p.read_bytes();r={'source':p.relative_to(ROOT).as_posix(),'figure':i,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        if ext=='.pdf':
            with pymupdf.open(p) as d:
                r['pages']=len(d);r['text']='\n'.join(x.get_text() for x in d)
                d[0].get_pixmap(matrix=pymupdf.Matrix(1.4,1.4),alpha=False).save(PRE/f'CURRENT_Figure_{i}__PDF.png')
        else:
            with Image.open(p) as im: im.verify()
        current.append(r)
(OUT/'vector_concordance.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
(OUT/'submission_reference_sources.json').write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'vector_files':len(checks),'min_structural_correlation':min(x['grayscale_correlation'] for x in checks),'reference_copy_sources':len(current)},ensure_ascii=False))
