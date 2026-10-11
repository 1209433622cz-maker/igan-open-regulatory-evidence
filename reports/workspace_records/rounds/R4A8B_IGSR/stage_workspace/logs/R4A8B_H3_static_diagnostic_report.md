# R4A8B-H3 static coverage diagnostic

**Purpose: diagnostic only; this script never runs SuSiE-RSS.**

- Full-set estimate_s reproduced: 0.191784920
- N_STUDIES range: 2–14
- Spearman |residual| vs N_STUDIES: rho=-0.1674, P=3.06e-11
- Mean |residual| for N_STUDIES<=5: 1.0367
- Mean |residual| for N_STUDIES>5: 0.6060
- Mann–Whitney one-sided P: 6.04e-17
- |residual|>3: 32 total; 26 have N_STUDIES<=5
- Enrichment OR (N_STUDIES<=5): 11.531, Fisher P=5.33e-10

## estimate_s by minimum N_STUDIES

|Criterion|Variants|estimate_s|
|---|---:|---:|
|N_STUDIES>=2|1555|0.191785|
|N_STUDIES>=3|1434|0.157120|
|N_STUDIES>=4|1305|0.129000|
|N_STUDIES>=5|1194|0.098983|
|N_STUDIES>=6|1113|0.092522|
|N_STUDIES>=7|966|0.090217|
|N_STUDIES>=8|857|0.070538|
|N_STUDIES>=9|792|0.062326|
|N_STUDIES>=10|724|0.059722|
|N_STUDIES>=11|639|0.056094|
|N_STUDIES>=12|544|0.055159|
|N_STUDIES>=13|387|0.041189|
|N_STUDIES>=14|134|0.002963|

## Interpretation

The steep decline in estimate_s as study coverage becomes more uniform supports a meta-analysis/sample-overlap covariance mismatch rather than a simple allele-orientation error. These subsets must not be used to force a credible-set PASS; they are root-cause diagnostics.
