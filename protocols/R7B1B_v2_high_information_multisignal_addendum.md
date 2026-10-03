# R7B1B v2 — High-information source-matched multi-signal protocol addendum

**Frozen:** 2026-10-03, after R7B1A ABF completion and before any new R7B1B multi-signal result is inspected.
**Governance:** QiTeng v0.3.24.2 evidence ceiling; no post-multi-signal selection.

## 1. Why v2 is required

R7B1B v1 freezes 184 single-causal ABF triggers (112 robust-H4 + 72 H3/H4 ambiguity) for multi-signal verification. That is valid for estimating the stability/weakening/reversal of **screen-positive or ambiguous** comparisons.

It is not, by itself, a symmetric benchmark of the PBC-wide H3/H4 decision space because 455 high-information comparisons classified as `H3_DISTINCT_SIGNAL` would never be allowed to show H3→H4 rescue under multi-signal modelling. Three additional comparisons have `PP(H3)+PP(H4) >= 0.80` but narrowly miss the v1 H4 trigger because absolute PP.H4 is <0.80 despite H4/(H3+H4)>0.80.

Therefore v2 does **not delete or redefine the original 184**. It nests them as the primary verification cohort and freezes a broader high-information calibration/falsification universe before R7B1B results are available.

## 2. Immutable v2 universe

Eligibility remains the R7B1A result-blind 6,923 comparison universe and the >=200-variant ABF-eligible subset of 5,460.

High-information v2 inclusion is purely mechanical:

```text
ABF eligible
AND PP(H3)+PP(H4) >= 0.80 at p12=1e-5
```

This yields exactly:

```text
642 comparisons
47 GJOKA loci
200 genes
14 cells
286 unique cell–locus blocks
94 GJOKA members
```

Cohort roles:

```text
184  PRIMARY_184_TRIGGER_VERIFICATION
455  H3_RESCUE_FALSIFICATION
  3  BORDERLINE_HIGH_INFORMATION_CALIBRATION
```

The original 184-trigger SHA-256 remains `bac35fe7572a336ceedcf60a19a3d4f7f8c3cd97337ebd34a2d08e5360cb1f0e` and is preserved as a separately reported primary cohort.

## 3. Analyses

For all 642 comparisons, apply the exact same disease-side GJOKA study-derived summary/LD logic and current-release OneK model-matched QTL logic.

Primary QTL model:
- current-release PF10 de novo summary;
- PF10 residualized LD from identical active donors and exact 18-column covariate model.

Sensitivity:
- current-release PF50 de novo summary;
- PF50 residualized LD from identical active donors and exact 58-column model.

Frozen SuSiE/coloc settings are inherited from R7B0A/R7B1B v1. No parameter may be chosen using observed R7B1B posteriors.

## 4. Two different estimands must remain separate

### Estimand A — original trigger verification

Among the immutable 184 v1 triggers:
- stable H4 fraction;
- weakened H4 fraction;
- H4→H3 reversal fraction;
- uninformative/QC-fail fraction.

This estimates the **positive-trigger stability / falsification burden**.

### Estimand B — high-information symmetric reclassification

Among all 642 high-information comparisons:
- H4→H3;
- H3→H4;
- stable H4;
- stable H3;
- ambiguity resolution;
- model-sensitive / uninformative / QC failure.

This is the appropriate real-data calibration of directionality of reclassification.

Neither estimand is equivalent to a full 6,923-comparison multi-signal landscape because low-information and insufficient-overlap comparisons are not all fitted with SuSiE.

## 5. Mandatory wording ceiling

Allowed after v2 completion:

> "Across the prespecified high-information ABF subset, source-matched multi-signal modelling quantified bidirectional H3/H4 reclassification, while the original 184 screen-positive/ambiguous comparisons were retained as an immutable primary verification cohort."

Not allowed:

> "We performed multi-signal fine-mapping for all PBC locus–gene–cell combinations."

Not allowed:

> "The 642 comparisons are 642 PBC regulatory discoveries."

## 6. Gate

`R7B1B_V2_COMPLETE` requires:

1. 94/94 GJOKA members verified for the 47 loci;
2. 286/286 PF10 and PF50 cell–locus model identities verified;
3. 642/642 comparisons attempted;
4. the original 184 cohort separately identifiable and unchanged;
5. 455/455 H3-distinct comparisons allowed to test rescue rather than being presumed negative;
6. all three borderline high-information comparisons retained;
7. QC failure separated from biological negative;
8. independent QA reproducing the cohort hashes and class counts.

Only after this gate should the simulation/calibration stage begin.
