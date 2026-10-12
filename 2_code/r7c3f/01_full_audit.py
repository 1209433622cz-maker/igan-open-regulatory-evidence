"""Fresh byte audit of every physical workspace file; extended Windows paths.
Content schemas are reused ONLY when the newly computed SHA equals the prior
audited identity. No deletion, no individual-level payload publication.
"""
from pathlib import Path
import os, stat, csv, json, time, hashlib, importlib.util
from collections import Counter, defaultdict
ROOT=Path(r'H:\SCI2\YR1')
OUT=ROOT/'5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012'
spec=importlib.util.spec_from_file_location('prior',ROOT/'2_code/00_workspace_management/R7C3C_20261012/01_full_audit.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
def ex(p):return prior.extended(p)
def sha(p):return prior.digest(p)
def write(name,rows,fields=None):prior.tsv(OUT/name,rows,fields)
def save(name,obj):prior.save_json(OUT/name,obj)
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cache={}
    for p in [ROOT/'5_analysis/R7C3C_WorkspaceAudit_Organization_20261012/before/ALL_FILES.tsv',ROOT/'5_analysis/R7C3E_SubfolderOrganization_20261012/ALL_CURRENT_FILES_CLOSING.tsv']:
        if p.exists():
            with p.open(encoding='utf-8-sig',newline='') as f:
                for row in csv.DictReader(f,delimiter='\t'):cache[row['relative_path']]=row
    physical=[];links=[];errors=[];directories=[]
    # Freeze the enumeration before any later staging/backup is created.
    for cur,ds,fs in os.walk(ex(ROOT)):
        normal=Path(cur.removeprefix('\\\\?\\'))
        if normal==OUT or OUT in normal.parents:ds[:]=[];continue
        keep=[]
        for n in ds:
            if os.lstat(ex(normal/n)).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:links.append({'path':(normal/n).relative_to(ROOT).as_posix(),'reason':'reparse target is not counted twice'})
            else:keep.append(n)
        ds[:]=keep;directories.append(normal.relative_to(ROOT).as_posix())
        for n in fs:physical.append(normal/n)
    rows=[];start=time.time();last=start;total=0
    for p in sorted(physical,key=lambda x:str(x).casefold()):
        rel=p.relative_to(ROOT).as_posix();r={'relative_path':rel,'top_level':rel.split('/')[0],'size_bytes':0,'mtime_ns':0,'sha256':'','hash_state':'READ_ERROR','extension':p.suffix.lower() or '[none]'}
        try:
            s=os.stat(ex(p));r.update(size_bytes=s.st_size,mtime_ns=s.st_mtime_ns,sha256=sha(p),hash_state='FRESH_FULL_SHA256')
            total+=s.st_size;r['category'],r['publication_policy']=prior.classify(rel)
            old=cache.get(rel,{})
            keys=['content_status','content_detail','title','stage_tokens','status_tokens','rows_or_pages','secret_signature_hits','parse_error','role','handling','future_use','project','primary_stage']
            if old.get('sha256')==r['sha256'] and old.get('content_status'):
                r.update({k:old.get(k,'') for k in keys});r['content_basis']='PRIOR_CONTENT_REVIEW_OF_IDENTICAL_FRESH_HASH'
            else:r.update(prior.summarize(p,rel,s.st_size));r['content_basis']='CURRENT_CONTENT_SCHEMA_READ'
            end=os.stat(ex(p))
            if end.st_size!=s.st_size or end.st_mtime_ns!=s.st_mtime_ns:r['hash_state']='CHANGED_DURING_READ'
        except Exception as e:
            r['parse_error']=type(e).__name__+':'+str(e)[:250];errors.append({'path':rel,'error':r['parse_error']})
        rows.append(r)
        if time.time()-last>20:print(json.dumps({'files':len(rows),'GiB':round(total/1024**3,3),'seconds':round(time.time()-start)}),flush=True);last=time.time()
    fields=sorted({k for r in rows for k in r});write('ALL_FILES_FRESH_SHA256.tsv',rows,fields)
    write('READ_ERRORS.tsv',errors,['path','error']);write('REPARSE_POINTS.tsv',links,['path','reason'])
    buckets=defaultdict(list)
    for r in rows:
        if r['sha256']:buckets[r['sha256']].append(r)
    dups=[{'sha256':h,'copies':len(rs),'size_each':rs[0]['size_bytes'],'relative_path':r['relative_path']} for h,rs in buckets.items() if len(rs)>1 for r in rs]
    write('EXACT_DUPLICATE_MEMBERS.tsv',dups,['sha256','copies','size_each','relative_path'])
    top=[{'folder':k,'files':sum(r['top_level']==k for r in rows),'bytes':sum(r['size_bytes'] for r in rows if r['top_level']==k)} for k in sorted({r['top_level'] for r in rows})]
    write('TOP_LEVEL_TOTALS.tsv',top)
    write('LARGE_FILES_OVER_10MiB_LOCAL.tsv',sorted([r for r in rows if r['size_bytes']>10*1024**2],key=lambda x:-x['size_bytes']),fields)
    write('CONTENT_PARSE_FINDINGS_LOCAL.tsv',[r for r in rows if r.get('parse_error')],fields)
    write('SECRET_SIGNATURE_FINDINGS_LOCAL.tsv',[{'path':r['relative_path'],'signature_count':r['secret_signature_hits']} for r in rows if str(r.get('secret_signature_hits','0')) not in ('','0')],['path','signature_count'])
    work=[r for r in rows if r['extension']=='.md' and (r['top_level'] in ('7.Report','9_Vote') or any(t in r['relative_path'].lower() for t in ['action_record','详细行动','decision','工作记录']))]
    write('WORK_RECORDS_LOCAL.tsv',work,fields)
    baseline=[r for r in rows if r['relative_path'].startswith(('5_manuscript/R7C3B_','5_manuscript/R7C3C_','4_figures/'))]
    write('FROZEN_MANUSCRIPT_AND_FIGURE_IDENTITIES.tsv',baseline,fields)
    state={'stage':'R7C3F','snapshot':'BEFORE_REBUILD','date':'2026-10-12','files':len(rows),'bytes':sum(r['size_bytes'] for r in rows),'GiB':sum(r['size_bytes'] for r in rows)/1024**3,'fresh_full_sha256':sum(r['hash_state']=='FRESH_FULL_SHA256' for r in rows),'read_errors':errors,'changed_during_read':sum(r['hash_state']=='CHANGED_DURING_READ' for r in rows),'reparse_points_excluded':len(links),'directories':len(directories),'work_records':len(work),'duplicate_groups':sum(len(x)>1 for x in buckets.values()),'duplicate_members':len(dups),'duplicate_copy_bytes':sum(rs[0]['size_bytes']*(len(rs)-1) for rs in buckets.values()),'content_parser_findings':sum(bool(r.get('parse_error')) for r in rows),'content_status_counts':dict(Counter(r.get('content_status','') for r in rows)),'elapsed_seconds':round(time.time()-start,2),'exclusions':'Own audit output directory only; junction targets not recursed; all other regular files including Git and runtimes included. New staging/backup files created after this frozen enumeration are separately inventoried.','limits':'Full-byte integrity is not full scientific validation. Raw genotype/BAM/RDS objects receive format/identity metadata; no false claim of row-by-row interpretation or complete statistical rerun.'}
    save('STATE_BEFORE.json',state);print(json.dumps(state,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
