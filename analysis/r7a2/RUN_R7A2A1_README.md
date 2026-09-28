# R7A2A1 本机执行说明

目标：使用与 PBC 五供者完全相同的冻结算法，处理 HRA008003 的五个肝血管瘤非病变肝组织对照；完成后按供者单位计算 FCRL3-B 与 IL12RB2-NK 的 5 vs 5 支持性比较。

先运行轻量预检：

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
  '.\2_code\06_intake\r7a2\RUN_R7A2A1_HRA008003_CONTROL_TARGET_PANEL.ps1' `
  -PreflightOnly
```

预检应输出 `PASS_R7A2A0_PREFLIGHT_ONLY`。正式运行：

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
  '.\2_code\06_intake\r7a2\RUN_R7A2A1_HRA008003_CONTROL_TARGET_PANEL.ps1'
```

五个对照 BAM 合计 134,657,112,757 bytes（约 125.4 GiB）。脚本逐供者下载、校验、完整扫描并在 compact summary/receipt 通过后删除该 BAM，因此不要求同时保留五个 BAM。中断后重复同一命令即可续跑。

最终结果：

```text
H:\SCI2\YR1\3_results\05_tissue\R7A2A1_control\PBC_vs_control_target_panel.json
H:\SCI2\YR1\3_results\05_tissue\R7A2A1_control\PBC_vs_control_target_panel.tsv
```

解释边界：比较以 donor 为统计单位，但 lineage 来自冻结 marker panel；可作为组织支持性证据，不能替代完整 scRNA-seq QC、重聚类和 donor-by-cell-type pseudobulk。
