# CMM R6A1：肾组织字节与目标可检测性

## GSE127136

- processed count matrix：15,703,242 bytes；SHA-256 `89c3580ad550ae5df9e736bba97101f0ae02e724201b61d2e1f5fa4247dbce40`。
- 24,153 genes × 3,620 cells；3,620/3,620 matrix cell titles 与 GEO SOFT metadata 精确匹配。
- kidney donors：13 IgAN + 6 kidney-cancer/paracancer controls。
- peripheral monocyte donors：5 IgAN + 5 normal，属于不同 compartment，不能并入肾组织对照。
- 146 个跨资源候选 gene 中检测到 145 个（99.32%）；22/22 个跨资源候选 locus 至少有一个可检测 gene。

该数据可做组织定位和 donor-level pseudobulk，但目前 metadata 缺少可直接复用的完整 kidney cell-cluster label。R6A2 必须先恢复或重建细胞注释，然后以 donor 为生物学重复，不能把 3,620 个细胞当作独立样本。

## GSE286184 / GSE286186

- GSE286184 Xenium：22 samples，其中 IgAN 4、Control 3、DKD 6、MCD 4、MN 5；RAW tar 声明 335,585,280 bytes。本项目把 4 个 IgAN 空间样本用于 localization，禁止单独冒充充分的 disease-control inference。
- GSE286186 SuperSeries：59 个 sample records；其 file list 与 series metadata 已验收，RAW tar 声明 3,452,221,440 bytes。本轮不下载大 RAW；R6A2 先拆分 snRNA 与 Xenium subseries、冻结 diagnosis/covariate 后再取所需对象。

`KIDNEY_TARGET_DETECTABILITY_GATE = PASS`。
