# R7B1A：R7B1B 下一阶段冻结目标与本地运行说明

## 冻结目标

```text
R7B1B = EXACT_184_TRIGGER_SOURCE_MATCHED_MULTISIGNAL

comparisons = 184
loci = 25
genes = 49
cells = 14
unique cell-locus LD blocks = 120
required GJOKA members = 50
```

Trigger set SHA-256：

`bac35fe7572a336ceedcf60a19a3d4f7f8c3cd97337ebd34a2d08e5360cb1f0e`

R7B1B 不允许再按默认 H4、审慎先验、source-cell q、基因知名度或预期发表价值删除比较。所有 184 项都必须获得终局或明确 QC failure。

## 大文件入口

25 个 loci 对应 50 个 GJOKA members：

```text
remote compressed transfer  357,742,541 bytes
local uncompressed members 1,080,148,372 bytes
```

已生成 range-download runner。它只下载 exact trigger loci，不下载 1.18 GB 完整 ZIP；逐 member 核对远端 inventory byte count、CRC32，并计算本地 SHA-256。

在本机运行：

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
'.\2_code\06_intake\r7b1\DOWNLOAD_R7B1B_GJOKA_TRIGGER_MEMBERS.ps1'
```

若网络中断，可重复同一命令；已存在且 byte/CRC 通过的成员会复用。

重点输出：

```text
H:\SCI2\YR1\1_data\study_inputs\PBC_GJOKA\R7B1B\
H:\SCI2\YR1\3_results\00_audit\R7B1B\R7B1B_GJOKA_member_receipts.tsv
H:\SCI2\YR1\3_results\00_audit\R7B1B\R7B1B_GJOKA_intake_state.json
```

## 下载后的计算顺序

1. 对 120 个 cell–locus blocks 构建 current PF10 residualized LD；
2. 为 exact 184 comparisons 重算 corrected PF50 beta/SE/z，并构建 PF50 residualized LD；
3. GJOKA disease z/LD allele/order harmonization；
4. SuSiE-RSS 与 z–LD/kriging/CS purity diagnostics；
5. coloc.susie 全 signal-pair 输出；
6. 184/184 五类 reclassification；
7. 独立 QA 与 G4 判定。

只有 R7B1B 完成，才能进入研究计划书 v2 的 simulation/calibration。当前不启动新稿、FinnGen 扩展或图件重构。
