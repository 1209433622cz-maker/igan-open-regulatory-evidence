# TenK10K 双基因正式复制

## IL12RB2 × NK

完整 PBC GWAS 经 hg19→hg38、精确位置与 allele orientation 后，与 TenK NK 的 IL12RB2 公开 QTL 得到 396 个变异。

| p12 | PP.H3 | PP.H4 | H4/(H3+H4) |
|---:|---:|---:|---:|
| 1e-6 | 0.0240266 | 0.9759734 | 0.9759734 |
| 1e-5 | 0.0024558 | 0.9975442 | 0.9975442 |
| 1e-4 | 0.0002461 | 0.9997539 | 0.9997539 |

判定：`PASS_FULL_PBC_INTERSECTION_WITH_SOURCE_CS_EXTERNAL_LD_CAVEAT`。完整交集去除了 292-rsID bridge 限制；TenK source-CS 仍未直接进入交集，故 source signal coherence 继续标注外部 EUR503 LD caveat。

## FCRL3 × B_intermediate

从 Zenodo 16.56 GB ZIP 中只获取预冻结 `B_intermediate` 成员的 591,715,279 压缩字节。验收依据是完整 ZIP member，而不是片段大小：

```text
uncompressed bytes = 2,392,868,507
CRC32 = 3c73842b
source lines including header = 16,543,537
exact FCRL3 rows = 843
extract SHA-256 = 2858979a854e5f59e6bd60b018c12ec0661e79b4effaa044118c190e08b3f4e1
```

PBC 与 QTL 得到 343 个精确 allele overlap。

| p12 | PP.H3 | PP.H4 | H4/(H3+H4) |
|---:|---:|---:|---:|
| 1e-6 | 0.0782743 | 0.9215758 | 0.9217140 |
| 1e-5 | 0.0084219 | 0.9915620 | 0.9915780 |
| 1e-4 | 0.0008486 | 0.9991497 | 0.9991514 |

Top conditional shared weights：

| variant | rsID | weight | TenK source CS1 PIP |
|---|---|---:|---:|
| 1:157701026:A:G | rs7528684 | 0.38399 | 0.34725 |
| 1:157700500:C:G | rs945635 | 0.24937 | 0.22212 |
| 1:157699488:C:T | rs3761959 | 0.19283 | 0.20812 |
| 1:157699203:C:T | rs2210913 | 0.17381 | 0.22212 |

四个 top variants 全部位于 TenK source CS1；预冻结 rs3761959 精确 identity 通过。判定为 `PASS_ROBUST_SINGLE_CAUSAL_ABF_SMOKE_WITH_SOURCE_CS1_IDENTITY`。

## 解释上限

TenK FCRL3 source SuSiE 文件有 45 个 FCRL3 credible-set rows，其中 24 个进入精确疾病/QTL overlap，并包含多个 credible sets。ABF 的单因果假设因此必须写入方法限制；本轮证明的是跨资源 compatible-cell signal replication，不能声称唯一因果变异。

公开来源：[TenK10K Zenodo](https://zenodo.org/records/18221260)。
