
# CMM R5A2A2：样本接口、Parquet schema 与等位基因审计

## schema

14 个 chr18 Parquet 的 schema 完全一致：`phenotype_id:string`、`variant_id:string`、`tss_distance:int32`、`af:float`、`ma_samples:int32`、`ma_count:int32`、`pval_nominal:double`、`slope:float`、`slope_se:float`。每个文件只有一个 row group；统计量范围、有限性、正 SE、variant–BIM 映射和 phenotype TSS 一致性全部通过。

## 样本接口的纠正

更新版 covariate 文件不能单独定义每个 cell 的实际 QTL donors。例如 CD4_SOX4 有 857 行 covariate，但 raw QTL 的计数只对应 295 donors；Plasma 为 795 对 253。继续把 covariate 全部行当作 LD 样本会产生错误频率和 LD。

本轮从官方 pseudobulk mean matrices 的 donor 列读取每个 cell 的非 `NA` mask，并检查前 5 个基因的 mask 完全一致。得到的 active donor 集合全部存在于 FAM 和相应 covariate 文件；用这些 donor 重新读取 BED 后，QTL 的 `af/ma_count/ma_samples` 精确复现。因此 cell-specific source LD 的样本列表已经明确。

| cell | 实际表达 donors | covariate 行 | NA mask 稳定 | 接口 |
|---|---|---|---|---|
| B_IN | 975 | 980 | True | True |
| B_MEM | 970 | 980 | True | True |
| CD4_ET | 980 | 980 | True | True |
| CD4_NC | 980 | 980 | True | True |
| CD4_SOX4 | 295 | 857 | True | True |
| CD8_ET | 980 | 980 | True | True |
| CD8_NC | 980 | 980 | True | True |
| CD8_S100B | 959 | 979 | True | True |
| DC | 726 | 967 | True | True |
| Mono_C | 851 | 967 | True | True |
| Mono_NC | 690 | 932 | True | True |
| NK | 980 | 980 | True | True |
| NK_R | 750 | 968 | True | True |
| Plasma | 253 | 795 | True | True |

`pseudobulk_matrix_columns` 中还包括非 donor 标识列，所以报告的“实际表达 donors”以非 NA donor ID 为准。
