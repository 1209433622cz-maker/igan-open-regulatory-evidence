# CMM R6A3A0 执行摘要：IgAN completion-design gate 执行闭环

**日期：2026-09-14**

## 当前判定

```text
UPSTREAM_R6A2C1D = PASS_INTEGRITY
IGAN_IMMUNE_CISEQTL_FULL24 = FROZEN_NO_GO

R6A3A0 = COMPLETE_EXECUTION_PREPARATION
TRACK_A_PUBLIC_PQTL_SOURCE = PASS_OPEN_DATA_SOURCE
TRACK_A_SIGNAL_RESULT = NOT_TESTED_IN_CURRENT_SANDBOX
TRACK_B_GSE127136_SOURCE = PASS_OPEN_DATA_SOURCE
TRACK_B_DONOR_LEVEL_RESULT = NOT_TESTED_IN_CURRENT_SANDBOX

MANUSCRIPT_SCALE_ANALYSIS = HOLD
NEXT = R6A3A1_LOCAL_TRUE_BYTE_EXECUTION
```

当前附件不包含用户本机规范 `1_data` 的 pQTL/GSE127136 大字节，因此本轮没有伪造 Track A/B 科学结果。

## 上游独立完整性

- R6A2C1D ZIP SHA-256: `72eb4634aa7ace502486706c9849c48c1518e89879dc352e6336a3b977f288a2`
- R6A2C1D ZIP CRC: `PASS`
- R6A2C1D entries: `46`
- YR1 snapshot SHA-256: `4f991ba240c3fd781333359567d55c09d53cdeb0aedb4b67d933bb42afbf8a05`
- YR1 ZIP CRC: `PASS`
- YR1 entries: `2427`

## Track A 已冻结公共源

eQTL Catalogue `QTS000035 / QTD000584`：
- Sun 2018 INTERVAL plasma；
- 3,301 donors；
- aptamer assay；
- GRCh38；
- ALT = QTL effect allele；
- full nominal sumstats ≈698 MB；
- permutation ≈128 KB；
- source SuSiE credible sets ≈1.0 MB；
- SuSiE LBF ≈438 MB。

执行策略是小文件先筛11个冻结蛋白，只有存在测量/source signal才触发大文件和 signal-level coloc。

## Track B

GSE127136 已冻结：
- 13 IgAN kidney donors；
- 6 kidney-cancer paracancer controls；
- processed count matrix 15,703,242 bytes；
- frozen SHA-256 `89c3580ad550ae5df9e736bba97101f0ae02e724201b61d2e1f5fa4247dbce40`；
- donor-level aggregate ZMIZ1 pseudobulk为primary；
- marker-based cell localization仅secondary/provisional。

## 下一步

将本包 `analysis/r6a3a/` 部署到
`H:\SCI2\YR1\2_code\06_intake\igan_r6a3a\`
并运行统一 runner。只有 Track A 至少一个新增 pQTL shared-signal locus + Track B PASS/INTERPRETABLE 同时成立，才恢复 manuscript-scale。
