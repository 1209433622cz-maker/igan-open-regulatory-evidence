# Current PBC reproducibility contract — RP v4 / R7C3G

The current primary project is **PBC**, not IgAN. The superseded root contract is archived in `0_admin/history/root_before_R7C3G1/REPRODUCIBILITY.md`.

1. Verify provider byte identity, genome build, alleles/effect direction, cell-specific active donors and source/covariate/model identity before statistical analysis. Large inputs are recovered from `1_data/` manifests, not mirrored here.
2. Preserve the 6,923 screening universe, 5,460 eligible comparisons and separate coverage-insufficient states. The source-matched multi-signal cohort is the prespecified 642 high-information subset (184 primary + 455 H3 rescue + 3 borderline), not an all-comparison multi-signal census.
3. Keep A0/A1/A2/M variant-support and disease-statistic contrasts distinct. Source/model-matched PF10 is primary and PF50 is sensitivity; retain actual signal-pair credible sets and diagnostic/evaluability states. The frozen stage protocols, not a simplified global rule, define each stage's gates and priors.
4. Scientific R stages used the recorded `coloc` 5.2.3 / `susieR` 0.14.2 environments. Stage scripts retain explicit local workspace/input settings. This is a documented research compendium, not a one-command portable raw-data-to-paper workflow.
5. Simulation separates credible-set discovery, pair-evaluable inference and end-to-end recovery. Never label uninformative or failed credible-set discovery as a biological distinct signal. Real-data reclassification is not a known-truth error rate.
6. R7C3G figure/document regeneration uses `2_code/11_manuscript/R7C3G`: 01 → 02 → 03 → 04 → 07 → 04a → 05 WPS → 06 machine QA → actual visual review → 08 package. Inputs are the frozen local R7C3F package and prior-stage results. WPS export is Windows-specific; automatic machine QA does not replace visual proof review.

Verify the current Git snapshot with Python standard library only:

```powershell
python 2_code/00_repository/verify_repository.py
```

This verifies canonical Git blobs against `MANIFEST.sha256`, independent of Windows working-tree line endings. The manifest excludes only itself. Old stage manifests retain original relative-path scope; use the path migration table when their repository paths refer to the old layout, or inspect the original historical tag. No original GWAS/LD/SuSiE/simulation fits were rerun by the repository restructuring.
