# R7B1A：PBC-wide ABF 结果与触发集解释

## 计算模型

每个细胞使用公开 pseudobulk 首行非 NA donor mask，并与冻结 active-donor list 逐序核对；表达按源流程 `log1p` 后按基因做 sample-SD 标准化。OneK PLINK BED 以 BIM A1 dosage 解码，PF10 使用 `sex + PC1–6 + age + PF1–10` 共 18 个协变量进行残差化。当前实现明确标记为 TensorQTL 1.0.10 formula-compatible NumPy，不声称调用了 TensorQTL binary。

ABF 使用 `p1=p2=10^-4`、`p12=10^-6/10^-5/10^-4`，疾病 prior SD=0.2，QTL prior SD=`0.15×sdY`；`sdY` 根据 QTL variance、MAF 与 active-donor N 估计。

## 完整结果

| 类别 | 数量 | 解释 |
|---|---:|---|
| ROBUST_H4_TRIGGER | 112 | 默认先验达到冻结 H4 门，仅触发多信号分析 |
| H3_H4_AMBIGUITY_TRIGGER | 72 | H3+H4≥0.80 且 ratio 0.20–0.80 |
| H3_DISTINCT_SIGNAL | 455 | 有信息但默认更支持不同信号 |
| NO_TRIGGER_OR_UNINFORMATIVE | 4,821 | 未达到触发门或 QTL/疾病信息不足 |
| INSUFFICIENT_VARIANT_OVERLAP | 1,463 | <200 variants，技术不可判定 |

184 个触发分布在 25 loci、49 genes、14 cells。最大工作量 locus 为 51（39 个，全部 ambiguity）、33（30 个）、34（18 个）、50（12 个）和 28（11 个）。这提示大量比较共享同一 disease locus，下一阶段必须按 120 个唯一 cell–locus blocks 复用并严格记录 LD，而不是生成 184 个来源不明的矩阵。

## 先验与 source-q 边界

- 112 个默认 robust H4 中，101 个在 `p12=10^-6` 时仍有 `H4/(H3+H4)≥0.5`，11 个不保持。
- 72 个 ambiguity 在审慎先验下均未达到 H4 dominance；它们的目的正是接受多信号证伪。
- 184 个触发中 156 个来自该 cell 自身 source q<0.05；28 个来自 gene-level 纳入后保留的其它细胞。它们不能因后验或 source-q 不利而在这一阶段删除。

## 历史锚点

- IL12RB2–NK：PP.H4≈0.998156；
- FCRL3–B_IN：PP.H4≈0.992829；
- FCRL3–B_MEM：PP.H4≈0.989717；
- FCRL3–CD8_ET：PP.H4≈0.941335。

与历史冻结值的一致性检查通过。FCRL3/CD8_ET 已知会在多信号 PF10 中反转，因此本轮再次说明：ABF trigger 不能被命名为最终共享信号。

## 证据上限

当前允许写：PBC-wide screen 产生了一个预冻结的 184-comparison multi-signal workload。当前禁止写：发现 112 个新共定位、49 个致病基因、或 184 个阳性 cell–gene mechanisms。
