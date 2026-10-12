"""Independent remote fetch and full canonical-blob verification; never pushes."""
from pathlib import Path
import subprocess, json, hashlib, csv, collections, datetime

ROOT=Path(r'H:\SCI2\YR1')
REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
AN=ROOT/'5_analysis/R7C3G1_20261012'
BACKUP=ROOT/'0_admin/backups/R7C3G1_GitHubEightFolder_20261012'
REMOTE='https://github.com/1209433622cz-maker/igan-open-regulatory-evidence.git'
EXPECTED_DIRS={'0_admin','1_data','2_code','3_results','4_figures','5_manuscript','6_release','7.Report'}

def call(args, cwd=None):return subprocess.check_output(args,cwd=cwd).decode('utf-8').strip()
def g(repo,*args):return call(['git','-C',str(repo),*args])
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    bare=AN/'independent_remote.git'
    if not bare.exists():subprocess.run(['git','init','--bare',str(bare)],check=True,stdout=subprocess.DEVNULL)
    print('Fetching actual GitHub main into independent bare repository',flush=True)
    subprocess.run(['git','-C',str(bare),'fetch','--depth=1','--no-tags',REMOTE,'refs/heads/main'],check=True)
    remote_head=g(bare,'rev-parse','FETCH_HEAD')
    assert remote_head==g(REPO,'rev-parse','HEAD'), 'Remote HEAD differs from local publication HEAD'
    manifest=g(bare,'show',remote_head+':MANIFEST.sha256')
    rows=[line.split('  ',1) for line in manifest.splitlines() if line.strip()]
    ls=g(bare,'ls-tree','-rz','--name-only',remote_head).split('\0')
    names=set(ls)-{''}
    assert names=={r[1] for r in rows}|{'MANIFEST.sha256'}, 'Whole-tree manifest coverage failure'
    directories={p.split('/')[0] for p in names if '/' in p}
    assert directories==EXPECTED_DIRS, directories
    proc=subprocess.Popen(['git','-C',str(bare),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    verified={};totals=collections.defaultdict(lambda:[0,0])
    try:
        for expected,path in rows:
            proc.stdin.write((remote_head+':'+path+'\n').encode('utf-8'));proc.stdin.flush()
            header=proc.stdout.readline().decode().strip().split()
            assert len(header)==3 and header[1]=='blob', path
            n=int(header[2]);body=proc.stdout.read(n);proc.stdout.read(1)
            digest=hashlib.sha256(body).hexdigest();assert digest==expected,path
            verified[path]=digest
            top=path.split('/')[0] if '/' in path else 'ROOT_METADATA'
            totals[top][0]+=1;totals[top][1]+=n
    finally:
        proc.stdin.close();proc.wait()
    with (REPO/'0_admin/audit/r7c3g1/PATH_MIGRATION_AND_PRESERVATION.tsv').open(encoding='utf-8-sig',newline='') as f:
        preserved=list(csv.DictReader(f,delimiter='\t'))
    for row in preserved:assert verified[row['new_path']]==row['sha256'],row['old_path']
    remote_refs=dict(line.split()[::-1] for line in call(['git','ls-remote',REMOTE]).splitlines())
    old_refs=[]
    for line in (BACKUP/'refs_before.txt').read_text(encoding='utf-8-sig').splitlines():
        oid,ref=line.split()
        if ref.startswith('refs/tags/') or ref=='refs/heads/archive/pre-rebuild-20261012':
            assert remote_refs.get(ref)==oid, ref
            old_refs.append({'ref':ref,'oid':oid,'status':'UNCHANGED'})
    metadata=json.loads(call(['gh','repo','view','1209433622cz-maker/igan-open-regulatory-evidence','--json','isPrivate,nameWithOwner,url']))
    assert metadata['isPrivate'] is False
    receipt={'stage':'R7C3G1_REMOTE_FULL_TREE_VERIFICATION','checked_at':datetime.datetime.now().astimezone().isoformat(),'repository':metadata['url'],'public':True,'remote_main':remote_head,'manifest_entries_verified':len(rows),'tracked_files':len(names),'exact_manifest_coverage':True,'canonical_blob_sha256':'PASS_ALL','required_eight_roots':sorted(directories),'whole_tree_bytes_excluding_manifest':sum(v[1] for v in totals.values()),'directory_summary':dict(totals),'old_files_preserved':len(preserved),'old_refs_unchanged':old_refs,'method':'Fresh independent GitHub fetch to separate bare repository, all remote canonical Git blob SHA-256; not local origin cache','journal_submission_completed':False,'DOI_generated':False}
    save(AN/'REMOTE_CONTENT_VERIFICATION.json',receipt)
    print(json.dumps({'remote_main':remote_head,'blob_sha256':f'{len(rows)}/{len(rows)} PASS','old_files_preserved':len(preserved),'old_refs_unchanged':len(old_refs),'eight_roots':'PASS','public':True}),flush=True)

if __name__=='__main__':main()
