# R7A2A0 冻结协议：PBC 论文级架构与对照肝组织门

**冻结日期：2026-09-28**

**五供者原始运行完成：2026-09-17**

## 1. 项目状态

PBC 正式升级为当前主项目。升级依据为三个彼此独立的证据层：

1. OneK1K 中 FCRL3 与 IL12RB2 的 signal-specific disease–eQTL 共享；
2. TenK10K compatible cell 中 2/2 基因复制；
3. HRA008003 五个 PBC 肝组织供者中，FCRL3–B 与 IL12RB2–NK 均为 5/5 promotion eligible。

## 2. 冻结的论文主命题

> PBC 风险信号指向 B 细胞 FCRL3 与 NK 细胞 IL12RB2 两条可跨免疫 QTL 资源复现、且在 PBC 肝组织相应免疫谱系中可检测的调控轴。

该命题允许陈述“遗传/QTL 共享、跨资源复制、疾病组织谱系定位”。它不自动包含“PBC 中上调”“疾病导致表达改变”或“肝组织介导了遗传效应”。

## 3. R7A2A1 对照组范围

只分析 HRA008003 的五个肝血管瘤非病变肝组织对照：

```text
HRR1849454
HRR1849455
HRR1849456
HRR1849457
HRR1849458
```

冻结要求：

- 使用与 PBC 五供者相同的 `02_hra_bam_target_panel_v2.py`；
- 不改变 called-cell、B/NK lineage、target UMI 或技术 QC 阈值；
- 每个 BAM 先过 bytes、provider MD5、SHA-256、samtools quickcheck 与 schema v1.2；
- compact summary/receipt 复核通过后才删除 BAM；
- 完成 exact 5 PBC vs 5 control 后才计算组间指标。

## 4. 统计单位与输出

供者是统计单位。两个预冻结 endpoint 分别为：

- FCRL3 在 B gate 内的 lineage-normalized CPM；
- IL12RB2 在 NK gate 内的 lineage-normalized CPM。

报告每个供者的 gate cell 数、target-positive cell 数、target UMI、lineage total UMI、positive-cell fraction 与 CPM。组间比较使用 10 个供者全部标签组合的双侧精确置换检验，并对两个预冻结 target 作 BH 校正。

## 5. 解释边界

R7A2A1 仍是 marker-panel 支持层。即使组间差异显著，也只能称为“在冻结 marker gate 下的供者级支持性富集”。若主稿需要完整 disease-state cell-expression claim，必须另行完成全部 10 个肝组织供者的全基因矩阵重建、统一 QC、重聚类与 donor-by-cell-type pseudobulk。

若组间差异不显著，不能否定遗传/QTL 主链；论文可保留“疾病组织可检测与谱系定位”，但不得称疾病特异上调。

## 6. 论文 Figure 架构

1. **Figure 1**：开放数据与门控设计、研究主线；
2. **Figure 2**：PBC loci、allele harmonization 与 source-LD；
3. **Figure 3**：OneK1K signal-specific FCRL3/IL12RB2 结果；
4. **Figure 4**：TenK10K compatible-cell 独立复制；
5. **Figure 5**：HRA008003 五 PBC 供者及 5 vs 5 对照组织结果；
6. **Figure 6**：跨层整合、敏感性分析与主张边界。

## 7. 下一阶段

```text
R7A2A1 = HRA008003_EXACT_5_VS_5_CONTROL_TARGET_PANEL
TEN_CONTROL_AND_PBC_FULL_RECLUSTERING = HOLD
MANUSCRIPT_FINAL_FIGURES = HOLD_UNTIL_R7A2A1
```
