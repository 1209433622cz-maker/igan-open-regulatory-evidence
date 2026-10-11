# CMM R4A12FG5：Source-matched LD 与公开可用性审计

## TenK10K公开summary层

已检查的TenK10K Zenodo release公开：
- 28细胞的100-kb完整common cis-eQTL summary；
- gene-level结果；
- SuSiE credible-set summary；
- coloc结果；
- 1-Mb扩展summary等。

在本轮检查到的公开Zenodo文件列表中，**未见单独发布的per-gene genotype correlation / LD matrix对象**。这是“已检查列表未见”，不是声称全互联网绝对不存在。

## Individual-level genotype层

EGA study：
- `EGAS50000001654` — TenK10K Phase 1 Genotypes
- 1,925人WGS
- GRCh38
- SNP/indel multisample VCF dataset：`EGAD50000002377`

EGA页面明确要求申请访问。因此真正的source-matched LD最直接路径仍是：
1. 获得EGA genotype权限；
2. 对IL12RB2预注册100-kb窗口生成1,925人signed LD；
3. 与source SAIGE-QTL variant order严格对齐。

## External LD层

1000G EUR503仍可作为：
- allele/AF sanity check；
- external-LD sensitivity；
- z–LD mismatch diagnostic。

但不能自动等同TenK10K source LD。

本轮还发现一个重要的“归档 vs 本地工作站”区别：
- 上传归档只包含1555旧GWAS匹配矩阵；
- 历史R4A8B工作记录证明用户本地曾构建27,067-variant full regional EUR503 panel。

因此下一轮首先应使用用户本地full regional panel补完current 891 variant external LD，而不是重新下载全1KG。

## 结论

当前paper-grade multi-signal路径有两个层级：

**External sensitivity path**
`full regional EUR503 -> current 891 LD -> strict QC -> multi-signal sensitivity`

**Source-matched definitive path**
`TenK10K EGA WGS -> IL12RB2 source LD -> final signal adjudication`

只有external path通过也仍需写作上标注为external-LD sensitivity；如果它失败，不允许删variant强迫通过。
