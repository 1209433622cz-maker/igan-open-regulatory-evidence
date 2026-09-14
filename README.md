# IgAN open regulatory evidence

This repository contains the reproducible, open-data workflow used to test whether IgA nephropathy (IgAN) GWAS signals share cell-specific cis-eQTL signals in OneK1K and TenK10K.

The repository is evidence-first: frozen candidate universes, all tested comparisons, negative and ambiguous results, software cross-checks, and gate decisions are retained together. Raw third-party datasets and donor-level genotype/LD matrices are not mirrored here; exact URLs, sizes, hashes, and expected local locations are recorded in [`data/LARGE_DATA_MANIFEST.tsv`](data/LARGE_DATA_MANIFEST.tsv).

## Current evidence state

- `ZMIZ1 × NK` is the positive benchmark: OneK1K combined-IgAN PP.H4 ≈ 0.931 and TenK10K NK precomputed PP.H4 ≈ 0.998.
- The frozen R6A2B0 expansion tested 183 cell–gene combinations across 8 additional loci and 3 ancestry datasets (549 comparisons).
- No additional combined-IgAN locus passed the robust shared-signal gate.
- Three combined smoke ambiguities received source-matched LD and 12 SuSiE-RSS sensitivity fits; all fits converged, but no stable 95% credible set was formed.
- `Asian-only IgAN × REEP3 × CD4_NC` passed the targeted OneK1K signal gate (PF10/L10 PP.H4 ≈ 0.900; one 15-variant credible set stable across four LD/L settings).
- REEP3 failed the frozen TenK10K replication gate: the OneK primary credible set had zero exact overlap with the TenK source credible sets after unique GRCh37→GRCh38 mapping, while author-precomputed IgAN coloc was H3-dominant in CD4 Naive and CD4 TCM (PP.H4 ≈ 0.031 and 0.026).

The frozen decision is `IMMUNE_CISEQTL_FULL24 = FROZEN_NO_GO`. REEP3 remains a discovery-only result and is not counted as a replicated locus.

R6A3A1 has now completed the public pQTL and kidney gate on real bytes. Of 11 pre-frozen plasma-protein targets, only TNFSF8 and TNFSF12 were source-supported. Their three valid source SuSiE components all failed the shared-signal gate (maximum PP.H4 among valid components ≈ 0.018). GSE127136 donor-level kidney pseudobulk showed a nonsignificant case-lower ZMIZ1 shift (13 IgAN vs 6 paracancer controls; difference = -0.256 log2CPM; exact permutation P = 0.483).

The final state is `IGAN_REGULATORY_MAIN = FROZEN_ARCHIVE`. The next protocol is R7A0, an open-data completion-first portfolio preflight across celiac disease, primary biliary cholangitis and alopecia areata.

![REEP3 discovery and replication result](figures/R6A2C1D_REEP3_falsification_summary.png)

## Repository layout

```text
analysis/r6a2b0/   frozen Python, R and PowerShell workflow
analysis/r6a2c/    REEP3 OneK source-LD and signal-specific falsification
analysis/r6a2d/    targeted TenK summary/coloc intake and cross-build adjudication
analysis/r6a3a/    public Sun 2018 pQTL and GSE127136 kidney gate
data/              large-file manifest and data availability rules
environment/       Python and R package requirements
figures/           decision figures
protocols/         frozen analysis and next-stage protocols
reports/           detailed Chinese-language audit records
results/r6a2a1/    positive benchmark tables
results/r6a2b0/    549-test and targeted multi-signal outputs
results/r6a2c/     REEP3 OneK signal-level outputs and gates
results/r6a2d/     TenK replication, liftover overlap and final adjudication
results/r6a3a1/    pQTL source-component, kidney and final freeze outputs
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

## Evidence and licensing

Code is released under the MIT License. Reports and small derived summary tables are provided for transparency. Third-party data remain subject to their source licenses and citation requirements; see [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md).
