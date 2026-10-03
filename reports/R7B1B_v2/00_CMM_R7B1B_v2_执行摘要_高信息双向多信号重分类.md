# CMM R7B1B v2 执行摘要：高信息子集的双向多信号重分类

日期：2026-10-03

R7B1B v2 已完成真实字节执行。原始 184 个 trigger 保持为 primary verification cohort；455 个 H3 comparisons 与 3 个 borderline cases 构成预结果冻结的对称 falsification/calibration layer。所有 642 个比较均使用 GJOKA study-matched disease LD 与 OneK1K cell-specific PF10/PF50 source-matched QTL LD。

```text
R7B1B_v2 = COMPLETE
HIGH_INFORMATION_COMPARISONS = 642/642
PRIMARY_184 = 184/184
H3_RESCUE = 455/455
BORDERLINE_CALIBRATION = 3/3
GJOKA_MEMBERS = 94/94
SOURCE_LD_BLOCKS = 286/286
QTL_SUMMARIES = 1284/1284
INDEPENDENT_QA = 19/19 PASS
QC_FAILURE = 0

CLAIM_CEILING =
PBC-wide ABF screening followed by source-matched multi-signal
reclassification of the prespecified high-information H3/H4 subset

MANUSCRIPT_REWRITE = HOLD
SIMULATION_CALIBRATION = GO_NEXT
NEW_GENE_CELL_LOCUS_FISHING = NO
```

## 核心结果

- PF10 主终裁中，稳定 H4 为 **92/642（14.3%）**，稳定 H3 为 **428/642（66.7%）**。
- 双向重分类中，**H3→H4 为 8**，**H4→H3 为 4**。这两个方向现在使用同一套预冻结门，可以直接估计 single-causal screening 的非对称误分类负担。
- PF10 与 PF50 被标记为方向敏感的比较为 **4**；PF50 仍是协变量模型敏感性，不替代 PF10 primary adjudication。
- 技术 QC failure 为 **0**。所有没有 credible set/signal pair 的比较均按 `UNINFORMATIVE` 报告，没有被改写成阴性或技术失败。

### 原始 184 primary cohort

| 判定 | n | 比例 |
|---|---:|---:|
| `STABLE_H4` | 78 | 42.4% |
| `AMBIGUITY_REMAINS_MODEL_SENSITIVE` | 46 | 25.0% |
| `H4_TO_UNINFORMATIVE` | 24 | 13.0% |
| `AMBIGUITY_TO_H3` | 15 | 8.2% |
| `AMBIGUITY_TO_UNINFORMATIVE` | 6 | 3.3% |
| `H4_TO_MODEL_SENSITIVE` | 6 | 3.3% |
| `AMBIGUITY_TO_H4` | 5 | 2.7% |
| `H4_TO_H3` | 4 | 2.2% |

### 455 个 H3 rescue/falsification cohort

| 判定 | n | 比例 |
|---|---:|---:|
| `STABLE_H3` | 409 | 89.9% |
| `H3_TO_UNINFORMATIVE` | 31 | 6.8% |
| `H3_TO_H4` | 8 | 1.8% |
| `H3_TO_MODEL_SENSITIVE` | 7 | 1.5% |

## 结论边界

本轮支持的是“PBC-wide single-causal screen + 冻结高信息子集的 source-matched multi-signal reclassification”。剩余低信息 comparisons 没有全部运行 SuSiE，因此仍不得写成全部 PBC locus–gene–cell combinations 的多信号 landscape。

下一阶段进入 R7B1C simulation/calibration。目的不是制造更多 H4，而是在已知真值下量化 false H4、H3→H4 recovery、LD mismatch distortion、credible-set coverage 与 convergence。稿件重写继续 HOLD，直到 simulation 通过。
