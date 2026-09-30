# R7A2A1 字节接入与独立复核

## 数据闭环

五个对照 run 为 `HRR1849454–HRR1849458`，对应 HRA008003 的五个 hepatic-hemangioma non-lesion liver 供者。累计原始 BAM 字节为 `134,657,112,757`。

逐 run 核对了：

- manifest 的 exact run、expected bytes、provider MD5 与 URL；
- 实际 observed MD5 与 SHA-256；
- samtools quickcheck 后留下的 schema v1.2 记录；
- target-panel summary 中的 run、bytes、SHA-256 与技术 QC；
- resume validator 的 summary/receipt identity；
- called-cell 表重新聚合后的 gate cell、positive cell、target UMI、lineage total UMI 与 CPM；
- 成功 compact 输出后 BAM 删除状态。

全部 5/5 通过，`bam_control` 当前为空。

## 独立重算

新增 `05_independent_QA_R7A2A1.py`，在不读取正式比较程序内部对象的情况下重新读取十个供者 called-cell 表，重算两个 target-lineage 的 donor metrics，再枚举全部 252 种 5 vs 5 标签组合。

结果：

```text
QA checks = 19/19 PASS
official JSON vs independent rerun = exact parsed match
official TSV vs independent rerun = byte-identical
FCRL3 exact P = 0.1111111111
IL12RB2 exact P = 0.06349206349
```

正式比较 JSON SHA-256 为 `e7e2082f324dad70b78c701c9fe83100301b4d3b75864637e998e8e7cbe3b7fd`，正式 TSV SHA-256 为 `ff9581e7f70c1bf244fa6a06674e0733c46d4ded0c47b19f46816ee88e8e5d1c`；独立输出完全一致。

## 敏感性分析

三类 donor endpoint 的方向在逐一删除任意一个供者后均保持 10/10 一致：

- FCRL3–B：PBC 较低；
- IL12RB2–NK：PBC 较高。

但三个 endpoint family 均未形成校正后显著性。这说明方向不是由单一供者完全决定，同时也不能把稳定方向写成阳性差异。
