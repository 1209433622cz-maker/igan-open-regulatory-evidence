# R4A9 independent RSS diagnostic reproduction

## Final status

**PASS_REPRODUCED_HOLD** — the calculation reproduced correctly, and the full public-summary branch remains outside the frozen RSS gate.

## Reproduced values

- Variants: 1555
- `estimate_s`: 0.191784922366631
- Maximum absolute standardized kriging residual: 5.361425644
- Frozen versus reproduced kriging maximum absolute difference: 4.88498e-15
- Gate: `estimate_s <= 0.1` and `max residual <= 5`
- Full-set result: **FAIL**
- SuSiE-RSS: **NOT_RUN**
- `C1_count`: **null (not tested)**

## Coverage diagnostic

- Exact `N_STUDIES=14`: 134 variants; `estimate_s=0.00296319947225`; maximum residual `4.0246407`
- Absolute residual versus `N_STUDIES`: Spearman rho `-0.16742137`, p `3.06021e-11`
- Mean absolute residual: `N_STUDIES<=5` 1.0367378 versus `>5` 0.60595055
- One-sided Wilcoxon p: `6.03831e-17`
- Residual `>3`: 32 total, 26 with `N_STUDIES<=5`

## Boundary

The pattern supports variant-dependent cohort or sample composition as a major source of covariance mismatch. `N_STUDIES` is only a proxy, so this audit does not identify a unique causal mechanism. Filtering to high-coverage variants would change the estimand and is not used to manufacture a primary fine-mapping result.

