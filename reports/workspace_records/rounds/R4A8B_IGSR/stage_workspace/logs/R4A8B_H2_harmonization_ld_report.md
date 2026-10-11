# R4A8B-H2 harmonization and signed-LD gate

## Status

**R4A8B_H2_HARMONIZATION_SIGNED_LD_PASS**

## Reference branch

- 1000 Genomes Phase 3 v5a, GRCh37
- EUR n = 503
- IL12RB2 region: chr1:67,306,207-68,306,207
- Regional biallelic SNP reference: 27067
- Reference equivalence: independent regional Phase3-v5a validation; **not** claimed to be Zenodo exact-MD5 reproduction

## GWAS reproduction

- Immutable GCST009131 regional rows reproduced: 1842
- Signed-Z reproduction: PASS

## Harmonization

- Retained for LD: 1555
- Exclusions: `{"NO_UNIQUE_RSID_POSITION_IN_VCF": 18, "PALINDROMIC_NO_GWAS_EAF": 264, "PANEL_MAF_LT_1PCT": 5, "PASS": 1555}`
- Allele authority: VCF REF/ALT
- LD orientation: GWAS A1 dosage

## LD QC

- Matrix dimension: 1555 x 1555
- Minimum eigenvalue: -1.7404e-13
- Maximum diagonal error: 3.55271e-15
- Maximum asymmetry: 0
- Matrix rank: 394
- rs3790566/rs3790567 signed r: 0.9946139843666341
- Numerical gate: PASS

## Next gate

Run the RSS diagnostic without removing outliers to force a pass. Only if `estimate_s <= 0.1` and the maximum absolute kriging standardized residual is `<= 5` should the engineering-only SuSiE-RSS smoke test run.
