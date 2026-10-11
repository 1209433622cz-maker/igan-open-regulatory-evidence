# CMM R4A12FG3：IL12RB2细胞优先级与QTL证据冻结

日期：2026-09-13。基于用户提供的 R4A12FG2 真实区域结果，并结合本轮公开数据源复核。外部信息均与附件证据分层记录。

## 1. Primary cell冻结：NK

从FG2原始派生表独立重算，NK为IL12RB2最强gene-level细胞：

- ACAT P = `3.423371e-118`
- top marker = `1:67324915:T:C`
- top marker P = `6.80524e-121`
- source SuSiE credible sets = 2
- source CS member总数 = 16

因此在任何新的disease↔eQTL结果出现之前，冻结：

> `PRIMARY_MOLECULAR_CELL = NK`

这样避免后续按PP4高低“挑细胞”。

## 2. 预注册secondary cells

所有已有source SuSiE CS的其他细胞均保留，按FG2 gene-level强度排序：

CD8_TEM, CD4_CTL, CD4_TCM, CD8_TCM, gdT, NK_Proliferating, MAIT, Treg, CD4_TEM, NK_CD56bright

这些细胞用于secondary/sensitivity分析；locus-level多重比较必须显式报告，不能把它们当成11个独立队列。

## 3. 其他细胞

其余有gene-level记录但无source CS的细胞只作为tertiary/exploratory expression-QTL背景。FG2中CD14 Mono和CD16 Mono对IL12RB2为`NOT_RETURNED`，不得补零或解释为生物学阴性。

## 4. 与SSc疾病证据的关系

2026 sex-specific SSc GWAS：`rs6662198`在女性中P=`8.52e-13`、OR=0.83（effect allele C），男性P=0.64；sex heterogeneity P=0.0051。论文进一步报告IL12RB2在whole blood与monocytes呈显著sex-dependent expression，在NK为nominally significant。

这支持IL12RB2是值得做cell-specific regulatory refinement的位点，但不能由此预设：

- NK eQTL与SSc disease signal共定位；
- rs6662198就是NK eQTL causal variant；
- monocyte中TenK10K `NOT_RETURNED`代表无调控。

正式判定仍必须从完整variant-level数据和signal model产生。

## 5. 可重复机器表

详见 `data/TenK10K_IL12RB2_cell_priority.tsv`，包含26个返回gene-level结果的细胞、ACAT、top marker、CS数量和冻结分析tier。
