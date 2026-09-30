# R7A2A2 冻结协议：PBC 论文证据定稿与图件组装

**冻结日期：2026-09-30**

## 项目状态

R7A2A1 已完成 exact 5 PBC vs 5 非病变对照肝组织分析，五个对照供者均通过 bytes、MD5、SHA-256、samtools、BAM schema、完整 target scan、summary/receipt 与独立重聚合门。独立 QA 为 19/19 PASS。

PBC 保持主项目 `GO`。继续的依据是两条跨资源遗传调控链均已闭环：

1. OneK1K source-LD 多信号分析支持 FCRL3 与 IL12RB2；
2. TenK10K compatible-cell 对两个基因均形成独立复制；
3. 两个 target-lineage pair 在 5/5 PBC 肝组织供者中可检测。

R7A2A1 没有支持疾病特异上调：FCRL3–B 的方向为 PBC 较低，IL12RB2–NK 的方向为 PBC 较高，但两个预设靶标的 BH q 均为 0.1111。

## 冻结的主命题

> PBC 风险信号与 FCRL3 和 IL12RB2 的细胞类型相关 cis-eQTL 信号共享；这两条轴能在独立免疫 QTL 资源中复制，并在 PBC 肝组织的预设 B/NK marker gate 中检出。

不得把该命题扩写为：

- FCRL3 或 IL12RB2 在 PBC 中特异上调；
- 肝组织表达介导了遗传效应；
- marker-panel 结果等同于全转录组细胞状态差异分析。

## R7A2A2 必须完成的对象

1. 冻结一张逐层证据矩阵，列出每条主张的输入、统计量、通过门和表述上限；
2. 组装 Figure 1–6 的最终数据源，不重新筛选基因或细胞；
3. 将 Figure 5 固定为 donor-level 5 vs 5 结果，同时完整报告阴性/方向性结果；
4. 对主稿 Results、Methods、Limitations 建立逐句证据映射；
5. 完成针对 FCRL3、IL12RB2 与 PBC 共定位/单细胞研究的最新文献新颖性复核；
6. 形成投稿级主稿骨架及补充材料目录。

## 不进入当前关键路径的分析

十个供者的全 BAM 重下载、全基因矩阵重建与重聚类暂缓。它不会增加供者数，无法解决 n=5 vs 5 的功效限制，而且主论文的核心遗传调控结论不依赖疾病特异差异表达。只有以下情况才重新开启：

- 外部审稿明确要求细胞状态分辨率；
- 新的预注册组织层问题需要全转录组矩阵；
- 获得更多独立供者，使 donor-level pseudobulk 的统计功效实质增加。

## R7A2A2 完成门

```text
CLAIM_EVIDENCE_MATRIX = COMPLETE
FIGURE_1_TO_6_SOURCE_MAP = COMPLETE
NOVELTY_AUDIT = PASS_OR_REFRAME
RESULTS_METHODS_LIMITATIONS_EVIDENCE_MAP = COMPLETE
MANUSCRIPT_SKELETON = COMPLETE
NO_UNSUPPORTED_TISSUE_ENRICHMENT_CLAIM = PASS
```

完成后进入 `R7A2A3_MANUSCRIPT_DRAFT_V1`。

