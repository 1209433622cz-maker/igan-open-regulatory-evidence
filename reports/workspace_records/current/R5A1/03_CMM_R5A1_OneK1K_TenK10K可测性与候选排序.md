# CMM R5A1：OneK1K / TenK10K 可测性与候选排序

日期：2026-09-13

## 已验收的实际字节

| 资源 | 文件 | 内容 | 本地验收 |
|---|---|---|---|
| OneK1K | `OneK1K_TensorQTL_top_eQTL_summary.zip` | 14 个免疫细胞、每细胞 22 个染色体、top cis-eQTL | 16,950,155 bytes；MD5 `46e986dc53c9f4f1b6daa2b7a73d277c`；PASS |
| TenK10K | `common_variant_gene_level_results_with_annotated_fails.zip` | 28 个免疫细胞 gene-level 结果 | 10,137,272 bytes；MD5 `b5cd2ee1f34f90539ebf6683dcd35a2e`；PASS |
| TenK10K | `susie_summary.zip` | 28 个免疫细胞 SuSiE credible sets | 59,669,579 bytes；MD5 `f321c719030cc837cf27e09cd2ea6b65`；PASS |

OneK1K 使用 GRCh37，TenK10K 使用 GRCh38。所有跨资源区域扫描使用 NCBI RefSNP 双 build 坐标，早期的直接坐标交叉结果已废弃。

## 候选区域排序

| 排名 | 区域 | 亚型模式 | 双资源筛查 | 冻结职责 |
|---:|---|---|---|---|
| 1 | chr5 rs6861227 | EOMG 富集 | TNIP1 在两资源显著；TenK10K SuSiE max PIP≈0.554；疾病 lead 在 B-naive TNIP1 CS 中，QTL PIP≈0.0236 | 第一证伪链；同时比较 7 个跨资源竞争基因 |
| 2 | chr2 rs7596255 | 方向翻转 | DHX57、GALM、SRSF7 跨资源；SOS1 仅 TenK10K fine-mapped | 检验方向翻转是否对应同一或不同调控信号 |
| 3 | chr18 rs7239261 | LOMG 富集 | PIGN、ZCCHC2 跨资源；TNFRSF11A 仅 TenK10K fine-mapped | LOMG 区域有界基因竞争 |
| 4 | chr1 rs2476601 | 共享效应 | RSBN1、SLC16A1-AS1 跨资源；PTPN22 仅 TenK10K fine-mapped | 亚型共享正控 |

chr5 / TNIP1 的具体筛查证据：

- OneK1K：NK q≈0.00249，CD4_NC q≈0.0434；
- TenK10K：CD4_Naive 最强 BH q≈`4.41e-15`，并在多个 B、T、monocyte、NK 细胞中显著；
- TenK10K SuSiE：TNIP1 最大 PIP≈0.5535（CD4_Naive）；
- exact disease lead `5:151067567:T:G` 位于 B-naive TNIP1 credible set，但 PIP 仅≈0.0236。

因此 TNIP1 是优先待证伪基因，不能被写成已证明的 causal gene。ANXA6、ATOX1、CCDC69、GM2A、RPS14、SLC36A1、TCOF1 仍保留在竞争集合中。

## OneK1K genotype 传输状态

公开记录确认 `plink_genotype_merged_980_donors.zip` 包含 980 donors、MAF>0.05 的 PLINK genotype，文件应为 233,198,074 bytes，MD5 `be1053e34fa023bc808388d4e0bf2aa1`。本轮已取得 215,495,213 bytes 的可续传分片，尚缺 17,702,861 bytes；Zenodo 多个官方路径持续返回 504。

该状态只证明源对象公开存在，并未通过本地 archive、BED/BIM/FAM、样本数、build 和逐 lead 覆盖审计。OneK1K genotype 只含 MAF>0.05 common variants，EAF 约 0.02 的 rs7596255 很可能不在文件中；这将由区域共同变异和可用 LD proxy 数决定 chr2 是否可分析。R5A2 的 LD 与推断步骤继续 HOLD。断点续传完成后必须运行 `audit_onek_genotype.py`。

## 仍缺的区域级输入

- OneK1K full cis-eQTL：10,344,009,571 bytes，MD5 `e42239480f40abd21f221c0d77c82cc3`；
- TenK10K full ±100 kb cis-eQTL：16,559,137,990 bytes，MD5 `dd54714b2effb91160ac171ccb941534`。

已提供一个 PowerShell 入口完成续传、checksum 和 genotype 审计。索引级显著结果只用于缩小区域，不用于 coloc。

## 来源

- OneK1K：`https://zenodo.org/records/18910121`
- TenK10K：`https://zenodo.org/records/18221260`
