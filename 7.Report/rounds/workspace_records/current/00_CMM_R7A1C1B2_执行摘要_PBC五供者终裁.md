# CMM R7A1C1B2 执行摘要：PBC 五供者终裁

**复核完成日期：2026-09-28**

**五供者原始运行完成：2026-09-17**

## 最终判定

```text
R7A1C1B2 = COMPLETE
HRA008003_PBC_LIVER_TECHNICAL_QC = PASS_5_OF_5
FCRL3_B_PROMOTION_ELIGIBLE = 5_OF_5
IL12RB2_NK_PROMOTION_ELIGIBLE = 5_OF_5
INDEPENDENT_QA = PASS_8_OF_8
BAM_CACHE_AFTER_VALIDATED_DELETION = EMPTY

PBC_PRIMARY_PROJECT = PROMOTED_GO
R7A2_MANUSCRIPT_SCALE = GO
```

本轮完成了 HRR1849462 与 HRR1849463 的真实完整扫描，并把此前三个供者与新完成的两个供者放回同一个冻结 adjudicator 中终裁。正式结果与独立重算逐字段一致：两个预冻结 target-lineage pair 均在五个 PBC 肝组织供者中通过。

| run | called cells | B gate | NK gate | FCRL3 B cells / UMI | IL12RB2 NK cells / UMI |
|---|---:|---:|---:|---:|---:|
| HRR1849459 | 5,447 | 472 | 1,910 | 12 / 17 | 68 / 70 |
| HRR1849460 | 3,468 | 1,280 | 806 | 81 / 148 | 25 / 26 |
| HRR1849461 | 5,666 | 782 | 2,661 | 33 / 45 | 49 / 53 |
| HRR1849462 | 2,981 | 829 | 682 | 39 / 89 | 30 / 31 |
| HRR1849463 | 6,247 | 698 | 2,860 | 34 / 58 | 183 / 209 |

五供者合计扫描 2,024,279,500 条 alignment records 和 284,941,671 条 molecule-representative records，获得 23,809 个 called cells。FCRL3 在 B gate 中共有 199 个阳性细胞、357 UMI；IL12RB2 在 NK gate 中共有 355 个阳性细胞、389 UMI。

这一结果完成的是疾病组织 detectability 与预冻结谱系定位。它不能单独写成病例–对照差异表达，也不能证明肝组织表达介导了遗传效应。

## 下一阶段

R7A2A0 的对照来源和执行链已经同时完成预验收。下一步是 `R7A2A1`：用完全相同的冻结算法处理 `HRR1849454–HRR1849458` 五个非病变肝组织对照，再进行 exact 5 vs 5 donor-level 支持性比较。
