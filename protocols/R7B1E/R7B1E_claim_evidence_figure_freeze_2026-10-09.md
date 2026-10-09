# R7B1E integrated claim–evidence and figure-source freeze

Date: 2026-10-09

R7B1E starts only after R7B1E0 independent QA passes. It integrates completed evidence and does not reopen gene, cell, locus or resource selection.

## Mandatory layers

1. R7B0A current-release PF10/PF50 model identity.
2. R7B1A 6,923-comparison PBC-wide ABF screen.
3. R7B1B v2 642-comparison high-information multi-signal reclassification.
4. R7B1E0 corrected kriging replay and signal-pair semantics.
5. R7B1C truth-known simulation/calibration.
6. R7B1D bounded external molecular/chromatin evidence.
7. R7A2A1 exact 5-vs-5 liver tissue boundary.

## Evidence ceiling

The manuscript may claim PBC-wide screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset. It may report bidirectional reclassification, signal-pair stability, model sensitivity and scenario-dependent calibration trade-offs.

It may not claim:

- multi-signal analysis of all 6,923 comparisons;
- general superiority over single-causal ABF;
- that every H3 comparison proves global absence of a shared signal;
- that all 92 H4 comparisons have external replication;
- a complete disease→caQTL→expression causal cascade;
- tissue mediation or PBC-specific target upregulation.

## Figure freeze

- Figure 1: study design and denominators.
- Figure 2: 642-comparison bidirectional reclassification.
- Figure 3: simulation false-H4/recovery/abstention trade-offs.
- Figure 4: IL12RB2–NK external evidence and allele direction.
- Figure 5: FCRL3 B-cell support, CD8_ET counterexample and mixed-signal semantics.
- Figure 6: exact 5-vs-5 tissue localization boundary.

Each panel requires a machine-readable source file, quantitative anchor, permitted caption and prohibited inference.

## Completion gate

R7B1E passes when the claim ledger, panel manifest, source tables, file hashes and independent QA all close. A pass advances to `R7B2_MANUSCRIPT_V1`; it does not authorize final submission without author metadata.
