# CMM R7A1C1B1R 执行摘要：v3.2 技术门修复

**日期：2026-09-16**

## 最终判定

R7A1C1B1R 已完成。v3.1 对 HRR1849462 的失败被确认是 coordinate-sorted prefix density 导致的技术假阴性，不是下载、BAM 完整性、tag schema 或生物学阴性。

HRR1849462 已通过：

```text
bytes = 28,323,326,606
MD5 = 79de18396f58543f649f2931d4a067eb
SHA-256 = 42ab19a8fc22ae0d4ce180f08ebc6361989c60ce9227ce601e21718d48cdb3ce
samtools quickcheck = PASS
schema v1.2 = PASS_WITH_WARNING
```

前 5,000,000 records 中虽只有 25 个 `xf bit 8`，但 CB/GN/UB/单基因 GN 完整率均为 1.0。低 prefix density 被保留为 warning，完整文件的 quantitative adequacy 仍由未修改的 full target-panel scan 决定。

前三个 donor 的 summary/receipt 再验证均通过，且 FCRL3-B 与 IL12RB2-NK 均为 3/3 promotion eligible。五供者协议尚未闭环，不能提前宣布 R7A2。

```text
R7A1C1B1R = COMPLETE
V3_2 = READY
FIVE_DONOR_FINAL_RESULT = NOT_TESTED
NEW_PRIMARY_PROJECT = HOLD_PENDING_COMPLETE_5_OF_5_ADJUDICATION
```

唯一下一阶段是 `R7A1C1B2`：使用 v3.2 对现有 HRR1849462 做完整扫描，再处理 HRR1849463，最后执行 exact 5/5 final adjudication。
