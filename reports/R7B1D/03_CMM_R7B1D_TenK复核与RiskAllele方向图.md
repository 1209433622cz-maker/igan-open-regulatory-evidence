# R7B1D TenK 复核与 Risk-Allele 方向图

## 证据角色

TenK10K 只承担 independent molecular-QTL resource replication。IL12RB2–NK 与 FCRL3–B_intermediate 都复用 GJOKA PBC GWAS，且未重建 TenK donor-level source LD，所以不能称为 independent disease replication 或第二套 source-matched multi-signal proof。

## IL12RB2–NK

在共同 anchor `rs6679356` 上，GJOKA/OneK、GJOKA/TenK 与 FinnGen R12 的等位基因方向可以精确统一。三个资源家族均显示：PBC risk allele 与更高 IL12RB2 表达相关。FinnGen 还在自己的 disease lead `rs6659932` 上给出相同方向。该方向一致性增强了调控解释，但不建立表达介导。

## FCRL3–B

在 `rs3761959` 上，OneK B_IN、OneK B_MEM 与 TenK B_intermediate 均显示：PBC risk allele 与更低 FCRL3 表达相关。FinnGen 没有返回 PBC–FCRL3 coloc，故不能加入 FinnGen disease-direction concordance。

## FCRL3–CD8_ET

OneK CD8_ET 的 QTL beta 可以计算，但由于 source-matched PF10 adjudication 支持 H3，该方向不得被解释为 PBC shared-signal direction。方向表将其标记为 `eligible_for_shared_signal_direction = FALSE`。

## 允许的生物学表述

- “PBC risk-associated allele was associated with higher IL12RB2 expression across OneK, TenK and FinnGen molecular-QTL contexts.”
- “PBC risk-associated allele was associated with lower FCRL3 expression in the OneK and TenK B-cell contexts.”

禁止使用 `mediates`、`drives`、`causes` 或 therapeutic-target efficacy 语言。
