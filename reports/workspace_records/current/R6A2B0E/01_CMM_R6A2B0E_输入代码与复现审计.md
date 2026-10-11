# R6A2B0E 输入、代码与复现审计

日期：2026-09-14

## 接收包

- 文件：`CMM_R6A2B0_IgAN_8Locus_BoundedExpansion_ExecutionPack_2026-09-14.zip`
- 字节：67,482
- SHA-256：`67e8efe94e74f92dfcc2a1e91f94246a5c3bcd0fadbcc66c03f72619b3be5620`
- ZIP CRC：PASS
- 内部 checksum：30/30 PASS
- 外部详细行动记录 SHA-256：`3a11f7a55cb51013632eae214fb84bf2cc0af65b0d822cfc7af0fedb77d8b83e`

## 冻结范围

- 8 个位点；
- 183 个唯一 locus×cell×gene；
- 43 个唯一 OneK1K chr×cell parquet；
- combined 为 primary，European-only/Asian-only 为 supportive；
- 最大 549 次 smoke tests；
- 不允许事后添加基因、细胞或位点；
- source-LD 只允许实际 trigger 组合。

静态检查结果：183 行全部唯一，8/8 位点均在 lead manifest，43/43 chr×cell 均覆盖组合全集，所有细胞 sample list、OneK1K archive 和 PLINK BED/BIM/FAM 均存在。8 个 Python 文件最终全部通过 `py_compile`，ABF synthetic test 通过。

## 实跑输入门

| 门 | 结果 |
|---|---|
| OneK1K archive bytes | 10,344,009,571/10,344,009,571 |
| OneK1K MD5 | `e42239480f40abd21f221c0d77c82cc3` |
| OneK1K SHA-256 | `63b980c82c234268183205a9cf3c9da96ead1440d7b4b4586652f38ea18039ea` |
| required/extracted chr×cell | 43/43 |
| testable combinations | 183/183 |
| QTL rows | 449,282 |
| GWAS windows | 24/24 |
| combined windows with ≥500 eligible SNPs | 8/8 |

## 本轮发现并修复的执行问题

1. runner 原路径写成 `tools/R-4.6.1/bin/Rscript.exe`，真实路径为 `tools/R/R-4.6.1/bin/Rscript.exe`。已修复。
2. 官方 R 复核会打印 1,647 组常规 posterior 表，造成日志洪泛。已用 `capture.output` 抑制例行打印；数值与参数未改变。
3. 初始 source-LD 脚本只保存相关矩阵，不能复算协变量残差 LD。现同时保存 active donor 顺序、标准化 A1 dosage、二进制相关矩阵和 LD 行序号。
4. 新增 PF10/PF50 covariate-residual LD 构建器。首次写 JSON 时遇到 `numpy.bool_` 编码问题，已显式转换为 Python `bool`；矩阵重新生成并通过全部 QC。
5. 新增 targeted SuSiE-RSS、signal-specific coloc 和机器裁决脚本。

## 数值复现

R 环境：R 4.6.1、`coloc 5.2.3`、`susieR 0.14.2`。官方 R 共运行 1,647 次后验计算，对应 549 个比较的三档 `p12`。Python/官方 R 合并 549/549，最大后验绝对差：

| 后验 | 最大绝对差 |
|---|---:|
| H0 | 1.61e-15 |
| H1 | 3.55e-15 |
| H2 | 3.77e-14 |
| H3 | 5.11e-15 |
| H4 | 1.50e-15 |

冻结容差为 `1e-10`，因此 PASS。

## Source-LD 与残差化门

| 组合 | donors | variants | PF10 rank/columns | PF50 rank/columns | gate |
|---|---:|---:|---:|---:|---|
| SIPA1 × CD8_ET | 980 | 2,258 | 19/19 | 59/59 | PASS |
| EIF4A1 × CD4_NC | 980 | 3,519 | 19/19 | 59/59 | PASS |
| SAT2 × B_IN | 975 | 3,428 | 19/19 | 59/59 | PASS |

三套 PF10/PF50 残差矩阵均为有限值、完全对称、对角线为 1，dual space 中不存在低于 `−1e-8` 的负特征值。SuSiE 读取 float32 时固定加入 `1e-4` ridge 并重新标准化对角线，参数写入结果表。

