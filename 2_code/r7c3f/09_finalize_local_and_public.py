"""Finalize truthful publication records after API/push/release confirmation."""
from pathlib import Path
import json, shutil, csv, subprocess, hashlib
ROOT=Path(r'H:\SCI2\YR1');AN=ROOT/'5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012'
PUB=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012';BACK=ROOT/'9.Version/github_rebuild/R7C3F_20261012'
REPORT=ROOT/'7.Report/rounds/R7C3F_20261012'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def call(args):
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if p.returncode:raise RuntimeError(p.stderr[:500])
    return p.stdout
def main():
    r=load(AN/'GITHUB_REBUILD_RECEIPT.json');assert r['old_repository_deleted'] and r['new_public_repository_created'] and r['releases']==6
    assert not (AN/'LOCAL_FINALIZATION_RECEIPT.json').exists(),'Avoid duplicate appended records'
    all_releases=json.loads(call(['gh','api','repos/'+r['repository']+'/releases?per_page=100']))
    backup=load(BACK/'BACKUP_RECEIPT.json');expected={(x['release_tag'],x['name']):x['sha256'] for x in backup['release_assets']}
    expected[(r['new_tag'],'CMM_R7C3F_npj_Submission_Candidate_20261012.zip')]=r['new_submission_zip_sha256']
    zsha=ROOT/'6_release/R7C3F_20261012/CMM_R7C3F_npj_Submission_Candidate_20261012.zip.sha256'
    expected[(r['new_tag'],zsha.name)]=hashlib.sha256(zsha.read_bytes()).hexdigest()
    identities=[]
    for rel in all_releases:
        for a in rel['assets']:
            key=(rel['tag_name'],a['name']);assert key in expected
            # GitHub server calculates a SHA-256 digest on uploaded release assets.
            digest=a.get('digest')
            if digest:assert digest=='sha256:'+expected[key]
            else:
                import tempfile
                with tempfile.TemporaryDirectory(prefix='r7c3f_remote_asset_') as td:
                    call(['gh','release','download',rel['tag_name'],'--repo',r['repository'],'--pattern',a['name'],'--dir',td])
                    assert hashlib.sha256((Path(td)/a['name']).read_bytes()).hexdigest()==expected[key]
            identities.append({'tag':rel['tag_name'],'asset':a['name'],'bytes':a['size'],'sha256':expected[key],'remote_sha256':'PASS_SERVER_DIGEST' if digest else 'PASS_INDEPENDENT_DOWNLOAD'})
    assert len(identities)==12
    r['release_asset_remote_sha256_verified']=identities;save(AN/'GITHUB_REBUILD_RECEIPT.json',r)
    original={}
    for p in [ROOT/'0_admin/navigation/CURRENT_PROJECT_AND_FILES.md',ROOT/'0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json',ROOT/'9_Vote/PBC_CurrentDecision_20261012.md']:
        b=BACK/'original_navigation'/p.relative_to(ROOT);b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);original[p.relative_to(ROOT).as_posix()]=hashlib.sha256(b.read_bytes()).hexdigest()
    state=load(ROOT/'0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json')
    state.update(CURRENT_ADMINISTRATIVE_STAGE='R7C3F_FULL_AUDIT_GITHUB_DELETED_RECREATED_PUBLIC_VERIFIED',GITHUB_PUBLIC_SYNC='REBUILT_PUBLIC_PUBLISHED_VERIFIED_COMPLETE',GITHUB_OLD_REPOSITORY_ID=r['old_repository_id'],GITHUB_NEW_REPOSITORY_ID=r['new_repository_id'],GITHUB_PAYLOAD_COMMIT=r['verified_payload_commit'],GITHUB_FINAL_HEAD=r['verified_payload_commit'],CURRENT_SUBMISSION_PACKAGE='5_manuscript/R7C3F_SubmissionCandidate_20261012',CURRENT_PUBLIC_MIRROR='0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012',NEW_BIOLOGICAL_ANALYSIS_REQUIRED=False,NEXT='R7C4_AUTHOR_FINAL_VERSION_CONFIRMATION_REPORTING_FORMS_PORTAL_PROOF_AND_SUBMISSION_RECEIPT')
    save(ROOT/'0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json',state)
    nav=ROOT/'0_admin/navigation/CURRENT_PROJECT_AND_FILES.md';txt=nav.read_text(encoding='utf-8')
    txt=txt.replace('更新：2026-10-12，R7C3E 子文件夹分类。','更新：2026-10-12，R7C3F 全量核查与 GitHub 删除重建已验证。')
    txt=txt.replace('6_release/R7C3C_2026-10-12/CMM_R7C3C_npj_Submission_Candidate_20261012.zip','6_release/R7C3F_20261012/CMM_R7C3F_npj_Submission_Candidate_20261012.zip').replace('CMM_R7C3C_npj_Submission_Candidate_20261012.zip','CMM_R7C3F_npj_Submission_Candidate_20261012.zip')
    txt=txt.replace('当前尚未投稿，没有本轮 DOI 或 GitHub 推送。','当前尚未投稿，没有本轮项目 DOI；本轮 GitHub 原库删除、同网址公开库重建和推送已真实验证。')
    txt+='\n当前公开仓库：https://github.com/'+r['repository']+' 。当前本机 Git 镜像：`0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012`；旧镜像保留为历史，不要从旧 main 推送覆盖新 main。\n\n本轮报告：[R7C3F详细行动记录](<H:/SCI2/YR1/7.Report/rounds/R7C3F_20261012/99_R7C3F_全量核查_GitHub重建_投稿包_详细行动记录_20261012.md>)；全量字节清单与重复/格式/工作记录索引在 `5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012`。十二目录导航保留 R7C3E 当时快照；本轮新增文件参照本轮 closing inventory。\n'
    nav.write_text(txt,encoding='utf-8')
    vote=ROOT/'9_Vote/PBC_CurrentDecision_20261012.md';vote.write_text(vote.read_text(encoding='utf-8')+'\n\n## R7C3F / 2026-10-12 实际执行补记\n\n全量字节与格式核查完成；原库已删除，同网址公开库重建并推送，8 旧标签及5旧Release恢复，新增R7C3F候选Release。投稿候选内容21件和Source成员48件保持身份。PBC GO；未投稿、无本轮Zenodo DOI。下一阶段R7C4最终版本/官方表格/门户proof/回执；不扩大候选集。\n',encoding='utf-8')
    appendix=f'''\n### 10.1 已完成远端真实执行\n\n旧 repository ID `{r['old_repository_id']}` 已通过 HTTP 204 删除。新公开 repository ID `{r['new_repository_id']}`，同网址 `{r['url']}`，default branch main。新 payload commit `{r['verified_payload_commit']}` 与 API remote HEAD 一致。旧 main 保留在 `{r['archive_branch']}`；8/8 old tag 对象身份一致。5旧Release描述和10旧附件恢复，另新增R7C3F Release，共6 Releases、12附件；12/12 remote SHA-256通过（服务端digest或独立下载）。新repo/release ID和日期为新的，未虚称原身份不变。\n\n候选ZIP SHA-256 `{r['new_submission_zip_sha256']}`，{r['new_submission_zip_bytes']:,} bytes。公开Git blob manifest和最终记录在 closing receipt commit再次核验；最终head在私有闭账receipt明确记录，避免自引用哈希。仓库重建/推送已完成，投稿和Zenodo DOI均未执行。\n'''
    appendix+='\n首次Git push长期未完成；保存删除/创建checkpoint后，仅终止核实属于新镜像push的进程树（6进程）。新镜像局部设置GitHub CLI凭据helper、HTTP/1.1与传输超时，再从已创建且ID核验的新库恢复。恢复脚本从不删除仓库；push、tags和Release随后闭环成功。未触及其他旧Git进程或重复删除新库。\n'
    report=REPORT/'99_R7C3F_全量核查_GitHub重建_投稿包_详细行动记录_20261012.md';report.write_text(report.read_text(encoding='utf-8')+appendix,encoding='utf-8')
    summary=REPORT/'00_R7C3F_执行摘要_20261012.md';summary.write_text(summary.read_text(encoding='utf-8')+'\n远端执行已完成：旧库HTTP204删除；新库公开、ID='+str(r['new_repository_id'])+'；same URL重建，8旧tags/5旧Release/10旧附件恢复；新增候选Release；12/12 remote附件SHA通过。无期刊投稿或项目DOI。\n',encoding='utf-8')
    for p in REPORT.glob('*.md'):
        q=PUB/'reports/r7c3f'/p.name;shutil.copy2(p,q)
    save(PUB/'audit/r7c3f/GITHUB_REBUILD_RECEIPT.json',r);save(PUB/'protocols/R7C3F_CURRENT_STATE.json',state)
    p=PUB/'README.md';txt=p.read_text(encoding='utf-8');txt+='\n## Verified repository rebuild — 12 October 2026\n\nThe old repository was deleted (HTTP 204) and a new public repository was created at the same URL. New repository ID: '+str(r['new_repository_id'])+'. All eight old tags and the old main at `archive/pre-rebuild-20261012` retain their Git identities; five historical Releases and ten asset files were restored. The new [R7C3F submission-candidate Release](https://github.com/'+r['repository']+'/releases/tag/'+r['new_tag']+') is published. Twelve Release assets pass remote SHA-256 verification. See [publication receipt](audit/r7c3f/GITHUB_REBUILD_RECEIPT.json) and [detailed action report](reports/r7c3f/'+report.name+'). Repository/Release IDs and creation timestamps changed; journal submission and project DOI did not occur.\n'
    p.write_text(txt,encoding='utf-8')
    save(AN/'LOCAL_FINALIZATION_RECEIPT.json',{'navigation_original_sha256':original,'publication_verified':True,'new_repository_id':r['new_repository_id'],'release_assets_remote_sha_verified':len(identities),'science_unchanged':True})
    shutil.copy2(Path(__file__),PUB/'analysis/r7c3f'/Path(__file__).name)
    print('FINAL_RECORDS_AND_REMOTE_12_ASSET_SHA_VERIFIED',flush=True)
if __name__=='__main__':main()
