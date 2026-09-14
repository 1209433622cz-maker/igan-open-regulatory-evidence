# Data availability

All core analysis inputs are publicly downloadable. This repository does not mirror the large raw files or donor-level genotype/LD data.

- IgAN combined, European-only and Asian-only GWAS summary statistics: Kiryluk laboratory public download site.
- OneK1K full cell-specific cis-eQTL, 980-donor PLINK genotype and covariates: Zenodo record 18910121.
- TenK10K full cis-eQTL, SuSiE and precomputed coloc resources: Zenodo record 18221260.

Exact objects used in the current workflow, byte sizes, checksums and relative paths are in [`data/LARGE_DATA_MANIFEST.tsv`](data/LARGE_DATA_MANIFEST.tsv). Checksums supplied by a source are labeled `source`; locally computed checksums are labeled `local intake`. Users should verify the download before analysis.

The published result tables contain summary-level statistics only. Active-donor lists, standardized dosage matrices, source-LD matrices and raw single-cell objects are deliberately excluded from GitHub.

