# CMM R4A12FG5：External-LD Strict Gate Audit

## 目的

检验FG4冻结的891个R13 disease↔NK exact variants，是否可由当前归档的1000G EUR503资产建立足够完整的signed LD，从而进入multi-signal adjudication。

## 映射与等位基因

使用 `gwas_rsids` 跨GRCh37/GRCh38定位，随后要求旧reference双等位集合与当前GRCh38 REF/ALT一致，并把503人dosage重新定向到**当前ALT**。

结果：
- target exact variants：891
- 成功映射：329
- coverage：**36.92%**
- 等位基因集合冲突：0（在329个已映射对象内）
- genotype missing：历史R4A9 audit为0

## AF一致性

R13 ALT AF vs EUR503：
- Pearson r = 0.986424
- median |ΔAF| = 0.03498
- P95 |ΔAF| = 0.09603

TenK10K NK ALT AF vs EUR503：
- Pearson r = 0.999059
- median |ΔAF| = 0.00667
- P95 |ΔAF| = 0.03327

这说明已映射329个variant的allele orientation整体合理，但不能说明未映射562个variant可忽略。

## Source-signal coverage

| NK source CS | FG4 exact members | FG4 PIP mass | archived LD members | archived LD PIP mass |
|---|---:|---:|---:|---:|
| CS1 | 11 | 0.73106 | **0** | **0** |
| CS2 | 3 | 0.95485 | **0** | **0** |

Mandatory anchors：
- NK QTL top `rs17129789`：**ABSENT**
- legacy/SSc anchor `rs6662198`：PRESENT
- FinnGen regional lead `rs1954118`：**ABSENT**

因此无论329×329 LD数值多漂亮，都不能用于当前multi-signal adjudication。

## LD数值性质

329×329 signed-r：
- max asymmetry = 2.22e-16
- max diagonal error = 2.22e-16
- min eigenvalue = -3.84e-14
- numerical rank = 111 / 329
- positive-spectrum condition number ≈ 90435.5

矩阵数值上近似PSD，但LD块高度共线；这本身不是失败原因，真正失败来自signal/variant coverage。

## z–LD诊断

| Release/Trait | estimate_s | max |std residual| | >5 |
|---|---:|---:|---:|
| R12 GWAS | 0.00533 | 5.539 | 2 |
| R13 GWAS | 0.00556 | 5.616 | 2 |
| NK QTL | 0.02677 | 4.135 | 0 |

该诊断为独立Python precision-matrix检查，不冒充 `susieR::kriging_rss` 原样输出。R12/R13 disease均出现>5 residual，再次说明当前子集不适合作为正式LD-aware inference输入。

## 决策

> **`FAIL_INPUT_COVERAGE_FOR_MULTISIGNAL`**

解释边界：
- 失败的是**归档的1555旧工程子集**；
- 不是1000G EUR503总体被判不适用；
- 用户本地历史R4A8B raw目录曾有27,067个区域参考变异，下一轮应直接从full regional PLINK reference重建891-variant LD，而不是继续复用1555矩阵。
