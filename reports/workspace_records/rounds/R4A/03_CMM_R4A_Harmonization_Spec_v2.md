# CMM R4A — Harmonization Specification v2

**状态**：FROZEN BEFORE DATA  
**目的**：把后续最容易被“看结果后调整”的规则预先固定。

---

# 1. Canonical build

**Target build = GRCh38**

Canonical variant key:

```text
chr:pos:ref:alt@GRCh38
```

rsID只做辅助，不作为唯一合并键。

---

# 2. Required source columns

## GWAS
至少需要：
- chr
- pos
- ref
- alt
- effect allele
- non-effect allele / recoverable counterpart
- beta or log(OR)
- SE
- P
- EAF/AF if available
- N or N_case/N_control
- build
- imputation quality if available

## eQTL / caQTL
至少需要：
- variant canonical coordinates
- ref/alt
- effect allele
- beta
- SE / P
- molecular phenotype id
- gene/peak
- cell type
- N
- build

## SuSiE
- signal/credible-set id
- PIP
- CS membership
- CS coverage if available
- phenotype/cell type
- variant

## peak–gene
- peak id / coordinates
- gene id
- score / method
- cell type if cell-specific

---

# 3. Allele harmonization

For each source:

```text
raw_ref
raw_alt
raw_effect
raw_beta
↓
normalize variant
↓
reference-genome REF validation
↓
orient to canonical ALT or chosen effect allele
↓
record flip status
```

输出必须保留：
- `was_strand_flip`
- `was_allele_swap`
- `was_liftover`
- `was_indel_normalized`
- `drop_reason`

---

# 4. Ambiguous SNPs

A/T and C/G:
- no AF → default drop from direction-dependent integration;
- AF available → only retain with unambiguous cross-source frequency compatibility;
- never guess orientation from rsID.

---

# 5. Indel rule — rs66578187重点

对 `rs66578187`：

1. 从每个实际source读取REF/ALT，不根据论文effect allele `AT` 猜REF；
2. `bcftools norm` equivalent left-normalization；
3. verify against GRCh38 reference;
4. split multi-allelic if necessary;
5. regenerate canonical key;
6. compare allele sequence across GWAS / FinnGen / TenK10K;
7. if one source uses symbolic/insertion coding incompatible with recovery → mark unresolved rather than force-match.

---

# 6. Locus windows

Initial smoke:
- ±500 kb around GWAS lead only for acquisition/indexing.

Statistical region:
- prefer signal-defined region / credible-set context;
- do not truncate strong LD signal merely to fixed window.

---

# 7. LD

For sex-SSc GWAS:
- European ancestry LD reference;
- prefer source-provided or ancestry-matched modern reference;
- Finnish LD is not automatically interchangeable with multi-cohort European SSc GWAS LD.

For FinnGen QTL:
- prioritize source-provided SuSiE fine-mapping;
- do not refit fine-map with generic 1000G unless sensitivity analysis.

---

# 8. Colocalization

Primary:
- signal-aware / SuSiE-aware where possible.

Required comparisons:
1. SSc GWAS ↔ caQTL
2. SSc GWAS ↔ eQTL
3. caQTL ↔ eQTL

C1 requires compatible evidence across the chain plus peak–gene mapping.

Approximate evidence labels:
- strong shared posterior ≥0.80;
- 0.50–0.80 = moderate, requires orthogonal support;
- <0.50 = not Tier-1.

No single threshold is treated as proof of causality.

---

# 9. Replication

TenK10K replication is defined before result viewing:

- same gene;
- exact or pre-mapped compatible cell lineage;
- same allele→expression direction if orientation can be resolved;
- independent donor cohort.

`all T cells = replication` is not allowed.

---

# 10. Negative result taxonomy

Every failed locus must be classified:

```text
ACCESS_FAILURE
SCHEMA_FAILURE
COVERAGE_FAILURE
ALLELE_UNRESOLVED
NO_QTL
QTL_DIFFERENT_SIGNAL
PEAK_GENE_AMBIGUOUS
NO_REPLICATION
BIOLOGICAL_NEGATIVE
```

Only `BIOLOGICAL_NEGATIVE` should count strongly toward disease-project NO-GO.

---

# 11. Reproducibility outputs

Per locus:

```text
01_raw_manifest.tsv
02_variant_normalization.tsv
03_gwas_region.tsv.gz
04_eqtl_region.tsv.gz
05_caqtl_region.tsv.gz
06_finemap_cs.tsv
07_coloc_summary.tsv
08_peak_gene.tsv
09_replication.tsv
10_cascade_evidence.tsv
11_QC.md
```


## 关键来源（核查日期：2026-09-08）

1. Rodriguez-Martin I, et al. *Sex-specific autosomal susceptibility loci in systemic sclerosis: a genome-wide association study.* Lancet Rheumatology. 2026;8(6):e438-e450. PMID: 41999721. DOI: 10.1016/S2665-9913(25)00376-5.
2. FinnGen. *Access results — FinnGen single-nucleus multiome*, public release 2026-08-13. https://www.finngen.fi/en/access_results
3. Cuomo ASE, et al. TenK10K Phase 1 sc-eQTL data. Zenodo record 18221260. DOI: 10.5281/zenodo.18221260.
4. Praetorius C, et al. Functional studies of IRF4 rs12203592 and subsequent cell-type-specific eQTL work (Genome Research / related mechanistic studies).
5. Existing R3 frozen protocol in this project: `03_CMM_R3_统计兼容性与冻结分析协议_v1.md`.

> 注：本轮严格区分“网页声明可用”“已确认文件清单”“已实际取得文件字节”。未实际取得的数据不会被写成已完成分析。
