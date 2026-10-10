# Data availability

All core analysis inputs are publicly downloadable. This repository does not mirror the large raw files or donor-level genotype/LD data.

- IgAN combined, European-only and Asian-only GWAS summary statistics: Kiryluk laboratory public download site.
- OneK1K full cell-specific cis-eQTL, 980-donor PLINK genotype and covariates: Zenodo record 18910121.
- TenK10K full cis-eQTL, SuSiE and precomputed coloc resources: Zenodo record 18221260.
- UCSC hg19-to-hg38 chain for explicit cross-build comparison.
- Sun 2018 INTERVAL plasma pQTL permutation, nominal summary-statistics, source SuSiE credible-set and LBF files: eQTL Catalogue QTS000035/QTD000584.
- GSE127136 processed single-cell counts and SOFT metadata: NCBI GEO. Kidney and peripheral-monocyte compartments are analysed separately; paracancer kidney samples are not described as healthy controls.
- PBC GCST90061440 GRCh37 summary statistics: GWAS Catalog/EBI FTP.
- PBC locus summary statistics and study-derived LD: the public GJOKA archive on Heather Cordell's Newcastle page. R7A1B retrieves only locus 2 and locus 4 after the frozen trigger gate.
- HRA008003 PBC liver/PBMC single-cell data: GSA-Human open-access record. R7A1C1B2 completed the five PBC liver BAMs. R7A2A0 freezes the five hepatic-hemangioma non-lesion liver controls for an exact 5-vs-5 target-panel comparison.
- PBC liver paper Supplementary Data 1–18 and Source Data: official Springer binary XLSX endpoints. Their hashes and aggregate audits are retained; the workbooks are not mirrored.

Exact objects used in the current workflow, byte sizes, checksums and relative paths are in [`data/LARGE_DATA_MANIFEST.tsv`](data/LARGE_DATA_MANIFEST.tsv). Checksums supplied by a source are labeled `source`; locally computed checksums are labeled `local intake`. Users should verify the download before analysis.

R7A1B generated matrices and targeted GJOKA member hashes are listed separately in [`data/R7A1B1_LARGE_FILE_MANIFEST.tsv`](data/R7A1B1_LARGE_FILE_MANIFEST.tsv).

The five HRA008003 BAMs and two audited paper workbooks are listed in [`data/R7A1C1B0R_LARGE_ASSET_MANIFEST.tsv`](data/R7A1C1B0R_LARGE_ASSET_MANIFEST.tsv). The manifest distinguishes provider MD5 values from SHA-256 values computed after download.

The completed PBC liver gate and pending controls are recorded in [`data/R7A1C1B2_R7A2A0_LARGE_ASSET_MANIFEST.tsv`](data/R7A1C1B2_R7A2A0_LARGE_ASSET_MANIFEST.tsv). HRR1849459–63 have validated compact outputs and deleted local BAMs. HRR1849454–58 remain source-hosted and are the frozen R7A2A1 inputs. Only compact aggregate summaries, schema audits and byte receipts are published. Called-cell tables and BAMs remain excluded.

The published result tables contain summary-level or aggregate statistics only. Active-donor lists, standardized dosage matrices, source-LD matrices, SuSiE RDS fits, raw pQTL tables, raw single-cell objects and donor-level expression tables are deliberately excluded from GitHub. R6A2D retrieves only three CRC-verified members of the TenK10K precomputed-coloc archive; its member receipt is published under `results/r6a2d/`. R6A3A1 publishes file receipts, component-level coloc results and aggregate kidney summaries while leaving third-party source bytes at their original repositories.

## R7C0 external sources

R7C0 redistributes only analysis code, source receipts, small derived summaries and figures. FinnGen summary-statistic objects, FinnGen CASCADE service responses, GJOKA source data, OneK individual-level or pseudobulk inputs, and OMIX001122 source archives are not redistributed here. Their identifiers, URLs, byte hashes where applicable and retrieval records are listed in `results/r7c0/R7C0_source_ledger.tsv` and the R7C0 reports. Users must obtain those source objects from their original providers and comply with the applicable source terms.
