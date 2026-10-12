# R7A1B v2 Frozen Protocol — PBC 3-control bounded signal gate

Date: 2026-09-15

## Frozen genes and OneK cell combinations

- IL12RB2: NK only.
- FCRL3: B_IN, B_MEM, CD4_NC, CD8_ET, CD8_NC, NK, NK_R.
- INAVA (OneK source symbol C1orf106): CD4_NC only.

Maximum smoke comparisons: 9.

No post-hoc gene or cell replacement is allowed.

## Disease inputs

Primary PBC summary statistics:
`GCST90061440`, GRCh37, 8,021 cases / 16,489 controls.

Study-matched disease LD:
Gjoka/Cordell locus 2 / 4 / 6.

## Amendment to v1

Published disease fine-mapping is frozen BEFORE observing R7A1B coloc results:

- locus 2 / 1p31.3 / IL12RB2: SuSiE-RSS has TWO disease credible signals (CS sizes 1 and 4).
- locus 4 / 1q23.1 / FCRL3: one disease credible signal (size 33).
- locus 6 / 1q32.1 / INAVA: one disease credible signal (size 33).

Therefore:

`IL12RB2 × NK` is forced into two-sided source-LD/SuSiE adjudication even if single-causal ABF is not robust.
This prevents a known multi-signal disease locus from being falsely rejected by the single-causal assumption.

For FCRL3 and INAVA, source-LD/SuSiE is triggered only by:
- robust single-causal H4; or
- material H3/H4 ambiguity.

## Smoke priors

p1 = 1e-4
p2 = 1e-4
p12 = 1e-6 / 1e-5 / 1e-4

Smoke robust:
- PP.H4 >= 0.80
- H4/(H3+H4) >= 0.80
- low-p12 ratio >= 0.50

Smoke is never the final PASS for a triggered gene.

## Signal-level PASS

Both disease and eQTL are independently fine-mapped with their own study/source LD.
`coloc.susie` may use different LD matrices in the two studies.

A gene PASS requires at least one PF10_L10 signal pair with:
- PP.H4 >= 0.80;
- H4/(H3+H4) >= 0.80;
- p12=1e-6 H4/(H3+H4) >= 0.50;
- both SuSiE fits converged;
- QTL signal stable enough to form a 95% credible set.

PF10_L5, PF10_L20 and PF50_L10 are frozen sensitivity configurations.

## Project gate

Only if >=2/3 genes PASS signal-level:
1. trigger TenK10K same-gene compatible-cell independent replication;
2. require >=1 replicated gene;
3. then trigger PBC liver target detectability/donor-level orthogonal validation.

Only after all three layers pass can:

`NEW_PRIMARY_PROJECT = PBC`

If <2 genes PASS:
`PBC_REGULATORY_MAIN = FROZEN_FAIL`
`CeD_AUTO_RESUME = NO`
`NEXT = NEW_RESEARCH_ARCHITECTURE_REDESIGN`

## Implementation hardening after hostile code audit

Before source-LD/multi-signal work, Python and official R `coloc.abf` default-prior posteriors must agree with maximum absolute difference <= `1e-10` across all frozen smoke comparisons.

A final gene PASS is sensitivity-stable, not a single-configuration event. The same OneK cell must contain at least one robust signal pair in each frozen configuration:
- PF10_L5
- PF10_L10
- PF10_L20
- PF50_L10

In each configuration both disease and QTL SuSiE must converge and each side must have at least one 95% credible set. Signal labels need not have the same numerical component index across different `L`; stability is evaluated by the existence of a robust shared signal in the same cell, avoiding false failure caused only by SuSiE component relabelling.
