"""User-authorized exact-repository rebuild; requires explicit execute flag.

Hard guards: old repository ID, verified full backup, immutable candidate,
clean canonical public manifest, delete_repo scope. Never delete a new/rebuilt
repository and never touch any other owner's repository.
"""
from pathlib import Path
import subprocess, json, hashlib, os, re, sys, time
ROOT=Path(r'H:\SCI2\YR1');REPO='1209433622cz-maker/igan-open-regulatory-evidence'
PUB=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
AN=ROOT/'5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012'
BACK=ROOT/'9.Version/github_rebuild/R7C3F_20261012'
TAG='r7c3f-full-audit-rebuilt-submission-2026-10-12'
REL=ROOT/'6_release/R7C3F_20261012'
def call(args):
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if p.returncode:raise RuntimeError(' '.join(args[:3])+': '+p.stderr[:600])
    return p.stdout
def api(endpoint):return json.loads(call(['gh','api',endpoint]))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
    return h.hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return call(['git','-C',str(PUB),*args])
def manifest():
    paths=[p for p in sorted(PUB.rglob('*')) if p.is_file() and '.git' not in p.parts and p!=PUB/'MANIFEST.sha256']
    (PUB/'MANIFEST.sha256').write_text(''.join(f'{sha(p)}  {p.relative_to(PUB).as_posix()}\n' for p in paths),encoding='utf-8')
    return len(paths)
