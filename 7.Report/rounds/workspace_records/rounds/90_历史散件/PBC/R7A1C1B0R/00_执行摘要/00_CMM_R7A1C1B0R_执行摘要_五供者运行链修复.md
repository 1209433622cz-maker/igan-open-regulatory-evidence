# CMM R7A1C1B0R 执行摘要：五供者运行链修复

**日期：2026-09-15**

```text
R7A1C1B0_INPUT = PASS_INTEGRITY_17_OF_17
R7A1C1B0_ORIGINAL_V3 = INVALID_FOR_FULL_EXECUTION
LIGHTWEIGHT_SUPPLEMENT_BYPASS = FAIL_NO_DONOR_TARGET_MATRIX
R7A1C1B0R_V3_1 = PASS_PREFLIGHT_AND_REAL_BAM_PREFIX_TEST

TENK_REPLICATION = PASS_2_OF_2
HRA_FIVE_DONOR_RESULT = NOT_TESTED
NEW_PRIMARY_PROJECT = HOLD
NEXT = R7A1C1B_FIVE_DONOR_BYTE_EXECUTION_V3_1
```

R7A1C1B0 发布包外部 SHA、ZIP CRC 和内部 17/17 checksums 均通过，但其中的 v3 runner 存在三个会影响真实执行的缺陷：最终 adjudicator 变量被错误赋值为三个路径；coordinate-sorted BAM 固定前 500,000 records 的 schema test 会在真实前缀上仅看到 15 个 `xf bit 8` 而假失败；断点复用允许 summary 在缺少匹配 byte/MD5/SHA receipt 时被接受。

本轮已修复为 v3.1。真实 HRR1849459 64 MiB 前缀测试显示，自适应读至 649,995 records 时正好取得 1,000 个 `xf bit 8` molecule representatives，CB/GN/UB 与 unambiguous GN 比例均为 1.0，schema PASS。

轻量补充表也已实际执行。2.59 MB Supplementary Data 只有两条人肝 FCRL3 pooled B-cell marker 命中；一条 IL12RB2 命中来自小鼠肝；16.95 MB Source Data 没有 target 命中；两者 donor ID 均为 0。因此公开表不能重建 `donor × lineage × target`，BAM 执行仍是唯一合法下一步。
