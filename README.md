# Open regulatory evidence: completion-first immune-disease signal gates

This repository contains the reproducible, open-data workflow used to test whether immune-disease GWAS signals share cell-specific cis-eQTL signals in OneK1K and TenK10K. It retains the completed IgAN work and the current primary biliary cholangitis (PBC) manuscript evidence chain.

The repository is evidence-first: frozen candidate universes, all tested comparisons, negative and ambiguous results, software cross-checks, and gate decisions are retained together. Raw third-party datasets and donor-level genotype/LD matrices are not mirrored here; exact URLs, sizes, hashes, and expected local locations are recorded in [`data/LARGE_DATA_MANIFEST.tsv`](data/LARGE_DATA_MANIFEST.tsv).

## Current evidence state

- `ZMIZ1 × NK` is the positive benchmark: OneK1K combined-IgAN PP.H4 ≈ 0.931 and TenK10K NK precomputed PP.H4 ≈ 0.998.
- The frozen R6A2B0 expansion tested 183 cell–gene combinations across 8 additional loci and 3 ancestry datasets (549 comparisons).
- No additional combined-IgAN locus passed the robust shared-signal gate.
- Three combined smoke ambiguities received source-matched LD and 12 SuSiE-RSS sensitivity fits; all fits converged, but no stable 95% credible set was formed.
- `Asian-only IgAN × REEP3 × CD4_NC` passed the targeted OneK1K signal gate (PF10/L10 PP.H4 ≈ 0.900; one 15-variant credible set stable across four LD/L settings).
- REEP3 failed the frozen TenK10K replication gate: the OneK primary credible set had zero exact overlap with the TenK source credible sets after unique GRCh37→GRCh38 mapping, while author-precomputed IgAN coloc was H3-dominant in CD4 Naive and CD4 TCM (PP.H4 ≈ 0.031 and 0.026).

The frozen IgAN decision is `IMMUNE_CISEQTL_FULL24 = FROZEN_NO_GO`. REEP3 remains a discovery-only result and is not counted as a replicated locus.

R6A3A1 has now completed the public pQTL and kidney gate on real bytes. Of 11 pre-frozen plasma-protein targets, only TNFSF8 and TNFSF12 were source-supported. Their three valid source SuSiE components all failed the shared-signal gate (maximum PP.H4 among valid components ≈ 0.018). GSE127136 donor-level kidney pseudobulk showed a nonsignificant case-lower ZMIZ1 shift (13 IgAN vs 6 paracancer controls; difference = -0.256 log2CPM; exact permutation P = 0.483).

The final state is `IGAN_REGULATORY_MAIN = FROZEN_ARCHIVE`. The next protocol is R7A0, an open-data completion-first portfolio preflight across celiac disease, primary biliary cholangitis and alopecia areata.

R7A1A has now completed the true-byte portfolio gate. PBC `GCST90061440` passed its 5,054,572-row schema audit and exposes 56 matched locus summary-statistics/LD pairs in the GJOKA archive. All three frozen PBC controls are cross-resource testable; IL12RB2 and FCRL3 are source-positive in both OneK1K and TenK10K, while INAVA/C1orf106 is weak in OneK1K. CeD was held because only UBASH3A was source-positive in both resources, its 2020 Immunochip file lacks SE, and the larger `GCST90014442` source is UK Biobank-derived and therefore excluded by the frozen data rule.

R7A1B has now executed that bounded PBC gate on real bytes. Nine frozen OneK cell–gene tests produced seven trigger combinations. Source-matched disease and QTL LD, four PF/L sensitivity configurations and 28 converged SuSiE fits support signal-specific shared genes at `FCRL3` and `IL12RB2`; `INAVA` remains uninformative because its OneK QTL is weak. `FCRL3 × CD8_ET` illustrates the required multi-signal correction: single-signal PP.H4 ≈ 0.941 fell to ≈ 0.004 after source-LD decomposition.

R7A1C1A has now closed the compatible-cell TenK10K replication gate for both eligible genes. IL12RB2 × NK retains robust H4 on 396 full PBC/TenK allele-matched variants (default PP.H4 ≈ 0.998). FCRL3 × B intermediate now has 343 exact variants, default PP.H4 ≈ 0.992 and low-prior H4/(H3+H4) ≈ 0.922; the four leading shared-weight variants are exactly TenK source CS1.

