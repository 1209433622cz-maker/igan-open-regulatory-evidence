# GSE127136 ZMIZ1 肾组织供体级结果

日期：2026-09-15

## 输入与分层

| 文件 | bytes | SHA-256 |
|---|---:|---|
| `GSE127136_project_IgA_nephropathy_counts.csv.gz` | 15,703,242 | `89c3580ad550ae5df9e736bba97101f0ae02e724201b61d2e1f5fa4247dbce40` |
| `GSE127136_family.soft.gz` | 265,591 | `8f7a347ea166c6bed6695107f0225d71f47d5dd3efe63d99b646803c0ada7642` |

来源：<https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE127136>。

SOFT 与 count matrix 的 3,620 个 cell titles 精确匹配。按 `patients` 前缀与组织字段拆分后：

- kidney：2,785 cells，13 IgAN donors + 6 kidney-cancer paracancer donors；
- peripheral monocytes：835 cells，5 IgAN + 5 normal donors。

主分析只使用 kidney。PBMC 未并入肾组织，也没有把 paracancer controls 写成 healthy kidney。

## pseudobulk 方法

每名供体先汇总所有肾细胞的 raw counts 与 library size，再计算 `(ZMIZ1 counts+0.5)/(library+1)×10^6` 和 `log2(CPM+1)`。供体是生物学重复。

统计量包括：19 名供体中全部 `C(19,13)=27,132` 种标签分配的双侧精确置换、10,000 次组内 bootstrap、Welch t test 和 Mann–Whitney test。随机种子固定为 20260914。

## 结果

| 指标 | 值 |
|---|---:|
| donor detection | 19/19（100%） |
| case-control mean log2CPM difference | -0.25637 |
| bootstrap 95% CI | [-0.83532, 0.33266] |
| exact permutation P | 0.48279 |
| Welch P | 0.43777 |
| Mann–Whitney P | 0.46705 |

方向为病例较低，但区间跨 0，三个检验均不显著。冻结状态为 `INTERPRETABLE_CASE_LOWER_NOT_SIGNIFICANT`，不能写成 disease-state validation。

## 二级 marker localization

修正原脚本后只对 2,785 个肾细胞运行 deterministic marker score。2,720/2,785 可得到非 `Unresolved` 标签。ZMIZ1 平均单细胞 log1pCPM 较高的 provisional labels 包括 Intercalated、Monocyte、Neutrophil、Podocyte 和 TAL。

该步骤没有进行完整 normalization、batch correction、clustering 或 reference mapping，只能作为后续可能重分析时的线索；它不参与 R6A3A1 GO/FAIL 门。

