# R4A8B H3 audit → H4 terminal closure plan
Date: 2026-09-10

## Decision

The H3 outputs independently reproduce the H2 RSS HOLD and provide strong evidence
that the mismatch is driven by variant-dependent meta-analysis study/sample
composition rather than by a broken allele or LD pipeline.

Recommended terminal classification for the present public-summary-statistic branch:

`HOLD_META_COVARIANCE_MISMATCH__PUBLIC_SUMMARY_STATS_NOT_SUITABLE_FOR_PAPER_GRADE_EXTERNAL_LD_SUSIE`

This does **not** invalidate the GWAS, the R4A8B reference construction, or the
signed-LD implementation.

## Frozen evidence

H2:

- 1,842 raw IL12RB2 regional GWAS rows reproduced.
- 1,555 variants retained after prespecified harmonization/QC.
- VCF REF/ALT is the allele authority.
- signed-r LD numerical gate passes.
- `estimate_s = 0.1917849`.
- max absolute kriging standardized residual = `5.361426`.
- SuSiE-RSS was correctly not run.

H3:

- H2 full-set `estimate_s` reproduced to numerical precision:
  `0.19178492023246593`.
- N_STUDIES spans 2–14.
- Spearman `|kriging residual|` vs N_STUDIES:
  rho = `-0.1674214`, P = `3.06e-11`.
- Mean `|residual|`: 1.0367 for N_STUDIES<=5 vs 0.6060 for >5.
- 26/32 variants with |residual|>3 have N_STUDIES<=5.
- Low-coverage enrichment OR = 11.53, Fisher P = 5.33e-10.
- `estimate_s` drops from 0.1918 in the full set to 0.0030 in the
  N_STUDIES=14 core.
- Changing nominal n from 5,000 to 1,000,000 leaves full-set estimate_s
  essentially unchanged (~0.1915–0.19185).

Coverage-stratified kriging further shows:

- Full set: HOLD.
- N_STUDIES>=5: estimate_s passes 0.1 but kriging residual fails.
- N_STUDIES>=8/10/12: estimate_s passes but residual still fails.
- N_STUDIES>=13 and >=14 satisfy both frozen engineering thresholds.

These higher-coverage subsets are diagnostic only and must not be used to
manufacture a fine-mapping PASS.

## Methodological interpretation

The source SSc GWAS is a 14-cohort European meta-analysis. The published methods
state that SNPs shared by at least two datasets were retained in the meta-analysis.
Therefore per-variant cohort/sample composition is intrinsically variable.

For two variants estimated from different subsets of cohorts, their sampling
covariance cannot generally be represented by one common external 1000G EUR LD
matrix. A single nominal sample size also cannot encode the missing cohort-overlap
matrix.

This directly matches the H3 pattern.

The original publication had access to cohort-level genotype data and reports
using genotype data from the 14 individual cohorts to estimate LD patterns.
Its Bayesian fine-mapping used PAINTOR. This is materially more informative than
what can be reconstructed from the public meta-analysis summary file alone.

## Important correction concerning susieR

Do not install release 0.16.0 expecting `R_finite` or `R_mismatch`.

The current latest GitHub release is 0.16.0, but the 0.16.0 `susie_rss`
signature does not expose `R_finite` or `R_mismatch`; it contains a
`sketch_samples` option for stochastic-sketch LD uncertainty.

`R_finite` and `R_mismatch` are present in the current upstream development
branch after the 0.16.0 release. Therefore any experiment using these options
must be explicitly labeled **unreleased/pinned-development-method sensitivity**,
not a stable-release analysis and not a replacement for the H2/H3 HOLD.

## H4 purpose

H4 is a terminal evidence-closure stage, not a rescue attempt.

It will:

1. Revalidate all frozen H2/H3 decision values.
2. Compute `estimate_s` separately for exact N_STUDIES strata 2–14.
3. Quantify residual burden within each exact stratum.
4. Demonstrate that N_STUDIES is a proxy for cohort composition, not a complete
   overlap descriptor.
5. Write a machine-readable terminal decision JSON.
6. Never run SuSiE-RSS.

## Next scientific target after H4

Preferred:

1. Obtain cohort-level summary statistics / cohort participation information, or
   a study with consistent per-variant sample coverage and explicit alleles/EAF/N;
   then rebuild the covariance model and fine-map.

Secondary, sensitivity-only:

2. Pin an exact upstream development commit containing `R_finite` /
   `R_mismatch`, use it in an isolated library, and treat the result as an
   experimental mismatch-aware sensitivity analysis only.

Not recommended:

- choosing an N_STUDIES cutoff because it makes the frozen threshold pass;
- deleting high residual SNPs;
- changing n_assumed to force a different result;
- presenting the N_STUDIES>=13/14 subsets as the primary fine-mapping dataset.
