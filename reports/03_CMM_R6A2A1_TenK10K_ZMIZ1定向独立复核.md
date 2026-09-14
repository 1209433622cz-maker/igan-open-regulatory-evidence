# CMM R6A2A1：TenK10K ZMIZ1 定向独立复核

## 数据接入方式

Zenodo 的 `coloc_100kb.zip` 为 626,505,208 bytes，官方 MD5 `c627f1c4bc47706e331039d1e9e6e7d1`。本轮没有下载16.6 GB完整 QTL，也没有强迫用户搬运大文件；通过 HTTP Range 解析 41,929-entry central directory，只提取两个预冻结成员：

| member | compressed | uncompressed | CRC32 | local SHA-256 |
|---|---:|---:|---|---|
| kiryluk_IgAN/NK/chr10.csv | 26,597 | 64,086 | `ff195570` | `d65e29e2bcf479873267ea783ded66bdc5a26c6ea3808b36d4cd9fba11737724` |
| kiryluk_IgAN/NK_CD56bright/chr10.csv | 11,522 | 29,061 | `76853ced` | `a2f0aee7b78ece34e8c031069b3c18ac2a5c270123fcef36a14ef259087ea94c` |

成员 CRC、解压长度和本地 SHA-256 全部 PASS。因为没有读取整包所有字节，本轮不声称本地重算了整包官方 MD5。

## ZMIZ1 结果

| cell | SNPs | PP.H3 | PP.H4 | H4 ratio | top SNP | 解释 |
|---|---:|---:|---:|---:|---|---|
| NK | 826 | 0.001732 | 0.998255 | 0.998268 | chr10_79287258_G_A | supportive replication |
| NK_CD56bright | 826 | 0.926773 | 0.019352 | 0.02045 | chr10_79287258_G_A | distinct signal favored |

TenK gene-level NK ZMIZ1：ACAT P=`1.52×10^-24`，top variant P=`2.33×10^-27`。Source SuSiE 有两个 credible sets；CS2 位于约 GRCh38 79.278–79.288 Mb，与 disease/coloc top 区域相邻。

## 结论边界

TenK 作者预计算 CSV 未编码其 exact priors、完整 disease byte manifest 和每一项 harmonization 详情，因此不能替代我们的可复算 OneK analysis。它证明相同疾病标签、相同 gene、相同 NK context 在独立资源中有极强的单因果模型 shared-signal support。多信号最终裁决留给后续 source-CS/LD 分析。
