# CMM R5A1：三套 MG GWAS 字节级接入与来源校验

日期：2026-09-13

## 数据对象与研究定义

三套 summary statistics 均来自 GWAS Catalog 的 harmonised GRCh38 文件：

| Accession | 表型 | Cases | Controls | 本地行数 | SHA-256 |
|---|---|---:|---:|---:|---|
| GCST90432156 | MG overall | 5,708 | 432,028 | 7,126,837 | `528a2e0d0216a6e7fb575d508e4a7815b6fedfdd1e9f594585ecf5a399181737` |
| GCST90432157 | EOMG | 1,391 | 22,407 | 7,563,388 | `cc3667600a831728b064d736e12665d424683591ba6ee479c61087d394dca5cc` |
| GCST90432158 | LOMG | 2,404 | 64,103 | 6,120,145 | `b824861a9e33f83b1af539084f30d54e41dbc4c921295187dd730abc0266b7e6` |

Braun 等的研究定义为 EOMG 起病年龄 `<50`，LOMG `≥50`。论文明确说明 LOMG controls 未纳入 EOMG GWAS，因此本轮冻结独立样本亚型差异检验，不使用重叠样本协方差修正。MHC 排除区固定为 GRCh38 chr6:25,000,000–35,000,000。

## 字节与内容验收

所有三个文件满足：

- 实际字节数等于官方 metadata 声明；
- gzip 流完整读取至 EOF；
- 12 列 header 完全一致；
- chromosome、base-pair、variant_id、reference/alternate/effect allele 映射无结构错误；
- odds ratio、standard error、effect allele frequency 和 P 值可解析；
- genome-wide significant lead 可在 EOMG 与 LOMG 间按同一 GRCh38 variant identity 和 ALT allele 对齐。

详细机器可读结果见 `3_results/00_audit/R5A1/MG_GWAS_intake_and_heterogeneity_audit.json` 与 `3_results/01_gwas/R5A1/MG_GWAS_byte_manifest.tsv`。

## GCST90432157 官方 MD5 sidecar 异常

`GCST90432157` 的官方 sidecar 声明 MD5 为 `ef79b92a35ec5e03c6be652e1ed908b0`，当前服务器实际文件 MD5 为 `a66eb9d0b742a1601b3d77b9ab9585ed`。该异常按以下证据裁定为 source-side sidecar defect：

1. 从字节 0 独立下载两次；
2. 两份文件均为 217,879,063 bytes；
3. 两份 SHA-256 完全一致，均为 `cc3667600a831728b064d736e12665d424683591ba6ee479c61087d394dca5cc`；
4. 两份 gzip 均可完整解析，行数、header 和内容 QC 一致；
5. 数据文件与 sidecar 的服务器更新时间不同。

因此该文件记为 `PASS_SOURCE_SIDECAR_DEFECT_TWO_IDENTICAL_RETRIEVALS`。例外被显式记录，未用自算 checksum 冒充官方 checksum。

## 统计模式

每套数据以 ALT 为统一效应等位基因，`beta_alt = ln(OR_alt)`。EOMG–LOMG 异质性为：

```text
z = (beta_EOMG - beta_LOMG) / sqrt(SE_EOMG^2 + SE_LOMG^2)
P_het = 2 * Phi(-abs(z))
```

四个非 MHC GWS 区域采用 4 次检验 Bonferroni。3 Mb 仅用于把显著行合并成描述性区域，不能解释为 LD 独立位点。正式 R5A2 必须使用区域级变异和 LD 重新界定信号。

## 来源

- GWAS Catalog study pages：`https://www.ebi.ac.uk/gwas/studies/GCST90432156`、`GCST90432157`、`GCST90432158`
- GWAS Catalog summary-statistics portal：`https://www.ebi.ac.uk/gwas/downloads/summary-statistics`
- Braun et al. 2024 full text：`https://pmc.ncbi.nlm.nih.gov/articles/PMC11560923/`

