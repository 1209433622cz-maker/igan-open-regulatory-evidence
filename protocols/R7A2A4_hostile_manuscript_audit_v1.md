# R7A2A4 frozen protocol — Hostile Manuscript Audit

## Entry state

R7A2A3 manuscript draft v1, claim ledger, reference ledger, methods–results mirror, reviewer-risk map, and figure-role map are complete.

## Objective

Test whether every reader-facing claim is supported by the frozen evidence and whether the manuscript can survive a skeptical genetics/molecular-QTL review without adding new biological targets.

## Required tasks

1. Perform a clause-level claim-to-source audit for Title, Abstract, Results, Discussion, Conclusion, and every figure legend.
2. Re-run a current primary-literature search for FCRL3, IL12RB2, PBC colocalization, source-matched LD, and PBC single-cell studies.
3. Verify every numerical value against the frozen upstream tables and report exact mismatches.
4. Audit first-appearance reference order, metadata, DOI, orphan citations, and support ownership.
5. Simulate at least two hostile reviews: statistical genetics and liver single-cell biology.
6. Repair Figure 1 layout and Figure 3 low-prior semantics; verify Figure 2/4 distinction between multi-signal discovery and single-causal replication.
7. Confirm Methods–Results mirror and route reproducibility detail to Supplement without deleting it.
8. Produce a decision ledger: KEEP, REWRITE, DOWNGRADE, MOVE_TO_SUPPLEMENT, or BLOCK.

## Prohibited scope expansion

- No new PBC locus, gene, or cell type.
- No restoration of archived SSc, MG, IgAN, or CeD projects.
- No conversion of tissue detectability into differential expression.
- No mechanistic, therapeutic, or causal claim without new direct evidence.
- No target-journal formatting until a journal is selected using the completed scientific audit.

## Exit criteria

```text
CLAIM_SOURCE_AUDIT = PASS
NUMERIC_AUDIT = PASS
REFERENCE_AUDIT = PASS
FIGURE_CLAIM_GATE = PASS
TWO_HOSTILE_REVIEWS = RESOLVED_OR_LOGGED
AUTHOR_METADATA_BLOCKERS = EXPLICIT
```

If all scientific gates pass, the next stage is `R7A2A5_TARGET_JOURNAL_AND_SUBMISSION_FORMAT`. If a core claim fails, return to a bounded R7A2A3 revision without opening new analyses.
