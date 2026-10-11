# CMM R6A2C1D：TenK10K 独立复制与跨 build 裁决

日期：2026-09-14

## 输入与来源

本机已有 TenK10K 公开小型摘要包：

| archive | bytes | SHA-256 |
|---|---:|---|
| gene-level results | 10,137,272 | `fcb99a4454a2a5f0feb11c56bcedad667400ebbeead2b39f256a25f48b71ae74` |
| source SuSiE summary | 59,669,579 | `0a2e2cb0dec4b76d18e42b29c36b243a9ccd67b8761f17d20a83ae51f656e7ff` |

此外从 626,505,208-byte author-precomputed `coloc_100kb.zip` 通过 HTTP Range 只提取三个冻结成员。中央目录 41,929 entries；三个成员均通过压缩长度、解压长度、CRC32 和本地 SHA-256：

| member | compressed bytes | uncompressed bytes | CRC32 | SHA-256 |
|---|---:|---:|---|---|
| kiryluk_IgAN/CD4_Naive/chr10.csv | 26,106 | 65,598 | `0de6bb46` | `e4436007e651d66e15d9ef5687c39e26eee019cce93ff0a63005457dca680c6c` |
| kiryluk_IgAN/CD4_TCM/chr10.csv | 28,304 | 70,188 | `b77065c5` | `bb3c01d69515e3003331b29634291200d3960e6e0e86abbc77ce3471e6aac7007` |
| kiryluk_IgAN/Treg/chr10.csv | 15,864 | 38,073 | `69e00f37` | `86bf2fdaee8f1da26f5e6dc81eb1d225333b9280cb6da8a64eb35d0db455f3378` |

整份 626 MB archive 未下载，本轮不声称实测整包 MD5；官方记录值仅作为来源元数据。

## 跨 build 与信号重叠

OneK1K 结果为 GRCh37，TenK10K 为 GRCh38。使用 UCSC `hg19ToHg38.over.chain.gz`，bytes 227,698，SHA-256 `5c0598e500ceb5a78c73086929e8ef993aec309bcafb595139b53d440b125a1d`。

PF10/L10 的 15 个 OneK credible-set variants 全部唯一映射到 GRCh38 chr10 正链。以 GRCh38 position 加无序 allele set 与 TenK source credible members 连接：

```text
OneK primary CS members = 15
unique plus-strand liftover = 15
exact overlap with TenK CD4_Naive/CD4_TCM source CS = 0
```

OneK CS 到 TenK CS 的最短位置距离：CD4_Naive 为 22,693 bp，CD4_TCM 为 5,512 bp。相邻并不等于相同；没有精确共享成员时不能宣布 source-CS replication。

## 作者预计算 coloc

`kiryluk_IgAN × REEP3` 的 354 个 tested SNPs 中，CD4_Naive 与 CD4_TCM 均强烈由 H3 主导。H4 ratio 只有 0.0315 与 0.0259；Treg 无 source SuSiE credible set，且 H4 ratio 0.1823。

该预计算对象并非本轮 Asian-only disease dataset 的独立重跑，因此不能单独否定 Asian-specific biology；但结合两个独立 QTL source CS 不重叠，它足以判定预冻结的 TenK molecular replication 门失败。

```text
TENK_REEP3_QTL_GENE_LEVEL = PRESENT
TENK_REEP3_SAME_SIGNAL_REPLICATION = FAIL
REEP3_ASIAN_DISCOVERY = RETAIN_WITHOUT_UPGRADE
```

