# R7A1C1B1R Schema v1.2 设计与回归测试

## 设计修复

v1.2 将两个问题分开：

1. schema 是否可解释；
2. 完整文件的 molecule/cell/lineage/target 数量是否充分。

schema 门继续 fail closed：无法读取、零 `xf bit 8`、缺失 CB/GN/UB、低单基因 GN 比例、缺失 STAR/annotate_reads 或 coordinate-sort header 均失败。只要存在结构完整的 molecule representative，prefix 中少于 1,000 个只记为 warning。

quantitative adequacy 继续由原始 `02_hra_bam_target_panel_v2.py` 完整扫描决定。该脚本、最终 adjudicator、v3.1 和旧 schema 文件的 SHA-256 均与上一轮冻结版本一致。

## 回归测试

| 场景 | 期望 | 结果 |
|---|---|---|
| prefix ≥1,000 xf8 | PASS | PASS |
| 25 xf8 且 tag 完整 | PASS_WITH_WARNING | PASS |
| 0 xf8 | FAIL | PASS |
| CB/GN/UB 各有缺失 | FAIL | PASS |
| 截断 BAM | FAIL | PASS |
| 合法 summary + receipt 恢复 | PASS | PASS |

总计 `6/6 PASS`。

## 真实 BAM 验证

HRR1849462：

```text
records inspected = 5,000,000
xf8 = 25
CB/GN/UB/unambiguous GN = 1.0/1.0/1.0/1.0
xf8 density per million = 5.0
status = PASS_WITH_WARNING
```

该结果只解除错误的 schema 阻塞，不构成 donor biology 结论。
