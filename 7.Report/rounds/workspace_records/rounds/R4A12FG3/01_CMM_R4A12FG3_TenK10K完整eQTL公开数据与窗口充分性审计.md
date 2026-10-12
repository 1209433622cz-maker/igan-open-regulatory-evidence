# CMM R4A12FG3：TenK10K完整eQTL公开数据与窗口充分性审计

日期：2026-09-13。基于用户提供的 R4A12FG2 真实区域结果，并结合本轮公开数据源复核。外部信息均与附件证据分层记录。

## 1. FG2留下的真实缺口

FG2已经证明IL12RB2在TenK10K中有强gene-level eQTL和source SuSiE CS，但用户附件中的小包只含gene-level ACAT/top marker以及CS member/PIP，因此当时“不运行正式coloc”是正确的。当前缺口不是基因是否存在，而是**完整per-variant association statistics**。

## 2. 本轮公开数据核查

TenK10K v2 Zenodo记录（2026-01-30）明确公开 `common_all_cis_pvalues_100kb.zip`，16.6 GB，MD5 `dd54714b2effb91160ac171ccb941534`。该ZIP内含28个细胞类型文件，例如 `NK_common_all_cis_raw_pvalues.tsv`、`CD8_TEM_common_all_cis_raw_pvalues.tsv` 等；每个成员约2.2–3.0 GB未压缩。

SAIGE标准association输出以Allele2为effect allele，字段包括 `Allele1/Allele2/AF_Allele2/BETA/SE/p.value`。因此该公开full-summary层在方法设计上满足新coloc/SMR所需的核心variant-level效应字段；最终仍应在真实字节到位后以文件header作为唯一schema真值。

## 3. 为什么100 kb已经足够

NCBI当前GRCh38 IL12RB2：chr1 `67,307,364-67,398,724`。TenK10K common cis-eQTL主分析定义为基因体±100 kb，因此目标范围是：

`chr1:67207364-67498724`

关键疾病variant：

- `rs6662198`：67,340,524，在IL12RB2基因体内；
- R12/R13 region lead `rs1954118`：67,448,804，距IL12RB2末端50,080 bp。

二者均落入TenK10K ±100 kb定义。FG2的R12/R13真实区域文件中，该范围各有1,918条记录、1,872个唯一位置。

因此：

- `common_all_cis_pvalues_100kb.zip` = **当前必须资源**；
- `part1–7 ... 1Mb.zip` ≈129.8 GB = **当前不需要**；
- 只有当预注册100-kb分析被证明因coverage不足而不可检验、且有独立科学理由时，才允许开启1-Mb rescue；不能因结果不漂亮扩大窗口。

## 4. 版本与完整性

优先使用Zenodo record `18221260` v2。下载后必须：

1. MD5核对 `dd54714b2effb91160ac171ccb941534`；
2. 记录local SHA-256；
3. 不把16.6 GB ZIP整包解压到磁盘；
4. 先流式提取NK的IL12RB2行，再提取预注册secondary cell types；
5. 保存每个source member、header和提取行数。

本轮已经附带安全dry-run下载脚本和流式提取脚本。
