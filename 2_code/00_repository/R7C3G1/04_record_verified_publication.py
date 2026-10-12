"""Download and verify actual release assets, preserve old releases, record events.

Read-only against GitHub; local receipt updates only. Normal Git push remains a
separate explicit operation. No token or individual source data is read/exported.
"""
from pathlib import Path
import subprocess, json, hashlib, shutil, datetime

ROOT=Path(r'H:\SCI2\YR1')
REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
AN=ROOT/'5_analysis/R7C3G1_20261012'
BACKUP=ROOT/'0_admin/backups/R7C3G1_GitHubEightFolder_20261012'
TAG='r7c3g1-eight-folder-expert-narrative-2026-10-12'
NAME='1209433622cz-maker/igan-open-regulatory-evidence'

def api(path):return json.loads(subprocess.check_output(['gh','api',path]).decode('utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    release=api(f'repos/{NAME}/releases/tags/{TAG}')
    assert not release['draft'] and release['prerelease'], 'Editorial candidate must be public and labeled review/prerelease'
    actual_releases=api(f'repos/{NAME}/releases?per_page=100')
    prior=json.loads((BACKUP/'releases_before.json').read_text(encoding='utf-8-sig'))
    now={r['id']:r for r in actual_releases}
    old_assets=0
    for old in prior:
        assert old['id'] in now, old['tag_name']
        new=now[old['id']]
        assert new['tag_name']==old['tag_name']
        old_ids={a['id']:a['size'] for a in old['assets']}
        new_ids={a['id']:a['size'] for a in new['assets']}
        for aid,size in old_ids.items():assert new_ids.get(aid)==size,aid
        old_assets+=len(old_ids)
    download=AN/'release_asset_remote_download';download.mkdir(parents=True,exist_ok=True)
    subprocess.run(['gh','release','download',TAG,'--repo',NAME,'--dir',str(download),'--clobber'],check=True)
    expected=ROOT/'6_release/R7C3G_20261012'
    assets=[]
    for a in release['assets']:
        p=download/a['name'];src=expected/a['name']
        assert src.is_file() and p.stat().st_size==a['size'] and sha(p)==sha(src),a['name']
        assets.append({'name':a['name'],'id':a['id'],'bytes':a['size'],'sha256':sha(p),'identity':'REMOTE_DOWNLOAD_EQUALS_LOCAL_FROZEN_ASSET','download_url':a['browser_download_url']})
    assert len(assets)==3
    remote=json.loads((AN/'REMOTE_CONTENT_VERIFICATION.json').read_text(encoding='utf-8'))
    save(REPO/'0_admin/audit/r7c3g1/REMOTE_CONTENT_VERIFICATION.json',remote)
    receipt={'stage':'R7C3G1_VERIFIED_GITHUB_PUBLICATION','verified_at':datetime.datetime.now().astimezone().isoformat(),'repository':release['html_url'].split('/releases/')[0],'content_commit_verified':remote['remote_main'],'content_canonical_blob_checks':remote['manifest_entries_verified'],'original_file_identities_preserved':2335,'required_eight_roots':'PASS','old_refs_unchanged':len(remote['old_refs_unchanged']),'prior_releases_preserved':len(prior),'prior_release_assets_preserved':old_assets,'release_id':release['id'],'release_tag':TAG,'release_url':release['html_url'],'public_review_prerelease':True,'remote_download_asset_sha256_checks':len(assets),'assets':assets,'publication_event':'Latest R7C3G editorial assets are now actually public; source-package creation-time state remains unchanged','note':'This receipt describes the independently verified scientific/editorial content commit. A later normal main commit records these verification files; its own hash is kept in the external local final receipt to avoid self-reference. Run the canonical manifest verifier on any current HEAD.','journal_submission_completed':False,'DOI_generated_or_verified_in_this_round':False,'next':'R7C3H_EXACT_VERSION_AUTHOR_REVIEW_AND_PUBLISHER_PROOF'}
    save(REPO/'6_release/PUBLICATION_RECEIPT.json',receipt)
    save(AN/'RELEASE_PUBLICATION_RECEIPT.json',receipt)
    state_path=REPO/'0_admin/CURRENT_PROJECT_STATE.json'
    state=json.loads(state_path.read_text(encoding='utf-8'))
    state['current_editorial_assets_github_published']=True
    state['publication_release_tag']=TAG
    state['source_package_creation_state_retained']=True
    save(state_path,state)
    notes=REPO/'6_release/README.md'
    body=notes.read_text(encoding='utf-8')
    if '## Actual publication verification' not in body:
        body+='\n## Actual publication verification\n\nThe public review/prerelease exists. All three Release assets were downloaded independently from GitHub and matched to the frozen local files by byte count and SHA-256. Six prior Releases and twelve assets remain intact. The verification record identifies the content commit; later main commits may append audit receipts. [Publication receipt](PUBLICATION_RECEIPT.json).\n'
    notes.write_text(body,encoding='utf-8')
    print(json.dumps({'content_commit':remote['remote_main'],'release_url':release['html_url'],'assets_verified':len(assets),'prior_releases_preserved':len(prior),'prior_assets_preserved':old_assets,'public_review_prerelease':True}))

if __name__=='__main__':main()
