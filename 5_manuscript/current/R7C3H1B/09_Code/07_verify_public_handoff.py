"""Portable checks for the exact-file candidate; aggregate evidence only.

Requires Python standard library. Does not render WPS or refit biological data.
"""
from pathlib import Path
import csv,hashlib,json,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'5_manuscript/current/R7C3H1B'
BASE=ROOT/'5_manuscript/current/R7C3H'
checks=[]
def test(name,v):checks.append((name,bool(v)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with (OUT/'06_QA/UPLOAD_CANDIDATE_MANIFEST.tsv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
test('13 candidate upload files',len(rows)==13)
test('one main manuscript',sum(r['portal_role']=='Main Manuscript' for r in rows)==1)
for row in rows:
    p=OUT/row['relative'];test('identity '+row['portal_role'],p.stat().st_size==int(row['bytes']) and sha(p)==row['sha256'])
for p in sorted((OUT/'05_Source_Data').glob('*.zip')):
    test('immutable science '+p.name,sha(p)==sha(BASE/'05_Source_Data'/p.name))
    with zipfile.ZipFile(p) as z:
        test('CRC '+p.name,z.testzip() is None)
        for line in z.read('checksums.sha256').decode('utf-8-sig').splitlines():
            if not line.strip():continue
            h,rel=line.split(None,1);rel=rel.strip().lstrip('*')
            test('source member '+p.name+'/'+rel,hashlib.sha256(z.read(rel)).hexdigest()==h)
test('27 exact figure masters',sum(sha(p)==sha(BASE/'02_Figures'/p.name) for p in (OUT/'02_Figures').iterdir() if p.is_file())==27)
test('workbook exact',sha(OUT/'03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx')==sha(BASE/'03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
with zipfile.ZipFile(OUT/'01_Manuscript/Manuscript_SubmissionCandidate.docx') as z:root=ET.fromstring(z.read('word/document.xml'))
text='\n'.join(''.join(p.itertext()) for p in root.findall('.//w:body/w:p',ns))
test('old code tag absent','r7c3f-full-audit-rebuilt-submission' not in text)
test('scientific tag linked',text.count('/tree/r7c3h0-statistical-reproducibility-closure-2026-10-13')==2)
test('two native LD equations',len(root.findall('.//m:oMath',ns))==2)
test('FCRL3 TenK points to Figure3d',any('FCRL3 showed stable OneK1K' in s and 'Figure 3d' in s and 'Figure 5b' not in s for s in text.splitlines()))
test('three source archive roles','Source Data 1-3 provide' in text)
qa=json.loads((OUT/'06_QA/MACHINE_QA.json').read_text(encoding='utf-8'))
test('local machine receipt 43/43',qa['status']=='PASS' and qa['checks_passed']==qa['checks_total']==43)
visual=json.loads((OUT/'06_QA/VISUAL_REVIEW_RECEIPT.json').read_text(encoding='utf-8'))
test('32 actual local proof pages',visual['total_pages']==32 and visual['status']=='PASS_LOCAL_VISUAL_REVIEW')
for p in visual['pdfs']:test('visual proof identity '+p['role'],sha(OUT/p['relative'])==p['sha256'])
state=json.loads((OUT/'08_Protocol/HANDOFF_STATE.json').read_text(encoding='utf-8'))
test('journal not falsely submitted',state['journal_submission']=='NOT_EXECUTED')
test('pending exact-file author approval explicit',state['fresh_exact_version_author_approval']=='PENDING')
result=dict(status='PASS' if all(v for _,v in checks) else 'FAIL',passed=sum(v for _,v in checks),total=len(checks),failed=[n for n,v in checks if not v],scope='Candidate byte identities, aggregate archives, navigation and local proof receipts; not fresh WPS inspection or raw scientific refits')
print(json.dumps(result));assert result['status']=='PASS',result['failed']
