"""Capture all remote refs and release assets before an authorized rebuild."""
from pathlib import Path
import subprocess, json, hashlib, os, zipfile
ROOT=Path(r'H:\SCI2\YR1'); REPO='1209433622cz-maker/igan-open-regulatory-evidence'
OUT=ROOT/'9.Version/github_rebuild/R7C3F_20261012'
def call(args):
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if p.returncode:raise RuntimeError(f'{args[0]} {args[1]} failed: '+p.stderr[:500])
    return p.stdout
def api(endpoint):return json.loads(call(['gh','api',endpoint]))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    data={k:api('repos/'+REPO+suffix) for k,suffix in {'repository':'','releases':'/releases?per_page=100','branches':'/branches?per_page=100','tags':'/tags?per_page=100','issues':'/issues?state=all&per_page=100','pulls':'/pulls?state=all&per_page=100','hooks':'/hooks?per_page=100','rulesets':'/rulesets?per_page=100'}.items()}
    for k,v in data.items():(OUT/(k+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    mirror=OUT/'remote_mirror.git'
    if not mirror.exists():call(['git','-c','http.proxy=http://127.0.0.1:7890','clone','--mirror','https://github.com/'+REPO+'.git',str(mirror)])
    head=call(['git','--git-dir',str(mirror),'rev-parse','refs/heads/main']).strip()
    assert head==data['branches'][0]['commit']['sha']
    fsck=call(['git','--git-dir',str(mirror),'fsck','--full']);(OUT/'git_fsck.txt').write_text(fsck,encoding='utf-8')
    bundle=OUT/'OLD_REMOTE_ALL_REFS.bundle'
    if not bundle.exists():call(['git','--git-dir',str(mirror),'bundle','create',str(bundle),'--all'])
    verify=call(['git','--git-dir',str(mirror),'bundle','verify',str(bundle)]);(OUT/'bundle_verify.txt').write_text(verify,encoding='utf-8')
    release_receipts=[]
    for release in data['releases']:
        folder=OUT/'release_assets'/release['tag_name'];folder.mkdir(parents=True,exist_ok=True)
        for asset in release['assets']:
            p=folder/asset['name']
            if not p.exists():call(['gh','release','download',release['tag_name'],'--repo',REPO,'--pattern',asset['name'],'--dir',str(folder)])
            assert p.stat().st_size==asset['size']
            if p.suffix=='.zip':
                with zipfile.ZipFile(p) as z:assert z.testzip() is None
            release_receipts.append({'release_tag':release['tag_name'],'name':asset['name'],'bytes':p.stat().st_size,'sha256':sha(p),'local_path':str(p),'crc':'PASS' if p.suffix=='.zip' else 'NOT_APPLICABLE'})
        print('BACKED_UP_RELEASE',release['tag_name'],flush=True)
    checks=[]
    for x in release_receipts:
        if x['name'].endswith('.sha256'):
            lines=Path(x['local_path']).read_text(encoding='utf-8-sig').splitlines()
            for line in lines:
                if line.strip():
                    h,name=line.strip().split(maxsplit=1);name=name.lstrip('*')
                    matches=[a for a in release_receipts if a['release_tag']==x['release_tag'] and a['name']==name]
                    assert len(matches)==1 and matches[0]['sha256']==h.lower();checks.append(name)
    state={'stage':'R7C3F','backup_complete':True,'old_repository':REPO,'old_repository_id':data['repository']['id'],'old_head':head,'branches':len(data['branches']),'tags':len(data['tags']),'releases':len(data['releases']),'issues':len(data['issues']),'pulls':len(data['pulls']),'hooks':len(data['hooks']),'rulesets':len(data['rulesets']),'bundle_sha256':sha(bundle),'bundle_bytes':bundle.stat().st_size,'git_fsck':'PASS','bundle_verify':'PASS','release_assets':release_receipts,'release_checksum_pairs_pass':len(checks),'caveat':'Repository identity, permissions, creation timestamps and release IDs cannot be preserved by recreating. Refs, blobs, release descriptions and asset bytes are captured. No repository deletion has occurred in this script.'}
    (OUT/'BACKUP_RECEIPT.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in state.items() if k!='release_assets'},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
