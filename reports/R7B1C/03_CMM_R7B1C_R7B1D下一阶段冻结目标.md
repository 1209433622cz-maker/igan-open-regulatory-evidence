# CMM R7B1C：下一阶段冻结目标

## R7B1D — External Molecular/Chromatin Replication and Direction

R7B1B 已完成真实数据双向重分类，R7B1C 已完成真值已知 calibration。下一阶段应执行研究计划书 v2 的外部层，不再扩增 OneK locus/gene/cell。

固定任务：

1. 继承 TenK10K 已冻结的 IL12RB2–NK 与 FCRL3–B cross-resource molecular-QTL evidence；
2. 对 FinnGen immune multiome 的 PBC endpoint、eQTL、caQTL、peak–gene 与 disease-coloc 对象做当前字节级复核；
3. 对 R7B1B stable H4 exemplars 进行预定义 cell mapping、variant/build/allele harmonization；
4. 建立 risk-allele/eQTL-effect direction table；
5. 将不支持、无覆盖与 assay/cell mapping 不充分结果完整保留。

不得新增 post-hoc OneK candidates，不得把 TenK 复用同一 PBC GWAS 写成 independent disease replication，不得在外部层完成前重写整篇 manuscript。

```text
R7B1C = COMPLETE
GRID_ROWS = 486/486
REPLICATES = 486000/486000
MATCHED_FIT_FAILURES = 0
MATCHED_NONCONVERGED = 0
INDEPENDENT_QA = 21/21 PASS
FALSE_H4_REDUCTION = DEMONSTRATED_WITH_RECOVERY_COST
GENERAL_METHOD_SUPERIORITY = NOT_DEMONSTRATED
PF10_TO_PF50_LD_MISMATCH_HARM = NOT_DEMONSTRATED_IN_TWO_TEMPLATES
MANUSCRIPT_REWRITE = HOLD
NEXT = R7B1D_EXTERNAL_MOLECULAR_CHROMATIN_REPLICATION_AND_DIRECTION
PUBLIC_GITHUB_SYNC = PENDING
```
