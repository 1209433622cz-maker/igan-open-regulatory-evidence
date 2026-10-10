# R7C1 — IL12RB2 External Validation Module + Manuscript Fork

## Purpose

R7C1 may add the R7C0 external evidence module to a new manuscript branch. The author-approved R7B4B2 submission candidate remains an immutable Q2 baseline.

## Frozen inputs

- FinnGen R13 `CHIRBIL_PRIM` IL12RB2-region summary statistics and disease credible set;
- the frozen OneK NK/IL12RB2 PF10 QTL input and source credible set;
- the prespecified CASCADE IL12RB2-linked peak `chr1-67307618-67308670`;
- R7C0 machine tables, source ledger and 25/25 independent QA result.

## Allowed analyses

1. Add a source-bound Methods module for the FinnGen R13 disease signal, the GRCh37/GRCh38 rsID bridge, single-causal ABF external validation and source-CS overlap.
2. Add bounded Results for R12/R13 disease-CS stability, FinnGen R13 × OneK NK/IL12RB2 signal sharing and the disease–eQTL / disease–caQTL / peak–gene triangle.
3. Assemble one external-validation figure and its source tables.
4. Update the abstract and Discussion while preserving the attribution-reliability and calibration framework as the manuscript's primary contribution.
5. Run hostile claim, numeric, reference and reader-facing QA before any journal re-ranking.

## Prohibited analyses and claims

```text
NEW_GENE_LOCUS_CELL_FISHING = NO
FULL_642_RERUN = NO
REOPEN_FCRL3_AS_FINNGEN_POSITIVE = NO
OMIX_AS_INDEPENDENT_REPLICATION = NO
PERSON_LEVEL_ZERO_OVERLAP_CLAIM = NO
DIRECT_EQTL_CAQTL_POSTERIOR_CLAIM = NO
DIRECT_MEDIATION_CLAIM = NO
OVERWRITE_R7B4B2 = NO
```

## Required wording boundaries

- FinnGen provides a different disease study system; person-level zero overlap has not been demonstrated.
- The external FinnGen R13 × OneK analysis is single-causal validation with a source-CS audit, not a second source-LD multi-signal fit.
- The chromatin result is triangular signal coherence. A direct eQTL–caQTL posterior and causal mediation estimate are unavailable.
- OMIX001122 supports descriptive detectability only because it contains one control and one PBC spatial matrix without independent donor replication.

## Exit gate

Continue the upgraded manuscript only if every new number maps to a frozen machine table, the above boundaries survive hostile review, and the external module adds a defensible journal-facing contribution. Otherwise retain the unchanged R7B4B2 baseline and stop the upgrade without changing project or candidate set.

## Next state

```text
R7C1 = GO_BOUNDED
PRIMARY_TARGET = IL12RB2_NK_EXTERNAL_VALIDATION_MODULE
Q2_BASELINE = R7B4B2_FROZEN
NEW_CANDIDATE_DISCOVERY = PROHIBITED
```
