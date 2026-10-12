"""Create navigable evidence catalogues and a hash-frozen submission candidate.

Copies the WPS-verified R7C3B assets unchanged. Does not claim author approval,
portal completion, a journal receipt, a minted DOI, or new biological findings.
"""
from pathlib import Path
import csv,json,shutil,zipfile,hashlib,importlib.util,re
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit',HERE/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=a.ROOT;OUT=a.OUT;DATE='20261012';STAGE='R7C3C'
BASE=ROOT/'5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011'
REPORT=ROOT/'7.Report/rounds/R7C3C_20261012'
PACK=ROOT/'5_manuscript/R7C3C_SubmissionCandidate_20261012'
RELEASE=ROOT/'6_release/R7C3C_2026-10-12'
REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence'

def text(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.rstrip()+'\n',encoding='utf-8')
def load(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))

def migrate_path(s):
    for row in json.loads((OUT/'organization/MOVE_JOURNAL.json').read_text(encoding='utf-8')):
        src,dst=row['source'],row['destination']
        if s==src or s.startswith(src+'/'):return dst+s[len(src):]
    return s

def checksum_zip(root,path):
    files=sorted(p for p in root.rglob('*') if p.is_file() and p.name!='checksums.sha256')
    text(root/'checksums.sha256','\n'.join(a.digest(p)+'  '+p.relative_to(root).as_posix() for p in files))
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(root).as_posix())
    with zipfile.ZipFile(path) as z:
        bad=z.testzip();count=0
        for line in z.read('checksums.sha256').decode('utf-8-sig').splitlines():
            h,n=line.split('  ',1)
            if hashlib.sha256(z.read(n)).hexdigest()!=h:raise ValueError('Internal hash mismatch '+n)
            count+=1
        if bad:raise ValueError('ZIP CRC failed '+bad)
    h=a.digest(path);text(path.with_suffix('.zip.sha256'),h+'  '+path.name)
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':h,'ZIP_CRC':'PASS','internal_checksums_pass':count,'entries':count+1}

