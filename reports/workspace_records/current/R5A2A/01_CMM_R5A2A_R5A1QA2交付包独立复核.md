# CMM R5A2A：R5A1-QA2 交付包独立复核

## 接入对象

- ZIP：`CMM_R5A1QA2_MG_ReplicationAwareRequalification_2026-09-13.zip`
- ZIP SHA-256：`c2125db6be3a73b08eb2bd710a077eff71434fc85d344c616824788563ab0f30`
- 独立 99 行动记录 SHA-256：`18f0958051b65a4b6266d3d61d0c97da406fc57de13422cfad0889f0c8e2b933`

原始对象已复制到 `7.Report/rounds/R5A1QA2/imported_2026-09-14/`，解包副本位于 `9.Version/stage_workspaces/R5A1QA2_imported_2026-09-14/`，没有覆盖当前规范资产。

## 完整性

- ZIP CRC：`PASS`；
- `checksums.sha256` 中 11 个 payload：`11/11 PASS`；
- 独立 99 报告与 ZIP 内 99 报告逐字节相同；
- 中文文件名和正文均为合法 UTF-8。终端曾显示为乱码，但 Unicode codepoint 复核显示中文原文完整，因此判定为 stdout 代码页显示问题，而非文件损坏。

## 科学内容复核

QA2 提出的三个主要纠偏均被保留：

1. 不能从四个预选位点内的 Bonferroni 校正推导全基因组异质性；
2. 候选排序必须同时考虑独立疾病复制和分子可测试性；
3. chr18 应先于 chr5，chr2 只能保留为低频探索位点。

## 代码审计与替换

QA2 附带的 `compute_mg_genomewide_subtype_heterogeneity.py` 可表达基本差异检验，但其 variant identity 由报告的 effect/other allele 构造，并默认输入排序可直接按该键合并。当前 GWAS 的 effect allele 恰好全部为 ALT，因此在本批数据上不必然给出错误结果；但这一实现对 effect=REF、同坐标多等位记录和未来 schema 变化不稳健。

本轮没有直接沿用该脚本，而是写入严格版：

- 从 `variant_id=chrom_position_REF_ALT` 建立 canonical key；
- 将 beta 和 EAF 统一定向到 canonical ALT；
- 同坐标多等位记录先分组再排序；
- 重复 canonical key 明确排除并计数；
- MHC、解析错误、单侧缺失、等位基因方向和输入 SHA-256 全量审计；
- 使用所有 exact shared non-MHC variants 定义 Bonferroni 阈值。

合成测试覆盖 ALT/REF 翻转并通过。真实全量运行结果见本轮报告 02。

## 结论

R5A1-QA2 的科学建议为 `ACCEPT_WITH_STRICT_RECOMPUTATION`。其交付完整性通过，但最终数值和阶段判定以本轮独立脚本、真实字节和新状态文件为准。
