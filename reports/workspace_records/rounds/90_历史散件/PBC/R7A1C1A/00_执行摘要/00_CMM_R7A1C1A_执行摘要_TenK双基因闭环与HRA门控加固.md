# CMM R7A1C1A 执行摘要：TenK 双基因闭环与 HRA 门控加固

**日期：2026-09-15**

## 最终判定

```text
R7A1C0_INPUT_PACKAGE = PASS_INTEGRITY
IL12RB2_TENK_NK = PASS_FULL_PBC_INTERSECTION
FCRL3_TENK_B_INTERMEDIATE = PASS_FORMAL_ABF_SMOKE_AND_EXACT_SOURCE_CS1_IDENTITY
TENK_REPLICATION_GATE = PASS_2_OF_2

R7A1C0_HRA_V1_RUNNER = INVALID_FOR_FINAL_ADJUDICATION
R7A1C1_HRA_V2 = READY_OUTCOME_BLIND
HRA_FIVE_DONOR_RESULT = NOT_TESTED

NEW_PRIMARY_PROJECT = HOLD
NEXT_STAGE = R7A1C1B_FIVE_DONOR_BYTE_EXECUTION
```

PBC 的遗传/QTL 跨资源复制证据已从“一条链通过、另一条链仅 source-CS identity”升级为两个预冻结基因都完成正式复核。`IL12RB2 × NK` 在完整 PBC–TenK 精确交集中有 396 个变异；默认 `PP.H4=0.99754`，低共享先验下 `H4/(H3+H4)=0.97597`。`FCRL3 × B_intermediate` 的完整公开 TenK 成员通过 2,392,868,507 解压字节、CRC32 `3c73842b` 和 843 行精确基因提取；343 个疾病/QTL 精确 allele overlap 的默认 `PP.H4=0.99156`，低共享先验下 H4 比例 `0.92171`。

FCRL3 的 ABF 共享权重集中在 source SuSiE CS1：`rs7528684`、`rs945635`、`rs3761959`、`rs2210913` 合计接近 1；其中预先冻结的 `rs3761959 / 1:157699488:C:T` 同时存在于疾病/QTL 精确交集和 TenK source CS1。由于 TenK source 仍有多个 credible sets，ABF 只作为单因果 smoke 证据，不能替代后续需要时的 signal-specific 分解。

本轮没有直接运行 152,488,497,199 字节的五个 HRA BAM，因为独立代码审计发现 R7A1C0 v1 把带 `CB` 的 barcode 当成 called cells。Cell Ranger BAM 中 `CB` 并不排除背景 barcode；v1 还没有按 `xf bit 8` 选择 molecule-representative records。若直接执行会把 ambient RNA 风险带入 ≥3/5 donor 判定。

修订后的 v2 已在结果盲态冻结：完整 BAM 单遍扫描、`xf bit 8`、order-of-magnitude called-cell、2500–7500 cells 与 median UMI ≥500 技术门、谱系细胞数 ≥10、每供者 target 至少 3 UMIs 且分布于至少 2 cells。代码语法、PowerShell parser 和五供者合成裁决均已 PASS。

下一阶段只允许执行五个 PBC liver donors。若 `FCRL3–B` 或 `IL12RB2–NK` 的稳健检测达到 ≥3/5，进入 R7A2；否则冻结 PBC regulatory-main，且不自动恢复 CeD。
