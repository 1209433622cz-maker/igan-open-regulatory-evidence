# CMM R4A12FG4：TenK10K NK IL12RB2 完整 QTL 验收

## 接入结果

| 项目 | 结果 |
|---|---:|
| 远程归档成员数 | 28 |
| NK 压缩成员字节 | 556,881,415 |
| NK 展开字节 | 2,272,841,254 |
| 完整源文件行数（含表头） | 15,588,167 |
| IL12RB2 精确行数 | 1,366 |
| IL12RB2 坐标范围（GRCh38） | chr1:67,207,429–67,498,705 |
| 成员 CRC32 | `25f9b199` PASS |
| 提取文件 SHA-256 | `3a4f0802507c31d81afdd9842ff256ef48587ccba88310f7760c7ccee9e956fd` |

真实字段为：空索引列、`CHR`、`POS`、`MarkerID`、`Allele1`、`Allele2`、`AC_Allele2`、`AF_Allele2`、`MissingRate`、`BETA`、`SE`、`Tstat`、`var`、`p.value`、`p.value.NA`、`Is.SPA`、`N`、`gene`、`is_snp`。本轮按 `gene` 字段精确匹配 `ENSG00000081985`，不再按任意单元格模糊搜索。

全部目标记录 N=1,925。QTL top 为 `1:67324915:T:C`，BETA=0.470725、SE=0.0201335、P=6.80524×10^-121。rs6662198 对应 `1:67340524:T:C`，QTL BETA=-0.360208、P=2.99088×10^-86。

`Allele2` 是 SAIGE-QTL 的效应等位基因；FinnGen 的 beta 和 AF 对 ALT。因此 harmonization 仅接受 exact REF/ALT。反向等位基因位置不能仅凭交换和翻转 beta 合并，尤其重复序列和多等位位点会造成严重 AF 冲突。
