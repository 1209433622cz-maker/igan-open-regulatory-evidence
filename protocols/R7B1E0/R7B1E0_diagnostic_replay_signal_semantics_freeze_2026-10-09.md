# R7B1E0 diagnostic replay and signal-semantics audit freeze

Date: 2026-10-09

## Trigger

The published R7B1B v2 runner accepted `kriging_rss()` only when its direct return was a data frame. The declared susieR 0.14.2 implementation returns a list containing `conditional_dist`. Consequently, the historical kriging fields are missing in all 2,568 comparison–configuration rows. This is a diagnostic extraction defect; it does not by itself invalidate the SuSiE or coloc posterior.

## Frozen replay inputs

- Exact 642-comparison workload frozen before R7B1B v2 results.
- Existing GJOKA summary statistics and study-matched LD.
- Existing OneK PF10/PF50 residualized LD blocks and QTL z scores.
- Exact variant intersection/order, N and `s_rss` values recorded by the completed R7B1B fits.
- susieR 0.14.2 and R 4.6.1.

No variant may be removed or reoriented in response to the replay result. The SuSiE and coloc fits are not rerun by default.

## Diagnostic rules

For each unique comparison × model (`PF10`, `PF50`), replay disease and QTL kriging with `susieR::kriging_rss()` and parse `conditional_dist`.

Two counts are retained without replacing either definition:

1. Historical frozen count: `logLR > 2`.
2. susieR plot-marking count: `logLR > 2 AND abs(z) > 2`.

Every call must return all required fields (`z`, `condmean`, `condvar`, `z_std_diff`, `logLR`), the expected number of variants and finite values. Missing/error/malformed diagnostics are `DIAGNOSTIC_NOT_EVALUATED` and block the final evidence freeze.

Calls with official-rule flags are reviewed, not automatically excluded. The review records the flagged variants, z, expected z, standardized discrepancy and logLR. A serious unresolved mismatch blocks R7B1E.

## Signal-semantics rules

Historical comparison-level labels remain unchanged. This post-result audit adds a separate semantic layer.

- `PF10_L10` is the anchor configuration.
- H4 pairs use the original default/low-prior pair-matched threshold.
- H3 pairs use the original default-prior threshold.
- Cross-L exact identity requires identical disease and QTL lead variants.
- Supporting credible-set identity requires Jaccard ≥0.50 for both disease and QTL credible sets.
- “Signal-pair stable” requires the L10 anchor to match at least one of L5/L20 by exact lead identity or by the two-trait credible-set rule.
- Coexisting H4-qualifying and H3-qualifying pairs are retained as `MIXED_SHARED_AND_DISTINCT_PAIRS`; H3 support is never interpreted as global absence of a shared signal.

This audit refines the meaning of stability. It does not overwrite the result-blind R7B1B v2 classification.

## Gate

R7B1E0 passes only if:

- all expected diagnostic units are evaluated;
- all input identities and dimensions close;
- every official-rule flag is retained and assigned a review status;
- the 642 historical classifications remain byte-identifiable;
- comparison-level and signal-pair-level stability are reported separately;
- independent QA passes.

If serious unresolved z–LD incompatibilities are found, only affected comparison/model inputs are held for investigation. The project must not silently delete variants or retune thresholds.
