# Sun 2018 pQTL 真实字节与 signal-level colocalization

日期：2026-09-15

## 数据接收

来源为 eQTL Catalogue `QTS000035/QTD000584`，Sun 2018 INTERVAL plasma aptamer pQTL，N=3,301，GRCh38，ALT 为 effect allele。

| 文件 | bytes | SHA-256 |
|---|---:|---|
| `QTD000584.permuted.tsv.gz` | 130,995 | `18504ebec4f9882a74dd30e8ea7fb7d103e10f9fe2499ba625a178c412576bc1` |
| `QTD000584.credible_sets.tsv.gz` | 1,032,049 | `cc324e6fe39cbc699879ae41d529215e347791ad13e69b823b9024fa6ee08644` |
| `QTD000584.all.tsv.gz` | 731,621,677 | `46f0ea73118adcfbb45c04ae1685d27d6c6471b08654b0b89e38bcab7f91b2c2` |
| `QTD000584.all.tsv.gz.tbi` | 1,304,240 | `f4943818b6130075cdcb515b608d7416932ab1a3761779b6a28d5b73aaa9c273` |
| `QTD000584.lbf_variable.txt.gz` | 459,588,570 | `9b852c0b8565901af67d52302b7875de13c849d3be265cec5b04eebaf3acbd5a` |

公共入口：<https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/>。

## 小文件筛选

11 个冻结蛋白的真实状态：

- measured：8/11；
- source-supported：TNFSF8、TNFSF12；
- measured but no source signal：TNFSF4、TNFRSF18、TNFSF15、TNFRSF13B、LIF、OSM；
- not measured：OVOL1、RELA、TNFSF13。

TNFSF8 `p_beta=0.00154479`，有 1 个 source CS；TNFSF12 `p_beta=1.84033×10^-93`，有 2 个 source CS。只有二者触发大文件。

## 提取和协调

- nominal rows before variant de-duplication：18,615；
- after de-duplication：16,778；
- LBF rows：16,778；
- source SuSiE LBF components：L1–L10；
- scanned/lifted disease rows：78,589；
- final harmonized rows：11,308；
- TNFSF8 overlap：6,144；
- TNFSF12 overlap：5,164。

疾病数据为 combined IgAN GWAS，原始 build 为 GRCh37。坐标经 UCSC `hg19ToHg38` chain 转换；仅保留唯一同染色体映射、精确 REF/ALT allele set；无频率救援时排除 palindromic SNP。

## 合法 source-CS 分量

| locus | protein | component | pQTL top variant | default H3 | default H4 | H4 ratio default | H4 ratio p12=1e-6 |
|---|---|---|---|---:|---:|---:|---:|
| TNFSF8/15 | TNFSF8 | L1 | chr9_114934654_C_A | 0.96708 | 0.01809 | 0.01836 | 0.00187 |
| TNFSF12/13 | TNFSF12 | L1 | chr17_7549435_G_A | 0.99988 | 0.0000051 | 0.0000051 | 0.00000051 |
| TNFSF12/13 | TNFSF12 | L2 | chr17_7545325_C_T | 0.99883 | 0.001049 | 0.001049 | 0.000105 |

门槛为 source CS 存在、default H4≥0.80、default ratio≥0.80、low-p12 ratio≥0.50。通过数为 0。

TNFSF12 的 disease lead 和 pQTL 都有强 nominal P 值，但 source-CS 分量显示 H3 压倒 H4。这是 distinct-signal 证据，不是“数据不足的阴性”。TNFSF8 的 source pQTL 较弱且 H3 同样主导。Track A 最终为 `FAIL_NO_ADDITIONAL_SHARED_SIGNAL`。

