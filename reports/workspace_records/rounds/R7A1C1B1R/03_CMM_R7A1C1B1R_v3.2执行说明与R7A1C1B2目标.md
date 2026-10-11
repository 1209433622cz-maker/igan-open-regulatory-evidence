# R7A1C1B1R v3.2 执行说明与 R7A1C1B2 目标

## 一键续跑

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
  '.\2_code\06_intake\r7a1c1\RUN_R7A1C1_HRA008003_TARGET_PANEL_v3_2.ps1'
```

v3.2 将：

1. 验证并跳过 HRR1849459–61；
2. 复用现有 HRR1849462 BAM，不重新下载；
3. 重验 bytes/MD5/SHA、quickcheck 与 schema v1.2；
4. 对 HRR1849462 执行完整单遍扫描；
5. 成功写入 summary 和 receipt 后删除其 BAM；
6. 下载并分析 HRR1849463；
7. exact 5/5 summary 完成后生成最终 adjudication。

中断后重复同一命令。不要删除现有 HRR1849462 BAM、`.part`、summary、receipt 或 audit JSON。

最终文件：

```text
H:\SCI2\YR1\3_results\05_tissue\R7A1C1\R7A1C1_liver_final_adjudication_v2.json
```

## R7A1C1B2 终裁出口

- promotion gate PASS：进入 `R7A2_PBC_MANUSCRIPT_SCALE`；
- 五 donor 技术全部 PASS 但 promotion gate FAIL：冻结 PBC regulatory-main；
- 任一 donor 技术失败：保持 HOLD，不能记为生物学阴性；
- CeD 不自动恢复。
