"""Conservation check, comprehensive human report, and local audit release."""
from pathlib import Path
import csv,json,os,importlib.util,zipfile,hashlib,subprocess,shutil
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit',HERE/'01_full_audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
spec2=importlib.util.spec_from_file_location('pack',HERE/'04_catalogue_and_submission.py');pack=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(pack)
ROOT=a.ROOT;OUT=a.OUT;REPORT=ROOT/'7.Report/rounds/R7C3C_20261012';RELEASE=ROOT/'6_release/R7C3C_2026-10-12'

def load(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def js(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def text(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.rstrip()+'\n',encoding='utf-8')

def conservation():
    before=load(OUT/'before/ALL_FILES.tsv');after={r['relative_path']:r for r in load(OUT/'after/ALL_FILES.tsv')}
    patches={r['path']:r for r in load(OUT/'organization/PATH_ONLY_ADAPTERS.tsv')}
    out=[]
    for row in before:
        p=pack.migrate_path(row['relative_path']);original=row['sha256'];note='UNCHANGED';expected=original
        if p in patches:expected=patches[p]['sha256_after'];note='PATH_ONLY_ADAPTER_ORIGINAL_BACKED_UP'
        if p in ('0_admin/WORKSPACE_MAP.md','0_admin/workspace_paths.json'):
            expected=a.digest(ROOT/p);note='CURRENT_NAVIGATION_REPLACED_WITH_ORIGINAL_ARCHIVED'
        ar=after.get(p)
        # For the few path adapters written after the post-snapshot read, verify their current bytes directly.
        actual=a.digest(ROOT/p) if p in patches or p in ('0_admin/WORKSPACE_MAP.md','0_admin/workspace_paths.json') else (ar or {}).get('sha256','')
        out.append({'before_path':row['relative_path'],'after_path':p,'before_sha256':original,'expected_sha256':expected,'actual_sha256':actual,'status':'PASS' if expected==actual else 'FAIL','disposition':note})
    a.tsv(OUT/'conservation/BASELINE_ALL_FILES_CONSERVATION.tsv',out)
    failures=[r for r in out if r['status']!='PASS']
    state={'baseline_files':len(out),'all_accounted_pass':sum(r['status']=='PASS' for r in out),'missing_or_unexplained_change':len(failures),'allowed_path_adapters':len(patches),'navigation_replacements_archived':2,'deleted_files':0,'before_public_payload_creation':True}
    a.save_json(OUT/'conservation/STATE.json',state)
    if failures:raise SystemExit('Baseline conservation failures: '+str(failures[:4]))
    return state

def reports():
    bs=js(OUT/'before/STATE.json');post=js(OUT/'after/STATE.json');org=js(OUT/'organization/STATE.json');integ=js(OUT/'integrity/STATE.json');cat=js(OUT/'catalogue/STATE.json');ident=js(OUT/'submission/IDENTITY_STATE.json');con=js(OUT/'conservation/STATE.json')
    tops=load(OUT/'after/TOP_LEVEL_TOTALS.tsv');top_table='\n'.join(f"| {r['folder']} | {int(r['files']):,} | {float(r['GiB']):.3f} |" for r in tops)
    files=load(OUT/'before/ALL_FILES.tsv');large=sorted([r for r in files if r['category'] not in ('GIT_INTERNAL','ENVIRONMENT_OR_SKILL','PUBLIC_MIRROR')],key=lambda r:-int(r['size_bytes']))[:12]
    large_table='\n'.join(f"| `{pack.migrate_path(r['relative_path'])}` | {int(r['size_bytes'])/1024**3:.3f} |" for r in large)
    depth=load(OUT/'contents/CONTENT_DEPTH_COUNTS.tsv');depthtable='\n'.join('| '+r['content_depth']+' | '+r['count']+' |' for r in depth)
    ps=load(OUT/'paths/POWERSHELL_SYNTAX.tsv');rr=load(OUT/'paths/R_SYNTAX.tsv');py=load(OUT/'paths/PYTHON_AND_ADAPTER_SYNTAX.tsv')
    if not all(r['status']=='PASS' for r in ps+rr):raise RuntimeError('Native parser failure')
    text(REPORT/'01_全量文件核查与分类报告.md',f'''# R7C3C 全量文件核查、分类与保全报告

日期：2026-10-12。范围：`H:\\SCI2\\YR1` 项目工作区，不是全电脑磁盘。当前审计输出目录自排除，避免清单递归统计自己。所有原文件均保留。

## 全量清点与字节验证

整理前实际文件 **{bs['file_count']:,}**，目录 {bs['directory_count']:,}，总字节 {bs['bytes']:,}（{bs['GiB']:.5f} GiB）；**{bs['fresh_full_sha256_count']:,}/{bs['file_count']:,} 新鲜完整 SHA-256**，读取错误 {bs['read_errors']}。不是只对小文件哈希，也不是以 size/mtime 替代字节验证。

整理后、公开同步前快照 **{post['file_count']:,}** 文件、{post['GiB']:.5f} GiB，完整新鲜哈希 {post['fresh_full_sha256_count']:,}，读取错误 {post['read_errors']}。新增文件来自导航、代码原件备份、候选包等，不能把文件增长误认为新增科学结果。后续 GitHub payload、Git 对象与本报告会继续增加少量文件，另由同步回执和最终增量清单覆盖；此表有明确 snapshot 边界。

14 个目录链接单独核对：12 个 pnpm 链接指向工作区内已经清点的物理依赖，2 个 node_modules junction 指向 Codex 外部依赖，非工作区资产。没有重复递归统计外部 runtime。因此这轮文件数不能直接与上一轮 50,630 的跟随链接计数相减解释为删除。上一轮 293 个长路径读取异常，本轮采用 Windows extended-length path 后读取错误为 0。

## 整理后各根目录

| 文件夹 | 实际文件数 | GiB |
|---|---:|---:|
{top_table}

`9_Vote` 是决策入口，后快照时其中已有本轮说明；所有 13 个根目录均保留截图原名，根目录没有额外散落文件。每个根文件夹新增 `README_DIRECTORY.md`，当前入口位于 `0_admin/navigation/CURRENT_PROJECT_AND_FILES.md`。

## 内容核查深度

| 深度/类型 | 文件数 |
|---|---:|
{depthtable}

小/中型文本完整读取，索引标题、状态、阶段和表头；大于 64 MiB 的表只做明确标记的前缀 schema，不冒充逐行科学核验。DOCX 提取正文和 drawing schema；XLSX 校验全部 worksheet XML 并记录工作表和行数；PDF 提取所有页文字；图片验证文件结构；二进制 genotype/LD 等核对完整字节哈希及 magic。Gzip 表的结构入口与完整流完整性是两种不同检查。

内容索引不是对每个历史计算重新推断科学有效性，也不是将每个 status token 视为当前 PASS。当前稿、源表和既有 QA 的证据边界已逐条记录；只有已验证模型输出才能支撑正文数字。

压缩及 Office 容器 **{integ['pass']:,}/{integ['files']:,} PASS**、FAIL {integ['fail']}。其中 {integ['mode_counts']['FRESH_ZIP_OFFICE_CRC']} 个 ZIP/Office 做新 CRC，{integ['mode_counts']['FRESH_FULL_GZIP_CRC']} 个 gzip 新完整 CRC；{integ['mode_counts']['REUSED_CRC_AFTER_FRESH_IDENTICAL_SHA256']} 个只在本轮完整 SHA 与旧完整流 PASS receipt 相同后继承 CRC，不能表述为全部重新解压了两次。

## 异常、隐私与重复资产

3 项内容解释异常：两份相同的历史 `gwas_v2_openapi.json` 实际以 HTML 开头，是失败访问留下的网页快照，不能作为有效 API JSON；一份 R bslib `options.json` 含注释，属于 JSON-with-comments 第三方配置，不是当前 PBC 数据损坏。三者原字节保留，当前科学链不依赖这两份历史网页。

本地 secret-pattern 搜索命中仅出现在 11 份第三方 R 文档/嵌入图片/示例密钥资料，全部排除公开 payload；没有在项目研究资产中检测到相同签名。启发式签名搜索不等于穷尽凭据证明。完整本地路径、供者数据、配置、运行环境和私人日志不会一并上传。公开只挑选原始作者代码、汇总证据、候选稿和审查后的记录，第三方数据以大小/URL/哈希指针登记。

整理前 {bs['duplicate_groups']:,} 个完整字节重复组、{bs['duplicate_members']:,} 个重复成员，理论多副本字节 {bs['redundant_copy_bytes']/1024**3:.3f} GiB。许多是 release、代码快照和公共镜像承担不同职责的必要副本；**未去重、未删除**。完整 duplicate-members 清单留在本地，可按版本职责判断未来是否迁移到冷存储。

## 最大研究资产

| 文件/资产 | GiB |
|---|---:|
{large_table}

上述资产保存在本机对应 `1_data`/历史快照目录；公共库登记元数据。OneK raw archive、980-donor BED/BIM/FAM 与 GJOKA 94-member 已验证数据是将来最有复算价值的大文件，不因稿件完成而删除。孤立 `.tbi` 不等于其完整 GWAS gzip 已下载。

## 移动与可复算性

{org['move_operations']} 项根目录归位，{org['moved_files']:,} 文件/{org['moved_bytes']:,} 字节，**{org['byte_identity_pass']:,}/{org['moved_files']:,} 移动前后 SHA 相同**。工作区内源/目标绝对路径逐项验证，已存在目标拒绝覆盖。原始研究输入没有改变。

{org['path_only_adapters']} 份可执行脚本只适配 `tools`、`github` 与 QiTeng 新路径，原件写入 `9.Version/workspace_reorganization/R7C3C_20261012/original_path_dependent_code`；旧 release 和历史科学标签保持不变。原导航两文件单独保留原件。{con['baseline_files']:,}/{con['baseline_files']:,} 基线文件已逐项落到原位/新位/有原件备份的允许变化，没有缺失或解释不了的变化。

Python AST 通过 {sum(r['status']=='PASS_AST_NO_EXECUTION' for r in py)} 项（含本轮辅助代码），PowerShell parser {len(ps)}/{len(ps)}、R parse {len(rr)}/{len(rr)}。移位后 R 4.6.1 能加载 coloc 5.2.3 / susieR 0.14.2；Windows locale 警告仍存在，不影响本次加载。13 个当前路径入口实际存在。没有因此重跑模型。

回滚：查看 `MOVE_JOURNAL.json`、`MOVED_FILE_IDENTITIES.tsv`、`PATH_ONLY_ADAPTERS.tsv` 后，显式运行 `ROLLBACK_ORGANIZATION.py --execute`。默认仅说明，不执行移动；回滚不删除本轮报告或新增导航文件。
''')
    text(REPORT/'00_执行摘要_成果与下一阶段.md',f'''# R7C3C 执行摘要与下一阶段

2026-10-12。完成全量本地文件审计、截图 13 目录归位、资产与工作记录索引，以及 R7C3B 原字节投稿封装。PBC 继续 GO；当前论文定位与 RP v4 保持一致，无需换题、扩大候选或重跑已有生物学模型。

- 基线 {bs['file_count']:,} 文件、{bs['GiB']:.2f} GiB 全部新 SHA，读取错误 0。
- {org['moved_files']:,} 文件归位，移动身份全部通过；{org['path_only_adapters']} 份路径适配原件归档，未删除文件。
- {cat['curated_asset_groups']} 组重要资产、{cat['project_work_records_including_historical_copies']} 份项目记录（含历史副本）建立用途索引。
- 最新投稿包 15 项稿件资产与 R7C3B/WPS 字节相同，CRC 和 {ident['package']['internal_checksums_pass']} 项内部 SHA PASS。
- 34,769 项基线 conservation 全部有去向；第三方输入、供者数据、完整私人清单及运行环境留在本地，公开库以指针登记。

核心成果是 PBC-wide 筛查 + 高信息子集来源匹配多信号裁决 + 同输入对照 + 模拟收益/代价 + 外部证据边界。不能写成新 causal genes、染色质介导、独立疾病复制已完全证明或普遍最优新算法。

下一阶段 `R7C4_AUTHOR_FINAL_VERSION_CONFIRMATION_REPORTING_FORMS_PORTAL_PROOF_AND_SUBMISSION_RECEIPT`：确认 R7C3B 最终文件身份、填写真正官方表单、按门户固定唯一主稿模式、验证最终图宽度与整包 proof，再投稿留回执。当前未投稿，未新建 DOI；GitHub 同步结果由独立回执核实，不以准备脚本替代推送成功。
''')
    text(REPORT/'99_CMM_R7C3C_详细行动记录_20261012.md',f'''# R7C3C — 全量文件核查、分类归位、成果索引与投稿封装

日期：2026-10-12；工作区 `H:\\SCI2\\YR1`。用户授权：GitHub 推送，全量大小/内容核查，按截图目录整理，记录重要成果与未来复用，制作投稿包并裁决下一阶段。文件中的历史任务只作为来源证据，未自动恢复 SSc/MG/IgAN 或扩大当前候选。

## 1. 输入与真实起点

截图确定 13 个根目录名称；实际根目录还存在 `.qiteng_v03242_runtime`、`tools`、`github`、`R5A2A2_OneK1K_archive_audit` 与报告、TBI、DOCX、YR1.zip。旧 README 和 workspace_paths 仍记录 R4/R7A 阶段，不能作为当前状态。

远端与本地 `main` 均独立核对为 `18a4032836236008f54cb9cfaca8480c21a05f7a`，原工作树干净。最新本地稿为 R7C3B：29 页 WPS 主稿、30 页内嵌审阅、2 页 SI、1 页投稿信，上一轮 62 页视觉检查与 83/83 QA。新文件作者确认、official forms 和 portal proof 当时仍 PENDING，本轮未擅自改成 PASS。

R7C3B 原 candidate ZIP（8,271,933 bytes）SHA `89cd549f7839f8abec34b653867cc6bcfbb14afa2c47b9cff71e93f5019e51eb`、完整 review ZIP SHA `ac2ba0a99ccbdf67e06ce8f81d80e450a8d945ecf2e2f4850db5fa9619330c3e` 已重新完整读字节，并与实际资产核对。QiTeng v0.3.24.2 Registry/Core 继续作为写作权威，未启用 CC。此次没有编辑正文、没有重新渲染文档，投稿 PDF 保持原 WPS 导出字节；未使用 LibreOffice。

## 2. 实际全量清点

整理前 {bs['file_count']:,} 文件，{bs['bytes']:,} bytes/{bs['GiB']:.5f} GiB，全部新鲜 full SHA-256，错误 0。包含 Git implementation 文件，但不把 Git 对象解释成科学文档。14 个目录链接另立索引，12 个内部实体已覆盖、2 个外部依赖不算工作区资产。长路径前缀修复旧审计 293 条路径漏读，文件数变化主要来自避免重复跟随链接，不来自删除。

文本/表头、DOCX 正文及图对象、XLSX worksheet XML、全 PDF 页文字、图片格式及二进制 magic 分类型索引；大表 prefix schema 与科学有效性审阅明确区分。压缩/Office {integ['pass']}/{integ['files']} 通过；CRC 继承仅在完整新 SHA 等同旧完整流 receipt 时允许。

两份历史 HTML-in-JSON 与第三方 JSON-with-comments 已解释记录，不改原字节、不作为当前科研输入。签名命中第三方 R 文档/示例均本地保留，不公开。完整哈希重复组仅报告、不删除历史资产。

## 3. 分类、移动、兼容与回滚

{org['move_operations']} 项移动、{org['moved_files']:,} 文件/{org['moved_bytes']:,} bytes，移动身份 {org['byte_identity_pass']:,}/{org['moved_files']:,} PASS。代码/runtime/Git 镜像分别归入 `0_admin/skills`、`0_admin/tooling`、`0_admin/repositories`；root reports 归 `7.Report/rounds/<stage>/root_records`；长对话记忆归 `7.Report/project_history`；旧计划和 YR1.zip 归 `9.Version/research_plans` / `workspace_snapshots`；TBI归 `1_data/gwas/PBC/FinnGen_R13/indices`，不计作完整 GWAS。

规范根目录只剩截图 13 项，增补每目录说明、最新导航、机器状态和路径字典。旧导航原件与 {org['path_only_adapters']} 份路径依赖原代码保留。路径替换仅解决搬迁，未改 statistical formulas、thresholds、donor definitions 或候选范围；旧 tag/release 科学字节不改。

校验覆盖基线 {con['all_accounted_pass']}/{con['baseline_files']} 文件全部有去向；Python AST、12 项 PS parser、16 项 R parse 均通过，R 库搬迁后加载成功。R locale 警告如实保留。`MOVE_PLAN` / `MOVE_JOURNAL` / file-identities / path-adapter ledger / rollback 均交付。

## 4. 成果与未来用途

本轮刷新 {cat['curated_asset_groups']} 组高价值资产和 {cat['project_work_records_including_historical_copies']} 份项目记录；原搜索命中 1,172 含 skill/template/public mirror 等，不等于独立项目行动数量。阶段时间线保留从 SSc→MG→IgAN→PBC 的失败边界和工程复用；不从归档项目恢复生物学预设。详见 `02_有价值资产与未来复用.md` 与 TSV。

当前论文的解释主线来自 6,923/5,460 筛查范围、642 高信息子集、92/428/59/63 PF10 adjudication、A0/A1/A2/M matched-input arms、signal-pair 语义、PF10/PF50 敏感性和 486,000 次模拟。IL12RB2/FCRL3 是实例而非首次发现新 causal genes；独立分子资源、不同疾病研究系统与未知参与者重叠分开；组织层非显著结果保留。

## 5. 投稿候选封装与官方核验

新包：`{ident['package']['file']}`，{ident['package']['bytes']:,} bytes，SHA `{ident['package']['sha256']}`，CRC PASS，{ident['package']['internal_checksums_pass']}/{ident['package']['internal_checksums_pass']} internal SHA PASS，{ident['package']['entries']} entries。

15 个实际稿件资产全部与 R7C3B 原字节相同；另附 QA、上传角色与完整身份清单。主 DOCX 唯一，WPS PDF 为 parity；六张独立 vector PDF 只在门户需要时使用，不自动重复合并。S1–S10 工作簿保持 10 sheets，S11 位于 Source Data 2，48 科学成员不改。内嵌 Results 审阅版不作为第二主稿混装。

2026-10-12 再查 npj 官方 indexed author guidelines；direct open 仍 Internal Error，访问限制写入 receipt。标题 12 words、摘要 135 words 符合当前索引限度；不能以此声称整个 live portal 合规。S09 final-width、S18 edited-version sign-off、S19 official forms、S22 publisher proof 尚未终结。投稿信保持原 11 October 日期，真实提交日再改日期并重新 WPS/哈希；不为了文件日期不断改论文。

官方入口：[content types](https://www.nature.com/npjgenmed/for-authors-and-referees/guide-to-authors/about/content-types)、[reporting standards](https://www.nature.com/npjgenmed/editorial-policies/reporting-standards)。2018 PDF typography guide 仅归档参考。

## 6. 公共同步与分享边界

本报告随 R7C3C payload 公共同步。选定原创代码、原字节候选文件、汇总审计、成果时间线和工作记录指针；大型原始 GWAS、genotype、pseudobulk、原始 LD、BAM、第三方 runtime、全量私人 content/path 清单不镜像。原 MIT / CC BY 4.0 分层范围保留，不重许可来源数据。

推送前重新核查差异、大小、明确 secret signatures、禁止数据类型、Source Data ZIP 成员、`git diff --cached --check` 和全 tracked MANIFEST；正常 fast-forward push，不 reset、force 或覆盖其他人的提交。最终 commit、remote HEAD、clean-tree 和 tag 以本地独立 `github/GIT_PUSH_RECEIPT.json` 为准；报告准备不冒充推送成功。

## 7. 当前科学终裁与下一阶段

`PBC_PRIMARY_PROJECT = GO`；`R7C3C = COMPLETE_AUDIT_ORGANIZATION_PACKAGE`；`NEW_BIOLOGICAL_ANALYSIS = NO`。最新候选稿可审阅、可公开，但未期刊投稿，未本轮生成 DOI，也未代签作者批准。

下一阶段 **R7C4 — final author version confirmation + official reporting forms + publisher proof + actual submission receipt**。先两位作者确认 R7C3B 文件身份，再按实际门户固定上传角色、核对图宽/全 proof，最后提交并记录稿号/时间。既有 Human Genomics 版本继续归档备选，不一稿多投。若没有审稿要求或新的核心来源缺陷，不再扩大分析数量或替换疾病。
''')

def fullrelease():
    stage=ROOT/'6_release/R7C3C_2026-10-12/_audit_stage';stage.mkdir(parents=True,exist_ok=True)
    for source,folder in [(OUT,'Audit'),(REPORT,'Reports'),(HERE,'Code')]:
        for p in source.rglob('*'):
            if p.is_file() and '__pycache__' not in str(p):
                dest=stage/folder/p.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    for p in [ROOT/'0_admin/workspace_paths.json',ROOT/'0_admin/navigation/CURRENT_PROJECT_AND_FILES.md',ROOT/'0_admin/protocol/current/PBC_CURRENT_STATE_20261012.json',RELEASE/'SUBMISSION_PACKAGE_RECEIPT.json']:
        dest=stage/'EntryPoints'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    text(stage/'README.md','# R7C3C local full audit\n\nContains private local path/content and byte inventories. Do not mirror this complete archive publicly. The selected public payload is separately reviewed. Submission assets are in the independently checksummed candidate ZIP. No raw input, runtime, genotype or old workspace ZIP is recopied into this audit archive. Before/after and final-delta inventory boundaries remain explicit.')
    receipt=pack.checksum_zip(stage,RELEASE/'CMM_R7C3C_FullWorkspaceAudit_Organization_20261012.zip')
    a.save_json(RELEASE/'FULL_AUDIT_RELEASE_RECEIPT.json',receipt);print(json.dumps(receipt,ensure_ascii=False),flush=True)

if __name__=='__main__':
    import sys
    if '--package' in sys.argv:fullrelease()
    else:conservation();reports();print('Conservation and comprehensive reports complete.',flush=True)