def main():
    assert '--execute-authorized-rebuild' in sys.argv,'Preparation only: execution requires the explicit flag after human authorization.'
    assert REPO=='1209433622cz-maker/igan-open-regulatory-evidence'
    backup=json.loads((BACK/'BACKUP_RECEIPT.json').read_text(encoding='utf-8'));qa=json.loads((AN/'QA_STATE.json').read_text(encoding='utf-8'))
    assert backup['backup_complete'] and backup['git_fsck']=='PASS' and backup['bundle_verify']=='PASS' and backup['release_checksum_pairs_pass']==5
    assert sha(BACK/'OLD_REMOTE_ALL_REFS.bundle')==backup['bundle_sha256'];assert qa['pass']
    assert json.loads((AN/'FULL_FORMAT_STATE.json').read_text(encoding='utf-8'))['review_findings']==0
    for x in backup['release_assets']:assert sha(Path(x['local_path']))==x['sha256']
    assert not (PUB/'.git').exists(),'Do not replay repository deletion after a prior initialized attempt.'
    old=api('repos/'+REPO);assert old['id']==1369613027==backup['old_repository_id'];assert old['permissions']['admin']
    headers=call(['gh','api','-i','user']);m=re.search(r'(?im)^X-Oauth-Scopes:\s*(.*)$',headers)
    assert m and 'delete_repo' in m.group(1),'Actual token still lacks delete_repo; no deletion attempted.'
    oldhead=api('repos/'+REPO+'/git/ref/heads/main')['object']['sha'];assert oldhead==backup['old_head']
    (PUB/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eol,-blank-at-eof\n',encoding='utf-8')
    # Never add ignored raw inputs; force only the already-reviewed exact public tree.
    git('init','-b','main');git('config','user.name','Zhi Chen');git('config','user.email','zhichen1@link.cuhk.edu.cn')
    git('fetch',str(BACK/'OLD_REMOTE_ALL_REFS.bundle'),'refs/heads/main:refs/heads/archive/pre-rebuild-20261012','refs/tags/*:refs/tags/*')
    manifest_count=manifest();git('add','--force','--all');git('diff','--cached','--check')
    git('commit','-m','Rebuild PBC open research: full audit, work records and submission candidate R7C3F')
    newhead=git('rev-parse','HEAD').strip();git('tag','-a',TAG,'-m','R7C3F full audit and byte-preserved submission candidate')
    # Validate canonical blobs before destructive action.
    call([sys.executable,str(PUB/'analysis/r7c3f/verify_public_manifest.py')])
    pre={'prepared_commit':newhead,'manifest_entries':manifest_count,'old_repository_id':old['id'],'old_head':oldhead,'backup_verified':True,'candidate_verified':True,'user_authorized_delete_recreate_public':True,'scope_verified_delete_repo':True,'repository_deleted':False,'repository_created':False}
    save(AN/'REBUILD_PREDELETION_GUARDS.json',pre);print('PREDELETION_GUARDS_PASS',newhead,flush=True)
    response=call(['gh','api','-i','-X','DELETE','repos/'+REPO]);assert re.search(r'HTTP/\S+ 204',response),response[:200]
    pre['repository_deleted']=True;save(AN/'REBUILD_OPERATION_CHECKPOINT.json',pre);print('OLD_REPOSITORY_DELETED_HTTP_204',flush=True)
    create={'name':REPO.split('/')[1],'description':'PBC regulatory attribution reliability: input-matched multi-signal colocalization, simulation calibration and bounded external evidence.','private':False,'has_issues':True,'has_wiki':False,'has_projects':False,'auto_init':False}
    cp=AN/'CREATE_REPOSITORY_REQUEST.json';save(cp,create)
    new=json.loads(call(['gh','api','-X','POST','user/repos','--input',str(cp)]));assert new['full_name']==REPO and not new['private'] and new['id']!=old['id']
    pre.update(repository_created=True,new_repository_id=new['id']);save(AN/'REBUILD_OPERATION_CHECKPOINT.json',pre);print('NEW_PUBLIC_REPOSITORY_CREATED',new['id'],flush=True)
    git('remote','add','origin','https://github.com/'+REPO+'.git')
    git('-c','http.proxy=http://127.0.0.1:7890','push','-u','origin','--all')
    git('-c','http.proxy=http://127.0.0.1:7890','push','origin','--tags')
    remote=api('repos/'+REPO+'/git/ref/heads/main')['object']['sha'];assert remote==newhead
    for tag in json.loads((BACK/'tags.json').read_text(encoding='utf-8')):
        r=api('repos/'+REPO+'/git/ref/tags/'+tag['name']);local=git('rev-parse','refs/tags/'+tag['name']).strip();assert r['object']['sha']==local
    releases=json.loads((BACK/'releases.json').read_text(encoding='utf-8'))
    for r in reversed(releases):
        notes=AN/('restore_'+r['tag_name']+'.md');notes.write_text(r['body'] or '',encoding='utf-8')
        args=['gh','release','create',r['tag_name'],'--repo',REPO,'--verify-tag','--title',r['name'],'--notes-file',str(notes)]
        if r.get('prerelease'):args.append('--prerelease')
        if r.get('draft'):args.append('--draft')
        args += [str(BACK/'release_assets'/r['tag_name']/a['name']) for a in r['assets']]
        call(args);print('RESTORED_RELEASE',r['tag_name'],flush=True)
    notes=AN/'NEW_RELEASE_NOTES.md';notes.write_text('''R7C3F: complete fresh-byte local audit, curated work records/code, detailed PBC README and a byte-preserved npj Genomic Medicine submission candidate. 36,209 files / 42.83 GiB rehashed; 21 original candidate content files and 48 scientific source members unchanged. Original history, eight scientific/editorial tags and five release assets sets restored after the explicitly authorized repository rebuild. Raw/individual-level files, vendor runtimes and copyrighted papers excluded; large inputs recorded by identity. This is not journal submission, causal mediation, participant-independent replication or a minted Zenodo DOI. See README and the action report for gates and boundaries.\n''',encoding='utf-8')
    z=REL/'CMM_R7C3F_npj_Submission_Candidate_20261012.zip'
    call(['gh','release','create',TAG,'--repo',REPO,'--verify-tag','--title','R7C3F PBC full audit and rebuilt submission compendium','--notes-file',str(notes),str(z),str(z)+'.sha256'])
    live=api('repos/'+REPO);current_releases=api('repos/'+REPO+'/releases?per_page=100');assert len(current_releases)==6
    expected_assets={(x['release_tag'],x['name']):x['bytes'] for x in backup['release_assets']};restored=[]
    for r in current_releases:
        for a in r['assets']:
            key=(r['tag_name'],a['name'])
            if key in expected_assets:assert a['size']==expected_assets[key];restored.append(key)
    assert len(restored)==10
    receipt={'stage':'R7C3F','date':'2026-10-12','repository':REPO,'url':live['html_url'],'old_repository_id':old['id'],'new_repository_id':live['id'],'old_repository_deleted':True,'delete_http_status':204,'new_public_repository_created':not live['private'],'default_branch':live['default_branch'],'old_head':oldhead,'verified_payload_commit':newhead,'remote_payload_head':remote,'archive_branch':'archive/pre-rebuild-20261012','historical_tags_restored':8,'new_tag':TAG,'releases':len(current_releases),'old_release_assets_restored':len(restored),'new_submission_zip_bytes':z.stat().st_size,'new_submission_zip_sha256':sha(z),'old_backup_bundle_sha256':backup['bundle_sha256'],'manifest_entries_at_payload':manifest_count,'release_identity_note':'Descriptions, tag/commit identities and uploaded asset bytes retained; new repository/release IDs and created timestamps differ. Prior subscriptions/settings outside exported metadata are not claimed preserved.','zenodo_doi_minted':False,'journal_submitted':False}
    save(AN/'GITHUB_REBUILD_RECEIPT.json',receipt);print(json.dumps(receipt,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
