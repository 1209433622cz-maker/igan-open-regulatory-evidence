# R7A1C1B v3.1 执行说明与下一目标

## 运行

在 PowerShell 中执行：

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
  '.\2_code\06_intake\r7a1c1\RUN_R7A1C1_HRA008003_TARGET_PANEL_v3_1.ps1'
```

预计网络与计算总耗时约 9–12 小时。保持电脑唤醒和网络稳定。任务按 donor 串行执行；中断后重复同一命令。不要删除 `.bam.part`、`.aria2`、`3_results\05_tissue\R7A1C1` 或 `3_results\00_audit\R7A1C1`。

## 查看状态

```powershell
Get-ChildItem `
  'H:\SCI2\YR1\3_results\05_tissue\R7A1C1' `
  -Filter '*_target_panel_summary.json'

Get-Content `
  'H:\SCI2\YR1\3_results\00_audit\R7A1C1\R7A1C1_HRA008003_receipts_v2.tsv'
```

成功完成后结果：

`H:\SCI2\YR1\3_results\05_tissue\R7A1C1\R7A1C1_liver_final_adjudication_v2.json`

## 下一阶段决策

通过 ≥3/5 donor gate：`NEW_PRIMARY_PROJECT=PBC`，进入 `R7A2_PBC_MANUSCRIPT_SCALE`。失败：冻结 PBC regulatory-main，CeD 不自动恢复。技术 QC fail closed：先解决公开数据处理问题，不能按生物学阴性计数。
