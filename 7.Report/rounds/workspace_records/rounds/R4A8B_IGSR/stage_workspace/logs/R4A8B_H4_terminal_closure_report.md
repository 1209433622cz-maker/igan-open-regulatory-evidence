# R4A8B-H4 terminal meta-covariance closure

**Status:** `HOLD_META_COVARIANCE_MISMATCH__PUBLIC_SUMMARY_STATS_NOT_SUITABLE_FOR_PAPER_GRADE_EXTERNAL_LD_SUSIE`

## Exact N_STUDIES strata

|Exact N_STUDIES|Variants|estimate_s|Mean |full-H2 kriging residual||Max |residual||
|---:|---:|---:|---:|---:|
|2|121|0.376285|1.1832|5.3614|
|3|129|0.154807|1.0944|4.2976|
|4|111|0.107755|0.9552|4.4958|
|5|81|0.115493|0.8379|3.4375|
|6|147|0.016544|0.4827|2.5234|
|7|109|0.043943|0.7895|4.0578|
|8|65|0.063333|0.7136|2.3327|
|9|68|0.035100|0.6393|2.5289|
|10|85|0.072788|0.6272|3.1068|
|11|95|0.019861|0.6466|3.2448|
|12|157|0.032828|0.5297|3.1816|
|13|253|0.019098|0.6419|3.1690|
|14|134|0.002963|0.5017|1.4534|

## Interpretation

The exact-stratum analysis strengthens the H3 conclusion while also showing that study count alone is not the complete explanation: exact-stratum estimate_s values are not strictly monotonic across 2–14. This is expected when different SNPs with the same N_STUDIES can still be contributed by different cohort combinations.

The N_STUDIES=14 stratum is special because, in a 14-cohort meta-analysis, it necessarily represents variants observed in all cohorts. Its very small estimate_s therefore provides a strong internal positive control for the meta-covariance interpretation.

No SuSiE-RSS model was run in H4.

## Next target

Prefer cohort-level / cohort-consistent data. Preserve H1–H4 unchanged. Any future mismatch-aware development-version method must be a separate sensitivity branch with an exact pinned commit.
