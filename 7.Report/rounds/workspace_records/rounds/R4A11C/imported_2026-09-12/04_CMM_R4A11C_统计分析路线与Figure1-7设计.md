# CMM R4A11C — 统计分析路线与 Figure 1–7 设计

## 1. 总体原则

本项目采用“问题驱动而非工具驱动”的Figure与统计架构。每一层分析必须回答一个不同的不确定性：疾病信号真实性、性别差异、分子调控信号、候选效应基因、跨资源复制、疾病组织一致性与转化意义。

## 2. 数据流DAG

```text
2026 sex-stratified SSc GWAS (primary)
             │
             ├───────────────┐
             │               │
       chr22 disease      IRF4 secondary
             │
             ▼
  FinnGen immune caQTL ──────┐
             │               │
             ▼               │
       target ATAC peak      │
             │               │
      peak→gene links        │
             │               │
             ▼               │
  SYNGR1 / 20-gene eQTL     │
             │               │
             └──────┬────────┘
                    ▼
             C1 signal triangle
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
 FinnGen R12 female/male   TenK10K eQTL
 disease replication       molecular replication
          │                    │
          └─────────┬──────────┘
                    ▼
          SSc disease tissue
       GSE312129 → GSE249279
                    │
                    ▼
         integrated evidence tier
```

## 3. 分阶段统计路线

### Stage A — P0/H6 data intake

每个疾病文件必须经过：

1. provider identity binding；
2. immutable byte hash；
3. genome build；
4. REF/ALT/effect allele；
5. beta/SE/P/AF/sample semantics；
6. duplicate/malformed key；
7. frozen region coverage。

### Stage B — FinnGen R12 sex replication

Primary test不是“female P<0.05且male P>0.05”。

报告：

- beta_female, SE_female, CI_female；
- beta_male, SE_male, CI_male；
- Cochran Q `all_inv_var_het_p`；
- sign concordance with 2026；
- effective case/control counts；
- power/precision classification。

分类：`REPLICATED_SIGNAL / DIRECTIONAL_SUPPORT_ONLY / INCONCLUSIVE_LOW_POWER / DISCORDANT_WITH_ADEQUATE_POWER / UNTESTABLE`。

### Stage C — Fine-mapping readiness

条件：coverage gate + LD gate + z–LD gate。

R12单cohort GRCh38结果优先于2019 GCST009131作工程正控，因为其直接beta/SE/allele可避免旧meta格式问题。

### Stage D — Signal-level colocalization

每个edge单独建模：D1、E1、M1。多信号区域优先SuSiE-aware coloc，不把单因果PP4当唯一结论。

同时输出：H3、H4、H4/(H3+H4)、priors sensitivity、signal pair、CS overlap、LD/coverage QC。

### Stage E — Candidate competition

20候选全部同规则。最终排序不是按单个P值，而是按预定义证据域：

1. disease shared signal；
2. caQTL shared signal；
3. eQTL shared signal；
4. peak→gene；
5. TenK10K replication；
6. R12 disease replication；
7. disease-tissue concordance。

### Stage F — Tissue

使用donor-level统计。scRNA/snATAC不把cell count当n。空间分析用于定位，不承担遗传因果证明。

## 4. Figure设计

### Figure 1 — Study architecture and evidence gates

**目的：**让审稿人在一张图中理解哪些数据是discovery、replication、molecular、tissue，以及每层何时才能进入下一层。

建议子图：
- 1a data landscape；
- 1b variant→chromatin→gene→cell→disease逻辑；
- 1c evidence gates / stopping rules；
- 1d primary vs replication cohorts。

### Figure 2 — Sex-stratified disease genetics and independent R12 replication

**仅在真实summary到位后正式生成。**

建议：
- 2a 2026 female/male regional association chr22；
- 2b FinnGen R12 female/male同区域；
- 2c effect forest plot；
- 2d heterogeneity and power；
- 2e IRF4 secondary comparison。

避免仅以两个Manhattan图堆叠。

### Figure 3 — Cell-resolved chr22 signal triangle

核心主图。

- 3a disease regional signal；
- 3b NK caQTL fine-map；
- 3c SYNGR1 NK eQTL fine-map；
- 3d signal-pair colocalization；
- 3e target peak genomic context；
- 3f peak→SYNGR1 evidence；
- 3g exact overlapping variants与CS概率。

### Figure 4 — Bounded effector-gene competition and independent QTL replication

- 4a 20-gene evidence heatmap；
- 4b SYNGR1/RPL3/PDGFB matched comparison；
- 4c TenK10K CS/eQTL replication；
- 4d cell-type specificity；
- 4e evidence-tier ranking。

### Figure 5 — Disease-tissue context in untreated SSc skin

仅C1过门后生成。

- cell atlas/Umap只做入口，不作为主亮点；
- target cell state pseudobulk expression；
- accessibility；
- disease vs control effect；
- regulatory program；
- spatial localization。

### Figure 6 — Independent tissue/spatial replication

优先GSE249279，其他数据按机制需要调用。

重点不是重复Figure 5，而是回答：

> primary tissue signal是否跨队列/平台重现？

### Figure 7 — Integrated mechanism and translational prioritization

只汇总已经过门证据：

- genetic evidence tier；
- sex-replication status；
- molecular signal；
- tissue evidence；
- safety/druggability；
- final mechanistic model。

## 5. Supplementary建议

- S1 all data provenance；
- S2 full R12 endpoint QC；
- S3 coverage/drop ledgers；
- S4 LD diagnostics；
- S5 priors sensitivity；
- S6 full 20-gene competition；
- S7 all cell types；
- S8 negative/untestable signal pairs；
- S9 tissue QC；
- S10 reproducibility/software/session info。

## 6. Nature-style视觉冻结

- 白底；
- 统一字体；
- 颜色仅编码固定语义，例如female/male/cell type；
- 不使用彩虹色热图；
- 170 mm full-width主图；
- panel label固定；
- effect size + CI优先于星号；
- 所有主图都保留source-data TSV/CSV与生成脚本。
