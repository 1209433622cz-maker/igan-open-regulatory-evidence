# CMM R4A12FG6：Source-matched LD 与主数据实时状态

## 1. TenK10K source LD

EGA 官方数据集 [EGAD50000002377](https://ega-archive.org/datasets/EGAD50000002377) 明确包含 1,925 个 TenK10K Phase 1 样本的 GRCh38 SNP/indel multi-sample VCF，归属研究 `EGAS50000001654`，需要通过 DAC `EGAC50000000931` 请求访问。公开页面列出该数据集 89 个文件、总量 475.1 GB，并限定健康/医学/生物医学、非商业研究及机构安全环境。

Zenodo 官方 record [18221260](https://zenodo.org/records/18221260) 当前列出 15 个公开对象，包括 100-kb/1-Mb eQTL summary、SuSiE summary 和 coloc 输出；本轮未发现 per-gene source correlation/LD matrix 公开对象。

因此 source-matched LD 的现实路径为：

1. 优先向作者/DAC请求 IL12RB2 100-kb、current 1,366 variants 的相关矩阵或可复核 per-gene LD；
2. 若只能提供受控基因型，则申请 `EGAD50000002377`，在获批机构环境中仅提取 chr1 目标区间并生成 signed ALT LD；
3. 受控数据及其衍生敏感文件不得进入普通 release ZIP。

## 2. 2026 sex-specific SSc 主数据

本轮于 2026-09-13 再查 GWAS Catalog 官方 v2 接口：

- PMID 41999721 publications：HTTP 200，0 条；
- studies：HTTP 200，0 条；
- `full_pvalue_set=true`：HTTP 200，0 条；
- GCST009131 正对照：HTTP 200，1 条。

因此本轮仍未取得 female/male 完整 summary-statistics 字节。0 条只表示所查官方入口尚未索引目标，不证明其他位置绝对不存在。

## 3. 优先级

2026 female/male 主数据一旦到达并通过 H6，优先级立即高于 IL12RB2 all-sex 支线。当前不得将 FinnGen overall 结果替代 sex-stratified 主问题。
