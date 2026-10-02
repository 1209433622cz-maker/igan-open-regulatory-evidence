# R7B1 PBC-wide eligibility and single-causal ABF protocol v1

**Status:** frozen after R7B0A G1B passed and before any PBC-wide posterior was calculated.
**Date:** 2026-10-03.

## Fixed disease and cell universe

- Disease universe: the 56 audited GJOKA non-HLA PBC regions.
- Cell universe: the 14 OneK cell labels present in the frozen R7B0 scaffold.
- HLA and post-result loci are excluded.

## Gene and comparison inclusion

1. Read the public OneK top cis-eQTL archive only for source testability.
2. Infer each gene TSS as `lead_variant_position - tss_distance` and require consistency across cells.
3. Select a gene if its source q value is `<0.05` in at least one frozen cell.
4. Map a selected gene to a GJOKA locus when its TSS lies within the regional boundary extended by 1 Mb on either side.
5. For every mapped gene, retain every frozen cell in which that gene has an available OneK top-summary row, regardless of that cell's q value.
6. No gene, cell or locus may be added or removed using PBC colocalization results.

The source q value defines ascertainment only. R7B1 primary effect statistics use the current-release de novo PF10 model established in R7B0A.

## Variant eligibility and harmonization

- GRCh37 position and OneK BIM A1/A2 identity are required.
- Disease effects are reoriented to BIM A1.
- Unresolved palindromic or conflicting duplicate variants are excluded.
- At least 200 harmonized variants are required per locus–gene–cell comparison.
- The exact variant set and its SHA-256 receipt must be recorded.

## Single-causal screen

- Method: Wakefield ABF / coloc.abf-equivalent calculation.
- Priors: `p1=p2=1e-4`; `p12=1e-6, 1e-5, 1e-4`.
- Disease prior SD: 0.2 on the log-odds scale.
- QTL prior SD: `0.15 × sdY`; `sdY` is estimated from QTL variance, MAF and active-donor N.
- Primary screen: current-release PF10 de novo summary.
- All eligible and ineligible comparisons, with exclusion reasons, must be retained.

## Multi-signal trigger

At default `p12=1e-5`, trigger a source-matched multi-signal analysis only when either:

```text
ROBUST_H4:
PP.H4 >= 0.80 AND H4/(H3+H4) >= 0.80

H3_H4_AMBIGUITY:
PP.H3 + PP.H4 >= 0.80
AND 0.20 <= H4/(H3+H4) <= 0.80
```

The complete triggered set is frozen before any new LD matrix is built. Current PF10 is primary; current PF50 is the matched-model sensitivity.

## Exit

`R7B1A_ELIGIBILITY_PASS` requires deterministic 56-locus/14-cell processing, a frozen source-q ascertainment manifest, and explicit variant-overlap status. ABF completion then determines the exact multi-signal workload; it does not change the inclusion universe.
