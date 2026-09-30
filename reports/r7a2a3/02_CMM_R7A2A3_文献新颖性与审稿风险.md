# R7A2A3 文献新颖性与审稿风险

## 新颖性敌意结论

本文有可发表的 method/replication contribution，但 gene-level novelty 较低。当前标题、摘要和讨论已按这一事实重写。

### 已被既有研究占据的表述

1. Cordell et al. 2021 已完成大规模 PBC GWAS/GWMA 并提名 FCRL3 等候选基因，也开展广泛分子共定位。
2. Gjoka & Cordell 2025 已对 56 个非 HLA PBC 位点执行 SuSiE-RSS/h2-D2；疾病侧 fine-mapping 本身不是本文新颖点。
3. Han et al. 2026 已报告 FCRL3 的遗传/mQTL/eQTL/pQTL 整合、PBC 肝 B 细胞定位和 Raji 实验，是 FCRL3 方向最直接的重叠威胁。
4. Wang et al. 2026 已完成 PBC GWAS、731 immune traits、blood transcriptome、liver bulk/scRNA 的广泛整合；“PBC multiomics”不能作为笼统 novelty。

### 当前可辩护贡献

- disease LD 与 cell-QTL LD 各自来自匹配来源；
- multi-signal 终裁显示 FCRL3/CD8_ET 单信号阳性是不同信号；
- 同时要求 OneK 与 TenK 两个 population-scale single-cell eQTL resource 支持；
- 组织非显著结果、INAVA 与 CD8_ET 被传播到摘要、正文、图和结论边界。

## Top reviewer risks

### R1：已有 FCRL3 文献削弱 novelty — HIGH

应对：保留 required novelty sentence，逐段引用 Cordell、Gjoka、Han、Wang；不使用 first/newly identified。

### R2：把共定位误写为介导 — HIGH

应对：证据等级固定 E2；所有机制内容放入 hypothesis/next test；对 decisive perturbation test 给出明确设计。

### R3：TenK 没有 donor-source LD — HIGH

应对：将 TenK 限定为 robust single-causal molecular replication with source-CS support；不得与 OneK source-LD multi-signal tier 等同。

### R4：5v5 组织数据太小 — HIGH

应对：donor 为单位、252 个 exact label assignments、两靶点 BH、LODO 仅称敏感性；保留 null，不做 cell-level pseudo-replication。

### R5：图形视觉越界 — HIGH

Figure 1 现版有框/箭头重叠；Figure 3 的颜色可能让低先验未达0.8的点看似“stable pass”。这两图在 R7A2A4 必须修复后才能投稿。

### R6：投稿元数据缺失 — BLOCKER

作者、单位、通讯、贡献、基金、利益冲突需要真实人类输入。稿件已显式标注占位，不允许自动推断。

## Submission-readiness judgment

科学初稿：`PASS_FOR_HOSTILE_AUDIT`。
直接投稿：`NO`。
需要新增大规模生物学分析：`NO_BY_DEFAULT`。
需要新增湿实验才能把 claim 升到机制：`YES`，但不属于当前 completion-first 主稿的提交前必需项。
