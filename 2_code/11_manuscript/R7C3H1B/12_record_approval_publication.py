"""Record the actual human approval and verify uploaded GitHub asset identities.

Does not rewrite the approved ZIP or change any approved submission file.
"""
from pathlib import Path
import csv,datetime,hashlib,json,shutil,subprocess
ROOT=Path(r'H:\SCI2\YR1')
OUT=ROOT/'5_manuscript/R7C3H1B_ExactVersionHandoff_20261013'
REL=ROOT/'6_release/R7C3H1B_20261013'
REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
TAG='r7c3h1b-exact-version-handoff-2026-10-13'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
local=json.loads((REL/'LOCAL_RELEASE_RECEIPT.json').read_text())
package=Path(local['package']);assert sha(package)==local['sha256']=='a67c893924e9eb4cb9e2432d8e475a9497c5590c3b817841baddfef4aefd0e25'
release=json.loads(subprocess.check_output(['gh','api','repos/1209433622cz-maker/igan-open-regulatory-evidence/releases/tags/'+TAG]).decode())
assert not release['draft']
asset=next(a for a in release['assets'] if a['name']==package.name)
assert asset['size']==package.stat().st_size and asset['digest']=='sha256:'+sha(package) and asset['state']=='uploaded'
rpzip=ROOT/'6_release/RP_v5_20261013/CMM_PBC_RP_v5_EvidenceAndFigureSources_20261013.zip'
rpasset=next(a for a in release['assets'] if a['name']==rpzip.name)
assert rpasset['size']==rpzip.stat().st_size and rpasset['digest']=='sha256:'+sha(rpzip)
with (OUT/'06_QA/UPLOAD_CANDIDATE_MANIFEST.tsv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
for r in rows:assert sha(OUT/r['relative'])==r['sha256']
approval=dict(status='APPROVED_EXACT_FILES',date='2026-10-13',evidence='Direct human answer in this Codex conversation to the exact-version approval question',
    human_answer_verbatim='两位作者批准这套精确版本',approved_authors=['Zhi Chen','Teng Qi'],approved_use='Submission to npj Genomic Medicine',
    zip_name=package.name,zip_sha256=sha(package),upload_manifest_sha256=sha(OUT/'06_QA/UPLOAD_CANDIDATE_MANIFEST.tsv'),approved_upload_files=rows,
    unchanged_package_snapshot='The ZIP was frozen before this answer and retains its historical PENDING approval state. This separate receipt records subsequent approval without changing ZIP bytes.',
    limit='This human approval is not a journal submission receipt, signed publisher form or publisher-generated PDF proof.')
(REL/'AUTHOR_APPROVAL_RECEIPT.json').write_text(json.dumps(approval,ensure_ascii=False,indent=2),encoding='utf-8')
publication=dict(status='PUBLISHED_ASSETS_BYTE_VERIFIED',url=release['html_url'],tag=TAG,source_commit=local['public_commit'],actions_run=local['actions_run'],
    assets=[dict(name=a['name'],bytes=a['size'],sha256=a['digest'].removeprefix('sha256:'),url=a['browser_download_url']) for a in [asset,rpasset]],
    approval='APPROVED_EXACT_FILES',publisher_proof='NOT_EXECUTED',journal_submission='NOT_EXECUTED',Zenodo_DOI='NOT_ESTABLISHED')
(REL/'PUBLICATION_RECEIPT.json').write_text(json.dumps(publication,indent=2),encoding='utf-8')
handoff=REPO/'5_manuscript/current/R7C3H1B'
for name in ['AUTHOR_APPROVAL_RECEIPT.json','PUBLICATION_RECEIPT.json']:
    for dest in [REPO/'6_release/r7c3h1b',handoff/'08_Protocol']:
        dest.mkdir(parents=True,exist_ok=True);shutil.copy2(REL/name,dest/name)
statepath=handoff/'08_Protocol/HANDOFF_STATE.json';s=json.loads(statepath.read_text(encoding='utf-8'))
s.update(fresh_exact_version_author_approval='APPROVED_EXACT_FILES',github_candidate_publication='PUBLISHED_ASSETS_BYTE_VERIFIED',
    public_candidate_commit=local['public_commit'],status='COMPLETE_LOCAL_HANDOFF_AUTHOR_APPROVED_PORTAL_PROOF_PENDING',
    next='R7C3H1C_PUBLISHER_PORTAL_PROOF_AND_AUTHOR_OPERATED_SUBMISSION',approved_zip_sha256=sha(package),approval_receipt='AUTHOR_APPROVAL_RECEIPT.json')
statepath.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
rootstatepath=REPO/'0_admin/CURRENT_PROJECT_STATE.json';s=json.loads(rootstatepath.read_text(encoding='utf-8'))
s.update(current_editorial_assets_github_publish_pending=False,current_editorial_assets_github_published=True,
    current_public_release_tag=TAG,current_public_release_url=release['html_url'],current_release_zip_sha256=sha(package),current_release_zip_bytes=package.stat().st_size,
    current_candidate_release_status='PUBLISHED_ASSETS_BYTE_VERIFIED',current_candidate_actions_status='PASS',public_candidate_commit=local['public_commit'],
    new_candidate_exact_version_author_review='APPROVED_EXACT_FILES',NEXT='R7C3H1C_PUBLISHER_PORTAL_PROOF_AND_AUTHOR_OPERATED_SUBMISSION',next='R7C3H1C_PUBLISHER_PORTAL_PROOF_AND_AUTHOR_OPERATED_SUBMISSION',
    publisher_portal_proof='NOT_EXECUTED_BROWSER_CONTROL_TIMED_OUT',journal_submission_completed=False)
rootstatepath.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
meta=handoff/'08_Protocol/PORTAL_METADATA_PREPARED.json';s=json.loads(meta.read_text(encoding='utf-8'));s['fresh_exact_file_approval']='APPROVED_EXACT_FILES';meta.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
guide=f'''# R7C3H1C 已批准文件与门户校样下一步

两位作者已在本会话明确批准 R7C3H1B 13文件清单用于 npj Genomic Medicine 投稿。批准绑定 ZIP SHA-256 `{sha(package)}`，批准后未改变任一主稿、图件、SI、工作簿、Source Data或cover。详见 AUTHOR_APPROVAL_RECEIPT.json。原ZIP在批准前冻结，包内PENDING是历史快照状态；后续批准通过本收据追加，不重打包或改变已批准对象。

GitHub公开发布及资产identity已通过API核对：[R7C3H1B release]({release['html_url']})。RP v5计划包也已公开。科学源tag R7C3H0与编辑handoff tag R7C3H1B职责不同，不把后者当新分析结果。

## 当前门户执行边界

浏览器工具分别尝试打开官方 for-authors 页面及恢复该页面，连续两次30秒timeout/reset。没有取得可用页面状态；不能据此断言用户未登录，也没有实际上传文件、操作submission form或生成publisher proof。主稿和SI WPS32页本地proof已经通过，不能替代publisher proof。

## 作者现在可执行的步骤

1. 从[期刊官方作者页](https://www.nature.com/npjgenmed/for-authors-and-referees/submisions)或[期刊首页](https://www.nature.com/npjgenmed/)点击 Submit manuscript，进入当前官方系统。使用作者自身账号；不要发送密码或令牌。
2. Article；Zhi Chen第一作者、Teng Qi通讯作者，核对ORCID与单位。身份与原创新稿/一稿专投/无资助/无冲突/AI声明已确认；门户需要的具体字段以真实页面为准。
3. 只选择一个 Main Manuscript：Manuscript_SubmissionCandidate.docx。加载六FigurePDF、SI PDF、工作簿、三SourceData ZIP和cover DOCX，按实际槽位映射13文件。如果门户不接收ZIP，按原成员身份解包并说明；如果自动重复插入已嵌入的图，调整组装选择并生成新proof，不改原图字节。
4. Generate/Build PDF后下载完整proof。核对title/authors/abstract、两条原生LD方程、Figure3d指向、Figure1–6图注同图、SI和附件完整；对每个门户文件保存文件名/role/大小/上传时间。记录是否有自动重复图或丢失特殊符号。
5. 本轮没有代签门户认证表单或触发真实投稿。最终提交前以proof与已批准清单一致为门。拿到manuscript ID/回执后记录实际日期；在此前SUBMISSION_COMPLETED=NO。

## 当前成果和后续科研

PBC与现稿继续GO。暂不换疾病、不扩候选、不批量重跑642模型或486,000模拟。可选组合gate校准、明确参与者独立疾病研究、direct eQTL-caQTL后验只在独立协议下推进；它们不是完成现稿有限论断的隐含前提。此阶段目标是**实际publisher proof与回执**，不是再造一轮阳性结果。
'''
(REL/'00_R7C3H1C_已批准文件_门户校样下一步.md').write_text(guide,encoding='utf-8')
for d in [REPO/'6_release/r7c3h1b',handoff/'08_Protocol']:shutil.copy2(REL/'00_R7C3H1C_已批准文件_门户校样下一步.md',d/'00_R7C3H1C_已批准文件_门户校样下一步.md')
reportpath=ROOT/'7.Report/rounds/R7C3H1B_20261013/99_R7C3H1B_详细行动记录_20261013.md'
addition=f'''\n## 13 发布后核验与后续作者批准\n\nGitHub Release已真实创建：{release['html_url']}。候选ZIP14,389,068bytes，GitHub digest与本地SHA `{sha(package)}` 完全一致；RP v5 ZIP17,920,623bytes，digest `ffb8ee360c4a63f229c3d0a9c47fef6518d9e98576d2e51165456bd6eb465417`一致。旧source release不变。本ZIP内部69/69 checksum和CRC通过；ZIP为批准前冻结的不可变快照。\n\n随后收到直接人类答复“**两位作者批准这套精确版本**”。AUTHOR_APPROVAL_RECEIPT把答复绑定本ZIP和13文件全部身份；不重打包、不改科学稿件，不把包内历史PENDING当成现在未批准。基本作者声明沿用此前明确确认。\n\n## 14 门户尝试与最终下一阶段\n\n公开入口已查到；浏览器工具连续两次30秒timeout/reset，无页面可读。实际账户登录、文件槽位、publisher-generated PDF均未验证，没有上传或提交；这不是数据/统计失败。准备metadata与按13文件mapping操作说明齐全。当前状态更新为`AUTHOR_APPROVAL=APPROVED_EXACT_FILES`，`PUBLISHER_PROOF=PENDING`，`SUBMISSION_COMPLETED=NO`。下一阶段为 **R7C3H1C_PUBLISHER_PORTAL_PROOF_AND_AUTHOR_OPERATED_SUBMISSION**，完成后必须真实回执闭环。\n\n本报告第11节是作者答复前的阶段快照；本第13–14节是最终状态。公开tag定位冻结交接内容，后续main的收据补充最新作者与发布状态。\n'''
assert '## 13 发布后' not in reportpath.read_text(encoding='utf-8')
reportpath.write_text(reportpath.read_text(encoding='utf-8')+addition,encoding='utf-8')
for d in [REPO/'7.Report/rounds/r7c3h1b',handoff/'07_Reports']:
    shutil.copy2(reportpath,d/reportpath.name)
readme=REPO/'README.md';text=readme.read_text(encoding='utf-8')
text=text.replace('approval of this exact candidate and actual portal proof are pending','approval of this exact candidate was received on 13 October 2026; actual portal proof is pending')
text=text.replace('exact-version author reconfirmation and publisher-generated PDF proof remain pending','exact-version author approval is recorded; publisher-generated PDF proof remains pending')
text=text.replace('| Current verified release | [R7C3H0 GitHub Release]', '| Scientific source release | [R7C3H0 GitHub Release]')
text=text.replace('## Scientific question and narrative','Current candidate publication: [R7C3H1B Release]('+release['html_url']+'). [Exact-file approval receipt](6_release/r7c3h1b/AUTHOR_APPROVAL_RECEIPT.json) and [publisher-proof next steps](6_release/r7c3h1b/00_R7C3H1C_已批准文件_门户校样下一步.md) preserve the approved ZIP bytes.\n\n## Scientific question and narrative')
readme.write_text(text,encoding='utf-8')
shutil.copy2(Path(__file__),REPO/'2_code/11_manuscript/R7C3H1B'/Path(__file__).name)
shutil.copy2(ROOT/'2_code/11_manuscript/R7C3H1B_20261013/11_package_handoff.py',REPO/'2_code/11_manuscript/R7C3H1B/11_package_handoff.py')
print(json.dumps(dict(approval=approval['status'],publication=publication['status'],scientific_uploads_changed=False,next='PUBLISHER_PORTAL_PROOF_AND_AUTHOR_OPERATED_SUBMISSION')))
