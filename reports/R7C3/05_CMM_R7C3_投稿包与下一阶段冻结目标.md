# R7C3 投稿包与下一阶段冻结目标

## npj 投稿包

本轮从已通过 R7C2 科学、格式和 WPS QA 的精确字节构建最小提交目录，不改写稿件内容：

1. cover letter DOCX；
2. main manuscript DOCX；
3. Figures 1–6 PDF；
4. supplementary information PDF；
5. Supplementary Data 1 XLSX；
6. Source Data 1 ZIP；
7. Source Data 2 ZIP；
8. submission metadata、upload checklist、WPS receipt 与 SHA-256 manifest。

WPS 复核仍绑定于当前精确文件：31 页 manuscript、1 页 cover letter、2 页 supplementary guide，共 34 页；clipping、overlap、missing figure 均为 0。投稿包同时保留 PDF 便于作者最终视觉核对，但 submission system 按 upload map 选择 DOCX/PDF/XLSX/ZIP。

## 已满足

- 作者：Zhi Chen 第一作者；Teng Qi 通讯作者；
- 单位、邮箱和 ORCID 已写入；
- 原创且未在其他期刊审稿；
- 无 funding、无利益冲突、无致谢；
- 公共去标识二次分析的伦理边界已陈述；
- 生成式 AI 使用由作者批准并披露；
- 数据与代码可用性声明、license 与公共 GitHub 已准备；
- 图、补充表、source data 和投稿信均有精确哈希。

## 尚需作者在投稿系统执行

- 登录 npj Genomic Medicine submission system；
- 逐字段录入 author/affiliation/ORCID；
- 选择 Article，上传文件并核对 system-generated proof；
- 回答 preprint/public version、AI、funding、ethics、competing interests 与 concurrent submission 问题；
- 确认 APC/waiver/机构协议；
- 点击正式提交并保存 manuscript ID、时间、PDF proof 和 confirmation email。

这些步骤涉及作者账户、法律声明和投稿系统最终按钮，应由作者本人完成。当前无科学或文件阻塞。

## R7C4 冻结目标

```text
R7C4 = AUTHOR_OPERATED_NPJ_SUBMISSION_AND_RECEIPT

INPUT = exact R7C3 submission package hashes
NEW_BIOLOGICAL_ANALYSIS = NO
NEW_LOCUS_GENE_CELL = NO
MANUSCRIPT_TEXT_CHANGE = only if submission proof exposes a factual/format defect

PASS = manuscript ID + submitted timestamp + generated proof + confirmation receipt
DESK_REJECT = direct Human Genomics fallback
REVIEW_REQUEST = bounded response branch tied to explicit reviewer requests
```

下一阶段的目标是获得正式投稿回执，而不是继续扩大分析。Zenodo DOI 可在获得认证令牌后单独发布并回填；它不是 npj 投稿的先决条件。
