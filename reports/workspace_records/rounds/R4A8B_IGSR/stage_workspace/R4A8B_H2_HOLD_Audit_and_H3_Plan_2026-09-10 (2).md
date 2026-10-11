# R4A8B H2 audit and H3 diagnostic plan — 2026-09-10

## Executive status

**H2 pipeline result:** `R4A8B_H2_HARMONIZATION_SIGNED_LD_PASS`

**RSS result:** `DIAGNOSTIC_HOLD`

**Recommended project-level interpretation:**

- Engineering validity of the R4A8B harmonization + signed-LD pipeline: **GO**
- Fine-mapping/credible-set inference from the current GCST009131 regional summary statistics + external EUR503 LD: **HOLD**
- Do not delete variants or weaken the diagnostic thresholds to force SuSiE-RSS to run.
- The next stage should diagnose why the z-score covariance is inconsistent with a single external LD matrix, with special attention to the strong variation in `N_STUDIES`.

## Frozen H2 evidence

Reference branch:

- 1000 Genomes Phase 3 v5a, GRCh37
- EUR reference n = 503
- IL12RB2 region = chr1:67,306,207–68,306,207
- Regional reference SNPs = 27,067
- Reference branch explicitly remains independent of the blocked Zenodo exact-MD5 branch.

GWAS and harmonization:

- GCST009131 regional rows reproduced from raw source = 1,842
- Signed-Z reproduction = PASS
- Retained for LD = 1,555 (84.42%)
- Excluded palindromic SNPs without GWAS EAF = 264
- Excluded because no unique rsID+position VCF match = 18
- Excluded because panel MAF <1% = 5
- Allele authority = VCF REF/ALT
- Genotype dosage orientation = GWAS A1

LD numerical QC:

- LD dimension = 1,555 × 1,555
- Matrix rank = 394
- Minimum eigenvalue = -1.7404e-13
- Maximum diagonal error = 3.5527e-15
- Maximum asymmetry = 0
- rs3790566/rs3790567 signed r = 0.994614
- rs3790566/rs3790567 r² = 0.989257
- Numerical LD gate = PASS

The rank of 394 is not itself a failure: with only 503 reference individuals, a centered genotype correlation matrix cannot have full rank across 1,555 variants. The tiny negative eigenvalue is numerical floating-point error and is well inside the frozen tolerance.

## Why H2 correctly stopped

Frozen RSS diagnostic:

- `estimate_s = 0.1917849`
- maximum absolute kriging standardized residual = `5.361426`
- frozen rule: HOLD when `estimate_s > 0.1` OR max absolute standardized residual >5
- therefore `diagnostic_pass = FALSE`
- `susie_rss = NOT_RUN`

This is a scientifically valid terminal outcome for H2. It should not be converted to PASS by removing the most discordant variants.

## New root-cause evidence from the uploaded H2 outputs

A static audit of the retained 1,555 variants shows that RSS inconsistency is strongly concentrated among variants contributed by fewer studies.

### Residual burden versus study coverage

- Spearman correlation between `abs(kriging standardized residual)` and `N_STUDIES`:
  - rho = -0.1674
  - P = 3.06e-11
- Mean absolute residual:
  - `N_STUDIES <= 5`: 1.0367
  - `N_STUDIES > 5`: 0.6060
  - one-sided Mann–Whitney P ≈ 6.04e-17
- Among 32 variants with `|standardized residual| > 3`:
  - 26 (81.25%) have `N_STUDIES <= 5`
- Enrichment of `|residual| > 3` among `N_STUDIES <= 5`:
  - odds ratio ≈ 11.53
  - Fisher exact P ≈ 5.33e-10
- All six variants with `|residual| > 4` have `N_STUDIES <= 7`.

The single most discordant variant is `rs3766264`:

- standardized residual = -5.3614
- `N_STUDIES = 2`
- heterogeneity I² = 85.52%
- A1 is present in VCF REF/ALT and the dosage orientation passed the allele gates.

This pattern does not look like a simple global allele-orientation failure.

### `estimate_s` versus study-coverage stability

Using the same null-MLE definition as `susieR::estimate_s_rss` and reproducing the full-set value to numerical precision:

| Retention diagnostic | Variants | estimate_s |
|---|---:|---:|
| N_STUDIES >= 2 (full H2) | 1555 | 0.191785 |
| N_STUDIES >= 3 | 1434 | 0.157120 |
| N_STUDIES >= 4 | 1305 | 0.129000 |
| N_STUDIES >= 5 | 1194 | 0.098983 |
| N_STUDIES >= 6 | 1113 | 0.092522 |
| N_STUDIES >= 7 | 966 | 0.090217 |
| N_STUDIES >= 8 | 857 | 0.070538 |
| N_STUDIES >= 9 | 792 | 0.062326 |
| N_STUDIES >= 10 | 724 | 0.059722 |
| N_STUDIES >= 11 | 639 | 0.056094 |
| N_STUDIES >= 12 | 544 | 0.055159 |
| N_STUDIES >= 13 | 387 | 0.041189 |
| N_STUDIES = 14 | 134 | 0.002963 |

