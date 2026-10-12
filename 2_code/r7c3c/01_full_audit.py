"""Read-only, complete byte inventory; no deletion and no raw data publication.

Windows long paths are opened with the extended-length prefix. Inventory errors
never cause a file to disappear silently. Git implementation objects are counted
and hashed, but are not interpreted as research documents. Semantic review and
binary integrity are different columns, not interchangeable PASS labels.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, csv, hashlib, os, json, re, stat, zipfile, gzip, time
from xml.etree import ElementTree as ET

ROOT = Path(r'H:\SCI2\YR1')
OUT = ROOT/'5_analysis/R7C3C_WorkspaceAudit_Organization_20261012'
TEXT = {'.md','.txt','.csv','.tsv','.json','.jsonl','.yaml','.yml','.toml','.ini','.cfg','.py','.ps1','.r','.rmd','.sh','.cmd','.bat','.tex','.bib','.cff','.html','.xml','.log','.sha256','.md5','.svg','.sql'}
SECRET = re.compile(r'(?i)(?:ghp_[a-z0-9]{30,}|github_pat_[a-z0-9_]{35,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
STAGE = re.compile(r'(?i)\bR\d+[A-Z][A-Z0-9]*\b')
STATUS = re.compile(r'(?i)\b(?:PASS|FAIL|HOLD|GO|NO_GO|FROZEN|PENDING|COMPLETE|UNINFORMATIVE|FALSIFIED)\b')

def extended(p):
    s = os.path.abspath(str(p))
    return s if s.startswith('\\\\?\\') else '\\\\?\\'+s

def digest(p):
    h=hashlib.sha256()
    with open(extended(p),'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

def save_json(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def tsv(p,rows,fields=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,delimiter='\t',fieldnames=fields or list(rows[0] if rows else {'path':None}),extrasaction='ignore')
        w.writeheader();w.writerows(rows)

def decode(b):
    for e in ('utf-8-sig','utf-16','gb18030'):
        try:return b.decode(e)
        except UnicodeError:pass
    return b.decode('utf-8',errors='replace')

def read_text(p):
    with open(extended(p),'rb') as f:return decode(f.read())

def classify(rel):
    r=rel.lower()
    if '/.git/' in '/'+r:return 'GIT_INTERNAL','LOCAL_ONLY'
    if r.startswith(('tools/','.qiteng_v03242_runtime/')) or '/tooling/' in r or '/skills/' in r:
        return 'ENVIRONMENT_OR_SKILL','LOCAL_ONLY_THIRD_PARTY'
    if r.startswith('1_data/') or any(x in r for x in ('active_donors','pseudobulk','dosage','covariates','correlation.npy')):
        return 'SOURCE_OR_INDIVIDUAL_LEVEL','METADATA_ONLY_PUBLIC'
    if '/snapshots/' in r or r.startswith('9.version/'):
        return 'HISTORICAL_PROVENANCE','REVIEW_BEFORE_PUBLIC'
    if r.startswith(('7.report/','9_vote/')) or '详细行动' in rel or 'action_record' in r:
        return 'REPORT_OR_DECISION','REVIEW_BEFORE_PUBLIC'
    if r.startswith('5_manuscript/'):
        return 'MANUSCRIPT_VERSION','VERSION_APPROVAL_STATE_REQUIRED'
    if r.startswith(('github/','0_admin/repositories/')):return 'PUBLIC_MIRROR','TRACKED_CONTENT_REVIEW'
    return rel.split('/')[0],'REVIEW_BEFORE_PUBLIC'

def summarize(p,rel,size):
    ext=p.suffix.lower(); r={ 'content_status':'METADATA_ONLY','content_detail':'','title':'','stage_tokens':';'.join(sorted(set(STAGE.findall(rel.upper())))),'status_tokens':'','rows_or_pages':'','secret_signature_hits':0,'parse_error':''}
    if '/.git/' in '/'+rel.lower():return r
    try:
        if ext in TEXT or p.name.lower() in ('license','notice','makefile','.gitignore','.gitattributes'):
            # Full text for small/medium research files. Huge tables get an explicit prefix-schema status.
            with open(extended(p),'rb') as f:b=f.read() if size<=64*1024*1024 else f.read(2*1024*1024)
            txt=decode(b);lines=txt.splitlines();r['content_status']='FULL_TEXT_INDEXED' if len(b)==size else 'PREFIX_SCHEMA_ONLY'
            title=next((s.strip().lstrip('#').strip() for s in lines if s.strip()),'')
            r['title']=title[:220];r['stage_tokens']=';'.join(sorted(set(STAGE.findall(rel.upper()+'\n'+txt.upper()))))
            r['status_tokens']=';'.join(sorted(set(x.upper() for x in STATUS.findall(txt))))
            r['rows_or_pages']=len(lines);r['secret_signature_hits']=len(SECRET.findall(txt))
            if ext in ('.csv','.tsv'):r['content_detail']='header='+title[:240]
            if ext=='.json':
                try:
                    obj=json.loads(txt);r['content_detail']='JSON '+type(obj).__name__+' '+','.join(list(obj)[:16]) if isinstance(obj,dict) else 'JSON '+type(obj).__name__
                except Exception as e:r['parse_error']='JSON:'+type(e).__name__
            # Do not publish content previews of individual-level or secret-bearing files.
            if classify(rel)[1]=='METADATA_ONLY_PUBLIC' or r['secret_signature_hits']:r['title']='[restricted content preview]'
        elif ext in ('.docx','.xlsx','.pptx','.docm','.xlsm','.zip'):
            with zipfile.ZipFile(extended(p)) as z:
                infos=z.infolist();r['content_status']='ARCHIVE_MEMBER_INDEX';r['content_detail']=f'members={len(infos)};expanded_bytes={sum(i.file_size for i in infos)}'
                if ext in ('.docx','.docm'):
                    xml=ET.fromstring(z.read('word/document.xml'));ns='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
                    pars=[''.join(n.itertext()) for n in xml.iter(ns+'t')]
                    txt=' '.join(pars);r['title']=txt[:220];r['rows_or_pages']=len(pars);r['content_status']='DOCX_FULL_TEXT_AND_OBJECT_SCHEMA'
                    r['stage_tokens']=';'.join(sorted(set(STAGE.findall(rel.upper()+' '+txt.upper()))))
                    r['content_detail']+=';drawings='+str(sum(1 for n in xml.iter() if n.tag.endswith('}drawing')))
                elif ext in ('.xlsx','.xlsm'):
                    xml=ET.fromstring(z.read('xl/workbook.xml')); sheets=[n.attrib.get('name','') for n in xml.iter() if n.tag.endswith('}sheet')]
                    r['title']=';'.join(sheets);r['content_status']='WORKBOOK_SHEETS_AND_DIMENSIONS'
                    dims=[]
                    for i in infos:
                        if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',i.filename):
                            # XML streaming validates all worksheet content without allocating full data frames.
                            rows=0;dim=''
                            with z.open(i) as stream:
                                for _,n in ET.iterparse(stream,events=('end',)):
                                    if n.tag.endswith('}dimension'):dim=n.attrib.get('ref','')
                                    if n.tag.endswith('}row'):rows+=1
                                    n.clear()
                            dims.append(i.filename+':'+dim+':rows='+str(rows))
                    r['content_detail']+=';'+';'.join(dims)
        elif ext=='.pdf':
            import fitz
            with fitz.open(extended(p)) as d:
                text='\n'.join(page.get_text() for page in d)
                r['content_status']='PDF_ALL_PAGE_TEXT_INDEX';r['rows_or_pages']=len(d);r['title']=(text.splitlines() or [''])[0][:220]
                r['content_detail']='creator='+str(d.metadata.get('creator',''))
                r['stage_tokens']=';'.join(sorted(set(STAGE.findall(rel.upper()+' '+text.upper()))))
        elif ext in ('.png','.jpg','.jpeg','.tif','.tiff','.webp'):
            from PIL import Image
            with Image.open(extended(p)) as im:
                r['content_status']='IMAGE_HEADER';r['content_detail']=f'{im.format} {im.size} {im.mode}'
                im.verify();r['content_status']='IMAGE_INTEGRITY'
        elif ext=='.gz':
            with gzip.open(extended(p),'rb') as f:b=f.read(32768)
            r['content_status']='GZIP_PREFIX_SCHEMA';r['content_detail']=decode(b).splitlines()[0][:220] if b else 'EMPTY_UNCOMPRESSED_STREAM'
        else:
            with open(extended(p),'rb') as f:r['content_detail']='magic='+f.read(16).hex()
    except Exception as e:
        r['parse_error']=type(e).__name__+':'+str(e)[:350];r['content_status']='PARSER_LIMITATION_OR_INVALID_FILE'
    return r

def audit(label):
    dest=OUT/label;dest.mkdir(parents=True,exist_ok=True)
    rows=[];errors=[];links=[];directories=[];start=time.time();hashed_bytes=0;last=start
    for cur,ds,fs in os.walk(extended(ROOT)):
        normal=Path(cur.removeprefix('\\\\?\\'))
        if normal==OUT or OUT in normal.parents:ds[:]=[];continue
        # Do not follow symlink/junction directories: one physical asset, one count.
        keep=[]
        for n in ds:
            dp=Path(cur)/n
            if os.lstat(dp).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:links.append({'path':str(normal/n),'reason':'reparse point excluded from recursive content traversal'})
            else:keep.append(n)
        ds[:]=keep;directories.append(normal.relative_to(ROOT).as_posix())
        for name in fs:
            p=normal/name;rel=p.relative_to(ROOT).as_posix()
            row={'relative_path':rel,'top_level':rel.split('/')[0],'size_bytes':0,'mtime_ns':0,'sha256':'','hash_state':'','category':'','publication_policy':'','extension':p.suffix.lower() or '[none]'}
            try:
                s=os.stat(extended(p));row['size_bytes']=s.st_size;row['mtime_ns']=s.st_mtime_ns
                row['category'],row['publication_policy']=classify(rel)
                row['sha256']=digest(p);row['hash_state']='FRESH_FULL_SHA256';hashed_bytes+=s.st_size
                row.update(summarize(p,rel,s.st_size))
                if os.stat(extended(p)).st_mtime_ns!=s.st_mtime_ns:row['hash_state']='CHANGED_DURING_READ'
            except Exception as e:
                row['hash_state']='READ_ERROR';row['parse_error']=type(e).__name__+':'+str(e)[:350];errors.append({'path':rel,'error':row['parse_error']})
            rows.append(row)
            if time.time()-last>20:
                print(json.dumps({'progress_files':len(rows),'hashed_GiB':round(hashed_bytes/1024**3,2),'seconds':round(time.time()-start)},ensure_ascii=False),flush=True);last=time.time()
    rows.sort(key=lambda r:r['relative_path'].casefold())
    tsv(dest/'ALL_FILES.tsv',rows,sorted(set(k for r in rows for k in r)))
    tsv(dest/'READ_ERRORS.tsv',errors,['path','error']);tsv(dest/'REPARSE_POINTS.tsv',links,['path','reason'])
    (dest/'ALL_DIRECTORIES.txt').write_text('\n'.join(sorted(directories)),encoding='utf-8')
    groups=defaultdict(list)
    for r in rows:
        if r['sha256']:groups[r['sha256']].append(r)
    dup=[]
    for h,rs in groups.items():
        if len(rs)>1:
            for r in rs:dup.append({'sha256':h,'copies':len(rs),'size_each':r['size_bytes'],'relative_path':r['relative_path'],'category':r['category']})
    tsv(dest/'EXACT_DUPLICATE_MEMBERS.tsv',dup,['sha256','copies','size_each','relative_path','category'])
    top=[]
    for k in sorted(set(r['top_level'] for r in rows)):
        rs=[r for r in rows if r['top_level']==k];top.append({'folder':k,'files':len(rs),'bytes':sum(r['size_bytes'] for r in rs),'GiB':round(sum(r['size_bytes'] for r in rs)/1024**3,6)})
    tsv(dest/'TOP_LEVEL_TOTALS.tsv',top)
    tsv(dest/'LARGE_FILES_OVER_10MiB.tsv',sorted([r for r in rows if r['size_bytes']>10*1024**2],key=lambda r:-r['size_bytes']),list(rows[0]))
    tsv(dest/'CONTENT_PARSE_FINDINGS.tsv',[r for r in rows if r.get('parse_error')],list(rows[0]))
    tsv(dest/'SECRET_SIGNATURE_FINDINGS_LOCAL_ONLY.tsv',[{'path':r['relative_path'],'signature_count':r['secret_signature_hits']} for r in rows if r.get('secret_signature_hits')],['path','signature_count'])
    records=[r for r in rows if r['extension']=='.md' and (r['category']=='REPORT_OR_DECISION' or any(x in r['relative_path'].lower() for x in ('record','report','记录','总结','decision')))]
    tsv(dest/'WORK_RECORD_INDEX.tsv',records,list(rows[0]))
    state={'stage':'R7C3C','snapshot':label,'date':'2026-10-12','root':str(ROOT),'file_count':len(rows),'directory_count':len(directories),'bytes':sum(r['size_bytes'] for r in rows),'GiB':sum(r['size_bytes'] for r in rows)/1024**3,'fresh_full_sha256_count':sum(r['hash_state']=='FRESH_FULL_SHA256' for r in rows),'read_errors':len(errors),'content_parser_findings':sum(bool(r.get('parse_error')) for r in rows),'reparse_points':len(links),'duplicate_groups':sum(len(rs)>1 for rs in groups.values()),'duplicate_members':len(dup),'redundant_copy_bytes':sum(rs[0]['size_bytes']*(len(rs)-1) for rs in groups.values() if len(rs)>1),'work_record_count':len(records),'elapsed_seconds':round(time.time()-start,2),'audit_output_self_excluded':str(OUT),'scope_note':'Every discovered regular file hashed afresh, including Git objects. Semantic indexing varies by format and is explicitly labelled. No deletion. No assertion of full scientific validity from a hash.'}
    save_json(dest/'STATE.json',state);print(json.dumps(state,ensure_ascii=False),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--label',default='before');audit(a.parse_args().label)
