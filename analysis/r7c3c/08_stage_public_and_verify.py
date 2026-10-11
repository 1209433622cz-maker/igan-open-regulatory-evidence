"""Selective staging + canonical Git-blob manifest and release privacy checks.

Never stage the project root or raw data. Content hashes are calculated from the
actual Git index blobs, so core.autocrlf cannot make a cross-platform manifest
falsely fail. Candidate assets have -text attributes to preserve WPS identities.
"""
import subprocess,json,hashlib,csv,re,zipfile,io,importlib.util
from pathlib import Path
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit',HERE/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=a.ROOT;OUT=a.OUT;REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence'

def git(*args):
    r=subprocess.run(['git',*args],cwd=REPO,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return r.stdout
def load(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def copy_code():
    import shutil
    for p in HERE.iterdir():
        if p.is_file() and p.suffix in ('.py','.R'):shutil.copy2(p,REPO/'analysis/r7c3c'/p.name)

def main():
    copy_code()
    att=REPO/'.gitattributes'
    if not att.exists():att.write_text('# Preserve exact submission-candidate file identities through Git.\nmanuscript/r7c3c/** -text whitespace=cr-at-eol\nmanuscript/r7c3b_review/** -text\n',encoding='utf-8')
    else:
        s=att.read_text(encoding='utf-8')
        if 'manuscript/r7c3c/** -text' not in s:s+='\nmanuscript/r7c3c/** -text whitespace=cr-at-eol\nmanuscript/r7c3b_review/** -text\n'
        s=s.replace('manuscript/r7c3c/** -text\n','manuscript/r7c3c/** -text whitespace=cr-at-eol\n');att.write_text(s,encoding='utf-8')
    wanted=['.gitattributes','.zenodo.json','CITATION.cff','README.md','analysis/r7c3b','analysis/r7c3c','audit/r7c3c','data/R7C3C_LARGE_ASSET_POINTERS.tsv','manuscript/r7c3b_review','manuscript/r7c3c','reports/r7c3c']
    payload=load(OUT/'github/PUBLIC_PAYLOAD_IDENTITIES.tsv')
    wanted+=sorted(set(r['path'] for r in payload if r['role']=='PATH_ONLY_RUNTIME_ADAPTER_IDENTICAL_ORIGINAL'))
    git('add','--',*wanted)
    git('add','-f','--','manuscript/r7c3c/05_Source_Data/Source_Data_1_Primary_Machine_Readable_Data.zip','manuscript/r7c3c/05_Source_Data/Source_Data_2_External_Regulatory_Evidence.zip')
    items=[]
    for raw in git('ls-files','--stage','-z').decode('utf-8').split('\0'):
        if not raw:continue
        left,path=raw.split('\t',1);mode,oid,stage=left.split()
        if stage!='0':raise SystemExit('Unmerged index '+path)
        if path!='MANIFEST.sha256':items.append((path,oid))
    changed=set(git('diff','--cached','--name-only','-z').decode('utf-8').strip('\0').split('\0'))
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=REPO,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    cache={};rows=[];blocked=[];all_issues=[];candidate_pass=0
    forbid={'.bed','.bim','.fam','.bam','.cram','.vcf','.bcf','.h5ad','.npy','.npz','.pgen','.psam','.pvar'}
    for path,oid in sorted(items):
        if oid not in cache:
            proc.stdin.write((oid+'\n').encode());proc.stdin.flush();h=proc.stdout.readline().decode().split();n=int(h[2]);data=proc.stdout.read(n);proc.stdout.read(1)
            cache[oid]=data
        data=cache[oid];sha=hashlib.sha256(data).hexdigest();issues=[]
        if len(data)>10*1024**2:issues.append('FILE_OVER_10MiB')
        if path in changed and Path(path).suffix.lower() in forbid:issues.append('RAW_INDIVIDUAL_LEVEL_FORMAT')
        if Path(path).suffix.lower() in a.TEXT or Path(path).name in ('LICENSE','NOTICE.md','README.md'):
            txt=a.decode(data)
            if a.SECRET.search(txt):issues.append('EXPLICIT_CREDENTIAL_SIGNATURE')
        if path.startswith('manuscript/r7c3c/'):
            actual=a.digest(REPO/path)
            if actual!=sha:issues.append('SUBMISSION_BLOB_WORKTREE_IDENTITY_DIFFERS')
            else:candidate_pass+=1
        if path in changed and path.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if z.testzip():issues.append('ZIP_CRC_FAIL')
                for name in z.namelist():
                    if Path(name).suffix.lower() in forbid:issues.append('RAW_DATA_ZIP_MEMBER:'+name)
                    if Path(name).suffix.lower() in a.TEXT:
                        if a.SECRET.search(a.decode(z.read(name))):issues.append('CREDENTIAL_IN_ZIP')
        row={'path':path,'Git_blob_oid':oid,'bytes':len(data),'sha256_canonical_Git_blob':sha,'changed_this_release':path in changed,'issues':';'.join(issues)};rows.append(row)
        if issues:
            all_issues.append(row)
            if path in changed:blocked.append(row)
    proc.stdin.close();proc.wait()
    a.tsv(OUT/'github/ALL_TRACKED_CANONICAL_BLOB_AUDIT.tsv',rows)
    a.tsv(OUT/'github/STAGED_RELEASE_SCAN.tsv',[r for r in rows if r['changed_this_release']],list(rows[0]))
    if blocked:raise SystemExit('Public staging gate rejected selected files: '+str([r['path']+':'+r['issues'] for r in blocked]))
    # Any old oversized/pattern-bearing file is disclosed separately, not silently deleted.
    a.tsv(OUT/'github/PREEXISTING_PUBLIC_FINDINGS.tsv',all_issues,list(rows[0]))
    (REPO/'MANIFEST.sha256').write_text(''.join(r['sha256_canonical_Git_blob']+'  '+r['path']+'\n' for r in rows),encoding='utf-8',newline='\n')
    git('add','--','MANIFEST.sha256');git('diff','--cached','--check')
    # Candidate package manifest must also verify against its actual canonical committed blobs.
    index={r['path']:r for r in rows};manifest=(REPO/'manuscript/r7c3c/checksums.sha256').read_text(encoding='utf-8-sig')
    own=0
    for line in manifest.splitlines():
        h,name=line.split('  ',1);rec=index['manuscript/r7c3c/'+name]
        if h!=rec['sha256_canonical_Git_blob']:raise SystemExit('Candidate internal hash differs in Git '+name)
        own+=1
    state={'tracked_without_manifest':len(rows),'staged_files':len(changed|{'MANIFEST.sha256'}),'new_or_changed_bytes':sum(r['bytes'] for r in rows if r['changed_this_release']),'staged_secret_or_raw_data_blockers':len(blocked),'old_public_findings':len(all_issues)-len(blocked),'candidate_blob_identity_pass':candidate_pass,'candidate_internal_checksums_pass':own,'Git_manifest_basis':'Canonical index blob bytes; stable across core.autocrlf checkouts','diff_cached_check':'PASS','committed':False,'pushed':False}
    a.save_json(OUT/'github/PRE_PUSH_GATE.json',state)
    print(json.dumps(state,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
