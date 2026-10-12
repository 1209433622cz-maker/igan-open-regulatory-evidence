# CMM R6A1 执行摘要：IgAN 字节级与阳性证据预检

日期：2026-09-14  
最终判定：**R6A1 COMPLETE；IgAN 主项目 `GO_R6A2`**

## 决策解释

本轮按用户正式指定的 **completion-first** 目标执行。R6A0 中基于创新性饱和度提出的早停意见作为历史审计保留；R6A0R 根据“研究完整做完、真实阳性证据充足、一区标准执行且二区/三区可接受”的目标重评后允许进入 R6A1。本文档只把用户的最新项目目标作为行动依据，未把附件内容当作新的用户指令。

R6A1 的八个冻结门全部通过：

| 门 | 结果 |
|---|---:|
| 4 套 GWAS 传输字节与分析字节 | PASS |
| schema、数值、25 个非 HLA signal 坐标 | PASS |
| 论文定义的非 HLA loci | 24 |
| OneK1K 可测 loci | 22 |
| TenK10K 可测 loci | 24 |
| 跨资源同基因、相容免疫细胞候选 loci | 22 |
| 已发表 DICE 正控在两套 QTL 中恢复 | 4 genes / 3 loci |
| GSE127136 靶基因可检测性 | 145/146（99.32%） |

## 最重要的证据

1. combined、European-only、Asian-only IgAN GWAS 和 serum IgA GWAS 均完成真实下载、SHA-256 固定和逐行扫描，共检查 39,013,110 条数据记录；未发现非数值、`SE<=0`、越界 P 值或 `SNP` 与 `CHR:BP_hg19` 不一致。
2. 从论文 Table 1 冻结的 30 个独立信号中，5 个为 HLA、25 个为非 HLA，后者分布于 24 个 locus；CFH 有两个独立信号。combined 数据中共有 523 个非 HLA genome-wide-significant 变异。
3. serum IgA 在 25 个非 HLA lead signal 中有 9 个 `P<0.05`，9 个方向均与 IgAN risk allele 一致。
4. OneK1K 的 514 个 source-significant cell–gene 对覆盖 22 个 locus；TenK10K 覆盖 24 个 locus；相同 gene symbol 且 broad immune class 相容的预检候选覆盖 22 个 locus、146 个基因。
5. 已发表 DICE 正控 `IRF4`、`DUSP22`、`ZMIZ1`、`ITGAX` 在 OneK1K 与 TenK10K 中都恢复为可测试候选，形成 R6A2 的三个方法正控 locus：`IRF4/DUSP22`、`ZMIZ1`、`ITGAM/ITGAX`。

## 结论边界

R6A1 证明的是：数据真实存在、结构可计算、阳性正控可进入 signal-level 验证、组织层能检测主要候选。它**没有产生新的疾病–eQTL 共定位阳性**，也不能凭 source QTL 显著性指定 causal gene。

## 下一阶段

进入 **R6A2 — IgAN Regulatory Landscape：正控先行的全 24-locus 信号级分析**。先在三个正控 locus 验证 harmonization 与 coloc 回收能力，再按同一冻结规则扩到全部 24 个非 HLA locus。只有具体 cell–gene 通过稳健 H4 或可解析 H3/H4 门，才构建对应 source LD；TenK10K 只复核预先触发的相同 gene/cell-class 组合。
