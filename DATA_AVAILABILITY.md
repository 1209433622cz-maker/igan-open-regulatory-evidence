# Data availability

All core analysis inputs are publicly downloadable. This repository does not mirror the large raw files or donor-level genotype/LD data.

- IgAN combined, European-only and Asian-only GWAS summary statistics: Kiryluk laboratory public download site.
- OneK1K full cell-specific cis-eQTL, 980-donor PLINK genotype and covariates: Zenodo record 18910121.
- TenK10K full cis-eQTL, SuSiE and precomputed coloc resources: Zenodo record 18221260.
- UCSC hg19-to-hg38 chain for explicit cross-build comparison.

Exact objects used in the current workflow, byte sizes, checksums and relative paths are in [`data/LARGE_DATA_MANIFEST.tsv`](data/LARGE_DATA_MANIFEST.tsv). Checksums supplied by a source are labeled `source`; locally computed checksums are labeled `local intake`. Users should verify the download before analysis.

The published result tables contain summary-level statistics only. Active-donor lists, standardized dosage matrices, source-LD matrices, SuSiE RDS fits and raw single-cell objects are deliberately excluded from GitHub. R6A2D retrieves only three CRC-verified members of the TenK10K precomputed-coloc archive; its member receipt is published under `results/r6a2d/`.
