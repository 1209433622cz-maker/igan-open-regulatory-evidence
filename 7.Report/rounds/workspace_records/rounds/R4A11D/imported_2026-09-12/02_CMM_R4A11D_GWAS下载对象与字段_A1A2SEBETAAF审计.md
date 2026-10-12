# FinnGen R12/R13 GWAS 文件与字段适配审计

## 1. Standard all-sex GWAS

FinnGen 当前标准 summary-statistics schema：

| 需求概念 | FinnGen列 | 是否满足 |
|---|---|---|
| chromosome | `#chrom` | YES |
| position | `pos` | YES |
| A2 / non-effect allele | `ref` | **YES（语义等价；不是字面A2列）** |
| A1 / effect allele | `alt` | **YES（ALT为effect allele）** |
| rsID | `rsids` | YES |
| P | `pval` | YES |
| BETA | `beta` | **YES** |
| SE | `sebeta` | **YES** |
| AF | `af_alt` | **YES** |
| case AF | `af_alt_cases` | YES |
| control AF | `af_alt_controls` | YES |
| INFO | annotation file | **不在主summary列；需join release annotation** |
| sample N | phenotype summary / pheno_n | **不建议从summary行推断** |

坐标是 GRCh38。对 binary endpoint，beta 是 ALT allele 的 log-odds effect。

### 与旧 GCST009131 的本质差异

GCST009131 旧overall文件需要处理 A2=`?`、无原始SE、GRCh37等问题。FinnGen R12/R13标准full summary天然带 `ref/alt/beta/sebeta/af_alt`，因此更适合直接进入现代harmonization、coloc和SMR流程。

## 2. R12 sex-specific files

官方在 2024-05-06 发布：

- female-only + male-only REGENIE results：2,207 endpoints；
- 262 endpoints因不适合sex-specific分析未提供；
- female–male inverse-variance meta；
- Cochran Q heterogeneity；
- 聚合GWS结果。

Green Library路径：

```text
gs://finngen-production-library-green/finngen_R12/finngen_R12_analysis_data/sex_difference/summary_stats/
gs://finngen-production-library-green/finngen_R12/finngen_R12_analysis_data/sex_difference/meta_analysis/meta_summary_stats/
gs://finngen-production-library-green/finngen_R12/finngen_R12_analysis_data/sex_difference/meta_analysis/sex_specific_meta_gwsig_in_either_sex_all_endpoints.tsv.gz
```

exclusion list：

```text
gs://finngen-production-library-green/finngen_R12/finngen_R12_analysis_data/sex_difference/regenie_single_sex_drop_list_plus_reason_262_endpoints.txt
```

meta文件关键列：

`#CHR POS REF ALT SNP female_beta female_se female_pval female_af_alt ... male_beta male_se male_pval male_af_alt ... all_inv_var_het_p rsid`

其中：

- ALT = effect allele；
- `all_inv_var_het_p` = female vs male Cochran Q heterogeneity P；
- female-male sex-difference beta 在PheWeb中定义为 female_beta - male_beta。

**本项目下一步必须实际读取exclusion list，确认 `M13_SYSTSLCE` 是否包含。病例数大于阈值并不能代替这个字节级验收。**

## 3. R13 sex-specific 状态

截至本轮核查，R13 release notes / core-analysis documentation明确提供 standard GWAS、fine-mapping、autoreporting等，但**没有发现一个与R12对应的、被官方文档明确发布的R13 female/male sex-specific GWAS release。**

因此：

- R13 all-sex：可作为最新疾病输入；
- R13 female/male：**NOT_OFFICIALLY_DOCUMENTED_IN_CHECKED_SOURCES**；
- 禁止根据R12路径命名规则“猜一个R13 sex_difference目录”并当作正式输入。

## 4. GWAS下载入口

### R12 public

Manifest：

```text
https://storage.googleapis.com/finngen-public-data-r12/summary_stats/finngen_R12_manifest.tsv
```

Green Library core summary：

```text
gs://finngen-production-library-green/finngen_R12/finngen_R12_analysis_data/summary_stats/release/
```

### R13 public / Green

Manifest：

```text
https://storage.googleapis.com/finngen-public-data-r13/summary_stats/finngen_R13_manifest.tsv
```

Green Library：

```text
gs://finngen-production-library-green/finngen_R13/finngen_R13_analysis_data/summary_stats/
```

### 推荐下载原则

不要手工拼接 guessed URL 作为最终provenance。正确流程：

1. 下载manifest；
2. 按endpoint精确过滤 `M13_SYSTSLCE`, `SYSTSCLE_STRICT`, `CREST`；
3. 保存manifest行；
4. 按manifest提供的URL下载；
5. 记录bytes/hash/release/build/schema；
6. 再进入H6/P0。
