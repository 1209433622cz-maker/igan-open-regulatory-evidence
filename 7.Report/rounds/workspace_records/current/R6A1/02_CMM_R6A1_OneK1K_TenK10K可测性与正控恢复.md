# CMM R6A1：OneK1K / TenK10K 可测性与正控恢复

## 冻结定义

- locus window：匹配 build 的已发表非 HLA lead ±1 Mb。
- OneK1K source-positive：source q-value `<0.05`，且 source top eQTL 位于窗口内。
- TenK10K source-positive：cell 内 gene-level ACAT P 经 BH FDR `<0.05`，或 source SuSiE credible-set member 位于窗口内。
- cross-resource candidate：同一 locus、同一 GENCODE gene symbol、broad immune class 相容。

这三个定义都是**预检候选定义**，不是 disease-QTL colocalization。

## 资源完整性

- OneK1K top-QTL ZIP：CRC PASS，308 个科学数据成员；full ±1 Mb cis-eQTL 与 980-donor PLINK genotype 已在工作区。
- TenK10K gene-level ZIP：CRC PASS，28/28 cell types。
- TenK10K SuSiE ZIP：CRC PASS，28/28 cell types。
- GENCODE v50：相关 812 个 Ensembl ID 中 804 个映射到 symbol；8 个未映射项保留，不做猜测式基因名替换。

## 结果

| 项目 | 数量 |
|---|---:|
| OneK1K source-significant cell–gene | 514 |
| OneK1K source-significant genes | 211 |
| OneK1K testable loci | 22/24 |
| TenK10K ACAT-FDR cell–gene | 4469 |
| TenK10K SuSiE gene–cell | 2861 |
| TenK10K testable loci | 24/24 |
| cross-resource compatible cell–gene pairings | 1189 |
| cross-resource genes | 146 |
| cross-resource loci | 22/24 |

CFH 与 IGH 在 OneK1K source-significant 层为 0，但 TenK10K 可测，因此列为 resource-asymmetric，不解释为生物学阴性。OneK1K public BIM 在 19/24 个 locus 有精确 lead position；其余 locus 仍有充分区域变异，后续必须用 harmonized regional variants，而不能因 exact lead 缺失直接判失败。

## 已发表正控

来自论文 DICE 分析的 14 个 gene–locus 正控中，4 个在两套资源和相容 broad cell class 中同时恢复：

| locus | gene |
|---|---|
| IRF4/DUSP22 | IRF4 |
| IRF4/DUSP22 | DUSP22 |
| ZMIZ1 | ZMIZ1 |
| ITGAM/ITGAX | ITGAX |

它们属于 R6A2 的方法 benchmark。只有 R6A2 在真实疾病 GWAS 与新 QTL 之间重算 signal-level 证据后，才能说是否在 OneK1K/TenK10K 中复现共定位。

`QTL_TESTABILITY_AND_CONTROL_ELIGIBILITY_GATE = PASS`。
