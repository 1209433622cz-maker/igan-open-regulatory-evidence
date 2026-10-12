# Current PBC reproducibility contract — RP v4 / R7C3H

The current primary project is **PBC**, not IgAN. The superseded root contract is archived in `0_admin/history/root_before_R7C3G1/REPRODUCIBILITY.md`.

1. Verify provider byte identity, genome build, alleles/effect direction, cell-specific active donors and source/covariate/model identity before statistical analysis. Large inputs are recovered from `1_data/` manifests, not mirrored here.
2. Preserve the 6,923 screening universe, 5,460 eligible comparisons and separate coverage-insufficient states. The source-matched multi-signal cohort is the prespecified 642 high-information subset (184 primary + 455 H3 rescue + 3 borderline), not an all-comparison multi-signal census.
3. Keep A0/A1/A2/M variant-support and disease-statistic contrasts distinct. Source/model-matched PF10 is primary and PF50 is sensitivity; retain actual signal-pair credible sets and diagnostic/evaluability states. The frozen stage protocols, not a simplified global rule, define each stage's gates and priors.
4. Scientific R stages used the recorded `coloc` 5.2.3 / `susieR` 0.14.2 environments. GJOKA SuSiE-RSS used the source-matched total sample size `N=24,510`; case-control `Neff=21,584.38` is a bounded 33-comparison stress test, not a correction. Raw scientific stages retain explicit local input settings. This is a documented research compendium, not a one-command portable raw-data-to-paper workflow.
5. Simulation separates credible-set discovery, pair-evaluable inference and end-to-end recovery. Never label uninformative or failed credible-set discovery as a biological distinct signal. Real-data reclassification is not a known-truth error rate.
6. R7C3H preserves the R7C3G figures and adds Source Data 3 plus bounded manuscript text. Portable inspection and aggregate endpoint replay use `2_code/11_manuscript/R7C3G/01_inspect.py` and `02_evidence_audit.py`; they infer the repository root and write outside the checkout. WPS export remains Windows-specific; automatic machine QA does not replace visual proof review.

Run the current portable checks:

```powershell
$env:R7_RUNTIME_OUT = "$env:TEMP\pbc-r7-portable-qa"
python 2_code/11_manuscript/R7C3G/01_inspect.py
python 2_code/11_manuscript/R7C3G/02_evidence_audit.py
```

These replay compact public evidence only. They do not reconstruct raw donor data, rebuild LD matrices or refit the complete 642-comparison scientific workload.

Verify the current Git snapshot with Python standard library only:

```powershell
python 2_code/00_repository/verify_repository.py
```

This verifies canonical Git blobs against `MANIFEST.sha256`, independent of Windows working-tree line endings. The manifest excludes only itself. Old stage manifests retain original relative-path scope; use the path migration table when their repository paths refer to the old layout, or inspect the original historical tag. No original GWAS/LD/SuSiE/simulation fits were rerun by the repository restructuring.
