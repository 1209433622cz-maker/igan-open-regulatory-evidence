# R7A1C1B 五供者原始字节执行协议 v3.1

**冻结日期：2026-09-15**

## 冻结状态

```text
TENK_REPLICATION_GATE = PASS_2_OF_2
LIGHTWEIGHT_SUPPLEMENT_BYPASS = FAIL_NO_DONOR_TARGET_MATRIX
HRA_FIVE_DONOR_OUTCOME = NOT_TESTED
NEW_PRIMARY_PROJECT = HOLD
```

本协议只修正 R7A1C1B0 v3 的工程错误。`R7A1C1_HRA008003_donor_target_detectability_v2.md` 中的 called-cell、谱系、target UMI 和 ≥3/5 donor 生物学阈值完全不变。

## 唯一输入

HRA008003 五个 PBC liver BAM：`HRR1849459–HRR1849463`，总计 152,488,497,199 bytes。运行 manifest 必须通过 exact run、bytes、MD5、HTTPS host/path 和 total-byte gate。

## 每供者顺序

1. aria2 断点下载单个 BAM；
2. exact bytes；
3. 单遍计算 MD5 与 SHA-256，MD5 必须等于 provider 值；
4. `samtools quickcheck -v`；
5. coordinate-sorted adaptive prefix schema audit：至少 500,000 records，继续扫描直到 `xf bit 8` records ≥1,000，上限 5,000,000；
6. 运行 v2 单遍完整 BAM called-cell/target panel；
7. summary 与 receipt 写入并验证后，默认删除该供者 BAM；
8. 下一供者。

断点复用只有在 summary 的 run/schema/bytes/SHA 和 receipt 的 provider MD5/observed MD5/bytes/SHA 完全一致时才允许。孤立 summary 不允许被当成已验收供者。

## 最终裁决

仅当五个 donor summary 全部存在且 technical QC 为 PASS 时运行单一路径 adjudicator：

`03_adjudicate_HRA008003_liver_gate_v2.py`

若 `FCRL3_B_promotion_eligible_donors ≥3` 或 `IL12RB2_NK_promotion_eligible_donors ≥3`，则 `GO_R7A2_PBC_MANUSCRIPT_SCALE`；否则冻结 PBC regulatory-main，不自动恢复 CeD。

## 执行

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
  '.\2_code\06_intake\r7a1c1\RUN_R7A1C1_HRA008003_TARGET_PANEL_v3_1.ps1'
```

中断后运行同一命令。不要移动已生成的 summary、receipt 或 `.bam.part/.aria2` 文件。
