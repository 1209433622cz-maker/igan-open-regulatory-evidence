# R7A1C1B1R 真实运行状态与三供者复核

## 已完成 donor

| donor | technical QC | FCRL3-B positive cells | IL12RB2-NK positive cells | 两目标 promotion eligible | summary/receipt |
|---|---:|---:|---:|---|---|
| HRR1849459 | PASS | 12 | 68 | 是 | PASS |
| HRR1849460 | PASS | 81 | 25 | 是 | PASS |
| HRR1849461 | PASS | 33 | 49 | 是 | PASS |

三个 donor 的 compact summary 均重新与唯一 receipt 核对：run、schema、technical QC、bytes、provider MD5、observed MD5 与 SHA-256 全部一致。它们可安全继承，不重新下载、不重新扫描。

## HRR1849462

本地 BAM 与 manifest 完全一致：

```text
bytes = 28,323,326,606
provider MD5 = observed MD5
SHA-256 = 42ab19a8fc22ae0d4ce180f08ebc6361989c60ce9227ce601e21718d48cdb3ce
samtools quickcheck = PASS
```

v1.1 和 v1.2 读取的是同一批前缀记录：5,000,000 records、1,474,475 个带 xf、25 个 `xf & 8 != 0`。v1.1 因少于 1,000 个而 FAIL；v1.2 根据 25/25 的 CB/GN/UB/单基因 GN 完整性判定 schema 有效，同时发出低密度 warning。

HRR1849462 尚未运行 full target panel，因此其 biology 仍为 `NOT_TESTED`。

## HRR1849463

尚无本地 BAM、summary 或 receipt，状态为 `NOT_TESTED`。

## 防止提前终止

已完成三 donor 数学上已达到 ≥3 positive donors，但冻结协议要求完整 5/5 technical adjudication。当前继续保持 HOLD，避免 informative missingness 和 selective completion。
