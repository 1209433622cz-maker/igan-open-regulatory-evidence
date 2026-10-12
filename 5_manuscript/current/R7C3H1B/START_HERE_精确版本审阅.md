# R7C3H1B 精确文件交接与作者审阅说明

本包是 RP v5 的必需交接任务产物。唯一主稿为 `01_Manuscript/Manuscript_SubmissionCandidate.docx`；同名 PDF 是 WPS 本地核对版，不作为第二份 Main Manuscript。当前状态是 **本地交接与 QA 完成、精确新版作者确认和出版社门户 proof 待完成**。

## 这次具体修改

FCRL3 TenK Results 交叉引用由 Figure 5b 改为 Figure 3d；真正的 FinnGen credible-set Figure 5b 引用保留。Data/Code availability 指向 R7C3H0 精确科学标签；Source Data 1–3 的职责写清。Figure 3d 来源图谱使用 pinned GitHub commit 的精确公开成员及 SHA-256。主稿 21 个指数、18 个支持集下标和两条既有 LD 定义改为原生 Word 格式；SI 的一个指数和两个支持集下标同步。所有数值和解释不变。

## 精确投稿候选清单

| 顺序 | 候选门户角色 | 包内文件 | Bytes | SHA-256 |
|---|---|---|---:|---|
| 1 | Main Manuscript | `01_Manuscript/Manuscript_SubmissionCandidate.docx` | 2,527,657 | `c67d3fec232989b779c2811e9261edb3f9a7b56587aa4cb005e197b80fc2d64f` |
| 2 | Figure 1 | `02_Figures/Figure_1.pdf` | 57,835 | `d55eb50c87c6350d3f76d64a4e4ee16efc840907770e447ff5700984262b4936` |
| 3 | Figure 2 | `02_Figures/Figure_2.pdf` | 53,655 | `cd79c7a04a6b99f4389908fcb510314f8a6ebd414d2d4d3992eec24c520c0552` |
| 4 | Figure 3 | `02_Figures/Figure_3.pdf` | 55,289 | `a0cf8a07c229aea3a6a9dd615e9986d8a06d316e51717123186c668d1cbf6aca` |
| 5 | Figure 4 | `02_Figures/Figure_4.pdf` | 53,253 | `b13e579d31e894e0e0fcf7c46e401209d98c43b5ba807bb906bb6bb3fa6bf397` |
| 6 | Figure 5 | `02_Figures/Figure_5.pdf` | 61,613 | `3261bd5c711786549cf9cdc769211ae884d754c954cf03e401dd2e24ce8ed0e7` |
| 7 | Figure 6 | `02_Figures/Figure_6.pdf` | 47,986 | `75612e13169531966993ee0dbe4028c9c75b1870383fab64cd82b7136c78d245` |
| 8 | Supplementary Information | `03_Supplement/Supplementary_Information_ExpertRebuilt.pdf` | 707,356 | `f7c0e95898d3e3b2a3126084b646fd2ae082563ad607199dfaa1e0d86bdbdf35` |
| 9 | Supplementary Data 1 | `03_Supplement/Supplementary_Data_1_Tables_S1-S10.xlsx` | 3,282,142 | `7f53dfd60195b9903a52f638ba5ae6f8c7286adec9bcec0652bf1c27adf57382` |
| 10 | Source Data 1 | `05_Source_Data/Source_Data_1_Primary_Machine_Readable_Data.zip` | 3,246,464 | `9dd7c32dc6284c98c27b5f5af2382b29a2023feffa79e2482ed582efdc5ba38e` |
| 11 | Source Data 2 | `05_Source_Data/Source_Data_2_External_Regulatory_Evidence.zip` | 31,023 | `2eb3201a54be96049c810dc9680d6acf5bda6546cdfbd87393843afd2a984ac8` |
| 12 | Source Data 3 | `05_Source_Data/Source_Data_3_Disease_N_Robustness.zip` | 8,950 | `2ae49d12b594f68295ff9a2b16796348744cd1366371a41a3846c374e5fba15c` |
| 13 | Cover Letter | `04_Cover/Cover_Letter_SubmissionCandidate.docx` | 38,506 | `7dcd21aef56ac4a6614d1a7f00588d6fa883bae7c80a1729ece54e08501936f9` |

13 文件总大小 10,171,729 bytes。真正上传时应按门户可选类别映射；若 ZIP 被拒绝，可解包科学成员并保留其原哈希。不要把证据 ZIP 填进 Figure 槽位，不要上传第二份主稿。既有主稿末尾的六图可供阅读，另备六份矢量 PDF；如门户自动重复插图，应调整门户组装选择并重新生成 proof，不覆盖科学图件。

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
