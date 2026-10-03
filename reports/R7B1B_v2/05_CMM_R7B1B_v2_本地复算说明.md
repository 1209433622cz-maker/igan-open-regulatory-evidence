# R7B1B v2 本地复算说明

在 PowerShell 7 中运行：

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
'.\2_code\06_intake\r7b1\RUN_R7B1B_V2_HIGH_INFORMATION_MULTISIGNAL.ps1' `
-Workers 2
```

已有 94 个 GJOKA 文件和 dual-model input 时可使用：

```powershell
pwsh -File `
'.\2_code\06_intake\r7b1\RUN_R7B1B_V2_HIGH_INFORMATION_MULTISIGNAL.ps1' `
-Workers 2 -SkipGJOKAIntake -SkipInputBuild
```

程序按 comparison/locus checkpoint，可安全重跑。当前机器内存压力较高时不要将 `Workers` 提高到 3 以上。
