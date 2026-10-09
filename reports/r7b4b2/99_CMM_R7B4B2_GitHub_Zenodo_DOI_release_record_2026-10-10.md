# 99_CMM_R7B4B2_GitHub_投稿包_Zenodo_DOI发布_详细行动记录_2026-10-10

## 1. 本轮任务与冻结边界

本轮按 PBC 研究计划书 RP v3、R7B4B 作者完成门与 QiTeng Academic Writing Skill v0.3.24.2 继续推进。作者已确认稿件、补充材料、图表、派生数据、投稿信、原创性、一稿专投、无并行审稿、生成式人工智能披露以及公开发布授权。本轮没有重新打开疾病、位点、基因、细胞、阈值、统计结果或图表数据。

目标是完成四项工程闭环：

1. 冻结许可证与第三方材料边界；
2. 重新推送公共 GitHub 仓库并创建版本化 Release；
3. 构建私有期刊投稿包与公开研究包；
4. 通过 Zenodo 预留并发布 DOI；若当前机器没有 Zenodo 身份凭据，则将凭据设定收敛为唯一外部阻塞，不接收或记录令牌明文。

## 2. 作者、单位与声明

作者顺序冻结为：

1. Zhi Chen（第一作者；ORCID 0009-0001-0072-5576）
2. Teng Qi（通讯作者；ORCID 0009-0007-7648-4776）

单位为 School of Medicine, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Boulevard, Longgang District, Shenzhen, Guangdong 518172, China。

声明已冻结：公开去标识数据的二次分析无需新增伦理审批；无利益冲突；无专项研究 funding；无致谢；两位作者批准最终版本；稿件原创且未在其他期刊审稿；生成式人工智能的受监督使用可以公开披露。私有邮箱、批准证据和投稿账户信息保留在本地私有记录，不进入 GitHub 或 Zenodo。

## 3. 许可证与再分发边界

- 原创代码与可执行工作流：MIT License。
- 原创稿件、图表、图形摘要、文档、协议、紧凑汇总结果和派生表格：Creative Commons Attribution 4.0 International（CC BY 4.0）。
- 第三方 GWAS、OneK1K/TenK10K、FinnGen、HRA008003、个体水平基因型、BAM、pseudobulk 矩阵和许可受限归档：不重新许可、不随公开包再分发，继续受来源方条款约束。

许可证文件为 `LICENSE`、`LICENSE_CONTENT.md` 与 `NOTICE.md`。Zenodo 记录层采用 CC BY 4.0；代码的 MIT 范围仍由仓库内许可证明确界定。

## 4. 投稿包与公开包

本地私有投稿包：

`local release directory / CMM_R7B4B2_HumanGenomics_SubmissionPackage_PRIVATE_2026-10-10.zip`

该包把 `UPLOAD_TO_HUMAN_GENOMICS` 与 `INTERNAL_DO_NOT_UPLOAD` 物理分开。前者包含稿件 DOCX/PDF、投稿信 DOCX/PDF、Figure 1–6、图形摘要和两个 Additional files；后者保存私有作者记录、WPS 回执和内部 QA，不得上传。

公开研究包：

`local release directory / PBC_R7B4B2_OpenResearchCompendium_2026-10-10.zip`

公开包含作者批准的稿件、Figure 1–6、图形摘要、Supplementary Tables S1–S10、机器可读派生数据、引用元数据和许可证。公开隐私扫描结果为 ZIP CRC PASS、第一作者私有邮箱 0 命中、私有记录标记 0 命中、绝对本地路径 0 命中。通讯作者的稿件公开联系邮箱属于正常出版元数据。

两套归档均生成内部 `MANIFEST.sha256`、外部 SHA-256 sidecar，并通过 ZIP CRC 检查。确切哈希记录在 `R7B4B2_package_receipt.json`，避免在后续重打包时沿用过期哈希。

## 5. WPS 与稿件 QA 继承

本轮没有重写或重渲染稿件。继续继承已经绑定到确切 DOCX 哈希的 WPS 后台渲染结果：主稿 30 页、投稿信 1 页，全部页面已完成视觉检查；未发现裁切、重叠、缺图、乱码或分页错误。最终投稿 QA 为 20 PASS、2 HOLD、0 FAIL。两个 HOLD 仅为院内期刊等级确认与作者本人操作期刊投稿系统，不影响 GitHub/Zenodo 开放发布。

## 6. GitHub 发布结果

公共仓库：

https://github.com/1209433622cz-maker/igan-open-regulatory-evidence

冻结标签：

`r7b4b2-author-approved-open-research-release-2026-10-10`

Release 地址：

https://github.com/1209433622cz-maker/igan-open-regulatory-evidence/releases/tag/r7b4b2-author-approved-open-research-release-2026-10-10

Release 只附加公开研究包及其 SHA-256 sidecar。私有投稿包、作者私有记录与 Zenodo token 不上传。

## 7. Zenodo 与 DOI 发布协议

Zenodo 元数据已冻结在 `.zenodo.json`，包括标题、两位作者、单位、ORCID、CC BY 4.0、publication/preprint 类型、版本 1.0.0、关键词与 GitHub 关联标识。

`publish_r7b4b2_to_zenodo.py` 严格使用 HTTPS Authorization header，从本机环境变量 `ZENODO_TOKEN` 读取令牌，不打印、不写盘。脚本先创建 deposition 并预留 DOI，上传公开 ZIP、SHA-256 sidecar 和 WPS 稿件 PDF，重新读取记录后才执行显式 `--publish`。令牌必须具备 `deposit:write` 与 `deposit:actions` 权限。

如果当前环境未设置令牌，脚本以 `ZENODO_AUTH_REQUIRED` 和退出码 20 停止，不会创建半成品记录。该状态是账户身份验证阻塞，不是科学、许可或文件 QA 阻塞。

## 8. 当前判定与下一阶段

```text
R7B4B2_SUBMISSION_PACKAGE = COMPLETE
PUBLIC_COMPENDIUM = COMPLETE
LICENSE_GATE = PASS
PUBLIC_PRIVACY_GATE = PASS
GITHUB_RELEASE = COMPLETE_VERIFIED
ZENODO_METADATA_AND_PUBLISHER = COMPLETE
ZENODO_DOI = PENDING_AUTHENTICATED_EXECUTION
JOURNAL_SUBMISSION = NOT_PERFORMED_AUTHOR_OPERATED
```

若 Zenodo 身份验证在本轮恢复，立即发布并把 DOI 回写至 `CITATION.cff`、README、出版状态 JSON 与 GitHub Release。若没有凭据，下一阶段被严格限定为 `R7B4B3_ZENODO_AUTHENTICATED_PUBLICATION_AND_DOI_BINDING`；完成 DOI 绑定后再由作者登录 Human Genomics 投稿系统，不新增生物学分析。


## GitHub remote verification

- `main` / `origin/main`: `16b4f30404694a4248921a1c02280bc594a43d74`
- annotated tag peeled commit: `16b4f30404694a4248921a1c02280bc594a43d74`
- Release: https://github.com/1209433622cz-maker/igan-open-regulatory-evidence/releases/tag/r7b4b2-author-approved-open-research-release-2026-10-10
- assets: public compendium ZIP and SHA-256 sidecar (2/2 uploaded)
- public ZIP SHA-256: `0bfe7e08e1fdea9d5cf7d5baa9dd6416804e3e28d29dc237c7d66386edaf87de`
- local private submission ZIP SHA-256: `2b0ee3cf1dd5a1b0f4cca43099072e77454ec65ec530f45bcc0a394ea523e1bd`
