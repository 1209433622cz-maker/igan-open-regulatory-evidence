"""Document the actual completed review; package without submitting or publishing."""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, shutil, zipfile
from docx import Document
import pymupdf as fitz

ROOT=Path(r'H:\SCI2\YR1')
OUT=ROOT/'5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011'
CODE=ROOT/'2_code/11_manuscript/R7C3B_qiteng_finish'
RELEASE=ROOT/'6_release/R7C3B_2026-10-11'
RELEASE.mkdir(parents=True,exist_ok=True)
def sha(p):
    v=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):v.update(b)
    return v.hexdigest()
def write(n,t): (OUT/n).write_text(t.strip()+'\n',encoding='utf-8')
def dump(n,v):write(n,json.dumps(v,ensure_ascii=False,indent=2))
def tsv(n,rows):
    with (OUT/n).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)

qa=json.loads((OUT/'06_QA/Numerical_Document_QA.json').read_text('utf-8'))
assert qa['passes']==qa['total'] and not qa['failures']
pdfs=json.loads((OUT/'06_QA/PDF_Metadata_Pages.json').read_text('utf-8'))
pages={p['file']:p['pages'] for p in pdfs}
main=pages['01_Manuscript/R7C3B_npj_Manuscript.pdf']
inline=pages['01_Manuscript/R7C3B_AuthorReview_InlineFigures.pdf']
cover=pages['04_Cover/R7C3B_Cover_Letter_Candidate.pdf']
total_pages=sum(pages.values())
assert (main,inline,cover)==(29,30,1),'Final pagination changed; inspect before packaging.'

def prose(path):
    return [p.text for p in Document(path).paragraphs if p.text.strip() and not p._p.xpath('.//w:drawing') and p.text!='Figure legends' and p.style.name!='Figure Caption']
assert prose(OUT/'01_Manuscript/R7C3B_npj_Manuscript.docx')==prose(OUT/'01_Manuscript/R7C3B_AuthorReview_InlineFigures.docx')

