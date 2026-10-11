# CMM R4A9：作者数据请求草稿与 H6 运行交接

日期：2026-09-10

## 1. 当前最短路径

论文数据共享声明称 sex-specific meta-GWAS summary statistics 将通过 GWAS Catalog 发布，但截至本轮官方 API 中没有目标 PMID 的 accession。本轮没有代用户发送邮件。下面的草稿可由用户人工审核后发送给论文通讯作者。

论文公开的通讯地址：`m.acostaherrera@ipb.csic.es`。

## 2. 英文请求草稿

**Subject:** Request for female- and male-stratified systemic sclerosis GWAS summary statistics (PMID 41999721)

Dear Dr Acosta-Herrera,

I am conducting a reproducible, cell-resolved regulatory analysis of the sex-specific systemic sclerosis GWAS reported in your 2026 Lancet Rheumatology article (PMID 41999721; DOI 10.1016/S2665-9913(25)00376-5).

The article states that the sex-specific meta-GWAS summary statistics will be available through the NHGRI-EBI GWAS Catalog. I checked the Catalog using the PMID and disease name, but I could not yet identify the corresponding GCST accession or full-summary files.

Could you please provide the accession or download instructions for the complete female- and male-stratified meta-analysis summary statistics? For reproducible harmonization and signal-level analysis, the following fields or accompanying metadata would be especially helpful:

- chromosome and base-pair position with the exact genome build;
- variant identifier, reference/alternate allele, and effect/non-effect allele;
- beta or log odds ratio, standard error, and P value;
- effect-allele frequency and imputation quality;
- per-variant sample size, effective sample size, or contributing-cohort count;
- case/control counts and ancestry description;
- data dictionary, analysis notes, and provider checksum;
- if available, cohort participation information or cohort-level regional results.

If the genome-wide release is still being processed, complete regional summary statistics for the following frozen windows would allow a bounded first analysis:

- GRCh38 chr22:38,328,807–40,328,807 around rs66578187/SYNGR1;
- GRCh38 chr6:1–1,396,321 around rs12203592/IRF4.

We aim first to reproduce the published GTEx colocalization and then test the additional immune-cell chromatin-accessibility layer. We will preserve the original source attribution and all access conditions.

Thank you for your help.

Kind regards,

[Name / affiliation]

## 3. 收到文件后的目录准备

保持 provider 原始压缩文件不变。复制 `h6_intake/metadata_template.json`，分别填写：

- `female_metadata.json`
- `male_metadata.json`

必须用数据提供方的说明填写 build、effect scale、source URL、accession、case/control counts 和样本量是否对所有变异固定。不要从文件名猜测。`expected_sha256` 或 `expected_md5` 必须来自提供方公布值或此前已经冻结的可信副本；仅在下载后对同一文件现算再回填的 hash 只能用于后续完整性复查，不能证明首次下载来源正确。没有逐变异 N/cohort count 时，只有 provider 明确说明固定 N，且 `cases + controls = total_sample_size`，才设置 `variant_sample_size_constant=true`。

## 4. 运行命令

完整 female + male：

```powershell
cd H:\SCI2\YR1\R4A9\h6_intake
.\RUN_H6_INTAKE.ps1 `
  -FemalePath 'D:\downloads\female_ssc_sumstats.tsv.gz' `
  -FemaleMetadata '.\female_metadata.json' `
  -MalePath 'D:\downloads\male_ssc_sumstats.tsv.gz' `
  -MaleMetadata '.\male_metadata.json'
```

若先取得 female：

```powershell
.\RUN_H6_INTAKE.ps1 `
  -FemalePath 'D:\downloads\female_ssc_sumstats.tsv.gz' `
  -FemaleMetadata '.\female_metadata.json'
```

脚本使用流式读取，可处理大文件；只导出 chr22 和 IRF4 两个冻结窗口及 JSON/MD 审计结果。它不运行 fine-mapping 或 coloc。

## 5. 已验证环境

- Python：`D:\bioinfor\python.exe`
- Python 依赖：仅标准库；H6 intake 不需新装包。
- 独立参考/LD 复核使用已有 NumPy/SciPy 与 WSL PLINK2。
- RSS 复核使用 R 4.6.0 与 susieR 0.14.2。
- `h6_intake/test_intake.py` 的 16 个状态回归测试全部通过，覆盖完整 PASS、核心列/逐行缺失、SHA/MD5、build、effect scale、双窗口覆盖、重复 key、截断扫描、样本设计和 INFO 越界。

本轮只生成 Markdown、JSON、TSV 与脚本，不存在需 Office 排版的 DOCX/XLSX/PPTX，因此没有调用任何 Office 渲染器。后续如需渲染 Office 文件，按用户要求使用 WPS 后台渲染。
