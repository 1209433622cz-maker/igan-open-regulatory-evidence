"""Independent package/publication guards. Never label unchanged PDFs as newly rendered."""
from pathlib import Path
import json, csv, hashlib, re, zipfile, ast, subprocess, sys
from xml.etree import ElementTree as ET
import pymupdf as fitz
ROOT=Path(r'H:\SCI2\YR1'); PUB=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
AN=ROOT/'5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012';PACK=ROOT/'5_manuscript/R7C3F_SubmissionCandidate_20261012'
SECRET=re.compile(rb'(?:ghp_[A-Za-z0-9]{30,}|gho_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def table(p):return list(csv.DictReader(p.open(encoding='utf-8-sig'),delimiter='\t'))
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    checks=[];details=[];errors=[]
    def check(name,ok,detail=''):
        checks.append({'check':name,'pass':bool(ok),'detail':detail})
        if not ok:errors.append(name)
    state=json.loads((AN/'STATE_BEFORE.json').read_text(encoding='utf-8'))
    check('FRESH_ALL_LOCAL_FILE_SHA',state['files']==state['fresh_full_sha256'] and not state['read_errors'] and state['changed_during_read']==0,str(state['files']))
    orig=ROOT/'5_manuscript/R7C3C_SubmissionCandidate_20261012'
    identities=table(PACK/'ASSET_IDENTITY_R7C3F.tsv');check('21_ORIGINAL_CONTENT_ASSETS',len(identities)==21)
    for r in identities:check('IDENTITY:'+r['path'],sha(PACK/r['path'])==r['sha256']==sha(orig/r['path']))
    for line in (PACK/'checksums.sha256').read_text(encoding='utf-8').splitlines():
        h,n=line.split('  ',1);check('SUBMISSION_SHA:'+n,sha(PACK/n)==h)
    sci=table(PACK/'06_Verification/Scientific_Source_Data_48_Identity.tsv');check('48_SCIENTIFIC_MEMBERS',len(sci)==48)
    for r in sci:
        with zipfile.ZipFile(PACK/'05_Source_Data'/r['new_archive']) as z:
            check('SOURCE_MEMBER:'+r['member'],hashlib.sha256(z.read(r['member'])).hexdigest()==r['science_sha256'])
    with zipfile.ZipFile(PACK/'01_Main/Manuscript.docx') as z:
        check('DOCX_CRC',z.testzip() is None)
        tree=ET.fromstring(z.read('word/document.xml'));ns='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        text=' '.join(''.join(n.itertext()) for n in tree.iter(ns+'t'))
        check('MAIN_HAS_6_DRAWINGS',sum(n.tag.endswith('}drawing') for n in tree.iter())==6)
        check('AUTHOR_NAMES',all(n in text for n in ['Zhi Chen','Teng Qi']))
        # External source Zenodo DOIs are legitimate citations. Repackaging has
        # not changed even one manuscript byte or minted a project DOI.
        check('NO_NEW_PROJECT_DOI_IN_REPACKAGING',sha(PACK/'01_Main/Manuscript.docx')==sha(orig/'01_Main/Manuscript.docx'))
        required=['6,923','5,460','642','486,000','160,782','12.41%','8.56%','32.99%','26.66%']
        check('KEY_NUMERICAL_TOKENS',all(n in text for n in required))
    for p in sorted(PACK.rglob('*.pdf')):
        with fitz.open(p) as d:
            check('PDF_PARSE:'+p.name,len(d)>0 and not d.is_encrypted,'pages='+str(len(d))+'; unchanged prior WPS/vector asset; not new visual proof')
    with zipfile.ZipFile(PACK/'03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx') as z:
        check('WORKBOOK_CRC',z.testzip() is None)
        t=ET.fromstring(z.read('xl/workbook.xml'));check('WORKBOOK_10_SHEETS',sum(n.tag.endswith('}sheet') for n in t.iter())==10)
    files=[p for p in sorted(PUB.rglob('*')) if p.is_file() and '.git' not in p.parts]
    for p in files:
        rel=p.relative_to(PUB).as_posix();b=p.read_bytes();ext=p.suffix.lower();status=[]
        if len(b)>10*1024**2:status.append('OVER_10MiB')
        if SECRET.search(b):status.append('CREDENTIAL_SIGNATURE')
        if ext in ['.bed','.bim','.fam','.bam','.rds','.h5ad','.npy','.npz','.vcf','.bcf'] or rel.startswith(('1_data/','node_modules/')) or '/node_modules/' in rel:status.append('RAW_OR_VENDOR_PAYLOAD')
        if ext in ['.zip','.docx','.xlsx']:
            try:
                with zipfile.ZipFile(p) as z:
                    if z.testzip() is not None:status.append('ZIP_CRC')
                    for i in z.infolist():
                        if i.is_dir():continue
                        if SECRET.search(z.read(i)):status.append('ARCHIVE_CREDENTIAL_SIGNATURE')
                        if Path(i.filename).suffix.lower() in ['.bed','.bim','.fam','.bam','.rds','.h5ad','.npy','.npz','.vcf','.bcf']:status.append('ARCHIVE_RAW_PAYLOAD')
            except Exception as e:status.append('ARCHIVE_PARSE:'+type(e).__name__)
        if ext=='.py':
            try:ast.parse(b.decode('utf-8-sig'))
            except Exception as e:status.append('PYTHON_PARSE:'+type(e).__name__)
        details.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'gate':'PASS' if not status else ';'.join(status)})
    bad=[r for r in details if r['gate']!='PASS'];check('PUBLIC_EVERY_FILE_GATE',not bad,f'{len(files)} files; failures={len(bad)}')
    # README links are local navigation; verify exact case-independent Windows targets.
    link_fail=[]
    for name in ['README.md','DATA_AVAILABILITY.md']:
        for target in re.findall(r'\]\(([^)]+)\)',(PUB/name).read_text(encoding='utf-8')):
            if target.startswith(('http','mailto:','#')):continue
            if not (PUB/target).exists():link_fail.append(name+':'+target)
    check('README_LOCAL_LINKS',not link_fail,';'.join(link_fail))
    # Frozen old history will be restored; scan its blobs without emitting content.
    mirror=ROOT/'9.Version/github_rebuild/R7C3F_20261012/remote_mirror.git'
    hist_bad=[];hist_count=0
    if mirror.exists():
        out=subprocess.check_output(['git','--git-dir',str(mirror),'rev-list','--objects','--all'],text=True,encoding='utf-8')
        proc=subprocess.Popen(['git','--git-dir',str(mirror),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        for line in out.splitlines():
            oid=line.split(' ',1)[0];proc.stdin.write((oid+'\n').encode());proc.stdin.flush()
            head=proc.stdout.readline().decode().strip().split();n=int(head[-1]);b=proc.stdout.read(n);proc.stdout.read(1)
            if head[1]=='blob':
                hist_count+=1
                if SECRET.search(b):hist_bad.append({'object':oid,'path':line.split(' ',1)[1] if ' ' in line else ''})
        proc.stdin.close();proc.wait();check('HISTORICAL_GIT_BLOB_CREDENTIAL_GATE',not hist_bad,f'{hist_count} blobs')
    else:check('HISTORICAL_MIRROR_PRESENT',False)
    save(AN/'QA_DETAILS.json',{'checks':checks,'public_file_findings':bad,'historical_credential_findings':hist_bad})
    with (AN/'PUBLIC_FILE_QA.tsv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,delimiter='\t',fieldnames=list(details[0]));w.writeheader();w.writerows(details)
    result={'pass':not errors,'checks':len(checks),'passed':sum(x['pass'] for x in checks),'failed':errors,'public_files':len(files),'public_bytes':sum(x['bytes'] for x in details),'public_largest_bytes':max(x['bytes'] for x in details),'historical_git_blobs_scanned':hist_count,'original_content_assets_unchanged':21,'scientific_source_members_unchanged':48,'new_biological_analysis':False,'new_render_or_portal_proof':False}
    save(AN/'QA_STATE.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
