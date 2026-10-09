# CMM R7B1C 执行摘要：真值已知的来源匹配多信号校准

日期：2026-10-09

```text
R7B1C = COMPLETE
GRID_ROWS = 486/486
REPLICATES = 486000/486000
MATCHED_FIT_FAILURES = 0
MATCHED_NONCONVERGED = 0
INDEPENDENT_QA = 21/21 PASS
FALSE_H4_REDUCTION = DEMONSTRATED_WITH_RECOVERY_COST
GENERAL_METHOD_SUPERIORITY = NOT_DEMONSTRATED
PF10_TO_PF50_LD_MISMATCH_HARM = NOT_DEMONSTRATED_IN_TWO_TEMPLATES
MANUSCRIPT_REWRITE = HOLD
NEXT = R7B1D_EXTERNAL_MOLECULAR_CHROMATIN_REPLICATION_AND_DIRECTION
PUBLIC_GITHUB_SYNC = PENDING
```

R7B1C 已完成研究计划书 v2 冻结的六场景、486 行和 486,000 次 replicate。每个参数格在两个经验模板中各运行 500 次：GJOKA locus 2 + OneK NK，以及 GJOKA locus 4 + OneK B_IN。模拟比较 single-causal ABF、source-matched multi-signal SuSiE/coloc 与 S6 的同位点 PF10→PF50 QTL-LD mismatch。

## 主要结果

- distinct truth（S2/S5）中，ABF 的平均 H4 decision rate 为 **12.41%**，source-matched multi-signal 为 **8.56%**，绝对下降 **3.85%**、相对下降 **31.02%**。
- shared truth（S1/S3/S4/S6）中，ABF 的平均 H4 recovery 为 **32.99%**，source-matched multi-signal 为 **26.66%**，绝对下降 **6.33%**、相对下降 **19.20%**。这是一项明确的 recovery / abstention 代价，不能从 false-H4 降低单独推导“方法普遍更优”。
- S2 correlated-distinct 的 false H4 仍为 **16.00%**；source matching 与多信号分解没有消除高相关不同因果变异带来的误判。
- S5 2×2/no-shared 的 H4 从 **4.32%** 降为 **1.12%**，说明在该冻结结构下存在有界增益。
- S6 matched H4 rate 为 **9.49%**，PF10 z + PF50 LD mismatch 为 **9.45%**；平均绝对 best-H4 改变量为 **0.0012**。
- matched fit failure=0；non-converged=0；没有删除不利或无信息格点。

| 场景 | 真值共享 | ABF H4 | matched H4 | matched H3 | uninformative | disease CS all coverage | QTL CS all coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1_one_shared | True | 65.94% | 54.12% | 0.05% | 45.83% | 95.45% | 55.97% |
| S2_distinct_correlated | False | 20.50% | 16.00% | 23.15% | 60.85% | 95.35% | 58.17% |
| S3_disease2_qtl1_partial | True | 36.87% | 33.44% | 2.12% | 64.43% | 40.25% | 55.72% |
| S4_two_by_two_one_shared | True | 14.59% | 9.57% | 2.65% | 87.78% | 40.53% | 5.38% |
| S5_two_by_two_none_highLD | False | 4.32% | 1.12% | 8.18% | 90.70% | 40.48% | 5.11% |
| S6_matched_vs_mismatched_LD | True | 14.58% | 9.49% | 2.70% | 87.81% | 40.16% | 5.35% |

## 结论边界

该模拟支持的是两个经验 LD 模板、固定效应量、固定 N 与冻结参数网格下的**条件性 trade-off**。它不支持 source-matched multi-signal 的全局优越性，也未在这两个模板中证明 PF10/PF50 LD mismatch 会造成普遍严重偏倚。它不能代表所有 ancestry、效应分布或基因组区域，也不能证明任何 PBC gene–cell assignment 的生物学机制。
