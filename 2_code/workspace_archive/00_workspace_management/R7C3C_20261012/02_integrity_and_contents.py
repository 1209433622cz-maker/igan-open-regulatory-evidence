"""Validate archive identity, catalogue file contents, and explain limitations."""
import csv,json,time,zipfile,gzip,hashlib,importlib.util
from pathlib import Path
from collections import Counter
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit',HERE/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=a.ROOT;OUT=a.OUT

def load(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))

def main():
    rows=load(OUT/'before/ALL_FILES.tsv')
    previous=load(ROOT/'5_analysis/R7C3_FullWorkspaceAudit_2026-10-11/integrity/R7C3_archive_integrity.tsv')
    old={r['sha256']:r for r in previous if r['sha256'] and r['status']=='PASS'}
    receipts=[];last=time.time()
    for r in rows:
        rel=r['relative_path'];p=ROOT/rel;ext=p.suffix.lower()
        if r['category']=='GIT_INTERNAL':continue
        if ext not in ('.zip','.gz','.docx','.xlsx','.pptx','.xlsm','.docm'):continue
        res={'path':rel,'sha256':r['sha256'],'bytes':int(r['size_bytes']),'mode':'','status':'','detail':'','expanded_bytes':0}
        if ext in ('.zip','.gz') and r['sha256'] in old:
            prev=old[r['sha256']];res.update(mode='REUSED_CRC_AFTER_FRESH_IDENTICAL_SHA256',status='PASS',detail='2026-10-11 full-stream receipt; exact bytes independently rehashed this round',expanded_bytes=int(prev['expanded_bytes_checked']))
        else:
            try:
                if ext=='.gz':
                    n=0
                    with gzip.open(a.extended(p),'rb') as f:
                        for b in iter(lambda:f.read(8*1024*1024),b''):n+=len(b)
                    res.update(mode='FRESH_FULL_GZIP_CRC',status='PASS',expanded_bytes=n)
                else:
                    with zipfile.ZipFile(a.extended(p)) as z:
                        bad=z.testzip();res.update(mode='FRESH_ZIP_OFFICE_CRC',status='PASS' if bad is None else 'FAIL',detail=bad or '',expanded_bytes=sum(i.file_size for i in z.infolist()))
            except Exception as e:res.update(mode='FRESH_ARCHIVE_CHECK',status='FAIL',detail=type(e).__name__+':'+str(e)[:220])
        receipts.append(res)
        if time.time()-last>20:print(json.dumps({'archive_checks':len(receipts),'mode_counts':dict(Counter(x['mode'] for x in receipts))}),flush=True);last=time.time()
    a.tsv(OUT/'integrity/ARCHIVE_INTEGRITY.tsv',receipts)
    summary={'files':len(receipts),'pass':sum(r['status']=='PASS' for r in receipts),'fail':sum(r['status']!='PASS' for r in receipts),'mode_counts':dict(Counter(r['mode'] for r in receipts)),'crc_reuse_basis':'Only previous full-stream PASS receipts with exact SHA-256 equal to this round fresh full hash; not path, timestamp, or file-size equality.'}
    a.save_json(OUT/'integrity/STATE.json',summary)
    # Size, class, and stage counts are transparent; index files do not automatically count as scientific results.
    stages=Counter();ext=Counter();parsed=Counter()
    for r in rows:
        ext[r['extension']]+=1;parsed[r.get('content_status','')]+=1
        if r['category'] not in ('GIT_INTERNAL','ENVIRONMENT_OR_SKILL','PUBLIC_MIRROR'):
            for s in r.get('stage_tokens','').split(';'):
                if s:stages[s]+=1
    a.tsv(OUT/'contents/STAGE_SEARCH_INDEX.tsv',[{'stage_token':s,'matching_files':n,'meaning':'search pointers, not an estimate of independent results'} for s,n in sorted(stages.items())])
    a.tsv(OUT/'contents/EXTENSION_COUNTS.tsv',[{'extension':k,'count':v} for k,v in ext.most_common()])
    a.tsv(OUT/'contents/CONTENT_DEPTH_COUNTS.tsv',[{'content_depth':k,'count':v} for k,v in parsed.most_common()])
    # Markdown records are indexed in full locally, with current vs historical tags.
    records=load(OUT/'before/WORK_RECORD_INDEX.tsv');index=[]
    for r in records:
        p=ROOT/r['relative_path'];txt=a.read_text(p)
        heads=[x.strip() for x in txt.splitlines() if x.startswith('#')]
        index.append({'path':r['relative_path'],'title':r['title'],'bytes':r['size_bytes'],'sha256':r['sha256'],'stage_tokens':r['stage_tokens'],'headings':' | '.join(heads)[:2000],'use':'CURRENT_EDITORIAL_QA' if 'R7C3B' in r['relative_path'] else 'HISTORICAL_EVIDENCE_OR_WORK_RECORD','publication':'LOCAL_INDEX_REDACTION_REQUIRED'})
    a.tsv(OUT/'contents/WORK_RECORD_CONTENT_INDEX.tsv',index)
    print(json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
