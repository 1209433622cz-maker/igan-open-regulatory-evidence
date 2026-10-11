# R7A1C1B 下一阶段冻结目标

## 唯一任务

```text
R7A1C1B = HRA008003 exact five-PBC-donor byte execution
```

不新增基因、locus、数据集、healthy control 或终稿图。运行：

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
  '.\2_code\06_intake\r7a1c1\RUN_R7A1C1_HRA008003_TARGET_PANEL_v2.ps1'
```

运行期间保持电脑唤醒和网络稳定。中断后运行同一命令即可继续；已完成供者通过 schema 与技术 QC 校验后会被跳过。

## 合法出口

若 `FCRL3_B_promotion_eligible_donors >= 3` 或 `IL12RB2_NK_promotion_eligible_donors >= 3`：

```text
NEW_PRIMARY_PROJECT = PBC
NEXT_STAGE = R7A2_PBC_MANUSCRIPT_SCALE
```

若两个 target 都失败，或完整数据迫使 called-cell 方法 fail closed 且不能由公开 filtered matrix 独立解决：

```text
PBC_REGULATORY_MAIN = FROZEN_FAIL_OR_HOLD_TECHNICAL
CeD_AUTO_RESUME = NO
NEXT_STAGE = NEW_RESEARCH_ARCHITECTURE_REDESIGN
```

结果文件：

`H:\SCI2\YR1\3_results\05_tissue\R7A1C1\R7A1C1_liver_final_adjudication_v2.json`
