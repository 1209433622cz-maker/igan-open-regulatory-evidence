"""Write the exact-file author handoff, metadata and local visual-review receipt."""
from pathlib import Path
import csv,hashlib,json,shutil,datetime
ROOT=Path(r'H:\SCI2\YR1')
OUT=ROOT/'5_manuscript/R7C3H1B_ExactVersionHandoff_20261013'
REPORT=ROOT/'7.Report/rounds/R7C3H1B_20261013'
REPORT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
qa=json.loads((OUT/'06_QA/MACHINE_QA.json').read_text(encoding='utf-8'))
assert qa['status']=='PASS' and qa['checks_passed']==43
with (OUT/'06_QA/UPLOAD_CANDIDATE_MANIFEST.tsv').open(encoding='utf-8-sig',newline='') as f:uploads=list(csv.DictReader(f,delimiter='\t'))
receipt=dict(status='PASS_LOCAL_VISUAL_REVIEW',reviewer='Codex visual inspection',
    inspected_pages=dict(Main=list(range(1,26)),Supplement=list(range(1,7)),Cover=[1]),total_pages=32,
    reviewed_items=['text clipping and overlap','headers and footers','figure legends on same page as their figure','native Word LD equations','links and scientific exponents','supplementary S1-S12 file map'],
    findings='No visible clipping, overlapping text, missing figure or truncated legend. Dedicated figure pages and the final supplement notice intentionally retain whitespace.',
    pdfs=[dict(role=role,relative=rel,sha256=sha(OUT/rel)) for role,rel in [('Main','01_Manuscript/Manuscript_SubmissionCandidate.pdf'),('Supplement','03_Supplement/Supplementary_Information_ExpertRebuilt.pdf'),('Cover','04_Cover/Cover_Letter_SubmissionCandidate.pdf')]],
    renderer='WPS background read-only export; PDF-to-PNG visual inspection',
    limitation='This is the local WPS proof, not a publisher-generated portal proof.',date='2026-10-13')
