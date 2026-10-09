# CMM R7B1D 执行摘要：外部多组学与方向门

## 最终判定

```text
R7B1D = COMPLETE
TARGET_FREEZE = PASS__4_PREEXISTING_ANCHORS
FINNGEN_PUBLIC_BYTE_INTAKE = PASS__18_OF_18
INDEPENDENT_QA = PASS__23_OF_23

IL12RB2_NK = PASS_EXTERNAL_DISEASE_AND_MULTIOME_SUPPORT_BOUNDED
FCRL3_B = PASS_CROSS_QTL_RESOURCE__FINNGEN_DISEASE_COLOC_NOT_RETURNED
FCRL3_CD8_ET = NEGATIVE_CONTROL_RETAINS_H3_NO_EXTERNAL_RESCUE

G6_EXTERNAL_REPLICATION = PASS_BOUNDED
GENERAL_METHOD_SUPERIORITY = NOT_ESTABLISHED_BY_R7B1C
PBC_PROJECT = RETAIN__EVIDENCE_INTEGRATION_GO

NEXT = R7B1E_INTEGRATED_CLAIM_EVIDENCE_FREEZE_AND_FIGURE_SOURCE_ASSEMBLY
```

R7B1D 没有从 R7B1B 的 78 个 stable-H4 comparison 中重新挑选外部结果最漂亮的对象。当前分析只继承四个早已冻结的代表性比较：IL12RB2–NK、FCRL3–B_IN、FCRL3–B_MEM，以及 FCRL3–CD8_ET 反例。

## 决策性结果

FinnGen R12 的公开 CASCADE 输出返回 3 条 `CHIRBIL_PRIM–IL12RB2` disease–eQTL 记录，细胞为 `l1.NK`、`l2.NK` 和 `l1.PBMC`。三条记录的 `PP.H4.abf` 为 0.9698–0.9706，credible-set overlap 为 5–9 个变异。它们构成相对于 GJOKA/OneK 主分析的外部 disease–molecular-QTL aggregate layer，但不替代 OneK 的来源匹配多信号分析。

IL12RB2 的 FinnGen regulatory layer 进一步包含 `chr1_67307966_T_C`、峰 `chr1-67307618-67308670` 与 IL12RB2 的 fasthurdle peak–gene link。该峰在 `l1.NK` 和 `l2.NK` 的 caQTL q 值分别为 3.93e-13 和 6.02e-15。然而该 eQTL variant 并不属于该峰的 caQTL credible set，所以本轮严格保留 **positional cascade** 表述，不声称完整的 disease→caQTL→expression 因果链。

FCRL3 的公开 gene/region/variant 查询返回强 B/T-cell eQTL 信息，但没有任何 `CHIRBIL_PRIM–FCRL3` coloc 记录。这个结果被定义为公开输出未返回，不是生物学阴性或经过充分功效检验的零效应。FCRL3–B 的可用外部证据仍然是 OneK source-matched stable H4 与 TenK B_intermediate single-causal molecular replication。

精确等位基因统一后，PBC risk allele 在 OneK、TenK 和 FinnGen 中一致关联 **更高 IL12RB2 表达**；FCRL3–B 在 OneK 与 TenK 中一致关联 **更低 FCRL3 表达**。这些是方向性关联，不是 mediation probability。

## 研究计划 v2 的含义

G6 的通过条件是“至少部分 robust assignment 在 TenK/FinnGen 再现或得到新的 regulatory layer”，当前已经满足。与此同时，R7B1C 未证明来源匹配多信号方法具有普遍优势，因此新论文应定位为 **PBC-wide systematic reclassification benchmark with scenario-dependent calibration and bounded external multiome support**，而不能升级为一般性方法优越性论文。

资源能力与论文状态已按 2026 年 10 月 9 日核对：[FinnGen access/results](https://www.finngen.fi/en/access_results)、[Nature 2026 immune multiome atlas](https://www.nature.com/articles/s41586-026-11078-2)、[CASCADE browser](https://cascade.finngen.fi/)。