R7A1C1B0R then completed a hostile pre-execution audit of the five-donor tissue gate. The received v3 runner had a malformed final-adjudicator assignment, accepted an orphan compact summary without a matching byte-verification receipt, and could falsely reject coordinate-sorted BAMs after a fixed 500,000-record prefix. The corrected v3.1 runner uses `xf` bit 8 molecule representatives, reconstructed called cells, an adaptive 0.5–5 million-record schema check and exact summary/receipt identity. Its manifest, parser and runtime preflight pass. Testing the public supplementary workbooks found pooled human FCRL3 B-cell marker evidence but no donor-by-lineage-by-target matrix; their only IL12RB2 hit is from a mouse sheet, so they cannot replace the human BAM gate.

R7A1C1B1R recorded the first real execution checkpoint and fixed a coordinate-sorted-prefix false failure without changing the full-scan biological thresholds.

R7A1C1B2 has now completed the exact five-donor PBC liver adjudication. All five donors pass technical QC; FCRL3 in the frozen B-cell gate and IL12RB2 in the frozen NK-cell gate are promotion-eligible in 5/5 donors. The five scans cover 2,024,279,500 alignment records, 284,941,671 molecule-representative records and 23,809 called cells. The official adjudication and a separately generated adjudication are byte-for-byte equivalent at the parsed JSON level; eight independent closeout checks pass. Each BAM was deleted only after its compact summary and byte-verification receipt were validated.

PBC is therefore promoted to the primary manuscript-scale project. The current claim is deliberately bounded to replicated disease–eQTL sharing plus target detectability in prespecified PBC liver immune lineages; it does not claim PBC-versus-control differential expression or tissue mediation.

R7A2A0 has frozen the next executable gate. Official HRA008003 metadata identify HRR1849454–58 as five hepatic-hemangioma non-lesion liver controls (134,657,112,757 bytes total). Their byte/MD5 manifest, resumable runner, exact 5-vs-5 donor-level comparison and synthetic regression tests are included. The next stage is `R7A2A1_HRA008003_EXACT_5_VS_5_CONTROL_TARGET_PANEL`.

R7A2A1 has now completed that exact 5-vs-5 gate. All five control BAM identities, schemas, compact summaries and deletion receipts pass; an independent closeout audit passes 19/19 checks and reproduces the frozen JSON and TSV exactly. Both target-lineage pairs were detected in 5/5 PBC and 5/5 control donors. FCRL3-B was directionally lower in PBC (mean log1p CPM difference -0.786; exact P=0.111), while IL12RB2-NK was directionally higher (+0.330; exact P=0.0635); both have BH q=0.111. The tissue layer therefore supports bounded lineage localization but not PBC-specific upregulation.

PBC remains the primary project because the core disease-eQTL signal-sharing evidence and 2/2 TenK10K replication remain intact. The next stage is `R7A2A2_MANUSCRIPT_EVIDENCE_FREEZE_AND_FIGURE_ASSEMBLY`. Full ten-donor reclustering is deferred because it would not increase the donor count and is not required for the bounded core claim.

R7A2A2 subsequently froze the claim–evidence matrix, novelty boundary, manuscript skeleton, Figure 1–6 source manifest and supplementary-item plan. R7A2A3 has now converted that evidence into a complete English scientific draft using the QiTeng v0.3.24.2 guarded manuscript workflow. The draft contains all Methods and Results modules, retains FCRL3/CD8_ET and INAVA boundary-changing negatives, and keeps the 5-vs-5 tissue result in the main evidence hierarchy. Deterministic manuscript QA passes 22/22 checks, including numerical tokens reconstructed from upstream tables, reference continuity and first-appearance order, required boundary sentences, and an 11/11 Methods–Results mirror.

R7A2A4 subsequently completed the hostile manuscript audit, including claim/source repair, 34/34 numeric checks, 17/17 reader-facing checks and repaired Figure 1–4/6 semantics. R7A2A5 has now selected **Human Genomics / Research** as the primary submission route and assembled the journal-format manuscript, graphical abstract, six main figures, four supplementary figures and a ten-table supplementary workbook. Final machine QA passes 55 checks with no technical failures. The submission state is `AWAITING_AUTHOR_METADATA`: author order, affiliations, correspondence, CRediT, funding, competing interests, local ethics/waiver wording and all-author approval must be supplied by the authors before submission. No new biological analysis is required by default.

The R7A submission route is now archived while the project follows the R7B0 v2 major redesign. R7B0A recovered a fully auditable current-release OneK model even though the historical PF10 input bytes remain unresolved: 14/14 PF10/PF50 model-identity rows and 28/28 SuSiE fits passed. R7B1A then froze a result-blind PBC-wide universe of 6,923 locus–gene–cell comparisons and regenerated current PF10 QTL statistics from public pseudobulk, donor genotype and covariates. Of 5,460 comparisons with at least 200 variants, the single-causal screen produced 112 default robust-H4 triggers and 72 prespecified H3/H4 ambiguities; 455 favored distinct signals, 4,821 did not trigger, and 1,463 lacked sufficient variant overlap. Independent QA passes 12/12 checks.

