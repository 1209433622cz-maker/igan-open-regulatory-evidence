# R7A1C1B1R 冻结协议：HRA008003 五供者执行 v3.2

**冻结日期：2026-09-16**

## 目的

修复 v3.1 将 coordinate-sorted BAM 前缀中的 `xf bit 8` 局部密度误作 schema 充分性门的问题。修复仅改变执行前技术门，不改变完整扫描、细胞调用、lineage adequacy、target detectability 或 ≥3/5 donor 规则。

## 已冻结事实

- HRR1849459、HRR1849460、HRR1849461：完整扫描与 summary/receipt 身份复核通过；
- 三个已完成 donor 的 FCRL3-B 和 IL12RB2-NK 均 promotion eligible；
- HRR1849462：28,323,326,606 bytes，provider MD5 与本地 SHA-256 已通过，`samtools quickcheck=PASS`；
- HRR1849462 的前 5,000,000 records 含 25 个 `xf bit 8`，其 CB/GN/UB/单基因 GN 完整率均为 1.0；
- HRR1849463 尚未下载和分析；
- 五供者最终裁决尚未生成。

## v3.2 schema 门

硬失败：

1. BAM 无法完整读取或 `samtools quickcheck` 失败；
2. provider bytes/MD5 不一致；
3. 抽样中 `xf bit 8=0`；
4. 任一抽样 `xf bit 8` record 缺失/空 CB、GN 或 UB；
5. 单基因 GN 比例低于 0.70；
6. 缺失 STAR、annotate_reads 或 coordinate-sort header。

`0 < xf bit 8 < 1000` 只产生 `LOW_PREFIX_XF8_DENSITY` warning。数量充分性由冻结的 `02_hra_bam_target_panel_v2.py` 完整单遍扫描裁决。

## 完整扫描与生物学门

保持原协议不变：

- 只使用 `xf & 8 != 0` molecule representatives；
- Cell Ranger order-of-magnitude called-cell reconstruction；
- called cells 2,500–7,500，median UMI ≥500；
- B/NK lineage cells 各 ≥10；
- target ≥3 UMI 且分布于 ≥2 lineage cells；
- 同一 target 在 ≥3/5 PBC donors 通过才可 promotion。

## 删除与恢复

- 已完成 donor 必须通过独立 summary/receipt 身份验证才跳过；
- 新 donor 的 summary、bytes、MD5、SHA 和 receipt 再验证通过后才允许删除 BAM；
- HRR1849462 的现有完整 BAM 不重新下载；
- 中断后重复同一 v3.2 命令。

## 唯一下一阶段

`R7A1C1B2_FIVE_DONOR_COMPLETION_AND_FINAL_ADJUDICATION`

只有 exact 5/5 summaries 与 technical QC 全部通过，才执行冻结的 final adjudicator。
