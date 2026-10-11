# R4A8B-H3 coverage-stratified kriging diagnostic

**Diagnostic only. No SuSiE-RSS fit is run.**

- susieR: 0.14.2
- The N_STUDIES>=2 row must reproduce the frozen H2 HOLD.
- Higher-coverage subsets are used only to diagnose the source of mismatch.

```
 min_N_STUDIES variants  estimate_s max_abs_standardized_residual
             2     1555 0.191784922                      5.361426
             5     1194 0.098983054                      6.366693
             8      857 0.070538290                      5.206352
            10      724 0.059722434                      5.386580
            12      544 0.055159173                      5.722752
            13      387 0.041188761                      4.490128
            14      134 0.002963199                      4.024641
 kriging_logLR_gt2_absz_gt2 original_rule_pass
                          0              FALSE
                          0              FALSE
                          0              FALSE
                          0              FALSE
                          0              FALSE
                          0               TRUE
                          0               TRUE
```

A lower estimate_s / residual burden in high-coverage subsets supports
variant-dependent meta-analysis/sample-overlap covariance as a major source
of the full-set RSS mismatch. It does not authorize variant deletion for
paper-grade fine-mapping.
