# CMM R4A12FG2：FinnGen 公开对象接入与 P0 验收

执行窗口：2026-09-12—2026-09-13（Asia/Hong_Kong）

## 1. Manifest 接入

| Release | Manifest bytes | Local SHA-256 | `M13_SYSTSLCE` N |
|---|---:|---|---|
| R12 | 773,612 | `730fc3f54f6a73d37dc6fc9c6a0fd13159f4134bbc274e93c4db980f93120772` | 854 / 484,260 |
| R13 | 820,805 | `c9caafa9b98ee5ef050a705766bd1c451fc2154fb8e81b069022012a2f75ae20` | 883 / 483,310 |

精确过滤了 `M13_SYSTSLCE`、`SYSTSCLE_STRICT`、`CREST`。两版共 6 个 summary 对象和 6 个 `.tbi` 均 HEAD=200，保存了 content length、ETag/provider MD5、CRC32C、Last-Modified、Accept-Ranges 和 URL。

全部 12 个对象为 4,715,338,809 bytes；主 endpoint 的 R13/R12 summary+index 为 1,587,342,434 bytes。为避免无目的下载，本轮只读取预注册 IL12RB2 区域；完整对象下载保持 dry-run，安全续传脚本已经冻结。

## 2. 远程 Tabix 接入

固定：

- assembly：GRCh38
- anchor：`rs6662198 = 1:67340524:T:C`
- region：`1:66840524-67840524`，anchor ±500 kb
- key：`chrom:pos:ref:alt`

Node.js `@gmod/tabix 3.8.2` 通过 `.tbi` 仅读取所需 BGZF ranges。结果保存 source object/index metadata、坐标转换、输出行数、范围错误、传输字节观察和输出 SHA-256。

| Release | Rows | Bytes | SHA-256 | Range transfer observed |
|---|---:|---:|---|---:|
| R12 | 6,855 | 705,906 | `6c034213990f857714f7baf4d06f8f5dd4fdf794f94b9742a24e5bef5af33046` | 283,683 |
| R13 | 6,855 | 687,381 | `cfce6adb2937c9db23e520df1abcc4816e7db4e7cad3a408603a0b66bb71db65` | 288,774 |

第二次查询在新的输出路径中取得完全相同的行数、bytes 和 SHA-256。两次 source ETag 也保持一致。

## 3. P0-FG 结构门

P0-FG 独立于 H6 v2.1。它检查：

- FinnGen all-sex 必需字段；
- 染色体与冻结区域边界；
- p、beta、SE、AF 的有限性和数值域；
- 至少 100 行、100 唯一位置和 250 kb span；
- rs6662198 的位置与无序等位基因精确唯一。

R12 与 R13 均为：

`PASS_REGION_STRUCTURAL_READY_FOR_HARMONIZATION`

每版 6,855 行、6,727 个唯一位置、0 个解析/数值/边界错误、1 个精确 anchor。

P0-FG 只确认区域结构可进入 harmonization。它没有检查 INFO、GRCh38 FASTA normalization、QTL coverage、LD、fine-mapping 或 coloc。

## 4. Sex-specific 门

R12 官方文档确认 female/male/meta 结构和 262-endpoint exclusion list，但 Green Library 对本机公开 HTTPS 返回 403，`gcloud auth list` 没有 active account。因此状态为：

`ACCESS_BLOCKED_403_NO_ACTIVE_FINNGEN_GCLOUD_ACCOUNT`

这表示未获授权字节；不表示 `M13_SYSTSLCE` 被排除。R13 未在已检查官方 release notes 中发现对应 sex-specific release，不能套用 R12 路径规则。

## 5. 工具与测试

- manifest/object audit
- resumable full-object downloader：`.part`、size、provider MD5、local SHA-256
- Green Library drop-list gate
- local full-object Tabix extractor
- all-sex P0-FG validator
- remote indexed regional reader
- 8/8 unit tests PASS；Python compile 与 Node syntax PASS

官方格式依据：[GWAS results format](https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files/gwas-results-format)、[sex-specific results format](https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files/sex-specific-gwas-results-format)。


