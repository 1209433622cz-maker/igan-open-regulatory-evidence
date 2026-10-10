# R7C0 GJOKA 样本量与模型来源审计

## 问题

RP v4 要求核对病例对照 GWAS 中总样本量 `N=24,510` 与有效样本量约定是否会造成 SuSiE-RSS 模型不匹配。

## 来源证据

Gjoka 与 Cordell 的真实数据分析明确说明：

- 输入来自 Cordell 等 2021 欧洲 PBC GWAS 的 logistic-regression summary statistics；
- 8,021 例病例、16,489 例对照，总样本量 24,510；
- 逐位点相关矩阵来自作者自己的欧洲 individual-level data；
- summary statistics 与 LD 用于 SuSiE-RSS；
- 官方数据页公开 `GJOKA_SUMSTATS.zip`。

本地 R7B1B v2 的疾病 SuSiE 实现固定使用 `susie_rss(z=zD, R=dld, n=24510, ...)`，输入为 GJOKA reanalysed z 与对应 study LD。

## 判断

`N=24,510` 与上游真实数据分析约定、summary statistics 和 LD 来源相匹配。`4N_caseN_control/N_total≈21,584` 是另一种二分类有效样本量表达；它可以用于某些近似公式或跨研究标准化，但不能自动替代来源作者在 SuSiE-RSS 中使用的总 N。

```text
G1 = PASS_SOURCE_MATCHED_N_TOTAL
642 comparison rerun = NO
N_eff sensitivity = RETIRED unless new source evidence appears
```

## 仍存在的限制

该判断证明“当前实现忠实继承来源模型”，不证明所有病例对照 fine-mapping 软件在任何情境下都应使用总 N。论文中应明确这是 source-matched reproduction，而不是宣称总 N 具有普遍优越性。

## 来源

- https://pmc.ncbi.nlm.nih.gov/articles/PMC11656035/
- https://www.staff.ncl.ac.uk/heather.cordell/GjokaPaper.html
- 本地实现与 checksum 见 `R7C0_G1_GJOKA_sample_size_adjudication.json`。
