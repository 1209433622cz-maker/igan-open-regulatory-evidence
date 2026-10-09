# R7B2A：R7B1C 模拟错误、no-CS 与 no-pair 终裁

## 全量迭代审计

对 486,000 个原始迭代逐行重判：

| 通道 | 次数 |
|---|---:|
| technical error / nonconvergence | 0 |
| 两侧均无 credible set | 130,994 |
| disease 无 credible set | 16,819 |
| QTL 无 credible set | 177,405 |
| 两侧有 credible set 但无 pair | 0 |
| pair 可评价 | 160,782 |

主分析 pair-evaluable 比例为 33.08%。不同情景差异显著：S1 57.54%、S2 59.79%、S3 39.10%、S4 14.35%、S5 13.29%、S6 14.43%。

## 解释规则

无条件 H4 率同时反映“是否发现足够稳定的 credible set”和“形成 pair 后如何判定”。pair-conditional H4 率只描述已形成 pair 后的 estimator behavior。例如 S2 的无条件 H4 为 16.0%，但在可评价 pair 中为 26.76%；S5 分别为 1.12% 与 8.45%。二者都需报告，不能只选有利分母。

主模拟没有软件错误；大量 uninformative 是信号发现/可识别性不足。它也不应被写成生物学阴性。

## 次级 mismatch 分支

S6 mismatch 共有 81,000 次，技术错误为 0，其中 69,346 次没有 pair。历史 worker 没有保存 mismatch disease/QTL 的 CS 数量，无法再区分是哪一侧无 CS。该分支只用于有限的 matched-vs-mismatched decision sensitivity，不用于 no-CS 机制归因。由于主 matched 分支已能完成 RP v3 所需分解，且此缺口不改变中心结论，本轮不重复 81,000 次拟合。
