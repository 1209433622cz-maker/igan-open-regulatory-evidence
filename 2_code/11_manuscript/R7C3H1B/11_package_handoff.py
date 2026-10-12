"""Create an immutable local handoff ZIP after actual public push and Actions QA."""
from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path(r'H:\SCI2\YR1')
OUT=ROOT/'5_manuscript/R7C3H1B_ExactVersionHandoff_20261013'
REL=ROOT/'6_release/R7C3H1B_20261013';REL.mkdir(parents=True,exist_ok=True)
REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD']).decode().strip()
remote=json.loads(subprocess.check_output(['gh','api','repos/1209433622cz-maker/igan-open-regulatory-evidence/git/ref/heads/main']).decode())['object']['sha']
assert head==remote
runs=json.loads(subprocess.check_output(['gh','run','list','-R','1209433622cz-maker/igan-open-regulatory-evidence','--limit','10','--json','databaseId,headSha,status,conclusion,url']).decode())
run=next(r for r in runs if r['headSha']==head);assert run['status']=='completed' and run['conclusion']=='success'
publication=dict(status='PUSH_AND_ACTIONS_VERIFIED_RELEASE_PENDING',commit=head,remote_head=remote,actions=run,
    scientific_source_tag='r7c3h0-statistical-reproducibility-closure-2026-10-13',candidate_release_tag='r7c3h1b-exact-version-handoff-2026-10-13',
    local_public_candidate_checks='95/95 PASS',aggregate_scientific_replay='38/38 PASS',canonical_git_blob_manifest='2746/2746 PASS',
    scope='Public candidate and research plan synchronization; no journal submission or DOI creation')
(OUT/'06_QA/GITHUB_PUSH_AND_ACTIONS_RECEIPT.json').write_text(json.dumps(publication,indent=2),encoding='utf-8')
statepath=OUT/'08_Protocol/HANDOFF_STATE.json';state=json.loads(statepath.read_text(encoding='utf-8'))
state['github_candidate_publication']='PUSH_AND_ACTIONS_VERIFIED_RELEASE_PENDING';state['public_candidate_commit']=head
statepath.write_text(json.dumps(state,indent=2,ensure_ascii=False),encoding='utf-8')
rp=ROOT/'7.Report/rounds/R7C3H1B_20261013/99_R7C3H1B_详细行动记录_20261013.md'
addition=f'''\n## 12 实际 GitHub 推送与远端 QA 收据\n\n已实际push并复核remote main=`{head}`。Actions run {run['databaseId']} completed/success：[远端检查]({run['url']})。本机canonical manifest2746/2746通过，公开候选byte/aggregate检查95/95通过，聚合科学结果38/38通过，Actions重新执行科学聚合与候选检查并通过。分次内容核对不能冒充原始642模型再拟合。公开stage检查97条路径、0 secret pattern、0 >10MiB文件、0个体数据扩展名；目录八根保持，原scientific tag不变。\n\n本ZIP生成时push/Actions已经完成，独立GitHub Release资产上传尚待执行；发布后的文件大小、GitHub digest和release URL写入单独publication receipt，避免把包自身SHA写入包中造成循环。\n'''
assert '## 12 实际 GitHub' not in rp.read_text(encoding='utf-8')
rp.write_text(rp.read_text(encoding='utf-8')+addition,encoding='utf-8');shutil.copy2(rp,OUT/'07_Reports'/rp.name)
for p in (ROOT/'2_code/11_manuscript/R7C3H1B_20261013').iterdir():
    if p.is_file():shutil.copy2(p,OUT/'09_Code'/p.name)
files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='checksums.sha256')
assert not any(p.stat().st_size>10*1024*1024 for p in files)
manifest='\n'.join(sha(p)+'  '+p.relative_to(OUT).as_posix() for p in files)+'\n'
(OUT/'checksums.sha256').write_text(manifest,encoding='utf-8',newline='\n')
package=REL/'CMM_R7C3H1B_ExactVersionHandoff_SubmissionCandidate_20261013.zip'
assert not package.exists(), 'Never overwrite a published ZIP'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(package) as z:
    assert z.testzip() is None
    for line in z.read('checksums.sha256').decode().splitlines():
        h,path=line.split('  ',1);assert hashlib.sha256(z.read(path)).hexdigest()==h,path
digest=sha(package);(REL/(package.name+'.sha256')).write_text(digest+'  '+package.name+'\n',encoding='utf-8')
receipt=dict(package=str(package),bytes=package.stat().st_size,sha256=digest,CRC='PASS',internal_checksum_count=len(files),internal_checksums='PASS',entries=len(files)+1,
    public_commit=head,actions_run=run['databaseId'],release_upload='PENDING',fresh_author_approval='PENDING',publisher_proof='PENDING')
(REL/'LOCAL_RELEASE_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt))
