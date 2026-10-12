"""Commit verified receipts and final QA; verify remote Git tree byte identity."""
from pathlib import Path
import json, subprocess, hashlib, importlib.util, shutil
ROOT=Path(r'H:\SCI2\YR1');CODE=ROOT/'2_code/00_workspace_management/R7C3F_20261012'
s=importlib.util.spec_from_file_location('rebuild',CODE/'07_authorized_github_rebuild.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
    receipt=json.loads((m.AN/'GITHUB_REBUILD_RECEIPT.json').read_text(encoding='utf-8'))
    assert len(receipt['release_asset_remote_sha256_verified'])==12
    # Avoid a self-referential final-HEAD value in the commit that creates it.
    p=m.PUB/'protocols/R7C3F_CURRENT_STATE.json';state=json.loads(p.read_text(encoding='utf-8'));state.pop('GITHUB_FINAL_HEAD',None);state['GITHUB_LATEST_HEAD_LOCATION']='GitHub refs/heads/main; immutable scientific payload identified separately';m.save(p,state)
    for p in CODE.glob('*.py'):shutil.copy2(p,m.PUB/'analysis/r7c3f'/p.name)
    shutil.copy2(m.AN/'QA_STATE.json',m.PUB/'audit/r7c3f/QA_STATE.json')
    count=m.manifest();m.git('add','--force','--all');m.git('diff','--cached','--check')
    m.git('commit','-m','Record verified rebuild, restored releases, full audit and next submission gates')
    head=m.git('rev-parse','HEAD').strip()
    subprocess.run(['git','-C',str(m.PUB),'-c','http.proxy=http://127.0.0.1:7890','push','origin','main'],check=True)
    remote=m.api('repos/'+m.REPO+'/git/ref/heads/main')['object']['sha'];assert remote==head
    subprocess.run(['git','-C',str(m.PUB),'-c','http.proxy=http://127.0.0.1:7890','fetch','origin','main'],check=True)
    tree=m.git('rev-parse','HEAD^{tree}').strip();remote_tree=m.git('rev-parse','origin/main^{tree}').strip();assert tree==remote_tree
    result=subprocess.check_output([__import__('sys').executable,str(m.PUB/'analysis/r7c3f/verify_public_manifest.py')],text=True,encoding='utf-8').strip()
    assert result==f'PASS {count}/{count} canonical Git-blob checksums'
    assert not m.git('status','--porcelain').strip()
    assert m.api('repos/'+m.REPO+'/git/ref/tags/r7c2-q1-journal-audit-dual-track-2026-10-11')['object']['sha']==m.git('rev-parse','refs/tags/r7c2-q1-journal-audit-dual-track-2026-10-11').strip()
    close={'stage':'R7C3F','new_repository_id':receipt['new_repository_id'],'url':receipt['url'],'payload_commit':receipt['verified_payload_commit'],'final_head':head,'remote_head':remote,'local_tree':tree,'remote_fetched_tree':remote_tree,'canonical_manifest_entries':count,'git_blob_verification':result,'working_tree':'CLEAN','manuscript_science_tag_link':'PASS_EXISTING_R7C2_TAG_RESTORED','release_assets_remote_sha256':12,'journal_submitted':False,'new_project_doi':False}
    m.save(m.AN/'FINAL_GITHUB_CLOSEOUT.json',close)
    local=ROOT/'0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json';st=json.loads(local.read_text(encoding='utf-8'));st['GITHUB_FINAL_HEAD']=head;m.save(local,st)
    # This local closeout is not inserted into its own commit; public receipt records
    # the verified scientific payload, and public HEAD is independently available.
    print(json.dumps(close,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
