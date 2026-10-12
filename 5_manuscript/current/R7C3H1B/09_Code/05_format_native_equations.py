"""Represent the two existing LD definitions as native editable Word equations."""
from pathlib import Path
import hashlib,json,zipfile
from lxml import etree
ROOT=Path(r'H:\SCI2\YR1')
OUT=ROOT/'5_manuscript/R7C3H1B_ExactVersionHandoff_20261013'
DOC=OUT/'01_Manuscript/Manuscript_SubmissionCandidate.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
NS={'w':W,'m':M}
def elem(name):return etree.Element('{'+M+'}'+name)
def run(s):
    r=elem('r');p=etree.SubElement(r,'{'+M+'}rPr');sty=etree.SubElement(p,'{'+M+'}sty');sty.set('{'+M+'}val','p')
    t=etree.SubElement(r,'{'+M+'}t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=s
    return r
def script(base,power,kind='sSup'):
    r=elem(kind);e=etree.SubElement(r,'{'+M+'}e');e.append(run(base))
    k=etree.SubElement(r,'{'+M+'}'+('sup' if kind=='sSup' else 'sub'));k.append(run(power));return r
def equation1():
    r=elem('oMath');r.extend([script('G','*'),run(' = [I − C')])
    inv=elem('sSup');e=etree.SubElement(inv,'{'+M+'}e');e.extend([run('('),script('C','T'),run('C)')])
    p=etree.SubElement(inv,'{'+M+'}sup');p.append(run('−1'))
    r.extend([inv,script('C','T'),run(']G,')]);return r
def equation2():
    r=elem('oMath');r.extend([run('and '),script('R','QTL','sSub'),run(' = cor('),script('G','*'),run(').')]);return r
with zipfile.ZipFile(DOC) as z:entries={i.filename:(i,z.read(i.filename)) for i in z.infolist()}
root=etree.fromstring(entries['word/document.xml'][1]);receipts=[]
for before,builder,semantic in [
    ('G* = [I - C(C^T C)^-1 C^T]G,',equation1,'G* = [I - C(C^T C)^-1 C^T]G,'),
    ('and R_QTL = cor(G*).',equation2,'and R_QTL = cor(G*).')]:
    ps=[p for p in root.xpath('.//w:body/w:p',namespaces=NS) if ''.join(p.xpath('.//w:t/text()',namespaces=NS))==before]
    assert len(ps)==1,before
    p=ps[0]
    for child in list(p):
        if child.tag!='{'+W+'}pPr':p.remove(child)
    math=builder();p.append(math)
    receipts.append(dict(before=before,semantic_equation=semantic,omml_sha256=hashlib.sha256(etree.tostring(math)).hexdigest()))
entries['word/document.xml']=(entries['word/document.xml'][0],etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True))
tmp=DOC.with_suffix('.tmp.docx')
with zipfile.ZipFile(tmp,'w') as z:
    for info,body in entries.values():z.writestr(info,body)
tmp.replace(DOC)
(OUT/'06_QA/NATIVE_EQUATION_LEDGER.json').write_text(json.dumps(dict(scope='Two existing LD equations; mathematical definitions unchanged',equations=receipts),indent=2),encoding='utf-8')
print('PASS: two native Word equations; definitions unchanged')