def main():
    REPORT.mkdir(parents=True,exist_ok=True);RELEASE.mkdir(parents=True,exist_ok=True)
    bs=json.loads((OUT/'before/STATE.json').read_text(encoding='utf-8'))
    org=json.loads((OUT/'organization/STATE.json').read_text(encoding='utf-8'))
    integrity=json.loads((OUT/'integrity/STATE.json').read_text(encoding='utf-8'))
    roles={
        '0_admin':('项目管理、规范、环境与仓库','navigation/ 为当前入口；protocol/current/ 保留各阶段历史状态；skills/ 为 QiTeng；tooling/ 为 R/包/安装器；repositories/ 为 GitHub 镜像。'),
        '1_data':('原始来源数据与下载身份','gwas/、qtl/、study_inputs/、reference/、catalogs/。原始 GWAS、genotype、QTL 不随公开 GitHub 镜像上传。'),
        '2_code':('可执行分析与发布代码','06_intake/ 为各项目门控；11_manuscript/ 为写作制作；00_workspace_management/ 为本轮清点、迁移、回滚。运行环境已移到 0_admin/tooling。'),
        '3_results':('可复算结果与验收','00_audit/、03_qtl/、04_integration/、05_simulation/、05_tissue/ 按阶段留存。历史 FAIL/HOLD 不删除、不解释成阳性。'),
        '4_figures':('分析图与源图','按项目/阶段保存；投稿图当前权威副本位于 5_manuscript/R7C3B.../02_Figures。历史图不自动用于当前稿。'),
        '4_output':('阅读展示与临时导出','figures/ 保留历史 REEP3 导出；review/ 记录当前 WPS 审阅入口。该目录不定义科学结果。'),
        '5_analysis':('自包含分析/审计工作目录','R7C0 为外部证据补强；R7C3 为上一轮全量审计；R7C3C 为本轮 before/after 清单、压缩验证、内容索引、路径迁移与 GitHub 回执。'),
        '5_manuscript':('论文版本与投稿候选','R7C3B 是最新 QiTeng/WPS 精修稿；R7C3C 是其原字节投稿封装。旧 Human Genomics、RP v3/v4 分支保留。'),
        '6_release':('冻结交付包','R7C3C_2026-10-12 为本轮投稿候选包和审计包；每包均带 SHA-256 与内部清单。旧 stage 和 staging 构建目录是历史版本。'),
        '7.Report':('行动记录、技术报告与项目记忆','rounds/ 按阶段；project_history/ 为长期对话总结；reorganization/ 为旧迁移报告；本轮入口 rounds/R7C3C_20261012/。'),
        '8.Reference':('文献与外部来源快照','literature/ 原始参考论文；external_resources/ 外部文档；历史 .json 若实际为 HTML 仅作为网页快照，不作为 API JSON。'),
        '9.Version':('研究计划、归档与回滚','当前计划 PBC_研究计划书_RP_v4_20261011.docx；research_plans/ 收录散落旧计划；workspace_snapshots/ 收录旧 YR1.zip；workspace_reorganization/ 保存原路径依赖代码。'),
        '9_Vote':('项目裁决与下一阶段决策','PBC_CurrentDecision_20261012.md 是本轮状态；不替代作者签字、官方 reporting forms 或真正投稿回执。')}
    for folder,(title,body) in roles.items():
        text(ROOT/folder/'README_DIRECTORY.md',f'# {folder} — {title}\n\n更新：2026-10-12。\n\n{body}\n\n总导航：[当前项目与文件入口](../0_admin/navigation/CURRENT_PROJECT_AND_FILES.md)。\n本轮全文件清单：`5_analysis/R7C3C_WorkspaceAudit_Organization_20261012/after/ALL_FILES.tsv`。\n\n目录中的阶段文件是带版本的历史；文件存在不等于其科学假设成立。')
    state={'schema':'YR1_CURRENT_STATE_20261012','date':'2026-10-12','PRIMARY_PROJECT':'PBC','RESEARCH_PLAN':'RP_v4','PBC_PRIMARY_PROJECT':'GO','CURRENT_SCIENTIFIC_BASELINE':'R7C1/R7C2; R7B2A matched-input analysis','CURRENT_EDITORIAL_BASELINE':'R7C3B_QiTeng_WPS_20261011','CURRENT_ADMINISTRATIVE_STAGE':'R7C3C_FULL_AUDIT_ROOT_ORGANIZATION_PUBLIC_SYNC','SSc':'FROZEN_ARCHIVE','MG':'NO_GO_REGULATORY_MAIN_ARCHIVED','IgAN':'FROZEN_ARCHIVE','OPEN_DATA_ONLY':True,'NEW_BIOLOGICAL_ANALYSIS_REQUIRED':False,'FRESH_AUTHOR_APPROVAL':'PENDING_FOR_R7C3B_EDITED_ASSETS','REPORTING_FORMS':'FACTUAL_ANSWERS_READY_OFFICIAL_FORMS_PENDING','FINAL_FIGURE_WIDTH':'PORTAL_OR_PUBLISHER_PROOF_PENDING','PUBLISHER_PORTAL_PROOF':'PENDING','SUBMISSION_COMPLETED':False,'ZENODO_DOI':'NOT_VERIFIED_PUBLISHED_NO_NEW_DOI_THIS_ROUND','GITHUB_PUBLIC_SYNC':'PREPARED_PENDING_PUSH','NEXT':'R7C4_AUTHOR_FINAL_VERSION_CONFIRMATION_REPORTING_FORMS_PORTAL_PROOF_AND_SUBMISSION_RECEIPT'}
    a.save_json(ROOT/'0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json',state)
    paths={'schema_version':'YR1_PATHS_3.0','workspace_root':str(ROOT),'canonical_root_folders':list(roles),'current_state':str(ROOT/'0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json'),'navigation':str(ROOT/'0_admin/navigation/CURRENT_PROJECT_AND_FILES.md'),'repo_local':str(REPO),'repo_url':'https://github.com/1209433622cz-maker/igan-open-regulatory-evidence','Rscript':str(ROOT/'0_admin/tooling/R/R-4.6.1/bin/x64/Rscript.exe'),'R_library':str(ROOT/'0_admin/tooling/R-library'),'QiTeng_runtime':str(ROOT/'0_admin/skills/qiteng_runtime_v03242'),'research_plan_v4':str(ROOT/'9.Version/PBC_研究计划书_RP_v4_20261011.docx'),'manuscript_latest':str(BASE/'01_Manuscript/R7C3B_npj_Manuscript.docx'),'submission_bundle':str(RELEASE/'CMM_R7C3C_npj_Submission_Candidate_20261012.zip'),'audit':str(OUT),'report':str(REPORT),'historical_paths_map':str(ROOT/'9.Version/workspace_reorganization/R7C3C_20261012/admin_navigation_before/workspace_paths.json'),'rollback_script':str(HERE/'ROLLBACK_ORGANIZATION.py')}
    a.save_json(ROOT/'0_admin/workspace_paths.json',paths)
    text(ROOT/'0_admin/WORKSPACE_MAP.md','# 工作区结构与最新状态\n\n旧 R4A12 路径字典已按原字节保存在 `9.Version/workspace_reorganization/R7C3C_20261012/admin_navigation_before/`。\n\n当前：[项目与文件入口](navigation/CURRENT_PROJECT_AND_FILES.md)。机器路径：`workspace_paths.json`。本轮根目录只保留截图中的 13 个文件夹，未删除任何原始资产。\n\n文件级移动映射和校验：`5_analysis/R7C3C_WorkspaceAudit_Organization_20261012/organization/`。')
    table='\n'.join('| '+f+' | '+x[0]+' | '+x[1]+' |' for f,x in roles.items())
    text(ROOT/'0_admin/navigation/CURRENT_PROJECT_AND_FILES.md',f'''# YR1 当前项目与文件入口

更新：2026-10-12。主项目为 PBC，按照 RP v4 双轨计划推进。当前稿件定位为调控归因可靠性、同输入方法比较与多信号解释，不能包装成两个新因果基因或普遍优越的新算法。

| 文件夹 | 科学/管理职责 | 分类与使用说明 |
|---|---|---|
{table}

## 本轮实际入口

- 最新主稿：[R7C3B_npj_Manuscript.docx](../../5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/01_Manuscript/R7C3B_npj_Manuscript.docx)。WPS 对照 PDF 29 页。
- 最新投稿封装：`6_release/R7C3C_2026-10-12/CMM_R7C3C_npj_Submission_Candidate_20261012.zip`。
- 资产与未来用途：`5_analysis/R7C3C_WorkspaceAudit_Organization_20261012/catalogue/VALUABLE_ASSETS.tsv`。
- 全量文件大小、SHA-256、内容深度、用途和公开边界：`5_analysis/R7C3C_WorkspaceAudit_Organization_20261012/after/ALL_FILES.tsv`。
- 行动记录：`7.Report/rounds/R7C3C_20261012/99_CMM_R7C3C_详细行动记录_20261012.md`。
- 公开仓库：[GitHub](https://github.com/1209433622cz-maker/igan-open-regulatory-evidence)，本地 `0_admin/repositories/igan-open-regulatory-evidence`。

## 当前结论与边界

6,923 个冻结比较中 5,460 可筛查；642 个预先冻结高信息比较接受多信号分析，不是 6,923 个比较全部做多信号。PF10 为 92 H4、428 H3、59 sensitive、63 uninformative，H4 涉及 27 genes / 19 loci。486,000 次模拟显示假 H4 减少伴随共享信号恢复率下降；不能只报告收益。两条分子轴和外部 IL12RB2 证据保留，组织层 5 vs 5 不支持 PBC 特异富集。

下一阶段是作者核对最终文件、官方 reporting forms、门户 PDF proof 和真实投稿回执。当前尚未投稿；本轮没有新 DOI。旧 `protocol/current` 内的逐阶段文件保持历史身份，使用 `PBC_CURRENT_STATE_20261012.json` 查最新状态。SSc/MG/IgAN 不自动恢复。
''')
    text(ROOT/'9_Vote/PBC_CurrentDecision_20261012.md',f'''# 2026-10-12 项目裁决

PBC 继续 GO，保留 RP v4 的原投稿候选基线和有边界的外部补强。最新文件是 R7C3B QiTeng/WPS 版，本轮只清点、分类、核验、封装与公开同步，不改科学数字、不重跑模型。

- SSc、MG、IgAN 仍归档；不寻找新阳性或新候选。
- 投稿目标 npj Genomic Medicine / Article。既有 Human Genomics 候选稿保留为退稿后可考虑的历史备选，不进行同时投稿。
- 作者身份和原始声明已确认；编辑后的 R7C3B 文件批准仍待真实确认，不能由打包或 GitHub 推送自动替代。
- 官方 reporting forms、最终图宽度和 publisher PDF proof 待完成；尚无投稿回执。
- 全量审计发现的两份 HTML-in-JSON 历史网页快照及一份 JSON-with-comments 第三方配置，不破坏当前 PBC 科学输入。

下一阶段：`{state['NEXT']}`。无新增生物学分析的默认要求。只有真正收到审稿意见或发现破坏核心结论的来源/模型错误，才重开针对性分析。
''')
    text(ROOT/'4_output/review/R7C3C_20261012/README.md','# 当前阅读导出入口\n\nR7C3B 全部 PDF 由 WPS 后台导出。29 页候选主稿、30 页内嵌审阅稿、2 页 SI、1 页投稿信共有 62 页，上一轮逐页审阅记录已冻结。本轮文件字节保持一致，未调用其他文档渲染器。\n\n原件：`5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/`。门户最终 PDF 不在此目录，须真正上传后获取。')
    # Catalogue existing assets, refresh obsolete CURRENT labels, retain historic provenance.
    old=load(ROOT/'5_analysis/R7C3_FullWorkspaceAudit_2026-10-11/assets/R7C3_high_value_asset_ledger.tsv');ledger=[]
    for r in old:
        rel=migrate_path(r['relative_path']);p=ROOT/rel
        if not p.exists():continue
        r.update(relative_path=rel)
        if r['asset_group']=='CURRENT_PAPER':r['asset_group']='ARCHIVED_SUBMISSION_BASELINE'
        if p.is_file():r['sha256_or_receipt']=a.digest(p)
        ledger.append(r)
    for rel,role,use,boundary in [
        ('5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011','LATEST_EDITORIAL_BASELINE','Latest QiTeng/WPS manuscript, legends, declarations, 83-check QA and 62-page review; author version approval pending','PUBLIC_CANDIDATE_NOT_SUBMITTED'),
        ('5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/01_Manuscript/R7C3B_npj_Manuscript.docx','MAIN_UPLOAD_CANDIDATE','One primary editable manuscript; Figure 1–6 at end, 12-word title, 135-word abstract','PUBLIC_CANDIDATE'),
        ('5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/08_Protocol/Reporting_Summary_Factual_Answer_Sheet_DRAFT.md','OFFICIAL_FORM_FACTS','Verified factual answers for Nature reporting; not an official completed form','AUTHOR_REVIEW'),
        ('7.Report/project_history','PROJECT_MEMORY','Long-form conversation summaries and decisions; use to avoid repeating failed projects, preserve input and claim boundaries','LOCAL_REDACTION_REQUIRED'),
        ('9.Version/workspace_snapshots/received_undated/YR1.zip','HISTORICAL_WORKSPACE_SNAPSHOT','Byte-preserved received project snapshot; no assumption that date or contents are latest','LOCAL_ARCHIVE'),
        ('0_admin/tooling','ENVIRONMENT','Reusable installed R, coloc, susieR and package library; not public source-data assets','THIRD_PARTY_LOCAL_RUNTIME'),
        ('0_admin/skills/qiteng_runtime_v03242','WRITING_AUTHORITY','Active v0.3.24.2 Registry + Core; evidence/archives do not override Runtime','LOCAL_SKILL_NOT_VALIDATED_UNIVERSAL_WRITER'),
        ('2_code/00_workspace_management/R7C3C_20261012','WORKSPACE_REUSE','Long-path hashing, format-aware indexing, byte-preserving moves, rollback, package/manifest QA','PUBLIC_ORIGINAL_CODE'),
        ('3_results/00_audit/R5A2A2_archive_member_audit','HISTORICAL_DATA_ENGINEERING','Archive member inventory reused to verify source contents; not positive molecular evidence','LOCAL_PROVENANCE'),
        ('1_data/gwas/PBC/FinnGen_R13/indices/finngen_R13_CHIRBIL_PRIM.gz.tbi','UNPAIRED_TABIX_INDEX','Index sidecar retained; corresponding complete GWAS gzip is not present here. Cannot count index as downloaded GWAS bytes','METADATA_ONLY_PUBLIC'),
    ]:
        p=ROOT/rel
        if not p.exists():raise FileNotFoundError(rel)
        files=[p] if p.is_file() else [x for x in p.rglob('*') if x.is_file()]
        ledger.append({'asset_group':'CURRENT_OR_REUSABLE','role':role,'relative_path':rel,'kind':'FILE' if p.is_file() else 'DIRECTORY','file_count':len(files),'size_bytes':sum(x.stat().st_size for x in files),'size_gib':sum(x.stat().st_size for x in files)/1024**3,'sha256_or_receipt':a.digest(p) if p.is_file() else 'DIRECTORY_FILE_HASH_MANIFEST','value_and_future_use':use,'publication_boundary':boundary})
    a.tsv(OUT/'catalogue/VALUABLE_ASSETS.tsv',ledger)
    timeline=load(ROOT/'5_analysis/R7C3_FullWorkspaceAudit_2026-10-11/assets/R7C3_retained_stage_timeline.tsv')
    timeline+= [{'phase':'R7C3B_editorial','primary_question':'Do argument, manuscript, panels, sources and WPS review agree?','final_disposition':'COMPLETE_EDITORIAL_WPS_QA_VERSION_APPROVAL_PENDING','retained_value':'83 checks; 48 unchanged scientific members; 62 WPS pages; 19 numbered and six URL reference identities','future_use':'Final author file confirmation, official reporting forms and portal proof'},{'phase':'R7C3C_stewardship','primary_question':'Are all local assets searchable, in canonical folders and safely synchronized?','final_disposition':'AUDIT_ORGANIZE_PACKAGE_PUBLIC_SYNC','retained_value':'Fresh byte hashes, long-path recovery, exact move identities, content and work-record indexes, public-safe pointers','future_use':'Submission handoff and reproducible long-term stewardship'}]
    a.tsv(OUT/'catalogue/PROJECT_TIMELINE.tsv',timeline)
    records=load(OUT/'contents/WORK_RECORD_CONTENT_INDEX.tsv')
    filtered=[r for r in records if not any(x in r['path'] for x in ('.qiteng_v03242_runtime','tools/','github/','/skills/','/tooling/','/repositories/'))]
    for r in filtered:r['path']=migrate_path(r['path'])
    a.tsv(OUT/'catalogue/PROJECT_WORK_RECORDS.tsv',filtered)
    a.save_json(OUT/'catalogue/STATE.json',{'curated_asset_groups':len(ledger),'project_work_records_including_historical_copies':len(filtered),'raw_record_search_hits':len(records),'warning':'Counts are files/search hits, not independent completed experiments. Historical status tokens do not define the latest state.'})
    # Public pointer manifest: sizes/hashes and source metadata only; no raw data contents.
    before=load(OUT/'before/ALL_FILES.tsv');large=[]
    for r in before:
        if int(r['size_bytes'])<=10*1024**2 or r['category'] in ('GIT_INTERNAL','ENVIRONMENT_OR_SKILL','PUBLIC_MIRROR'):continue
        large.append({'workspace_path':migrate_path(r['relative_path']),'bytes':r['size_bytes'],'sha256':r['sha256'],'publication':'METADATA_ONLY_NOT_MIRRORED','source_lookup':'data/LARGE_DATA_MANIFEST.tsv or data/DATA_AVAILABILITY.md; original input manifests','use':r['category']})
    a.tsv(OUT/'catalogue/LARGE_ASSET_POINTERS_PUBLIC.tsv',large)
    # All candidate scientific/editorial assets remain byte-identical to the WPS-verified baseline.
    assetpairs=[('01_Manuscript/R7C3B_npj_Manuscript.docx','01_Main/Manuscript.docx','PRIMARY_EDITABLE_MAIN'),('01_Manuscript/R7C3B_npj_Manuscript.pdf','01_Main/Manuscript_WPS_Review.pdf','LOCAL_PARITY_PDF_NOT_SECOND_MAIN'),('03_Supplement/R7C3B_Supplementary_Information.pdf','03_Supplement/Supplementary_Information.pdf','SUPPLEMENTARY_INFORMATION'),('03_Supplement/R7C3B_Supplementary_Information.docx','03_Supplement/Supplementary_Information_Editable.docx','EDITABLE_COMPANION_CONDITIONAL'),('03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx','03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx','SUPPLEMENTARY_DATA_1'),('04_Cover/R7C3B_Cover_Letter_Candidate.docx','04_Cover/Cover_Letter.docx','COVER_CANDIDATE_DATE_11_OCT_UPDATE_ON_ACTUAL_SUBMISSION'),('04_Cover/R7C3B_Cover_Letter_Candidate.pdf','04_Cover/Cover_Letter_WPS_Review.pdf','LOCAL_COVER_PARITY'),('05_Source_Data/Source_Data_1_Primary_Machine_Readable_Data.zip','05_Source_Data/Source_Data_1_Primary_Machine_Readable_Data.zip','SOURCE_DATA_1'),('05_Source_Data/Source_Data_2_External_Regulatory_Evidence.zip','05_Source_Data/Source_Data_2_External_Regulatory_Evidence.zip','SOURCE_DATA_2_S11')]
    assetpairs += [(f'02_Figures/Figure_{i}.pdf',f'02_Figures/Figure_{i}.pdf','SEPARATE_FIGURE_ONLY_IF_PORTAL_REQUIRES') for i in range(1,7)]
    identities=[]
    for src,dst,role in assetpairs:
        sp,dp=BASE/src,PACK/dst;dp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(sp,dp)
        h=a.digest(sp);h2=a.digest(dp)
        if h!=h2:raise ValueError('Asset differs '+dst)
        identities.append({'package_path':dst,'source':sp.relative_to(ROOT).as_posix(),'bytes':dp.stat().st_size,'sha256':h,'identity':'PASS','upload_role':role})
    a.tsv(PACK/'UPLOAD_ROLES_AND_IDENTITIES.tsv',identities)
    for name in ('Numerical_Document_QA.json','QiTeng_S01-S22_Production_Gate.tsv','WPS_Export_Receipt.json','Scientific_Source_Data_48_Identity.tsv'):
        dp=PACK/'06_Verification'/name;dp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/'06_QA'/name,dp)
    text(PACK/'README_SUBMISSION.md','''# npj Genomic Medicine — submission candidate, not a submitted manuscript

Package date: 12 October 2026. Manuscript science and editorial text are R7C3B (11 October), unchanged. All PDF companions are the original WPS background exports. No new document renderer or new biological model was used.

Use one primary main file: `01_Main/Manuscript.docx`. It contains Figure 1–6 at the end. The WPS PDF is for parity review; do not upload it as a second competing main manuscript. Separate figure PDFs are conditional assets if the actual portal requests them. If the portal requires a figure-free main, generate that mode from the same approved text and verify the new hashes/proof before submission. The 30-page inline review copy is deliberately excluded.

Upload one SI PDF, Supplementary Data 1 (ten-sheet XLSX), Source Data 1 and Source Data 2 (including S11) with their distinct file roles. Editable SI and cover/PDF companions are retained for review and conditional portal use, not automatic duplicate supplements.

Before final submission: both authors confirm these exact R7C3B edited assets; complete the actual required reporting forms using the existing factual answer sheet; update the cover date on the true submission date; verify final figure-width legibility and the publisher-generated merged PDF. Never treat all 22 production gates as PASS: S09, S18, S19 and S22 remain conditional/pending. Originality, author identity, no funding/conflicts and AI disclosure were confirmed previously; this package does not sign for either author.

Licences: original code MIT; original author text/figures/documentation/aggregate derived results CC BY 4.0, subject to repository NOTICE and source-specific restrictions. Third-party raw datasets, donor genotype, pseudobulk, raw LD/BAM and published articles are excluded. No Zenodo DOI or journal receipt was minted in this operation.

Current official instructions (indexed text rechecked 12 October; direct page retrieval limited): https://www.nature.com/npjgenmed/for-authors-and-referees/guide-to-authors/about/content-types ; https://www.nature.com/npjgenmed/editorial-policies/reporting-standards . The old 2018 typography PDF is archival guidance, not proof of the current portal workflow.
''')
    package_receipt=checksum_zip(PACK,RELEASE/'CMM_R7C3C_npj_Submission_Candidate_20261012.zip')
    a.save_json(RELEASE/'SUBMISSION_PACKAGE_RECEIPT.json',package_receipt)
    a.save_json(OUT/'submission/IDENTITY_STATE.json',{'unchanged_assets':len(identities),'all_original_sha256_identical':True,'source_scientific_members':48,'baseline_QA':'83/83 from R7C3B; inherited through exact file identity, not re-executed models','WPS_PDF':'Original byte-identical WPS exports; no new export necessary','fresh_author_approval':'PENDING','portal_proof':'PENDING','submitted':False,'package':package_receipt})
    a.save_json(OUT/'submission/OFFICIAL_GUIDELINES_20261012.json',{'official_urls':['https://www.nature.com/npjgenmed/for-authors-and-referees/guide-to-authors/about/content-types','https://www.nature.com/npjgenmed/editorial-policies/reporting-standards'],'date':'2026-10-12','verification':'Official indexed content verified using search; direct opens returned Internal Error. No claim of live portal conformity.','article_title_limit':15,'abstract_limit':150,'current_title_words':12,'current_abstract_words':135,'old_typography_pdf':'2018 archive; secondary, explicitly dated'})
    text(REPORT/'02_有价值资产与未来复用.md','''# 有价值成果与后续用途

## 当前论文可用成果

PBC-wide 问题已从两个候选基因上升为调控归因可靠性审计：6,923 比较的筛查范围、642 高信息子集的对称多信号重分类、A0/A1/A2/M 同输入对照、PF10/PF50 模型匹配敏感性、signal-pair 身份检查和 486,000 模拟共同支撑核心贡献。没有覆盖全部低信息比较，因此不称全 PBC 组合多信号图谱。

PF10 的 92/428/59/63 状态应从当前稿件源表理解；早期 R7B1B 的 78/409 等旧稳定定义仍留作历史，不能混作同一分母。PF10 H4 支持 27 genes / 19 loci。模拟中 false-H4 12.41%→8.56% 的改善伴随 H4 recovery 32.99%→26.66% 的代价，均需报告。47 位点聚类重抽样衡量固定范围的构成敏感性，不是全体 PBC 位点的总体置信区间。

IL12RB2–NK 与 FCRL3–B 保留分子证据；FCRL3–CD8_ET 的模型反转、INAVA 弱 QTL 与 5 vs 5 非显著组织差异是论文重要边界。TenK 复用相同疾病 GWAS，是跨分子 QTL 资源复制，不能算独立疾病复制。FinnGen R13 是不同疾病研究系统，参与者独立性未知。caQTL/eQTL/peak–gene triangle 不等于直接 eQTL–caQTL 共定位或染色质介导。OMIX 单病例单对照不能提供人群空间复制。

## 方法与工程资产库

- SSc：variant identity、build/allele harmonization、H6 输入门、source-CS coverage、公开数据与权限排除、checksum/provenance 状态机。
- MG：亚型效应异质性、真实细胞供者集合、bounded gene competition、source-LD、未触发与失败的明确停止规则。
- IgAN：正控定义修正、8-locus bounded expansion、REEP3 亚洲特异发现与失败复制、公开蛋白与组织层 completion gate。
- PBC：study-matched disease LD、QTL source/model-matched residualized LD、同输入方法对照、模拟校准、donor-level pseudobulk、图表数据连结和 QiTeng/WPS 制作审计。
- 本轮：完整字节哈希、长路径文件访问、内容深度标记、可回滚分类、公开大文件元数据指针。

这些内容可用来设计其他公开数据疾病研究、回答审稿问题与复算现有论文，但不自动重启归档项目、增加 PBC 候选或用于宣称新因果机制。

## 工作记录与长期记忆

全量工作记录文件按路径、标题、章节、阶段标签、大小和 SHA-256 建索引。重复归档、模板和公开镜像均与项目原始记录区分；计数是文件/搜索命中数，不是独立分析数量。`7.Report/project_history` 的对话总结解释多次选题切换原因，可用于避免重复补救已经失败的路线；阶段协议解释数字和定义如何变化。

机器入口：`catalogue/VALUABLE_ASSETS.tsv`、`PROJECT_TIMELINE.tsv`、`PROJECT_WORK_RECORDS.tsv` 与 `contents/WORK_RECORD_CONTENT_INDEX.tsv`。全文科学证据应回到原始阶段源表和受冻结协议约束的代码；不能只凭工作记录的 PASS token 下科学结论。
''')
    print(json.dumps({'asset_groups':len(ledger),'project_work_records':len(filtered),'submission_asset_identity_pass':len(identities),'package':package_receipt},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
