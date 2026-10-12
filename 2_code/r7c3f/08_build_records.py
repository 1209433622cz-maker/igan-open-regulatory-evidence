"""Write source-bound action records and useful-asset guides before publication."""
from pathlib import Path
import csv,json,shutil,hashlib
ROOT=Path(r'H:\SCI2\YR1');AN=ROOT/'5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012'
PUB=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
REPORT=ROOT/'7.Report/rounds/R7C3F_20261012'
CODE=ROOT/'2_code/00_workspace_management/R7C3F_20261012'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def main():
    state=load(AN/'STATE_BEFORE.json');qa=load(AN/'QA_STATE.json');fmt=load(AN/'FULL_FORMAT_STATE.json');cur=load(AN/'CURATION_RECEIPT.json');backup=load(ROOT/'9.Version/github_rebuild/R7C3F_20261012/BACKUP_RECEIPT.json')
    top=list(csv.DictReader((AN/'TOP_LEVEL_TOTALS.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    table='\n'.join(f"| {r['folder']} | {int(r['files']):,} | {int(r['bytes']):,} | {int(r['bytes'])/1024**3:.6f} |" for r in top)
    matrix=[
      ('PBC frozen universe','3_results/04_integration/R7B1A; public results/r7b1a','6,923 registry / 5,460 eligible / 1,463 insufficient','Keep all denominators and non-trigger states','New unrelated discovery claims cannot reuse positive counts as independent discoveries'),
      ('642 source-matched follow-up','public results/r7b1b_v2; Source Data 1 S2/S3','47 loci / 200 genes / 14 cells / 286 blocks','Protocol-frozen symmetric H3/H4 reclassification','Not multi-signal coverage of all 6,923'),
      ('Matched input audit','public results/r7b2a','A0/A1/A2/M identities; 8 H4→H3 / 10 H3→H4','Variant/support and disease-statistic attribution','Real-data transitions are not known-truth error corrections'),
      ('Known-truth simulation','public results/r7b1c and results/r7b2a/simulation_audit','486,000; pair-evaluable 160,782','Discovery adequacy and inference-performance trade-off','Two LD templates / finite grid; no universal superiority'),
      ('LD and diagnostic engineering','1_data and 3_results source matrices; public QA summaries','Active donors; covariate-matched LD; kriging review','Variant/build/allele order and model identity','Donor-level matrices remain local; source contexts are not interchangeable'),
      ('External molecular and disease evidence','public results/r7c1/external_evidence','IL12RB2–NK; FCRL3–B; FinnGen and CASCADE ledgers','Signal direction, credible sets and evidence independence','Same discovery GWAS reuse / overlap unknown / no direct mediation posterior'),
      ('Donor tissue evidence','public results/r7a2a1; current Source Data','5 PBC + 5 controls; both q≈0.111','Donor-level exact tests and lineage detectability','Not disease-specific enrichment or whole-transcriptome reclustering'),
      ('Current submission assets','5_manuscript/R7C3F_SubmissionCandidate_20261012','21 unchanged content assets; 48 unchanged science members','Unique main DOCX and WPS parity; six vector PDFs / SI / XLSX / Source ZIP','Candidate, not journal receipt or new visual rendering'),
      ('Figure classification','4_figures/Fig1–Fig8; public figures/classified','46 images, stage annotations and source support','Retrieve by scientific job and historical version','Fig7 MG / Fig8 IgAN are historical; submission figures have separate authority'),
      ('Work records and decision trail','7.Report; public docs/WORK_RECORD_AND_CODE_INDEX.tsv','568 work-record/annotation entries; 389 code entries','Failure boundaries, frozen decisions and interfaces','Historical next/journal/counts are not current state'),
      ('54-paper writing-method corpus','8.Reference/literature/54_papers; docs/writing_methods','54 local PDFs; original synthesis and method matrix','Writing architecture, evidence ordering and reusable methods','PDFs not mirrored; historical JIF values not revalidated; missing per-paper reports not fabricated'),
      ('SSc / MG / IgAN archives','9.Version stage workspaces; historical reports and codes','SSc frozen / MG regulatory-main no-go / IgAN archive','P0/H6, access gates, variant identity, bounded failure and stop rules','No default biological salvage or renewed gene fishing'),
      ('Repository provenance','9.Version/github_rebuild/R7C3F_20261012','Old Git bundle, 8 tags, 5 releases / 10 assets / 5 SHA pairs','Recover original refs and exact source attribution','New repo and release IDs/timestamps differ after recreation'),
    ]
    with (AN/'VALUABLE_ASSETS_AND_REUSE.tsv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['asset','location','frozen_evidence','future_use','boundary']);w.writerows(matrix)
    summary=f'''# R7C3F 全量核查、GitHub 重建与投稿封装 — 执行摘要

日期：2026-10-12。主项目 PBC，RP v4；写作/成果说明依据 QiTeng v0.3.24.2。作者信息及既有公开发布授权沿用，不新增生物学筛选。

- 全量初始快照：{state['files']:,} 文件、{state['bytes']:,} 字节（{state['GiB']:.6f} GiB）；全部新鲜 SHA-256；读取错误 0，期间变化 0；14 个目录链接单列。
- 全面格式补查：272 ZIP/Office CRC PASS，4,324 小/中 GZIP 全解压 CRC PASS，60 NPY 头部/尺寸 PASS，3 PLINK BED magic PASS；9 大 GZIP 仅 full-byte SHA，未声称完整解压。
- 复用登记：957 代码/记录入口，其中 568 工作记录与注释入口、389 原创工作流代码入口；158 项去重的大输入身份只公开元数据；54 篇参考 PDF 保留本地。
- 21 个投稿内容资产和 48 个 Source Data 科学成员保持字节一致；本轮没有新 WPS 渲染、模型重拟合或出版社 proof。
- 公开发布前独立 QA：114/114 PASS；逐文件、嵌套 ZIP/Office、Python 语法、凭据特征、原始数据边界、README 路径及 1,529 历史 Git blob 检查。
- 旧仓库 full Git bundle、8 tags、5 releases 与 10 附件已备份，5 SHA 配对 PASS；后续删除/重建/远端推送的实际结果仅以 GITHUB_REBUILD_RECEIPT.json 和报告最终补记为准。

投稿候选包：`6_release/R7C3F_20261012/CMM_R7C3F_npj_Submission_Candidate_20261012.zip`。
科学判断：PBC 保留 GO；不是新因果基因/治疗机制或通用优越算法论文；优先完成 npj Genomic Medicine 的最终版本、官方表格及门户 proof/回执。
'''
    put(REPORT/'00_R7C3F_执行摘要_20261012.md',summary)
    report=f'''# R7C3F — GitHub 删除重建、全量文件核查、成果复用与投稿包行动记录

日期：2026-10-12；工作区 `H:\\SCI2\\YR1`。依据用户本轮明确指令：核查所有本地文件大小/内容、记录成果与工作记录、先删除旧对应 GitHub 仓库再创建公开库并推送、详细 README、制作投稿包、判断下一阶段。删除和公开发布授权直接来自用户；附带历史报告作为证据，不作为新的指令。

## 1. 当前科学与版本定位

PBC 是唯一当前主项目，研究计划 RP v4 双轨。科学 baseline 包括 R7B2A 同输入对照和 R7C0/R7C1 外部证据，编辑 baseline 是 R7C3B QiTeng/WPS。旧 SSc、MG、IgAN 生物学主线归档，不重新筛疾病、位点或细胞。R7C3D 图件分类与 R7C3E 十二目录整理已经完成，本轮承接其资产身份，保留十三个根目录和历史原件。

QiTeng active registry 为 v0.3.24.2；采用其证据层级、逻辑—证据—边界和输出目的规则撰写 README/总结。本轮未使用 CC 写作 skill。只重新封装已冻结 DOCX/PDF，不重写正文；所有 PDF 保留既有 WPS 后台导出或原 vector 图件。没有使用 LibreOffice，也没有把历史视觉 QA冒充本轮新逐页审稿。

## 2. 全量核查范围与文件总量

初始枚举冻结于任何大备份/公开 staging 生成之前：{state['files']:,} regular files、{state['bytes']:,} bytes、{state['GiB']:.9f} GiB，{state['directories']:,} directories。包括 `.git`、运行环境、历史快照、数据输入、结果、报告和当前稿件。所有 {state['fresh_full_sha256']:,} 文件重新读取完整原字节计算 SHA-256；无读取错误、无扫描期间变化。14 reparse/junction 记录但不递归，避免同一物理文件重复计数。仅自身 audit 输出目录排除，以避免递归自计数。本轮后续新 staging、备份、报告、Git 对象另行闭账清点，不混入初始快照分母。

| 根目录 | 初始文件数 | 初始字节 | GiB |
|---|---:|---:|---:|
{table}

完整私有清单：`5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012/ALL_FILES_FRESH_SHA256.tsv`。它记录大小、哈希、格式/内容检查状态、角色、历史阶段和公开处理边界。大文本读取上限和 raw binary header-only 限制明确标注；相同新鲜哈希对应的先前内容审计可以复用，不等于本轮重新逐字阅读或重跑每个科学模型。538 PDF 全页文本、71 DOCX 对象/文本、26 工作簿表单结构等沿用身份一致的内容索引。哈希 PASS 不能证明统计结论、版权或语义正确。

## 3. 全面格式与压缩完整性补查

另行对 initial snapshot 中全部 ZIP/Office 做 member-level CRC：272/272 PASS。4,324 <=64 MiB GZIP 做完整解压与尾部校验 PASS；9 >64 MiB GZIP 保持完整原字节 SHA 核查，没有做全文解压。60 NPY 使用版本匹配的公开 NumPy 头部 API，核对 dtype/shape/payload size，全部 PASS；3 BED 检查 SNP-major magic PASS。此处不宣称所有 genotype 的统计属性或第三方全数据内部语义经本轮重新验证。

首次 NPY 格式检查遇到 60 条 `numpy.lib.format._read_array_header` 私有 API 已移除异常；定位为检查器兼容性问题，改用 `read_array_header_1_0/2_0`，仅复核这 60 NPY，没有修改原 NPY。修复前状态保留在 attempts/。首次投稿 QA 的“不得有任何 Zenodo DOI”规则误判了合法第三方数据 DOI，改为“本轮稿件身份不变、没有新增项目 DOI”；保留来源引用。这两项是 QA 实现修复，不是新发现的科学数据错误。

## 4. 相同字节副本及内容复用

发现 {state['duplicate_groups']:,} 相同哈希组，涉及 {state['duplicate_members']:,} 文件；按每组保留一份计算的重复副本字节为 {state['duplicate_copy_bytes']:,}（约 {state['duplicate_copy_bytes']/1024**3:.3f} GiB）。这个数字不是可直接删除空间：包括版本档案、论文附件、冻结输入、发布包和运行环境。没有批量去重删除。保留逐项清单和用途判断，公开内容使用 SHA 映射复用已有相同文件。

科学/工程/记录资产矩阵位于 `VALUABLE_ASSETS_AND_REUSE.tsv`，公开说明 `docs/EVIDENCE_AND_REUSE.md`。公开复用索引有 957 行：568 工作记录或说明入口，389 原创可执行工作流入口；入口行数不等于独立轮次数，同一哈希和重复记录映射到已有公开副本。初始全工作区工作记录候选有 837 条，7.Report 中去除目录导航后有 417 种 MD 内容身份。历史状态与“NEXT”保留其当时语境，当前状态独立说明。

54 篇参考 PDF 继续留在六类方法文件夹。原创综合报告和写作范式矩阵加入公开文档；矩阵里的原 JIF 不是本轮实时核验结果。此前本地扫描未定位的逐篇 P01–P54 分析报告，保留“未定位”的事实，不补造，不推断永久丢失。

## 5. 当前成果的实质判断

1. **研究范围**：6,923 frozen registry，5,460 可筛查，1,463 coverage insufficient；642 high-information subset =184 primary +455 H3 rescue/falsification +3 borderline，覆盖 47 loci、200 genes、14 cells、286 blocks。不得把 subset 当作全 universe multi-signal census。
2. **多信号结果**：PF10 =92 H4、428 H3、59 model-sensitive、63 uninformative；92 比较涉及 27 genes/19 loci。32 H4 比较同时存在 qualifying H3 pair；区域不宜强制单标签机制。
3. **同输入方法对照**：support-set restriction 改变 15 states，disease-statistic matching 改变 19；两者可重叠，不简单相加。A2→M 有 8 H4→H3、10 H3→H4，属于真实数据重分类，不是已知真相的错误校正。
4. **模型敏感性**：520 definite PF10 中 PF50 491 一致、4 改变、25 uninformative。FCRL3/CD8_ET 作为敏感例保留，不隐藏反例。
5. **模拟**：486,000 primary iterations；160,782 pair-evaluable (33.08%)。false-sharing 12.41%→8.56%，shared recovery 32.99%→26.66%。有限 grid、两个 empirical LD templates 和 fixed N 不支持通用优越性声明。
6. **外部证据**：IL12RB2–NK、FCRL3–B 跨 molecular-QTL 资源支持；OneK/TenK 使用同一 discovery GWAS，因此不叫独立疾病复制。FinnGen R13 提供另一 disease-study system，但 individual overlap 未建立；疾病–eQTL/caQTL 加 peak–gene link 形成信号一致性，缺 direct eQTL–caQTL posterior，不等于 chromatin mediation。
7. **组织边界**：five PBC vs five non-lesion surgical controls；两轴两组皆 5/5 检出，两个 corrected q≈0.111。支持 lineage detectability，不支持疾病特异富集。

最有价值的是输入匹配和信号对层级解释如何改变调控归因，以及何时模型/发现能力/外部来源限制结论。当前无需重开全部 GWAS、642 fit、486,000 模拟或组织聚类。按 npj Genomic Medicine 当前路径继续候选投稿；不承诺期刊分区、接收概率或机制创新。

## 6. 公共仓库取舍、README 与可复现边界

使用旧 HEAD `{backup['old_head']}` 的 canonical Git blob 解出公共基线，避免 Windows CRLF 将冻结 manifest 误判。保留既有 analysis/results/protocols/manuscript 路径和旧科学标签引用。公开新目录增补当前代码、分类 Fig1–8、原创 54-paper synthesis/matrix、RP v4、工作记录与价值复用说明。

README 以 PBC 为主线，给出唯一稿件、图表/补充/Source Data 入口、科学问题、真实结果和分母、环境、分阶段复算说明、十三目录映射、历史定位、作者/许可/AI 披露及尚未完成投稿/DOI状态。旧 README 与 Data Availability 存为 history 原件，避免覆盖项目记忆。脚本保留 local ROOT/source assumptions，明确不是跨机器一条命令就能端到端重跑。

原始 GWAS/QTL bulk、donor genotype/covariates/pseudobulk/LD/BAM/RDS、vendor runtime、技能源码、完整 private file-content index 和第三方论文 PDF 不上传。158 个去重的大输入以 family、bytes、SHA 和获取说明公开；精确私有路径仍在本机。原 code MIT；原 text/figures/docs/aggregate results CC BY 4.0；第三方来源条件保留，公开可下载不自动等于允许再分发。

本轮更新 13 个既有 public code counterpart 的路径 adapter（12 Figure +1 source HTML），其科学表达和统计流程继承 R7C3D/E 的 AST/path-only 核验；其余本地原创代码按内容身份独立索引。完整 25 local Figure path changes 不被声称全部重新编写。新增 stage scripts 另行纳入 final public manifest。

## 7. 删除前旧仓库备份与授权

确切旧库：`1209433622cz-maker/igan-open-regulatory-evidence`，repository ID 1369613027。旧 main `{backup['old_head']}`。备份 full Git refs/objects、8 tags、5 Release JSON、10 asset files，5 ZIP/SHA 对 PASS。Git fsck 与 bundle verify PASS，bundle = {backup['bundle_bytes']:,} bytes，SHA `{backup['bundle_sha256']}`。issues/PR/hooks/rulesets 各 0；exported scope 不包括无法还原的订阅和身份时间戳。

用户明确要求删除后重建公开库，不重复索要删除决定。起初 CLI token 缺 `delete_repo`；两次实际 header 核对仍缺，用户要求帮助获取。由官方 `gh auth refresh -h github.com -s delete_repo` 启动 device flow，用户在官方页面完成授权；终端 Authentication complete，随后实际 OAuth headers 确认 delete_repo 生效。凭据或密码没有写入报告/仓库。

采用同一 owner/name/URL，避免稿件既有科学 tag 的代码链接失效；README 标题改为 PBC，历史 IgAN slug 的保留原因明确。旧仓库的 repository ID/created date 和 Release IDs 在重建后会变化，不把恢复旧 Git bytes 叫“同一个仓库未删”。计划恢复 old tags、archive/pre-rebuild branch 及五 Release 描述/资产。删除和新建的实际 HTTP/ID/HEAD/Release 闭环只由最终 receipt 和本记录附记确认，准备就绪不等于远端已经执行。

## 8. 投稿包实物与检验

新的 `5_manuscript/R7C3F_SubmissionCandidate_20261012` 含 21 个与原 R7C3C 完全相同的内容资产，另加 START_HERE、identity TSV、新 checksum manifest；共 24 个文件、23 个 internal checksum 项。原校验清单被重新生成，故不把所有原 22 文件都称“字节不变”。原六 Figure PDFs、主 DOCX/WPS PDF、SI、S1–S10、cover companions、Source Data 1/2 均 unchanged。48/48 Source scientific members 独立解出重新 SHA，PASS。

新的 candidate ZIP CRC PASS；sha `{cur['submission_zip_sha256']}`。它是候选包，不是投稿证明。独立生产 QA 初次修复后 114/114 PASS；公开准备树每个文件全部检核（{qa['public_files']:,} files；最大 {qa['public_largest_bytes']:,} bytes），所有 Python parse、ZIP/Office CRC、嵌套 raw/pattern credential 约束、README links 及 1,529 historical Git blobs credential scan PASS。后续记录/发布 receipts 会在 final manifest 再验，不把这一次分母套到增长后的树上。

唯一 main：`01_Main/Manuscript.docx`，文末六图；WPS PDF parity review，不自动重复上传为第二 main。独立 PDF figure 的使用以实际门户为准；若要求 figure-free main，需另做模式并进行身份/proof核验。SI editable与cover companion 是条件底稿。作者身份、无 funding/conflicts、原创性和 AI 披露沿用既有真实授权；不得代签官方表格。

官方 npj article guide 于本轮检索确认 editable manuscript、abstract up to 150 words、individual author contributions 要求；直接取页有限，门户实际流程尚未进入。来源：https://www.nature.com/npjgenmed/for-authors-and-referees/guide-to-authors/about/content-types 。旧 2018 PDF不作为当前门户权威。GitHub CLI deletion scope 来源：https://cli.github.com/manual/gh_repo_delete 。

## 9. 可复核文件与下一阶段

初始 full inventory、work records、duplicate hashes、大输入、本轮格式、公开 export/counterparts、独立 QA、备份 receipt、准备 guards、操作 checkpoint、最终 GitHub receipt 均分别保存。报告不是数据库唯一副本；对应脚本在 `2_code/00_workspace_management/R7C3F_20261012`。后续 closing snapshot 明确新增和变动边界。

固定下一阶段为 **R7C4 — 作者最终版本确认、实际 reporting forms、publisher merged PDF proof 和真实 submission receipt**。具体动作：确认这组 exact文件；填真实官方 forms；实际投稿当天修订 cover date；按门户明确唯一主稿模式；检查图件终尺寸和合并 proof；完成作者操作投稿并记录 manuscript number/time/receipt。未取得真实回执前 SUBMISSION_COMPLETED=false。Zenodo 项目 DOI 仍未验证发布，不用 GitHub tag或源数据 DOI冒充它。除非发现明确破坏核心结果的新缺陷，不再新增候选或重跑全部模型。

## 10. 最终执行补记

由远端发布完成后的 closing 工具追加真实执行状态、ID/HEAD/Release核验和全量新增清点。此初始记录不预写成功结果。
'''
    put(REPORT/'99_R7C3F_全量核查_GitHub重建_投稿包_详细行动记录_20261012.md',report)
    for p in REPORT.glob('*.md'):
        q=PUB/'reports/r7c3f'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    shutil.copy2(AN/'VALUABLE_ASSETS_AND_REUSE.tsv',PUB/'docs/R7C3F_VALUABLE_ASSETS_AND_REUSE.tsv')
    for name in ['QA_STATE.json','FULL_FORMAT_STATE.json','CURATION_RECEIPT.json']:
        obj=load(AN/name)
        # CURATION contains only relative public/path adapter names, no credentials.
        q=PUB/'audit/r7c3f'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for p in CODE.glob('*.py'):
        q=PUB/'analysis/r7c3f'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    for folder,purpose in [(AN,'全量文件核查、格式/重复内容、成果复用和 GitHub 执行收据；完整路径清单保持本地。'),(REPORT,'本轮行动、当前成果裁决和下一阶段；实际远端执行追加在99报告。'),(ROOT/'9.Version/github_rebuild/R7C3F_20261012','删除前旧库完整恢复材料；不要当作新的科学结果或自动重复推送。'),(ROOT/'6_release/R7C3F_20261012','本轮投稿候选 ZIP/SHA 与最终审计交付；候选不等于投稿回执。'),(CODE,'本轮可审查管理脚本；07删除重建仅对明确授权的旧 repository ID执行一次。')]:put(folder/'README.md',f'# R7C3F / 2026-10-12\n\n{purpose}\n')
    print('RECORDS_PREPARED',flush=True)
if __name__=='__main__':main()
