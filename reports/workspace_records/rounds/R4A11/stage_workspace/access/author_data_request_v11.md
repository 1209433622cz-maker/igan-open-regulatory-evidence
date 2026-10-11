# R4A11：2026 SSc female/male summary statistics 请求草稿

日期：2026-09-12  
状态：**DRAFT / NOT SENT**

本文件是供用户审核和自行发送的草稿。本轮没有向作者、期刊、数据库或其他外部对象发送消息。

## Email draft

**Subject:** Request for female- and male-stratified systemic sclerosis GWAS summary statistics (PMID 41999721)

Dear Dr Acosta-Herrera,

I am conducting a reproducible, cell-resolved regulatory analysis of the sex-specific systemic sclerosis GWAS reported in your 2026 Lancet Rheumatology article (PMID 41999721; DOI 10.1016/S2665-9913(25)00376-5).

The article states that the sex-specific meta-GWAS summary statistics will be made available through the NHGRI-EBI GWAS Catalog. As of 12 September 2026, I could not identify the corresponding GCST accession or downloadable full-summary files using the PMID, DOI, title, or the reported lead variants.

Could you please provide the accession or download instructions for the complete female- and male-stratified meta-analysis summary statistics? To preserve provenance and support reproducible harmonization, it would be especially helpful to receive the original provider files together with a checksum manifest or signed transfer record, and the following fields or documentation:

- chromosome and base-pair position with the exact genome build;
- variant identifier, reference/alternate allele, and effect/non-effect allele;
- beta or log odds ratio, standard error, and P value;
- effect-allele frequency and imputation quality;
- per-variant sample size, effective sample size, or contributing-cohort count, with the exact meaning of any column named N;
- female and male case/control counts and ancestry description;
- association model, data dictionary, analysis notes, and provider-generated SHA-256 or MD5 manifest;
- if available, cohort participation information, study-matched LD, or cohort-level regional results.

If the genome-wide release is still being processed, complete variant-level regional statistics for both female and male analyses in these pre-registered GRCh38 windows would support a bounded first analysis:

- chr22:38,328,807–40,328,807 around rs66578187/SYNGR1;
- chr6:1–1,396,321 around rs12203592/IRF4.

We plan first to reproduce the published broad-tissue SYNGR1 colocalization direction and then test the additional immune-cell chromatin-accessibility layer. We will preserve the original attribution, access conditions, and provider files without modification.

Thank you for your help.

Kind regards,

[Name]  
[Affiliation]  
[Contact details]

## 收到文件后不要先改动

1. 保留下载原文件、下载 URL/邮件原件和提供方 checksum sidecar；不要重命名、解压或编辑原文件。
2. 把 female 和 male 文件分别复制到一个只读归档目录。
3. 从 `R4A11/h6_v2_1` 复制对应 metadata 模板，只用提供方材料填写空字段。
4. checksum 证据文件也单独保留并计算其自身 SHA-256。
5. 运行 H6 v2.1；只有 exit 0 加 exact PASS 才进入 R4A12。

请求作者数据是当前最短的外部路径，但是否发送和以何身份发送由用户决定。
