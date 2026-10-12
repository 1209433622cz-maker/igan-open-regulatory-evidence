# CMM R4A9 交付索引

本轮完成 R4A8B reference/LD 独立复核、2019 overall RSS HOLD 复现、2026 SSc 正式数据入口核查、原论文 supplementary appendix 完整审计，以及 SYNGR1 新颖性纠偏。

## 先读

1. `00_CMM_R4A9_执行摘要_独立复核与新颖性纠偏.md`
2. `02_CMM_R4A9_原论文附录复核与SYNGR1新颖性纠偏.md`
3. `03_CMM_R4A9_R4A10任务与冻结验收标准.md`
4. `99_CMM_R4A9_详细行动记录_2026-09-11.md`

## 可复现资产

- `RUN_R4A9.ps1`：在原工作区重跑 reference/LD、RSS、GWAS Catalog access、H6 unit tests 与发布状态验收。
- `independent_reference_ld_audit.py`：PLINK2 第三方剂量/LD 复核。
- `reproduce_rss_gate.R`：susieR RSS 门复算。
- `research/check_ssc_access.py`：官方 GWAS Catalog 入口检查。
- `h6_intake/RUN_H6_INTAKE.ps1`：新 female/male 文件到位后的流式接入。
- `verify_release.py`：验证状态、主张边界、关键数值和报告完整性。
- `package_release.py`：按显式白名单生成 checksum 和轻量发布 ZIP，不打包 1.2 GB reference 或历史附件。

### 重跑先决资产

轻量 ZIP 中的 H6 intake 与其测试可独立运行。完整 `RUN_R4A9.ps1` 还依赖工作区相邻目录：

- `..\R4A8B_IGSR\raw` 与 `..\R4A8B_IGSR\results`：1KG reference、区域 BED/VCF、冻结 z/LD/kriging；
- `..\R4A8\R_library`：本轮使用的 R package library；
- 本机 `D:\bioinfor\python.exe`、R 4.6.0，以及 WSL 中的 PLINK2。

这些大型或机器相关资产未复制进发布 ZIP，因此 ZIP 自身不承诺完整 reference/RSS 重跑。

## 当前状态

`PROJECT=CONDITIONAL_GO_ACCESS_LIMITED_AND_NOVELTY_REFRAMED`

`R4B=HOLD`

`C1_count=null`

下一阶段：`R4A10_H6_SEX_SPECIFIC_INTAKE_AND_EXTENSION_ONLY_GATE`。