The original 184 screen triggers remain a nested primary verification cohort. R7B1B v2 expands the pre-result-frozen multi-signal workload to 642 high-information comparisons so H4-to-H3 and H3-to-H4 reclassification can be measured symmetrically.

![REEP3 discovery and replication result](figures/R6A2C1D_REEP3_falsification_summary.png)

![PBC three-control signal gate](figures/R7A1B_PBC_signal_gate_summary.png)

![PBC exact five-versus-five liver target panel](figures/R7A2A1_PBC_vs_control_target_panel.png)


## R7B1B v2 high-information multi-signal reclassification

R7B1B v2 preserves the original 184 screen-positive/ambiguous comparisons as the primary verification cohort and adds a pre-result-frozen symmetric layer of 455 H3 comparisons plus three borderline high-information calibration cases. All 642 comparisons were run with GJOKA study-matched disease LD and current-release OneK1K PF10/PF50 cell-specific LD; 2,568 SuSiE fits completed with no QC failures.

The PF10 adjudication retained 78 stable H4 and 409 stable H3 comparisons. Eight ABF H3 comparisons were reclassified to stable H4, while four ABF H4 comparisons were reclassified to stable H3. FCRL3 × CD8_ET reproduces the key H4-to-H3 counterexample; IL12RB2 × NK and the FCRL3 B-cell comparisons remain stable shared-signal exemplars. Independent mechanical QA passes 19/19 checks.

The evidence ceiling is **PBC-wide ABF screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset**. It is not a multi-signal analysis of every one of the 6,923 screened comparisons. The next frozen stage is simulation/calibration under known truth; manuscript rewriting remains on hold.

![R7B1B v2 bidirectional reclassification](figures/R7B1B_v2/Figure_R7B1B_1_bidirectional_reclassification.png)

## Repository layout

```text
analysis/r6a2b0/   frozen Python, R and PowerShell workflow
analysis/r6a2c/    REEP3 OneK source-LD and signal-specific falsification
analysis/r6a2d/    targeted TenK summary/coloc intake and cross-build adjudication
analysis/r6a3a/    public Sun 2018 pQTL and GSE127136 kidney gate
analysis/r7a1a/    PBC/CeD byte intake, source audit and frozen-control screen
analysis/r7a1b/    bounded PBC ABF, source-LD, SuSiE and signal adjudication
analysis/r7a1c1/   TenK full-window replication and hardened HRA donor gate
analysis/r7a2/     frozen five-control HRA runner and exact donor comparison
analysis/r7a2a3/   deterministic manuscript structure, reference and numeric QA
analysis/r7a2a5/   Human Genomics asset builders, WPS export and final QA
analysis/r7b1/     PBC-wide eligibility, harmonization and PF10 ABF screen
analysis/r7b1b_v2/ R7B1B v2 source-LD, SuSiE, adjudication, QA and release
data/              large-file manifest and data availability rules
environment/       Python and R package requirements
figures/           decision figures
figures/r7a2a3_draft/ R7A2A2-frozen Figure 1–4/6 review assets with known repair notes
figures/r7a2a5_submission/ Human Genomics main, supplementary and graphical-abstract assets
manuscript/r7a2a5/ Human Genomics-formatted manuscript v3 in MD, DOCX and WPS PDF
protocols/         frozen analysis and next-stage protocols
reports/           detailed Chinese-language audit records
results/r6a2a1/    positive benchmark tables
results/r6a2b0/    549-test and targeted multi-signal outputs
results/r6a2c/     REEP3 OneK signal-level outputs and gates
results/r6a2d/     TenK replication, liftover overlap and final adjudication
results/r6a3a1/    pQTL source-component, kidney and final freeze outputs
results/r7a1a/     PBC/CeD schema, GJOKA inventory, QTL controls and gate state
results/r7a1b/     PBC smoke, source-LD QC, credible sets and final adjudication
results/r7a1c/     TenK replication, source-CS tables and outcome-blind QA
results/r7a1c1b0r/ five-donor runner QA, BAM-prefix schema test and supplement audit
results/r7a1c1b1r/ real three-donor checkpoint, donor-4 schema hotfix and v3.2 QA
results/r7a1c1b2/  completed five-PBC-donor summaries, receipts and final adjudication
results/r7a2a0/    control-source audit, manifest preflight and execution-pack tests
results/r7a2a1/    exact 5-vs-5 donor metrics, independent QA and final adjudication
results/r7a2a3/    claim/reference/risk ledgers, Methods–Results mirror and manuscript QA
results/r7a2a5/    journal matrix, supplementary workbook, state and 55-check final QA
results/r7b1a/     6,923-test ABF registry, exact 184-trigger set and independent QA
results/r7b1b_v2/  642-comparison bidirectional reclassification and 19-check QA
```

