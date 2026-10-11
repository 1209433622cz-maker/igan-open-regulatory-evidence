# CMM R4A — 数据访问实测与 Manifest v2

**核查日期**：2026-09-08

---

# 1. 数据状态分级定义

为了避免“公开”与“已取得”混用，本项目统一使用：

- **PUBLISHED**：论文/资源已发表；
- **PUBLIC_DECLARED**：官方明确声明对公众开放；
- **MANIFEST_VERIFIED**：文件名/内容类别/大小/校验信息至少部分可核查；
- **BYTES_ACQUIRED**：实际文件已进入分析环境；
- **SCHEMA_VERIFIED**：已检查header/build/allele/columns；
- **ANALYSIS_READY**：可直接进入预注册统计流程。

---

# 2. 2026 sex-specific SSc GWAS

## Publication
- PMID: 41999721
- DOI: 10.1016/S2665-9913(25)00376-5
- Journal: The Lancet Rheumatology
- Publication: 2026

## Cohort
- SSc cases: 10,653
- controls: 18,043
- male: 1,556 cases + 6,990 controls
- female: 9,097 cases + 11,053 controls
- variants analysed:
  - male ~9.54 million
  - female ~9.60 million
- ancestry: European meta-analysis

## Data sharing statement
论文明确声明 sex-specific meta-analysis summary statistics 将通过 NHGRI–EBI GWAS Catalog 公布。

## 本轮实际状态
```text
PUBLISHED = YES
PUBLIC_DECLARED = YES
GCST_ACCESSION_RESOLVED = NO
BYTES_ACQUIRED = NO
SCHEMA_VERIFIED = NO
ANALYSIS_READY = NO
```

## 处理规则
绝不从Figure 2的LocusZoom图片反向数字化成“summary statistics”。

绝不把Table 1 lead SNP当作完整区域数据进行coloc。

---

# 3. FinnGen single-nucleus multiome

## Official release
Public release: **2026-08-13**

## Resource scale
- 1,108 individuals
- 10,612,211 snRNA nuclei
- 7,100,899 snATAC nuclei
- 33 cell types
- 27,294 genes
- 297,024 chromatin accessibility peaks
- 17,167,198 variants

## Available result families
- cis-eQTL summary statistics
- cis-caQTL summary statistics
- SuSiE fine-mapping
- peak-gene links
- CASCADE categorization
- GWAS colocalization
- consensus peaks
- per-cell-type accessibility tracks

## Access route
官方要求：
1. online form；
2. email instructions；
3. download。

## 本轮状态
```text
PUBLIC_DECLARED = YES
RESOURCE_CONTENT_VERIFIED = YES
BROWSER_VERIFIED = YES
FILE_MANIFEST_BYTES = NO
BYTES_ACQUIRED = NO
SCHEMA_VERIFIED = NO
ANALYSIS_READY = NO
```

## 必须获取的最小数据
不需要一开始全量下载。

优先：
1. cell-type manifest；
2. eQTL index / region-readable summary；
3. caQTL index / region-readable summary；
4. SuSiE credible-set summary；
5. peak-gene links；
6. variant annotation/allele metadata。

---

# 4. TenK10K Phase 1

## Zenodo
DOI: **10.5281/zenodo.18221260**

## Verified file manifest

| File | Purpose | Size | MD5 |
|---|---|---:|---|
| common_variant_gene_level_results_with_annotated_fails.zip | 28 cell types, top common cis-eQTL per gene | 10.1 MB | b5cd2ee1f34f90539ebf6683dcd35a2e |
| susie_summary.zip | 95% credible-set variants by cell type | 59.7 MB | f321c719030cc837cf27e09cd2ea6b65 |
| common_all_cis_pvalues_100kb.zip | full ±100kb cis stats | 16.6 GB | dd54714b2effb91160ac171ccb941534 |
| coloc_100kb.zip | existing coloc results by trait/cell/chromosome | 626.5 MB | c627f1c4bc47706e331039d1e9e6e7d1 |

## R4A推荐下载策略

### Phase 1
只下载：
- 10.1 MB gene-level
- 59.7 MB SuSiE

用于：
- 是否存在目标gene eQTL；
- 哪些cell types最强；
- target是否有fine-mapped common variants。

### Phase 2
只有目标通过Phase 1才考虑：
- 16.6GB 100kb full summary stats；
或按可用方式获取必要region。

这可以避免为一个可能失败的target先下载170GB级别资源。

## 本轮状态
```text
PUBLIC = YES
MANIFEST_VERIFIED = YES
CHECKSUM_METADATA = YES
BYTES_ACQUIRED_IN_SESSION = NO
```

---

# 5. SSc disease tissue datasets

R4A继续维持R3冻结，不提前扩大下载。

| Dataset | Role | R4A status |
|---|---|---|
| GSE312129 | 主SSc skin snRNA+snATAC+spatial | HOLD until Tier-1 genetic target |
| GSE249279 | independent skin scRNA/spatial replication | HOLD |
| GSE236111 | IFN/endothelial targeted validation | CONDITIONAL |
| GSE312932 | high-resolution Xenium | DEFER |
| GSE312591 | RUNX1 perturbation | ONLY IF RUNX1 AXIS EMERGES |

---

# 6. 当前真正缺失的文件

## Blocking
- male SSc full GWAS summary stats
- female SSc full GWAS summary stats
- FinnGen multiome eQTL/caQTL/fine-map/peak-gene files

## Non-blocking but useful
- TenK10K 10.1MB gene-level archive
- TenK10K 59.7MB SuSiE archive

---

# 7. 可重复性记录要求

文件一旦取得，立即生成：

```text
source_manifest.tsv
checksums.sha256
headers/
build_report.md
allele_report.md
celltype_dictionary.tsv
variant_normalization_log.tsv
```

任何文件只有达到：

```text
BYTES_ACQUIRED + SCHEMA_VERIFIED
```

才允许进入统计分析。


## 关键来源（核查日期：2026-09-08）

1. Rodriguez-Martin I, et al. *Sex-specific autosomal susceptibility loci in systemic sclerosis: a genome-wide association study.* Lancet Rheumatology. 2026;8(6):e438-e450. PMID: 41999721. DOI: 10.1016/S2665-9913(25)00376-5.
2. FinnGen. *Access results — FinnGen single-nucleus multiome*, public release 2026-08-13. https://www.finngen.fi/en/access_results
3. Cuomo ASE, et al. TenK10K Phase 1 sc-eQTL data. Zenodo record 18221260. DOI: 10.5281/zenodo.18221260.
4. Praetorius C, et al. Functional studies of IRF4 rs12203592 and subsequent cell-type-specific eQTL work (Genome Research / related mechanistic studies).
5. Existing R3 frozen protocol in this project: `03_CMM_R3_统计兼容性与冻结分析协议_v1.md`.

> 注：本轮严格区分“网页声明可用”“已确认文件清单”“已实际取得文件字节”。未实际取得的数据不会被写成已完成分析。
