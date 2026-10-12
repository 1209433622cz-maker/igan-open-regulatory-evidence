# R7C3H0 GJOKA 样本量来源与 Neff 压力测试

## 来源裁决

Gjoka 与 Cordell 的原始 PBC fine-mapping 论文写明，其 SuSiE-RSS 输入为 logistic-regression summary statistics，使用总样本量 24,510，即 8,021 病例和 16,489 对照。公开数据入口为 GJOKA companion archive。

- 原文：[Fine-Mapping the Results From Genome-Wide Association Studies of Primary Biliary Cholangitis Using SuSiE and h2-D2](https://pmc.ncbi.nlm.nih.gov/articles/PMC11656035/)
- 官方资源页：[Gjoka paper data](https://www.staff.ncl.ac.uk/heather.cordell/GjokaPaper.html)
- SuSiE-RSS 文档：[susie_rss reference](https://stephenslab.github.io/susieR/reference/susie_rss.html)

因此不能把通用病例对照有效样本量公式自动当作来源分析的“正确替代”。主分析继续保留 `N=24,510`。

## 压力测试设计

有效样本量为：

```text
Neff = 4 / (1 / 8021 + 1 / 16489)
     = 21584.376825785395
```

预冻结工作量包括 33 个比较、14 个位点：全部 18 个严格 A2→M 反转、四条稿件关键轴、六个 H4 边界比较和六个高信息不确定比较。重叠后为 33 个唯一 comparison_id。

每个比较使用原疾病 z 统计、原 GJOKA disease LD、原 QTL summary、原 source-matched QTL LD 和原四套模型，只替换疾病样本量。新结果写入独立路径 `3_results/04_integration/R7C3H0/neff_probe`，没有覆盖 R7B1B。

## 结果

| 指标 | 结果 |
|---|---:|
| 比较 | 33 |
| 位点 | 14 |
| SuSiE fit | 132 |
| fit QC | 132/132 PASS |
| 最终状态改变 | 0/33 |
| 稿件关键轴改变 | 0/4 |
| 疾病可信集成员记录完全一致 | 164/164 |
| 最小可信集 Jaccard | 1.0 |
| PF10 L=10 最佳 H4 最大绝对变化 | 0.0001632569 |

关键输出：

- `3_results/00_audit/R7C3H0/R7C3H0_neff_probe_comparisons.tsv`
- `3_results/04_integration/R7C3H0/neff_probe/adjudication/R7C3H0_33_neff_state_comparison.tsv`
- `3_results/04_integration/R7C3H0/neff_probe/adjudication/R7C3H0_disease_CS_identity.tsv`
- `3_results/04_integration/R7C3H0/neff_probe/adjudication/R7C3H0_neff_probe_state.json`

## 科学解释

这项结果支持“当前主要结论不依赖于 24,510 与 21,584.38 之间的样本量口径差异”，但只对预冻结的 33 个高风险比较成立。它不是 642 个比较的全面重跑，也不能证明两种口径在其它疾病、效应大小、病例比例或 LD 架构下普遍等价。

由于主分析与来源一致，Neff rerun 的角色固定为二级稳健性检查，不是勘误、替代分析或新验证队列。
