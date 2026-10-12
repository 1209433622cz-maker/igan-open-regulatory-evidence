"""Resume publishing an already-created verified new repo; NEVER deletes."""
from pathlib import Path
import importlib.util,json,subprocess,sys
ROOT=Path(r'H:\SCI2\YR1');CODE=ROOT/'2_code/00_workspace_management/R7C3F_20261012'
s=importlib.util.spec_from_file_location('rebuild',CODE/'07_authorized_github_rebuild.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
    checkpoint=json.loads((m.AN/'REBUILD_OPERATION_CHECKPOINT.json').read_text(encoding='utf-8'))
    assert checkpoint['repository_deleted'] and checkpoint['repository_created']
    current=m.api('repos/'+m.REPO);assert current['id']==checkpoint['new_repository_id']!=checkpoint['old_repository_id'] and not current['private']
    head=m.git('rev-parse','HEAD').strip();assert head==checkpoint['prepared_commit']
    subprocess.run([sys.executable,str(m.PUB/'analysis/r7c3f/verify_public_manifest.py')],check=True)
    subprocess.run(['git','-C',str(m.PUB),'-c','http.proxy=http://127.0.0.1:7890','push','--progress','-u','origin','--all'],check=True)
    subprocess.run(['git','-C',str(m.PUB),'-c','http.proxy=http://127.0.0.1:7890','push','origin','--tags'],check=True)
    remote=m.api('repos/'+m.REPO+'/git/ref/heads/main')['object']['sha'];assert remote==head
    backup=json.loads((m.BACK/'BACKUP_RECEIPT.json').read_text(encoding='utf-8'))
    for tag in json.loads((m.BACK/'tags.json').read_text(encoding='utf-8')):
        assert m.api('repos/'+m.REPO+'/git/ref/tags/'+tag['name'])['object']['sha']==m.git('rev-parse','refs/tags/'+tag['name']).strip()
    existing={r['tag_name'] for r in m.api('repos/'+m.REPO+'/releases?per_page=100')}
    for r in reversed(json.loads((m.BACK/'releases.json').read_text(encoding='utf-8'))):
        if r['tag_name'] in existing:continue
        notes=m.AN/('restore_'+r['tag_name']+'.md');notes.write_text(r['body'] or '',encoding='utf-8')
        args=['gh','release','create',r['tag_name'],'--repo',m.REPO,'--verify-tag','--title',r['name'],'--notes-file',str(notes)]
        if r.get('prerelease'):args.append('--prerelease')
        if r.get('draft'):args.append('--draft')
        args += [str(m.BACK/'release_assets'/r['tag_name']/a['name']) for a in r['assets']]
        m.call(args);print('RESTORED_RELEASE',r['tag_name'],flush=True)
    z=m.REL/'CMM_R7C3F_npj_Submission_Candidate_20261012.zip'
    if m.TAG not in existing:
        notes=m.AN/'NEW_RELEASE_NOTES.md';notes.write_text('R7C3F: complete fresh-byte audit (36,209 files;42.83GiB), detailed PBC README, curated work records/code and byte-preserved npj Genomic Medicine candidate. 21 original content assets and 48 scientific source members unchanged. Old repository was explicitly deleted; same-URL new public repository retains archive history/eight tags/five historical Releases. Original code MIT; original content/aggregates CC BY4 under NOTICE. Individual-level/bulk/vendor/copyrighted inputs excluded. Not a journal submission, mechanistic proof or minted project DOI.\n',encoding='utf-8')
        m.call(['gh','release','create',m.TAG,'--repo',m.REPO,'--verify-tag','--title','R7C3F PBC full audit and rebuilt submission compendium','--notes-file',str(notes),str(z),str(z)+'.sha256'])
    releases=m.api('repos/'+m.REPO+'/releases?per_page=100');assert len(releases)==6
    expected={(x['release_tag'],x['name']):x['bytes'] for x in backup['release_assets']};restored=[]
    for r in releases:
        for a in r['assets']:
            key=(r['tag_name'],a['name'])
            if key in expected:assert a['size']==expected[key];restored.append(key)
    assert len(restored)==10
    receipt={'stage':'R7C3F','date':'2026-10-12','repository':m.REPO,'url':current['html_url'],'old_repository_id':checkpoint['old_repository_id'],'new_repository_id':current['id'],'old_repository_deleted':True,'delete_http_status':204,'new_public_repository_created':True,'default_branch':'main','old_head':checkpoint['old_head'],'verified_payload_commit':head,'remote_payload_head':remote,'archive_branch':'archive/pre-rebuild-20261012','historical_tags_restored':8,'new_tag':m.TAG,'releases':6,'old_release_assets_restored':10,'new_submission_zip_bytes':z.stat().st_size,'new_submission_zip_sha256':m.sha(z),'old_backup_bundle_sha256':backup['bundle_sha256'],'manifest_entries_at_payload':checkpoint['manifest_entries'],'release_identity_note':'Tag/commit identities, release descriptions and asset bytes preserved; repository/release IDs and creation timestamps changed.','recovery':'Initial Git push did not finish; only its verified process tree was stopped. This resume uses repo-local GitHub CLI credentials and HTTP/1.1. It validates the new ID and never deletes/recreates again.','zenodo_doi_minted':False,'journal_submitted':False}
    m.save(m.AN/'GITHUB_REBUILD_RECEIPT.json',receipt);print(json.dumps(receipt,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
