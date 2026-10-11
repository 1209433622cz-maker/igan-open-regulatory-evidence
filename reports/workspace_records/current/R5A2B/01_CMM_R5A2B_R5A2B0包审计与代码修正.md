# R5A2B0 包审计与代码修正

## 发布包完整性

- 文件：`CMM_R5A2B0_chr5_BoundedPilot_Preflight_2026-09-14.zip`；
- bytes：69,101；
- SHA-256：`e6291c8c59d94bcffa95ea5d9f1b6e85ba95aeb646ed32b9e584de0bd8bf76ec`；
- ZIP CRC：PASS；
- 内部 checksum：25/25 PASS；
- 独立 99 报告 SHA-256：`f514408e56556c9872cc01b7cf00b17a1ed40387ec11897756b6b2ce5b87100c`，与包内版本逐字节相同。

32 个 target 已从官方 OneK1K top-eQTL archive 独立重算：cell–gene–top variant 32/32 精确一致，P/beta/q-value 最大绝对差 `3.39×10^-21`。资格规则为冻结 8 基因、source `q<0.05` 且 source top 位于固定 chr5 窗口。

## 执行前发现并修复的问题

`03_extract_harmonize_mg_grch37_chr5.py` 的计算变量已经是 chr5 / rs6861227，但 docstring、输出 chromosome、lead key 和审计标签仍残留 chr18 / rs7239261。规范副本在执行前全部改为：

```text
chromosome = 5
lead = rs6861227
window = GRCh37 5:149447128–151447128
```

原始接收包保留未改写。

第一次 GWAS gate 还发现 EOMG `5:150666843` 有一条 A/G allele-mismatch 和一条可匹配 A/C 记录。原脚本按坐标进入 BIM 就计为重复，导致假性失败。修正后门控只要求 inference-eligible 记录唯一；A/G 记录仍保留为审计行并排除，A/C 记录唯一进入分析。三套 GWAS 最终全部通过。

`04_run_chr5_coloc_smoke.py` 的 top-SNP tie-break 也改为使用完成 finite 过滤后的 variant index，避免极端情况下 ids 与 posterior 长度不一致。

机器审计位于 `3_results/00_audit/R5A2B/`。
