# R7A2A3 下一阶段冻结目标：R7A2A4 Hostile Manuscript Audit

## 冻结决策

R7A2A3 已完成 scientific draft v1。下一阶段不运行新的位点分析，而是审计当前稿件是否忠实呈现冻结证据。

```text
NEXT_STAGE = R7A2A4_HOSTILE_MANUSCRIPT_AUDIT
NEW_LOCUS_GENE_CELL = PROHIBITED
NEW_TISSUE_RECLUSTERING = HOLD
NEW_BIOLOGICAL_ANALYSIS = NO_BY_DEFAULT
```

## R7A2A4 的五个核心目标

1. **Clause-level claim audit**：标题、摘要、结果、讨论、结论和图例逐句连接 claim ledger 与源表。
2. **Current novelty audit**：重新检索截至执行日的 primary literature，尤其是 PBC/FCRL3/IL12RB2/sc-eQTL/colocalization。
3. **Hostile reviewer simulation**：分别从 statistical genetics 与 liver single-cell biology 角度出具 major/minor comments，并逐条处理。
4. **Figure repair**：修复 Figure 1 重叠、Figure 3 低先验视觉语义，并核验 Figure 2/4 不混淆 multi-signal 与 single-causal replication。
5. **Submission blocker ledger**：只把真正需要作者输入或目标期刊决定的项目留为 blocker。

## 出口

若 claim、数字、引用、图形语义全部 PASS，则进入：

```text
R7A2A5_TARGET_JOURNAL_AND_SUBMISSION_FORMAT
```

若核心 claim 失败，则回到有边界的 R7A2A3 文本/图修订。失败不能触发新位点救援。