## Reproduction

1. Install Python 3.11+ and R 4.4+; install the packages listed under `environment/`.
2. Download the files listed in `data/LARGE_DATA_MANIFEST.tsv` and place them at the specified relative paths.
3. Set `IGAN_PROJECT_ROOT` to the project root.
4. Run the bounded workflow from the project root:

```powershell
$env:IGAN_PROJECT_ROOT = (Get-Location).Path
pwsh -File .\analysis\r6a2b0\RUN_R6A2B0_8LOCUS_BOUNDED_EXPANSION.ps1
```

The runner intentionally stops after smoke-test adjudication. Build LD only for combinations listed in `results/r6a2b0/R6A2B0_sourceLD_triggers.tsv`, then run scripts 08–10. This preserves the trigger-only rule.

The REEP3 follow-up can be reproduced after the large inputs are present:

```powershell
$env:IGAN_PROJECT_ROOT = (Get-Location).Path
pwsh -File .\analysis\r6a2c\RUN_R6A2C_REEP3_FALSIFICATION.ps1
python .\analysis\r6a2d\01_extract_tenk_reep3_summary.py
python .\analysis\r6a2d\02_extract_tenk_igan_cd4_coloc_members.py
python .\analysis\r6a2d\03_compare_onek_tenk_reep3_signals.py
```

The final pQTL/kidney gate can be reproduced after the R6A3A inputs in the large-data manifest are present:

```powershell
$env:IGAN_PROJECT_ROOT = (Get-Location).Path
pwsh -File .\analysis\r6a3a\RUN_R6A3A_COMPLETION_DESIGN_GATE.ps1
```

The R7A1A portfolio intake is self-contained apart from the OneK1K/TenK10K files listed in the manifest. It intentionally stops before disease–QTL colocalization:

```powershell
$env:R7_PROJECT_ROOT = (Get-Location).Path
pwsh -File .\analysis\r7a1a\RUN_R7A1A_TRUE_BYTE_QTL_PREFLIGHT.ps1
```

The R7A1B runner reads the full OneK1K archive, but downloads only the triggered GJOKA locus members and builds LD only for triggered cell–gene combinations:

```powershell
$env:R7_PROJECT_ROOT = (Get-Location).Path
pwsh -File .\analysis\r7a1b\RUN_R7A1B_PBC_3CONTROL_SIGNAL_GATE.ps1
```

The corrected R7A1C1 HRA runner processes one official PBC liver BAM at a time and deletes it only after validated compact output plus an exact byte-verification receipt. It is resumable:

```powershell
$env:R7_PROJECT_ROOT = (Get-Location).Path
pwsh -File .\analysis\r7a1c1\RUN_R7A1C1_HRA008003_TARGET_PANEL_v3_2.ps1
```

The R7A2A1 runner applies the same frozen target-panel algorithm to the exact five HRA008003 non-lesion liver controls, then performs the prespecified 5-vs-5 donor comparison. It is also resumable and deletes each control BAM only after validated compact output:

```powershell
$env:R7_PROJECT_ROOT = (Get-Location).Path
pwsh -File .\analysis\r7a2\RUN_R7A2A1_HRA008003_CONTROL_TARGET_PANEL_HARDENED.ps1
```

The R7B1A runner rebuilds the result-blind PBC-wide universe, GWAS harmonization, current-release PF10 QTL statistics, all 6,923 ABF records and the independently checked exact trigger set:

```powershell
$env:R7_PROJECT_ROOT = (Get-Location).Path
pwsh -File .\analysis\r7b1\RUN_R7B1A_PBCWIDE_ABF.ps1
```

The subsequent intake runner range-fetches only the 50 GJOKA members required by the frozen 25-locus R7B1B workload:

```powershell
$env:R7_PROJECT_ROOT = (Get-Location).Path
pwsh -File .\analysis\r7b1\DOWNLOAD_R7B1B_GJOKA_TRIGGER_MEMBERS.ps1
```

## Evidence and licensing

Code is released under the MIT License. Reports and small derived summary tables are provided for transparency. Third-party data remain subject to their source licenses and citation requirements; see [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md).
