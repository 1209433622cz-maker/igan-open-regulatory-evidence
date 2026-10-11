# CMM R7A1C1B2：五供者独立复核与数据清理审计

**复核完成日期：2026-09-28**

**五供者原始运行完成：2026-09-17**

## 1. 身份闭环

五个 run 的 summary、called-cell table、hash file、resume validation 与 receipt 均存在且一一对应。receipt 的 observed MD5 与 provider MD5 5/5 一致，summary SHA-256 与 hash/receipt 5/5 一致。

| run | bytes | SHA-256 | receipt | BAM 删除 |
|---|---:|---|---|---|
| HRR1849459 | 26,041,030,352 | `fab7a10a…11e722` | PASS | True |
| HRR1849460 | 33,332,591,265 | `963b23cd…56bc6` | PASS | True |
| HRR1849461 | 28,873,594,843 | `6d9e0560…374f7d` | PASS | True |
| HRR1849462 | 28,323,326,606 | `42ab19a8…db3ce` | PASS | True |
| HRR1849463 | 35,917,954,133 | `8e30c76d…56c293` | PASS | True |

## 2. v3.2 技术门

HRR1849462 前 5,000,000 records 中仅 25 个 `xf bit 8`，但 CB/GN/UB/单基因 GN 完整率均为 1.0，因此按冻结规则为 `PASS_WITH_WARNING`。完整扫描随后获得 63,090,187 条 molecule records，证明旧固定前缀数量门会造成技术假阴性。

HRR1849463 在 2,078,203 records 时获得 1,000 个 `xf bit 8`，标签完整率均为 1.0，schema 为 `PASS`；完整扫描获得 59,840,037 条 molecule records。

## 3. 独立终裁

再次运行冻结的 `03_adjudicate_HRA008003_liver_gate_v2.py`，写入独立 audit 路径。独立 JSON 与正式 JSON 完全相同：

```text
technical_QC_donors = 5
FCRL3_B_primary_positive_donors = 5
IL12RB2_NK_primary_positive_donors = 5
FCRL3_B_promotion_eligible_donors = 5
IL12RB2_NK_promotion_eligible_donors = 5
primary_gate = PASS
promotion_gate = PASS
next_stage = GO_R7A2_PBC_MANUSCRIPT_SCALE
```

独立 QA 共 8 项，8/8 PASS。

## 4. 清理安全性

每个 BAM 都在 compact summary 与 receipt 身份复核后删除。`1_data/scrna/PBC/HRA008003/bam` 当前没有 `.bam`、`.part` 或 `.aria2` 残留。called-cell gzip、summary、hash、schema audit、resume validation 和最终 adjudication 均保留。

该清理没有删除复算入口：manifest 保存 provider URL、bytes 和 MD5，receipt 保存本地 SHA-256，runner 支持逐供者重新获取。
