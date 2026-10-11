# R4A8B H1 → H2 action record — 2026-09-10

## H1 frozen result

The independent regional reference branch passed all reference gates:

- Assembly: GRCh37/hg19
- Reference: 1000 Genomes Phase 3 v5a
- Population: EUR
- Full chr1 indexed records: 6,468,094
- IL12RB2 ±500 kb all-Phase3 records: 28,390
- EUR samples: 503 / 503 unique / 0 missing from VCF
- EUR503 biallelic SNPs: 27,067
- Missing rsID: 0
- Duplicate rsID: 0
- Duplicate rsID+BP: 0
- PLINK BED expected bytes: 3,410,445
- PLINK BED actual bytes: 3,410,445
- BED magic: `6c1b01`
- Final H1 status: `R4A8B_REGIONAL_REFERENCE_FROZEN_PASS`

This branch is an independent Phase3-v5a regional validation and must not be represented as Zenodo exact-MD5 reproduction. The original R4A8 Zenodo branch remains `HOLD_EXTERNAL_ZENODO_DELIVERY` because the file endpoint returned HTTP 504 even for one-byte range requests.

## H2 objective

Reproduce the immutable 1,842-row GCST009131 IL12RB2 regional GWAS input and signed-Z values, then harmonize each row against the authoritative VCF REF/ALT manifest using unique rsID+position matching. Use the derived PLINK BED only as the genotype cache, orient dosage to GWAS A1, apply palindromic/allele/missingness/MAF gates, and compute signed-r LD in the exact retained order.

The RSS stage is engineering-only. It may run SuSiE-RSS only if `estimate_s <= 0.1` and maximum absolute kriging standardized residual `<= 5`. A HOLD is scientifically valid and must not be forced to pass by deleting variants.
