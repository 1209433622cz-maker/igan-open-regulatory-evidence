# CMM R5A1：R5A2 下一阶段冻结目标

日期：2026-09-13  
下一阶段：`R5A2_MG_BOUNDED_THREE_LOCUS_PILOT`

## 当前状态拆分

```text
INPUT_ACQUISITION = GO
INFERENTIAL_ANALYSIS = HOLD
TISSUE_SCALE_UP = HOLD
MANUSCRIPT_DRAFT = HOLD
```

HOLD 的解除条件是：OneK1K genotype、本地 full OneK1K eQTL 和 full TenK10K eQTL 的 byte count 与 checksum 全部通过，并且 genotype 的 ZIP、BED/BIM/FAM、980 donors 与 build 验收通过。四个 lead 的存在性和每个区域的共同变异/LD proxy 覆盖须分别裁定；因 OneK1K 只含 MAF>0.05，低频 rs7596255 缺失并不等于整个 archive 失败。

## R5A2 只做四条有界链

| 职责 | 区域 | 目标 |
|---|---|---|
| Primary | chr5 rs6861227 | TNIP1 与 7 个跨资源竞争基因的 disease–eQTL shared-signal 检验 |
| Secondary | chr2 rs7596255 | 检验 EOMG/LOMG 方向翻转是否与 SOS1/DHX57/GALM/SRSF7 调控信号有关 |
| Secondary | chr18 rs7239261 | 检验 LOMG 信号与 TNFRSF11A/PIGN/ZCCHC2 的关系 |
| Positive control | chr1 rs2476601 | 验证共享亚型效应与区域流程的稳定性 |

不进行全基因组无边界扩张，不先跑完整 GEO，不先写因果故事。

## 执行顺序与验收

1. **传输门**：续传三个公共文件并核对冻结 MD5；
2. **结构门**：确认文件内部结构、样本数、build、变异 ID 与四个 lead；
3. **区域提取**：只提取三个主区域及 chr1 正控，记录完整 variant coverage；
4. **harmonization**：统一 GRCh37/38、REF/ALT、effect allele，剔除不可消解的回文位点；
5. **LD**：从 OneK1K genotype 生成 QTL-side source-aware LD，并运行 allele/LD 一致性 QC；
6. **信号分析**：单信号条件满足时 coloc.abf，多信号时条件化或 SuSiE-RSS；
7. **复制**：TenK10K 检查 gene、cell、方向和 credible set；
8. **组织验证**：只对通过 molecular gate 的链做 donor-level 单细胞验证。

## 下一轮判定

- 至少一个区域完整通过：`GO_MECHANISTIC_FOLLOWUP`；
- 方向一致但 LD、覆盖或共享信号不充分：`HOLD_AMBIGUOUS`；
- chr5 在充分覆盖下失败：转 chr2/chr18，不救 TNIP1；
- 三个区域均在充分覆盖下失败：`NO_GO_MG_MAIN`，触发 IgAN Plan B。

## 用户本地运行入口

```powershell
Set-Location H:\SCI2\YR1
pwsh -File .\2_code\06_intake\mg_r5a2\RUN_R5A1_TRANSFER_AND_R5A2_LARGE_INPUTS.ps1 -Mode GenotypeOnly -Concurrency 2
```

genotype 完成后再运行全量模式：

```powershell
pwsh -File .\2_code\06_intake\mg_r5a2\RUN_R5A1_TRANSFER_AND_R5A2_LARGE_INPUTS.ps1 -Mode All -Concurrency 2
```

脚本可重复运行并保留断点；Zenodo 504 时稍后重跑。全量模式建议预留至少 60 GB 磁盘。