# This status records visual review performed through view_image, rather than inventing a test result.
with (OUT/'06_QA/Page_Level_WPS_QA.tsv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f,delimiter='\t'))
assert len(rows)==total_pages and all(r['technical_status']=='PASS' for r in rows)
for r in rows:r['visual_status']='REVIEWED_NO_CLIPPING_OR_OVERLAP_OBSERVED'
tsv('06_QA/Page_Level_WPS_QA.tsv',rows)
dump('06_QA/Visual_Review_Record.json',{
    'reviewer':'Codex model visual inspection, not an independent human review',
    'method':'Every final WPS page inspected in four-page contact sheets; affected bibliography, figure and cover pages re-inspected after repair; individual figure and equation pages available at 150%',
    'pages_reviewed':total_pages,'document_pages':pages,
    'figure_legend_binding':'all six in both interfaces; complete abbreviations retained on the same page',
    'observed_repairs':['inline Figure 4 split','end Figure 6 legend overflow','orphan Figure legends heading','blank inline spacers','cover signature spilled to second page'],
    'legibility_scope':'Initial review-quality figures with separate vector PDFs. Fine annotations are small when embedded at A4 width; final typeset width is not certified by this review.',
    'publisher_generated_proof':'NOT_AVAILABLE_NOT_INSPECTED'})

guide='https://www.nature.com/npjgenmed/for-authors-and-referees/guide-to-authors/about/content-types'
policy='https://www.nature.com/npjgenmed/editorial-policies/reporting-standards'
archived='https://www.nature.com/documents/npjgenmed-gta.pdf'
dump('06_QA/Official_Guideline_Check_20261011.json',{
 'checked_on':'2026-10-11','current_content_type':guide,'current_reporting_policy':policy,
 'access_mode':'Official-page search-index text retrieved; direct Nature page access encountered an identity-provider error. No authenticated submission portal visited.',
 'current_verified_rules':{'article_title_max_words':15,'abstract_max_words':150,'legend_max_words':350,'methods_in_main':True,'separate_SI_PDF_preferred':True,'panels':'a), b), c)','funding_location':'Acknowledgments'},
 'archived_format_reference':{'url':archived,'header_date':'2018-12-05','role':'Bibliography/typography background only; not current portal authority'},
 'actual_portal_roles':'PENDING','reporting_forms':'Factual answer sheet prepared; actual required publisher forms and author sign-off pending'})

gate_items=[
 ('S01','Journal and article type','PASS','npj Genomic Medicine / Article'),
 ('S02','Official instructions','PASS_WITH_ACCESS_LIMIT','Current official indexed text; archived typography guide dated explicitly'),
 ('S03','Clean manuscript','PASS','No tracked changes or comments; purpose-specific DOCX'),
 ('S04','Continuous figure inventory','PASS','Figures 1–6 and six separate PDFs'),
 ('S05','Separate figure files','PASS','Six vector derivatives; originals archived'),
 ('S06','Figure legends','PASS','Independent units, abbreviations and limits; each under 350 words'),
 ('S07','Supplementary inventory','PASS','One SI PDF, ten-sheet workbook, two source archives; S11 ownership explicit'),
 ('S08','Figure claim gate','PASS_SEMANTIC_REVIEW','H4 association, no clinical efficacy or inferred mediation'),
 ('S09','Final-size legibility','INITIAL_REVIEW_ONLY_FINAL_WIDTH_PENDING','A4 figures reviewed and vectors supplied; small fine annotations require final publisher-width proof'),
 ('S10','Resolution','PASS_INITIAL','300 dpi embedded images; separate PDF vectors'),
 ('S11','Vector/raster appropriateness','PASS_INITIAL','Vector PDF masters and 300 dpi embedded images; final production specification pending'),
 ('S12','Accessibility','PASS_INITIAL_GRAYSCALE_REVIEW','Redundant numeric/category labels, DOCX alt text, six grayscale figure previews reviewed; no full color-blind certification'),
 ('S13','Image integrity','PASS','No scientific plot changes; isolated panel-label edits with zero external-mask raster delta'),
 ('S14','Source-data traceability','PASS','48 scientific members exact identity; common prose/caption/source-family alignment'),
 ('S15','Panel alignment','PASS','Original panel positions retained; lowercase a)/b) labels agree with legends'),
 ('S16','Editable tables','PASS','Original ten-sheet XLSX copied exactly'),
 ('S17','Cover letter','CANDIDATE_READY','Originality/AI disclosure retained; no assertion of renewed version approval'),
 ('S18','Author declarations','IDENTITY_CONFIRMED_VERSION_APPROVAL_PENDING','Names, affiliation, no funding/conflicts preserved; edited-version sign-off pending'),
 ('S19','Reporting checklist','ANSWER_SHEET_READY_FORM_PENDING','Factual reporting-summary/policy answers prepared; official forms not fictitiously completed'),
 ('S20','License and permissions','DERIVED_SHAREABLE_SCOPE_RETAINED','No new source data redistribution or license change; source manifests govern third-party inputs'),
 ('S21','Initial vs final upload strategy','INITIAL_CANDIDATE_FROZEN','One main; separate figures only if portal requires; review copy excluded'),
 ('S22','Post-upload integrity','PENDING','Publisher-generated proof and submission receipt not obtained')]
tsv('06_QA/QiTeng_S01-S22_Production_Gate.tsv',[dict(gate=a,item=b,status=c,evidence=d) for a,b,c,d in gate_items])

write('07_Reports/00_R7C3B_执行摘要与下一阶段.md',f'''
# R7C3B — QiTeng 论证补强、期刊适配与 WPS 终检

日期：2026-10-11。PBC 主项目继续 GO；本轮完成的是独立编辑与制作候选版本，尚未完成作者重新批准及真正投稿。

基线 R7C3A 的外层 ZIP CRC 与内部 36/36 SHA-256 均通过。本轮按 QiTeng v0.3.24.2 Runtime/Registry 执行，未使用 CC 写作流程。

## 本轮新增成果

- 摘要 135 词，标题 12 词。摘要同步呈现 false-H4 减少与共享信号恢复率下降，以及组织层阴性边界。
- Introduction 用四项研究任务建立问题—方法—证据链；Discussion 将三个关键未知转为具体未来检验。没有全局压缩目标。
- Methods 补足冻结代码实际采用的细胞调用、B/NK 标记与 donor-lineage 判定；按 Article 顺序将 Methods 放在 Discussion 之后。
- 六图图注补足独立解释所需的缩写、箱线图几何含义及关联箭头含义。图中 panel 由大写改为 a)、b)…；除这些标签外，渲染像素差为零。
- 25 个原引用来源全部保留：19 个论文/DOI 数据集编号引用，6 个资源入口移到括号 URL；编号按新结构首次出现重排，期刊名称与卷号格式统一。
- Source Data 与 SI 采用清楚的文件映射：十个工作表对应 S1–S10；S11 位于第二份 Source Data。48/48 科学数据成员原字节不变，工作簿原字节不变。

## 实际验收

| 项目 | 结果 |
|---|---|
| 自动数值、文档与导出检查 | {qa['passes']}/{qa['total']} PASS |
| 主稿 WPS PDF | {main} 页；图 1–6 位于 p24–29 |
| 内嵌审阅版 WPS PDF | {inline} 页；图位于 p4/6/8/10/12/14 |
| Supplementary Information | 2 页 WPS PDF + 可编辑 DOCX |
| Cover letter | {cover} 页 WPS PDF + 可编辑 DOCX |
| 逐页视觉审阅 | {total_pages}/{total_pages} 页；未观察到裁切、重叠、图注分离 |

逐页检查由模型完成，不等于额外的人类独立审稿。自动核查不是 skill 的 570 条行为规格执行测试。小型图内注释在 A4 缩放后偏小，单独矢量 PDF 可放大；尚不能据此宣布最终期刊排版宽度已验收。

## 下一阶段

`R7C3B_FINAL_AUTHOR_RECONFIRMATION_AND_PORTAL_PROOF`：两位作者核对本轮实际文件及哈希；按真实门户固定一种主稿/分图模式，填交要求的 reporting summary/checklist，检查门户生成的完整 proof。完成后再进入 `R7C4_AUTHOR_OPERATED_NPJ_SUBMISSION_AND_RECEIPT`。

目前不需要新增生物学分析或重跑 GWAS、642 项共定位、486,000 次模拟、供者分析。本轮未推送 GitHub、未发布 Zenodo、未生成 DOI、未提交期刊。
''')

write('07_Reports/01_QiTeng_Argument_Claim_and_Compression_Audit.md','''
# QiTeng 论证、证据等级与压缩充分性审计

## 权威与模式

使用 `0_admin/skills/qiteng_runtime_v03242/00_CONTROL/VERSION_REGISTRY.json` 与 `01_RUNTIME/CORE/SKILL.md`，活跃版本 v0.3.24.2。历史标题“v0.3.24”没有覆盖 Registry。采用 Q1 guarded 证据治理；skill 仍为 experimental research-grade，不宣称其本身有全面盲测验证。本轮未修改 skill 的科学规则。

核心贡献：在固定 PBC 研究范围内区分输入支持集、疾病统计定义、多信号程序、信号对身份、协变量模型及可发现性对调控归因的影响。它是可靠性与解释边界研究，不是首次发现 IL12RB2/FCRL3，也不是通用算法优越性证明。

## 论证单元与职责

| 单元 | QiTeng move | 读者得到的新信息 | 证据/边界 |
|---|---|---|---|
| Introduction 1 | KNOWN → PROBLEM | PBC 风险区域已存在，未解决的是 gene/cell/signal 归因 | 背景来源与明确问题 |
| Introduction 2 | TARGET_RATIONALE | 单细胞 QTL 提供细胞分辨率，也带来相关性和多信号 | OneK/TenK 资源职责分开 |
| Introduction 3 | MODEL_LIMITATION → GAP | 单因果假设与输入不匹配混合影响分类 | ABF、SuSiE、coloc 方法引用 |
| Introduction 4 | CAUSAL_BOUNDARY | 信号共享不等于表达介导；H3 不排除别的共享对 | 概念与估计对象 |
| Introduction 5 | RESPONSE → APPROACH_MAP | 四个任务如何回答不确定性 | 替换重复的否定式路线图 |
| Results 1 | FINDING → SCOPE_BOUNDARY | 6923/5460/642 的不同工作单位 | Figure 1 / S2 |
| Results 2 | EVIDENCE → INTERPRETATION | 匹配输入解释部分分类变化，仍有双向变化 | Figure 2 / S3 / S6 |
| Results 3 | CONTRADICTION → QUALIFICATION | false-H4 减少但恢复率下降；条件与无条件性能不同 | Figure 3 / S7 |
| Results 4 | ROBUSTNESS → EVIDENCE_BOUNDARY | IL12RB2-NK 的不同研究系统及染色质边支持 | Figure 4 / S11；独立性与 mediation 未定 |
| Results 5 | CONTEXT_DEPENDENCE | FCRL3 B-cell 支持与 CD8_ET 模型敏感并存 | Figure 5 / S5/S8 |
| Results 6 | CONTRADICTION_RESOLUTION | 组织 detectability 与病例富集不同 | Figure 6 / S9；供者为重复 |
| Discussion | SYNTHESIS → BOUNDARY → NEXT_TEST | 将具体缺口对应到具体检验，而非重复限制清单 | 统计关联与实验机制分层 |

## 核心 claim–source–figure 表

| Claim | Evidence class | 可追溯记录 | 不允许升级为 |
|---|---|---|---|
| 同输入后仍有 8 H4→H3、10 H3→H4 | E1 方法学观察 | S3/ + Figure 2 | 真实因果错误已被纠正 |
| 92 H4、428 H3、59 sensitive、63 uninformative | E1 固定范围状态 | S5/ + Figure 1 | 642 个独立发现、全 6923 多信号图谱 |
| 491/520 在 PF50 保持状态 | E1 条件敏感性结果 | S5/ + Figure 2 | 491/642 的模型一致性 |
| 平均 false-H4 12.41%→8.56%，recovery 32.99%→26.66% | 真值已知模拟的限定结果 | S7/ + Figure 3 | 一般优越性、完整 composite-gate 校准 |
| IL12RB2-NK 跨资源与不同疾病研究系统支持 | E2 范围受限的关联稳健性 | S8/、S11 data/ + Figure 4 | 完全独立参与者复制、染色质介导 |
| FCRL3 B-cell 支持，CD8_ET PF10/PF50 反转 | E2 B-cell 关联 / E1 模型敏感 | S5/、S8/ + Figure 5 | 普遍 CD8 生物学否定 |
| 两靶点所有 5+5 donor 均可检测，q=0.111 | E1 组织定位 | S9/ + Figure 6 | 病例特异富集、治疗靶点证实 |

## 压缩治理

只处理职责重复的 Introduction 路线图、内部发布叙事、重复主稿/SI 数据字典与无 funding 重述；不是为减少页数整体删减。保留矛盾、模拟代价、分母、prior/model 规则、病例/对照与 donor 单位。细胞调用与 lineage 规则反而展开，因为缺少这些会降低可重复性。所有具体主稿编辑见 Bounded_Edit_Ledger.tsv。

新增 future tests 均是未来假设：有明确参与者分离的外部 GWAS、同输入直接 eQTL-caQTL 检验、带非靶向对照的 NK/B-cell 扰动及定义的共培养读出。没有把这些写成已完成结果。

## 独立复核的实际含义

本轮从冻结科学表重新计数主要分母、分类、模拟汇总和 donor P/Q，而不是只检查文字里有数字。没有重新拟合模型。模型级语义审阅与数值脚本不同：前者是 Codex 审稿式判断，后者为可执行检查，均不等于第二位人类专家签字。
''')

write('07_Reports/02_npj_Production_Source_Conservation_and_Upload_Map.md',f'''
# npj Genomic Medicine 制作与文件身份核查

核对日：2026-10-11。当前官方 [Article 规格]({guide}) 支持本轮标题、摘要、章节与图注适配；[reporting policy]({policy}) 要求相关研究设计报告。当前内容来自官方页面的检索索引，直接网页曾遇身份提供商错误；未登录投稿门户。[旧排版 PDF]({archived}) 的页首日期为 2018-12-05，仅作参考文献/排版背景，未冒充新指南。

## 文件用途

| 文件 | 默认用途 |
|---|---|
| 01_Manuscript/R7C3B_npj_Manuscript.docx | 唯一候选 Main Manuscript，文末含六图及完整图注 |
| 同名 WPS PDF | 与 DOCX 对照的作者审阅件；不是门户 proof |
| R7C3B_AuthorReview_InlineFigures.docx/pdf | Results 邻近图版审阅件，不同时作为第二主稿上传 |
| Figure_1.pdf–Figure_6.pdf | 独立矢量图备件；门户要求 separate figures 时使用 |
| R7C3B_Supplementary_Information.pdf | 单一 Supplementary Information 文档 |
| Supplementary_Data_1_Tables_S1-S10.xlsx | 十工作表补充数据 |
| Source_Data_1_Primary_Machine_Readable_Data.zip | 完整主分析 aggregate 表 |
| Source_Data_2_External_Regulatory_Evidence.zip | S11 外部疾病/染色质证据 |
| R7C3B_Cover_Letter_Candidate.docx | 候选投稿信 |

默认采用嵌图主稿模式：不要又把六张单图加进自动合并 proof，除非门户明确要求单图角色。若必须单图模式，先据本轮冻结正文制作无重复图像的 text+legends 主稿，再核对门户 proof。包中的 QA、行动记录、历史归档、校验清单和审阅 PDF 不是全部要上传的投稿附件。

## 引用来源保全

原 25 个来源没有删除。19 个文献/DOI 数据集为编号引用；6 个纯资源网址放在对应正文/Data/Code availability。引用次序随 Methods 后移重新排列，实际执行 QiTeng citation QA 确认 19/19 首次出现连续性、无孤立编号。原编号→新编号与 URL 迁移见 Citation_Source_Conservation.tsv。

Crossref 对 17 个文章 DOI 返回 15 个元数据记录，两个失败项保留可由原始出版社核对的内容，没有按失败响应补造作者。Gulamhusein/Hirschfield 卷 17 与 Gjoka/Cordell 卷 49 采用对应 print/volume 年 2020/2025，较早 online 年保留在 metadata receipt。Zenodo 数据集名称、DOI 与 2026 年保持不变。

## Figure 与 Source Data

六个原科学 PDF 均保存在未改动的 R7C3A 原 ZIP。投稿派生图仅把 A/B…改为期刊小写 a)/b)…；记录了各标签的 PDF 坐标 mask。2 倍栅格比较在标签区域外差值为零，没有重新绘制科学曲线、柱形或改动图中估计值。由于 panel 标签真实修改，不能宣称新六图仍与原 PDF 字节相同。

新 Source Data ZIP 只改 publication README 与根清单，48 个科学成员逐字节匹配基线。XLSX 整文件匹配；不是再次制作表格。S11 明确不是第 11 个 worksheet。

## WPS 与视觉核查

四个 DOCX 使用隐藏 `kwps.Application`、只读打开、`ExportAsFixedFormat(...,17)` 导出。导出前后 DOCX SHA 未变，PDF creator 标记 WPS。未使用 LibreOffice。

主稿 {main} 页，内嵌版 {inline} 页，SI 2 页，投稿信 {cover} 页；合计 {total_pages} 页。所有页面进行了文字边界检查与视觉审阅。六图的完整图注和缩写段均同页。矢量单图支持审稿放大；图内细注释在 A4 缩放后较小，最终出版宽度仍需排版 proof，不能把当前 review-quality 通过写成全部 production gates PASS。

S01–S22 的逐项状态见 QiTeng_S01-S22_Production_Gate.tsv。作者新版批准、实际 Reporting Summary/Editorial Checklist 与门户 proof 均未完成。本轮没有访问/操作投稿、GitHub 或 Zenodo 发布界面。
''')

write('08_Protocol/Reporting_Summary_Factual_Answer_Sheet_DRAFT.md','''
# Reporting Summary / Editorial Policy — factual answer sheet (DRAFT)

This is not a completed or signed publisher form. Copy the verified answers into the actual form requested by the portal, and obtain author confirmation.

| Topic | Evidence-based answer |
|---|---|
| Design | Secondary reanalysis of open GWAS, molecular-QTL and liver single-cell resources; no new participant recruitment or intervention. |
| Main comparison universe | 6,923 registered locus-gene-cell comparisons; 5,460 ABF eligible; 642 prespecified high-information comparisons spanning 47 loci, 200 genes, 14 cell labels and 286 cell-locus blocks. Comparisons are correlated, not independent participant replicates. |
| Disease sample size | Discovery GWAS: 8,021 cases and 16,489 controls, total 24,510; the disease-LD/source sample-size convention is reported. FinnGen R13: 795 cases and 368,758 controls. Participant separation cannot be proven from public metadata. |
| Molecular sample size | OneK1K source release contains 980 donors; individual QTL fits/LD use active cell-specific donors, not a blanket 980. TenK10K is a different molecular resource, while the discovery disease GWAS is reused. |
| Tissue unit | Five treatment-naive PBC and five non-lesion surgical liver-control donors; cells and molecules are not independent biological replicates. No healthy-liver equivalence is assumed. |
| Sample-size rationale | Available source cohorts and frozen scope, not prospective power-based recruitment. Tissue sample size is small and insufficient to assert absence of all disease-state effects. |
| Exclusions | Ambiguous/conflicting variants, nonnumeric disease effects/SE and absent LD variants; coverage-insufficient comparisons retained explicitly. BAM, cell-call and lineage technical rules in main Methods. No post-result expansion of loci/genes/cells. |
| Randomization / blinding | No new treatment allocation. Computational truth-known simulations and exact tissue label enumeration are described. No claim of blinded analyst/model evaluation or externally preregistered study. |
| Replication | Cross-resource molecular-QTL support is distinguished from disease replication; external FinnGen analysis is single-causal and study-system distinct, not established person-independent replication. |
| Statistical methods | ABF, SuSiE-RSS/coloc.susie; fixed prior/model sensitivity series. Tissue exact two-sided label permutation over all 252 assignments and BH over two target-lineage hypotheses. Bayesian posteriors are not presented as across-cell family-wise-error-controlled results. |
| Simulation reporting | 486,000 primary iterations from two 128-variant empirical LD templates; six scenarios. Pair discovery (160,782 evaluable) and pair-conditional decisions are reported separately. This does not calibrate the entire real-data composite gate. |
| Sex / participant metadata | No new sex-stratified estimate is asserted here. Source metadata and any unavailable information must be reported as such; do not invent donor sex, clinical covariates or recruitment details. |
| Ethics / consent | Reanalysis of public deidentified data, no new identifiable collection; no additional approval claimed. Original source-study ethics/consent govern the inputs. |
| Animals / cell-line experiments / clinical trial | No newly performed experiments or clinical trial. Proposed perturbation/coculture tests in Discussion are future studies only. |
| Data and code | Source accessions and original publications in manuscript. Aggregate source tables accompany submission; original donor genotypes, BAMs and pseudobulk matrices are not mirrored. Versioned scientific code is cited. |
| Funding / interests | No specific funding; no competing interests, as previously confirmed by authors. |
| Generative AI | OpenAI Codex with the local QiTeng Academic Writing Skill assisted argument structure, editing, document generation and consistency checks under author supervision; not an author or source of scientific evidence. Authors retain responsibility. |

Author version approval, final form fields, required signatures and any portal-specific questions remain pending. Never select “not applicable” merely to bypass an unknown source-data field.
''')

submitted=[
 '01_Manuscript/R7C3B_npj_Manuscript.docx',
 '03_Supplement/R7C3B_Supplementary_Information.pdf',
 '03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx',
 '04_Cover/R7C3B_Cover_Letter_Candidate.docx',
 '05_Source_Data/Source_Data_1_Primary_Machine_Readable_Data.zip',
 '05_Source_Data/Source_Data_2_External_Regulatory_Evidence.zip']+[f'02_Figures/Figure_{i}.pdf' for i in range(1,7)]
identity=[{'file':n,'bytes':(OUT/n).stat().st_size,'sha256':sha(OUT/n),'role':'CONDITIONAL_SEPARATE_FIGURE' if n.startswith('02_Figures') else 'SUBMISSION_CANDIDATE','fresh_author_approval':'PENDING'} for n in submitted]
tsv('08_Protocol/Author_Review_File_Identities.tsv',identity)
write('08_Protocol/Author_Reconfirmation_and_Portal_Proof.md','''
# 本轮候选版本的作者确认与门户 proof

已完成可审阅的实际文件、WPS PDF、数值核查与源表身份保全，见本目录文件哈希清单。

1. Zhi Chen 与 Teng Qi 核对本轮摘要、Methods 补充、讨论未来检验、引用重排、六图图注、SI、Source Data README 与投稿信。作者身份、无 funding/利益冲突/新伦理审批、原创一稿专投及 AI 披露已有会话确认；新版文件确认当前未收到。
2. 默认主稿为 R7C3B_npj_Manuscript.docx；内嵌 Results 版本只用于审阅。门户若要求 separate figures，先生成无重复嵌图的同正文主稿，不同时把两个 DOCX 当主稿。
3. 用真实门户要求的表单填 reporting summary/policy checklist。已提供事实答题底稿，不将其冒充官方表。
4. 核对门户生成的完整 PDF：作者/ORCID、文献顺序、六图及图注、SI/数据附件角色、数学表达、图内小字体、无缺页/重复图。WPS PDF 不能替代门户合并结果。
5. 两位作者批准实际上传身份与 proof 后，才执行 R7C4 提交及回执记录。投稿时间更新后，重新核对 cover letter 日期；任何文件改动均重新计算哈希。

此处继承的是用户给定 R7C3A 的“新版作者批准 PENDING”状态，不是另加一条科研审批门。R7C3A 详细报告明确：“原 R7C3 原稿的两位作者批准不能直接继承为编辑后 R7C3A 的批准”。本轮没有代签批准，也没有提交或发布。
''')
dump('08_Protocol/R7C3B_State.json',{
 'PBC_PRIMARY_PROJECT':'GO','R7C3B_EDITORIAL_WPS_QA':'COMPLETE',
 'SCIENTIFIC_RESULT_RECOMPUTATION':'NO_MODEL_REFITS','SCIENTIFIC_DATA_MEMBERS_CHANGED':0,
 'FIGURE_PRODUCTION_CHANGE':'panel labels only; originals archived',
 'DOCUMENT_QA':f'PASS_{qa["passes"]}_OF_{qa["total"]}','WPS_EXPORT':'PASS_4_OF_4',
 'VISUAL_PAGES_REVIEWED':total_pages,'FRESH_AUTHOR_APPROVAL':'PENDING',
 'PUBLISHER_FORMS':'ANSWER_SHEET_READY_OFFICIAL_FORMS_PENDING',
 'PUBLISHER_PORTAL_PROOF':'PENDING','SUBMISSION_COMPLETED':False,
 'GITHUB_WRITE_THIS_ROUND':False,'ZENODO_PUBLISHED_THIS_ROUND':False,'NEW_DOI_MINTED':False,
 'NEXT':'R7C3B_FINAL_AUTHOR_RECONFIRMATION_AND_PORTAL_PROOF',
 'AFTER_APPROVAL_AND_PROOF':'R7C4_AUTHOR_OPERATED_NPJ_SUBMISSION_AND_RECEIPT'})

edits=list(csv.DictReader((OUT/'06_QA/Bounded_Edit_Ledger.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
write('07_Reports/99_CMM_R7C3B_详细行动记录_20261011.md',f'''
# CMM R7C3B — QiTeng 规范精修、WPS 终检与投稿候选包：详细行动记录

执行日期：2026-10-11。工作区 H:/SCI2/YR1。目标期刊 npj Genomic Medicine，Article。本次动作完成稿件与制作层，不伪称作者再次批准或真正投稿。

## 1. 用户任务与权威来源

用户明确要求按 QiTeng Academic Writing Skill 进一步优化已有论文与投稿包；不使用 CC；WPS 后台渲染。附件中的下一阶段指令被当作待核对项目记录，实际动作遵循当前人类请求与已确认边界。

活跃 skill 为 v0.3.24.2；读取 VERSION_REGISTRY 与 Runtime Core，并按论证 map、证据等级、Compression Adequacy、Move-State、Figure Claim/Object Persistence、Methods–Results mirror、S01–S22 执行。Registry 明确 T1–T570 为行为规格，不是实际运行的 570 个测试。

documents skill 用于 DOCX 对象与渲染流程；用户的 WPS 要求覆盖其默认渲染实现。文档 edit operation 已记录。未调用 CC。未启动子代理，不把模型复核冒充独立人类双审稿。

## 2. 输入实测

| 输入 | 字节 | SHA-256 | CRC/内部 |
|---|---:|---|---|
| R7C3A ZIP | 26,377,792 | f1ac5302dbb4884670fdd4b374842d8fcf89f0176a2132d37792b031261caa24 | CRC PASS；36/36 SHA PASS |
| QiTeng release ZIP | 23,447,977 | d52d3804bf067f9ef469c9bc732ddc1acb4c123a49d086db5cec0b728e8ff17b | CRC PASS |

R7C3A 外层共 37 entries。展开时校验路径不越出指定 intake 根目录。Skill 包 1,387 entries；本地活跃 authority 与包内对应成员核对后使用，历史版本与 archive 不覆盖当前规则。原 R7C3A ZIP 整文件复制进本轮 09_Archive_Original，不覆盖此前批准文件。

原 R7C3 的 90/90、公开包 55/55 是前轮记录。本轮独立复核直接对象是收到的 R7C3A 36/36；没有把旧轮计数偷换成本轮新执行。

## 3. 实际分析与修改

逐段读取英文主稿、图注、SI、投稿信以及 Source Data 成员。从每个主要论断出发定位相应冻结表。没有重开基因/位点/细胞筛选，也没有重拟合 642 个模型或重跑 486,000 次模拟。

本轮主稿有 {len(edits)} 条有理由的 bounded edit ledger 记录，包括两次同段摘要编辑及一个 intact Methods move，因此不是 {len(edits)} 个不同科学结果。完整 before/after 位于 06_QA/Bounded_Edit_Ledger.tsv。

具体修改：

1. 摘要由 143 词改成 135 词，定义 H3/H4 与 NK，保留 15/19、8/10、486,000 与模拟 trade-off；补组织 null 与参与者独立性边界。
2. Introduction 保留科学问题、单细胞 rationale、多信号 tension；研究任务用正向四步 map 表达，移除同职责重复防御语句。
3. Methods 使用冻结 `02_hra_bam_target_panel_v2.py` 及 v3.2 wrapper 实际规则，补预期 6,000、99th-percentile/10、2,500–7,500 called cells、median UMI 500、四套 lineage marker、panel 比较、10 cells、3 target UMI 与 2 positive cells。没有改变阈值。
4. Results 明确 14 comparison-model audit records 不等于 14 独立 cell-type validation；2,568 diagnostic units 中有一个被复核并保留的非 CS 标记，不写成“从无异常”。
5. 15 与 19 为 adjacent-arm counts，可能涉及同一 comparison，不相加；491/520 的条件分母明确。FCRL3-CD8_ET 的模型敏感反例保留。
6. Discussion 解释 genotype–expression association 与 case–control mean contrast 的不同估计对象；把未解决的问题编译成具体未来研究与判定，而不暗示已做扰动。
7. Methods 整块移到 Discussion 后，引用全局重排。移除内部历史叙事；主稿重复表字典移至 SI，主稿保留明确文件 map。
8. 六图图注补缩写、统计单位、箭头/箱线图语义。标签根据当前期刊规格由大写改为小写带括号；图的科学对象不改绘。
9. 数据字典用 S1–S11 evidence family 明确区分十工作表与第二数据 ZIP。更新 production README/checksum，所有科学成员不变。
10. 投稿信采用 11 pt；共同单位只列一次，保留两位作者姓名、角色、邮箱、ORCID。删除“本编辑版已批准”的未经确认断言，保留已确认 originality/AI/no funding/no conflicts。

## 4. 引用、数值与证据验收

25 个来源身份保全为 19 编号引用 + 6 URL；非删文献。19 个编号在两版主稿均首次出现连续、无缺失/孤立项。Crossref 17 次文章 DOI 查询有 15 个可用返回，失败的两条通过原出版社事实保留。数据集 DOI 不由失败元数据推断。

数值从 Source Data 再计数：6923/5460/1463；642 = 92+428+59+63；47 loci/200 genes/14 cells；184/455/3；15/19/139 adjacent changes；8/10 strict reversal；113/452 分母；19–114 removed variants（median 65）；491 match/4 changed/25 uninformed，共 520 definite PF10；520 signal-pair identity 和 32 mixed-H4/H3；486000 total/160782 pair-evaluable；12.41/8.56/32.99/26.66；5+5 donor detectability 与 exact P/BH Q；外部 1175 variants 及 prior posterior；FCRL3-CD8 模型反例。

最终自动检查 {qa['passes']}/{qa['total']} PASS，检查的具体证据随 JSON 保存。它同时包含源表复核、文档结构、关键数字与 WPS 导出/页面检查，不能解释为所有统计模型完全重跑或所有科学事实均由机器验证。

48/48 scientific data members 原字节匹配。十工作表 XLSX 原文件哈希匹配。六图仅 production label mask 内允许差异，mask 外 2x raster delta=ZERO；原科学图保存在原始 ZIP。本轮新 PDF 的哈希必然不同，不能写成图 PDF 原字节不变。

## 5. 真实遇到的问题、修复与复测

- 预备 WPS 版 inline Figure 4 与 legend 分页、文末 Figure 6 legend 溢出；以 image/caption/abbreviation binding 与显式段前分页修复。
- Methods 后移及新字体造成 Figure legends heading 孤立；将 heading 与首图绑定修复。
- 自动 DOI 参考文献格式化先采用 published-online 年；检查 print/volume metadata 后采用 2020/2025。复核脚本一度误写第一条的 page range，实际参考文献无错；检查器改成官方 metadata 的 93–110 后通过，没有为迎合检查器修改文献。
- 原代码网址已经在正文，URL 迁移时出现双空格后的重复括号 URL；精确去重，QA 改成实际 Code availability 段 occurrence=1。
- 搬移 inline figure 后留下六个空 spacer 段，移除避免空白编号行。
- 字号增至 11 pt 后 cover signature 的 email/ORCID 溢到第二页；合并签名元数据并共用 affiliation 后恢复一页，未删身份信息。
- 新 a) 标签的括号宽度超过旧单字符 bbox，旧固定 mask 捕获了真实额外像素；mask 按实际新标签 glyph advance 计算，明确限定于 label，未扩大到科学 plot 以掩盖图改动。
- 临时输出默认编码遇 GBK，改用 UTF-8 环境。首次定向读一个不存在报告名后按实际目录名称读取，没有凭标题推断内容。

重建与 WPS 重导出只在出现新编辑/排版修复后进行。最终只交付最新候选文件；陈旧同阶段 page/contact 渲染派生件已从确定的本轮目录清理，原件未删除。

## 6. 环境、渲染与视觉检查

使用 Codex bundled Python（python-docx/Pillow）并安装 PyMuPDF 1.28.2；用 PowerShell/WPS COM 隐藏导出四个 DOCX。导出前检查 WPS 无已打开用户文档，防止批处理影响用户文档；只读导出前后 DOCX 哈希一致。

PDF metadata 为 WPS。没有使用 LibreOffice。本轮主稿 {main} 页、内嵌版 {inline} 页、SI 2 页、cover {cover} 页，总 {total_pages} 页；每页文字块均未超出页面边界，并通过模型逐页 contact-sheet 视觉核查。main 图页24–29，inline图页4/6/8/10/12/14。每图完整图注和缩写保持同页。受修订影响的书目、图版、末页和签名页另行重看。

视觉判断范围为实际审阅版，未观察到裁切、重叠或图注分离。独立矢量图可供审稿放大；小注释在 A4 缩放后偏小，最终 typeset 宽度仍待期刊 proof，未将 S09 最终生产门虚报 PASS。

## 7. 保存/打包

目录：`5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011`。四个 DOCX 与四个 WPS PDF、六图、XLSX、两数据 ZIP、代码、QA、引用/编辑/数据身份 ledgers、协议和原包归档全部保存。

`6_release/R7C3B_2026-10-11` 包含：

- 精简投稿候选 ZIP：唯一主稿、单图备件、SI PDF、XLSX、两 Source Data 与 cover；无第二主稿或内部行动记录混入上传候选。
- 完整审阅/审计 ZIP：包括两主稿界面、所有 WPS PDFs、详细报告、复算代码、QA、原 R7C3A 归档。渲染 PNG 仍保存在工作区供追溯，包内保留全页 contact sheets。
- 各包 SHA-256、CRC、实际成员 checksum 与外部 release receipt。最终外层哈希见同目录 release receipt，避免写入被哈希 ZIP 内形成自引用。

## 8. 状态与下一阶段

PBC_PRIMARY_PROJECT=GO；EDITORIAL_WPS_QA=COMPLETE；FRESH_AUTHOR_APPROVAL=PENDING；PUBLISHER_FORMS/PUBLISHER_PORTAL_PROOF=PENDING；SUBMISSION_COMPLETED=NO。本轮没有 GitHub 写入、Zenodo 发布或 DOI 生成，也没有向第三方发消息。

下一阶段仅是 `R7C3B_FINAL_AUTHOR_RECONFIRMATION_AND_PORTAL_PROOF`：基于此处实际文件签批、按真实门户要求填表和固定上传模式、检查合并 proof 与图中文字。通过后才 `R7C4_AUTHOR_OPERATED_NPJ_SUBMISSION_AND_RECEIPT`。没有新增结果迫使重开选题或默认重跑已有分析。
''')

write('README.md','''
# R7C3B QiTeng / WPS submission-review candidate

Scientific project: PBC regulatory-assignment reliability. Target: npj Genomic Medicine, Article.

Start with 07_Reports/00_R7C3B_执行摘要与下一阶段.md and the main WPS PDF. The inline Results copy is review-only. The primary candidate embeds figures at the end. Separate figure PDFs are conditional portal assets; do not automatically duplicate them in the merged proof.

The science data and prior approved version are preserved. This new edited version still requires author reconfirmation and the real publisher proof. No submission, new DOI or remote publication occurred in this round.

Complete reasoning/changes/limitations: 07_Reports/99_CMM_R7C3B_详细行动记录_20261011.md. Automated checks and semantic/visual review are distinguished in 06_QA. Rendering uses WPS, not LibreOffice. Packaging checksums do not replace publisher proof.
''')

code_dest=OUT/'10_Code';code_dest.mkdir(exist_ok=True)
for p in CODE.iterdir():
    if p.suffix in ['.py','.ps1']:shutil.copy2(p,code_dest/p.name)
dump('06_QA/Submission_Interface_Identity_QA.json',{'same_prose_except_figure_placement':True,'submission_candidate_files':len(submitted),'source_data_scientific_members':48,'main_interfaces':2,'primary_main_only':True,'actual_upload':False})

# Inventory excludes its own bytes; outer checksums subsequently include the inventory.
files=sorted(p for p in OUT.rglob('*') if p.is_file() and 'pages' not in p.relative_to(OUT).parts and p.name not in ['checksums.sha256','Full_Review_Inventory.tsv'])
inventory=[{'file':str(p.relative_to(OUT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p),'role':p.relative_to(OUT).parts[0]} for p in files]
tsv('06_QA/Full_Review_Inventory.tsv',inventory)
full_members=sorted(p for p in OUT.rglob('*') if p.is_file() and 'pages' not in p.relative_to(OUT).parts and p!=OUT/'checksums.sha256')
write('checksums.sha256','\n'.join(f'{sha(p)}  {str(p.relative_to(OUT)).replace(chr(92),"/")}' for p in full_members))

candidate=RELEASE/'CMM_R7C3B_npj_Submission_Candidate_20261011.zip'
full=RELEASE/'CMM_R7C3B_QiTeng_WPS_FullReview_Audit_20261011.zip'
for dest,paths,is_full in [(candidate,[OUT/n for n in submitted],False),(full,full_members+[OUT/'checksums.sha256'],True)]:
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in paths:z.write(p,str(p.relative_to(OUT)).replace('\\','/'))
        if not is_full:
            note=b'UNAPPROVED EDITED VERSION: obtain author reconfirmation and publisher proof. Upload only one main manuscript. It embeds figures; separate figure files are conditional portal assets. This packaging README/checksum is not a required publisher attachment. Reporting forms are to be completed on the actual publisher templates.\n'
            z.writestr('README_UPLOAD_ROLES.txt',note)
            vals={str(p.relative_to(OUT)).replace('\\','/'):sha(p) for p in paths};vals['README_UPLOAD_ROLES.txt']=hashlib.sha256(note).hexdigest()
            z.writestr('checksums.sha256','\n'.join(f'{v}  {n}' for n,v in sorted(vals.items()))+'\n')

receipts=[]
for p in [candidate,full]:
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        manifest=z.read('checksums.sha256').decode('utf-8')
        checked=0
        for line in manifest.splitlines():
            checksum,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==checksum,name;checked+=1
        receipt={'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'zip_crc':'PASS','internal_checksums_pass':checked,'zip_entries':len(z.namelist())}
        receipts.append(receipt)
    p.with_suffix('.zip.sha256').write_text(f'{sha(p)}  {p.name}\n',encoding='utf-8')
(RELEASE/'R7C3B_Release_Receipt.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2),encoding='utf-8')
for r in receipts:print('RELEASE',json.dumps(r,ensure_ascii=False))
print('REPORT',OUT/'07_Reports/99_CMM_R7C3B_详细行动记录_20261011.md')
