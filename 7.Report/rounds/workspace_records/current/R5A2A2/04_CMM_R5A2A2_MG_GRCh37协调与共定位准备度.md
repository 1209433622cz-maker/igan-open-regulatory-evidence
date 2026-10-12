
# CMM R5A2A2：MG GRCh37 协调与共定位准备度

## 原始疾病输入

为避免把 GRCh38 harmonised GWAS 再映射回 OneK1K GRCh37，本轮下载 GWAS Catalog 的 original GRCh37 TSV，并逐文件完整扫描。三项字节数和官方 MD5 均通过。

| accession | trait | bytes | 全文件行 | 窗口行 | BIM 匹配 | 可推断 | 排除 | MD5 |
|---|---|---|---|---|---|---|---|---|
| GCST90432156 | MG_overall | 332,462,076 | 7,142,383 | 5,450 | 3,873 | 3,854 | 19 | True |
| GCST90432157 | EOMG | 359,301,658 | 7,585,282 | 5,816 | 4,198 | 4,153 | 45 | True |
| GCST90432158 | LOMG | 300,669,210 | 6,307,768 | 4,497 | 2,607 | 2,596 | 11 | True |

协调规则固定为同一 GRCh37 染色体与唯一位置连接，再用 allele set 定向到 BIM A1。非回文 SNP 可直接处理 exact、swap 或 reverse-complement；回文 SNP 只有在一个频率方向至少比另一个近 0.10 且与 OneK AF 相差不超过 0.20 时才保留。其余回文歧义、allele mismatch 和 |ΔAF|>0.20 均排除。

LOMG 原始窗口有 7 个重复位置，来自不同 indel/多等位记录；与 OneK BIM allele set 匹配后的结果没有重复 variant_id。它们被保留在审计计数中，但不构成推断输入失败。

## rs7239261 锚点复核

| trait | GWAS EA | OneK A1 | OR | beta_A1 | SE | P | EAF_A1 | OneK AF_A1 | |ΔAF| |
|---|---|---|---|---|---|---|---|---|---|
| MG_overall | A | A | 1.21458 | 0.194398 | 0.0212 | 3.981e-20 | 0.436274 | 0.452551 | 0.016277 |
| EOMG | A | A | 0.96977 | -0.0306963 | 0.0475 | 0.5184 | 0.374204 | 0.452551 | 0.078347 |
| LOMG | A | A | 1.29576 | 0.259097 | 0.0337 | 1.561e-14 | 0.368259 | 0.452551 | 0.084292 |

三套原始 GWAS 的 effect allele 均为 A，与 OneK BIM A1 一致。此前 GRCh38 harmonised 表使用 ALT C，因此 beta 符号相反但生物学方向一致。LOMG 的 A1 正效应等价于先前 C 的 beta=-0.2591；EOMG 接近零，overall MG 为强疾病信号。

## cell–gene 共同覆盖

三套疾病数据有 2,497 个共同可推断变异。每个 cell–gene 单独与 EOMG 和 LOMG 相交后：

| phenotype | cells | 每对最少 EOMG∩LOMG∩QTL | 最多 | ABF 输入门 |
|---|---|---|---|---|
| BCL2 | 14 | 1124 | 1216 | True |
| CDH20 | 3 | 1759 | 1759 | True |
| KIAA1468 | 14 | 2406 | 2558 | True |
| PHLPP1 | 9 | 2111 | 2117 | True |
| PIGN | 11 | 2480 | 2491 | True |
| RP11-879F14.2 | 1 | 1958 | 1958 | True |
| TNFRSF11A | 5 | 2517 | 2562 | True |
| ZCCHC2 | 14 | 2296 | 2441 | True |

71/71 组合达到预设的至少 500 个 EOMG∩LOMG∩QTL 共同变异，实际范围为 1,124–2,562。该结果只证明 coloc 输入足够，并不证明任何组合存在 H4 共享信号。