(OUT/'06_QA/VISUAL_REVIEW_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
qa['visual_review']='PASS_32_OF_32_LOCAL_WPS_PAGES'
(OUT/'06_QA/MACHINE_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
state=json.loads((OUT/'08_Protocol/HANDOFF_STATE.json').read_text(encoding='utf-8'))
state.update(status='COMPLETE_LOCAL_HANDOFF_AND_QA',research_plan='RP_v5',document_QA='PASS_43_OF_43',local_WPS_visual_QA='PASS_32_OF_32',
    candidate_upload_files=13,scientific_source_archives_changed=False,supplement_changes='Native notation only; workbook, crosswalk and all figure bytes unchanged',
    next='R7C3H1C_EXACT_AUTHOR_APPROVAL_AND_PUBLISHER_PORTAL_PROOF',github_candidate_publication='PENDING_SYNC')
(OUT/'08_Protocol/HANDOFF_STATE.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
meta=dict(journal='npj Genomic Medicine',article_type='Article',title='Input matched multisignal colocalization clarifies regulatory assignments at primary biliary cholangitis loci',
    authors=[dict(given_name='Zhi',family_name='Chen',email='zhichen1@link.cuhk.edu.cn',ORCID='0009-0001-0072-5576',order=1,corresponding=False),dict(given_name='Teng',family_name='Qi',email='tengqi@link.cuhk.edu.cn',ORCID='0009-0007-7648-4776',order=2,corresponding=True)],
    affiliation='School of Medicine, The Chinese University of Hong Kong, Shenzhen, Shenzhen, Guangdong, China',
    declarations=dict(identity_and_affiliation='Previously confirmed by user',funding='No specific funding',competing_interests='None declared',acknowledgements='No acknowledgement recipients',ethics='Secondary reanalysis of public de-identified data; no new recruitment or identifiable collection',originality_and_exclusive_submission='Previously confirmed by user',generative_AI='OpenAI Codex with QiTeng Academic Writing Skill, disclosed in Methods under author responsibility'),
    fresh_exact_file_approval='PENDING',portal_fields='Prepared; not entered or verified in journal portal',publisher_proof='NOT_GENERATED',journal_submission='NOT_EXECUTED')
(OUT/'08_Protocol/PORTAL_METADATA_PREPARED.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
rows='\n'.join(f"| {r['order']} | {r['portal_role']} | `{r['relative']}` | {int(r['bytes']):,} | `{r['sha256']}` |" for r in uploads)
guide=f'''# R7C3H1B 精确文件交接与作者审阅说明

本包是 RP v5 的必需交接任务产物。唯一主稿为 `01_Manuscript/Manuscript_SubmissionCandidate.docx`；同名 PDF 是 WPS 本地核对版，不作为第二份 Main Manuscript。当前状态是 **本地交接与 QA 完成、精确新版作者确认和出版社门户 proof 待完成**。

## 这次具体修改

FCRL3 TenK Results 交叉引用由 Figure 5b 改为 Figure 3d；真正的 FinnGen credible-set Figure 5b 引用保留。Data/Code availability 指向 R7C3H0 精确科学标签；Source Data 1–3 的职责写清。Figure 3d 来源图谱使用 pinned GitHub commit 的精确公开成员及 SHA-256。主稿 21 个指数、18 个支持集下标和两条既有 LD 定义改为原生 Word 格式；SI 的一个指数和两个支持集下标同步。所有数值和解释不变。

## 精确投稿候选清单

| 顺序 | 候选门户角色 | 包内文件 | Bytes | SHA-256 |
|---|---|---|---:|---|
{rows}

13 文件总大小 {sum(int(r['bytes']) for r in uploads):,} bytes。真正上传时应按门户可选类别映射；若 ZIP 被拒绝，可解包科学成员并保留其原哈希。不要把证据 ZIP 填进 Figure 槽位，不要上传第二份主稿。既有主稿末尾的六图可供阅读，另备六份矢量 PDF；如门户自动重复插图，应调整门户组装选择并重新生成 proof，不覆盖科学图件。

## 作者现在需要审阅的内容

请两位作者核对唯一主稿、SI、工作簿、六主图、三份 Source Data 和 cover 的实际内容及上表身份，确认是否同意将这套精确版本用于投稿。姓名、单位、ORCID、无资助、无利益冲突、原创新稿及一稿专投等此前确认的信息已继承，无需重复收集。此处只记录新版实际文件批准；目前没有代签作者表单或推断同意。

RP v5 第30章写明“待精确文件清单稳定后，由作者确认该清单并检查publisher PDF”；第38章的通过条件包括“作者确认精确新版、publisher PDF无缺页裁切或附件遗漏”。这一确认来自计划书的交接门，不是 QiTeng skill 的额外审批规则。

## 通过后下一阶段

1. 将作者批准与本清单 SHA-256 绑定，记录日期和批准范围。
2. 在 npj Genomic Medicine 门户核对 Article、两位作者、通讯信息、声明和附件类别。
3. 下载门户组装的完整 PDF；核对题名、作者、摘要、原生公式、Figure 1–6、图注、SI、表和 Source Data 附件列表。当地 WPS proof 不能替代此步骤。
4. 如发生任何内容变更，新增版本、更新清单并重新核对受影响内容。
5. 只有真实提交回执或 manuscript ID 到手，才标记 SUBMISSION_COMPLETED=YES。

## 当前科学边界

642 高信息比较不是全部 PBC comparisons 的多信号普查；8 H4→H3 与10 H3→H4 是重分类，非真值纠错率。模拟展示假共享下降与恢复率损失并存，不证明普遍方法优越性；完整跨 L/低先验组合门尚未直接校准。TenK 重用同一疾病 GWAS；FinnGen 参与者不重叠未知；直接 eQTL–caQTL posterior 缺失；肝组织仅支持可检出性，两目标 BH q≈0.111，不支持疾病特异富集。

## 文件夹职责

01 主稿与本地 WPS PDF；02 原样图件；03 SI 和工作簿；04 cover；05 三份源数据及一份公开 locator 复核表；06 机器 QA、图源映射、改动日志与身份清单；07 本轮报告；08 门控与 prepared metadata；09 生成和核查代码。06、07、08、09 是审计材料，默认不上传为论文附件。

当前科学来源：[R7C3H0](https://github.com/1209433622cz-maker/igan-open-regulatory-evidence/releases/tag/r7c3h0-statistical-reproducibility-closure-2026-10-13)。当前期刊格式核对参考：[官方 Article content types](https://www.nature.com/npjgenmed/for-authors-and-referees/guide-to-authors/about/content-types)。本轮使用官方索引核对；直接页面部分被登录重定向阻断，未声称已核对实际门户字段。
'''
(OUT/'START_HERE_精确版本审阅.md').write_text(guide,encoding='utf-8')
report=f'''# R7C3H1B 详细行动记录 20261013

## 1 本轮裁决

按 RP v5 正式推进 Exact Version Handoff and Author Proof 准备。本地交接包完成，PBC_PRIMARY_PROJECT=GO；科学基线保持 R7C3H / R7C3H0。本轮可交付精确文件、WPS 本地校样和独立身份 QA；精确新版作者批准、publisher portal proof、期刊投稿及 Zenodo DOI 均未自动宣称完成。

## 2 输入与权限边界

RP v5 包含58页计划书和完整证据索引；本轮根据第30/38章推进版本交接，未把历史文档中的操作建议当成新的人类授权。用户既有公开 GitHub 同步授权继续适用；作者身份与基本声明已确认。本轮不删除仓库、不改写旧标签、不重开 SSc/MG/IgAN，不新增 PBC gene/cell/locus。使用 QiTeng v0.3.24.2 Runtime Core 和 VERSION_REGISTRY 组织 claim/evidence/boundary；未使用 cc skill。源目录115个文件的 SHA-256 再核对均未变化。

## 3 实际执行和改动

主稿4个段落发生导航编辑：一处 FCRL3 Figure5b→3d、两处 code-tree 标签同步、一处 Data availability 增补精确科学 release 和三份 Source Data 职责。Figure3d 的34-row panel map 将本地 H 盘路径改为 pinned commit `4fb58180c23af48e337e9a14e4073d9071e44d16` 的公开成员；compact TenK 表 SHA-256 为 `150088385a300fa4fc596fd6db103cca13776c65e0ee770a747e58bd2652d479`。FinnGen 的真实 Figure5b 引用保留。

逐页检查进一步识别继承的 `10^` 与支持集下标纯文本记法。主稿21个指数、18个支持集下标改为原生 Word 格式；两条原 LD 定义改为 editable OMML 方程，矩阵投影和相关定义没有变化。SI 同步1个指数和2个下标。OOXML 非正文部件、样式、嵌入图像均保持；正文语义通过精确预期替换和方程结构身份检查。

27个图件文件逐字节一致；工作簿和历史panel crosswalk一致；三份Source Data ZIP逐字节一致，ZIP CRC通过、内部60/60 SHA-256通过。SI DOCX/PDF因原生记法与WPS重导出而改变，不能再称“所有SI字节不变”；其文字数值、图像、文件职责与科学解释不变。Cover DOCX/PDF原样继承。

## 4 机器检查与异常修复

最终43/43 PASS，包含原输入保持、段落语义、数学对象、图件/源表身份、作者声明、source archive checksum、upload唯一性以及PDF边界检查。最初检查器错误假设主稿必须包含第一作者 email、声明必须出现特定字面词、supplement应有5文件；实际是通讯 email在主稿、OpenAI Codex与无specific grant声明齐全、supplement原目录4文件。调整检查器以匹配已确认输入，不通过删除真实失败或改变科学内容取得PASS。随后原生排版及SI导出增加独立检查，最终43项为本轮实测结果，不是复制旧阶段QA数。

标题12词；摘要按含连接词和小数的token规则129词、空白分隔126词、保守字母数字分片148词。RP v5曾记150词，本轮用明示计数算法纠正交接元数据，摘要全文未改。六legend按同一算法分别115、118、146、159、154、121词；计数口径不同不能解释成重新压缩摘要或改动科学结果。门户实际计数仍需核对。

## 5 WPS 与视觉 QA

只读隐藏 `kwps.Application` 后台导出主稿和SI，DOCX前后SHA不变。主稿25页、SI6页、cover1页，32/32页实际打开审阅。确认边界、页码、作者行、公式、图版和图注；六主图位于第19–24页，各自图注同页。references结束及末尾Supplement说明的留白属于保留独立图页的结构。图PDF矢量源和科学图内容没有重新绘制。此检查是本地WPS proof，不是出版社生成的PDF proof。

## 6 唯一投稿候选清单

唯一主稿DOCX、六主图PDF、一份SI PDF、一份S1–S10工作簿、三Source Data ZIP和一份cover DOCX，共13文件、{sum(int(r['bytes']) for r in uploads):,} bytes。逐文件路径、大小、SHA在 `06_QA/UPLOAD_CANDIDATE_MANIFEST.tsv`；作者审阅说明包含完整表。PDF阅读版不作为第二份Main Manuscript。门户分类目前prepared未实际操作；ZIP支持及图件自动组装方式必须在真实门户验证。

## 7 当前论文成果与论断上限

6,923 registry /5,460 eligible；642高信息比较跨47loci、200genes、14cells、286blocks。PF10=92H4、428H3、59sensitive、63uninformative；92H4涉及27genes/19loci；32条H4记录共存distinct pair。匹配输入后的严格8 H4→H3和10 H3→H4支持双向重分类，不能称18真值纠错。PF50条件分母520，491相同/4变更/25uninformative。FCRL3-CD8_ET保留PF10/PF50反转而不宣称普遍CD8否定。

486,000模拟，160,782 pair-evaluable=33.08%；false sharing12.41→8.56%与recovery32.99→26.66%共同呈现。当前模拟是有限grid、single-configuration组件评价，未直接校准完整cross-L/low-prior门。外部IL12RB2跨疾病研究支持成立，但participation non-overlap未知、direct eQTL-caQTL posterior缺失、PBMC peak-gene link非NK特异介导。肝组织5vs5为donor单位、目标可检出但q≈0.111，不能写疾病富集。

源匹配N=24,510保持primary；Neff=21,584.38的33高风险比较/14loci/132fits stress test没有改变最终状态或164条疾病CS身份，不推广为所有样本量约定等价。公开工程资产足以做聚合复核，不等于当前全量raw BAM/genotype仍在库或已全流程重新拟合。

## 8 期刊与公开发布核查

按 npj Genomic Medicine /Article准备。官方索引支持≤15词标题、≤150词单段摘要、editable main、独立figure和单一SI PDF等格式职责；这里只做格式适配。直接访问部分Nature页面被登录重定向阻断，不伪造门户已确认：[官方内容类型](https://www.nature.com/npjgenmed/for-authors-and-referees/guide-to-authors/about/content-types)。现有科学release R7C3H0和精确tag已通过GitHub API核实。首次git ls-remote遇connection reset，使用API复核及后续实际push/remote identity，而非把网络失败当科研FAIL。

新候选与RPv5计划将作为独立目录同步公开仓库；远端实际commit、Actions和release结果通过发布后收据记录。GitHub release不等于期刊投稿、作者签名或Zenodo DOI。旧科学包和source tag保留，稿件可追溯它们。

## 9 成果复用与目录

继续复用source identities、model-matched LD、same-input A0/A1/A2/M、pair semantics、coverage/UNINFORMATIVE状态、有限prior敏感性、完整模拟channel和donor-level permutation，而不是迁移归档疾病的生物学预设。本轮改动日志和精确文件清单可用于reviewer revision和版本回溯。报告保存到7.Report；投稿资产到5_manuscript；代码到2_code；正式ZIP和发布收据到6_release，不移动历史结果。

## 10 下一阶段冻结

`R7C3H1C_EXACT_AUTHOR_APPROVAL_AND_PUBLISHER_PORTAL_PROOF`。先由两位作者确认本清单，再核对门户作者信息、声明、唯一稿件/附件角色与完整组装PDF；如数值、图源或附件身份不一致，返回具体修复点，不自动开启新基因或换题。只有真实回执可推进author-operated submission closure。可选完整composite-gate simulation、明确独立疾病GWAS和direct eQTL-caQTL升级仍单列未来gate，当前不强制启动。

## 11 本轮状态

```text
PBC_PRIMARY_PROJECT=GO
RESEARCH_PLAN=RP_v5
R7C3H1B=COMPLETE_LOCAL_HANDOFF_AND_QA
DOCUMENT_QA=43/43 PASS
LOCAL_WPS_VISUAL=32/32 PASS
SCIENTIFIC_RESULT_CHANGE=NO
FIGURE_BYTE_CHANGE=NO
FRESH_EXACT_FILE_AUTHOR_APPROVAL=PENDING
PUBLISHER_PORTAL_PROOF=PENDING
SUBMISSION_COMPLETED=NO
ZENODO_DOI=NOT_ESTABLISHED
NEXT=R7C3H1C_EXACT_AUTHOR_APPROVAL_AND_PUBLISHER_PORTAL_PROOF
```

所有PASS均注明范围；本地审阅与远端公开不是期刊录用证据。
'''
rp=REPORT/'99_R7C3H1B_详细行动记录_20261013.md';rp.write_text(report,encoding='utf-8')
shutil.copy2(rp,OUT/'07_Reports'/rp.name)
for p in (ROOT/'2_code/11_manuscript/R7C3H1B_20261013').glob('*'):
    if p.is_file():shutil.copy2(p,OUT/'09_Code'/p.name)
print(json.dumps(dict(local_status=state['status'],qa=43,visual_pages=32,files=13,report=str(rp))))
