# R4A8B H4 audit and H5 data-acquisition gate
Date: 2026-09-10

## H4 terminal closure: independently reviewed

The uploaded H4 outputs are internally consistent and support the frozen terminal classification:

`HOLD_META_COVARIANCE_MISMATCH__PUBLIC_SUMMARY_STATS_NOT_SUITABLE_FOR_PAPER_GRADE_EXTERNAL_LD_SUSIE`

This classification applies to the **current combination** of:

- GCST009131 public meta-analysis summary statistics;
- a single external 1000 Genomes Phase 3 v5a EUR503 LD reference;
- paper-grade SuSiE-RSS credible-set inference.

It does not invalidate the GWAS itself or the R4A8B engineering pipeline.

### Frozen state

- H1 reference construction: PASS
- H2 raw GWAS reproduction: PASS
- H2 allele harmonization: PASS
- H2 signed-r LD: PASS
- H2 numerical LD QC: PASS
- H2 full-set RSS consistency: HOLD
- H3 meta-covariance diagnosis: PASS
- H4 terminal closure: PASS
- Primary SuSiE-RSS: NOT RUN

### H4 exact-study-count diagnostic

| Exact N_STUDIES | Variants | estimate_s |
|---:|---:|---:|
| 2 | 121 | 0.376285 |
| 3 | 129 | 0.154807 |
| 4 | 111 | 0.107755 |
| 5 | 81 | 0.115493 |
| 6 | 147 | 0.016544 |
| 7 | 109 | 0.043943 |
| 8 | 65 | 0.063333 |
| 9 | 68 | 0.035100 |
| 10 | 85 | 0.072788 |
| 11 | 95 | 0.019861 |
| 12 | 157 | 0.032828 |
| 13 | 253 | 0.019098 |
| 14 | 134 | 0.002963 |

The non-monotonic exact-stratum pattern is useful: N_STUDIES is a proxy, not the
complete covariance descriptor. SNPs with the same study count can still come from
different subsets of cohorts.

The N_STUDIES=14 stratum is the strongest internal positive control because the
2019 SSc meta-analysis contained 14 cohorts. Its very small estimate_s is therefore
consistent with the hypothesis that stable cohort composition greatly improves
z-LD consistency.

## New external evidence affecting the next target

A 2026 sex-specific SSc GWAS has now been published:

Rodriguez-Martin et al., *The Lancet Rheumatology* (2026),
DOI 10.1016/S2665-9913(25)00376-5, PMID 41999721.

Important features:

- 15 European cohorts.
- Final data: 10,653 SSc cases and 18,043 controls.
- 9,097 female cases + 11,053 female controls.
- 1,556 male cases + 6,990 male controls.
- IL12RB2 is specifically highlighted as a female-specific locus.
- Lead IL12RB2 variant: rs6662198, effect allele C.
- Female association: OR 0.83 (95% CI 0.79–0.87), P=8.52e-13.
- Male association: OR 0.98, P=0.64.
- The paper states that full sex-specific GWAS summary statistics will be made
  available through the NHGRI-EBI GWAS Catalog after publication.

This is now the highest-value public-data target for the IL12RB2 branch because
it is newer, directly implicates IL12RB2, and provides a biologically meaningful
sex-stratified validation axis.

## Important constraints

Do not assume that the 2026 summary statistics are already downloadable or guess
their GCST accession.

Do not assume the genome build. The article's lead-variant table reports hg38
coordinates, so the downloaded summary-statistic metadata/build must be checked
before reusing the GRCh37 R4A8B reference.

Do not treat the 2026 sex-specific dataset as a replacement for the H4 HOLD until
its own per-variant coverage, alleles, sample-size fields, and z-LD consistency
have passed independent gates.

## H5 objective

`R4A8B-H5_2026_SEX_SPECIFIC_SSC_GWAS_ACQUISITION_GATE`

H5 should:

1. Query the official GWAS Catalog v2 API in real time.
2. Use GCST009131 as a positive-control API query.
3. Query PMID 41999721 for all curated studies.
4. Query the same PMID with `full_pvalue_set=true`.
5. Save all raw API responses.
6. Extract any GCST accession IDs without guessing them.
7. Classify availability as:
   - `GO_2026_SEX_SPECIFIC_SUMSTATS_DISCOVERED`,
   - `HOLD_CATALOG_CURATED_BUT_SUMSTATS_NOT_FLAGGED`,
   - or `HOLD_2026_PUBLICATION_NOT_YET_CURATED_OR_INDEXED`.
8. Preserve H1-H4 unchanged.

## Next decision after H5

### If summary statistics are available

Proceed to H6:

`2026 sex-specific SSc GWAS schema/build/coverage audit`

Before any fine-mapping:

- identify female, male, combined and interaction analyses;
- verify genome build;
- verify effect/non-effect allele;
- verify beta/OR and SE;
- verify EAF;
- verify per-variant N or cohort coverage;
- independently reconstruct signed Z;
- quantify IL12RB2 regional row completeness;
- build a native-build reference;
- run the same z-LD diagnostic gates used in H2.

Female IL12RB2 should be the primary new validation branch because the 2026 study
reports a strong female-specific association.

### If summary statistics are not yet available

Freeze H5 as an availability HOLD and do not waste effort reconstructing data from
top-hit tables.

The next actionable route is to request the sex-specific summary statistics from
the corresponding authors or wait for the GWAS Catalog deposit, while optionally
using the published rs6662198 signal only as external locus-level validation.

## Current overall project state

`R4A8B engineering pipeline = GO`

`GCST009131 public summary + one external EUR LD = terminal HOLD for paper-grade SuSiE`

`Next highest-value target = 2026 sex-specific SSc summary-statistics acquisition`
