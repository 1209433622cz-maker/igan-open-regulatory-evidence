
# CMM R5A2A2：OneK1K 10 GB 归档与基因型字节审计

## raw cis-eQTL archive

- 文件：`1_data/qtl/OneK1K/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz`
- bytes：`10,344,009,571`
- MD5：`e42239480f40abd21f221c0d77c82cc3`，与 Zenodo 官方记录一致；
- SHA-256：`63b980c82c234268183205a9cf3c9da96ead1440d7b4b4586652f38ea18039ea`；
- tar members：622；其中科学成员 311、AppleDouble metadata 311；
- 科学 Parquet：308，即 14 cells × 22 chromosomes；
- 真实 chr18 Parquet：14/14，外加 README 与 BIM，共提取 16 个对象、408,104,922 bytes。

AppleDouble 成员只从科学成员选择中排除；完整 archive 仍被顺序读取并参与哈希。这个处理不改变原文件，也没有把 metadata 文件误当成第二份 QTL 数据。

## genotype

OneK1K genotype ZIP 的官方 MD5 已在 R5A2A 通过。本轮把 3 个真实 PLINK 成员解出到规范数据目录：BED/BIM/FAM 合计 `1,461,094,883` bytes；FAM 为 980 个唯一 donors，BIM 为 5,326,925 个唯一 variant IDs，BED magic 表明 SNP-major PLINK v1。

raw eQTL archive 内的 `plink_merged.bim` 与 genotype ZIP 的 BIM 逐字节相同，大小 `155,979,658` bytes，SHA-256 `6e28edad34d5930ca99f7be873e4684a885e26433d13ddba3d970bb8f8ad0bb6`。这使 Parquet `variant_id`、BIM 顺序和 BED offset 构成同一可验证接口。

## 代码级方向定义

官方 OneK1K TensorQTL 脚本通过 `PlinkReader` 载入 PLINK，TensorQTL 当前 `genotypeio.py` 明确执行 `self.bed = 2 - self.bed`。结合 3,655 个跨 14 cells 的 BED 重算，本轮确认：

- Parquet `af` 与 `slope` 对应 BIM `A1`；
- `ma_count` 与 `ma_samples` 对应较小频率等位基因；当 A1 AF>0.5 时，它们对应 A2，而不是 A1；
- 3,655/3,655 行的 minor allele count、carrier count 和 A1 AF 均精确复现。

因此下游效应统一方向冻结为 OneK1K BIM A1。
