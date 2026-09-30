# CMM R7A2A5 执行摘要：Human Genomics 投稿格式冻结

日期：2026-09-30
阶段：R7A2A5 — Target Journal and Submission Format

## 最终判定

```text
PBC_PRIMARY_PROJECT = GO
R7A2A4_INPUT = PASS_SHA256_AND_25_OF_25_INTERNAL_CHECKSUMS

PRIMARY_JOURNAL = Human Genomics
ARTICLE_TYPE = Research
COMPLETION_FIRST_BACKUP = BMC Medical Genomics
SECOND_BACKUP = Scientific Reports
ASPIRATIONAL_HOLD = Genes & Immunity

R7A2A5_MACHINE_QA = PASS_55_FAIL_0
WPS_PDF_RENDER = PASS
MANUSCRIPT_PAGES = 27
COVER_LETTER_PAGES = 1
SUPPLEMENT_WORKBOOK_SHEETS = 11

NEW_BIOLOGICAL_ANALYSIS_REQUIRED = NO
SUBMISSION_READY = NO
BLOCKER = VERIFIED_AUTHOR_AND_INSTITUTIONAL_METADATA

NEXT = R7A2A6_AUTHOR_METADATA_AND_FINAL_SUBMISSION_QA
GITHUB_LOCAL_RELEASE_COMMIT = PREPARED
GITHUB_REMOTE_SYNC = PENDING_NETWORK_RETRY
```

R7A2A5 已把 R7A2A4 的敌意审稿后稿件转换成可审阅的目标期刊资产。当前首选期刊为 **Human Genomics / Research**，因为其官方范围直接覆盖人类遗传流行病学、GWAS、统计与调控基因组学、单细胞及整合组学。稿件的贡献继续限定为 source-matched LD、多信号拆分、冻结比较全集、跨 molecular-QTL 资源复现和明确的阴性组织边界，不宣称新基因发现、表达介导、因果机制或治疗价值。

主稿已完成 Human Genomics 所需的结构化摘要、标准章节、缩略语表、完整 Declarations 子标题、独立图件、图形摘要和补充材料接口。参考文献已按首次出现顺序重新编号；该修正消除了 R7A2A4 主题分组编号直接进入 Vancouver 风格投稿的风险。

主稿 DOCX 使用 Times New Roman、双倍行距、连续行号和页码。WPS 后台导出的 27 页 PDF 已逐页审阅。投稿信经第一次渲染发现短第二页后，被压缩为一页并重新导出和复核。Supplementary Tables S1–S10 被组装为 11-sheet XLSX（含 Index），公式/错误扫描为 0 个错误。六张主图保持原像素和约 300 dpi，四张补充图为 300 dpi；920×300 图形摘要同时提供 PNG 与可编辑 SVG。

QiTeng Academic Writing Skill v0.3.24.2 是本轮唯一学术写作治理层，采用 QITENG_Q1 的证据—主张强度约束、矛盾保留、边界显式化和 late-stage focused patch 原则。没有使用 CC Review skill，也没有重新打开已冻结的生物学分析。

## 不能自动完成的项目

稿件保留了显式占位符，不能以当前状态提交。必须由作者提供并核实：作者顺序、单位映射、通讯信息、CRediT、Funding、Competing interests、伦理/本机构豁免口径、Acknowledgements、全体作者批准、AI 辅助披露确认，以及 APC/许可选择。

## 下一阶段

R7A2A6 只做作者元数据合并与最终投稿 QA。收到真实信息后，将同步更新主稿、投稿信、投稿系统字段和声明，重新运行引用、图件、DOCX、WPS PDF、补充材料和 checksum 全套门控。除非作者或编辑提出新的科学问题，否则不新增位点、细胞、QTL、组织队列或生物学分析。

公共仓库资产已在本地 clean commit 中完成，且 >10 MB 文件门、secret-pattern scan、`git diff --check` 和全仓库 manifest 均通过。当前设备到 `github.com:443` 的连接连续失败，因此本轮没有把本地 commit 虚报为远端同步成功；已提供 fail-closed 的 `SYNC_R7A2A5_TO_GITHUB.ps1`，网络恢复后可完成 fast-forward push 和 remote-HEAD 复核。
