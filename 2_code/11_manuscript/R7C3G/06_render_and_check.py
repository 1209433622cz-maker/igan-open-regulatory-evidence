from pathlib import Path
import json, re, hashlib, csv, shutil
import pymupdf
from PIL import Image,ImageOps,ImageDraw
from docx import Document

R=Path(r'H:\SCI2\YR1')
O=R/'5_manuscript/R7C3G_ExpertNarrative_20261012'
A=R/'5_analysis/R7C3G_ExpertNarrative_20261012'
Q=O/'06_QA'; V=A/'VISUAL_REVIEW'; V.mkdir(exist_ok=True)
checks=[]
def check(name,ok,detail):checks.append({'check':name,'pass':bool(ok),'detail':str(detail)})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Supporting historical masters are not duplicate current upload files.
arch=Q/'Archived_supporting_masters';arch.mkdir(exist_ok=True)
for p in (O/'02_Figures').glob('Supplementary_Figure_*_SOURCE.pdf'):
 shutil.move(str(p),str(arch/p.name))
pages=[];current_visual=set()
for p in [*sorted((O/'01_Manuscript').glob('*.pdf')),*sorted((O/'03_Supplement').glob('*.pdf')),*sorted((O/'04_Cover').glob('*.pdf'))]:
 d=pymupdf.open(p);thumbs=[]
 for i,pg in enumerate(d):
  txt=pg.get_text();blocks=pg.get_text('blocks');outside=[b[:4] for b in blocks if b[4].strip() and (b[0]<-1 or b[1]<-1 or b[2]>pg.rect.width+1 or b[3]>pg.rect.height+1)]
  imgs=len(pg.get_images());name=f'{p.stem}_p{i+1:02d}.png';pix=pg.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25));pix.save(str(V/name))
  current_visual.add(name);im=Image.open(V/name).convert('RGB');im.thumbnail((400,565));canvas=Image.new('RGB',(425,605),'#e5e5e5');canvas.paste(im,((425-im.width)//2,30));ImageDraw.Draw(canvas).text((10,7),f'{p.stem[:37]} | p{i+1}',fill='black');thumbs.append(canvas)
  pages.append({'pdf':str(p.relative_to(O)),'page':i+1,'text_chars':len(txt.strip()),'images':imgs,'outside_bounds':outside,'caption_figures':re.findall(r'(?:Supplementary )?Figure (?:S)?[1-6]\. ',txt),'text':txt})
  check(f'{p.stem} p{i+1} nonblank',len(txt.strip())>25 or imgs>0,f'text={len(txt.strip())}, images={imgs}')
  check(f'{p.stem} p{i+1} page bounds',not outside,outside)
 for start in range(0,len(thumbs),6):
  sheet=Image.new('RGB',(1275,1210),'white')
  for j,im in enumerate(thumbs[start:start+6]):sheet.paste(im,((j%3)*425,(j//3)*605))
  cn=f'CONTACT_{p.stem}_{start//6+1:02d}.jpg';sheet.save(V/cn,quality=92);current_visual.add(cn)
 check(p.stem+' image/caption parity',all(x['caption_figures'] for x in pages if x['pdf']==str(p.relative_to(O)) and x['images']>0),'Image-containing pages also contain Figure captions')
for p in V.iterdir():
 if p.is_file() and p.suffix in ['.png','.jpg'] and p.name not in current_visual:
  archive=A/'VISUAL_REVIEW_SUPERSEDED';archive.mkdir(exist_ok=True);assert p.resolve().parent==V.resolve();shutil.move(str(p),str(archive/p.name))
check('WPS receipt hashes current',all(sha(O/x['docx'])==x['docx_sha256'] and sha(Path(x['pdf']))==x['pdf_sha256'] for x in json.loads((Q/'WPS_Export_Receipt.json').read_text(encoding='utf-8-sig'))),'4 DOCX/PDF pairs')
md=(O/'01_Manuscript/Manuscript_ExpertRebuilt.md').read_text(encoding='utf-8')
doc=Document(O/'01_Manuscript/Manuscript_ExpertRebuilt.docx')
t='\n'.join(p.text for p in doc.paragraphs)
check('Six main caption headings',len(re.findall(r'^Figure [1-6]\. ',t,re.M))==6,'Separate figure captions')
check('No old Figure6c callout','Figure 6c' not in t,'Redundant evidence schematic removed')
abstract=next(doc.paragraphs[i+1].text for i,p in enumerate(doc.paragraphs) if p.text=='Abstract');check('Abstract <=150 words',len(abstract.split())<=150,len(abstract.split()))
check('Title <=15 words',len(doc.paragraphs[0].text.split())==12,'12 words')
check('Main embedded figures six',len(doc.inline_shapes)==6,len(doc.inline_shapes))
review=Document(O/'01_Manuscript/Manuscript_AuthorReview_InlineFigures.docx')
check('Review embedded figures six',len(review.inline_shapes)==6,len(review.inline_shapes))
sup=Document(O/'03_Supplement/Supplementary_Information_ExpertRebuilt.docx')
check('SI embedded figures three',len(sup.inline_shapes)==3,len(sup.inline_shapes))
main_until_refs=t.split('References')[0]
order=[]
for x in re.findall(r'\[([0-9,\-– ]+)\]',main_until_refs):
 for item in x.split(','):
  if re.fullmatch(r'\s*\d+\s*',item):nums=[int(item)]
  elif re.fullmatch(r'\s*\d+[-–]\d+\s*',item):lo,hi=map(int,re.split('[-–]',item));nums=range(lo,hi+1)
  else:nums=[]
  for n in nums:
   if n not in order:order.append(n)
check('Reference first-occurrence order',order==list(range(1,20)),order)
B=R/'5_manuscript/R7C3F_SubmissionCandidate_20261012'
for p in (O/'05_Source_Data').glob('*.zip'):check(p.name+' unchanged',sha(p)==sha(B/'05_Source_Data'/p.name),sha(p))
p=O/'03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx';check('Original workbook unchanged',sha(p)==sha(B/'03_Supplement'/p.name),sha(p))
check('Baseline source manuscript unchanged',sha(B/'01_Main/Manuscript.docx')=='d862dcc8e2e6830b28730f3c1dca5327b3dae5f4afe7a7a0e4147a5df49498aa',sha(B/'01_Main/Manuscript.docx'))
vals=json.loads((Q/'FIGURE_VALUES.json').read_text(encoding='utf-8'));check('Figure S3 uses full CS sizes',vals['S3']['sizes']==[19,17],vals['S3']['sizes'])
check('PBMC source-cell ceiling retained','PBMC designated as its best cell context' in t and 'PBMC best cell context' in t,'Methods and legend')
with (O/'03_Supplement/Supplementary_Editorial_Panel_Crosswalk.tsv').open(encoding='utf-8-sig',newline='') as f:cross=list(csv.DictReader(f,delimiter='\t'))
check('S10 historical/current panel crosswalk complete',len(cross)==37 and len({x['historical_record_id'] for x in cross})==37,'27 historical claims +10 MethodsResults rows')
check('S10 C17 supersession explicitly annotated',any(x['historical_record_id']=='C17' and 'SUPERSEDED' in x['scientific_content_status'] for x in cross),'Source ZIP unchanged; current S11 route supplied')
for p in sorted((O/'02_Figures').glob('*.pdf')):
 d=pymupdf.open(p);pg=d[0];fonts=pg.get_fonts(full=True)
 check(p.stem+' vector master one page',len(d)==1,f'{len(d)} page, {len(fonts)} fonts, {pg.rect.width/72*25.4:.2f}x{pg.rect.height/72*25.4:.2f} mm')
 check(p.stem+' editable SVG available',p.with_suffix('.svg').is_file(),str(p.with_suffix('.svg').relative_to(O)))
 check(p.stem+' extracted text present',len(pg.get_text())>100,len(pg.get_text()))
with (Q/'DOCUMENT_MACHINE_QA.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=checks[0].keys(),delimiter='\t');w.writeheader();w.writerows(checks)
(Q/'WPS_PAGE_CONTENT_INDEX.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
(Q/'DOCUMENT_QA_STATE.json').write_text(json.dumps({'checks':len(checks),'pass':sum(x['pass'] for x in checks),'fail':[x for x in checks if not x['pass']],'pages':len(pages),'pdfs':len(set(x['pdf'] for x in pages)),'visual_review':'PENDING_HUMAN_MODEL_INSPECTION'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(pages),'checks':len(checks),'fails':[x for x in checks if not x['pass']],'contact_sheets':[str(p) for p in V.glob('CONTACT*')]}))
