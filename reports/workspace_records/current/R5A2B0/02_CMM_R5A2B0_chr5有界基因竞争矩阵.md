# R5A2B0：chr5 有界基因竞争重新冻结

## 为什么不能只测 TNIP1

OneK1K source q-value 与 TenK10K SuSiE 显示 chr5 是典型的“多个强 cis-eQTL 共存”区域。

### TNIP1
- OneK1K source-significant：NK、CD4_NC；
- TenK10K gene-level显著且有 SuSiE CS；
- TenK10K 最大PIP约0.554；
- rs6861227 对应 disease lead 进入 B-naive TNIP1 CS，但 QTL PIP仅约0.0236。

### 主要竞争基因
- ANXA6：OneK1K 12个 source-significant cells；TenK10K max PIP=1；
- GM2A：OneK1K 5个；TenK10K max PIP≈0.9996；
- RPS14：OneK1K 7个；TenK10K max PIP=1；
- CCDC69：OneK1K 2个；TenK10K max PIP≈0.991；
- ATOX1 / SLC36A1 / TCOF1 也均至少有一个 OneK1K source-significant cell。

但这些强 competitor 的 disease lead 均不在 TenK10K source CS。换言之，“QTL很强”不能替代“疾病与QTL同一信号”。

## 冻结原则

所有 32 个 source-significant cell–gene 在第一层得到同等待遇。TNIP1 的优先级来自疾病 locus identity 与 TenK10K disease-lead CS evidence，而不是允许它使用更宽松的 coloc 阈值。