This monotonic collapse is highly informative. It strongly suggests that the full regional z-vector is not well described by one common covariance structure because different variants were meta-analyzed across substantially different sets/numbers of contributing studies.

**Important:** these subset calculations are diagnostic only. They are not permission to discard low-coverage variants and claim a fine-mapping PASS.

### Engineering n is not the main cause

Full-set `estimate_s` is essentially unchanged over a very broad assumed-N range:

| assumed n | estimate_s |
|---:|---:|
| 5,000 | 0.191510 |
| 10,000 | 0.191679 |
| 15,000 | 0.191735 |
| 20,000 | 0.191764 |
| 26,679 | 0.191785 |
| 30,000 | 0.191792 |
| 40,000 | 0.191806 |
| 50,000 | 0.191815 |
| 100,000 | 0.191832 |
| 1,000,000 | 0.191847 |

Therefore simply changing `n_assumed = 26679` cannot repair the current mismatch.

## Scientific interpretation

The most likely problem is now **summary-statistic covariance heterogeneity**, not a broken LD matrix.

GCST009131 contains substantial variant-to-variant variation in `N_STUDIES` (2–14 among retained SNPs). When two SNPs were not estimated from the same effective set of cohorts/samples, their z-score covariance is not necessarily represented by one fixed external 1000G EUR correlation matrix. A single nominal `n` also cannot encode this changing overlap structure.

This interpretation is consistent with:

1. Strong allele and identity QC.
2. Exact signed-Z reproduction from the frozen GWAS source.
3. Clean LD numerical QC.
4. Very strong positive-control LD.
5. No systematic residual excess by REF-versus-ALT orientation.
6. Large reduction in `estimate_s` as study coverage becomes more uniform.
7. Near-zero `estimate_s` in the N_STUDIES=14 diagnostic subset.

## H3 objective

H3 is a **root-cause diagnostic**, not a fine-mapping stage.

It will:

1. Reproduce the H2 full-set `estimate_s`.
2. Run study-coverage sensitivity across prespecified N_STUDIES thresholds.
3. Test sensitivity to the engineering sample-size approximation.
4. Re-run kriging on selected coverage-defined subsets.
5. Quantify whether the mismatch disappears as study coverage becomes stable.
6. Never invoke `susie_rss` and never remove variants to manufacture a PASS.

## Decision after H3

### If the coverage trend reproduces

Classify the current GCST009131 + external-LD fine-mapping input as:

`HOLD_META_COVARIANCE_MISMATCH`

Then prioritize one of the following for paper-grade inference:

- Obtain summary statistics from a GWAS with consistent per-variant cohort/sample coverage and explicit A1/A2, EAF, SE and per-variant N.
- Obtain cohort-level or cohort-consistent summary data enabling an LD/sample-overlap-aware model.
- Use a newer mismatch-aware SuSiE method only as a clearly separated sensitivity branch, not as a way to erase the H2 HOLD.

### Newer SuSiE branch

The frozen H2 used CRAN `susieR 0.14.2`. A newer GitHub release (0.16.0) and current upstream documentation include finite-reference and broader LD-mismatch modeling (`R_finite` and `R_mismatch`). Because 0.16.0 is not the frozen CRAN baseline used by H2, any use should be isolated as a new method-sensitivity branch, with version and source pinned.

A reasonable later experiment would be:

- preserve H2 unchanged;
- install/pin the newer release in a separate R library;
- use `R_finite = 503`;
- evaluate `R_mismatch = "eb"`;
- inspect the newer finite-reference/mismatch diagnostics;
- compare with the conservative H2/H3 conclusions.

This should happen only after H3 confirms the coverage-driven mismatch pattern.

## Project-level state

- R4A8 exact Zenodo branch: `HOLD_EXTERNAL_ZENODO_DELIVERY`
- R4A8B H1 reference construction: `PASS`
- R4A8B H2 harmonization + signed LD: `PASS`
- R4A8B H2 RSS consistency: `HOLD`
- R4A8B overall engineering pipeline: `GO`
- Current GCST009131 paper-grade credible-set inference: `HOLD`
- Next stage: `R4A8B-H3 STUDY-COVERAGE / META-COVARIANCE DIAGNOSTIC`
