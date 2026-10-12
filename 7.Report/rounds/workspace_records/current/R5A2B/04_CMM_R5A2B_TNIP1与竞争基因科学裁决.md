# R5A2B TNIP1 与竞争基因科学裁决

## TNIP1

TNIP1 是 chr5 中最合理的先验候选，但不能通过本轮信号门。

NK/TNIP1 source top 为 `5:150477087`，nominal `P=1.70×10^-7`；disease lead rs6861227 的 QTL `P=0.00631`。EOMG 疾病 top 是 exact rs6861227，默认 coloc 却为 `H3=0.9094、H4=0.0662`。这符合“同一区域存在疾病信号和 eQTL，但不是同一 signal”。

CD4_NC/TNIP1 更弱：source top `P=2.26×10^-5`，rs6861227 QTL `P=0.0937`，默认 H4 0.0552。TenK10K 中 disease lead 落入 TNIP1 credible set 的旧证据不能覆盖 OneK1K signal-level 失败；按冻结顺序，TenK10K 本轮不触发。

## 竞争基因

ANXA6、GM2A、RPS14、CCDC69 等有远强于 TNIP1 的 source eQTL，但 EOMG coloc 几乎完全由 H3 主导。最典型的 CD4_NC/ANXA6：QTL `P≈5.15×10^-59`，但默认 `H4≈1.88×10^-5`、`H3≈0.99974`。

这直接证明：最强 eQTL 不能自动成为疾病效应基因。竞争模型没有发现可以替代 TNIP1 的共享信号基因。

## claim 边界

允许：

> chr5/rs6861227 是具有历史与 EOMG 富集支持的 MG 疾病位点，但公开 OneK1K PBMC cis-eQTL 不支持八个冻结基因中的共享 expression-mediated signal。

不允许：

- “TNIP1 被生物学否定”；
- “chr5 疾病位点无效”；
- “强 ANXA6/GM2A eQTL 证明它们是 MG causal genes”；
- “高 p12 下 H4 上升证明共定位”。
