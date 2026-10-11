# R4A4 YR1(1) 与 R4A3 完整性/增量审计

日期：2026-09-09

## 输入

- `CMM_R4A3_双位点证据审计与完整复现包_2026-09-09.zip`
- `YR1(1).zip`
- 四份单独上传的R4A3报告

## 完整性结果

用户上传的R4A3 ZIP实际SHA256：

`40460cb7498b175c92dc8051a8ac89a2e1809c2190b6245fad3d03dcadfc344c`

YR1(1) 内部 `R4A3/results/release_validation.json` 声明的R4A3 release SHA256完全相同，因此当前上传的R4A3完整包与YR1记录的正式release是同一字节快照。

R4A3 release validation记录：132 members、131 verified hashes、CRC PASS。

YR1(1)不是“新的SSc疾病数据包”；其主要增量是把R2/R3/R4A历史报告、R4A1原始TenK10K文件和R4A3工作区集中保存。因此本轮没有把YR1(1)误判成新的female/male GWAS输入。

## 可直接复用的新增计算资产

YR1(1) 中存在：

- TenK10K `common_variant_gene_level_results_with_annotated_fails.zip`
- TenK10K `susie_summary.zip`
- R4A1既有schema、target screen、celltype mapping
- R4A3 FinnGen chr22 eQTL/caQTL快照与peak/gene JSON

因此本轮合法地完成了新的本地独立复算，而不是重复依赖旧报告结论。

## 未发现

YR1(1) 中未发现：

- 2026 female SSc full/region summary statistics
- 2026 male SSc full/region summary statistics
- 对应新GCST accession metadata文件
- ancestry-matched disease LD矩阵
- FinnGen multiome正式release README + full nominal/SuSiE下载快照

因此 disease coloc 仍保持 NOT_TESTED。
