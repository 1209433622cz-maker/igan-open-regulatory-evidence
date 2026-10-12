"""Bounded typographic edit: native Word exponents and support-set subscripts.

Does not change numerical values, model settings, paragraphs, equations or figures.
Run once on the newly prepared candidate before its final WPS proof.
"""
from pathlib import Path
from copy import deepcopy
import hashlib, json, re, zipfile, sys
from lxml import etree

ROOT = Path(r'H:\SCI2\YR1')
OUT = ROOT/'5_manuscript/R7C3H1B_ExactVersionHandoff_20261013'
DOC = Path(sys.argv[1]) if len(sys.argv)>1 else OUT/'01_Manuscript/Manuscript_SubmissionCandidate.docx'
is_main=DOC.name=='Manuscript_SubmissionCandidate.docx'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'
pattern=re.compile(r'(?:[x×])?10\^[-+]?\d+|S_[AM]')
with zipfile.ZipFile(DOC) as z:
    entries={i.filename:(i,z.read(i.filename)) for i in z.infolist()}
root=etree.fromstring(entries['word/document.xml'][1])
changes=[]

def newrun(template, value, alignment=None):
    r=deepcopy(template)
    for e in list(r):
        if e.tag != W+'rPr': r.remove(e)
    if alignment:
        props=r.find(W+'rPr')
        if props is None:
            props=etree.Element(W+'rPr');r.insert(0,props)
        for e in list(props):
            if e.tag==W+'vertAlign':props.remove(e)
        e=etree.SubElement(props,W+'vertAlign');e.set(W+'val',alignment)
    t=etree.SubElement(r,W+'t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=value
    return r

all_text=''.join(root.xpath('.//w:t/text()',namespaces=NS))
expected_matches=len(pattern.findall(all_text))
for r in list(root.xpath('.//w:r[w:t]',namespaces=NS)):
    ts=r.findall(W+'t')
    if len(ts)!=1:continue
    s=ts[0].text or ''
    matches=list(pattern.finditer(s))
    if not matches:continue
    assert all(e.tag in [W+'rPr',W+'t'] for e in r), 'Mixed run must not be duplicated'
    parts=[];cursor=0
    for m in matches:
        if m.start()>cursor:parts.append(newrun(r,s[cursor:m.start()]))
        token=m.group()
        if token.startswith('S_'):
            parts.extend([newrun(r,'S'),newrun(r,token[-1],'subscript')])
            kind='native_support_subscript';visible='S'+token[-1]
        else:
            base,exponent=token.split('^');base=base.replace('x','×')
            parts.extend([newrun(r,base),newrun(r,exponent,'superscript')])
            kind='native_power_superscript';visible=base+exponent
        changes.append(dict(before=token,after_visible_text=visible,format=kind))
        cursor=m.end()
    if cursor<len(s):parts.append(newrun(r,s[cursor:]))
    parent=r.getparent();index=parent.index(r)
    for k,new in enumerate(parts):parent.insert(index+k,new)
    parent.remove(r)
assert len(changes)==expected_matches and expected_matches>0, (len(changes),expected_matches)
entries['word/document.xml']=(entries['word/document.xml'][0],etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True))
temporary=DOC.with_suffix('.tmp.docx')
with zipfile.ZipFile(temporary,'w') as z:
    for info,body in entries.values():z.writestr(info,body)
temporary.replace(DOC)

md=OUT/'01_Manuscript/Manuscript_SubmissionCandidate.md'
sup=str.maketrans('-+0123456789','⁻⁺⁰¹²³⁴⁵⁶⁷⁸⁹')
def mdformat(m):
    token=m.group()
    if token.startswith('S_'):return 'S'+{'A':'ₐ','M':'ₘ'}[token[-1]]
    base,power=token.split('^');return base.replace('x','×')+power.translate(sup)
if is_main:md.write_text(pattern.sub(mdformat,md.read_text(encoding='utf-8')),encoding='utf-8')
receipt=dict(scope='Presentation only; values and scientific interpretation unchanged',
             changes=changes,native_power_count=sum(c['format']=='native_power_superscript' for c in changes),
             native_support_count=sum(c['format']=='native_support_subscript' for c in changes),
             docx_sha256=hashlib.sha256(DOC.read_bytes()).hexdigest())
(OUT/'06_QA'/('TYPOGRAPHY_CHANGE_LEDGER.json' if is_main else 'SUPPLEMENT_TYPOGRAPHY_CHANGE_LEDGER.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in receipt.items() if k!='changes'}))
