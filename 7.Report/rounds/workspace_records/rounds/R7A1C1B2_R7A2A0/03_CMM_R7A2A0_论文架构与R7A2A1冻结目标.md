# CMM R7A2A0：论文架构与 R7A2A1 冻结目标

**日期：2026-09-28**

## 1. 论文主线

论文主线冻结为两条并行、可互相校验的调控轴：

```text
PBC GWAS → source-aware LD / signal decomposition
         → OneK1K FCRL3-B shared signal
         → TenK10K B-intermediate replication
         → PBC liver B-lineage detectability

PBC GWAS → source-aware LD / signal decomposition
         → OneK1K IL12RB2-NK shared signal
         → TenK10K NK replication
         → PBC liver NK-lineage detectability
```

INAVA 保持 `UNINFORMATIVE_WEAK_ONEK_QTL`，不进入论文核心结果，也不新增第四个基因。

## 2. Figure 设计

| Figure | 内容 | 当前状态 |
|---|---|---|
| 1 | 数据来源、门控与研究设计 | 可开始组装 |
| 2 | PBC loci、harmonization、source-LD | 上游结果已存在 |
| 3 | OneK signal-specific 两基因证据 | 上游结果已存在 |
| 4 | TenK compatible-cell 2/2 复制 | 已闭环 |
| 5 | PBC 肝组织 5/5 与 5 vs 5 对照 | 等待 R7A2A1 |
| 6 | 整合模型、敏感性与 claim ladder | 等待 R7A2A1 后冻结 |

## 3. R7A2A1 的三个合法出口

### A. 一个或两个 target 显示供者级支持性富集

保留 exact permutation P 与 BH q，表述为 marker-gated donor-level support。只有在进一步全矩阵重聚类后，才升级为 cell-state differential-expression claim。

### B. 两个 target 在对照中同样可检测且无组间差异

不推翻遗传/QTL 主链。Figure 5 表述为 tissue/cell-lineage localization；论文主命题不使用“PBC-specific upregulation”。

### C. 对照 technical QC 失败

只允许修复预分析技术问题；不得放宽 B/NK gate 或 target 阈值。若公开 BAM schema 与 PBC 不兼容，转入完整矩阵方案的独立可行性审计。

## 4. 下一阶段冻结

```text
NEXT = R7A2A1_HRA008003_EXACT_5_VS_5_CONTROL_TARGET_PANEL
CONTROL_RUNS = HRR1849454..HRR1849458
TOTAL_DOWNLOAD = 134657112757 bytes
FULL_RECLUSTERING = HOLD
FINAL_MANUSCRIPT_FIGURES = HOLD
```
