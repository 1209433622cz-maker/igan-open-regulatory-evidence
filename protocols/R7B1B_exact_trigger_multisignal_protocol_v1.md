# R7B1B exact-trigger source-matched multi-signal protocol v1

**Status:** frozen on 2026-10-03 after R7B1A trigger generation and before any new PBC-wide SuSiE/coloc.susie result.
**Writing governance:** QiTeng v0.3.24.2 evidence-ceiling and deterministic-QA rules.

## Immutable input universe

- R7B1A all-comparison universe: 6,923 comparisons.
- ABF-eligible comparisons: 5,460.
- Exact multi-signal trigger set: 184 comparisons.
- Trigger composition: 112 `ROBUST_H4_TRIGGER` and 72 `H3_H4_AMBIGUITY_TRIGGER`.
- Trigger scope: 25 disease loci, 49 genes, 14 cells, and 120 unique cell–locus LD blocks.
- Trigger-set SHA-256: `bac35fe7572a336ceedcf60a19a3d4f7f8c3cd97337ebd34a2d08e5360cb1f0e`.

No comparison may be removed because its skeptical prior, source-cell q value, PF50 result, or multi-signal result is unfavorable. No new comparison may be added after this freeze.

## Disease-side inputs

- Use the GJOKA study-derived regional summary statistics and covariance/LD member for each of the exact 25 triggered loci.
- Verify remote member byte count and CRC against the frozen central-directory inventory; compute local SHA-256.
- Reconcile GJOKA variant order, alleles, and signs to the harmonized OneK BIM A1 variant set before fitting.
- A disease fit is shared by comparisons in the same locus only when its exact ordered variant set is identical; otherwise fit the exact subset separately and record its hash.

## QTL-side inputs

- PF10 primary summary: current-release de novo TensorQTL 1.0.10 formula-compatible statistics generated in R7B1A.
- PF10 LD: active-donor genotype residualized against the exact 18-column PF10 covariate model.
- Corrected PF50 sensitivity: regenerate beta/SE/z with the 58-column PF50 model and pair it with PF50-residualized LD from the same active donors and exact variant order.
- Raw genotype LD may be retained as a diagnostic only; it is not a substitute for the model-matched primary LD.

## Fit and diagnostic requirements

- Run SuSiE-RSS for disease and QTL with frozen `L` configurations and record software/session information.
- Record convergence, credible-set count/size/purity, PIP concentration, kriging/z–LD diagnostics, ordered variant hashes, and all eligible coloc.susie signal pairs.
- A numerical or identity failure is `QC_FAIL`/`NON_CONVERGENT`, never a biological negative.
- Current PF10 is the primary classification. Corrected PF50 and skeptical prior are sensitivity dimensions.

## Final classification

- `STABLE_H4`: single-causal and multi-signal support sharing; skeptical prior and PF50 do not reverse the class.
- `WEAKENED_H4`: multi-signal remains H4-predominant but misses the strict stable threshold.
- `REVERSED_TO_H3`: ABF H4 trigger becomes H3-dominant or falls below the frozen signal-pair rule.
- `UNINFORMATIVE`: no eligible signal pair or H0/H1/H2 dominance after adequate technical coverage.
- `NON_CONVERGENT_OR_QC_FAIL`: identity, LD, z–LD, convergence, or coverage failure.

All 184 rows must receive exactly one terminal class. The primary benchmark endpoint is the complete class distribution, not the count of favorable genes.

## Gate

`R7B1B_COMPLETE` requires:

1. 50/50 required GJOKA members verified;
2. 120/120 PF10 and 120/120 PF50 cell–locus model identities verified;
3. 184/184 comparisons attempted with all signal-pair outputs retained;
4. all QC failures separated from biological negatives;
5. an exact machine-readable reclassification table and independent QA PASS.

Only after this gate may the project claim a PBC-wide stable/weakened/reversed landscape and proceed to the frozen simulation benchmark.
