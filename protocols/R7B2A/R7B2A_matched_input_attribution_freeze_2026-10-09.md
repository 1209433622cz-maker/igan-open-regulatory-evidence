# R7B2A Matched-input attribution freeze

Date: 2026-10-09

Status: `FROZEN_BEFORE_A1_A2_RESULTS`

Authority: RP v3 and the 2026-10-09 R7B2A targeted-completion protocol. This is a post-result methodological audit. It is not an external preregistration and does not alter the historical R7B1E PASS state.

## 1. Objective

Separate three contributors to the historical ABF-to-multi-signal transition:

1. the variant-support change from the original ABF set `S_A` to the actual multi-signal set `S_M`;
2. the disease-statistic change from GCST90061440 harmonized beta/SE to the GJOKA regional disease statistics used with study-matched LD;
3. the remaining full-method difference between single-causal ABF and the frozen source-matched multi-signal analysis.

The objective is attribution, not preservation of 12 historical direction changes, 92 H4 comparisons, or any named gene.

## 2. Frozen universe

- Exact 642 comparison IDs from `R7B1B_v2_exact_642_high_information_comparisons.tsv`.
- Nested roles remain 184 primary verification, 455 H3 rescue/falsification and 3 borderline calibration.
- Disease, locus, gene, cell and model identities cannot be added, removed or reselected using A1/A2 results.
- Current PF10 is the primary QTL model. PF50 remains the historical sensitivity model and is not rerun in A1/A2.
- Historical A0, M, credible sets, posteriors and labels remain immutable.

## 3. Four arms

### A0 historical ABF

- Disease: GCST90061440 harmonized `beta_A1` and `standard_error`.
- Support: original ABF set `S_A` represented by each PF10 QTL file.
- QTL: current-release PF10 slope/SE.
- Role: immutable historical reference plus deterministic formula replay.

### A1 support-matched ABF

- Disease: same GCST beta/SE as A0.
- Support: exact `S_M` reconstructed with the same block, rsID, position and finite-GJOKA rules as the historical multi-signal runner.
- QTL: same PF10 rows as A0 restricted to `S_M`.
- Only intended change from A0: `S_A -> S_M`.

### A2 disease-statistic-matched ABF

- Disease: GJOKA `STAT` on `S_M`; primary beta is explicitly derived as `STAT × SE` so the z score exactly matches the historical multi-signal disease input.
- Secondary rounding sensitivity: source GJOKA `BETA/SE` on the same `S_M`.
- QTL: identical to A1.
- Only intended primary change from A1: disease statistic source/rounding definition.

### M frozen multi-signal

- Existing PF10 multi-signal state and signal-pair posterior.
- Same reconstructed `S_M` identity must match the recorded `common_variants_min`.
- No refit by default.

## 4. Scale and priors

- Disease prior SD: 0.2.
- QTL prior SD: `0.15 × sdY`.
- Primary A0/A1/A2 comparison fixes `sdY` to the historical A0 estimate so support-set changes do not silently change phenotype scale.
- A1/A2 native-`sdY` sensitivity is computed separately from the actual `S_M` QTL rows.
- `p1=p2=1e-4`; `p12` is evaluated at `1e-6`, `1e-5` and `1e-4`.
- The default classification uses the historical `p12=1e-5` ABF rules. Low-prior fields are reported but do not silently redefine the historical classifier.

## 5. ABF states

At default `p12=1e-5`:

- `ABF_H4_DOMINANT`: `PP.H4 >= 0.80` and `H4/(H3+H4) >= 0.80`.
- `ABF_AMBIGUOUS`: not H4 dominant, `H3+H4 >= 0.80` and ratio in `[0.20,0.80]`.
- `ABF_H3_DOMINANT`: `H3+H4 >= 0.80` and ratio `<0.20`.
- `ABF_H4_BORDERLINE`: `H3+H4 >= 0.80`, ratio `>0.80`, but `PP.H4 <0.80`.
- `ABF_UNINFORMATIVE_OR_NO_TRIGGER`: all remaining valid fits.
- Technical error and missing input are reported separately and are never recoded as uninformative.

## 6. Required identity checks

For every comparison:

- exact comparison ID, locus, gene, cell and 184/455/3 role;
- `S_A` and `S_M` ordered member lists, sizes and SHA-256;
- disease/QTL allele, position and rsID mapping;
- QTL N, active-donor and covariate identity inherited from frozen receipts;
- A0 `sdY`, fixed-scale and native-scale status;
- GJOKA source file identity, `STAT`, source BETA/SE, NMISS and rounding delta;
- source-LD block identity and historical M common-variant count;
- software, formula, priors and classification rule.

V3-G0 fails closed on key drift, duplicate variants, missing QTL/GJOKA inputs, `S_M<200`, `S_M` count mismatch, or unaccounted allele/position mismatch.

## 7. Outputs and attribution

- 642-row arm-identity manifest.
- Ordered `S_A` and `S_M` membership table.
- 642-row A0 replay, A1, A2 matched-z, A2 rounded and native-`sdY` sensitivity results.
- A0 observed-versus-replayed numeric audit.
- Complete A0→A1→A2→M trajectories and adjacent-arm transition matrices.
- Separate report for the historical 12 direction changes; the main report remains all 642.
- Posterior-delta summaries and locus/gene/cell denominators.

Adjacent transitions are descriptive and not assumed additive. A2→M compares full inference procedures under matched disease/QTL variant support; it does not isolate causal-variant count alone because ABF and SuSiE differ in effect modelling and posterior construction.

## 8. Simulation audit

Existing R7B1C iteration-level outputs are audited before any rerun. Technical errors, successful fits with no credible set, and successful fits with no signal pair are separate states. A rerun is permitted only when existing outputs cannot recover these states and must retain the original seed, grid, effect parameters and thresholds. No favorable scenario may be added.

## 9. Gates

- `V3-G0 INPUT_LOCK`: exact identities and sets complete.
- `V3-G1 CONTRAST_VALID`: A1/A2 change only declared factors; scale sensitivities separate.
- `V3-G2 COVERAGE`: all 642 have results or explicit failure reasons.
- `V3-G3 SIMULATION_INTERPRETABLE`: error/no-CS/no-pair states are separated or the claim is restricted.
- `V3-G4 ATTRIBUTION`: trajectories are interpretable with mixed-pair and external/tissue boundaries preserved.
- `V3-G5 MANUSCRIPT_LOCK`: claim ledger, Methods–Results mirror and Figure 1–6 source plan updated.

Passing does not require a positive count. If support/statistic changes explain most historical transitions, the manuscript centers input harmonization. If A2→M differences persist, the method-comparison contribution remains. Only a reproducible, unrepairable defect that prevents the central reliability question from being answered triggers project reselection.
